import json
import os
from config import Config

ACCESS_FILE = "access_control.json"

class AuthManager:
    def __init__(self):
        self.super_admins = Config.ADMIN_IDS  # این‌ها از فایل .env می‌آیند و ثابت هستند
        self.sub_admins = self.load_sub_admins()

    def load_sub_admins(self):
        """لیست مدیران عادی را از فایل جیسون می‌خواند"""
        if not os.path.exists(ACCESS_FILE):
            return []
        try:
            with open(ACCESS_FILE, "r") as f:
                return json.load(f)
        except:
            return []

    def save_sub_admins(self):
        """لیست مدیران عادی را ذخیره می‌کند"""
        with open(ACCESS_FILE, "w") as f:
            json.dump(self.sub_admins, f)

    def get_role(self, user_id):
        """نقش کاربر را برمی‌گرداند: super_admin, sub_admin, یا None"""
        if user_id in self.super_admins:
            return "super_admin"
        if user_id in self.sub_admins:
            return "sub_admin"
        return None

    def add_admin(self, new_admin_id):
        """افزودن مدیر جدید (فقط اگر قبلاً نباشد)"""
        if new_admin_id not in self.sub_admins and new_admin_id not in self.super_admins:
            self.sub_admins.append(new_admin_id)
            self.save_sub_admins()
            return True
        return False

    def remove_admin(self, admin_id):
        """حذف مدیر (نمی‌توان مدیر کل را حذف کرد)"""
        if admin_id in self.sub_admins:
            self.sub_admins.remove(admin_id)
            self.save_sub_admins()
            return True
        return False

    def get_all_admins(self):
        """لیست همه مدیران برای نمایش"""
        return {
            "super": self.super_admins,
            "sub": self.sub_admins
        }

# نمونه جهانی برای استفاده در کل برنامه
auth = AuthManager()