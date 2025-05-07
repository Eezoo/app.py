import os
import cv2
from datetime import datetime
import flet as ft
from flet import icons
from flet import *

class PhotoGalleryApp:
    """
    فئة تطبيق معرض الصور المتقدم
    تقوم بإنشاء واجهة مستخدم لالتقاط وعرض وإدارة الصور
    """
    
    def __init__(self):
        """تهيئة التطبيق وإعداد المتغيرات الأساسية"""
        self.image_dir = "photos"  # مجلد تخزين الصور
        os.makedirs(self.image_dir, exist_ok=True)  # إنشاء المجلد إذا لم يكن موجوداً
        self.selected_photos = []  # قائمة لتخزين الصور المحددة
        self.app = ft.app(target=self.main, view=ft.AppView.FLET_APP)  # إنشاء تطبيق Flet

    def main(self, page: ft.Page):
        """الدالة الرئيسية لتشغيل التطبيق"""
        self.page = page  # حفظ مرجع الصفحة
        self.setup_page()  # تهيئة إعدادات الصفحة
        self.create_controls()  # إنشاء عناصر التحكم
        self.setup_events()  # ربط الأحداث بالوظائف
        self.load_photos()  # تحميل الصور الموجودة
        self.page.add(self.build_ui())  # بناء واجهة المستخدم
        #############################################################################
        
        ############################################################################
        self.page.update()# تحديث الصفحة

    def setup_page(self):
        """تهيئة إعدادات صفحة التطبيق"""
        self.page.title = "معرض الصور المتقدم"
        self.page.window.left=1180
        self.page.window.top=70
        self.page.window.width = 350  # عرض النافذة
        self.page.window.height = 750  # ارتفاع النافذة
        self.page.theme_mode = ft.ThemeMode.LIGHT  # وضع السمة الفاتحة
        self.page.padding = 20  # الحشو الداخلي
        self.page.window.resizable = True  # قابلية تغيير حجم النافذة
        self.page.bgcolor = 'white'  # لون الخلفية
        self.page.fonts = {"arabic": "assets/NotoNaskhArabic-Regular.ttf"}  # إعداد الخط العربي
        self.page.theme = ft.Theme(font_family="arabic")  # تطبيق الخط العربي


    def create_controls(self):
        """إنشاء عناصر التحكم في الواجهة"""
        
        # حقل البحث
        self.search_field = ft.TextField(
            label="بحث عن الصور",
            hint_text="",
            width=250,
            border_radius=25,
            text_size=14,
            prefix_icon=icons.SEARCH,
            on_change=self.search_photos
        )
        
        # حقل إدخال اسم الصورة
        self.photo_name = ft.TextField(
            label="اسم الصورة",
            hint_text="أدخل اسمًا للصورة",
            width=200,
            border_radius=25,
            text_size=14
        )
        
        # زر التقاط الصورة
        self.capture_btn = ft.ElevatedButton(
            text=" ",
            icon=icons.CAMERA_ALT_OUTLINED,
            width=50,
            height=50,
            style=ft.ButtonStyle(
                shape=ft.RoundedRectangleBorder(radius=20),
                padding=10
            )
        )
        
        # أزرار التحكم
        self.delete_btn = ft.IconButton(
            icon=icons.DELETE,
            icon_color=ft.colors.RED,
            icon_size=30,
            tooltip="حذف المحدد",
            disabled=True
        )
        
        self.share_btn = ft.IconButton(
            icon=icons.SHARE,
            icon_color=ft.colors.BLUE,
            icon_size=30,
            tooltip="مشاركة",
            disabled=True
        )
        
        self.refresh_btn = ft.IconButton(
            icon=icons.REFRESH,
            icon_size=30,
            tooltip="تحديث",
            on_click=lambda e: self.load_photos()
        )
        
        # معرض الصور
        self.gallery = ft.GridView(
            expand=True,
            runs_count=3,  # عدد الأعمدة
            spacing=10,  # المسافة بين العناصر
            run_spacing=10,  # المسافة بين الصفوف
            padding=10  # الحشو الداخلي
        )
        
        # شريط الحالة
        self.status_bar = ft.Text(
            value="جاهز",
            size=12,
            color=ft.colors.GREY_600
        )

    def setup_events(self):
        """ربط الأحداث بالوظائف المناسبة"""
        self.capture_btn.on_click = self.capture_photo
        self.delete_btn.on_click = self.delete_photos
        self.share_btn.on_click = self.share_photos

    def capture_photo(self, e):
        """وظيفة التقاط صورة من الكاميرا"""
        name = self.photo_name.value.strip()
        if not name:
            self.show_status("الرجاء إدخال اسم الصورة", ft.colors.RED)
            return

        try:
            # فتح الكاميرا
            cap = cv2.VideoCapture(0)
            if not cap.isOpened():
                self.show_status("الكاميرا غير متوفرة", ft.colors.RED)
                return

            # التقاط الصورة
            ret, frame = cap.read()
            if not ret:
                self.show_status("فشل في التقاط الصورة", ft.colors.RED)
                return

            # حفظ الصورة
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"{name}_{timestamp}.jpg"
            filepath = os.path.join(self.image_dir, filename)
            
            cv2.imwrite(filepath, frame)
            self.show_status(f"تم حفظ الصورة: {filename}", ft.colors.GREEN)
            self.load_photos()
            
        except Exception as ex:
            self.show_status(f"خطأ: {str(ex)}", ft.colors.RED)
        finally:
            if 'cap' in locals():
                cap.release()  # إغلاق الكاميرا
            self.photo_name.value = ""
            self.page.update()

    def load_photos(self, search_query=None):
        """تحميل الصور من المجلد وعرضها في المعرض"""
        try:
            self.gallery.controls.clear()  # مسح المعرض الحالي
            photos = []  # قائمة لتخزين أسماء الصور
            
            # قراءة محتويات المجلد
            for f in os.listdir(self.image_dir):
                if f.lower().endswith(('.jpg', '.jpeg', '.png')):
                    if search_query and search_query.lower() not in f.lower():
                        continue  # تخطي الصور التي لا تطابق بحث
                    photos.append(f)
            
            # ترتيب الصور حسب تاريخ التعديل (الأحدث أولاً)
            photos.sort(key=lambda x: os.path.getmtime(os.path.join(self.image_dir, x)), reverse=True)
            
            # إذا لم توجد صور
            if not photos:
                self.gallery.controls.append(
                    ft.Container(
                        content=ft.Column([
                            ft.Icon(icons.PHOTO_LIBRARY, size=50, color=ft.colors.GREY_400),
                            ft.Text("لا توجد صور متاحة", size=16, color=ft.colors.GREY)
                        ], alignment=ft.MainAxisAlignment.CENTER, spacing=10),
                        alignment=ft.alignment.center
                    )
                )
                return
            
            # عرض كل الصور في المعرض
            for photo in photos:
                img_path = os.path.join(self.image_dir, photo)
                
                img_container = ft.Container(
                    content=ft.Column([
                        ft.Image(
                            src=img_path,
                            width=200,
                            height=150,
                            fit=ft.ImageFit.COVER,
                            border_radius=10
                        ),
                        ft.Text(
                            photo[:20] + (photo[20:] and '...'),  # تقليل طول اسم الملف إذا كان طويلاً
                            size=12,
                            text_align=ft.TextAlign.CENTER,
                            width=200
                        )
                    ], spacing=5),
                    data=img_path,  # تخزين مسار الصورة كبيانات
                    on_click=lambda e: self.toggle_select_photo(e),  # حدث النقر
                    border=ft.border.all(2, ft.colors.TRANSPARENT),  # حد شفاف
                    padding=5,
                    border_radius=10
                )
                
                self.gallery.controls.append(img_container)
            
            self.show_status(f"تم تحميل {len(photos)} صورة", ft.colors.GREEN)
            
        except Exception as ex:
            self.show_status(f"خطأ في تحميل الصور: {str(ex)}", ft.colors.RED)
        finally:
            self.page.update()

    def search_photos(self, e):
        """بحث الصور حسب النص المدخل"""
        self.load_photos(self.search_field.value)

    def toggle_select_photo(self, e):
        """تحديد أو إلغاء تحديد صورة"""
        img_path = e.control.data
        
        if img_path in self.selected_photos:
            # إلغاء التحديد
            self.selected_photos.remove(img_path)
            e.control.border = ft.border.all(2, ft.colors.TRANSPARENT)
        else:
            # تحديد الصورة
            self.selected_photos.append(img_path)
            e.control.border = ft.border.all(2, ft.colors.BLUE_400)
        
        # تفعيل/تعطيل الأزرار حسب وجود صور محددة
        self.delete_btn.disabled = len(self.selected_photos) == 0
        self.share_btn.disabled = len(self.selected_photos) == 0
        
        self.page.update()

    def delete_photos(self, e):
        """حذف الصور المحددة"""
        if not self.selected_photos:
            return
            
        try:
            for photo in self.selected_photos:
                try:
                    os.remove(photo)  # حذف الصورة
                except:
                    continue  # الاستمرار في حالة وجود خطأ
            
            self.show_status(f"تم حذف {len(self.selected_photos)} صورة", ft.colors.GREEN)
            self.selected_photos.clear()  # تفريغ القائمة
            self.delete_btn.disabled = True  # تعطيل زر الحذف
            self.share_btn.disabled = True  # تعطيل زر المشاركة
            self.load_photos()  # إعادة تحميل المعرض
            
        except Exception as ex:
            self.show_status(f"خطأ في الحذف: {str(ex)}", ft.colors.RED)

    def share_photos(self, e):
        """وظيفة مشاركة الصور (مكانية)"""
        if not self.selected_photos:
            return
            
        self.show_status(f"جاهز لمشاركة {len(self.selected_photos)} صورة", ft.colors.BLUE)
        # يمكن إضافة منطق المشاركة هنا (مثل رفع إلى السحابة أو إرسال بالبريد)

    def show_status(self, message, color=None):
        """عرض رسالة في شريط الحالة"""
        self.status_bar.value = message
        if color:
            self.status_bar.color = color
        self.page.update()

    def build_ui(self):
        """بناء واجهة المستخدم"""
        return ft.Column(
            controls=[
                # صف البحث والتحديث
                ft.Row([
                    self.search_field,
                    self.refresh_btn
                ], alignment=ft.MainAxisAlignment.CENTER),
                
                ft.Divider(height=20),
                
                # صف إدخال الاسم والالتقاط
                ft.Row([
                    self.photo_name,
                    self.capture_btn
                ], alignment=ft.MainAxisAlignment.CENTER),
                
                # صف أزرار التحكم
                ft.Row([
                    self.delete_btn,
                    self.share_btn
                ], alignment=ft.MainAxisAlignment.CENTER),
                
                ft.Divider(height=20),
                
                # معرض الصور
                ft.Container(
                    content=self.gallery,
                    border=ft.border.all(1, ft.colors.GREY_300),
                    border_radius=10,
                    expand=True
                ),
                
                ft.Divider(height=10),
                
                # شريط الحالة
                self.status_bar
            ],
            expand=True,
            spacing=10
        )

if __name__ == "__main__":
    # تشغيل التطبيق عند تنفيذ الملف مباشرة
    app = PhotoGalleryApp()
