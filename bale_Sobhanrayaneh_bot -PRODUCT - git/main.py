import os
# --- تنظیمات حذف پروکسی ---
os.environ.pop("HTTP_PROXY", None)
os.environ.pop("HTTPS_PROXY", None)
os.environ.pop("http_proxy", None)
os.environ.pop("https_proxy", None)

import time
from config import Config
from services.bale import BaleService
from utils.state_manager import state_manager
from utils.auth_manager import auth
from handlers import admin

def main():
    bale = BaleService()
    last_update_id = 0
    
    print("🔒 Bot is running in PRIVATE MODE (Admins Only)...")

    # --- تعریف منوها (دکمه ویرایش اضافه شد) ---
    KEYBOARD_SUPER_ADMIN = [
        ["➕ افزودن محصول", "✏️ ویرایش محصول"],
        ["📊 دریافت گزارش", "👤 مدیریت ادمین‌ها"]
    ]
    
    KEYBOARD_SUB_ADMIN = [
        ["➕ افزودن محصول", "✏️ ویرایش محصول"]
    ]
    # -------------------

    while True:
        updates = bale.get_updates(offset=last_update_id + 1)
        
        if updates and updates.get("ok"):
            for update in updates["result"]:
                last_update_id = update["update_id"]
                
                if "message" not in update:
                    continue
                
                message = update["message"]
                chat_id = message["chat"]["id"]
                text = message.get("text", "")
                
                # 0. بررسی سطح دسترسی
                user_role = auth.get_role(chat_id)
                
                if user_role is None:
                    bale.send_message(chat_id, "⛔ <b>احراز هویت نشدید!</b>")
                    continue

                user_step = state_manager.get_step(chat_id)

                # 1. مدیریت دستور Start
                if text == "/start":
                    state_manager.clear_state(chat_id)
                    if user_role == "super_admin":
                        bale.send_message(chat_id, "👋 پنل مدیریت:", keyboard=KEYBOARD_SUPER_ADMIN)
                    elif user_role == "sub_admin":
                        bale.send_message(chat_id, "👋 پنل همکار:", keyboard=KEYBOARD_SUB_ADMIN)
                    continue

                # 2. ارجاع به هندلر ادمین
                # تمام دستورات (افزودن، ویرایش، مدیریت ادمین) در هندلر مدیریت می‌شوند
                try:
                    admin.handle_admin_flow(chat_id, message)
                except Exception as e:
                    print(f"Admin Handler Error: {e}")
                    bale.send_message(chat_id, "❌ خطای داخلی سیستم.")
                
        time.sleep(1)

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\nBot stopped.")