import httpx
from openai import OpenAI
from config import Config

class AIService:
    def __init__(self):
        # تنظیم کلاینت برای اتصال مستقیم (بدون پروکسی)
        http_client = httpx.Client(
            timeout=60.0,
            follow_redirects=True,
            verify=False,
            # --- مهم: اگر فیلتر نیست، حتما False باشد ---
            trust_env=False  
            # --------------------------------------------
        )
        
        self.client = OpenAI(
            base_url="https://api.gapgpt.app/v1",
            api_key=Config.GAP_API_KEY,
            http_client=http_client,
            max_retries=1
        )

    def _send_request(self, system_msg, user_msg):
        """تابع کمکی برای ارسال درخواست به هوش مصنوعی"""
        try:
            response = self.client.chat.completions.create(
                model="gpt-5-nano",
                messages=[
                    {"role": "system", "content": system_msg},
                    {"role": "user", "content": user_msg}
                ],
                temperature=0.7
            )
            return response.choices[0].message.content.strip()
        except Exception as e:
            print(f"⚠️ AI Connection Error: {e}")
            return None

    def generate_slug(self, product_name):
        print(f"LOG: Generating SLUG for {product_name}...")
        # برای اسلاگ نیازی به تغییر خاصی نیست، اما پرامپت را کمی دقیق‌تر می‌کنیم
        sys = "You are a URL slug generator used for an electronics e-commerce store."
        usr = f"Convert this product title to a clean URL slug (English, lowercase, dashes only, remove special chars): '{product_name}'"
        result = self._send_request(sys, usr)
        if result:
            return result.replace(" ", "-").lower()
        return None

    def generate_short_desc(self, product_name):
        print(f"LOG: Generating SHORT DESC for {product_name}...")
        
        # System Prompt: تعریف نقش فروشنده تخصصی مانیتور و تجهیزات جانبی
        sys = 'You are an expert Copywriter for "Sobhan Rayaneh" (Specialist in Monitors, All-in-One PCs, Laptops, and Ergonomic Stands). You MUST output in PERSIAN only.'
        
        # User Prompt: تمرکز بر کیفیت تصویر، ارگونومی و گارانتی
        usr = (
            f"Write a persuasive, trustworthy, 2-line Persian product summary for: '{product_name}'.\n"
            "Focus on: Display Quality (for screens), Ergonomics/Stability (for stands), and Build Quality.\n"
            "Keywords to include: [سبحان رایانه, ضمانت اصالت, کیفیت ساخت بالا, ارسال ایمن].\n"
            "Strict Rules: NO emojis. NO price. Max 2 lines. Tone: Professional and inviting."
        )
        
        return self._send_request(sys, usr)

    def generate_long_desc(self, product_name):
        print(f"LOG: Generating LONG DESC with FAQ for {product_name}...")
        
        # System Prompt: متخصص سخت‌افزار و تجهیزات اداری/گیمینگ
        sys = 'You are a Senior Tech Reviewer & SEO Specialist for "Sobhan Rayaneh" (Retailer of High-end Monitors, AiOs, Laptops, and Monitor Arms). Output in PERSIAN only.'
        
        # User Prompt: ساختار نقد و بررسی متناسب با مانیتور و پایه
        usr = (
            f"Write a comprehensive, professional Persian HTML product review for '{product_name}'.\n"
            "Target Audience: Professionals, Gamers, and Office users looking for ergonomic setups or high-quality displays.\n\n"
            "**Required HTML Structure:**\n"
            f"1. <h2>نقد و بررسی تخصصی {product_name}</h2>: A detailed paragraph about the product's performance, visual experience (if monitor) or stability/ergonomics (if stand).\n"
            "2. <h3>ویژگی‌های فنی و کاربردها</h3>: Use <ul><li> to list specific specs (e.g., Panel Type/Refresh Rate for screens, VESA compatibility/Weight capacity for stands, CPU/Ram for Laptops/AiO).\n"
            "3. <h3>نکات مهم پیش از خرید</h3>: Briefly advise checking compatibility (e.g., checking VESA for arms, or Port connectivity for monitors). Mention that choosing the right equipment improves health and productivity.\n"
            "4. <h3>چرا خرید از سبحان رایانه؟</h3>: Explain that Sobhan Rayaneh specializes in **Display & Ergonomic Solutions**. Highlight **Safe Packaging** (crucial for fragile monitors), **Official Warranty**, and **Expert Pre-sales Advice**. (Do NOT mention repair services like soldering).\n"
            "5. <h3>سوالات متداول کاربران</h3>: Generate 3-4 relevant Q&A pairs. One question MUST be about 'Shipping Safety' or 'Compatibility'. Answer it by assuring safe packaging and consulting with Sobhan Rayaneh experts.\n\n"
            "**Constraints:**\n"
            "- Use relevant LSI keywords: [خرید مانیتور و آل این وان, پایه نگهدارنده مانیتور, تجهیزات ارگونومیک, گارانتی معتبر سبحان رایانه, مشاوره تخصصی].\n"
            "- NO emojis. NO prices. NO <html>/<body> tags.\n"
            "- Keep the tone authoritative, modern, and 100% Persian."
        )
        
        return self._send_request(sys, usr)