import os
from utils.state_manager import state_manager
from services.bale import BaleService
from services.woo import WooService
from services.ai import AIService
from utils.image_utils import process_image  
# ایمپورت تابع جدید لاگ
from utils.excel_logger import log_product_to_excel, log_edit_to_excel, LOG_FILE
from utils.auth_manager import auth

bale = BaleService()
woo = WooService()
ai = AIService()

# --- مراحل وضعیت ---
WAITING_TITLE = "WAITING_TITLE"
WAITING_PRICE = "WAITING_PRICE"
WAITING_SKU = "WAITING_SKU"
WAITING_CATEGORY = "WAITING_CATEGORY"
WAITING_IMAGE = "WAITING_IMAGE"
WAITING_NEW_ADMIN_ID = "WAITING_NEW_ADMIN_ID"
WAITING_DEL_ADMIN_ID = "WAITING_DEL_ADMIN_ID"
WAITING_EDIT_SEARCH = "WAITING_EDIT_SEARCH"
WAITING_EDIT_ACTION = "WAITING_EDIT_ACTION"
WAITING_EDIT_VALUE = "WAITING_EDIT_VALUE"

# --- کیبوردها ---
BTN_CANCEL = [["🔙 انصراف"]]
BTN_FINISH_UPLOAD = [["✅ پایان ارسال و انتشار"], ["🔙 انصراف"]]

KB_MAIN_SUPER = [
    ["➕ افزودن محصول", "✏️ ویرایش محصول"],
    ["📊 دریافت گزارش", "👤 مدیریت ادمین‌ها"]
]

KB_MAIN_SUB = [
    ["➕ افزودن محصول", "✏️ ویرایش محصول"]
]

KB_ADMIN_PANEL = [
    ["➕ استخدام مدیر", "❌ حذف مدیر"],
    ["📋 لیست مدیران"],
    ["🔙 بازگشت"]
]

KB_EDIT_ACTIONS = [
    ["💰 تغییر قیمت", "📦 وضعیت موجودی"],
    ["📝 تغییر نام", "🔙 انصراف"]
]

KB_STOCK_STATUS = [
    ["✅ موجود (In Stock)", "❌ ناموجود (Out of Stock)"],
    ["🔙 انصراف"]
]

def handle_admin_flow(chat_id, message_data):
    text = message_data.get("text", "")
    current_step = state_manager.get_step(chat_id)
    user_role = auth.get_role(chat_id)

    main_kb = KB_MAIN_SUPER if user_role == "super_admin" else KB_MAIN_SUB

    # --- انصراف ---
    if text == "🔙 انصراف":
        state_manager.clear_state(chat_id)
        bale.send_message(chat_id, "لغو شد.", keyboard=main_kb)
        return

    # ==========================
    # بخش ۱: مدیریت سیستم (فقط مدیر کل)
    # ==========================
    if user_role == "super_admin":
        if text == "👤 مدیریت ادمین‌ها":
            bale.send_message(chat_id, "⚙️ پنل پرسنل:", keyboard=KB_ADMIN_PANEL)
            return
        if text == "🔙 بازگشت":
            bale.send_message(chat_id, "🏠 منوی اصلی:", keyboard=main_kb)
            return
        if text == "📋 لیست مدیران":
            admins = auth.get_all_admins()
            msg = f"👑 Super: {admins['super']}\n💼 Sub: {admins['sub']}"
            bale.send_message(chat_id, msg)
            return
        if text == "➕ استخدام مدیر":
            state_manager.clear_state(chat_id)
            state_manager.set_step(chat_id, WAITING_NEW_ADMIN_ID)
            bale.send_message(chat_id, "🔢 آیدی عددی:", keyboard=BTN_CANCEL)
            return
        if current_step == WAITING_NEW_ADMIN_ID:
            if text.isdigit() and auth.add_admin(int(text)):
                bale.send_message(chat_id, "✅ شد.", keyboard=KB_ADMIN_PANEL)
            else:
                bale.send_message(chat_id, "⚠️ نشد.", keyboard=KB_ADMIN_PANEL)
            state_manager.clear_state(chat_id)
            return
        if text == "❌ حذف مدیر":
            state_manager.clear_state(chat_id)
            state_manager.set_step(chat_id, WAITING_DEL_ADMIN_ID)
            bale.send_message(chat_id, "🔢 آیدی حذف:", keyboard=BTN_CANCEL)
            return
        if current_step == WAITING_DEL_ADMIN_ID:
            if text.isdigit() and auth.remove_admin(int(text)):
                bale.send_message(chat_id, "🗑 حذف شد.", keyboard=KB_ADMIN_PANEL)
            else:
                bale.send_message(chat_id, "⛔ نشد.", keyboard=KB_ADMIN_PANEL)
            state_manager.clear_state(chat_id)
            return
        if text == "📊 دریافت گزارش":
            if os.path.exists(LOG_FILE):
                bale.send_document(chat_id, LOG_FILE, caption="📊 گزارش جامع")
            else:
                bale.send_message(chat_id, "❌ خالی.")
            return

    # ==========================
    # بخش ۲: ویرایش محصول (کامل شده با لاگ)
    # ==========================
    
    # 1. درخواست ویرایش
    if text == "✏️ ویرایش محصول":
        state_manager.clear_state(chat_id)
        state_manager.set_step(chat_id, WAITING_EDIT_SEARCH)
        bale.send_message(chat_id, "🔍 لطفا <b>شناسه محصول (SKU)</b> را وارد کنید:", keyboard=BTN_CANCEL)
        return

    # 2. جستجو
    if current_step == WAITING_EDIT_SEARCH:
        bale.send_message(chat_id, "⏳ جستجو...")
        product = woo.get_product_by_sku(text)
        
        if not product:
            bale.send_message(chat_id, "❌ یافت نشد. مجدد تلاش کنید:", keyboard=BTN_CANCEL)
            return

        # ذخیره تمام اطلاعات لازم برای لاگ و آپدیت
        # اینجا نام و SKU را هم نگه می‌داریم
        edit_context = {
            "id": product['id'],
            "name": product['name'],
            "sku": product['sku']
        }
        state_manager.update_data(chat_id, "edit_context", edit_context)
        
        # نمایش اطلاعات
        title = product['name']
        price = product['regular_price'] or "ندارد"
        stock = "✅ موجود" if product['stock_status'] == 'instock' else "❌ ناموجود"
        img = product['images'][0]['src'] if product['images'] else None
        
        caption = (f"📦 <b>یافت شد:</b>\n🏷 {title}\n💰 {price} تومان\n📦 {stock}")
        
        if img:
            try: bale.send_photo(chat_id, img, caption)
            except: bale.send_message(chat_id, caption)
        else:
            bale.send_message(chat_id, caption)
            
        state_manager.set_step(chat_id, WAITING_EDIT_ACTION)
        bale.send_message(chat_id, "انتخاب عملیات:", keyboard=KB_EDIT_ACTIONS)
        return

    # 3. انتخاب عملیات
    if current_step == WAITING_EDIT_ACTION:
        if text == "💰 تغییر قیمت":
            state_manager.update_data(chat_id, "edit_mode", "price")
            state_manager.set_step(chat_id, WAITING_EDIT_VALUE)
            bale.send_message(chat_id, "💰 قیمت جدید (تومان):", keyboard=BTN_CANCEL)
            return
            
        if text == "📦 وضعیت موجودی":
            state_manager.update_data(chat_id, "edit_mode", "stock")
            state_manager.set_step(chat_id, WAITING_EDIT_VALUE)
            bale.send_message(chat_id, "📦 وضعیت جدید:", keyboard=KB_STOCK_STATUS)
            return

        if text == "📝 تغییر نام":
            state_manager.update_data(chat_id, "edit_mode", "name")
            state_manager.set_step(chat_id, WAITING_EDIT_VALUE)
            bale.send_message(chat_id, "📝 نام جدید:", keyboard=BTN_CANCEL)
            return

        bale.send_message(chat_id, "⛔ دکمه بزنید.")
        return

    # 4. اعمال تغییرات + لاگ
    if current_step == WAITING_EDIT_VALUE:
        data = state_manager.get_data(chat_id)
        ctx = data.get("edit_context") # اطلاعات محصول (id, name, sku)
        mode = data.get("edit_mode")
        
        update_data = {}
        log_action = ""
        log_details = ""
        
        # الف) قیمت
        if mode == "price":
            clean = text.replace(",", "")
            if not clean.isdigit():
                bale.send_message(chat_id, "⛔ فقط عدد.")
                return
            update_data = {"regular_price": clean}
            log_action = "تغییر قیمت"
            log_details = f"قیمت جدید: {clean}"

        # ب) موجودی
        elif mode == "stock":
            if "موجود (In Stock)" in text:
                update_data = {"stock_status": "instock", "manage_stock": False}
                log_action = "تغییر موجودی"
                log_details = "وضعیت: موجود"
            elif "ناموجود" in text:
                update_data = {"stock_status": "outofstock"}
                log_action = "تغییر موجودی"
                log_details = "وضعیت: ناموجود"
            else:
                bale.send_message(chat_id, "⛔ دکمه بزنید.")
                return

        # ج) نام
        elif mode == "name":
            update_data = {"name": text}
            log_action = "تغییر نام"
            log_details = f"نام جدید: {text}"

        # ارسال به ووکامرس
        bale.send_message(chat_id, "⏳ آپدیت...")
        res = woo.update_product(ctx['id'], update_data)
        
        if res:
            # --- لاگ کردن تغییرات در اکسل ---
            log_edit_to_excel(
                user_id=chat_id,
                title=ctx['name'],    # نام قدیمی محصول
                sku=ctx['sku'],
                action_type=log_action,
                details=log_details
            )
            # -------------------------------

            bale.send_message(chat_id, f"✅ انجام شد!\n📌 {log_details}", keyboard=main_kb)
        else:
            bale.send_message(chat_id, "❌ خطا در آپدیت.", keyboard=main_kb)
        
        state_manager.clear_state(chat_id)
        return

    # ==========================
    # بخش ۳: افزودن محصول (کدهای قبلی)
    # ==========================
    if text == "➕ افزودن محصول":
        state_manager.clear_state(chat_id)
        state_manager.set_step(chat_id, WAITING_TITLE)
        bale.send_message(chat_id, "🛒 <b>نام محصول</b>:", keyboard=BTN_CANCEL)
        return

    if current_step == WAITING_TITLE:
        state_manager.update_data(chat_id, "title", text)
        state_manager.set_step(chat_id, WAITING_PRICE)
        bale.send_message(chat_id, "💰 <b>قیمت</b> (تومان):", keyboard=BTN_CANCEL)
        return

    if current_step == WAITING_PRICE:
        clean = text.replace(",", "")
        if not clean.isdigit():
            bale.send_message(chat_id, "⛔ فقط عدد.")
            return
        state_manager.update_data(chat_id, "price", clean)
        state_manager.set_step(chat_id, WAITING_SKU)
        bale.send_message(chat_id, "🔖 <b>شناسه (SKU)</b>:", keyboard=BTN_CANCEL)
        return

    if current_step == WAITING_SKU:
        state_manager.update_data(chat_id, "sku", text)
        bale.send_message(chat_id, "⏳ دریافت دسته‌ها...")
        cats = woo.get_categories(parent=0)
        if not cats:
            bale.send_message(chat_id, "❌ خطا.", keyboard=BTN_CANCEL)
            return
        
        kb = []
        row = []
        valid = {}
        for c in cats:
            valid[c['name']] = c['id']
            row.append(c['name'])
            if len(row) == 2:
                kb.append(row)
                row = []
        if row: kb.append(row)
        kb.append(["🔙 انصراف"])

        state_manager.update_data(chat_id, "valid_cats", valid)
        state_manager.set_step(chat_id, WAITING_CATEGORY)
        bale.send_message(chat_id, "📂 انتخاب دسته:", keyboard=kb)
        return

    if current_step == WAITING_CATEGORY:
        data = state_manager.get_data(chat_id)
        valid = data.get("valid_cats", {})
        
        if text not in valid:
            bale.send_message(chat_id, "⛔ دکمه بزنید.")
            return

        cat_id = valid[text]
        subs = woo.get_categories(parent=cat_id)
        
        if subs:
            new_valid = {}
            new_kb = []
            row = []
            for c in subs:
                new_valid[c['name']] = c['id']
                row.append(c['name'])
                if len(row) == 2:
                    new_kb.append(row)
                    row = []
            if row: new_kb.append(row)
            new_kb.append(["🔙 انصراف"])
            state_manager.update_data(chat_id, "valid_cats", new_valid)
            bale.send_message(chat_id, f"📂 زیر‌دسته «{text}»:", keyboard=new_kb)
            return
        else:
            state_manager.update_data(chat_id, "cat_id", cat_id)
            title = data['title']
            
            bale.send_message(chat_id, "1️⃣ لینک...", keyboard=BTN_CANCEL)
            slug = ai.generate_slug(title)
            if not slug:
                bale.send_message(chat_id, "❌ خطا AI")
                return
            state_manager.update_data(chat_id, "seo_slug", slug)

            bale.send_message(chat_id, "2️⃣ مقاله...", keyboard=BTN_CANCEL)
            long = ai.generate_long_desc(title)
            if not long: return
            state_manager.update_data(chat_id, "seo_long", long)

            bale.send_message(chat_id, "3️⃣ خلاصه...", keyboard=BTN_CANCEL)
            short = ai.generate_short_desc(title)
            state_manager.update_data(chat_id, "seo_short", short)

            state_manager.update_data(chat_id, "uploaded_images", []) 
            
            state_manager.set_step(chat_id, WAITING_IMAGE)
            msg = "📸 عکس‌ها را بفرستید. در پایان دکمه 'پایان ارسال' را بزنید."
            bale.send_message(chat_id, msg, keyboard=BTN_FINISH_UPLOAD)
            return

    if current_step == WAITING_IMAGE:
        data = state_manager.get_data(chat_id)
        uploaded_images = data.get("uploaded_images", [])

        if text == "✅ پایان ارسال و انتشار":
            if not uploaded_images:
                bale.send_message(chat_id, "⛔ حداقل یک عکس لازم است.", keyboard=BTN_FINISH_UPLOAD)
                return
            
            bale.send_message(chat_id, f"🚀 انتشار...")
            
            result = woo.create_product(
                title=data['title'], price=data['price'], sku=data['sku'],
                category_id=data['cat_id'], slug=data['seo_slug'],
                description=data['seo_long'], short_description=data['seo_short'],
                image_ids=uploaded_images
            )

            if result and result.get("id"):
                link = result.get('permalink')
                log_product_to_excel(chat_id, data['title'], data['price'], data['sku'], link)
                bale.send_message(chat_id, f"✅ منتشر شد!\n🔗 {link}", keyboard=main_kb)
                state_manager.clear_state(chat_id)
            else:
                bale.send_message(chat_id, "❌ خطا در ثبت.")
            return

        if "photo" in message_data:
            bale.send_message(chat_id, "⏳ آپلود...")
            file_id = message_data["photo"][-1]["file_id"]
            path = bale.get_file_path(file_id)
            raw = bale.download_file(path)
            if not raw: return

            processed = process_image(raw)
            wp_id = woo.upload_image_to_wp(processed)

            if wp_id:
                uploaded_images.append(wp_id)
                state_manager.update_data(chat_id, "uploaded_images", uploaded_images)
                count = len(uploaded_images)
                bale.send_message(chat_id, f"✅ عکس {count} ثبت شد.", keyboard=BTN_FINISH_UPLOAD)
            else:
                bale.send_message(chat_id, "❌ خطا آپلود.")
            return
        
        else:
            bale.send_message(chat_id, "⛔ عکس بفرستید.")
            return