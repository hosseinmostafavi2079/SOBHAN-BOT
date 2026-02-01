import os
from dotenv import load_dotenv

# Load .env file
load_dotenv()

class Config:
    BALE_TOKEN = os.getenv("BALE_BOT_TOKEN")
    WOO_URL = os.getenv("WOO_URL")
    WOO_KEY = os.getenv("WOO_CONSUMER_KEY")
    WOO_SECRET = os.getenv("WOO_CONSUMER_SECRET")
    WP_USERNAME = os.getenv("WP_USERNAME")
    WP_APP_PASSWORD = os.getenv("WP_APP_PASSWORD")
    GAP_API_KEY = os.getenv("GAP_API_KEY")
    
    # Convert comma-separated string to a list of integers
    admin_ids_str = os.getenv("ADMIN_IDS", "")
    ADMIN_IDS = [int(x) for x in admin_ids_str.split(",")] if admin_ids_str else []

    # API Base URLs
    BALE_API_URL = f"https://tapi.bale.ai/bot{BALE_TOKEN}"
    BALE_FILE_URL = f"https://tapi.bale.ai/file/bot{BALE_TOKEN}"