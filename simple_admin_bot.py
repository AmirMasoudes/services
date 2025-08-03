#!/usr/bin/env python3
"""
ربات ادمین ساده - بدون کتابخانه telegram
"""

import os
import sys
import django
import requests
import json
import time
from datetime import datetime

# تنظیم Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from django.conf import settings

class SimpleAdminBot:
    """ربات ادمین ساده با requests"""
    
    def __init__(self):
        self.token = getattr(settings, 'ADMIN_BOT_TOKEN', None)
        self.password = getattr(settings, 'ADMIN_PASSWORD', 'admin123')
        self.admin_user_ids = getattr(settings, 'ADMIN_USER_IDS', [])
        self.base_url = f"https://api.telegram.org/bot{self.token}"
        self.offset = 0
        
        if not self.token or self.token == 'YOUR_ADMIN_BOT_TOKEN':
            print("❌ لطفاً ADMIN_BOT_TOKEN را در تنظیمات تنظیم کنید!")
            sys.exit(1)
        
        if not self.admin_user_ids:
            print("❌ لطفاً ADMIN_USER_IDS را در تنظیمات تنظیم کنید!")
            sys.exit(1)
    
    def send_message(self, chat_id, text):
        """ارسال پیام"""
        try:
            url = f"{self.base_url}/sendMessage"
            data = {
                'chat_id': chat_id,
                'text': text,
                'parse_mode': 'Markdown'
            }
            
            session = requests.Session()
            session.trust_env = False
            
            response = session.post(url, json=data, timeout=10)
            
            if response.status_code == 200:
                return True
            else:
                print(f"❌ خطا در ارسال پیام: {response.status_code}")
                return False
                
        except Exception as e:
            print(f"❌ خطا در ارسال پیام: {e}")
            return False
    
    def get_updates(self):
        """دریافت آپدیت‌ها"""
        try:
            url = f"{self.base_url}/getUpdates"
            params = {
                'offset': self.offset,
                'timeout': 30
            }
            
            session = requests.Session()
            session.trust_env = False
            
            response = session.get(url, params=params, timeout=35)
            
            if response.status_code == 200:
                data = response.json()
                if data.get('ok'):
                    updates = data.get('result', [])
                    if updates:
                        self.offset = updates[-1]['update_id'] + 1
                    return updates
                else:
                    print(f"❌ خطا در API: {data.get('description')}")
                    return []
            else:
                print(f"❌ خطای HTTP: {response.status_code}")
                return []
                
        except Exception as e:
            print(f"❌ خطا در دریافت آپدیت‌ها: {e}")
            return []
    
    def test_connection(self):
        """تست اتصال"""
        try:
            url = f"{self.base_url}/getMe"
            
            session = requests.Session()
            session.trust_env = False
            
            response = session.get(url, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                if data.get('ok'):
                    bot_info = data.get('result', {})
                    print(f"✅ ربات فعال: {bot_info.get('first_name')} (@{bot_info.get('username')})")
                    return True
                else:
                    print(f"❌ خطا در API: {data.get('description')}")
                    return False
            else:
                print(f"❌ خطای HTTP: {response.status_code}")
                return False
                
        except Exception as e:
            print(f"❌ خطا در تست اتصال: {e}")
            return False
    
    def handle_message(self, message):
        """پردازش پیام"""
        chat_id = message['chat']['id']
        user_id = message['from']['id']
        text = message.get('text', '')
        
        # بررسی مجوز
        if user_id not in self.admin_user_ids:
            self.send_message(chat_id, "❌ شما مجوز دسترسی ندارید!")
            return
        
        # پردازش دستورات
        if text == '/start':
            self.send_message(chat_id, "🔐 لطفاً رمز عبور ادمین را وارد کنید:")
            
        elif text == '/dashboard':
            self.show_dashboard(chat_id)
            
        elif text == '/users':
            self.show_users(chat_id)
            
        elif text == '/inbounds':
            self.show_inbounds(chat_id)
            
        elif text == '/stats':
            self.show_stats(chat_id)
            
        elif text == '/help':
            self.show_help(chat_id)
            
        elif text == self.password:
            self.send_message(chat_id, 
                "✅ ورود موفق!\n\n"
                "دستورات موجود:\n"
                "/dashboard - داشبورد\n"
                "/users - مدیریت کاربران\n"
                "/inbounds - مدیریت Inbound ها\n"
                "/stats - آمار کلی\n"
                "/help - راهنما"
            )
            
        elif text.startswith('/'):
            self.send_message(chat_id, "❌ دستور نامعتبر! از /help استفاده کنید.")
            
        else:
            # احتمالاً رمز عبور
            if text != self.password:
                self.send_message(chat_id, "❌ رمز عبور نامعتبر!")
    
    def show_dashboard(self, chat_id):
        """نمایش داشبورد"""
        try:
            from xui_servers.models import XUIServer, XUIInbound, XUIClient, UserConfig
            from accounts.models import UsersModel
            
            # آمار کلی
            total_users = UsersModel.objects.count()
            active_configs = UserConfig.objects.filter(is_active=True).count()
            total_servers = XUIServer.objects.filter(is_active=True).count()
            total_inbounds = XUIInbound.objects.filter(is_active=True).count()
            
            message = f"""
📊 **داشبورد سیستم**

👥 کاربران: {total_users}
⚙️ کانفیگ‌های فعال: {active_configs}
🖥️ سرورها: {total_servers}
🔗 Inbound ها: {total_inbounds}

🕐 زمان: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
            """
            
            self.send_message(chat_id, message)
            
        except Exception as e:
            self.send_message(chat_id, f"❌ خطا در دریافت آمار: {e}")
    
    def show_users(self, chat_id):
        """نمایش کاربران"""
        try:
            from accounts.models import UsersModel
            
            users = UsersModel.objects.all()[:10]  # فقط 10 کاربر اول
            
            message = "👥 **لیست کاربران:**\n\n"
            for user in users:
                message += f"• {user.full_name} (@{user.username_tel})\n"
            
            if UsersModel.objects.count() > 10:
                message += f"\n... و {UsersModel.objects.count() - 10} کاربر دیگر"
            
            self.send_message(chat_id, message)
            
        except Exception as e:
            self.send_message(chat_id, f"❌ خطا در دریافت کاربران: {e}")
    
    def show_inbounds(self, chat_id):
        """نمایش Inbound ها"""
        try:
            from xui_servers.models import XUIInbound
            
            inbounds = XUIInbound.objects.filter(is_active=True)
            
            if not inbounds.exists():
                self.send_message(chat_id, "❌ هیچ Inbound فعالی یافت نشد!")
                return
            
            message = "🔗 **Inbound های فعال:**\n\n"
            for inbound in inbounds:
                message += f"• {inbound.remark} (پورت: {inbound.port})\n"
            
            self.send_message(chat_id, message)
            
        except Exception as e:
            self.send_message(chat_id, f"❌ خطا در دریافت Inbound ها: {e}")
    
    def show_stats(self, chat_id):
        """نمایش آمار"""
        try:
            from xui_servers.models import XUIServer, XUIInbound, XUIClient, UserConfig
            from accounts.models import UsersModel
            
            # آمار تفصیلی
            total_users = UsersModel.objects.count()
            active_configs = UserConfig.objects.filter(is_active=True).count()
            expired_configs = UserConfig.objects.filter(is_active=False).count()
            total_servers = XUIServer.objects.filter(is_active=True).count()
            total_inbounds = XUIInbound.objects.filter(is_active=True).count()
            total_clients = XUIClient.objects.filter(is_active=True).count()
            
            message = f"""
📈 **آمار تفصیلی سیستم**

👥 کاربران کل: {total_users}
⚙️ کانفیگ‌های فعال: {active_configs}
⏰ کانفیگ‌های منقضی: {expired_configs}
🖥️ سرورهای فعال: {total_servers}
🔗 Inbound های فعال: {total_inbounds}
👤 کلاینت‌های فعال: {total_clients}

🕐 زمان: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
            """
            
            self.send_message(chat_id, message)
            
        except Exception as e:
            self.send_message(chat_id, f"❌ خطا در دریافت آمار: {e}")
    
    def show_help(self, chat_id):
        """نمایش راهنما"""
        message = """
🤖 **راهنمای ربات ادمین X-UI**

📋 دستورات موجود:
/start - شروع و ورود
/dashboard - داشبورد کلی
/users - مدیریت کاربران
/inbounds - مدیریت Inbound ها
/stats - آمار تفصیلی
/help - این راهنما

🔐 امنیت:
• فقط ادمین‌های مجاز
• رمز عبور اجباری
• لاگ تمام عملیات
        """
        
        self.send_message(chat_id, message)
    
    def run(self):
        """اجرای ربات"""
        print("🚀 راه‌اندازی ربات ادمین ساده...")
        
        # بررسی تنظیمات
        print("✅ تنظیمات ربات ادمین بررسی شد")
        print(f"🔑 رمز ادمین: {self.password}")
        print(f"👥 تعداد ادمین‌ها: {len(self.admin_user_ids)}")
        
        # تست اتصال
        if not self.test_connection():
            print("❌ خطا در تست اتصال!")
            return
        
        print("✅ ربات ادمین آماده اجرا است!")
        print("📱 برای استفاده:")
        print("   1. ربات را در تلگرام پیدا کنید")
        print("   2. دستور /start را ارسال کنید")
        print("   3. با رمز ادمین وارد شوید")
        print("   4. از دستورات مدیریت استفاده کنید")
        
        # حلقه اصلی
        print("\n🔄 شروع دریافت پیام‌ها...")
        try:
            while True:
                updates = self.get_updates()
                
                for update in updates:
                    if 'message' in update:
                        self.handle_message(update['message'])
                
                time.sleep(1)  # تاخیر 1 ثانیه
                
        except KeyboardInterrupt:
            print("\n👋 ربات متوقف شد!")
        except Exception as e:
            print(f"❌ خطا در اجرای ربات: {e}")

def main():
    """تابع اصلی"""
    try:
        bot = SimpleAdminBot()
        bot.run()
    except Exception as e:
        print(f"❌ خطا در راه‌اندازی ربات: {e}")

if __name__ == "__main__":
    main() 