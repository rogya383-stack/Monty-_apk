#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Themes Module - إدارة سمات التطبيق
Handles application themes and styling
"""

import json
import os
from PyQt5.QtGui import QColor, QPalette, QFont
from PyQt5.QtCore import QSettings, QFile, QTextStream, QDir

class ThemeManager:
    """مدير السمات - يدير أنماط وتنسيقات التطبيق"""
    
    def __init__(self, app_name="ProfessionalPDFReader"):
        """
        تهيئة مدير السمات
        
        Args:
            app_name (str): اسم التطبيق لحفظ الإعدادات
        """
        self.app_name = app_name
        self.settings = QSettings("PDFReader", app_name)
        self.current_theme = "light"
        self.custom_colors = {}
        self.font_settings = {}
        
        # تعريف السمات المتاحة
        self.themes = {
            "light": self._get_light_theme(),
            "dark": self._get_dark_theme(),
            "blue": self._get_blue_theme(),
            "green": self._get_green_theme(),
            "purple": self._get_purple_theme(),
            "high_contrast": self._get_high_contrast_theme()
        }
        
        # تحميل الإعدادات المحفوظة
        self.load_settings()
    
    def _get_light_theme(self):
        """السمة الفاتحة (الافتراضية)"""
        return {
            "name": "فاتح",
            "type": "light",
            "colors": {
                "primary": "#0078d7",
                "primary_dark": "#005a9e",
                "primary_light": "#50b0ff",
                "secondary": "#6c757d",
                "success": "#28a745",
                "danger": "#dc3545",
                "warning": "#ffc107",
                "info": "#17a2b8",
                
                "background": "#f8f9fa",
                "background_secondary": "#e9ecef",
                "background_tertiary": "#ffffff",
                
                "text_primary": "#212529",
                "text_secondary": "#6c757d",
                "text_disabled": "#adb5bd",
                
                "border": "#dee2e6",
                "border_hover": "#ced4da",
                
                "toolbar": "#ffffff",
                "sidebar": "#f8f9fa",
                "statusbar": "#e9ecef",
                
                "scrollbar": "#c1c1c1",
                "scrollbar_hover": "#a8a8a8",
                
                "selection": "#0078d7",
                "selection_text": "#ffffff",
                
                "link": "#0078d7",
                "link_hover": "#005a9e",
                
                "shadow": "rgba(0, 0, 0, 0.1)",
                "overlay": "rgba(0, 0, 0, 0.5)",
                
                "canvas_bg": "#ffffff",
                "page_shadow": "rgba(0, 0, 0, 0.1)",
                "grid_color": "rgba(0, 0, 0, 0.05)"
            },
            "fonts": {
                "family": "'Segoe UI', 'Arial', 'Tahoma', sans-serif",
                "arabic_family": "'Arial', 'Segoe UI', sans-serif",
                "size": "9pt",
                "title_size": "11pt",
                "heading_size": "10pt",
                "small_size": "8pt"
            },
            "borders": {
                "radius": "4px",
                "width": "1px",
                "focus_width": "2px"
            },
            "spacing": {
                "small": "2px",
                "medium": "5px",
                "large": "10px",
                "xlarge": "15px"
            },
            "transitions": {
                "fast": "0.15s",
                "medium": "0.3s",
                "slow": "0.5s"
            }
        }
    
    def _get_dark_theme(self):
        """السمة الداكنة"""
        return {
            "name": "داكن",
            "type": "dark",
            "colors": {
                "primary": "#0d6efd",
                "primary_dark": "#0a58ca",
                "primary_light": "#3d8bfd",
                "secondary": "#6c757d",
                "success": "#198754",
                "danger": "#dc3545",
                "warning": "#ffc107",
                "info": "#0dcaf0",
                
                "background": "#121212",
                "background_secondary": "#1e1e1e",
                "background_tertiary": "#2d2d2d",
                
                "text_primary": "#e9ecef",
                "text_secondary": "#adb5bd",
                "text_disabled": "#6c757d",
                
                "border": "#495057",
                "border_hover": "#6c757d",
                
                "toolbar": "#1e1e1e",
                "sidebar": "#121212",
                "statusbar": "#0d0d0d",
                
                "scrollbar": "#555555",
                "scrollbar_hover": "#777777",
                
                "selection": "#0d6efd",
                "selection_text": "#ffffff",
                
                "link": "#0d6efd",
                "link_hover": "#3d8bfd",
                
                "shadow": "rgba(255, 255, 255, 0.1)",
                "overlay": "rgba(0, 0, 0, 0.7)",
                
                "canvas_bg": "#1a1a1a",
                "page_shadow": "rgba(255, 255, 255, 0.1)",
                "grid_color": "rgba(255, 255, 255, 0.05)"
            },
            "fonts": {
                "family": "'Segoe UI', 'Arial', 'Tahoma', sans-serif",
                "arabic_family": "'Arial', 'Segoe UI', sans-serif",
                "size": "9pt",
                "title_size": "11pt",
                "heading_size": "10pt",
                "small_size": "8pt"
            },
            "borders": {
                "radius": "4px",
                "width": "1px",
                "focus_width": "2px"
            },
            "spacing": {
                "small": "2px",
                "medium": "5px",
                "large": "10px",
                "xlarge": "15px"
            },
            "transitions": {
                "fast": "0.15s",
                "medium": "0.3s",
                "slow": "0.5s"
            }
        }
    
    def _get_blue_theme(self):
        """السمة الزرقاء"""
        return {
            "name": "أزرق",
            "type": "blue",
            "colors": {
                "primary": "#0078d7",
                "primary_dark": "#005a9e",
                "primary_light": "#50b0ff",
                "secondary": "#17a2b8",
                "success": "#28a745",
                "danger": "#dc3545",
                "warning": "#ffc107",
                "info": "#17a2b8",
                
                "background": "#e3f2fd",
                "background_secondary": "#bbdefb",
                "background_tertiary": "#ffffff",
                
                "text_primary": "#0d47a1",
                "text_secondary": "#1976d2",
                "text_disabled": "#64b5f6",
                
                "border": "#90caf9",
                "border_hover": "#42a5f5",
                
                "toolbar": "#bbdefb",
                "sidebar": "#e3f2fd",
                "statusbar": "#90caf9",
                
                "scrollbar": "#64b5f6",
                "scrollbar_hover": "#42a5f5",
                
                "selection": "#0078d7",
                "selection_text": "#ffffff",
                
                "link": "#0078d7",
                "link_hover": "#005a9e",
                
                "shadow": "rgba(33, 150, 243, 0.3)",
                "overlay": "rgba(13, 71, 161, 0.5)",
                
                "canvas_bg": "#ffffff",
                "page_shadow": "rgba(33, 150, 243, 0.2)",
                "grid_color": "rgba(33, 150, 243, 0.1)"
            },
            "fonts": {
                "family": "'Segoe UI', 'Arial', 'Tahoma', sans-serif",
                "arabic_family": "'Arial', 'Segoe UI', sans-serif",
                "size": "9pt",
                "title_size": "11pt",
                "heading_size": "10pt",
                "small_size": "8pt"
            },
            "borders": {
                "radius": "4px",
                "width": "1px",
                "focus_width": "2px"
            },
            "spacing": {
                "small": "2px",
                "medium": "5px",
                "large": "10px",
                "xlarge": "15px"
            },
            "transitions": {
                "fast": "0.15s",
                "medium": "0.3s",
                "slow": "0.5s"
            }
        }
    
    def _get_green_theme(self):
        """السمة الخضراء"""
        return {
            "name": "أخضر",
            "type": "green",
            "colors": {
                "primary": "#28a745",
                "primary_dark": "#1e7e34",
                "primary_light": "#4caf50",
                "secondary": "#6c757d",
                "success": "#28a745",
                "danger": "#dc3545",
                "warning": "#ffc107",
                "info": "#17a2b8",
                
                "background": "#e8f5e9",
                "background_secondary": "#c8e6c9",
                "background_tertiary": "#ffffff",
                
                "text_primary": "#1b5e20",
                "text_secondary": "#2e7d32",
                "text_disabled": "#81c784",
                
                "border": "#a5d6a7",
                "border_hover": "#66bb6a",
                
                "toolbar": "#c8e6c9",
                "sidebar": "#e8f5e9",
                "statusbar": "#a5d6a7",
                
                "scrollbar": "#81c784",
                "scrollbar_hover": "#66bb6a",
                
                "selection": "#28a745",
                "selection_text": "#ffffff",
                
                "link": "#28a745",
                "link_hover": "#1e7e34",
                
                "shadow": "rgba(76, 175, 80, 0.3)",
                "overlay": "rgba(27, 94, 32, 0.5)",
                
                "canvas_bg": "#ffffff",
                "page_shadow": "rgba(76, 175, 80, 0.2)",
                "grid_color": "rgba(76, 175, 80, 0.1)"
            },
            "fonts": {
                "family": "'Segoe UI', 'Arial', 'Tahoma', sans-serif",
                "arabic_family": "'Arial', 'Segoe UI', sans-serif",
                "size": "9pt",
                "title_size": "11pt",
                "heading_size": "10pt",
                "small_size": "8pt"
            },
            "borders": {
                "radius": "4px",
                "width": "1px",
                "focus_width": "2px"
            },
            "spacing": {
                "small": "2px",
                "medium": "5px",
                "large": "10px",
                "xlarge": "15px"
            },
            "transitions": {
                "fast": "0.15s",
                "medium": "0.3s",
                "slow": "0.5s"
            }
        }
    
    def _get_purple_theme(self):
        """السمة الأرجوانية"""
        return {
            "name": "أرجواني",
            "type": "purple",
            "colors": {
                "primary": "#6f42c1",
                "primary_dark": "#563d7c",
                "primary_light": "#9c89ff",
                "secondary": "#6c757d",
                "success": "#28a745",
                "danger": "#dc3545",
                "warning": "#ffc107",
                "info": "#17a2b8",
                
                "background": "#f3e5f5",
                "background_secondary": "#e1bee7",
                "background_tertiary": "#ffffff",
                
                "text_primary": "#4a148c",
                "text_secondary": "#6a1b9a",
                "text_disabled": "#ba68c8",
                
                "border": "#ce93d8",
                "border_hover": "#ab47bc",
                
                "toolbar": "#e1bee7",
                "sidebar": "#f3e5f5",
                "statusbar": "#ce93d8",
                
                "scrollbar": "#ba68c8",
                "scrollbar_hover": "#ab47bc",
                
                "selection": "#6f42c1",
                "selection_text": "#ffffff",
                
                "link": "#6f42c1",
                "link_hover": "#563d7c",
                
                "shadow": "rgba(156, 39, 176, 0.3)",
                "overlay": "rgba(74, 20, 140, 0.5)",
                
                "canvas_bg": "#ffffff",
                "page_shadow": "rgba(156, 39, 176, 0.2)",
                "grid_color": "rgba(156, 39, 176, 0.1)"
            },
            "fonts": {
                "family": "'Segoe UI', 'Arial', 'Tahoma', sans-serif",
                "arabic_family": "'Arial', 'Segoe UI', sans-serif",
                "size": "9pt",
                "title_size": "11pt",
                "heading_size": "10pt",
                "small_size": "8pt"
            },
            "borders": {
                "radius": "4px",
                "width": "1px",
                "focus_width": "2px"
            },
            "spacing": {
                "small": "2px",
                "medium": "5px",
                "large": "10px",
                "xlarge": "15px"
            },
            "transitions": {
                "fast": "0.15s",
                "medium": "0.3s",
                "slow": "0.5s"
            }
        }
    
    def _get_high_contrast_theme(self):
        """سمة التباين العالي"""
        return {
            "name": "تباين عالي",
            "type": "high_contrast",
            "colors": {
                "primary": "#000000",
                "primary_dark": "#000000",
                "primary_light": "#000000",
                "secondary": "#000000",
                "success": "#000000",
                "danger": "#000000",
                "warning": "#000000",
                "info": "#000000",
                
                "background": "#ffffff",
                "background_secondary": "#ffffff",
                "background_tertiary": "#ffffff",
                
                "text_primary": "#000000",
                "text_secondary": "#000000",
                "text_disabled": "#666666",
                
                "border": "#000000",
                "border_hover": "#000000",
                
                "toolbar": "#ffffff",
                "sidebar": "#ffffff",
                "statusbar": "#ffffff",
                
                "scrollbar": "#000000",
                "scrollbar_hover": "#000000",
                
                "selection": "#000000",
                "selection_text": "#ffffff",
                
                "link": "#000000",
                "link_hover": "#000000",
                
                "shadow": "rgba(0, 0, 0, 0.5)",
                "overlay": "rgba(255, 255, 255, 0.9)",
                
                "canvas_bg": "#ffffff",
                "page_shadow": "#000000",
                "grid_color": "#000000"
            },
            "fonts": {
                "family": "'Arial Black', 'Arial', sans-serif",
                "arabic_family": "'Arial Black', 'Arial', sans-serif",
                "size": "10pt",
                "title_size": "12pt",
                "heading_size": "11pt",
                "small_size": "9pt"
            },
            "borders": {
                "radius": "0px",
                "width": "2px",
                "focus_width": "3px"
            },
            "spacing": {
                "small": "3px",
                "medium": "6px",
                "large": "12px",
                "xlarge": "18px"
            },
            "transitions": {
                "fast": "0s",
                "medium": "0s",
                "slow": "0s"
            }
        }
    
    def get_stylesheet(self, theme_name=None):
        """
        الحصول على تنسيق السمة
        
        Args:
            theme_name (str, optional): اسم السمة، إذا كان None يستخدم السمة الحالية
            
        Returns:
            str: تنسيق CSS للسمة
        """
        if theme_name is None:
            theme_name = self.current_theme
        
        if theme_name not in self.themes:
            theme_name = "light"
        
        theme = self.themes[theme_name]
        colors = theme["colors"]
        fonts = theme["fonts"]
        borders = theme["borders"]
        spacing = theme["spacing"]
        transitions = theme["transitions"]
        
        # بناء تنسيق CSS
        stylesheet = f"""
        /* ===== السمة: {theme['name']} ===== */
        
        /* العناصر الرئيسية */
        QMainWindow {{
            background-color: {colors['background']};
            color: {colors['text_primary']};
            font-family: {fonts['family']};
            font-size: {fonts['size']};
        }}
        
        QWidget {{
            background-color: transparent;
            color: {colors['text_primary']};
            font-family: {fonts['family']};
            font-size: {fonts['size']};
            selection-background-color: {colors['selection']};
            selection-color: {colors['selection_text']};
        }}
        
        /* النصوص */
        QLabel {{
            color: {colors['text_primary']};
            font-family: {fonts['arabic_family']};
        }}
        
        QLabel[cssClass="title"] {{
            font-size: {fonts['title_size']};
            font-weight: bold;
        }}
        
        QLabel[cssClass="heading"] {{
            font-size: {fonts['heading_size']};
            font-weight: bold;
        }}
        
        QLabel[cssClass="small"] {{
            font-size: {fonts['small_size']};
        }}
        
        /* الأزرار */
        QPushButton {{
            background-color: {colors['background_tertiary']};
            color: {colors['text_primary']};
            border: {borders['width']} solid {colors['border']};
            border-radius: {borders['radius']};
            padding: {spacing['small']} {spacing['medium']};
            font-weight: normal;
            transition: background-color {transitions['fast']} ease;
        }}
        
        QPushButton:hover {{
            background-color: {colors['background_secondary']};
            border-color: {colors['border_hover']};
        }}
        
        QPushButton:pressed {{
            background-color: {colors['primary']};
            color: {colors['selection_text']};
        }}
        
        QPushButton:checked {{
            background-color: {colors['primary']};
            color: {colors['selection_text']};
            border-color: {colors['primary_dark']};
        }}
        
        QPushButton:disabled {{
            background-color: {colors['background_secondary']};
            color: {colors['text_disabled']};
            border-color: {colors['border']};
        }}
        
        /* أزرار خاصة */
        QPushButton[cssClass="primary"] {{
            background-color: {colors['primary']};
            color: {colors['selection_text']};
            border-color: {colors['primary_dark']};
            font-weight: bold;
        }}
        
        QPushButton[cssClass="primary"]:hover {{
            background-color: {colors['primary_dark']};
        }}
        
        QPushButton[cssClass="danger"] {{
            background-color: {colors['danger']};
            color: white;
            border-color: #c82333;
        }}
        
        QPushButton[cssClass="danger"]:hover {{
            background-color: #c82333;
        }}
        
        QPushButton[cssClass="success"] {{
            background-color: {colors['success']};
            color: white;
            border-color: #1e7e34;
        }}
        
        QPushButton[cssClass="success"]:hover {{
            background-color: #1e7e34;
        }}
        
        /* أشرطة الأدوات */
        QToolBar {{
            background-color: {colors['toolbar']};
            border: none;
            border-bottom: {borders['width']} solid {colors['border']};
            spacing: {spacing['small']};
            padding: {spacing['small']};
        }}
        
        QToolBar::separator {{
            background-color: {colors['border']};
            width: 1px;
            margin: {spacing['small']} {spacing['medium']};
        }}
        
        /* أشرطة الحالة */
        QStatusBar {{
            background-color: {colors['statusbar']};
            color: {colors['text_secondary']};
            border-top: {borders['width']} solid {colors['border']};
            padding: {spacing['small']};
        }}
        
        /* الأشرطة الجانبية */
        QDockWidget {{
            background-color: {colors['sidebar']};
            border: {borders['width']} solid {colors['border']};
            titlebar-close-icon: url(:/icons/close.svg);
            titlebar-normal-icon: url(:/icons/float.svg);
        }}
        
        QDockWidget::title {{
            background-color: {colors['background_secondary']};
            padding: {spacing['small']} {spacing['medium']};
            border-bottom: {borders['width']} solid {colors['border']};
            text-align: left;
        }}
        
        /* القوائم */
        QMenuBar {{
            background-color: {colors['toolbar']};
            color: {colors['text_primary']};
            border-bottom: {borders['width']} solid {colors['border']};
        }}
        
        QMenuBar::item {{
            background-color: transparent;
            padding: {spacing['small']} {spacing['medium']};
        }}
        
        QMenuBar::item:selected {{
            background-color: {colors['selection']};
            color: {colors['selection_text']};
        }}
        
        QMenu {{
            background-color: {colors['background_tertiary']};
            color: {colors['text_primary']};
            border: {borders['width']} solid {colors['border']};
        }}
        
        QMenu::item {{
            padding: {spacing['small']} {spacing['medium']};
        }}
        
        QMenu::item:selected {{
            background-color: {colors['selection']};
            color: {colors['selection_text']};
        }}
        
        QMenu::separator {{
            background-color: {colors['border']};
            height: 1px;
            margin: {spacing['small']} 0;
        }}
        
        /* مربعات النصوص */
        QLineEdit, QTextEdit, QPlainTextEdit {{
            background-color: {colors['background_tertiary']};
            color: {colors['text_primary']};
            border: {borders['width']} solid {colors['border']};
            border-radius: {borders['radius']};
            padding: {spacing['small']} {spacing['medium']};
            selection-background-color: {colors['selection']};
            selection-color: {colors['selection_text']};
        }}
        
        QLineEdit:focus, QTextEdit:focus, QPlainTextEdit:focus {{
            border: {borders['focus_width']} solid {colors['primary']};
        }}
        
        QLineEdit:disabled, QTextEdit:disabled, QPlainTextEdit:disabled {{
            background-color: {colors['background_secondary']};
            color: {colors['text_disabled']};
        }}
        
        /* القوائم المنسدلة */
        QComboBox {{
            background-color: {colors['background_tertiary']};
            color: {colors['text_primary']};
            border: {borders['width']} solid {colors['border']};
            border-radius: {borders['radius']};
            padding: {spacing['small']} {spacing['medium']};
            min-height: 1.5em;
        }}
        
        QComboBox:hover {{
            border-color: {colors['border_hover']};
        }}
        
        QComboBox::drop-down {{
            subcontrol-origin: padding;
            subcontrol-position: top right;
            width: 20px;
            border-left: {borders['width']} solid {colors['border']};
            border-top-right-radius: {borders['radius']};
            border-bottom-right-radius: {borders['radius']};
        }}
        
        QComboBox::down-arrow {{
            image: url(:/icons/down_arrow.svg);
            width: 12px;
            height: 12px;
        }}
        
        QComboBox QAbstractItemView {{
            background-color: {colors['background_tertiary']};
            color: {colors['text_primary']};
            border: {borders['width']} solid {colors['border']};
            selection-background-color: {colors['selection']};
            selection-color: {colors['selection_text']};
        }}
        
        /* المربعات الاختيارية */
        QCheckBox, QRadioButton {{
            color: {colors['text_primary']};
            spacing: {spacing['small']};
        }}
        
        QCheckBox::indicator, QRadioButton::indicator {{
            width: 16px;
            height: 16px;
        }}
        
        QCheckBox::indicator:unchecked {{
            border: {borders['width']} solid {colors['border']};
            background-color: {colors['background_tertiary']};
        }}
        
        QCheckBox::indicator:checked {{
            border: {borders['width']} solid {colors['primary']};
            background-color: {colors['primary']};
            image: url(:/icons/check.svg);
        }}
        
        QCheckBox::indicator:disabled {{
            border: {borders['width']} solid {colors['border']};
            background-color: {colors['background_secondary']};
        }}
        
        QRadioButton::indicator:unchecked {{
            border: {borders['width']} solid {colors['border']};
            background-color: {colors['background_tertiary']};
            border-radius: 8px;
        }}
        
        QRadioButton::indicator:checked {{
            border: {borders['width']} solid {colors['primary']};
            background-color: {colors['primary']};
            border-radius: 8px;
        }}
        
        /* أشرطة التمرير */
        QScrollBar:vertical {{
            background-color: {colors['background_secondary']};
            width: 12px;
            border: none;
        }}
        
        QScrollBar::handle:vertical {{
            background-color: {colors['scrollbar']};
            border-radius: 6px;
            min-height: 20px;
        }}
        
        QScrollBar::handle:vertical:hover {{
            background-color: {colors['scrollbar_hover']};
        }}
        
        QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {{
            background: none;
            height: 0px;
        }}
        
        QScrollBar:horizontal {{
            background-color: {colors['background_secondary']};
            height: 12px;
            border: none;
        }}
        
        QScrollBar::handle:horizontal {{
            background-color: {colors['scrollbar']};
            border-radius: 6px;
            min-width: 20px;
        }}
        
        QScrollBar::handle:horizontal:hover {{
            background-color: {colors['scrollbar_hover']};
        }}
        
        /* علامات التبويب */
        QTabWidget::pane {{
            background-color: {colors['background_tertiary']};
            border: {borders['width']} solid {colors['border']};
            border-top: none;
        }}
        
        QTabBar::tab {{
            background-color: {colors['background_secondary']};
            color: {colors['text_secondary']};
            padding: {spacing['small']} {spacing['medium']};
            margin-right: {spacing['small']};
            border: {borders['width']} solid {colors['border']};
            border-bottom: none;
            border-top-left-radius: {borders['radius']};
            border-top-right-radius: {borders['radius']};
        }}
        
        QTabBar::tab:selected {{
            background-color: {colors['background_tertiary']};
            color: {colors['text_primary']};
            border-bottom: 2px solid {colors['primary']};
        }}
        
        QTabBar::tab:hover {{
            background-color: {colors['background']};
            color: {colors['text_primary']};
        }}
        
        /* المجموعات */
        QGroupBox {{
            background-color: {colors['background_secondary']};
            color: {colors['text_primary']};
            border: {borders['width']} solid {colors['border']};
            border-radius: {borders['radius']};
            margin-top: {spacing['large']};
            padding-top: {spacing['medium']};
            font-weight: bold;
        }}
        
        QGroupBox::title {{
            subcontrol-origin: margin;
            subcontrol-position: top left;
            padding: 0 {spacing['small']};
            background-color: {colors['background_secondary']};
        }}
        
        /* الجداول */
        QTableWidget {{
            background-color: {colors['background_tertiary']};
            color: {colors['text_primary']};
            gridline-color: {colors['border']};
            border: {borders['width']} solid {colors['border']};
            selection-background-color: {colors['selection']};
            selection-color: {colors['selection_text']};
        }}
        
        QTableWidget::item {{
            padding: {spacing['small']};
        }}
        
        QTableWidget::item:selected {{
            background-color: {colors['selection']};
            color: {colors['selection_text']};
        }}
        
        QHeaderView::section {{
            background-color: {colors['background_secondary']};
            color: {colors['text_primary']};
            padding: {spacing['small']} {spacing['medium']};
            border: {borders['width']} solid {colors['border']};
        }}
        
        /* الرسائل والتقدم */
        QProgressBar {{
            background-color: {colors['background_secondary']};
            color: {colors['text_primary']};
            border: {borders['width']} solid {colors['border']};
            border-radius: {borders['radius']};
            text-align: center;
        }}
        
        QProgressBar::chunk {{
            background-color: {colors['primary']};
            border-radius: {borders['radius']};
        }}
        
        /* الروابط */
        QLabel[cssClass="link"] {{
            color: {colors['link']};
            text-decoration: underline;
        }}
        
        QLabel[cssClass="link"]:hover {{
            color: {colors['link_hover']};
            cursor: pointer;
        }}
        
        /* عناصر خاصة بتطبيق PDF */
        #pdf_canvas {{
            background-color: {colors['canvas_bg']};
        }}
        
        .page_shadow {{
            box-shadow: 0 2px 10px {colors['page_shadow']};
        }}
        
        .grid_lines {{
            background-image: linear-gradient({colors['grid_color']} 1px, transparent 1px),
                              linear-gradient(90deg, {colors['grid_color']} 1px, transparent 1px);
        }}
        
        /* الطبقات المساعدة */
        .border {{
            border: {borders['width']} solid {colors['border']};
        }}
        
        .border_top {{
            border-top: {borders['width']} solid {colors['border']};
        }}
        
        .border_bottom {{
            border-bottom: {borders['width']} solid {colors['border']};
        }}
        
        .border_left {{
            border-left: {borders['width']} solid {colors['border']};
        }}
        
        .border_right {{
            border-right: {borders['width']} solid {colors['border']};
        }}
        
        .rounded {{
            border-radius: {borders['radius']};
        }}
        
        .shadow {{
            box-shadow: 0 2px 5px {colors['shadow']};
        }}
        
        .bg_primary {{
            background-color: {colors['primary']};
            color: {colors['selection_text']};
        }}
        
        .bg_secondary {{
            background-color: {colors['secondary']};
            color: white;
        }}
        
        .bg_success {{
            background-color: {colors['success']};
            color: white;
        }}
        
        .bg_danger {{
            background-color: {colors['danger']};
            color: white;
        }}
        
        .bg_warning {{
            background-color: {colors['warning']};
            color: {colors['text_primary']};
        }}
        
        .bg_info {{
            background-color: {colors['info']};
            color: white;
        }}
        
        .text_primary {{
            color: {colors['text_primary']};
        }}
        
        .text_secondary {{
            color: {colors['text_secondary']};
        }}
        
        .text_disabled {{
            color: {colors['text_disabled']};
        }}
        
        .text_success {{
            color: {colors['success']};
        }}
        
        .text_danger {{
            color: {colors['danger']};
        }}
        
        .text_warning {{
            color: {colors['warning']};
        }}
        
        .text_info {{
            color: {colors['info']};
        }}
        
        .p_small {{
            padding: {spacing['small']};
        }}
        
        .p_medium {{
            padding: {spacing['medium']};
        }}
        
        .p_large {{
            padding: {spacing['large']};
        }}
        
        .m_small {{
            margin: {spacing['small']};
        }}
        
        .m_medium {{
            margin: {spacing['medium']};
        }}
        
        .m_large {{
            margin: {spacing['large']};
        }}
        """
        
        return stylesheet
    
    def apply_theme(self, widget, theme_name=None):
        """
        تطبيق سمة على عنصر واجهة
        
        Args:
            widget: عنصر واجهة المستخدم
            theme_name (str, optional): اسم السمة
        """
        stylesheet = self.get_stylesheet(theme_name)
        widget.setStyleSheet(stylesheet)
        
        if theme_name:
            self.current_theme = theme_name
            self.save_settings()
    
    def get_theme_names(self):
        """
        الحصول على أسماء السمات المتاحة
        
        Returns:
            list: قائمة أسماء السمات
        """
        return list(self.themes.keys())
    
    def get_theme_display_names(self):
        """
        الحصول على أسماء عرض السمات
        
        Returns:
            dict: قاموس بأسماء العرض {id: display_name}
        """
        display_names = {}
        for theme_id, theme_data in self.themes.items():
            display_names[theme_id] = theme_data["name"]
        return display_names
    
    def get_theme_info(self, theme_name):
        """
        الحصول على معلومات سمة
        
        Args:
            theme_name (str): اسم السمة
            
        Returns:
            dict: معلومات السمة أو None إذا لم توجد
        """
        if theme_name in self.themes:
            return self.themes[theme_name].copy()
        return None
    
    def create_custom_theme(self, name, base_theme="light", custom_colors=None):
        """
        إنشاء سمة مخصصة
        
        Args:
            name (str): اسم السمة المخصصة
            base_theme (str): السمة الأساسية
            custom_colors (dict): الألوان المخصصة
            
        Returns:
            bool: True إذا نجح الإنشاء
        """
        if base_theme not in self.themes:
            return False
        
        # نسخ السمة الأساسية
        custom_theme = self.themes[base_theme].copy()
        custom_theme["name"] = name
        custom_theme["type"] = "custom"
        
        # تطبيق الألوان المخصصة
        if custom_colors:
            for key, value in custom_colors.items():
                if key in custom_theme["colors"]:
                    custom_theme["colors"][key] = value
        
        # حفظ السمة المخصصة
        theme_id = f"custom_{name.lower().replace(' ', '_')}"
        self.themes[theme_id] = custom_theme
        
        # حفظ في الإعدادات
        self.save_custom_theme(theme_id, custom_theme)
        
        return True
    
    def save_custom_theme(self, theme_id, theme_data):
        """حفظ سمة مخصصة في الإعدادات"""
        custom_themes = self.settings.value("custom_themes", {})
        custom_themes[theme_id] = theme_data
        self.settings.setValue("custom_themes", custom_themes)
        self.settings.sync()
    
    def load_custom_themes(self):
        """تحميل السمات المخصصة من الإعدادات"""
        custom_themes = self.settings.value("custom_themes", {})
        
        for theme_id, theme_data in custom_themes.items():
            if isinstance(theme_data, dict):
                self.themes[theme_id] = theme_data
    
    def delete_custom_theme(self, theme_id):
        """
        حذف سمة مخصصة
        
        Args:
            theme_id (str): معرف السمة المخصصة
            
        Returns:
            bool: True إذا نجح الحذف
        """
        if theme_id.startswith("custom_") and theme_id in self.themes:
            # حذف من القاموس
            del self.themes[theme_id]
            
            # حذف من الإعدادات
            custom_themes = self.settings.value("custom_themes", {})
            if theme_id in custom_themes:
                del custom_themes[theme_id]
                self.settings.setValue("custom_themes", custom_themes)
                self.settings.sync()
            
            return True
        
        return False
    
    def get_color(self, color_name, theme_name=None):
        """
        الحصول على لون من السمة
        
        Args:
            color_name (str): اسم اللون
            theme_name (str, optional): اسم السمة
            
        Returns:
            str: قيمة اللون أو None إذا لم يوجد
        """
        if theme_name is None:
            theme_name = self.current_theme
        
        if theme_name in self.themes and color_name in self.themes[theme_name]["colors"]:
            return self.themes[theme_name]["colors"][color_name]
        
        # البحث في جميع السمات
        for theme in self.themes.values():
            if color_name in theme["colors"]:
                return theme["colors"][color_name]
        
        return None
    
    def get_palette(self, theme_name=None):
        """
        الحصول على لوحة ألوان Qt
        
        Args:
            theme_name (str, optional): اسم السمة
            
        Returns:
            QPalette: لوحة الألوان
        """
        palette = QPalette()
        
        if theme_name is None:
            theme_name = self.current_theme
        
        if theme_name not in self.themes:
            return palette
        
        theme = self.themes[theme_name]
        colors = theme["colors"]
        
        # تحويل الألوان من HEX إلى QColor
        def hex_to_color(hex_color):
            hex_color = hex_color.lstrip('#')
            if len(hex_color) == 8:  # مع الشفافية
                r = int(hex_color[0:2], 16)
                g = int(hex_color[2:4], 16)
                b = int(hex_color[4:6], 16)
                a = int(hex_color[6:8], 16)
                return QColor(r, g, b, a)
            else:  # بدون شفافية
                r = int(hex_color[0:2], 16)
                g = int(hex_color[2:4], 16)
                b = int(hex_color[4:6], 16)
                return QColor(r, g, b)
        
        try:
            # تعيين ألوان اللوحة
            palette.setColor(QPalette.Window, hex_to_color(colors['background']))
            palette.setColor(QPalette.WindowText, hex_to_color(colors['text_primary']))
            palette.setColor(QPalette.Base, hex_to_color(colors['background_tertiary']))
            palette.setColor(QPalette.AlternateBase, hex_to_color(colors['background_secondary']))
            palette.setColor(QPalette.ToolTipBase, hex_to_color(colors['background_tertiary']))
            palette.setColor(QPalette.ToolTipText, hex_to_color(colors['text_primary']))
            palette.setColor(QPalette.Text, hex_to_color(colors['text_primary']))
            palette.setColor(QPalette.Button, hex_to_color(colors['background_tertiary']))
            palette.setColor(QPalette.ButtonText, hex_to_color(colors['text_primary']))
            palette.setColor(QPalette.BrightText, Qt.white)
            palette.setColor(QPalette.Link, hex_to_color(colors['link']))
            palette.setColor(QPalette.Highlight, hex_to_color(colors['selection']))
            palette.setColor(QPalette.HighlightedText, hex_to_color(colors['selection_text']))
            
            # ألوان الحالات
            palette.setColor(QPalette.Light, hex_to_color(colors['border_hover']))
            palette.setColor(QPalette.Midlight, hex_to_color(colors['border']))
            palette.setColor(QPalette.Dark, hex_to_color(colors['border']))
            palette.setColor(QPalette.Mid, hex_to_color(colors['border']))
            palette.setColor(QPalette.Shadow, hex_to_color(colors['shadow']))
            
        except Exception as e:
            print(f"خطأ في إنشاء لوحة الألوان: {e}")
        
        return palette
    
    def save_settings(self):
        """حفظ إعدادات السمات"""
        self.settings.setValue("current_theme", self.current_theme)
        self.settings.setValue("custom_colors", self.custom_colors)
        self.settings.setValue("font_settings", self.font_settings)
        self.settings.sync()
    
    def load_settings(self):
        """تحميل إعدادات السمات"""
        # تحميل السمة الحالية
        saved_theme = self.settings.value("current_theme")
        if saved_theme and saved_theme in self.themes:
            self.current_theme = saved_theme
        
        # تحميل الألوان المخصصة
        saved_colors = self.settings.value("custom_colors")
        if saved_colors and isinstance(saved_colors, dict):
            self.custom_colors = saved_colors
        
        # تحميل إعدادات الخطوط
        saved_fonts = self.settings.value("font_settings")
        if saved_fonts and isinstance(saved_fonts, dict):
            self.font_settings = saved_fonts
        
        # تحميل السمات المخصصة
        self.load_custom_themes()
    
    def export_theme(self, theme_name, file_path):
        """
        تصدير سمة إلى ملف
        
        Args:
            theme_name (str): اسم السمة
            file_path (str): مسار الملف
            
        Returns:
            bool: True إذا نجح التصدير
        """
        if theme_name not in self.themes:
            return False
        
        try:
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(self.themes[theme_name], f, ensure_ascii=False, indent=2)
            return True
        except Exception as e:
            print(f"خطأ في تصدير السمة: {e}")
            return False
    
    def import_theme(self, file_path):
        """
        استيراد سمة من ملف
        
        Args:
            file_path (str): مسار الملف
            
        Returns:
            str: معرف السمة المستوردة أو None إذا فشل
        """
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                theme_data = json.load(f)
            
            # التحقق من صحة بيانات السمة
            if not all(key in theme_data for key in ['name', 'type', 'colors', 'fonts']):
                return None
            
            # إنشاء معرف فريد للسمة
            theme_id = f"imported_{os.path.splitext(os.path.basename(file_path))[0]}"
            
            # إضافة السمة
            self.themes[theme_id] = theme_data
            
            # حفظ كسمة مخصصة
            self.save_custom_theme(theme_id, theme_data)
            
            return theme_id
            
        except Exception as e:
            print(f"خطأ في استيراد السمة: {e}")
            return None
    
    def reset_to_defaults(self):
        """إعادة تعيين جميع الإعدادات إلى الافتراضية"""
        # الحفاظ على السمات الأساسية فقط
        default_themes = {
            "light": self._get_light_theme(),
            "dark": self._get_dark_theme(),
            "blue": self._get_blue_theme(),
            "green": self._get_green_theme(),
            "purple": self._get_purple_theme(),
            "high_contrast": self._get_high_contrast_theme()
        }
        
        self.themes = default_themes
        self.current_theme = "light"
        self.custom_colors = {}
        self.font_settings = {}
        
        # حذف الإعدادات المحفوظة
        self.settings.remove("custom_themes")
        self.settings.remove("current_theme")
        self.settings.remove("custom_colors")
        self.settings.remove("font_settings")
        self.settings.sync()


# اختبار الوحدة
if __name__ == "__main__":
    from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QPushButton, QLabel
    import sys
    
    app = QApplication(sys.argv)
    
    # إنشاء نافذة اختبار
    window = QWidget()
    window.setWindowTitle("اختبار السمات")
    window.setGeometry(100, 100, 400, 300)
    
    layout = QVBoxLayout(window)
    
    # عناصر اختبار
    label = QLabel("اختبار تطبيق السمات")
    layout.addWidget(label)
    
    button1 = QPushButton("زر عادي")
    layout.addWidget(button1)
    
    button2 = QPushButton("زر أساسي")
    button2.setProperty("cssClass", "primary")
    layout.addWidget(button2)
    
    button3 = QPushButton("زر خطير")
    button3.setProperty("cssClass", "danger")
    layout.addWidget(button3)
    
    # اختبار مدير السمات
    theme_manager = ThemeManager()
    
    # تطبيق السمات المختلفة
    themes = ["light", "dark", "blue", "green", "purple"]
    current_index = 0
    
    def switch_theme():
        nonlocal current_index
        theme_name = themes[current_index]
        theme_manager.apply_theme(window, theme_name)
        label.setText(f"السمة الحالية: {theme_manager.themes[theme_name]['name']}")
        current_index = (current_index + 1) % len(themes)
    
    # زر تبديل السمات
    switch_btn = QPushButton("تبديل السمة")
    switch_btn.clicked.connect(switch_theme)
    layout.addWidget(switch_btn)
    
    # تطبيق السمة الافتراضية
    theme_manager.apply_theme(window)
    
    window.show()
    sys.exit(app.exec_())
