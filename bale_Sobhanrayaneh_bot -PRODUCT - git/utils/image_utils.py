from PIL import Image
import io

def process_image(image_bytes):
    """
    تصویر را به ابعاد 512x512 تغییر سایز می‌دهد و حجم آن را به زیر 100 کیلوبایت می‌رساند.
    """
    try:
        # باز کردن تصویر از حافظه
        img = Image.open(io.BytesIO(image_bytes))
        
        # 1. تغییر سایز دقیق به 512x512 (ممکن است نسبت تصویر تغییر کند)
        # اگر می‌خواهید نسبت تصویر حفظ شود، به جای resize از thumbnail استفاده کنید
        img = img.resize((512, 512), Image.LANCZOS)
        
        # تبدیل به RGB (چون JPEG از شفافیت/Alpha پشتیبانی نمی‌کند)
        if img.mode in ("RGBA", "P"):
            img = img.convert("RGB")
            
        # 2. فشرده‌سازی تا رسیدن به حجم زیر 100KB
        output = io.BytesIO()
        quality = 95
        
        while quality > 10:
            output.seek(0)
            output.truncate()
            # ذخیره با کیفیت فعلی
            img.save(output, format="JPEG", quality=quality, optimize=True)
            
            # بررسی حجم
            size_kb = output.tell() / 1024
            if size_kb <= 100:
                break # اگر حجم مناسب بود، حلقه را بشکن
            
            quality -= 5 # کاهش کیفیت برای تلاش بعدی
            
        print(f"LOG: Image processed. Final Size: {int(size_kb)}KB, Quality: {quality}")
        return output.getvalue()

    except Exception as e:
        print(f"⚠️ Image Processing Error: {e}")
        return image_bytes # در صورت خطا، همان فایل اصلی را برگردان