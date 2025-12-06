#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Sidebar Module - الشريط الجانبي
Contains bookmarks, thumbnails, and document information
"""

import os
from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QTabWidget,
    QTreeWidget, QTreeWidgetItem, QListWidget, QListWidgetItem,
    QTextEdit, QLabel, QPushButton, QGroupBox,
    QFormLayout, QScrollArea, QFrame, QSplitter,
    QLineEdit, QCheckBox, QMessageBox, QFileDialog,
    QSizePolicy, QSpacerItem
)
from PyQt5.QtGui import (
    QFont, QIcon, QPixmap, QImage, QColor, QPalette,
    QTextCharFormat, QTextCursor, QTextDocument,
    QSyntaxHighlighter, QTextFormat
)
from PyQt5.QtCore import (
    Qt, pyqtSignal, QSize, QTimer, QRect, QPoint,
    QPropertyAnimation, QEasingCurve
)

class SideBar(QWidget):
    """الشريط الجانبي الرئيسي"""
    
    # إشارات
    pageClicked = pyqtSignal(int)
    bookmarkClicked = pyqtSignal(int)
    annotationClicked = pyqtSignal(int, int)
    searchRequested = pyqtSignal(str, bool, bool)
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.parent = parent
        self.pdf_handler = None
        self.current_page = 0
        self.thumbnail_size = 100  # نسبة مئوية
        
        self.init_ui()
        self.setup_styles()
    
    def init_ui(self):
        """تهيئة واجهة المستخدم"""
        self.setMinimumWidth(250)
        self.setMaximumWidth(350)
        
        # التخطيط الرئيسي
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)
        
        # علامات التبويب
        self.tab_widget = QTabWidget()
        self.tab_widget.setTabPosition(QTabWidget.West)
        self.tab_widget.setDocumentMode(True)
        
        # إنشاء علامات التبويب
        self.create_pages_tab()
        self.create_bookmarks_tab()
        self.create_annotations_tab()
        self.create_search_tab()
        self.create_info_tab()
        
        main_layout.addWidget(self.tab_widget)
        
        # شريط الحالة المصغر
        self.create_status_bar()
    
    def setup_styles(self):
        """إعداد الأنماط"""
        self.setStyleSheet("""
            QTabWidget::pane {
                border: 1px solid #cccccc;
                background-color: #f5f5f5;
            }
            QTabBar::tab {
                background-color: #e0e0e0;
                padding: 8px 12px;
                margin-right: 2px;
                border: 1px solid #cccccc;
            }
            QTabBar::tab:selected {
                background-color: #ffffff;
                border-bottom: 2px solid #0078d7;
            }
            QTabBar::tab:hover {
                background-color: #f0f0f0;
            }
            QTreeWidget {
                border: none;
                background-color: white;
            }
            QListWidget {
                border: none;
                background-color: white;
            }
            QTextEdit {
                border: none;
                background-color: white;
            }
            QGroupBox {
                font-weight: bold;
                border: 1px solid #cccccc;
                border-radius: 5px;
                margin-top: 10px;
                padding-top: 10px;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 5px 0 5px;
            }
        """)
    
    def create_pages_tab(self):
        """إنشاء علامة تبويب الصفحات المصغرة"""
        pages_widget = QWidget()
        layout = QVBoxLayout(pages_widget)
        layout.setContentsMargins(5, 5, 5, 5)
        
        # شريط الأدوات
        toolbar = QWidget()
        toolbar_layout = QHBoxLayout(toolbar)
        toolbar_layout.setContentsMargins(0, 0, 0, 0)
        
        # عناصر التحكم بالحجم
        size_label = QLabel("الحجم:")
        toolbar_layout.addWidget(size_label)
        
        self.zoom_out_btn = QPushButton("➖")
        self.zoom_out_btn.setFixedSize(25, 25)
        self.zoom_out_btn.setToolTip("تصغير الصور المصغرة")
        self.zoom_out_btn.clicked.connect(self.zoom_out_thumbnails)
        toolbar_layout.addWidget(self.zoom_out_btn)
        
        self.thumbnail_size_label = QLabel("100%")
        self.thumbnail_size_label.setFixedWidth(40)
        self.thumbnail_size_label.setAlignment(Qt.AlignCenter)
        toolbar_layout.addWidget(self.thumbnail_size_label)
        
        self.zoom_in_btn = QPushButton("➕")
        self.zoom_in_btn.setFixedSize(25, 25)
        self.zoom_in_btn.setToolTip("تكبير الصور المصغرة")
        self.zoom_in_btn.clicked.connect(self.zoom_in_thumbnails)
        toolbar_layout.addWidget(self.zoom_in_btn)
        
        toolbar_layout.addStretch()
        
        # زر الترتيب
        self.sort_btn = QPushButton("ترتيب")
        self.sort_btn.setToolTip("ترتيب الصفحات")
        self.sort_btn.clicked.connect(self.toggle_sort_order)
        toolbar_layout.addWidget(self.sort_btn)
        
        layout.addWidget(toolbar)
        
        # قائمة الصفحات المصغرة
        self.pages_list = QListWidget()
        self.pages_list.setViewMode(QListWidget.IconMode)
        self.pages_list.setIconSize(QSize(120, 170))
        self.pages_list.setResizeMode(QListWidget.Adjust)
        self.pages_list.setMovement(QListWidget.Static)
        self.pages_list.setSpacing(10)
        self.pages_list.setUniformItemSizes(True)
        self.pages_list.itemClicked.connect(self.on_page_clicked)
        
        layout.addWidget(self.pages_list)
        
        self.tab_widget.addTab(pages_widget, "📄 صفحات")
    
    def create_bookmarks_tab(self):
        """إنشاء علامة تبويب العلامات المرجعية"""
        bookmarks_widget = QWidget()
        layout = QVBoxLayout(bookmarks_widget)
        layout.setContentsMargins(5, 5, 5, 5)
        
        # عنوان
        title_label = QLabel("جدول المحتويات")
        title_label.setFont(QFont("Arial", 12, QFont.Bold))
        title_label.setAlignment(Qt.AlignCenter)
        title_label.setStyleSheet("""
            QLabel {
                padding: 8px;
                background-color: #0078d7;
                color: white;
                border-radius: 3px;
                margin-bottom: 5px;
            }
        """)
        layout.addWidget(title_label)
        
        # شجرة العلامات المرجعية
        self.bookmarks_tree = QTreeWidget()
        self.bookmarks_tree.setHeaderLabel("المحتوى")
        self.bookmarks_tree.setColumnCount(2)
        self.bookmarks_tree.setColumnHidden(1, True)  # إخفاء عمود الصفحة
        self.bookmarks_tree.setAlternatingRowColors(True)
        self.bookmarks_tree.itemClicked.connect(self.on_bookmark_clicked)
        
        layout.addWidget(self.bookmarks_tree)
        
        # معلومات
        self.bookmarks_info = QLabel("لا توجد علامات مرجعية")
        self.bookmarks_info.setAlignment(Qt.AlignCenter)
        self.bookmarks_info.setStyleSheet("color: #666666; font-style: italic;")
        layout.addWidget(self.bookmarks_info)
        
        self.tab_widget.addTab(bookmarks_widget, "📑 فهرس")
    
    def create_annotations_tab(self):
        """إنشاء علامة تبويب التعليقات التوضيحية"""
        annotations_widget = QWidget()
        layout = QVBoxLayout(annotations_widget)
        layout.setContentsMargins(5, 5, 5, 5)
        
        # عنوان
        title_label = QLabel("التعليقات التوضيحية")
        title_label.setFont(QFont("Arial", 12, QFont.Bold))
        title_label.setAlignment(Qt.AlignCenter)
        title_label.setStyleSheet("""
            QLabel {
                padding: 8px;
                background-color: #28a745;
                color: white;
                border-radius: 3px;
                margin-bottom: 5px;
            }
        """)
        layout.addWidget(title_label)
        
        # فلتر التعليقات
        filter_widget = QWidget()
        filter_layout = QHBoxLayout(filter_widget)
        filter_layout.setContentsMargins(0, 0, 0, 0)
        
        filter_label = QLabel("تصفية:")
        filter_layout.addWidget(filter_label)
        
        self.annotation_filter = QComboBox()
        self.annotation_filter.addItems(["جميع التعليقات", "التظليل", "النص", "الأشكال"])
        self.annotation_filter.currentTextChanged.connect(self.filter_annotations)
        filter_layout.addWidget(self.annotation_filter)
        
        filter_layout.addStretch()
        layout.addWidget(filter_widget)
        
        # قائمة التعليقات
        self.annotations_list = QListWidget()
        self.annotations_list.setAlternatingRowColors(True)
        self.annotations_list.itemClicked.connect(self.on_annotation_clicked)
        
        layout.addWidget(self.annotations_list)
        
        # أزرار التحكم
        control_widget = QWidget()
        control_layout = QHBoxLayout(control_widget)
        control_layout.setContentsMargins(0, 0, 0, 0)
        
        self.delete_annotation_btn = QPushButton("حذف")
        self.delete_annotation_btn.setIcon(QIcon("🗑️"))
        self.delete_annotation_btn.setToolTip("حذف التعليق المحدد")
        self.delete_annotation_btn.clicked.connect(self.delete_selected_annotation)
        self.delete_annotation_btn.setEnabled(False)
        control_layout.addWidget(self.delete_annotation_btn)
        
        self.clear_annotations_btn = QPushButton("مسح الكل")
        self.clear_annotations_btn.setIcon(QIcon("🚫"))
        self.clear_annotations_btn.setToolTip("مسح جميع التعليقات")
        self.clear_annotations_btn.clicked.connect(self.clear_all_annotations)
        control_layout.addWidget(self.clear_annotations_btn)
        
        control_layout.addStretch()
        
        self.annotations_count_label = QLabel("0 تعليق")
        control_layout.addWidget(self.annotations_count_label)
        
        layout.addWidget(control_widget)
        
        self.tab_widget.addTab(annotations_widget, "✏️ تعليقات")
    
    def create_search_tab(self):
        """إنشاء علامة تبويب البحث"""
        search_widget = QWidget()
        layout = QVBoxLayout(search_widget)
        layout.setContentsMargins(5, 5, 5, 5)
        
        # عنوان
        title_label = QLabel("البحث في المستند")
        title_label.setFont(QFont("Arial", 12, QFont.Bold))
        title_label.setAlignment(Qt.AlignCenter)
        title_label.setStyleSheet("""
            QLabel {
                padding: 8px;
                background-color: #ff6b6b;
                color: white;
                border-radius: 3px;
                margin-bottom: 5px;
            }
        """)
        layout.addWidget(title_label)
        
        # حقل البحث
        search_input_widget = QWidget()
        search_input_layout = QHBoxLayout(search_input_widget)
        search_input_layout.setContentsMargins(0, 0, 0, 0)
        
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("أدخل نص البحث...")
        self.search_input.returnPressed.connect(self.perform_search)
        search_input_layout.addWidget(self.search_input)
        
        self.search_btn = QPushButton("🔍")
        self.search_btn.setFixedSize(30, 30)
        self.search_btn.setToolTip("بحث")
        self.search_btn.clicked.connect(self.perform_search)
        search_input_layout.addWidget(self.search_btn)
        
        layout.addWidget(search_input_widget)
        
        # خيارات البحث
        options_widget = QWidget()
        options_layout = QVBoxLayout(options_widget)
        options_layout.setContentsMargins(0, 5, 0, 5)
        
        self.case_sensitive_check = QCheckBox("مطابقة حالة الأحرف")
        options_layout.addWidget(self.case_sensitive_check)
        
        self.whole_word_check = QCheckBox("مطابقة الكلمة كاملة")
        options_layout.addWidget(self.whole_word_check)
        
        layout.addWidget(options_widget)
        
        # نتائج البحث
        results_label = QLabel("النتائج:")
        results_label.setFont(QFont("Arial", 10, QFont.Bold))
        layout.addWidget(results_label)
        
        self.results_list = QListWidget()
        self.results_list.itemClicked.connect(self.on_search_result_clicked)
        layout.addWidget(self.results_list)
        
        # معلومات النتائج
        self.results_info = QLabel("اكتب نص البحث واضغط Enter")
        self.results_info.setAlignment(Qt.AlignCenter)
        self.results_info.setStyleSheet("color: #666666; font-style: italic;")
        layout.addWidget(self.results_info)
        
        # أدوات التنقل
        nav_widget = QWidget()
        nav_layout = QHBoxLayout(nav_widget)
        nav_layout.setContentsMargins(0, 0, 0, 0)
        
        self.prev_result_btn = QPushButton("السابق")
        self.prev_result_btn.setIcon(QIcon("◀"))
        self.prev_result_btn.setToolTip("النتيجة السابقة")
        self.prev_result_btn.clicked.connect(self.go_to_prev_result)
        self.prev_result_btn.setEnabled(False)
        nav_layout.addWidget(self.prev_result_btn)
        
        self.next_result_btn = QPushButton("التالي")
        self.next_result_btn.setIcon(QIcon("▶"))
        self.next_result_btn.setToolTip("النتيجة التالية")
        self.next_result_btn.clicked.connect(self.go_to_next_result)
        self.next_result_btn.setEnabled(False)
        nav_layout.addWidget(self.next_result_btn)
        
        nav_layout.addStretch()
        
        self.results_count_label = QLabel("0/0")
        nav_layout.addWidget(self.results_count_label)
        
        layout.addWidget(nav_widget)
        
        self.tab_widget.addTab(search_widget, "🔍 بحث")
    
    def create_info_tab(self):
        """إنشاء علامة تبويب المعلومات"""
        info_widget = QWidget()
        layout = QVBoxLayout(info_widget)
        layout.setContentsMargins(5, 5, 5, 5)
        
        # عنوان
        title_label = QLabel("معلومات المستند")
        title_label.setFont(QFont("Arial", 12, QFont.Bold))
        title_label.setAlignment(Qt.AlignCenter)
        title_label.setStyleSheet("""
            QLabel {
                padding: 8px;
                background-color: #6f42c1;
                color: white;
                border-radius: 3px;
                margin-bottom: 5px;
            }
        """)
        layout.addWidget(title_label)
        
        # منطقة التمرير
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        
        info_content = QWidget()
        info_layout = QVBoxLayout(info_content)
        
        # معلومات الملف
        file_group = QGroupBox("معلومات الملف")
        file_layout = QFormLayout()
        
        self.file_title_label = QLabel("غير معروف")
        file_layout.addRow("العنوان:", self.file_title_label)
        
        self.file_author_label = QLabel("غير معروف")
        file_layout.addRow("المؤلف:", self.file_author_label)
        
        self.file_subject_label = QLabel("غير معروف")
        file_layout.addRow("الموضوع:", self.file_subject_label)
        
        self.file_pages_label = QLabel("0")
        file_layout.addRow("الصفحات:", self.file_pages_label)
        
        self.file_size_label = QLabel("0 بايت")
        file_layout.addRow("الحجم:", self.file_size_label)
        
        file_group.setLayout(file_layout)
        info_layout.addWidget(file_group)
        
        # معلومات الإنتاج
        production_group = QGroupBox("معلومات الإنتاج")
        production_layout = QFormLayout()
        
        self.prod_creator_label = QLabel("غير معروف")
        production_layout.addRow("المنشئ:", self.prod_creator_label)
        
        self.prod_producer_label = QLabel("غير معروف")
        production_layout.addRow("المنتج:", self.prod_producer_label)
        
        self.prod_created_label = QLabel("غير معروف")
        production_layout.addRow("تاريخ الإنشاء:", self.prod_created_label)
        
        self.prod_modified_label = QLabel("غير معروف")
        production_layout.addRow("آخر تعديل:", self.prod_modified_label)
        
        production_group.setLayout(production_layout)
        info_layout.addWidget(production_group)
        
        # إحصائيات
        stats_group = QGroupBox("إحصائيات")
        stats_layout = QFormLayout()
        
        self.stats_annotations_label = QLabel("0")
        stats_layout.addRow("التعليقات:", self.stats_annotations_label)
        
        self.stats_bookmarks_label = QLabel("0")
        stats_layout.addRow("العلامات المرجعية:", self.stats_bookmarks_label)
        
        self.stats_images_label = QLabel("0")
        stats_layout.addRow("الصور:", self.stats_images_label)
        
        stats_group.setLayout(stats_layout)
        info_layout.addWidget(stats_group)
        
        # معلومات إضافية
        extra_group = QGroupBox("معلومات إضافية")
        extra_layout = QVBoxLayout()
        
        self.extra_text = QTextEdit()
        self.extra_text.setReadOnly(True)
        self.extra_text.setMaximumHeight(100)
        extra_layout.addWidget(self.extra_text)
        
        extra_group.setLayout(extra_layout)
        info_layout.addWidget(extra_group)
        
        spacer = QSpacerItem(20, 40, QSizePolicy.Minimum, QSizePolicy.Expanding)
        info_layout.addItem(spacer)
        
        scroll_area.setWidget(info_content)
        layout.addWidget(scroll_area)
        
        self.tab_widget.addTab(info_widget, "ℹ️ معلومات")
    
    def create_status_bar(self):
        """إنشاء شريط الحالة المصغر"""
        status_widget = QWidget()
        status_layout = QHBoxLayout(status_widget)
        status_layout.setContentsMargins(5, 2, 5, 2)
        
        self.status_label = QLabel("جاهز")
        self.status_label.setStyleSheet("color: #666666; font-size: 9pt;")
        status_layout.addWidget(self.status_label)
        
        status_layout.addStretch()
        
        self.page_status_label = QLabel("صفحة: 0/0")
        self.page_status_label.setStyleSheet("color: #666666; font-size: 9pt;")
        status_layout.addWidget(self.page_status_label)
        
        self.layout().addWidget(status_widget)
    
    def set_pdf_handler(self, handler):
        """تعيين معالج PDF"""
        self.pdf_handler = handler
        if handler:
            self.load_all_info()
    
    def load_all_info(self):
        """تحميل جميع المعلومات"""
        if not self.pdf_handler:
            return
        
        # تحميل الصفحات المصغرة
        self.load_thumbnails()
        
        # تحميل العلامات المرجعية
        self.load_bookmarks()
        
        # تحميل التعليقات
        self.load_annotations()
        
        # تحميل معلومات الملف
        self.load_file_info()
        
        # تحديث شريط الحالة
        self.update_status()
    
    def load_thumbnails(self):
        """تحميل الصفحات المصغرة"""
        self.pages_list.clear()
        
        if not self.pdf_handler:
            return
        
        total_pages = self.pdf_handler.total_pages
        
        # عرض مؤشر التحميل
        self.status_label.setText(f"جاري تحميل {total_pages} صفحة...")
        
        # تحميل الصور المصغرة على مراحل لتجنب تجميد الواجهة
        self.thumbnail_queue = list(range(total_pages))
        self.current_thumbnail_index = 0
        
        QTimer.singleShot(100, self.load_next_thumbnail)
    
    def load_next_thumbnail(self):
        """تحميل الصورة المصغرة التالية"""
        if not self.thumbnail_queue or self.current_thumbnail_index >= len(self.thumbnail_queue):
            self.status_label.setText("تم تحميل جميع الصفحات")
            return
        
        page_num = self.thumbnail_queue[self.current_thumbnail_index]
        
        try:
            # الحصول على صورة مصغرة
            thumbnail = self.pdf_handler.get_page_thumbnail(page_num)
            
            if thumbnail:
                # تحويل إلى QPixmap
                qimage = QImage(
                    thumbnail.tobytes(),
                    thumbnail.width,
                    thumbnail.height,
                    QImage.Format_RGB888
                )
                pixmap = QPixmap.fromImage(qimage)
                
                # إنشاء عنصر القائمة
                item = QListWidgetItem()
                item.setIcon(QIcon(pixmap))
                item.setText(f"الصفحة {page_num + 1}")
                item.setData(Qt.UserRole, page_num)
                item.setToolTip(f"الصفحة {page_num + 1}\nانقر نقراً مزدوجاً للانتقال")
                
                self.pages_list.addItem(item)
            
        except Exception as e:
            print(f"خطأ في تحميل الصورة المصغرة للصفحة {page_num}: {e}")
        
        self.current_thumbnail_index += 1
        
        # تحديث حالة التقدم
        progress = int((self.current_thumbnail_index / len(self.thumbnail_queue)) * 100)
        self.status_label.setText(f"جاري التحميل: {progress}%")
        
        # تحميل الصورة التالية بعد فترة وجيزة
        QTimer.singleShot(10, self.load_next_thumbnail)
    
    def load_bookmarks(self):
        """تحميل العلامات المرجعية"""
        self.bookmarks_tree.clear()
        
        if not self.pdf_handler:
            return
        
        bookmarks = self.pdf_handler.get_bookmarks()
        
        if not bookmarks:
            self.bookmarks_info.setText("لا توجد علامات مرجعية")
            return
        
        # تنظيم العلامات المرجعية في هرمية
        root_items = {}
        
        for bookmark in bookmarks:
            level = bookmark.get('level', 1)
            title = bookmark.get('title', 'بدون عنوان')
            page = bookmark.get('page', 0)
            
            item = QTreeWidgetItem()
            item.setText(0, title)
            item.setText(1, str(page + 1))  # للعرض
            item.setData(0, Qt.UserRole, page)
            
            # إضافة أيقونة حسب المستوى
            if level == 1:
                item.setIcon(0, QIcon("📖"))
            elif level == 2:
                item.setIcon(0, QIcon("📑"))
            else:
                item.setIcon(0, QIcon("📄"))
            
            if level == 1:
                # مستوى جذر
                self.bookmarks_tree.addTopLevelItem(item)
                root_items[1] = item
            else:
                # مستوى فرعي
                parent = root_items.get(level - 1)
                if parent:
                    parent.addChild(item)
                else:
                    self.bookmarks_tree.addTopLevelItem(item)
                
                root_items[level] = item
        
        # توسيع جميع العناصر
        self.bookmarks_tree.expandAll()
        
        self.bookmarks_info.setText(f"{len(bookmarks)} علامة مرجعية")
    
    def load_annotations(self):
        """تحميل التعليقات التوضيحية"""
        self.annotations_list.clear()
        
        if not self.pdf_handler:
            return
        
        annotations = self.pdf_handler.get_all_annotations()
        total_count = 0
        
        for page_num, page_annotations in annotations.items():
            for annotation in page_annotations:
                ann_type = annotation.get('type', 'unknown')
                ann_text = annotation.get('text', '')
                ann_id = annotation.get('id', 0)
                ann_date = annotation.get('date', '')
                
                # إنشاء نص العنصر
                item_text = f"الصفحة {page_num + 1}: "
                
                # تحديد نوع التعليق
                type_names = {
                    'highlight': '🖍️ تظليل',
                    'underline': '⎁ خط سفلي',
                    'strikeout': '☓ شطب',
                    'rectangle': '▭ مستطيل',
                    'circle': '○ دائرة',
                    'text': '📝 نص'
                }
                
                item_text += type_names.get(ann_type, ann_type)
                
                if ann_text:
                    item_text += f" - {ann_text[:30]}"
                
                if ann_date:
                    item_text += f" ({ann_date[:10]})"
                
                # إنشاء العنصر
                item = QListWidgetItem(item_text)
                item.setData(Qt.UserRole, (page_num, ann_id))
                
                # تلوين حسب النوع
                if ann_type == 'highlight':
                    item.setForeground(QColor(255, 255, 0, 100))
                elif ann_type == 'underline':
                    item.setForeground(QColor(0, 0, 255))
                elif ann_type == 'strikeout':
                    item.setForeground(QColor(255, 0, 0))
                elif ann_type in ['rectangle', 'circle']:
                    item.setForeground(QColor(0, 128, 0))
                elif ann_type == 'text':
                    item.setForeground(QColor(128, 0, 128))
                
                self.annotations_list.addItem(item)
                total_count += 1
        
        # تحديث العدد
        self.annotations_count_label.setText(f"{total_count} تعليق")
        
        # تفعيل/تعطيل الأزرار
        self.delete_annotation_btn.setEnabled(total_count > 0)
        self.clear_annotations_btn.setEnabled(total_count > 0)
    
    def load_file_info(self):
        """تحميل معلومات الملف"""
        if not self.pdf_handler:
            return
        
        metadata = self.pdf_handler.get_metadata()
        
        # معلومات الملف
        self.file_title_label.setText(metadata.get('title', 'غير معروف'))
        self.file_author_label.setText(metadata.get('author', 'غير معروف'))
        self.file_subject_label.setText(metadata.get('subject', 'غير معروف'))
        self.file_pages_label.setText(str(metadata.get('pages', 0)))
        
        # حجم الملف
        file_size = metadata.get('file_size', 0)
        if file_size >= 1024*1024:
            size_text = f"{file_size/(1024*1024):.1f} MB"
        elif file_size >= 1024:
            size_text = f"{file_size/1024:.1f} KB"
        else:
            size_text = f"{file_size} بايت"
        self.file_size_label.setText(size_text)
        
        # معلومات الإنتاج
        self.prod_creator_label.setText(metadata.get('creator', 'غير معروف'))
        self.prod_producer_label.setText(metadata.get('producer', 'غير معروف'))
        self.prod_created_label.setText(metadata.get('creation_date', 'غير معروف'))
        self.prod_modified_label.setText(metadata.get('modification_date', 'غير معروف'))
        
        # إحصائيات
        annotations = self.pdf_handler.get_all_annotations()
        total_annotations = sum(len(anns) for anns in annotations.values())
        self.stats_annotations_label.setText(str(total_annotations))
        
        bookmarks = self.pdf_handler.get_bookmarks()
        self.stats_bookmarks_label.setText(str(len(bookmarks)))
        
        # معلومات إضافية
        extra_info = f"""
        <b>مسار الملف:</b> {metadata.get('file_path', 'غير معروف')}<br>
        <b>الكلمات المفتاحية:</b> {metadata.get('keywords', 'لا يوجد')}<br>
        <b>مشفر:</b> {'نعم' if metadata.get('is_encrypted') else 'لا'}<br>
        """
        self.extra_text.setHtml(extra_info)
    
    def update_status(self):
        """تحديث شريط الحالة"""
        if self.pdf_handler:
            total_pages = self.pdf_handler.total_pages
            self.page_status_label.setText(f"صفحة: {self.current_page + 1}/{total_pages}")
            self.status_label.setText("جاهز")
    
    def on_page_clicked(self, item):
        """عند النقر على صفحة مصغرة"""
        page_num = item.data(Qt.UserRole)
        if page_num is not None:
            self.current_page = page_num
            self.pageClicked.emit(page_num)
            self.update_status()
    
    def on_bookmark_clicked(self, item):
        """عند النقر على علامة مرجعية"""
        page_num = item.data(0, Qt.UserRole)
        if page_num is not None:
            self.current_page = page_num
            self.bookmarkClicked.emit(page_num)
            self.update_status()
    
    def on_annotation_clicked(self, item):
        """عند النقر على تعليق"""
        data = item.data(Qt.UserRole)
        if data:
            page_num, ann_id = data
            self.current_page = page_num
            self.annotationClicked.emit(page_num, ann_id)
            self.update_status()
    
    def on_search_result_clicked(self, item):
        """عند النقر على نتيجة بحث"""
        page_num = item.data(Qt.UserRole)
        if page_num is not None:
            self.current_page = page_num
            self.pageClicked.emit(page_num)
            self.update_status()
    
    def zoom_in_thumbnails(self):
        """تكبير الصور المصغرة"""
        self.thumbnail_size = min(self.thumbnail_size + 20, 200)
        self.thumbnail_size_label.setText(f"{self.thumbnail_size}%")
        self.update_thumbnails_size()
    
    def zoom_out_thumbnails(self):
        """تصغير الصور المصغرة"""
        self.thumbnail_size = max(self.thumbnail_size - 20, 50)
        self.thumbnail_size_label.setText(f"{self.thumbnail_size}%")
        self.update_thumbnails_size()
    
    def update_thumbnails_size(self):
        """تحديث حجم الصور المصغرة"""
        size = int(120 * (self.thumbnail_size / 100))
        self.pages_list.setIconSize(QSize(size, int(size * 1.4)))
    
    def toggle_sort_order(self):
        """تبديل ترتيب الصفحات"""
        # يمكن تنفيذ ترتيب تصاعدي/تنازلي هنا
        pass
    
    def filter_annotations(self, filter_text):
        """تصفية التعليقات"""
        # سيتم تنفيذ في إصدار لاحق
        pass
    
    def perform_search(self):
        """تنفيذ البحث"""
        search_text = self.search_input.text().strip()
        if not search_text or not self.pdf_handler:
            return
        
        case_sensitive = self.case_sensitive_check.isChecked()
        whole_word = self.whole_word_check.isChecked()
        
        # إرسال إشارة البحث
        self.searchRequested.emit(search_text, case_sensitive, whole_word)
    
    def go_to_prev_result(self):
        """الذهاب إلى نتيجة سابقة"""
        # سيتم تنفيذ في إصدار لاحق
        pass
    
    def go_to_next_result(self):
        """الذهاب إلى نتيجة تالية"""
        # سيتم تنفيذ في إصدار لاحق
        pass
    
    def delete_selected_annotation(self):
        """حذف التعليق المحدد"""
        current_item = self.annotations_list.currentItem()
        if not current_item:
            return
        
        data = current_item.data(Qt.UserRole)
        if not data:
            return
        
        page_num, ann_id = data
        
        if self.pdf_handler:
            self.pdf_handler.remove_annotation(page_num, ann_id)
            
            # إزالة من القائمة
            row = self.annotations_list.row(current_item)
            self.annotations_list.takeItem(row)
            
            # تحديث العد
            count = self.annotations_list.count()
            self.annotations_count_label.setText(f"{count} تعليق")
            self.delete_annotation_btn.setEnabled(count > 0)
            self.clear_annotations_btn.setEnabled(count > 0)
            
            # تحديث الإحصائيات
            self.stats_annotations_label.setText(str(count))
    
    def clear_all_annotations(self):
        """مسح جميع التعليقات"""
        if not self.pdf_handler:
            return
        
        reply = QMessageBox.question(
            self,
            "مسح التعليقات",
            "هل أنت متأكد من مسح جميع التعليقات التوضيحية؟\nلا يمكن التراجع عن هذا الإجراء.",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            self.pdf_handler.annotations.clear()
            self.pdf_handler.save_annotations()
            self.annotations_list.clear()
            
            # تحديث العد
            self.annotations_count_label.setText("0 تعليق")
            self.delete_annotation_btn.setEnabled(False)
            self.clear_annotations_btn.setEnabled(False)
            
            # تحديث الإحصائيات
            self.stats_annotations_label.setText("0")


# استيرادات إضافية لـ QComboBox
from PyQt5.QtWidgets import QComboBox


# تشغيل مباشر للاختبار
if __name__ == "__main__":
    from PyQt5.QtWidgets import QApplication
    import sys
    
    app = QApplication(sys.argv)
    sidebar = SideBar()
    sidebar.show()
    sys.exit(app.exec_())
