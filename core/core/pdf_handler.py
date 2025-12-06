#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
PDF Handler Module - معالج ملفات PDF
الوحدة الأساسية لقراءة ومعالجة ملفات PDF
"""

import fitz  # PyMuPDF
import pdfplumber
import os
import json
from PIL import Image
import numpy as np
from datetime import datetime
from typing import List, Dict, Optional, Tuple, Any

class PDFHandler:
    """فئة معالجة ملفات PDF الرئيسية"""
    
    def __init__(self):
        """تهيئة معالج PDF"""
        self.doc = None  # وثيقة PDF
        self.file_path = None  # مسار الملف
        self.total_pages = 0  # عدد الصفحات الكلي
        self.current_page = 0  # الصفحة الحالية
        self.annotations = {}  # التعليقات التوضيحية
        self.bookmarks = []  # العلامات المرجعية
        self.metadata = {}  # البيانات الوصفية
        self.search_results = []  # نتائج البحث
        self.current_search_index = -1  # فهرس البحث الحالي
        
    # ============================================================================
    # العمليات الأساسية
    # ============================================================================
    
    def open_pdf(self, file_path: str) -> Tuple[bool, str]:
        """
        فتح ملف PDF
        
        Args:
            file_path (str): مسار ملف PDF
            
        Returns:
            Tuple[bool, str]: (النجاح, الرسالة)
        """
        try:
            # إغلاق الملف الحالي إذا كان مفتوحاً
            if self.doc:
                self.close_pdf()
            
            # التحقق من وجود الملف
            if not os.path.exists(file_path):
                return False, "❌ الملف غير موجود"
            
            # التحقق من امتداد الملف
            if not file_path.lower().endswith('.pdf'):
                return False, "❌ الملف ليس بصيغة PDF"
            
            # فتح ملف PDF
            self.doc = fitz.open(file_path)
            self.file_path = file_path
            self.total_pages = len(self.doc)
            self.current_page = 0
            
            # تهيئة التعليقات التوضيحية
            self.annotations = {i: [] for i in range(self.total_pages)}
            
            # تحميل البيانات الوصفية
            self.metadata = self.get_metadata()
            
            # تحميل العلامات المرجعية
            self.bookmarks = self.get_bookmarks()
            
            # تحميل التعليقات المحفوظة مسبقاً
            self.load_saved_annotations()
            
            return True, f"✅ تم فتح الملف: {os.path.basename(file_path)}"
            
        except Exception as e:
            error_msg = f"❌ خطأ في فتح الملف: {str(e)}"
            print(error_msg)
            return False, error_msg
    
    def close_pdf(self) -> None:
        """إغلاق ملف PDF الحالي"""
        if self.doc:
            # حفظ التعليقات التوضيحية قبل الإغلاق
            self.save_annotations()
            
            self.doc.close()
            self.doc = None
            self.file_path = None
            self.total_pages = 0
            self.current_page = 0
            self.annotations = {}
            self.bookmarks = []
            self.metadata = {}
            self.search_results = []
            self.current_search_index = -1
    
    def save_pdf(self, file_path: str = None) -> Tuple[bool, str]:
        """
        حفظ ملف PDF
        
        Args:
            file_path (str, optional): مسار الحفظ الجديد
            
        Returns:
            Tuple[bool, str]: (النجاح, الرسالة)
        """
        if not self.doc:
            return False, "❌ لا يوجد ملف مفتوح"
        
        try:
            save_path = file_path or self.file_path
            
            if not save_path:
                return False, "❌ لم يتم تحديد مسار الحفظ"
            
            # حفظ الوثيقة
            self.doc.save(save_path)
            
            # تحديث مسار الملف إذا كان جديداً
            if file_path:
                self.file_path = file_path
            
            # حفظ التعليقات التوضيحية
            self.save_annotations()
            
            return True, f"✅ تم حفظ الملف: {os.path.basename(save_path)}"
            
        except Exception as e:
            return False, f"❌ خطأ في حفظ الملف: {str(e)}"
    
    # ============================================================================
    # عرض الصفحات
    # ============================================================================
    
    def get_page_image(self, page_num: int, zoom: float = 1.5, 
                       rotation: int = 0) -> Optional[Image.Image]:
        """
        الحصول على صورة الصفحة للعرض
        
        Args:
            page_num (int): رقم الصفحة (يبدأ من 0)
            zoom (float): عامل التكبير
            rotation (int): زاوية التدوير (0, 90, 180, 270)
            
        Returns:
            Optional[Image.Image]: صورة الصفحة أو None
        """
        if not self.doc or page_num < 0 or page_num >= self.total_pages:
            return None
        
        try:
            page = self.doc.load_page(page_num)
            
            # تطبيق التدوير
            if rotation in [90, 180, 270]:
                page.set_rotation(rotation)
            
            # إنشاء مصفوفة التحويل
            mat = fitz.Matrix(zoom, zoom)
            
            # الحصول على الصورة النقطية
            pix = page.get_pixmap(matrix=mat, alpha=False)
            
            # تحويل إلى صيغة PIL Image
            img = Image.frombytes("RGB", [pix.width, pix.height], pix.samples)
            
            return img
            
        except Exception as e:
            print(f"❌ خطأ في تحويل الصفحة {page_num + 1} إلى صورة: {e}")
            return None
    
    def get_page_thumbnail(self, page_num: int, size: Tuple[int, int] = (100, 150)) -> Optional[Image.Image]:
        """
        الحصول على صورة مصغرة للصفحة
        
        Args:
            page_num (int): رقم الصفحة
            size (Tuple[int, int]): الحجم المطلوب (عرض، ارتفاع)
            
        Returns:
            Optional[Image.Image]: الصورة المصغرة
        """
        img = self.get_page_image(page_num, zoom=0.3)
        if img:
            return img.resize(size, Image.Resampling.LANCZOS)
        return None
    
    # ============================================================================
    # استخراج النصوص
    # ============================================================================
    
    def get_page_text(self, page_num: int) -> str:
        """
        استخراج النص من صفحة محددة
        
        Args:
            page_num (int): رقم الصفحة
            
        Returns:
            str: النص المستخرج
        """
        if not self.doc:
            return ""
        
        if page_num < 0 or page_num >= self.total_pages:
            return ""
        
        text = ""
        
        try:
            # المحاولة باستخدام pdfplumber (أكثر دقة)
            with pdfplumber.open(self.file_path) as pdf:
                if page_num < len(pdf.pages):
                    page = pdf.pages[page_num]
                    extracted_text = page.extract_text()
                    if extracted_text:
                        text = extracted_text
        except Exception as e:
            print(f"⚠️ خطأ في pdfplumber: {e}")
        
        # إذا لم يتم استخراج نص باستخدام pdfplumber، استخدام PyMuPDF
        if not text:
            try:
                page = self.doc.load_page(page_num)
                text = page.get_text()
            except Exception as e:
                print(f"⚠️ خطأ في PyMuPDF: {e}")
        
        return text
    
    def get_all_text(self) -> str:
        """الحصول على نص جميع الصفحات"""
        all_text = []
        for page_num in range(self.total_pages):
            page_text = self.get_page_text(page_num)
            if page_text:
                all_text.append(f"=== الصفحة {page_num + 1} ===\n{page_text}\n")
        
        return "\n".join(all_text)
    
    # ============================================================================
    # البحث
    # ============================================================================
    
    def search_in_pdf(self, search_text: str, case_sensitive: bool = False, 
                     whole_word: bool = False) -> List[Dict]:
        """
        البحث عن نص في جميع صفحات PDF
        
        Args:
            search_text (str): النص المطلوب البحث عنه
            case_sensitive (bool): مراعاة حالة الأحرف
            whole_word (bool): مطابقة الكلمة كاملة
            
        Returns:
            List[Dict]: قائمة نتائج البحث
        """
        self.search_results = []
        self.current_search_index = -1
        
        if not self.doc or not search_text.strip():
            return self.search_results
        
        try:
            for page_num in range(self.total_pages):
                page = self.doc.load_page(page_num)
                
                # البحث في النص
                text_instances = page.search_for(
                    search_text,
                    quads=True,  # الحصول على الإحداثيات الدقيقة
                    case_sensitive=case_sensitive
                )
                
                for i, rect in enumerate(text_instances):
                    # الحصول على النص المحيط
                    context_text = self.get_text_context(page_num, rect, chars=50)
                    
                    self.search_results.append({
                        'page': page_num,
                        'rect': rect,
                        'text': search_text,
                        'context': context_text,
                        'id': len(self.search_results),
                        'page_text': f"الصفحة {page_num + 1}",
                        'position': f"نتيجة {i + 1} في الصفحة {page_num + 1}"
                    })
            
            self.current_search_index = 0 if self.search_results else -1
            
        except Exception as e:
            print(f"❌ خطأ في البحث: {e}")
        
        return self.search_results
    
    def get_text_context(self, page_num: int, rect, chars: int = 50) -> str:
        """
        الحصول على النص المحيط بمنطقة محددة
        
        Args:
            page_num (int): رقم الصفحة
            rect: المنطقة المستطيلة
            chars (int): عدد الأحرف المطلوبة
            
        Returns:
            str: النص المحيط
        """
        try:
            page_text = self.get_page_text(page_num)
            if not page_text:
                return ""
            
            # هذا تبسيط - في التطبيق الحقيقي تحتاج لتحويل rect إلى موضع في النص
            return page_text[:chars] + "..."
        except:
            return ""
    
    def get_next_search_result(self) -> Optional[Dict]:
        """الحصول على نتيجة البحث التالية"""
        if not self.search_results:
            return None
        
        self.current_search_index = (self.current_search_index + 1) % len(self.search_results)
        return self.search_results[self.current_search_index]
    
    def get_prev_search_result(self) -> Optional[Dict]:
        """الحصول على نتيجة البحث السابقة"""
        if not self.search_results:
            return None
        
        self.current_search_index = (self.current_search_index - 1) % len(self.search_results)
        return self.search_results[self.current_search_index]
    
    # ============================================================================
    # البيانات الوصفية والمعلومات
    # ============================================================================
    
    def get_metadata(self) -> Dict[str, Any]:
        """
        الحصول على البيانات الوصفية لملف PDF
        
        Returns:
            Dict[str, Any]: البيانات الوصفية
        """
        if not self.doc:
            return {}
        
        meta = self.doc.metadata
        file_size = 0
        
        if self.file_path and os.path.exists(self.file_path):
            try:
                file_size = os.path.getsize(self.file_path)
            except:
                pass
        
        # تحويل التواريخ إلى تنسيق مقروء
        creation_date = meta.get('creationDate', '')
        mod_date = meta.get('modDate', '')
        
        if creation_date:
            creation_date = self._parse_pdf_date(creation_date)
        
        if mod_date:
            mod_date = self._parse_pdf_date(mod_date)
        
        return {
            'title': meta.get('title', 'بدون عنوان'),
            'author': meta.get('author', 'غير معروف'),
            'subject': meta.get('subject', 'بدون وصف'),
            'keywords': meta.get('keywords', 'لا يوجد'),
            'creator': meta.get('creator', 'غير معروف'),
            'producer': meta.get('producer', 'غير معروف'),
            'creation_date': creation_date,
            'modification_date': mod_date,
            'pages': self.total_pages,
            'file_size': file_size,
            'file_size_mb': f"{file_size / (1024*1024):.2f} MB" if file_size > 0 else "0 MB",
            'file_path': self.file_path,
            'file_name': os.path.basename(self.file_path) if self.file_path else '',
            'is_encrypted': self.doc.is_encrypted,
            'permissions': self.doc.permissions
        }
    
    def _parse_pdf_date(self, pdf_date: str) -> str:
        """تحويل تاريخ PDF إلى تنسيق مقروء"""
        try:
            # تنسيق PDF Date: D:YYYYMMDDHHmmSS
            if pdf_date.startswith('D:'):
                date_str = pdf_date[2:]
                year = date_str[:4]
                month = date_str[4:6] if len(date_str) >= 6 else '01'
                day = date_str[6:8] if len(date_str) >= 8 else '01'
                return f"{year}-{month}-{day}"
        except:
            pass
        return pdf_date
    
    def get_bookmarks(self) -> List[Dict]:
        """
        الحصول على العلامات المرجعية (جدول المحتويات)
        
        Returns:
            List[Dict]: قائمة العلامات المرجعية
        """
        if not self.doc:
            return []
        
        try:
            toc = self.doc.get_toc()
            formatted_toc = []
            
            for level, title, page_num in toc:
                formatted_toc.append({
                    'level': level,
                    'title': title,
                    'page': page_num - 1,  # تحويل إلى فهرس يبدأ من 0
                    'page_display': page_num  # للعرض للمستخدم
                })
            
            return formatted_toc
            
        except Exception as e:
            print(f"⚠️ خطأ في الحصول على العلامات المرجعية: {e}")
            return []
    
    def get_page_info(self, page_num: int) -> Dict[str, Any]:
        """
        الحصول على معلومات عن صفحة محددة
        
        Args:
            page_num (int): رقم الصفحة
            
        Returns:
            Dict[str, Any]: معلومات الصفحة
        """
        if not self.doc or page_num < 0 or page_num >= self.total_pages:
            return {}
        
        try:
            page = self.doc.load_page(page_num)
            rect = page.rect
            
            return {
                'number': page_num + 1,
                'width': rect.width,
                'height': rect.height,
                'rotation': page.rotation,
                'has_images': len(page.get_images()) > 0,
                'has_text': bool(page.get_text()),
                'annotations_count': len(self.annotations.get(page_num, []))
            }
        except:
            return {}
    
    # ============================================================================
    # التعليقات التوضيحية
    # ============================================================================
    
    def add_annotation(self, page_num: int, annotation_type: str, 
                      points: List, color: Tuple[float, float, float] = (1, 0, 0), 
                      text: str = "") -> int:
        """
        إضافة تعليق توضيحي جديد
        
        Args:
            page_num (int): رقم الصفحة
            annotation_type (str): نوع التعليق ('highlight', 'underline', 'strikeout', 'rectangle', 'circle', 'text')
            points (List): نقاط التعليق [x, y, width, height] أو قائمة نقاط للمضلعات
            color (Tuple[float, float, float]): اللون (RGB 0-1)
            text (str): نص التعليق (لتعليقات النص)
            
        Returns:
            int: معرف التعليق
        """
        if page_num not in self.annotations:
            self.annotations[page_num] = []
        
        annotation_id = len(self.annotations[page_num])
        
        annotation = {
            'id': annotation_id,
            'type': annotation_type,
            'points': points,
            'color': color,
            'text': text,
            'date': datetime.now().isoformat(),
            'page': page_num,
            'visible': True
        }
        
        self.annotations[page_num].append(annotation)
        
        # حفظ التعليقات تلقائياً
        self.save_annotations()
        
        return annotation_id
    
    def remove_annotation(self, page_num: int, annotation_id: int) -> bool:
        """
        حذف تعليق توضيحي
        
        Args:
            page_num (int): رقم الصفحة
            annotation_id (int): معرف التعليق
            
        Returns:
            bool: True إذا تم الحذف بنجاح
        """
        if page_num in self.annotations:
            initial_count = len(self.annotations[page_num])
            self.annotations[page_num] = [
                ann for ann in self.annotations[page_num] 
                if ann['id'] != annotation_id
            ]
            
            # إذا تغير العدد، حفظ التغييرات
            if len(self.annotations[page_num]) != initial_count:
                self.save_annotations()
                return True
        
        return False
    
    def get_page_annotations(self, page_num: int) -> List[Dict]:
        """
        الحصول على جميع التعليقات التوضيحية لصفحة محددة
        
        Args:
            page_num (int): رقم الصفحة
            
        Returns:
            List[Dict]: قائمة التعليقات
        """
        return self.annotations.get(page_num, [])
    
    def get_all_annotations(self) -> Dict[int, List[Dict]]:
        """الحصول على جميع التعليقات التوضيحية"""
        return self.annotations
    
    def save_annotations(self) -> bool:
        """حفظ التعليقات التوضيحية إلى ملف"""
        if not self.file_path:
            return False
        
        try:
            annotations_file = self.file_path + '.annotations.json'
            
            with open(annotations_file, 'w', encoding='utf-8') as f:
                json.dump(self.annotations, f, ensure_ascii=False, indent=2)
            
            return True
            
        except Exception as e:
            print(f"⚠️ خطأ في حفظ التعليقات: {e}")
            return False
    
    def load_saved_annotations(self) -> bool:
        """تحميل التعليقات التوضيحية المحفوظة مسبقاً"""
        if not self.file_path:
            return False
        
        try:
            annotations_file = self.file_path + '.annotations.json'
            
            if os.path.exists(annotations_file):
                with open(annotations_file, 'r', encoding='utf-8') as f:
                    loaded_annotations = json.load(f)
                
                # تحويل المفاتيح من نص إلى أعداد صحيحة
                self.annotations = {int(k): v for k, v in loaded_annotations.items()}
                
                # التأكد من أن التعليقات ضمن نطاق الصفحات الصحيح
                self.annotations = {k: v for k, v in self.annotations.items() 
                                  if 0 <= k < self.total_pages}
                
                return True
            
        except Exception as e:
            print(f"⚠️ خطأ في تحميل التعليقات: {e}")
        
        return False
    
    # ============================================================================
    # التصدير والتحويل
    # ============================================================================
    
    def export_to_text(self, output_path: str, start_page: int = 0, 
                      end_page: int = None, include_metadata: bool = True) -> bool:
        """
        تصدير PDF إلى ملف نصي
        
        Args:
            output_path (str): مسار ملف الإخراج
            start_page (int): صفحة البداية (يبدأ من 0)
            end_page (int): صفحة النهاية
            include_metadata (bool): تضمين البيانات الوصفية
            
        Returns:
            bool: True إذا نجح التصدير
        """
        if not self.doc:
            return False
        
        if end_page is None:
            end_page = self.total_pages - 1
        
        # التأكد من النطاق صحيح
        start_page = max(0, min(start_page, self.total_pages - 1))
        end_page = max(start_page, min(end_page, self.total_pages - 1))
        
        try:
            with open(output_path, 'w', encoding='utf-8') as f:
                # كتابة رأس الملف
                f.write("=" * 70 + "\n")
                f.write("تصدير من قارئ PDF احترافي\n")
                f.write("=" * 70 + "\n\n")
                
                # تضمين البيانات الوصفية إذا طلب
                if include_metadata:
                    f.write("معلومات الملف:\n")
                    f.write("-" * 40 + "\n")
                    f.write(f"العنوان: {self.metadata.get('title', 'غير معروف')}\n")
                    f.write(f"المؤلف: {self.metadata.get('author', 'غير معروف')}\n")
                    f.write(f"عدد الصفحات: {self.total_pages}\n")
                    f.write(f"تاريخ الإنشاء: {self.metadata.get('creation_date', 'غير معروف')}\n")
                    f.write("\n")
                
                # تصدير نص كل صفحة
                for page_num in range(start_page, end_page + 1):
                    text = self.get_page_text(page_num)
                    
                    if text.strip():
                        f.write(f"\n{'='*40}\n")
                        f.write(f"الصفحة {page_num + 1}\n")
                        f.write(f"{'='*40}\n\n")
                        f.write(text + "\n")
                    else:
                        f.write(f"\n[الصفحة {page_num + 1}: لا تحتوي على نص]\n")
                
                f.write("\n" + "=" * 70 + "\n")
                f.write("نهاية التصدير\n")
                f.write("=" * 70 + "\n")
            
            return True
            
        except Exception as e:
            print(f"❌ خطأ في تصدير النص: {e}")
            return False
    
    def extract_images(self, output_folder: str) -> List[Dict]:
        """
        استخراج الصور من PDF
        
        Args:
            output_folder (str): مجلد الإخراج
            
        Returns:
            List[Dict]: معلومات الصور المستخرجة
        """
        if not self.doc or not self.file_path:
            return []
        
        images = []
        
        try:
            # إنشاء مجلد الإخراج إذا لم يكن موجوداً
            if not os.path.exists(output_folder):
                os.makedirs(output_folder)
            
            for page_num in range(self.total_pages):
                page = self.doc.load_page(page_num)
                image_list = page.get_images(full=True)
                
                for img_index, img in enumerate(image_list):
                    xref = img[0]
                    base_image = self.doc.extract_image(xref)
                    image_bytes = base_image["image"]
                    image_ext = base_image["ext"]
                    
                    # إنشاء اسم ملف فريد
                    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                    image_name = f"page_{page_num+1}_img_{img_index+1}_{timestamp}.{image_ext}"
                    image_path = os.path.join(output_folder, image_name)
                    
                    # حفظ الصورة
                    with open(image_path, "wb") as f:
                        f.write(image_bytes)
                    
                    images.append({
                        'path': image_path,
                        'page': page_num + 1,
                        'index': img_index + 1,
                        'size': len(image_bytes),
                        'format': image_ext.upper(),
                        'name': image_name
                    })
            
            return images
            
        except Exception as e:
            print(f"❌ خطأ في استخراج الصور: {e}")
            return []
    
    # ============================================================================
    # العمليات المتقدمة
    # ============================================================================
    
    def rotate_page(self, page_num: int, rotation: int) -> bool:
        """
        تدوير صفحة محددة
        
        Args:
            page_num (int): رقم الصفحة
            rotation (int): زاوية التدوير (0, 90, 180, 270)
            
        Returns:
            bool: True إذا نجح التدوير
        """
        if not self.doc or page_num < 0 or page_num >= self.total_pages:
            return False
        
        try:
            page = self.doc.load_page(page_num)
            page.set_rotation(rotation)
            return True
            
        except Exception as e:
            print(f"❌ خطأ في تدوير الصفحة: {e}")
            return False
    
    def delete_page(self, page_num: int) -> bool:
        """
        حذف صفحة محددة
        
        Args:
            page_num (int): رقم الصفحة
            
        Returns:
            bool: True إذا نجح الحذف
        """
        if not self.doc or page_num < 0 or page_num >= self.total_pages:
            return False
        
        try:
            self.doc.delete_page(page_num)
            self.total_pages = len(self.doc)
            
            # تحديث التعليقات بعد الحذف
            self._update_annotations_after_deletion(page_num)
            
            return True
            
        except Exception as e:
            print(f"❌ خطأ في حذف الصفحة: {e}")
            return False
    
    def _update_annotations_after_deletion(self, deleted_page: int):
        """تحديث التعليقات بعد حذف صفحة"""
        new_annotations = {}
        
        for page_num, annotations in self.annotations.items():
            if page_num < deleted_page:
                # الصفحات قبل المحذوفة تبقى كما هي
                new_annotations[page_num] = annotations
            elif page_num > deleted_page:
                # الصفحات بعد المحذوفة تنقل إلى صفحة أقل بواحد
                new_annotations[page_num - 1] = annotations
        
        self.annotations = new_annotations
    
    def merge_pdfs(self, pdf_files: List[str], output_path: str) -> bool:
        """
        دمج عدة ملفات PDF في ملف واحد
        
        Args:
            pdf_files (List[str]): قائمة مسارات ملفات PDF
            output_path (str): مسار ملف الإخراج
            
        Returns:
            bool: True إذا نجح الدمج
        """
        try:
            merged_doc = fitz.open()
            
            # إضافة الملف الحالي إذا كان مفتوحاً
            if self.doc:
                merged_doc.insert_pdf(self.doc)
            
            # إضافة الملفات الأخرى
            for pdf_file in pdf_files:
                if os.path.exists(pdf_file):
                    doc_to_add = fitz.open(pdf_file)
                    merged_doc.insert_pdf(doc_to_add)
                    doc_to_add.close()
            
            # حفظ الملف المدمج
            merged_doc.save(output_path)
            merged_doc.close()
            
            return True
            
        except Exception as e:
            print(f"❌ خطأ في دمج ملفات PDF: {e}")
            return False
    
    # ============================================================================
    # أدوات مساعدة
    # ============================================================================
    
    def is_valid_pdf(self, file_path: str) -> bool:
        """
        التحقق من أن الملف هو PDF صالح
        
        Args:
            file_path (str): مسار الملف
            
        Returns:
            bool: True إذا كان PDF صالحاً
        """
        try:
            if not os.path.exists(file_path):
                return False
            
            # التحقق من امتداد الملف
            if not file_path.lower().endswith('.pdf'):
                return False
            
            # محاولة فتح الملف كـ PDF
            with fitz.open(file_path) as test_doc:
                if len(test_doc) > 0:
                    return True
            
            return False
            
        except:
            return False
    
    def get_file_size_mb(self) -> float:
        """الحصول على حجم الملف بالميجابايت"""
        if not self.file_path or not os.path.exists(self.file_path):
            return 0.0
        
        try:
            size_bytes = os.path.getsize(self.file_path)
            return size_bytes / (1024 * 1024)
        except:
            return 0.0
    
    def get_statistics(self) -> Dict[str, Any]:
        """الحصول على إحصاءات عن الملف"""
        stats = {
            'total_pages': self.total_pages,
            'file_size_mb': self.get_file_size_mb(),
            'has_bookmarks': len(self.bookmarks) > 0,
            'total_annotations': sum(len(anns) for anns in self.annotations.values()),
            'is_encrypted': self.doc.is_encrypted if self.doc else False,
            'metadata': self.metadata
        }
        
        # إحصاءات الصفحات
        page_stats = []
        for page_num in range(min(10, self.total_pages)):  # أول 10 صفحات فقط
            page_info = self.get_page_info(page_num)
            page_stats.append(page_info)
        
        stats['sample_pages'] = page_stats
        
        return stats
    
    def cleanup(self):
        """تنظيف الموارد"""
        self.close_pdf()


# ============================================================================
# دوال مساعدة
# ============================================================================

def validate_pdf_file(file_path: str) -> Tuple[bool, str]:
    """
    التحقق من صحة ملف PDF
    
    Args:
        file_path (str): مسار الملف
        
    Returns:
        Tuple[bool, str]: (صالح، رسالة)
    """
    if not os.path.exists(file_path):
        return False, "الملف غير موجود"
    
    if not file_path.lower().endswith('.pdf'):
        return False, "الملف ليس بصيغة PDF"
    
    try:
        with fitz.open(file_path) as doc:
            if len(doc) == 0:
                return False, "ملف PDF فارغ"
        return True, "ملف PDF صالح"
    except Exception as e:
        return False, f"ملف PDF تالف: {str(e)}"


def get_pdf_info(file_path: str) -> Dict[str, Any]:
    """
    الحصول على معلومات ملف PDF دون فتحه في معالج
    
    Args:
        file_path (str): مسار الملف
        
    Returns:
        Dict[str, Any]: معلومات الملف
    """
    try:
        with fitz.open(file_path) as doc:
            meta = doc.metadata
            return {
                'pages': len(doc),
                'title': meta.get('title', 'غير معروف'),
                'author': meta.get('author', 'غير معروف'),
                'is_encrypted': doc.is_encrypted,
                'file_size': os.path.getsize(file_path) if os.path.exists(file_path) else 0
            }
    except Exception as e:
        return {'error': str(e)}


if __name__ == "__main__":
    # اختبار الوحدة
    print("📚 وحدة معالج PDF جاهزة للاستخدام")
    print("واجهة البرمجة الرئيسية:")
    print("1. PDFHandler() - إنشاء معالج جديد")
    print("2. handler.open_pdf('file.pdf') - فتح ملف PDF")
    print("3. handler.get_page_image(0) - الحصول على صورة الصفحة الأولى")
    print("4. handler.search_in_pdf('نص') - البحث في الملف")
    print("5. handler.export_to_text('output.txt') - التصدير إلى نص")
