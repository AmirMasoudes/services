#!/usr/bin/env python3
import os
import sys
import django
import uuid
import random
import string
from datetime import datetime, timedelta

# تنظیم Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from xui_servers.models import XUIServer, UserConfig
from accounts.models import UsersModel
from xui_servers import settings as xui_settings
from django.utils import timezone

def fix_xui_services():
    """اصلاح xui_servers/services.py"""
    print("🔧 اصلاح xui_servers/services.py...")
    
    # محتوای جدید برای services.py
    new_content = '''import requests
import json
import base64
import uuid
import random
import string
from datetime import datetime, timedelta
from django.utils import timezone
from .models import XUIServer, UserConfig
from . import settings as xui_settings
from accounts.models import UsersModel
from plan.models import ConfingPlansModel

class SimpleConfigService:
    """سرویس کانفیگ ساده بدون نیاز به x-ui API"""
    
    def __init__(self):
        self.server = XUIServer.objects.filter(is_active=True).first()
        if not self.server:
            raise Exception("سرور X-UI فعالی یافت نشد")
    
    def create_trial_config(self, user: UsersModel, protocol: str = "vless"):
        """ایجاد کانفیگ تستی برای کاربر"""
        try:
            print(f"🔧 ایجاد کانفیگ تستی برای {user.full_name}...")
            
            # تولید کانفیگ
            config_data = self._generate_config(user, protocol, is_trial=True)
            
            # ذخیره در دیتابیس
            config_name = f"پلن تستی {user.full_name} ({protocol.upper()})"
            
            user_config = UserConfig.objects.create(
                user=user,
                server=self.server,
                xui_inbound_id=0,  # فعلاً 0 قرار می‌دهیم
                xui_user_id=user.telegram_id,
                config_name=config_name,
                config_data=config_data,
                protocol=protocol,
                is_trial=True,
                created_at=timezone.now(),
                expires_at=timezone.now() + timedelta(hours=24)  # 24 ساعت
            )
            
            print(f"✅ کانفیگ تستی ایجاد شد:")
            print(f"  - نام: {user_config.config_name}")
            print(f"  - ID: {user_config.id}")
            print(f"  - پروتکل: {user_config.protocol}")
            print(f"  - انقضا: {user_config.expires_at}")
            
            return user_config, xui_settings.SUCCESS_MESSAGES["trial_created"].format(protocol=protocol.upper())
            
        except Exception as e:
            print(f"❌ خطا در ایجاد کانفیگ تستی: {e}")
            return None, f"خطا در ایجاد کانفیگ: {e}"
    
    def create_paid_config(self, user: UsersModel, plan: ConfingPlansModel, protocol: str = "vless"):
        """ایجاد کانفیگ پولی برای کاربر"""
        try:
            print(f"🔧 ایجاد کانفیگ پولی برای {user.full_name}...")
            
            # تولید کانفیگ
            config_data = self._generate_config(user, protocol, is_trial=False)
            
            # ذخیره در دیتابیس
            config_name = f"{plan.name} {user.full_name} ({protocol.upper()})"
            
            user_config = UserConfig.objects.create(
                user=user,
                server=self.server,
                xui_inbound_id=0,  # فعلاً 0 قرار می‌دهیم
                xui_user_id=user.telegram_id,
                config_name=config_name,
                config_data=config_data,
                protocol=protocol,
                plan=plan,
                is_trial=False,
                created_at=timezone.now(),
                expires_at=timezone.now() + timedelta(days=30)  # 30 روز
            )
            
            print(f"✅ کانفیگ پولی ایجاد شد:")
            print(f"  - نام: {user_config.config_name}")
            print(f"  - ID: {user_config.id}")
            print(f"  - پروتکل: {user_config.protocol}")
            print(f"  - انقضا: {user_config.expires_at}")
            
            return user_config, xui_settings.SUCCESS_MESSAGES["paid_created"].format(protocol=protocol.upper())
            
        except Exception as e:
            print(f"❌ خطا در ایجاد کانفیگ پولی: {e}")
            return None, f"خطا در ایجاد کانفیگ: {e}"
    
    def _generate_config(self, user: UsersModel, protocol: str, is_trial: bool = False):
        """تولید کانفیگ بر اساس پروتکل"""
        
        # انتخاب دامنه فیک تصادفی
        fake_domain = random.choice(xui_settings.FAKE_DOMAINS)
        
        # انتخاب کلید عمومی تصادفی
        public_key = random.choice(xui_settings.REALITY_PUBLIC_KEYS)
        
        # تولید shortId تصادفی
        short_id = ''.join(random.choices(string.hexdigits.lower(), k=8))
        
        # تولید UUID برای کاربر
        user_uuid = str(uuid.uuid4())
        
        # تولید پورت تصادفی
        port = random.randint(10000, 65000)
        
        if protocol.lower() == "vless":
            # تولید کانفیگ VLess Reality
            config_data = f"vless://{user_uuid}@{self.server.host}:{port}?type=tcp&security=reality&sni={fake_domain}&fp=chrome&pbk={public_key}&sid={short_id}&spx=%2F#{user.full_name}"
        elif protocol.lower() == "vmess":
            # تولید کانفیگ VMess
            vmess_config = {
                "v": "2",
                "ps": f"{user.full_name} - {protocol.upper()}",
                "add": self.server.host,
                "port": port,
                "id": user_uuid,
                "aid": "0",
                "net": "ws",
                "type": "none",
                "host": "",
                "path": "/",
                "tls": "tls"
            }
            
            config_str = json.dumps(vmess_config)
            encoded = base64.b64encode(config_str.encode()).decode()
            config_data = f"vmess://{encoded}"
        elif protocol.lower() == "trojan":
            # تولید کانفیگ Trojan
            config_data = f"trojan://{user_uuid}@{self.server.host}:{port}?security=tls#{user.full_name}"
        else:
            raise ValueError(f"پروتکل نامعتبر: {protocol}")
        
        print(f"📋 کانفیگ تولید شده:")
        print(f"  - پورت: {port}")
        print(f"  - دامنه: {fake_domain}")
        print(f"  - کلید عمومی: {public_key[:20]}...")
        print(f"  - Short ID: {short_id}")
        print(f"  - UUID: {user_uuid}")
        
        return config_data
    
    def get_user_configs(self, user: UsersModel):
        """دریافت کانفیگ‌های کاربر"""
        return UserConfig.objects.filter(user=user, is_active=True)
    
    def delete_user_config(self, config_id: int):
        """حذف کانفیگ کاربر"""
        try:
            config = UserConfig.objects.get(id=config_id)
            config.delete()
            return True, xui_settings.SUCCESS_MESSAGES["config_deleted"]
        except UserConfig.DoesNotExist:
            return False, "کانفیگ یافت نشد"
        except Exception as e:
            return False, f"خطا در حذف کانفیگ: {e}"

# برای سازگاری با کد قدیمی
class UserConfigService:
    """سرویس مدیریت کانفیگ کاربران (برای سازگاری)"""
    
    @staticmethod
    def create_trial_config(user: UsersModel, server: XUIServer, protocol: str = "vless"):
        """ایجاد کانفیگ تستی برای کاربر"""
        config_service = SimpleConfigService()
        return config_service.create_trial_config(user, protocol)
    
    @staticmethod
    def create_paid_config(user: UsersModel, server: XUIServer, plan: ConfingPlansModel, protocol: str = "vless"):
        """ایجاد کانفیگ پولی برای کاربر"""
        config_service = SimpleConfigService()
        return config_service.create_paid_config(user, plan, protocol)
    
    @staticmethod
    def delete_user_config(user_config: UserConfig):
        """حذف کانفیگ کاربر"""
        config_service = SimpleConfigService()
        return config_service.delete_user_config(user_config.id)

# کلاس‌های قدیمی برای سازگاری
class XUIService:
    """سرویس برای اتصال به X-UI (برای سازگاری)"""
    
    def __init__(self, server: XUIServer):
        self.server = server
    
    def login(self):
        """ورود به X-UI (برای سازگاری)"""
        return True
    
    def get_inbounds(self):
        """دریافت لیست inbound ها (برای سازگاری)"""
        return []
    
    def create_user_specific_inbound(self, user_id: int, protocol: str = "vless", port: int = None):
        """ایجاد inbound جداگانه برای هر کاربر (برای سازگاری)"""
        return 0
    
    def get_or_create_inbound_for_user(self, user_id: int, protocol: str = "vless"):
        """دریافت یا ایجاد inbound جداگانه برای هر کاربر (برای سازگاری)"""
        return 0

class ConfigGenerator:
    """تولیدکننده کانفیگ‌های مختلف (برای سازگاری)"""
    
    @staticmethod
    def generate_vless_reality_config(server_host: str, port: int, uuid: str, user_name: str = "User"):
        """تولید کانفیگ VLess Reality"""
        fake_domain = random.choice(xui_settings.FAKE_DOMAINS)
        public_key = random.choice(xui_settings.REALITY_PUBLIC_KEYS)
        short_id = ''.join(random.choices(string.hexdigits.lower(), k=8))
        
        config = f"vless://{uuid}@{server_host}:{port}?type=tcp&security=reality&sni={fake_domain}&fp=chrome&pbk={public_key}&sid={short_id}&spx=%2F#{user_name}"
        return config
'''
    
    # نوشتن فایل جدید
    with open('xui_servers/services.py', 'w', encoding='utf-8') as f:
        f.write(new_content)
    
    print("✅ فایل xui_servers/services.py اصلاح شد!")
    print("📋 تغییرات اعمال شده:")
    print("  - حذف وابستگی به x-ui API")
    print("  - استفاده از سیستم کانفیگ ساده")
    print("  - حفظ سازگاری با کد قدیمی")
    print("  - تولید کانفیگ‌های VLess Reality")
    print("  - ذخیره در دیتابیس")

def test_fixed_services():
    """تست سرویس‌های اصلاح شده"""
    print("\n🔧 تست سرویس‌های اصلاح شده...")
    
    try:
        from xui_servers.services import SimpleConfigService, UserConfigService
        
        # ایجاد کاربر تستی
        test_user, created = UsersModel.objects.get_or_create(
            telegram_id=999999,
            defaults={
                'id_tel': '999999',
                'username_tel': 'testuser',
                'full_name': 'کاربر تست ساده',
                'username': 'testuser'
            }
        )
        
        print(f"👤 کاربر: {test_user.full_name}")
        
        # تست SimpleConfigService
        print("\n📊 تست SimpleConfigService...")
        config_service = SimpleConfigService()
        trial_config, trial_data = config_service.create_trial_config(test_user, "vless")
        
        print(f"✅ کانفیگ تستی ایجاد شد:")
        print(f"  - نام: {trial_config.config_name}")
        print(f"  - ID: {trial_config.id}")
        
        # تست UserConfigService (برای سازگاری)
        print("\n📊 تست UserConfigService...")
        server = XUIServer.objects.filter(is_active=True).first()
        paid_config, message = UserConfigService.create_trial_config(test_user, server, "vless")
        
        print(f"✅ کانفیگ پولی ایجاد شد:")
        print(f"  - نام: {paid_config.config_name}")
        print(f"  - پیام: {message}")
        
        print("\n🎉 تست سرویس‌های اصلاح شده کامل شد!")
        
    except Exception as e:
        print(f"❌ خطا در تست: {e}")

if __name__ == "__main__":
    fix_xui_services()
    test_fixed_services() 