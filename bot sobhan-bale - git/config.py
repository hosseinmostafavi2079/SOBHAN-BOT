# --- فایل اصلاح شده: config.py ---
import os
from dotenv import load_dotenv
import logging

load_dotenv()

# --- مسیردهی دقیق ---
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# --- تنظیمات اصلی (تغییر یافته برای بله) ---
# توکن را از بازوی BotFather در بله بگیرید
BALE_TOKEN = os.getenv("BALE_TOKEN") 

# آدرس‌های اختصاصی سرور بله
BALE_API_BASE_URL = "https://tapi.bale.ai/bot"
BALE_FILE_BASE_URL = "https://tapi.bale.ai/file/bot"

WC_URL = os.getenv("WC_URL")
WC_KEY = os.getenv("WC_KEY")
WC_SECRET = os.getenv("WC_SECRET")

# --- تنظیمات فایل‌ها ---
FONT_PATH = os.path.join(BASE_DIR, "IRANSans(FaNum)_Medium.ttf")
LOG_FILE = os.path.join(BASE_DIR, "audit_log.csv")
FONT_NAME_INTERNAL = "PersianFont"

# --- سطح دسترسی ---
# نکته مهم: در بله هم شناسه عددی (User ID) وجود دارد.
# ادمین‌ها باید ابتدا یک پیام به ربات بدهند تا ID آن‌ها در لاگ چاپ شود و اینجا جایگزین کنند.
AUTHORIZED_USERS = {
    int(os.getenv("ADMIN_ID_1", 0)): {"name": "mostafavi ", "role": "admin"},
    #int(os.getenv("ADMIN_ID_3", 0)): {"name": "h.maghzian", "role": "manager"},
    #int(os.getenv("ADMIN_ID_2", 0)): {"name": "foroshgah", "role": "manager"},
    #int(os.getenv("ADMIN_ID_4", 0)): {"name": "h.kahkeshan", "role": "manager"}
}

# --- وضعیت‌های گفتگو (بدون تغییر) ---
(
    MENU_STATE,
    WAIT_LIST_FILTER, WAIT_LIST_PARENT, WAIT_LIST_SUB,
    WAIT_BULK_SCOPE, WAIT_BULK_CAT, WAIT_BULK_METHOD, WAIT_BULK_VALUE, WAIT_BULK_CONFIRM,
    WAIT_REM_SCOPE, WAIT_REM_CAT, WAIT_REM_CONFIRM,
    WAIT_EXP_TYPE, WAIT_EXP_SCOPE, WAIT_EXP_CAT,
    WAIT_INPUT_PRICE, WAIT_INPUT_ADD, WAIT_INPUT_REDUCE
) = range(18)

# --- تنظیمات لاگ ---
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger("SobhanBot_Bale")