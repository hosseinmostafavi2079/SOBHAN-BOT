import csv
import os
from datetime import datetime
from functools import wraps
from telegram import Update
from telegram.ext import ContextTypes, ConversationHandler
import config

try:
    from reportlab.lib import colors
    from reportlab.lib.pagesizes import A4
    from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    from reportlab.lib.enums import TA_RIGHT
    from reportlab.pdfbase import pdfmetrics
    from reportlab.pdfbase.ttfonts import TTFont
    import arabic_reshaper
    from bidi.algorithm import get_display
    PDF_SUPPORT = True
except ImportError:
    PDF_SUPPORT = False

class Utils:
    @staticmethod
    def to_english(text):
        if not text: return ""
        text = str(text).strip()
        replacements = {'۰': '0', '۱': '1', '۲': '2', '۳': '3', '۴': '4', '۵': '5', '۶': '6', '۷': '7', '۸': '8', '۹': '9', ',': '', '،': ''}
        for old, new in replacements.items(): text = text.replace(old, new)
        return text

    @staticmethod
    def format_price(price):
        if not price or price == "": return "0"
        try: return f"{int(float(price)):,}"
        except: return str(price)

    @staticmethod
    def reshape_fa(text):
        if not PDF_SUPPORT or not text: return str(text) if text else ""
        try: return get_display(arabic_reshaper.reshape(str(text)))
        except: return str(text)

class Security:
    @staticmethod
    def authorize(func):
        @wraps(func)
        async def wrapper(update: Update, context: ContextTypes.DEFAULT_TYPE, *args, **kwargs):
            user_id = update.effective_user.id
            # بررسی وجود کاربر در لیست جدید
            if user_id not in config.AUTHORIZED_USERS:
                await update.message.reply_text("⛔ شما مجوز دسترسی ندارید.")
                return ConversationHandler.END
            return await func(update, context, *args, **kwargs)
        return wrapper

    @staticmethod
    def log_audit(user_id, action, sku, detail):
        """ثبت لاگ با نام کاربر و SKU واقعی"""
        try:
            # دریافت اطلاعات کاربر از کانفیگ
            user_info = config.AUTHORIZED_USERS.get(user_id, {"name": "ناشناس", "role": "unknown"})
            user_name = user_info['name']
            role = user_info['role']
            
            ts = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            file_path = config.LOG_FILE
            
            needs_header = not os.path.exists(file_path) or os.path.getsize(file_path) == 0
            
            with open(file_path, 'a', newline='', encoding='utf-8-sig') as f:
                writer = csv.writer(f)
                if needs_header:
                    writer.writerow(["تاریخ و ساعت", "نام کاربر", "نقش", "عملیات", "کد محصول (SKU)", "جزئیات"])
                
                # ثبت نام به جای آیدی
                writer.writerow([ts, user_name, role, action, sku, detail])
                
            print(f"✅ LOG: {user_name} -> {action} on {sku}")
            
        except Exception as e:
            print(f"❌ LOG ERROR: {e}")
            config.logger.error(f"Audit Log Error: {e}")