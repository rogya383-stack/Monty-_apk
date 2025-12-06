#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Thumbnails Module - لوحة الصفحات المصغرة
"""

import os
from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QListWidget, QListWidgetItem,
    QLabel, QPushButton, QScrollArea, QFrame, QMenu,
    QSizePolicy, QProgressBar, QInputDialog, QMessageBox
)
from PyQt5.QtGui import (
    QIcon, QPixmap, QImage, QFont, QPainter, QColor, QPen,
    QBrush, QMouseEvent, QContextMenuEvent, QPalette
)
from PyQt5.QtCore import (
    Qt, QSize, pyqtSignal, QTimer, QRect, QPoint, QEvent,
    QPropertyAnimation, QEasingCurve, QThread, pyqtSlot
)
from PIL import Image, ImageDraw, ImageFont
import time

class ThumbnailWorker(QThread):
    """عامل لتحميل الصور المصغرة في الخلفية"""
    
    thumbnailLoaded = pyqtSignal(int, object)  # (page_num, thumbnail_image)
    progressUpdated = pyqtSignal(int)  # progress percentage
    
    def __init__(self, pdf_handler, page_numbers, size=(120, 170)):
        super().__init__()
        self.pdf_handler = pdf_handler
        self.page_numbers = page_numbers
        self.thumbnail_size = size
        self.running = True
    
    def run(self):
        """تشغيل العامل"""
        total = len(self.page_numbers)
        
        for i, page_num in enumerate(self.page_numbers):
            if not self.running:
                break
            
            try:
                # الحصول على صورة مصغرة
                thumbnail = self.pdf_handler.get_page_thumbnail(
                    page_num,
                    size=self.thumbnail_size
                )
                
                if thumbnail:
                    self.thumbnailLoaded.emit(page_num, thumbnail)
                
                # تحديث التقدم
                progress = int((i + 1) / total * 100)
                self.progressUpdated.emit(progress)
                
                # إعطاء فرصة لتحديث الواجهة
                self.msleep(10)
                
            except Exception as e:
                print(f"خطأ في تحميل الصورة المصغرة للصفحة {page_num}: {e}")
        
        self.progressUpdated.emit(100)
    
    def stop(self):
        """إيقاف العامل"""
        self.running = False
        self.wait()

class ThumbnailItem(QListWidgetItem):
    """عنصر صفحة مصغرة مخصص"""
    
    def __init__(self, page_num, parent=None):
        super().__init__(parent)
        self.page_num = page_num
        self.thumbnail = None
        self.has_annotations = False
        self.is_bookmarked = False
        self.is_current = False
        self.loaded = False
        
        self.setData(Qt.UserRole, page_num)
        self.setText(f"الصفحة {page_num + 1}")
        self.setToolTip(f"الصفحة {page_num + 1}\nانقر للانتقال")
        
        # تعيين حجم ثابت
        self.setSizeHint(QSize(150, 200))
    
    def set_thumbnail(self, thumbnail):
        """تعيين الصورة المصغرة"""
        self.thumbnail = thumbnail
        self.loaded = True
        
        if thumbnail:
            # تحويل صورة PIL إلى QPixmap
            qimage = QImage(
                thumbnail.tobytes(),
                thumbnail.width,
                thumbnail.height,
                QImage.Format_RGB888
            )
            pixmap = QPixmap.fromImage(qimage)
            
            # إضافة تأثيرات إذا لزم
            if self.has_annotations:
                pixmap = self.add_annotation_badge(pixmap)
            
            if self.is_bookmarked:
                pixmap = self.add_bookmark_badge(pixmap)
            
            if self.is_current:
                pixmap = self.add_current_page_border(pixmap)
            
            self.setIcon(QIcon(pixmap))
    
    def add_annotation_badge(self, pixmap):
        """إضافة شارة للتعليقات"""
        painter = QPainter(pixmap)
        painter.setRenderHint(QPainter.Antialiasing)
        
        # رسم دائرة حمراء صغيرة
        badge_color = QColor(255, 59, 48)  # أحمر
        painter.setBrush(QBrush(badge_color))
        painter.setPen(Qt.NoPen)
        
        badge_size = 12
        badge_x = pixmap.width() - badge_size - 5
        badge_y = 5
        
        painter.drawEllipse(badge_x, badge_y, badge_size, badge_size)
        
        # رسم رقم التعليقات (إن وجد)
        painter.setPen(QPen(Qt.white))
        painter.setFont(QFont("Arial", 8))
        painter.drawText(
            QRect(badge_x, badge_y, badge_size, badge_size),
            Qt.AlignCenter,
            "!"
        )
        
        painter.end()
        return pixmap
    
    def add_bookmark_badge(self, pixmap):
        """إضافة شارة للعلامات المرجعية"""
        painter = QPainter(pixmap)
        painter.setRenderHint(QPainter.Antialiasing)
        
        # رسم علامة مرجعية في الأعلى
        bookmark_color = QColor(255, 204, 0)  # أصفر
        painter.setBrush(QBrush(bookmark_color))
        painter.setPen(QPen(bookmark_color.darker(), 1))
        
        # رسم شكل علامة مرجعية
        points = [
            QPoint(10, 5),
            QPoint(20, 15),
            QPoint(15, 15),
            QPoint(15, 25),
            QPoint(5, 25),
            QPoint(5, 15),
            QPoint(0, 15)
        ]
        
        painter.drawPolygon(points)
        
        painter.end()
        return pixmap
    
    def add_current_page_border(self, pixmap):
        """إضافة حدود للصفحة الحالية"""
        painter = QPainter(pixmap)
        painter.setRenderHint(QPainter.Antialiasing)
        
        # رسم حدود زرقاء
        border_color = QColor(0, 122, 255)  # أزرق
        painter.setPen(QPen(border_color, 3))
        painter.setBrush(Qt.NoBrush)
        
        # رسم مستطيل مع زوايا مستديرة
        rect = QRect(2, 2, pixmap.width() - 4, pixmap.height() - 4)
        painter.drawRoundedRect(rect, 5, 5)
        
        painter.end()
        return pixmap
    
    def update_appearance(self):
        """تحديث المظهر"""
        if self.thumbnail:
            self.set_thumbnail(self.thumbnail)

class ThumbnailPanel(QWidget):
    """لوحة الصفحات المصغرة"""
    
    # إشارات
    pageClicked = pyqtSignal(int)
    pageDoubleClicked = pyqtSignal(int)
    thumbnailSizeChanged = pyqtSignal(int)
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.parent = parent
        self.pdf_handler = None
        self.current_page = 0
        self.thumbnail_size = 120  # عرض الصورة المصغرة
        self.thumbnail_ratio = 1.4  # نسبة الارتفاع إلى العرض
        
        # إعدادات العرض
        self.show_page_numbers = True
        self.show_annotations_badge = True
        self.show_bookmarks_badge = True
        self.highlight_current_page = True
        
        # إدارة الذاكرة المؤقتة
        self.thumbnail_cache = {}
        self.max_cache_size = 50
        
        # عامل تحميل الصور المصغرة
        self.thumbnail_worker = None
        
        self.init_ui()
        self.setup_connections()
    
    def init_ui(self):
        """تهيئة واجهة المستخدم"""
        self.setMinimumWidth(200)
        
        # التخطيط الرئيسي
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(5, 5, 5, 5)
        main_layout.setSpacing(5)
        
        # شريط الأدوات العلوي
        self.create_toolbar(main_layout)
        
        # شريط التقدم
        self.progress_bar = QProgressBar()
        self.progress_bar.setVisible(False)
        main_layout.addWidget(self.progress_bar)
        
        # منطقة الصفحات المصغرة
        self.create_thumbnail_area(main_layout)
        
        # شريط المعلومات السفلي
        self.create_status_bar(main_layout)
    
    def create_toolbar(self, parent_layout):
        """إنشاء شريط الأدوات"""
        toolbar = QWidget()
        toolbar_layout = QHBoxLayout(toolbar)
        toolbar_layout.setContentsMargins(0, 0, 0, 0)
        
        # عنوان
        title_label = QLabel("الصفحات المصغرة")
        title_label.setFont(QFont("Arial", 11, QFont.Bold))
        title_label.setStyleSheet("color: #333333;")
        toolbar_layout.addWidget(title_label)
        
        toolbar_layout.addStretch()
        
        # أزرار التحكم بالحجم
        size_group = QWidget()
        size_layout = QHBoxLayout(size_group)
        size_layout.setContentsMargins(0, 0, 0, 0)
        size_layout.setSpacing(2)
        
        self.zoom_out_btn = QPushButton("−")
        self.zoom_out_btn.setFixedSize(25, 25)
        self.zoom_out_btn.setToolTip("تصغير الصور المصغرة")
        size_layout.addWidget(self.zoom_out_btn)
        
        self.size_label = QLabel("100%")
        self.size_label.setFixedWidth(40)
        self.size_label.setAlignment(Qt.AlignCenter)
        size_layout.addWidget(self.size_label)
        
        self.zoom_in_btn = QPushButton("+")
        self.zoom_in_btn.setFixedSize(25, 25)
        self.zoom_in_btn.setToolTip("تكبير الصور المصغرة")
        size_layout.addWidget(self.zoom_in_btn)
        
        toolbar_layout.addWidget(size_group)
        
        # زر الإعدادات
        self.settings_btn = QPushButton("⚙")
        self.settings_btn.setFixedSize(30, 30)
        self.settings_btn.setToolTip("إعدادات العرض")
        toolbar_layout.addWidget(self.settings_btn)
        
        parent_layout.addWidget(toolbar)
    
    def create_thumbnail_area(self, parent_layout):
        """إنشاء منطقة الصفحات المصغرة"""
        # منطقة التمرير
        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(True)
        self.scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        
        # حاوية الصور المصغرة
        self.thumbnails_container = QWidget()
        self.container_layout = QVBoxLayout(self.thumbnails_container)
        self.container_layout.setAlignment(Qt.AlignTop)
        self.container_layout.setSpacing(10)
        self.container_layout.setContentsMargins(5, 5, 5, 5)
        
        # قائمة العناصر
        self.thumbnail_items = []
        
        self.scroll_area.setWidget(self.thumbnails_container)
        parent_layout.addWidget(self.scroll_area)
    
    def create_status_bar(self, parent_layout):
        """إنشاء شريط المعلومات"""
        status_bar = QFrame()
        status_bar.setFrameStyle(QFrame.StyledPanel | QFrame.Raised)
        status_bar.setMaximumHeight(30)
        
        status_layout = QHBoxLayout(status_bar)
        status_layout.setContentsMargins(10, 2, 10, 2)
        
        self.page_info_label = QLabel("0 صفحة")
        self.page_info_label.setStyleSheet("color: #666666;")
        status_layout.addWidget(self.page_info_label)
        
        status_layout.addStretch()
        
        self.selection_info_label = QLabel("محدد: 0")
        self.selection_info_label.setStyleSheet("color: #666666;")
        status_layout.addWidget(self.selection_info_label)
        
        parent_layout.addWidget(status_bar)
    
    def setup_connections(self):
        """إعداد الاتصالات"""
        # أزرار التكبير/التصغير
        self.zoom_out_btn.clicked.connect(self.decrease_thumbnail_size)
        self.zoom_in_btn.clicked.connect(self.increase_thumbnail_size)
        
        # زر الإعدادات
        self.settings_btn.clicked.connect(self.show_settings_menu)
    
    def set_pdf_handler(self, handler):
        """تعيين معالج PDF"""
        self.pdf_handler = handler
        
        # إيقاف أي تحميل جارٍ
        if self.thumbnail_worker:
            self.thumbnail_worker.stop()
        
        # مسح الذاكرة المؤقتة
        self.thumbnail_cache.clear()
        
        if handler:
            self.load_thumbnails()
    
    def load_thumbnails(self):
        """تحميل الصفحات المصغرة"""
        if not self.pdf_handler:
            return
        
        # إزالة العناصر القديمة
        self.clear_thumbnails()
        
        total_pages = self.pdf_handler.total_pages
        
        # إنشاء عناصر الصفحات
        for page_num in range(total_pages):
            item = ThumbnailItem(page_num)
            
            # التحقق من وجود تعليقات
            if page_num in self.pdf_handler.annotations:
                annotations = self.pdf_handler.annotations[page_num]
                if annotations:
                    item.has_annotations = True
            
            # التحقق من وجود علامات مرجعية
            bookmarks = self.pdf_handler.get_bookmarks()
            for bookmark in bookmarks:
                if bookmark.get('page') == page_num:
                    item.is_bookmarked = True
                    break
            
            # التحقق إذا كانت الصفحة الحالية
            if page_num == self.current_page:
                item.is_current = True
            
            self.thumbnail_items.append(item)
        
        # تحديث المعلومات
        self.page_info_label.setText(f"{total_pages} صفحة")
        
        # بدء تحميل الصور المصغرة في الخلفية
        self.start_thumbnail_loading()
    
    def start_thumbnail_loading(self):
        """بدء تحميل الصور المصغرة في الخلفية"""
        if not self.pdf_handler:
            return
        
        # إيقاف العامل السابق إذا كان يعمل
        if self.thumbnail_worker:
            self.thumbnail_worker.stop()
        
        # إعداد شريط التقدم
        self.progress_bar.setVisible(True)
        self.progress_bar.setValue(0)
        
        # إنشاء عامل جديد
        page_numbers = list(range(self.pdf_handler.total_pages))
        thumbnail_size = (self.thumbnail_size, int(self.thumbnail_size * self.thumbnail_ratio))
        
        self.thumbnail_worker = ThumbnailWorker(
            self.pdf_handler,
            page_numbers,
            thumbnail_size
        )
        
        # ربط الإشارات
        self.thumbnail_worker.thumbnailLoaded.connect(self.on_thumbnail_loaded)
        self.thumbnail_worker.progressUpdated.connect(self.on_progress_updated)
        self.thumbnail_worker.finished.connect(self.on_loading_finished)
        
        # بدء التحميل
        self.thumbnail_worker.start()
    
    @pyqtSlot(int, object)
    def on_thumbnail_loaded(self, page_num, thumbnail):
        """عند تحميل صورة مصغرة"""
        # حفظ في الذاكرة المؤقتة
        self.thumbnail_cache[page_num] = thumbnail
        
        # تحديث العنصر المقابل
        for item in self.thumbnail_items:
            if item.page_num == page_num:
                item.set_thumbnail(thumbnail)
                
                # إضافة العنصر إلى الواجهة
                self.add_thumbnail_to_ui(item)
                break
    
    @pyqtSlot(int)
    def on_progress_updated(self, progress):
        """عند تحديث التقدم"""
        self.progress_bar.setValue(progress)
    
    @pyqtSlot()
    def on_loading_finished(self):
        """عند انتهاء التحميل"""
        self.progress_bar.setVisible(False)
        
        # ترتيب العناصر في الواجهة
        self.arrange_thumbnails()
        
        # الانتقال إلى الصفحة الحالية
        self.scroll_to_current_page()
    
    def add_thumbnail_to_ui(self, item):
        """إضافة صفحة مصغرة إلى الواجهة"""
        # إنشاء عنصر واجهة للصفحة المصغرة
        thumbnail_widget = self.create_thumbnail_widget(item)
        
        # إضافة إلى التخطيط
        self.container_layout.addWidget(thumbnail_widget)
    
    def create_thumbnail_widget(self, item):
        """إنشاء عنصر واجهة للصفحة المصغرة"""
        widget = QWidget()
        widget.setFixedSize(self.thumbnail_size + 40, 
                          int(self.thumbnail_size * self.thumbnail_ratio) + 60)
        
        layout = QVBoxLayout(widget)
        layout.setContentsMargins(5, 5, 5, 5)
        layout.setSpacing(5)
        
        # إطار الصورة
        frame = QFrame()
        frame.setFrameStyle(QFrame.StyledPanel | QFrame.Raised)
        frame.setFixedSize(self.thumbnail_size + 10, 
                          int(self.thumbnail_size * self.thumbnail_ratio) + 10)
        
        frame_layout = QVBoxLayout(frame)
        frame_layout.setContentsMargins(5, 5, 5, 5)
        
        # تسمية الصورة
        if item.thumbnail:
            qimage = QImage(
                item.thumbnail.tobytes(),
                item.thumbnail.width,
                item.thumbnail.height,
                QImage.Format_RGB888
            )
            pixmap = QPixmap.fromImage(qimage)
            
            image_label = QLabel()
            image_label.setPixmap(pixmap)
            image_label.setAlignment(Qt.AlignCenter)
            frame_layout.addWidget(image_label)
        
        layout.addWidget(frame)
        
        # تسمية رقم الصفحة
        page_label = QLabel(f"الصفحة {item.page_num + 1}")
        page_label.setAlignment(Qt.AlignCenter)
        page_label.setStyleSheet("""
            QLabel {
                font-weight: bold;
                color: #333333;
                padding: 2px;
            }
        """)
        
        if item.is_current:
            page_label.setStyleSheet("""
                QLabel {
                    font-weight: bold;
                    color: #0078d7;
                    background-color: #e3f2fd;
                    border-radius: 3px;
                    padding: 2px;
                }
            """)
        
        layout.addWidget(page_label)
        
        # إضافة مؤشرات
        if item.has_annotations or item.is_bookmarked:
            indicators_widget = QWidget()
            indicators_layout = QHBoxLayout(indicators_widget)
            indicators_layout.setContentsMargins(0, 0, 0, 0)
            
            if item.has_annotations:
                ann_label = QLabel("🖍️")
                ann_label.setToolTip("تحتوي على تعليقات")
                indicators_layout.addWidget(ann_label)
            
            if item.is_bookmarked:
                bm_label = QLabel("📖")
                bm_label.setToolTip("علامة مرجعية")
                indicators_layout.addWidget(bm_label)
            
            indicators_layout.addStretch()
            layout.addWidget(indicators_widget)
        
        # جعل العنصر قابل للنقر
        widget.mousePressEvent = lambda e, p=item.page_num: self.on_thumbnail_clicked(e, p)
        widget.mouseDoubleClickEvent = lambda e, p=item.page_num: self.on_thumbnail_double_clicked(e, p)
        
        return widget
    
    def arrange_thumbnails(self):
        """ترتيب الصفحات المصغرة في شبكة"""
        # حذف جميع العناصر الحالية
        while self.container_layout.count():
            item = self.container_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()
        
        # إعادة ترتيب العناصر في شبكة
        items_per_row = max(1, self.width() // (self.thumbnail_size + 50))
        
        row_widget = None
        row_layout = None
        
        for i, item in enumerate(self.thumbnail_items):
            if i % items_per_row == 0:
                # صف جديد
                row_widget = QWidget()
                row_layout = QHBoxLayout(row_widget)
                row_layout.setContentsMargins(0, 0, 0, 0)
                row_layout.setSpacing(10)
                self.container_layout.addWidget(row_widget)
            
            # إضافة عنصر الصفحة المصغرة
            thumbnail_widget = self.create_thumbnail_widget(item)
            row_layout.addWidget(thumbnail_widget)
    
    def scroll_to_current_page(self):
        """التمرير إلى الصفحة الحالية"""
        # سيتم تنفيذ في إصدار لاحق
        pass
    
    def clear_thumbnails(self):
        """مسح جميع الصفحات المصغرة"""
        # إزالة العناصر من الواجهة
        while self.container_layout.count():
            item = self.container_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()
        
        # مسح القائمة
        self.thumbnail_items.clear()
        
        # إيقاف العامل إذا كان يعمل
        if self.thumbnail_worker:
            self.thumbnail_worker.stop()
            self.thumbnail_worker = None
    
    def on_thumbnail_clicked(self, event, page_num):
        """عند النقر على صفحة مصغرة"""
        if event.button() == Qt.LeftButton:
            self.select_page(page_num)
            self.pageClicked.emit(page_num)
        
        elif event.button() == Qt.RightButton:
            self.show_thumbnail_context_menu(event.globalPos(), page_num)
    
    def on_thumbnail_double_clicked(self, event, page_num):
        """عند النقر المزدوج على صفحة مصغرة"""
        if event.button() == Qt.LeftButton:
            self.select_page(page_num)
            self.pageDoubleClicked.emit(page_num)
    
    def select_page(self, page_num):
        """تحديد صفحة محددة"""
        self.current_page = page_num
        
        # تحديث مظهر جميع العناصر
        for item in self.thumbnail_items:
            item.is_current = (item.page_num == page_num)
            item.update_appearance()
        
        # إعادة ترتيب الواجهة
        self.arrange_thumbnails()
        
        # تحديث معلومات التحديد
        self.selection_info_label.setText(f"محدد: {page_num + 1}")
    
    def show_thumbnail_context_menu(self, pos, page_num):
        """عرض قائمة السياق للصفحة المصغرة"""
        menu = QMenu()
        
        # إجراءات الصفحة
        goto_action = menu.addAction("انتقال إلى الصفحة")
        delete_action = menu.addAction("حذف الصفحة")
        duplicate_action = menu.addAction("تكرار الصفحة")
        
        menu.addSeparator()
        
        # إجراءات العلامات المرجعية
        add_bookmark_action = menu.addAction("إضافة علامة مرجعية")
        
        menu.addSeparator()
        
        # إجراءات التصدير
        export_page_action = menu.addAction("تصدير الصفحة كصورة")
        
        # تنفيذ الإجراء المحدد
        action = menu.exec_(pos)
        
        if action == goto_action:
            self.select_page(page_num)
            self.pageClicked.emit(page_num)
        
        elif action == delete_action:
            self.delete_page(page_num)
        
        elif action == duplicate_action:
            self.duplicate_page(page_num)
        
        elif action == add_bookmark_action:
            self.add_bookmark(page_num)
        
        elif action == export_page_action:
            self.export_page_as_image(page_num)
    
    def delete_page(self, page_num):
        """حذف صفحة"""
        reply = QMessageBox.question(
            self,
            "حذف الصفحة",
            f"هل تريد حذف الصفحة {page_num + 1}؟\nلا يمكن التراجع عن هذا الإجراء.",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )
        
        if reply == QMessageBox.Yes and self.pdf_handler:
            # هنا سيتم تنفيذ حذف الصفحة في إصدار لاحق
            QMessageBox.information(self, "معلومة", "ميزة حذف الصفحات قيد التطوير")
    
    def duplicate_page(self, page_num):
        """تكرار صفحة"""
        # سيتم تنفيذ في إصدار لاحق
        pass
    
    def add_bookmark(self, page_num):
        """إضافة علامة مرجعية"""
        title, ok = QInputDialog.getText(
            self,
            "إضافة علامة مرجعية",
            "أدخل عنوان العلامة المرجعية:",
            text=f"الصفحة {page_num + 1}"
        )
        
        if ok and title:
            # هنا سيتم إضافة العلامة المرجعية في إصدار لاحق
            QMessageBox.information(self, "معلومة", "ميزة العلامات المرجعية قيد التطوير")
    
    def export_page_as_image(self, page_num):
        """تصدير الصفحة كصورة"""
        if not self.pdf_handler:
            return
        
        file_path, _ = QFileDialog.getSaveFileName(
            self,
            "تصدير الصفحة كصورة",
            f"page_{page_num + 1}.png",
            "صور PNG (*.png);;صور JPEG (*.jpg);;جميع الملفات (*)"
        )
        
        if file_path:
            try:
                # الحصول على صورة الصفحة
                page_image = self.pdf_handler.get_page_image(page_num, zoom=2.0)
                
                if page_image:
                    page_image.save(file_path)
                    QMessageBox.information(self, "نجاح", f"تم تصدير الصفحة إلى:\n{file_path}")
                else:
                    QMessageBox.warning(self, "خطأ", "تعذر تصدير الصفحة")
                    
            except Exception as e:
                QMessageBox.critical(self, "خطأ", f"حدث خطأ أثناء التصدير:\n{str(e)}")
    
    def increase_thumbnail_size(self):
        """زيادة حجم الصور المصغرة"""
        self.thumbnail_size = min(self.thumbnail_size + 20, 300)
        self.update_thumbnail_size()
    
    def decrease_thumbnail_size(self):
        """تقليل حجم الصور المصغرة"""
        self.thumbnail_size = max(self.thumbnail_size - 20, 60)
        self.update_thumbnail_size()
    
    def update_thumbnail_size(self):
        """تحديث حجم الصور المصغرة"""
        # تحديث التسمية
        percentage = int((self.thumbnail_size / 120) * 100)
        self.size_label.setText(f"{percentage}%")
        
        # إعادة تحميل الصور المصغرة
        if self.pdf_handler:
            self.start_thumbnail_loading()
        
        # إرسال إشارة تغيير الحجم
        self.thumbnailSizeChanged.emit(self.thumbnail_size)
    
    def show_settings_menu(self):
        """عرض قائمة إعدادات العرض"""
        menu = QMenu()
        
        # خيارات العرض
        show_numbers_action = menu.addAction("إظهار أرقام الصفحات")
        show_numbers_action.setCheckable(True)
        show_numbers_action.setChecked(self.show_page_numbers)
        show_numbers_action.triggered.connect(
            lambda checked: setattr(self, 'show_page_numbers', checked)
        )
        
        show_ann_badge_action = menu.addAction("إظهار شارات التعليقات")
        show_ann_badge_action.setCheckable(True)
        show_ann_badge_action.setChecked(self.show_annotations_badge)
        show_ann_badge_action.triggered.connect(
            lambda checked: setattr(self, 'show_annotations_badge', checked)
        )
        
        show_bm_badge_action = menu.addAction("إظهار شارات العلامات")
        show_bm_badge_action.setCheckable(True)
        show_bm_badge_action.setChecked(self.show_bookmarks_badge)
        show_bm_badge_action.triggered.connect(
            lambda checked: setattr(self, 'show_bookmarks_badge', checked)
        )
        
        highlight_current_action = menu.addAction("تمييز الصفحة الحالية")
        highlight_current_action.setCheckable(True)
        highlight_current_action.setChecked(self.highlight_current_page)
        highlight_current_action.triggered.connect(
            lambda checked: setattr(self, 'highlight_current_page', checked)
        )
        
        menu.addSeparator()
        
        # إجراءات إضافية
        refresh_action = menu.addAction("تحديث الصور المصغرة")
        refresh_action.triggered.connect(self.refresh_thumbnails)
        
        clear_cache_action = menu.addAction("مسح الذاكرة المؤقتة")
        clear_cache_action.triggered.connect(self.clear_thumbnail_cache)
        
        menu.exec_(self.settings_btn.mapToGlobal(QPoint(0, self.settings_btn.height())))
    
    def refresh_thumbnails(self):
        """تحديث الصور المصغرة"""
        if self.pdf_handler:
            self.thumbnail_cache.clear()
            self.start_thumbnail_loading()
    
    def clear_thumbnail_cache(self):
        """مسح الذاكرة المؤقتة للصور المصغرة"""
        self.thumbnail_cache.clear()
        QMessageBox.information(self, "تم", "تم مسح الذاكرة المؤقتة للصور المصغرة")
    
    def resizeEvent(self, event):
        """عند تغيير حجم النافذة"""
        super().resizeEvent(event)
        self.arrange_thumbnails()
    
    def closeEvent(self, event):
        """عند إغلاق النافذة"""
        # إيقاف العامل إذا كان يعمل
        if self.thumbnail_worker:
            self.thumbnail_worker.stop()
        
        super().closeEvent(event)


# تشغيل مباشر للاختبار
if __name__ == "__main__":
    from PyQt5.QtWidgets import QApplication
    import sys
    
    app = QApplication(sys.argv)
    panel = ThumbnailPanel()
    panel.show()
    sys.exit(app.exec_())
