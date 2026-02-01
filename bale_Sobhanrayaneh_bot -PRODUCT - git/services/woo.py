import requests
from woocommerce import API
from config import Config

class WooService:
    def __init__(self):
        self.wcapi = API(
            url=Config.WOO_URL,
            consumer_key=Config.WOO_KEY,
            consumer_secret=Config.WOO_SECRET,
            version="wc/v3",
            timeout=40
        )

        if hasattr(Config, 'WP_USERNAME') and Config.WP_USERNAME and hasattr(Config, 'WP_APP_PASSWORD') and Config.WP_APP_PASSWORD:
            self.auth = (Config.WP_USERNAME, Config.WP_APP_PASSWORD)
        else:
            self.auth = (Config.WOO_KEY, Config.WOO_SECRET)

    def search_products(self, query):
        try:
            products = self.wcapi.get("products", params={"search": query, "status": "publish"}).json()
            return products
        except Exception as e:
            print(f"Woo Search Error: {e}")
            return []

    def get_categories(self, parent=0):
        try:
            params = {"per_page": 50, "orderby": "count", "order": "desc", "parent": parent}
            cats = self.wcapi.get("products/categories", params=params).json()
            return cats
        except Exception as e:
            print(f"Get Categories Error: {e}")
            return []

    def upload_image_to_wp(self, image_data, filename="product.jpg"):
        url = f"{Config.WOO_URL}/wp-json/wp/v2/media"
        headers = {
            "User-Agent": "Mozilla/5.0",
            "Content-Disposition": f"attachment; filename={filename}",
            "Content-Type": "image/jpeg"
        }
        try:
            response = requests.post(url, data=image_data, headers=headers, auth=self.auth)
            if response.status_code == 201:
                return response.json().get('id')
            return None
        except Exception:
            return None

    def create_product(self, title, price, sku, category_id, slug, description, short_description, image_ids):
        meta_data = [{"key": "_yoast_wpseo_focuskw", "value": title}]
        # تبدیل لیست آیدی‌ها
        images_data = [{"id": img_id} for img_id in image_ids]

        data = {
            "name": title,
            "type": "simple",
            "regular_price": str(price),
            "sku": sku,
            "slug": slug,
            "description": description,
            "short_description": short_description,
            "categories": [{"id": category_id}] if category_id else [],
            "images": images_data,
            "meta_data": meta_data
        }
        
        try:
            response = self.wcapi.post("products", data)
            if response.status_code == 201:
                return response.json()
            else:
                print(f"Create Error: {response.text}")
                return None
        except Exception as e:
            print(f"Create Exception: {e}")
            return None

    # --- توابع جدید برای بخش ویرایش ---

    def get_product_by_sku(self, sku):
        """یافتن محصول بر اساس شناسه SKU"""
        try:
            # جستجوی دقیق SKU
            products = self.wcapi.get("products", params={"sku": sku}).json()
            if products:
                return products[0]
            return None
        except Exception as e:
            print(f"Get SKU Error: {e}")
            return None

    def update_product(self, product_id, data):
        """آپدیت محصول با ID"""
        try:
            response = self.wcapi.put(f"products/{product_id}", data)
            if response.status_code == 200:
                return response.json()
            return None
        except Exception as e:
            print(f"Update Error: {e}")
            return None