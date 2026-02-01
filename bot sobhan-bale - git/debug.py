import config
from woocommerce import API
import sys

print("--- 🔍 START DEBUGGING ---")

# 1. بررسی متغیرها
print(f"1. Checking Config:")
print(f"   URL: {config.WC_URL}")
print(f"   Key Loaded: {'YES' if config.WC_KEY else 'NO'}")
print(f"   Secret Loaded: {'YES' if config.WC_SECRET else 'NO'}")

if not config.WC_URL or not config.WC_KEY:
    print("❌ ERROR: اطلاعات فایل .env خوانده نشد!")
    sys.exit()

# 2. تست اتصال
print("\n2. Testing Connection to WooCommerce...")
wcapi = API(
    url=config.WC_URL,
    consumer_key=config.WC_KEY,
    consumer_secret=config.WC_SECRET,
    version="wc/v3",
    timeout=30
)

try:
    # درخواست ساده برای گرفتن اطلاعات سیستم
    response = wcapi.get("system_status")
    
    print(f"   Response Code: {response.status_code}")
    
    if response.status_code == 200:
        print("✅ SUCCESS: ارتباط با سایت برقرار است!")
    elif response.status_code == 401:
        print("❌ ERROR 401: کلیدهای API اشتباه است (Unauthorized).")
    elif response.status_code == 404:
        print("❌ ERROR 404: آدرس سایت اشتباه است یا API ووکامرس فعال نیست.")
    else:
        print(f"❌ ERROR: {response.text}")

except Exception as e:
    print(f"❌ CRITICAL ERROR: {e}")

print("--- 🏁 END DEBUGGING ---")