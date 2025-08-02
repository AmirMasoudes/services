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

class SimpleConfigSystem:
    """سیستم کانفیگ ساده بدون نیاز به x-ui API"""
    
    def __init__(self):
        self.server = XUIServer.objects.filter(is_active=True).first()
        if not self.server:
            raise Exception("سرور X-UI فعالی یافت نشد")
    
    def create_trial_config(self, user: UsersModel, protocol: str = "vless"):
        """ایجاد کانفیگ تستی برای کاربر"""
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
        
        return user_config, config_data
    
    def create_paid_config(self, user: UsersModel, plan, protocol: str = "vless"):
        """ایجاد کانفیگ پولی برای کاربر"""
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
        
        return user_config, config_data
    
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
            import base64
            import json
            
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
            return True, "کانفیگ با موفقیت حذف شد"
        except UserConfig.DoesNotExist:
            return False, "کانفیگ یافت نشد"
        except Exception as e:
            return False, f"خطا در حذف کانفیگ: {e}"

def test_simple_config_system():
    """تست سیستم کانفیگ ساده"""
    print("🔧 تست سیستم کانفیگ ساده...")
    
    try:
        # ایجاد سیستم
        config_system = SimpleConfigSystem()
        print(f"✅ سیستم کانفیگ ایجاد شد")
        print(f"🖥️ سرور: {config_system.server.name}")
        
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
        
        # ایجاد کانفیگ تستی
        print("\n📊 ایجاد کانفیگ تستی...")
        trial_config, trial_data = config_system.create_trial_config(test_user, "vless")
        
        print(f"\n📋 کانفیگ تستی:")
        print(trial_data)
        
        # ایجاد کانفیگ پولی (بدون پلن)
        print("\n📊 ایجاد کانفیگ پولی...")
        paid_config, paid_data = config_system.create_paid_config(test_user, None, "vless")
        
        print(f"\n📋 کانفیگ پولی:")
        print(paid_data)
        
        # دریافت کانفیگ‌های کاربر
        print("\n📊 کانفیگ‌های کاربر:")
        user_configs = config_system.get_user_configs(test_user)
        for config in user_configs:
            print(f"  - {config.config_name} (ID: {config.id})")
        
        print("\n🎉 تست سیستم کانفیگ ساده کامل شد!")
        
    except Exception as e:
        print(f"❌ خطا در تست: {e}")

if __name__ == "__main__":
    test_simple_config_system() 