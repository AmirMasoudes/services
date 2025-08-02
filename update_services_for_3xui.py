#!/usr/bin/env python3
import os
import sys
import django

# تنظیم Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

def update_services_for_3xui():
    """به‌روزرسانی services.py برای 3X-UI"""
    print("🔧 به‌روزرسانی services.py برای 3X-UI...")
    
    # محتوای جدید برای services.py با 3X-UI API
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

class XUIService:
    """سرویس برای اتصال به 3X-UI API"""
    
    def __init__(self, server: XUIServer):
        self.server = server
        self.base_url = f"http://{server.host}:{server.port}/BerLdbHxpmtoT3xuzu"
        self.session = requests.Session()
        self.session.headers.update({
            'Content-Type': 'application/json',
            'User-Agent': 'Django-3XUI-Bot/1.0'
        })
    
    def login(self):
        """ورود به 3X-UI"""
        try:
            login_data = {
                "username": self.server.username,
                "password": self.server.password
            }
            
            response = self.session.post(f"{self.base_url}/api/login", json=login_data)
            
            if response.status_code == 200:
                return True
            return False
            
        except Exception as e:
            print(f"خطا در ورود به 3X-UI: {e}")
            return False
    
    def get_inbounds(self):
        """دریافت لیست inbound ها"""
        try:
            response = self.session.get(f"{self.base_url}/api/v1/inbounds")
            if response.status_code == 200:
                data = response.json()
                return data.get('obj', [])
            return []
            
        except Exception as e:
            print(f"خطا در دریافت inbound ها: {e}")
            return []
    
    def create_inbound(self, inbound_data: dict):
        """ایجاد inbound جدید"""
        try:
            response = self.session.post(f"{self.base_url}/api/v1/inbounds", json=inbound_data)
            if response.status_code == 200:
                data = response.json()
                return data.get('obj', {}).get('id')
            return None
            
        except Exception as e:
            print(f"خطا در ایجاد inbound: {e}")
            return None
    
    def add_client(self, inbound_id: int, client_data: dict):
        """اضافه کردن کاربر به inbound"""
        try:
            response = self.session.post(
                f"{self.base_url}/api/v1/inbounds/{inbound_id}/clients", 
                json=client_data
            )
            if response.status_code == 200:
                return True
            return False
            
        except Exception as e:
            print(f"خطا در اضافه کردن کاربر: {e}")
            return False
    
    def delete_client(self, inbound_id: int, client_email: str):
        """حذف کاربر از inbound"""
        try:
            response = self.session.delete(
                f"{self.base_url}/api/v1/inbounds/{inbound_id}/clients/{client_email}"
            )
            if response.status_code == 200:
                return True
            return False
            
        except Exception as e:
            print(f"خطا در حذف کاربر: {e}")
            return False

class UserConfigService:
    """سرویس کانفیگ کاربر با 3X-UI"""
    
    @staticmethod
    def create_trial_config(user: UsersModel, server: XUIServer, protocol: str = "vless"):
        """ایجاد کانفیگ تستی"""
        try:
            xui_service = XUIService(server)
            if not xui_service.login():
                return None, "خطا در ورود به 3X-UI"
            
            # تولید پورت تصادفی
            port = random.randint(10000, 65000)
            
            # تولید UUID
            user_uuid = str(uuid.uuid4())
            
            # انتخاب دامنه و کلید تصادفی
            fake_domain = random.choice(xui_settings.FAKE_DOMAINS)
            public_key = random.choice(xui_settings.REALITY_PUBLIC_KEYS)
            short_id = ''.join(random.choices(string.hexdigits.lower(), k=8))
            
            # ایجاد inbound
            inbound_data = {
                "protocol": protocol,
                "port": port,
                "stream": {
                    "network": "tcp",
                    "security": "reality",
                    "realitySettings": {
                        "serverName": fake_domain,
                        "fingerprint": "chrome",
                        "publicKey": public_key,
                        "shortId": short_id,
                        "spiderX": "/"
                    }
                },
                "clients": [
                    {
                        "id": user_uuid,
                        "email": f"trial_{user.telegram_id}@example.com",
                        "totalGB": 1,
                        "expiryTime": int((timezone.now() + timedelta(hours=24)).timestamp() * 1000)
                    }
                ]
            }
            
            inbound_id = xui_service.create_inbound(inbound_data)
            if not inbound_id:
                return None, "خطا در ایجاد inbound"
            
            # تولید کانفیگ
            config_data = f"vless://{user_uuid}@{server.host}:{port}?type=tcp&security=reality&sni={fake_domain}&fp=chrome&pbk={public_key}&sid={short_id}&spx=%2F#{user.full_name}"
            
            # ذخیره در دیتابیس
            config_name = f"پلن تستی {user.full_name} ({protocol.upper()})"
            
            user_config = UserConfig.objects.create(
                user=user,
                server=server,
                xui_inbound_id=inbound_id,
                xui_user_id=str(user.telegram_id),
                config_name=config_name,
                config_data=config_data,
                protocol=protocol,
                is_trial=True,
                created_at=timezone.now(),
                expires_at=timezone.now() + timedelta(hours=24)
            )
            
            return user_config, f"کانفیگ {protocol.upper()} تستی با موفقیت ایجاد شد"
            
        except Exception as e:
            print(f"خطا در ایجاد کانفیگ تستی: {e}")
            return None, f"خطا در ایجاد کانفیگ: {e}"
    
    @staticmethod
    def create_paid_config(user: UsersModel, server: XUIServer, plan: ConfingPlansModel, protocol: str = "vless"):
        """ایجاد کانفیگ پولی"""
        try:
            if not plan:
                return None, "پلن مشخص نشده است"
            
            xui_service = XUIService(server)
            if not xui_service.login():
                return None, "خطا در ورود به 3X-UI"
            
            # تولید پورت تصادفی
            port = random.randint(10000, 65000)
            
            # تولید UUID
            user_uuid = str(uuid.uuid4())
            
            # انتخاب دامنه و کلید تصادفی
            fake_domain = random.choice(xui_settings.FAKE_DOMAINS)
            public_key = random.choice(xui_settings.REALITY_PUBLIC_KEYS)
            short_id = ''.join(random.choices(string.hexdigits.lower(), k=8))
            
            # محاسبه حجم داده
            traffic_gb = plan.traffic_mb / 1024
            
            # ایجاد inbound
            inbound_data = {
                "protocol": protocol,
                "port": port,
                "stream": {
                    "network": "tcp",
                    "security": "reality",
                    "realitySettings": {
                        "serverName": fake_domain,
                        "fingerprint": "chrome",
                        "publicKey": public_key,
                        "shortId": short_id,
                        "spiderX": "/"
                    }
                },
                "clients": [
                    {
                        "id": user_uuid,
                        "email": f"paid_{user.telegram_id}_{plan.id}@example.com",
                        "totalGB": traffic_gb,
                        "expiryTime": int((timezone.now() + timedelta(days=30)).timestamp() * 1000)
                    }
                ]
            }
            
            inbound_id = xui_service.create_inbound(inbound_data)
            if not inbound_id:
                return None, "خطا در ایجاد inbound"
            
            # تولید کانفیگ
            config_data = f"vless://{user_uuid}@{server.host}:{port}?type=tcp&security=reality&sni={fake_domain}&fp=chrome&pbk={public_key}&sid={short_id}&spx=%2F#{user.full_name}"
            
            # ذخیره در دیتابیس
            config_name = f"{plan.name} {user.full_name} ({protocol.upper()})"
            
            user_config = UserConfig.objects.create(
                user=user,
                server=server,
                xui_inbound_id=inbound_id,
                xui_user_id=str(user.telegram_id),
                config_name=config_name,
                config_data=config_data,
                protocol=protocol,
                plan=plan,
                is_trial=False,
                created_at=timezone.now(),
                expires_at=timezone.now() + timedelta(days=30)
            )
            
            return user_config, f"کانفیگ {protocol.upper()} پولی با موفقیت ایجاد شد"
            
        except Exception as e:
            print(f"خطا در ایجاد کانفیگ پولی: {e}")
            return None, f"خطا در ایجاد کانفیگ: {e}"

class SimpleConfigService:
    """سرویس کانفیگ ساده (برای سازگاری)"""
    
    def __init__(self):
        self.server = XUIServer.objects.filter(is_active=True).first()
        if not self.server:
            raise Exception("سرور X-UI فعالی یافت نشد")
    
    def create_trial_config(self, user: UsersModel, protocol: str = "vless"):
        """ایجاد کانفیگ تستی (برای سازگاری)"""
        return UserConfigService.create_trial_config(user, self.server, protocol)
    
    def create_paid_config(self, user: UsersModel, plan: ConfingPlansModel, protocol: str = "vless"):
        """ایجاد کانفیگ پولی (برای سازگاری)"""
        return UserConfigService.create_paid_config(user, self.server, plan, protocol)

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
    
    print("✅ فایل xui_servers/services.py برای 3X-UI به‌روزرسانی شد!")

if __name__ == "__main__":
    update_services_for_3xui() 