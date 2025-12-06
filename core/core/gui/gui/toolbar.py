#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Toolbar Module - شريط الأدوات
"""

from PyQt5.QtWidgets import (
    QToolBar, QAction, QWidget, QHBoxLayout, QLabel, 
    QComboBox, QPushButton, QSpinBox, QFrame
)
from PyQt5.QtGui import QIcon, QFont, QPixmap
from PyQt5.QtCore import Qt, QSize, pyqtSignal

class MainToolBar(QToolBar):
    """شريط الأدوات الرئيسي"""
    
    # إشارات
    actionTriggered = pyqtSignal(str, object)  # (action_name, data)
    zoomChanged = pyqtSignal(float)
    pageChanged = pyqtSignal(int)
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.parent = parent
        self.current_zoom = 100
        self.current_page = 1
        self.total_pages = 1
        
        self.init_ui()
        self.setup_actions()
    
    def init_ui(self):
        """تهيئة واجهة شريط الأدوات"""
        self.setWindowTitle("الأدوات الرئيسية")
        self.setMovable(False)
        self.setIconSize(QSize(24, 24))
        self.setToolButtonStyle(Qt.ToolButtonIconOnly)
        self.setStyleSheet("""
            QToolBar {
                background-color: #f0f0f0;
                border-bottom: 1px solid #cccccc;
                spacing: 5px;
                padding: 3px;
            }
            QToolButton {
                padding: 5px;
                border-radius: 3px;
            }
            QToolButton:hover {
                background-color: #e0e0e0;
            }
            QToolButton:checked {
                background-color: #d0d0d0;
                border: 1px solid #a0a0a0;
            }
        """)
    
    def setup_actions(self):
        """إعداد الإجراءات"""
        # ملف
        self.add_file_actions()
        self.addSeparator()
        
        # التنقل
        self.add_navigation_actions()
        self.addSeparator()
        
        # التكبير/التصغير
        self.add_zoom_actions()
        self.addSeparator()
        
        # العرض
        self.add_view_actions()
        self.addSeparator()
        
        # البحث
        self.add_search_actions()
        self.addSeparator()
        
        # التعليقات التوضيحية
        self.add_annotation_actions()
    
    def add_file_actions(self):
        """إضافة إجراءات الملف"""
        # فتح
        self.open_action = self.create_action(
            "فتح",
            "📂",
            "فتح ملف PDF",
            lambda: self.actionTriggered.emit("open", None)
        )
        self.addAction(self.open_action)
        
        # حفظ
        self.save_action = self.create_action(
            "حفظ",
            "💾",
            "حفظ الملف",
            lambda: self.actionTriggered.emit("save", None)
        )
        self.addAction(self.save_action)
        
        # طباعة
        self.print_action = self.create_action(
            "طباعة",
            "🖨️",
            "طباعة الملف",
            lambda: self.actionTriggered.emit("print", None)
        )
        self.addAction(self.print_action)
    
    def add_navigation_actions(self):
        """إضافة إجراءات التنقل"""
        # أول صفحة
        self.first_action = self.create_action(
            "أول",
            "⏮",
            "الصفحة الأولى",
            lambda: self.actionTriggered.emit("first_page", None)
        )
        self.addAction(self.first_action)
        
        # صفحة سابقة
        self.prev_action = self.create_action(
            "سابق",
            "◀",
            "الصفحة السابقة",
            lambda: self.actionTriggered.emit("prev_page", None)
        )
        self.addAction(self.prev_action)
        
        # عناصر التحكم بالصفحات
        self.add_page_controls()
        
        # صفحة تالية
        self.next_action = self.create_action(
            "تالي",
            "▶",
            "الصفحة التالية",
            lambda: self.actionTriggered.emit("next_page", None)
        )
        self.addAction(self.next_action)
        
        # آخر صفحة
        self.last_action = self.create_action(
            "آخر",
            "⏭",
            "الصفحة الأخيرة",
            lambda: self.actionTriggered.emit("last_page", None)
        )
        self.addAction(self.last_action)
    
    def add_page_controls(self):
        """إضافة عناصر التحكم بالصفحات"""
        page_widget = QWidget()
        layout = QHBoxLayout(page_widget)
        layout.setContentsMargins(5, 0, 5, 0)
        layout.setSpacing(5)
        
        # تسمية الصفحة
        page_label = QLabel("صفحة:")
        page_label.setFont(QFont("Arial", 9))
        layout.addWidget(page_label)
        
        # مربع رقم الصفحة
        self.page_spin = QSpinBox()
        self.page_spin.setMinimum(1)
        self.page_spin.setMaximum(1)
        self.page_spin.setValue(1)
        self.page_spin.setFixedWidth(60)
        self.page_spin.valueChanged.connect(
            lambda v: self.actionTriggered.emit("goto_page", v-1)
        )
        layout.addWidget(self.page_spin)
        
        # تسمية العدد الكلي
        self.total_label = QLabel("/ 1")
        self.total_label.setFont(QFont("Arial", 9))
        layout.addWidget(self.total_label)
        
        self.addWidget(page_widget)
    
    def add_zoom_actions(self):
        """إضافة إجراءات التكبير"""
        # تصغير
        self.zoom_out_action = self.create_action(
            "تصغير",
            "➖",
            "تصغير",
            lambda: self.actionTriggered.emit("zoom_out", None)
        )
        self.addAction(self.zoom_out_action)
        
        # عناصر التحكم بالتكبير
        self.add_zoom_controls()
        
        # تكبير
        self.zoom_in_action = self.create_action(
            "تكبير",
            "➕",
            "تكبير",
            lambda: self.actionTriggered.emit("zoom_in", None)
        )
        self.addAction(self.zoom_in_action)
    
    def add_zoom_controls(self):
        """إضافة عناصر التحكم بالتكبير"""
        zoom_widget = QWidget()
        layout = QHBoxLayout(zoom_widget)
        layout.setContentsMargins(5, 0, 5, 0)
        layout.setSpacing(5)
        
        # قائمة التكبير
        self.zoom_combo = QComboBox()
        self.zoom_combo.setFixedWidth(80)
        self.zoom_combo.addItems([
            "25%", "50%", "75%", "100%", "125%", "150%", "200%", "300%", "400%"
        ])
        self.zoom_combo.setCurrentText("100%")
        self.zoom_combo.currentTextChanged.connect(
            lambda t: self.actionTriggered.emit("zoom_to", float(t.replace("%", "")) / 100)
        )
        layout.addWidget(self.zoom_combo)
        
        # زر ملاءمة العرض
        self.fit_action = self.create_action(
            "ملاءمة",
            "🗘",
            "ملاءمة للعرض",
            lambda: self.actionTriggered.emit("zoom_fit", None),
            add_to_toolbar=False
        )
        fit_btn = QPushButton("🗘")
        fit_btn.setToolTip("ملاءمة للعرض")
        fit_btn.setFixedSize(30, 30)
        fit_btn.clicked.connect(self.fit_action.trigger)
        layout.addWidget(fit_btn)
        
        self.addWidget(zoom_widget)
    
    def add_view_actions(self):
        """إضافة إجراءات العرض"""
        # تدوير لليسار
        self.rotate_left_action = self.create_action(
            "يسار",
            "↶",
            "تدوير لليسار",
            lambda: self.actionTriggered.emit("rotate_left", None)
        )
        self.addAction(self.rotate_left_action)
        
        # تدوير لليمين
        self.rotate_right_action = self.create_action(
            "يمين",
            "↷",
            "تدوير لليمين",
            lambda: self.actionTriggered.emit("rotate_right", None)
        )
        self.addAction(self.rotate_right_action)
        
        # فاصل
        self.addSeparator()
        
        # وضع العرض
        view_widget = QWidget()
        layout = QHBoxLayout(view_widget)
        layout.setContentsMargins(5, 0, 5, 0)
        
        self.view_combo = QComboBox()
        self.view_combo.addItems(["صفحة واحدة", "وجهين", "مستمر"])
        self.view_combo.setFixedWidth(120)
        self.view_combo.currentTextChanged.connect(
            lambda t: self.actionTriggered.emit("view_mode", t)
        )
        layout.addWidget(self.view_combo)
        
        self.addWidget(view_widget)
    
    def add_search_actions(self):
        """إضافة إجراءات البحث"""
        # بحث
        self.search_action = self.create_action(
            "بحث",
            "🔍",
            "بحث في المستند",
            lambda: self.actionTriggered.emit("search", None)
        )
        self.addAction(self.search_action)
        
        # بحث تالي
        self.find_next_action = self.create_action(
            "تالي",
            "⏭",
            "بحث عن التالي",
            lambda: self.actionTriggered.emit("find_next", None)
        )
        self.addAction(self.find_next_action)
        
        # بحث سابق
        self.find_prev_action = self.create_action(
            "سابق",
            "⏮",
            "بحث عن السابق",
            lambda: self.actionTriggered.emit("find_prev", None)
        )
        self.addAction(self.find_prev_action)
    
    def add_annotation_actions(self):
        """إضافة إجراءات التعليقات"""
        # أداة اليد
        self.hand_action = self.create_action(
            "يد",
            "✋",
            "أداة اليد",
            lambda: self.actionTriggered.emit("tool_hand", None),
            checkable=True,
            checked=True
        )
        self.addAction(self.hand_action)
        
        # أداة التحديد
        self.select_action = self.create_action(
            "تحديد",
            "☐",
            "أداة التحديد",
            lambda: self.actionTriggered.emit("tool_select", None),
            checkable=True
        )
        self.addAction(self.select_action)
        
        # فاصل
        self.addSeparator()
        
        # تظليل
        self.highlight_action = self.create_action(
            "تظليل",
            "🖍️",
            "تظليل النص",
            lambda: self.actionTriggered.emit("tool_highlight", None),
            checkable=True
        )
        self.addAction(self.highlight_action)
        
        # خط سفلي
        self.underline_action = self.create_action(
            "خط",
            "⎁",
            "خط سفلي",
            lambda: self.actionTriggered.emit("tool_underline", None),
            checkable=True
        )
        self.addAction(self.underline_action)
        
        # خط علوي
        self.strike_action = self.create_action(
            "شطب",
            "☓",
            "شطب النص",
            lambda: self.actionTriggered.emit("tool_strike", None),
            checkable=True
        )
        self.addAction(self.strike_action)
        
        # فاصل
        self.addSeparator()
        
        # مستطيل
        self.rectangle_action = self.create_action(
            "مربع",
            "▭",
            "رسم مستطيل",
            lambda: self.actionTriggered.emit("tool_rectangle", None),
            checkable=True
        )
        self.addAction(self.rectangle_action)
        
        # دائرة
        self.circle_action = self.create_action(
            "دائرة",
            "○",
            "رسم دائرة",
            lambda: self.actionTriggered.emit("tool_circle", None),
            checkable=True
        )
        self.addAction(self.circle_action)
        
        # ملاحظة
        self.note_action = self.create_action(
            "ملاحظة",
            "📝",
            "إضافة ملاحظة",
            lambda: self.actionTriggered.emit("tool_note", None),
            checkable=True
        )
        self.addAction(self.note_action)
    
    def create_action(self, text, icon, tooltip, callback, 
                     checkable=False, checked=False, add_to_toolbar=True):
        """إنشاء إجراء"""
        action = QAction(icon, text, self)
        action.setToolTip(tooltip)
        action.triggered.connect(callback)
        
        if checkable:
            action.setCheckable(True)
            action.setChecked(checked)
        
        if add_to_toolbar:
            self.addAction(action)
        
        return action
    
    def update_page_info(self, current_page, total_pages):
        """تحديث معلومات الصفحات"""
        self.current_page = current_page + 1
        self.total_pages = total_pages
        
        self.page_spin.blockSignals(True)
        self.page_spin.setMaximum(total_pages)
        self.page_spin.setValue(self.current_page)
        self.page_spin.blockSignals(False)
        
        self.total_label.setText(f"/ {total_pages}")
    
    def update_zoom_info(self, zoom_level):
        """تحديث معلومات التكبير"""
        zoom_percent = int(zoom_level * 100)
        self.current_zoom = zoom_percent
        
        # تحديث قائمة التكبير
        zoom_text = f"{zoom_percent}%"
        index = self.zoom_combo.findText(zoom_text)
        
        if index >= 0:
            self.zoom_combo.blockSignals(True)
            self.zoom_combo.setCurrentIndex(index)
            self.zoom_combo.blockSignals(False)
        else:
            # إضافة الخيار الجديد
            self.zoom_combo.addItem(zoom_text)
            self.zoom_combo.setCurrentText(zoom_text)
    
    def set_active_tool(self, tool_name):
        """تعيين الأداة النشطة"""
        # إلغاء تفعيل جميع الأدوات
        self.hand_action.setChecked(False)
        self.select_action.setChecked(False)
        self.highlight_action.setChecked(False)
        self.underline_action.setChecked(False)
        self.strike_action.setChecked(False)
        self.rectangle_action.setChecked(False)
        self.circle_action.setChecked(False)
        self.note_action.setChecked(False)
        
        # تفعيل الأداة المحددة
        tool_actions = {
            "hand": self.hand_action,
            "select": self.select_action,
            "highlight": self.highlight_action,
            "underline": self.underline_action,
            "strikeout": self.strike_action,
            "rectangle": self.rectangle_action,
            "circle": self.circle_action,
            "note": self.note_action
        }
        
        if tool_name in tool_actions:
            tool_actions[tool_name].setChecked(True)
    
    def enable_actions(self, enabled=True):
        """تفعيل/تعطيل الإجراءات"""
        actions = [
            self.save_action, self.print_action,
            self.first_action, self.prev_action, self.next_action, self.last_action,
            self.zoom_out_action, self.zoom_in_action,
            self.rotate_left_action, self.rotate_right_action,
            self.search_action, self.find_next_action, self.find_prev_action,
            self.hand_action, self.select_action, self.highlight_action,
            self.underline_action, self.strike_action,
            self.rectangle_action, self.circle_action, self.note_action
        ]
        
        for action in actions:
            action.setEnabled(enabled)
        
        self.page_spin.setEnabled(enabled)
        self.zoom_combo.setEnabled(enabled)
        self.view_combo.setEnabled(enabled)
