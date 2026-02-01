import asyncio
import logging
from woocommerce import API
import config  # خواندن تنظیمات امن از فایل کانفیگ

# اتصال به ووکامرس با استفاده از توکن‌های امن
wcapi = API(
    url=config.WC_URL,
    consumer_key=config.WC_KEY,
    consumer_secret=config.WC_SECRET,
    version="wc/v3",
    timeout=120  # تایم‌اوت بالا برای جلوگیری از قطع شدن
)

logger = logging.getLogger("SobhanBot")

class WCService:
    """
    لایه ارتباط با ووکامرس به صورت کاملاً Async (غیرهمگام).
    تمام درخواست‌ها با asyncio.to_thread اجرا می‌شوند تا ربات قفل نشود.
    """

    @staticmethod
    async def get_product(sku=None, pid=None):
        def _sync_req():
            try:
                if sku:
                    res = wcapi.get("products", params={"sku": sku.strip()})
                    data = res.json()
                    return data[0] if data else None
                elif pid:
                    res = wcapi.get(f"products/{pid}")
                    return res.json()
            except Exception as e:
                logger.error(f"WC API Error: {e}")
                return None
        
        # اجرای درخواست سنگین در ترد جداگانه
        return await asyncio.to_thread(_sync_req)

    @staticmethod
    async def get_categories(parent=0):
        def _sync_req():
            all_cats = []
            page = 1
            while True:
                try:
                    res = wcapi.get("products/categories", params={"parent": parent, "per_page": 50, "page": page})
                    if res.status_code != 200: break
                    data = res.json()
                    if not data: break
                    all_cats.extend(data)
                    page += 1
                except Exception as e:
                    logger.error(f"Category Fetch Error: {e}")
                    break
            return all_cats
        
        return await asyncio.to_thread(_sync_req)

    @staticmethod
    async def update_product(pid, data):
        def _sync_req():
            try:
                print(f"⚡ Sending Update for ID {pid}: {data}") # لاگ ارسال
                response = wcapi.put(f"products/{pid}", data)
                
                print(f"📬 Response Code: {response.status_code}") # لاگ کد وضعیت
                
                if response.status_code in [200, 201]:
                    print("✅ Update Successful")
                    return True
                else:
                    print(f"❌ Update Failed: {response.text}") # متن دقیق خطا
                    return False
            except Exception as e:
                config.logger.error(f"Update Exception: {e}")
                print(f"❌ Exception: {e}")
                return False
        return await asyncio.to_thread(_sync_req)

    @staticmethod
    async def batch_update(payload):
        def _sync_req():
            try:
                res = wcapi.post("products/batch", payload)
                return res.status_code == 200
            except Exception as e:
                logger.error(f"Batch Error: {e}")
                return False
        return await asyncio.to_thread(_sync_req)

    @staticmethod
    async def fetch_products_generator(cat_id=None, stock_status=None):
        """ژنراتور محصولات برای عملیات سنگین (لیست و تغییر گروهی)"""
        page = 1
        params = {"per_page": 50, "status": "publish"}
        if cat_id: params["category"] = cat_id
        if stock_status: params["stock_status"] = stock_status

        while True:
            def _fetch_page(p):
                try:
                    pp = params.copy()
                    pp["page"] = p
                    res = wcapi.get("products", params=pp)
                    if res.status_code == 200:
                        return res.json()
                except Exception as e:
                    logger.error(f"Fetch Generator Error: {e}")
                return None

            products = await asyncio.to_thread(_fetch_page, page)
            if not products: break
            yield products
            page += 1