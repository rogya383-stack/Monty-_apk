#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Dialogs Module - النوافذ المنبثقة
Contains all dialog windows for the PDF reader
"""

from PyQt5.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QFormLayout,
    QLabel, QLineEdit, QPushButton, QCheckBox,
    QSpinBox, QComboBox, QGroupBox, QRadioButton,
    QTableWidget, QTableWidgetItem, QTextEdit,
    QDialogButtonBox, QTabWidget, QWidget,
    QFileDialog, QMessageBox, QListWidget, QListWidgetItem,
    QProgressBar, QTreeWidget, QTreeWidgetItem,
    QSlider, QFrame, QSplitter, QScrollArea,
    QSizePolicy, QSpacerItem, QApplication
)
from PyQt5.QtGui import (
    QFont, QIcon, QPixmap, QColor, QPalette,
    QIntValidator, QDoubleValidator, QRegExpValidator
)
from PyQt5.QtCore import (
    Qt, QSize, QRegExp, pyqtSignal, QTimer,
    QPropertyAnimation, QEasingCurve
)
import os
from datetime import datetime

class SearchDialog(QDialog):
    """نافذة البحث"""
    
    # إشارات
    searchRequested = pyqtSignal(str, bool, bool, bool)  # text, case, whole, regex
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("بحث في المستند")
        self.setModal(True)
        self.setMinimumWidth(500)
        
        self.init_ui()
        self.setup_connections()
    
    def init_ui(self):
        """تهيئة واجهة البحث"""
        layout = QVBoxLayout(self)
        
        # حقل البحث
        search_group = QGroupBox("بحث عن نص")
        search_layout = QVBoxLayout()
        
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("أدخل النص الذي تريد البحث عنه...")
        self.search_input.setClearButtonEnabled(True)
        search_layout.addWidget(self.search_input)
        
        search_group.setLayout(search_layout)
        layout.addWidget(search_group)
        
        # خيارات البحث
        options_group = QGroupBox("خيارات البحث")
        options_layout = QVBoxLayout()
        
        self.case_sensitive_check = QCheckBox("مطابقة حالة الأحرف (حساس للحالة)")
        options_layout.addWidget(self.case_sensitive_check)
        
        self.whole_word_check = QCheckBox("مطابقة الكلمة كاملة")
        options_layout.addWidget(self.whole_word_check)
        
        self.regex_check = QCheckBox("بحث باستخدام التعبيرات النمطية")
        options_layout.addWidget(self.regex_check)
        
        options_group.setLayout(options_layout)
        layout.addWidget(options_group)
        
        # نطاق البحث
        range_group = QGroupBox("نطاق البحث")
        range_layout = QVBoxLayout()
        
        self.whole_document_radio = QRadioButton("البحث في المستند كاملاً")
        self.whole_document_radio.setChecked(True)
        range_layout.addWidget(self.whole_document_radio)
        
        self.current_page_radio = QRadioButton("البحث في الصفحة الحالية فقط")
        range_layout.addWidget(self.current_page_radio)
        
        self.page_range_radio = QRadioButton("بحث في نطاق صفحات:")
        range_layout.addWidget(self.page_range_radio)
        
        range_widget = QWidget()
        range_h_layout = QHBoxLayout(range_widget)
        range_h_layout.setContentsMargins(20, 0, 0, 0)
        
        self.start_page_spin = QSpinBox()
        self.start_page_spin.setMinimum(1)
        self.start_page_spin.setMaximum(9999)
        self.start_page_spin.setValue(1)
        self.start_page_spin.setEnabled(False)
        range_h_layout.addWidget(self.start_page_spin)
        
        range_h_layout.addWidget(QLabel("إلى"))
        
        self.end_page_spin = QSpinBox()
        self.end_page_spin.setMinimum(1)
        self.end_page_spin.setMaximum(9999)
        self.end_page_spin.setValue(1)
        self.end_page_spin.setEnabled(False)
        range_h_layout.addWidget(self.end_page_spin)
        
        range_h_layout.addStretch()
        range_layout.addWidget(range_widget)
        
        range_group.setLayout(range_layout)
        layout.addWidget(range_group)
        
        # أزرار
        button_box = QDialogButtonBox(
            QDialogButtonBox.Ok | QDialogButtonBox.Cancel | QDialogButtonBox.Help
        )
        button_box.button(QDialogButtonBox.Ok).setText("بحث")
        button_box.button(QDialogButtonBox.Cancel).setText("إلغاء")
        button_box.button(QDialogButtonBox.Help).setText("مساعدة")
        
        layout.addWidget(button_box)
        
        # تعيين الأحجام
        self.setFixedHeight(450)
        
        # الاتصالات الخاصة بالنطاق
        self.whole_document_radio.toggled.connect(self.on_range_changed)
        self.current_page_radio.toggled.connect(self.on_range_changed)
        self.page_range_radio.toggled.connect(self.on_range_changed)
    
    def setup_connections(self):
        """إعداد الاتصالات"""
        # ربط أزرار الحوار
        buttons = self.findChild(QDialogButtonBox)
        if buttons:
            buttons.accepted.connect(self.on_search)
            buttons.rejected.connect(self.reject)
            buttons.helpRequested.connect(self.show_help)
    
    def on_range_changed(self):
        """عند تغيير نطاق البحث"""
        is_range = self.page_range_radio.isChecked()
        self.start_page_spin.setEnabled(is_range)
        self.end_page_spin.setEnabled(is_range)
    
    def on_search(self):
        """عند النقر على زر البحث"""
        search_text = self.search_input.text().strip()
        
        if not search_text:
            QMessageBox.warning(self, "تنبيه", "يرجى إدخال نص للبحث")
            self.search_input.setFocus()
            return
        
        # جمع معاملات البحث
        case_sensitive = self.case_sensitive_check.isChecked()
        whole_word = self.whole_word_check.isChecked()
        use_regex = self.regex_check.isChecked()
        
        # تحديد نطاق البحث
        if self.current_page_radio.isChecked():
            search_range = "current"
        elif self.page_range_radio.isChecked():
            search_range = (
                self.start_page_spin.value(),
                self.end_page_spin.value()
            )
        else:
            search_range = "all"
        
        # إرسال إشارة البحث
        self.searchRequested.emit(search_text, case_sensitive, whole_word, use_regex)
        
        # قبول النافذة
        self.accept()
    
    def show_help(self):
        """عرض مساعدة البحث"""
        help_text = """
        <h3>مساعدة البحث</h3>
        <p><b>البحث الأساسي:</b> أدخل النص الذي تريد البحث عنه.</p>
        <p><b>مطابقة حالة الأحرف:</b> للتمييز بين الأحرف الكبيرة والصغيرة.</p>
        <p><b>كلمة كاملة:</b> للبحث عن الكلمة كاملة وليس جزء منها.</p>
        <p><b>التعبيرات النمطية:</b> للبحث باستخدام أنماط متقدمة.</p>
        
        <h4>أمثلة على التعبيرات النمطية:</h4>
        <ul>
            <li><code>^البداية</code> - نصوص تبدأ بـ "البداية"</li>
            <li><code>النهاية$</code> - نصوص تنتهي بـ "النهاية"</li>
            <li><code>كلم.ة</code> - نقطة تطابق أي حرف واحد</li>
            <li><code>كلمة\d</code> - تطابق أرقام بعد "كلمة"</li>
        </ul>
        """
        
        QMessageBox.information(self, "مساعدة البحث", help_text)
    
    def set_page_range(self, start_page, end_page):
        """تعيين نطاق الصفحات"""
        self.start_page_spin.setMaximum(end_page)
        self.end_page_spin.setMaximum(end_page)
        self.start_page_spin.setValue(start_page)
        self.end_page_spin.setValue(end_page)
    
    def get_search_params(self):
        """الحصول على معاملات البحث"""
        return (
            self.search_input.text(),
            self.case_sensitive_check.isChecked(),
            self.whole_word_check.isChecked(),
            self.regex_check.isChecked()
        )

class GotoPageDialog(QDialog):
    """نافذة الانتقال إلى صفحة"""
    
    pageRequested = pyqtSignal(int)
    
    def __init__(self, total_pages, current_page=1, parent=None):
        super().__init__(parent)
        self.total_pages = total_pages
        self.current_page = current_page
        
        self.setWindowTitle("الانتقال إلى صفحة")
        self.setModal(True)
        self.setFixedSize(350, 200)
        
        self.init_ui()
    
    def init_ui(self):
        """تهيئة واجهة الانتقال"""
        layout = QVBoxLayout(self)
        
        # العنوان
        title_label = QLabel("انتقال إلى صفحة")
        title_label.setFont(QFont("Arial", 14, QFont.Bold))
        title_label.setAlignment(Qt.AlignCenter)
        title_label.setStyleSheet("color: #0078d7; padding: 10px;")
        layout.addWidget(title_label)
        
        # معلومات الصفحات
        info_label = QLabel(f"المستند يحتوي على {self.total_pages} صفحة")
        info_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(info_label)
        
        # حقل إدخال رقم الصفحة
        form_layout = QFormLayout()
        
        self.page_spin = QSpinBox()
        self.page_spin.setMinimum(1)
        self.page_spin.setMaximum(self.total_pages)
        self.page_spin.setValue(self.current_page)
        self.page_spin.setFixedWidth(100)
        
        form_layout.addRow("رقم الصفحة:", self.page_spin)
        
        # شريط التمرير
        self.page_slider = QSlider(Qt.Horizontal)
        self.page_slider.setMinimum(1)
        self.page_slider.setMaximum(self.total_pages)
        self.page_slider.setValue(self.current_page)
        self.page_slider.setTickPosition(QSlider.TicksBelow)
        self.page_slider.setTickInterval(max(1, self.total_pages // 10))
        
        form_layout.addRow("اختر صفحة:", self.page_slider)
        
        layout.addLayout(form_layout)
        
        # ارتباط SpinBox و Slider
        self.page_spin.valueChanged.connect(self.page_slider.setValue)
        self.page_slider.valueChanged.connect(self.page_spin.setValue)
        
        # أزرار التنقل السريع
        quick_nav_widget = QWidget()
        quick_nav_layout = QHBoxLayout(quick_nav_widget)
        
        first_btn = QPushButton("الأولى")
        first_btn.clicked.connect(lambda: self.page_spin.setValue(1))
        quick_nav_layout.addWidget(first_btn)
        
        prev_btn = QPushButton("السابقة")
        prev_btn.clicked.connect(lambda: self.page_spin.setValue(max(1, self.page_spin.value() - 1)))
        quick_nav_layout.addWidget(prev_btn)
        
        next_btn = QPushButton("التالية")
        next_btn.clicked.connect(lambda: self.page_spin.setValue(min(self.total_pages, self.page_spin.value() + 1)))
        quick_nav_layout.addWidget(next_btn)
        
        last_btn = QPushButton("الأخيرة")
        last_btn.clicked.connect(lambda: self.page_spin.setValue(self.total_pages))
        quick_nav_layout.addWidget(last_btn)
        
        layout.addWidget(quick_nav_widget)
        
        # أزرار الحوار
        button_box = QDialogButtonBox(
            QDialogButtonBox.Ok | QDialogButtonBox.Cancel
        )
        button_box.accepted.connect(self.accept)
        button_box.rejected.connect(self.reject)
        
        layout.addWidget(button_box)
    
    def get_page_number(self):
        """الحصول على رقم الصفحة"""
        return self.page_spin.value()

class SettingsDialog(QDialog):
    """نافذة الإعدادات"""
    
    settingsChanged = pyqtSignal(dict)
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("إعدادات التطبيق")
        self.setModal(True)
        self.setMinimumSize(600, 500)
        
        self.settings = {}
        self.init_ui()
    
    def init_ui(self):
        """تهيئة واجهة الإعدادات"""
        layout = QVBoxLayout(self)
        
        # علامات التبويب
        self.tab_widget = QTabWidget()
        
        # علامة تبويب عام
        self.create_general_tab()
        
        # علامة تبويب عرض
        self.create_display_tab()
        
        # علامة تبويب ملفات
        self.create_files_tab()
        
        # علامة تبويب متقدمة
        self.create_advanced_tab()
        
        layout.addWidget(self.tab_widget)
        
        # أزرار الحوار
        button_box = QDialogButtonBox(
            QDialogButtonBox.Save | QDialogButtonBox.Cancel | QDialogButtonBox.RestoreDefaults
        )
        button_box.button(QDialogButtonBox.Save).setText("حفظ")
        button_box.button(QDialogButtonBox.Cancel).setText("إلغاء")
        button_box.button(QDialogButtonBox.RestoreDefaults).setText("إعادة ضبط")
        
        button_box.accepted.connect(self.save_settings)
        button_box.rejected.connect(self.reject)
        button_box.clicked.connect(
            lambda btn: self.restore_defaults() if button_box.buttonRole(btn) == QDialogButtonBox.ResetRole else None
        )
        
        layout.addWidget(button_box)
    
    def create_general_tab(self):
        """إنشاء علامة تبويب عام"""
        general_tab = QWidget()
        layout = QVBoxLayout(general_tab)
        
        # المظهر
        appearance_group = QGroupBox("المظهر")
        appearance_layout = QFormLayout()
        
        self.theme_combo = QComboBox()
        self.theme_combo.addItems(["فاتح", "داكن", "أزرق", "أخضر", "مخصص"])
        appearance_layout.addRow("السمة:", self.theme_combo)
        
        self.language_combo = QComboBox()
        self.language_combo.addItems(["العربية", "الإنجليزية", "الفرنسية", "الألمانية"])
        appearance_layout.addRow("اللغة:", self.language_combo)
        
        self.font_combo = QComboBox()
        self.font_combo.addItems(["Arial", "Times New Roman", "Tahoma", "Segoe UI"])
        appearance_layout.addRow("الخط:", self.font_combo)
        
        self.font_size_spin = QSpinBox()
        self.font_size_spin.setRange(8, 20)
        self.font_size_spin.setValue(10)
        appearance_layout.addRow("حجم الخط:", self.font_size_spin)
        
        appearance_group.setLayout(appearance_layout)
        layout.addWidget(appearance_group)
        
        # سلوك التطبيق
        behavior_group = QGroupBox("سلوك التطبيق")
        behavior_layout = QVBoxLayout()
        
        self.auto_save_check = QCheckBox("حفظ تلقائي للتعليقات التوضيحية")
        behavior_layout.addWidget(self.auto_save_check)
        
        self.auto_load_check = QCheckBox("فتح آخر ملف عند بدء التشغيل")
        behavior_layout.addWidget(self.auto_load_check)
        
        self.confirm_exit_check = QCheckBox("طلب تأكيد عند الخروج")
        behavior_layout.addWidget(self.confirm_exit_check)
        
        self.single_instance_check = QCheckBox("تشغيل نسخة واحدة فقط من التطبيق")
        behavior_layout.addWidget(self.single_instance_check)
        
        behavior_group.setLayout(behavior_layout)
        layout.addWidget(behavior_group)
        
        spacer = QSpacerItem(20, 40, QSizePolicy.Minimum, QSizePolicy.Expanding)
        layout.addItem(spacer)
        
        self.tab_widget.addTab(general_tab, "عام")
    
    def create_display_tab(self):
        """إنشاء علامة تبويب عرض"""
        display_tab = QWidget()
        layout = QVBoxLayout(display_tab)
        
        # عرض الصفحات
        page_view_group = QGroupBox("عرض الصفحات")
        page_view_layout = QFormLayout()
        
        self.default_zoom_combo = QComboBox()
        self.default_zoom_combo.addItems(["ملاءمة للصفحة", "ملاءمة للعرض", "100%", "مخصص"])
        page_view_layout.addRow("التكبير الافتراضي:", self.default_zoom_combo)
        
        self.page_layout_combo = QComboBox()
        self.page_layout_combo.addItems(["صفحة واحدة", "وجهين", "مستمر"])
        page_view_layout.addRow("ترتيب الصفحات:", self.page_layout_combo)
        
        self.page_margin_spin = QSpinBox()
        self.page_margin_spin.setRange(0, 100)
        self.page_margin_spin.setValue(10)
        self.page_margin_spin.setSuffix(" بكسل")
        page_view_layout.addRow("هوامش الصفحة:", self.page_margin_spin)
        
        page_view_group.setLayout(page_view_layout)
        layout.addWidget(page_view_group)
        
        # الصفحات المصغرة
        thumbnails_group = QGroupBox("الصفحات المصغرة")
        thumbnails_layout = QFormLayout()
        
        self.thumbnail_size_slider = QSlider(Qt.Horizontal)
        self.thumbnail_size_slider.setRange(50, 200)
        self.thumbnail_size_slider.setValue(100)
        self.thumbnail_size_slider.setTickPosition(QSlider.TicksBelow)
        thumbnails_layout.addRow("حجم الصور المصغرة:", self.thumbnail_size_slider)
        
        self.thumbnail_quality_combo = QComboBox()
        self.thumbnail_quality_combo.addItems(["منخفض", "متوسط", "عالي", "أقصى"])
        thumbnails_layout.addRow("جودة الصور المصغرة:", self.thumbnail_quality_combo)
        
        thumbnails_group.setLayout(thumbnails_layout)
        layout.addWidget(thumbnails_group)
        
        # خيارات عرض إضافية
        extra_group = QGroupBox("خيارات إضافية")
        extra_layout = QVBoxLayout()
        
        self.show_grid_check = QCheckBox("إظهار الشبكة")
        extra_layout.addWidget(self.show_grid_check)
        
        self.show_rulers_check = QCheckBox("إظهار المساطر")
        extra_layout.addWidget(self.show_rulers_check)
        
        self.smooth_scrolling_check = QCheckBox("تمرير سلس")
        extra_layout.addWidget(self.smooth_scrolling_check)
        
        self.hardware_accel_check = QCheckBox("تسريع العتاد (إن وجد)")
        extra_layout.addWidget(self.hardware_accel_check)
        
        extra_group.setLayout(extra_layout)
        layout.addWidget(extra_group)
        
        spacer = QSpacerItem(20, 40, QSizePolicy.Minimum, QSizePolicy.Expanding)
        layout.addItem(spacer)
        
        self.tab_widget.addTab(display_tab, "عرض")
    
    def create_files_tab(self):
        """إنشاء علامة تبويب ملفات"""
        files_tab = QWidget()
        layout = QVBoxLayout(files_tab)
        
        # الملفات الحديثة
        recent_group = QGroupBox("الملفات الحديثة")
        recent_layout = QFormLayout()
        
        self.recent_files_spin = QSpinBox()
        self.recent_files_spin.setRange(5, 50)
        self.recent_files_spin.setValue(10)
        recent_layout.addRow("عدد الملفات في القائمة:", self.recent_files_spin)
        
        self.clear_recent_btn = QPushButton("مسح قائمة الملفات الحديثة")
        recent_layout.addRow("", self.clear_recent_btn)
        
        recent_group.setLayout(recent_layout)
        layout.addWidget(recent_group)
        
        # مجلدات التخزين
        storage_group = QGroupBox("مجلدات التخزين")
        storage_layout = QFormLayout()
        
        self.temp_dir_edit = QLineEdit()
        self.temp_dir_edit.setReadOnly(True)
        storage_layout.addRow("مجلد الملفات المؤقتة:", self.temp_dir_edit)
        
        self.browse_temp_btn = QPushButton("تصفح...")
        storage_layout.addRow("", self.browse_temp_btn)
        
        self.cache_dir_edit = QLineEdit()
        self.cache_dir_edit.setReadOnly(True)
        storage_layout.addRow("مجلد الذاكرة المؤقتة:", self.cache_dir_edit)
        
        self.browse_cache_btn = QPushButton("تصفح...")
        storage_layout.addRow("", self.browse_cache_btn)
        
        storage_group.setLayout(storage_layout)
        layout.addWidget(storage_group)
        
        # خيارات الملفات
        file_options_group = QGroupBox("خيارات الملفات")
        file_options_layout = QVBoxLayout()
        
        self.backup_check = QCheckBox("إنشاء نسخ احتياطية تلقائية")
        file_options_layout.addWidget(self.backup_check)
        
        self.auto_reload_check = QCheckBox("إعادة تحميل الملف تلقائياً إذا تغير")
        file_options_layout.addWidget(self.auto_reload_check)
        
        self.prompt_save_check = QCheckBox("طلب حفظ قبل إغلاق الملف")
        file_options_layout.addWidget(self.prompt_save_check)
        
        file_options_group.setLayout(file_options_layout)
        layout.addWidget(file_options_group)
        
        spacer = QSpacerItem(20, 40, QSizePolicy.Minimum, QSizePolicy.Expanding)
        layout.addItem(spacer)
        
        self.tab_widget.addTab(files_tab, "ملفات")
    
    def create_advanced_tab(self):
        """إنشاء علامة تبويب متقدمة"""
        advanced_tab = QWidget()
        layout = QVBoxLayout(advanced_tab)
        
        # أداء النظام
        performance_group = QGroupBox("أداء النظام")
        performance_layout = QFormLayout()
        
        self.cache_size_spin = QSpinBox()
        self.cache_size_spin.setRange(10, 1000)
        self.cache_size_spin.setValue(100)
        self.cache_size_spin.setSuffix(" ميجابايت")
        performance_layout.addRow("حجم الذاكرة المؤقتة:", self.cache_size_spin)
        
        self.render_threads_spin = QSpinBox()
        self.render_threads_spin.setRange(1, 8)
        self.render_threads_spin.setValue(2)
        performance_layout.addRow("خيوط التقديم:", self.render_threads_spin)
        
        self.memory_usage_slider = QSlider(Qt.Horizontal)
        self.memory_usage_slider.setRange(1, 5)
        self.memory_usage_slider.setValue(3)
        self.memory_usage_slider.setTickPosition(QSlider.TicksBelow)
        performance_layout.addRow("استخدام الذاكرة:", self.memory_usage_slider)
        
        performance_group.setLayout(performance_layout)
        layout.addWidget(performance_group)
        
        # التحديثات
        updates_group = QGroupBox("التحديثات")
        updates_layout = QVBoxLayout()
        
        self.auto_update_check = QCheckBox("التحقق تلقائياً عن التحديثات")
        updates_layout.addWidget(self.auto_update_check)
        
        self.beta_updates_check = QCheckBox("تلقي تحديثات بيتا")
        updates_layout.addWidget(self.beta_updates_check)
        
        self.check_now_btn = QPushButton("التحقق عن تحديثات الآن")
        updates_layout.addWidget(self.check_now_btn)
        
        updates_group.setLayout(updates_layout)
        layout.addWidget(updates_group)
        
        # إعدادات متقدمة
        expert_group = QGroupBox("إعدادات للمستخدمين المتقدمين")
        expert_layout = QVBoxLayout()
        
        self.enable_logging_check = QCheckBox("تفعيل التسجيل (Logging)")
        expert_layout.addWidget(self.enable_logging_check)
        
        self.debug_mode_check = QCheckBox("وضع التصحيح (Debug)")
        expert_layout.addWidget(self.debug_mode_check)
        
        self.reset_settings_btn = QPushButton("إعادة ضبط جميع الإعدادات")
        expert_layout.addWidget(self.reset_settings_btn)
        
        expert_group.setLayout(expert_layout)
        layout.addWidget(expert_group)
        
        spacer = QSpacerItem(20, 40, QSizePolicy.Minimum, QSizePolicy.Expanding)
        layout.addItem(spacer)
        
        self.tab_widget.addTab(advanced_tab, "متقدم")
    
    def save_settings(self):
        """حفظ الإعدادات"""
        self.settings = {
            'theme': self.theme_combo.currentText(),
            'language': self.language_combo.currentText(),
            'font': self.font_combo.currentText(),
            'font_size': self.font_size_spin.value(),
            'auto_save': self.auto_save_check.isChecked(),
            'auto_load': self.auto_load_check.isChecked(),
            'confirm_exit': self.confirm_exit_check.isChecked(),
            'single_instance': self.single_instance_check.isChecked(),
            'default_zoom': self.default_zoom_combo.currentText(),
            'page_layout': self.page_layout_combo.currentText(),
            'page_margin': self.page_margin_spin.value(),
            'thumbnail_size': self.thumbnail_size_slider.value(),
            'thumbnail_quality': self.thumbnail_quality_combo.currentText(),
            'show_grid': self.show_grid_check.isChecked(),
            'show_rulers': self.show_rulers_check.isChecked(),
            'smooth_scrolling': self.smooth_scrolling_check.isChecked(),
            'hardware_accel': self.hardware_accel_check.isChecked(),
            'recent_files_count': self.recent_files_spin.value(),
            'backup_files': self.backup_check.isChecked(),
            'auto_reload': self.auto_reload_check.isChecked(),
            'prompt_save': self.prompt_save_check.isChecked(),
            'cache_size': self.cache_size_spin.value(),
            'render_threads': self.render_threads_spin.value(),
            'memory_usage': self.memory_usage_slider.value(),
            'auto_update': self.auto_update_check.isChecked(),
            'beta_updates': self.beta_updates_check.isChecked(),
            'enable_logging': self.enable_logging_check.isChecked(),
            'debug_mode': self.debug_mode_check.isChecked()
        }
        
        self.settingsChanged.emit(self.settings)
        self.accept()
    
    def restore_defaults(self):
        """إعادة الإعدادات إلى الوضع الافتراضي"""
        reply = QMessageBox.question(
            self,
            "إعادة الضبط",
            "هل تريد إعادة جميع الإعدادات إلى القيم الافتراضية؟",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            # إعادة تعيين جميع عناصر التحكم
            self.theme_combo.setCurrentIndex(0)
            self.language_combo.setCurrentIndex(0)
            self.font_combo.setCurrentIndex(0)
            self.font_size_spin.setValue(10)
            self.auto_save_check.setChecked(True)
            self.auto_load_check.setChecked(True)
            self.confirm_exit_check.setChecked(True)
            self.single_instance_check.setChecked(False)
            self.default_zoom_combo.setCurrentIndex(0)
            self.page_layout_combo.setCurrentIndex(0)
            self.page_margin_spin.setValue(10)
            self.thumbnail_size_slider.setValue(100)
            self.thumbnail_quality_combo.setCurrentIndex(2)
            self.show_grid_check.setChecked(False)
            self.show_rulers_check.setChecked(False)
            self.smooth_scrolling_check.setChecked(True)
            self.hardware_accel_check.setChecked(True)
            self.recent_files_spin.setValue(10)
            self.backup_check.setChecked(True)
            self.auto_reload_check.setChecked(False)
            self.prompt_save_check.setChecked(True)
            self.cache_size_spin.setValue(100)
            self.render_threads_spin.setValue(2)
            self.memory_usage_slider.setValue(3)
            self.auto_update_check.setChecked(True)
            self.beta_updates_check.setChecked(False)
            self.enable_logging_check.setChecked(False)
            self.debug_mode_check.setChecked(False)
    
    def load_settings(self, settings):
        """تحميل الإعدادات"""
        if not settings:
            return
        
        # تحميل الإعدادات في عناصر التحكم
        # (سيتم تنفيذ بالكامل في الإصدار النهائي)
        pass

class ExportDialog(QDialog):
    """نافذة التصدير"""
    
    exportRequested = pyqtSignal(str, int, int, bool, str)
    
    def __init__(self, total_pages, parent=None):
        super().__init__(parent)
        self.total_pages = total_pages
        
        self.setWindowTitle("تصدير المستند")
        self.setModal(True)
        self.setMinimumWidth(500)
        
        self.init_ui()
    
    def init_ui(self):
        """تهيئة واجهة التصدير"""
        layout = QVBoxLayout(self)
        
        # نوع التصدير
        type_group = QGroupBox("نوع الملف")
        type_layout = QVBoxLayout()
        
        self.text_radio = QRadioButton("نص (.txt)")
        self.text_radio.setChecked(True)
        type_layout.addWidget(self.text_radio)
        
        self.pdf_radio = QRadioButton("PDF (.pdf)")
        type_layout.addWidget(self.pdf_radio)
        
        self.word_radio = QRadioButton("مستند Word (.docx)")
        type_layout.addWidget(self.word_radio)
        
        self.html_radio = QRadioButton("HTML (.html)")
        type_layout.addWidget(self.html_radio)
        
        self.images_radio = QRadioButton("صور (.png/.jpg)")
        type_layout.addWidget(self.images_radio)
        
        type_group.setLayout(type_layout)
        layout.addWidget(type_group)
        
        # نطاق الصفحات
        range_group = QGroupBox("نطاق الصفحات")
        range_layout = QVBoxLayout()
        
        self.all_pages_radio = QRadioButton("جميع الصفحات")
        self.all_pages_radio.setChecked(True)
        range_layout.addWidget(self.all_pages_radio)
        
        self.current_page_radio = QRadioButton("الصفحة الحالية فقط")
        range_layout.addWidget(self.current_page_radio)
        
        self.range_radio = QRadioButton("نطاق صفحات:")
        range_layout.addWidget(self.range_radio)
        
        range_widget = QWidget()
        range_h_layout = QHBoxLayout(range_widget)
        range_h_layout.setContentsMargins(20, 0, 0, 0)
        
        self.start_spin = QSpinBox()
        self.start_spin.setMinimum(1)
        self.start_spin.setMaximum(self.total_pages)
        self.start_spin.setValue(1)
        self.start_spin.setEnabled(False)
        range_h_layout.addWidget(self.start_spin)
        
        range_h_layout.addWidget(QLabel("إلى"))
        
        self.end_spin = QSpinBox()
        self.end_spin.setMinimum(1)
        self.end_spin.setMaximum(self.total_pages)
        self.end_spin.setValue(self.total_pages)
        self.end_spin.setEnabled(False)
        range_h_layout.addWidget(self.end_spin)
        
        range_h_layout.addStretch()
        range_layout.addWidget(range_widget)
        
        # خيارات الصفحات المحددة
        self.selected_pages_radio = QRadioButton("صفحات محددة:")
        range_layout.addWidget(self.selected_pages_radio)
        
        self.selected_pages_edit = QLineEdit()
        self.selected_pages_edit.setPlaceholderText("مثال: 1,3,5-8,10")
        self.selected_pages_edit.setEnabled(False)
        range_layout.addWidget(self.selected_pages_edit)
        
        range_group.setLayout(range_layout)
        layout.addWidget(range_group)
        
        # خيارات إضافية
        options_group = QGroupBox("خيارات إضافية")
        options_layout = QVBoxLayout()
        
        self.include_comments_check = QCheckBox("تضمين التعليقات التوضيحية")
        options_layout.addWidget(self.include_comments_check)
        
        self.include_bookmarks_check = QCheckBox("تضمين العلامات المرجعية")
        options_layout.addWidget(self.include_bookmarks_check)
        
        self.preserve_layout_check = QCheckBox("الحفاظ على تخطيط الصفحة")
        options_layout.addWidget(self.preserve_layout_check)
        
        options_group.setLayout(options_layout)
        layout.addWidget(options_group)
        
        # جودة التصدير (للصور)
        self.quality_group = QGroupBox("جودة الصور")
        self.quality_group.setVisible(False)
        quality_layout = QFormLayout()
        
        self.quality_slider = QSlider(Qt.Horizontal)
        self.quality_slider.setRange(1, 100)
        self.quality_slider.setValue(90)
        quality_layout.addRow("جودة الضغط:", self.quality_slider)
        
        self.format_combo = QComboBox()
        self.format_combo.addItems(["PNG", "JPEG", "TIFF", "BMP"])
        quality_layout.addRow("صيغة الملف:", self.format_combo)
        
        self.quality_group.setLayout(quality_layout)
        layout.addWidget(self.quality_group)
        
        # أزرار
        button_box = QDialogButtonBox(
            QDialogButtonBox.Ok | QDialogButtonBox.Cancel
        )
        button_box.accepted.connect(self.on_export)
        button_box.rejected.connect(self.reject)
        
        layout.addWidget(button_box)
        
        # الاتصالات
        self.all_pages_radio.toggled.connect(self.on_range_changed)
        self.current_page_radio.toggled.connect(self.on_range_changed)
        self.range_radio.toggled.connect(self.on_range_changed)
        self.selected_pages_radio.toggled.connect(self.on_range_changed)
        
        self.images_radio.toggled.connect(
            lambda checked: self.quality_group.setVisible(checked)
        )
    
    def on_range_changed(self):
        """عند تغيير نطاق الصفحات"""
        self.start_spin.setEnabled(self.range_radio.isChecked())
        self.end_spin.setEnabled(self.range_radio.isChecked())
        self.selected_pages_edit.setEnabled(self.selected_pages_radio.isChecked())
    
    def on_export(self):
        """عند النقر على تصدير"""
        # تحديد نوع الملف
        if self.text_radio.isChecked():
            file_type = "txt"
        elif self.pdf_radio.isChecked():
            file_type = "pdf"
        elif self.word_radio.isChecked():
            file_type = "docx"
        elif self.html_radio.isChecked():
            file_type = "html"
        else:
            file_type = "images"
        
        # تحديد نطاق الصفحات
        if self.all_pages_radio.isChecked():
            start_page = 0
            end_page = self.total_pages - 1
        elif self.current_page_radio.isChecked():
            # سيتم الحصول من الوالد
            start_page = end_page = 0
        elif self.range_radio.isChecked():
            start_page = self.start_spin.value() - 1
            end_page = self.end_spin.value() - 1
        else:
            # صفحات محددة
            pages_text = self.selected_pages_edit.text()
            # سيتم معالجة النص لاستخراج الأرقام
            start_page = 0
            end_page = self.total_pages - 1
        
        # خيارات إضافية
        include_comments = self.include_comments_check.isChecked()
        quality = self.quality_slider.value() if file_type == "images" else 0
        format_str = self.format_combo.currentText() if file_type == "images" else ""
        
        # إرسال إشارة التصدير
        self.exportRequested.emit(file_type, start_page, end_page, include_comments, format_str)
        
        # قبول النافذة
        self.accept()
    
    def get_export_params(self):
        """الحصول على معاملات التصدير"""
        return {
            'file_type': "txt" if self.text_radio.isChecked() else 
                        "pdf" if self.pdf_radio.isChecked() else 
                        "docx" if self.word_radio.isChecked() else 
                        "html" if self.html_radio.isChecked() else "images",
            'start_page': 0 if self.all_pages_radio.isChecked() else self.start_spin.value() - 1,
            'end_page': self.total_pages - 1 if self.all_pages_radio.isChecked() else self.end_spin.value() - 1,
            'include_comments': self.include_comments_check.isChecked(),
            'quality': self.quality_slider.value(),
            'format': self.format_combo.currentText()
        }

class PropertiesDialog(QDialog):
    """نافذة خصائص الملف"""
    
    def __init__(self, metadata, parent=None):
        super().__init__(parent)
        self.metadata = metadata
        
        self.setWindowTitle("خصائص المستند")
        self.setModal(True)
        self.setMinimumSize(500, 400)
        
        self.init_ui()
    
    def init_ui(self):
        """تهيئة واجهة الخصائص"""
        layout = QVBoxLayout(self)
        
        # علامات التبويب
        self.tab_widget = QTabWidget()
        
        # علامة تبويب الوصف
        self.create_description_tab()
        
        # علامة تبويب الأمان
        self.create_security_tab()
        
        # علامة تبويب متقدمة
        self.create_advanced_tab()
        
        layout.addWidget(self.tab_widget)
        
        # أزرار
        button_box = QDialogButtonBox(QDialogButtonBox.Close)
        button_box.rejected.connect(self.reject)
        
        layout.addWidget(button_box)
    
    def create_description_tab(self):
        """إنشاء علامة تبويب الوصف"""
        desc_tab = QWidget()
        layout = QFormLayout(desc_tab)
        
        # معلومات الملف الأساسية
        self.add_form_row(layout, "العنوان:", self.metadata.get('title', 'غير معروف'))
        self.add_form_row(layout, "المؤلف:", self.metadata.get('author', 'غير معروف'))
        self.add_form_row(layout, "الموضوع:", self.metadata.get('subject', 'غير معروف'))
        self.add_form_row(layout, "الكلمات المفتاحية:", self.metadata.get('keywords', 'لا يوجد'))
        
        layout.addItem(QSpacerItem(20, 20))
        
        # معلومات الإنتاج
        self.add_form_row(layout, "المنشئ:", self.metadata.get('creator', 'غير معروف'))
        self.add_form_row(layout, "المنتج:", self.metadata.get('producer', 'غير معروف'))
        
        layout.addItem(QSpacerItem(20, 20))
        
        # معلومات التواريخ
        self.add_form_row(layout, "تاريخ الإنشاء:", self.metadata.get('creation_date', 'غير معروف'))
        self.add_form_row(layout, "آخر تعديل:", self.metadata.get('modification_date', 'غير معروف'))
        
        layout.addItem(QSpacerItem(20, 20))
        
        # معلومات الملف
        self.add_form_row(layout, "عدد الصفحات:", str(self.metadata.get('pages', 0)))
        
        file_size = self.metadata.get('file_size', 0)
        if file_size > 1024*1024:
            size_text = f"{file_size/(1024*1024):.2f} MB"
        elif file_size > 1024:
            size_text = f"{file_size/1024:.2f} KB"
        else:
            size_text = f"{file_size} بايت"
        
        self.add_form_row(layout, "حجم الملف:", size_text)
        
        self.tab_widget.addTab(desc_tab, "الوصف")
    
    def create_security_tab(self):
        """إنشاء علامة تبويب الأمان"""
        security_tab = QWidget()
        layout = QFormLayout(security_tab)
        
        # معلومات الأمان
        is_encrypted = self.metadata.get('is_encrypted', False)
        self.add_form_row(layout, "مشفر:", "نعم" if is_encrypted else "لا")
        
        permissions = self.metadata.get('permissions', -1)
        if permissions != -1:
            perms_text = self.decode_permissions(permissions)
            self.add_form_row(layout, "الصلاحيات:", perms_text)
        
        # معلومات إضافية
        self.add_form_row(layout, "نوع الملف:", "PDF")
        self.add_form_row(layout, "إصدار PDF:", "1.7")  # يمكن استخراجها من الميتاداتا
        
        self.tab_widget.addTab(security_tab, "الأمان")
    
    def create_advanced_tab(self):
        """إنشاء علامة تبويب متقدمة"""
        advanced_tab = QWidget()
        layout = QVBoxLayout(advanced_tab)
        
        # عرض الميتاداتا الخام
        metadata_text = QTextEdit()
        metadata_text.setReadOnly(True)
        metadata_text.setFont(QFont("Courier New", 9))
        
        # تنسيق الميتاداتا
        formatted_metadata = ""
        for key, value in self.metadata.items():
            formatted_metadata += f"{key}: {value}\n"
        
        metadata_text.setText(formatted_metadata)
        layout.addWidget(metadata_text)
        
        self.tab_widget.addTab(advanced_tab, "متقدم")
    
    def add_form_row(self, layout, label, value):
        """إضافة صف إلى النموذج"""
        value_label = QLabel(str(value))
        value_label.setStyleSheet("font-weight: normal; color: #333333;")
        layout.addRow(QLabel(f"<b>{label}</b>"), value_label)
    
    def decode_permissions(self, permissions):
        """فك تشفير صلاحيات PDF"""
        perms = []
        
        if permissions & 1 << 2:  # يمكن الطباعة
            perms.append("طباعة")
        if permissions & 1 << 3:  # يمكن التعديل
            perms.append("تعديل")
        if permissions & 1 << 4:  # يمكن نسخ
            perms.append("نسخ")
        if permissions & 1 << 5:  # يمكن تعديل التعليقات
            perms.append("تعديل التعليقات")
        
        return ", ".join(perms) if perms else "مقيد"

class AboutDialog(QDialog):
    """نافذة حول التطبيق"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("حول قارئ PDF")
        self.setModal(True)
        self.setFixedSize(500, 400)
        
        self.init_ui()
    
    def init_ui(self):
        """تهيئة واجهة حول"""
        layout = QVBoxLayout(self)
        
        # العنوان
        title_label = QLabel("قارئ PDF احترافي")
        title_label.setFont(QFont("Arial", 18, QFont.Bold))
        title_label.setAlignment(Qt.AlignCenter)
        title_label.setStyleSheet("color: #0078d7; padding: 20px;")
        layout.addWidget(title_label)
        
        # الإصدار
        version_label = QLabel("الإصدار 1.0.0")
        version_label.setAlignment(Qt.AlignCenter)
        version_label.setStyleSheet("color: #666666;")
        layout.addWidget(version_label)
        
        # وصف
        desc_label = QLabel(
            "تطبيق مفتوح المصدر لقراءة ومعالجة ملفات PDF\n"
            "بميزات متقدمة وواجهة مستخدم عربية كاملة"
        )
        desc_label.setAlignment(Qt.AlignCenter)
        desc_label.setWordWrap(True)
        layout.addWidget(desc_label)
        
        # معلومات الرخصة
        license_group = QGroupBox("الترخيص")
        license_layout = QVBoxLayout()
        
        license_label = QLabel(
            "هذا البرنامج مرخص تحت رخصة MIT.\n"
            "يمكن استخدامه، تعديله، وتوزيعه بحرية."
        )
        license_label.setWordWrap(True)
        license_layout.addWidget(license_label)
        
        license_group.setLayout(license_layout)
        layout.addWidget(license_group)
        
        # المكتبات المستخدمة
        libs_group = QGroupBox("المكتبات المستخدمة")
        libs_layout = QVBoxLayout()
        
        libs_text = QTextEdit()
        libs_text.setReadOnly(True)
        libs_text.setMaximumHeight(100)
        libs_text.setPlainText(
            "• PyMuPDF - لمعالجة PDF\n"
            "• PyQt5 - لواجهة المستخدم\n"
            "• pdfplumber - لاستخراج النصوص\n"
            "• Pillow - لمعالجة الصور\n"
            "• reportlab - لإنشاء PDF"
        )
        libs_layout.addWidget(libs_text)
        
        libs_group.setLayout(libs_layout)
        layout.addWidget(libs_group)
        
        # معلومات المطور
        dev_label = QLabel("المطور: فريق قارئ PDF\n© 2024 جميع الحقوق محفوظة")
        dev_label.setAlignment(Qt.AlignCenter)
        dev_label.setStyleSheet("color: #888888; font-size: 10pt;")
        layout.addWidget(dev_label)
        
        # أزرار
        button_box = QDialogButtonBox(QDialogButtonBox.Close)
        button_box.rejected.connect(self.reject)
        
        layout.addWidget(button_box)
        
        # تأثيرات
        self.setStyleSheet("""
            QDialog {
                background-color: #f5f5f5;
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

# حوارات إضافية يمكن إضافتها لاحقاً

class ProgressDialog(QDialog):
    """نافذة تقدم"""
    
    def __init__(self, title="جاري المعالجة", parent=None):
        super().__init__(parent)
        self.setWindowTitle(title)
        self.setModal(True)
        self.setFixedSize(400, 150)
        
        self.init_ui()
    
    def init_ui(self):
        """تهيئة واجهة التقدم"""
        layout = QVBoxLayout(self)
        
        # الرسالة
        self.message_label = QLabel("جاري معالجة الطلب...")
        self.message_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(self.message_label)
        
        # شريط التقدم
        self.progress_bar = QProgressBar()
        self.progress_bar.setRange(0, 100)
        self.progress_bar.setValue(0)
        layout.addWidget(self.progress_bar)
        
        # التسمية المئوية
        self.percentage_label = QLabel("0%")
        self.percentage_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(self.percentage_label)
        
        # زر الإلغاء
        self.cancel_btn = QPushButton("إلغاء")
        self.cancel_btn.clicked.connect(self.reject)
        layout.addWidget(self.cancel_btn)
    
    def update_progress(self, value, message=None):
        """تحديث التقدم"""
        self.progress_bar.setValue(value)
        self.percentage_label.setText(f"{value}%")
        
        if message:
            self.message_label.setText(message)
        
        QApplication.processEvents()
    
    def set_range(self, minimum, maximum):
        """تعيين نطاق التقدم"""
        self.progress_bar.setRange(minimum, maximum)

class MessageDialog(QDialog):
    """نافذة رسائل مخصصة"""
    
    def __init__(self, title, message, icon=QMessageBox.Information, parent=None):
        super().__init__(parent)
        self.setWindowTitle(title)
        self.setModal(True)
        self.setFixedSize(400, 200)
        
        self.init_ui(message, icon)
    
    def init_ui(self, message, icon):
        """تهيئة واجهة الرسالة"""
        layout = QVBoxLayout(self)
        
        # الأيقونة
        icon_label = QLabel()
        icon_pixmap = self.get_icon_pixmap(icon)
        if icon_pixmap:
            icon_label.setPixmap(icon_pixmap)
            icon_label.setAlignment(Qt.AlignCenter)
            layout.addWidget(icon_label)
        
        # الرسالة
        message_label = QLabel(message)
        message_label.setAlignment(Qt.AlignCenter)
        message_label.setWordWrap(True)
        layout.addWidget(message_label)
        
        # أزرار
        button_box = QDialogButtonBox(QDialogButtonBox.Ok)
        button_box.accepted.connect(self.accept)
        layout.addWidget(button_box)
    
    def get_icon_pixmap(self, icon):
        """الحصول على أيقونة حسب النوع"""
        # يمكن إضافة أيقونات مخصصة هنا
        return None

# اختبار الحوارات
if __name__ == "__main__":
    from PyQt5.QtWidgets import QApplication
    import sys
    
    app = QApplication(sys.argv)
    
    # اختبار نافذة حول
    about_dialog = AboutDialog()
    about_dialog.exec_()
    
    # اختبار نافذة الإعدادات
    settings_dialog = SettingsDialog()
    settings_dialog.exec_()
    
    sys.exit(app.exec_())
