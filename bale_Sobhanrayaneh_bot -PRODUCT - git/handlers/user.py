from services.bale import BaleService
from services.woo import WooService

bale = BaleService()
woo = WooService()

def handle_user_search(chat_id, text):
    """
    Searches WooCommerce for the text provided and sends results.
    """
    bale.send_message(chat_id, f"🔍 در حال جستجو برای: {text} ...")
    
    products = woo.search_products(text)

    if not products:
        bale.send_message(chat_id, "❌ محصولی با این نام یافت نشد.")
        return

    # Limit to top 5 results to avoid spamming
    for product in products[:5]:
        title = product.get("name")
        price = product.get("price") or "نامشخص"
        link = product.get("permalink")
        images = product.get("images", [])
        
        caption = (f"🛍 <b>{title}</b>\n"
                   f"💰 قیمت: {price} تومان\n\n"
                   f"🔗 <a href='{link}'>مشاهده در سایت</a>")

        if images:
            photo_url = images[0].get("src")
            bale.send_message(chat_id, caption) # Fallback if photo fails or just send caption
            # Better UX: Try sending photo, if fails (e.g. invalid URL), send text
            try:
                bale.send_photo(chat_id, photo_url, caption)
            except:
                bale.send_message(chat_id, caption)
        else:
            bale.send_message(chat_id, caption)