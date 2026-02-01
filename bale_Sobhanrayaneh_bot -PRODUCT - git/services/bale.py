import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry
from config import Config

class BaleService:
    def __init__(self):
        self.base_url = Config.BALE_API_URL
        self.file_base_url = Config.BALE_FILE_URL
        
        self.session = requests.Session()
        
        # --- مهم: غیرفعال کردن پروکسی برای بله ---
        self.session.trust_env = False 
        # ---------------------------------------
        
        retry_strategy = Retry(
            total=5,
            backoff_factor=1,
            status_forcelist=[429, 500, 502, 503, 504],
        )
        adapter = HTTPAdapter(max_retries=retry_strategy)
        self.session.mount("https://", adapter)
        self.session.mount("http://", adapter)

    def get_updates(self, offset=None):
        url = f"{self.base_url}/getUpdates"
        params = {"timeout": 10}
        if offset:
            params["offset"] = offset
        try:
            response = self.session.get(url, params=params, timeout=20)
            if response.status_code == 200:
                return response.json()
        except Exception as e:
            print(f"⚠️ Network Warning: {e}")
        return None

    def send_message(self, chat_id, text, keyboard=None):
        url = f"{self.base_url}/sendMessage"
        data = {"chat_id": chat_id, "text": text}
        if keyboard:
            data["reply_markup"] = {
                "keyboard": keyboard,
                "resize_keyboard": True,
                "one_time_keyboard": False
            }
        try:
            self.session.post(url, json=data, timeout=15)
        except Exception as e:
            print(f"❌ Failed to send message: {e}")

    def send_photo(self, chat_id, photo_url, caption=None):
        url = f"{self.base_url}/sendPhoto"
        data = {"chat_id": chat_id, "photo": photo_url}
        if caption: data["caption"] = caption
        try:
            self.session.post(url, json=data, timeout=40)
        except Exception as e:
            print(f"❌ Failed to send photo: {e}")

    def send_document(self, chat_id, file_path, caption=None):
        url = f"{self.base_url}/sendDocument"
        try:
            with open(file_path, 'rb') as f:
                files = {'document': f}
                data = {'chat_id': chat_id}
                if caption: data['caption'] = caption
                self.session.post(url, data=data, files=files, timeout=120)
        except Exception as e:
            print(f"❌ Failed to send document: {e}")

    def get_file_path(self, file_id):
        url = f"{self.base_url}/getFile"
        try:
            response = self.session.post(url, json={"file_id": file_id}, timeout=30)
            result = response.json()
            if result.get("ok"): return result["result"]["file_path"]
        except: pass
        return None

    def download_file(self, file_path):
        url = f"{self.file_base_url}/{file_path}"
        try:
            response = self.session.get(url, timeout=60)
            if response.status_code == 200: return response.content
        except: pass
        return None