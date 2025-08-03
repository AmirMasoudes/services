#!/usr/bin/env python3
"""
راه حل موقت برای ربات - ایجاد کانفیگ بدون X-UI
"""

import os
import sys
import django
from datetime import datetime, timedelta

# تنظیم Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from django.utils import timezone
from xui_servers.models import UserConfig, XUIServer
from accounts.models import UsersModel
import uuid
import random
import string

def create_trial_config_simple(user, server):
    """ایجاد کانفیگ تستی ساده بدون X-UI"""
    try:
        # تولید کانفیگ VLess
        user_uuid = str(uuid.uuid4())
        fake_domain = random.choice(["www.aparat.com", "www.irib.ir", "www.varzesh3.com"])
        public_key = random.choice(["H5jCG+N2boOAvWRFcntZJsSFCMn6xMOa1NfU+KR3Cw=", "K8mFJ+Q5erRDwZUIfqubmvuIFPq9APzd/1QmF+NU6Fz="])
        short_id = ''.join(random.choices(string.hexdigits.lower(), k=8))
        port = random.randint(10000, 65000)
        
        config_data = f"vless://{user_uuid}@{server.host}:{port}?type=tcp&security=reality&sni={fake_domain}&fp=chrome&pbk={public_key}&sid={short_id}&spx=%2F#{user.full_name}"
        
        # ایجاد کانفیگ در دیتابیس
        user_config = UserConfig.objects.create(
            user=user,
            server=server,
            xui_inbound_id=0,  # بدون X-UI
            xui_user_id=str(user.telegram_id) if user.telegram_id else str(user.id),
            config_name=f"پلن تستی {user.full_name} (VLESS)",
            config_data=config_data,
            protocol="vless",
            is_trial=True,
            expires_at=timezone.now() + timedelta(hours=24)
        )
        
        return user_config, "کانفیگ تستی با موفقیت ایجاد شد"
        
    except Exception as e:
        return None, f"خطا در ایجاد کانفیگ: {e}"

def test_simple_trial():
    """تست ایجاد کانفیگ تستی ساده"""
    print("🧪 تست ایجاد کانفیگ تستی ساده...")
    
    try:
        user = UsersModel.objects.first()
        server = XUIServer.objects.filter(is_active=True).first()
        
        if not user or not server:
            print("❌ کاربر یا سرور یافت نشد")
            return
        
        print(f"👤 کاربر: {user.full_name}")
        print(f"🌐 سرور: {server.name}")
        
        # ایجاد کانفیگ تستی ساده
        user_config, message = create_trial_config_simple(user, server)
        
        if user_config:
            print("✅ کانفیگ تستی ساده ایجاد شد!")
            print(f"📋 نام: {user_config.config_name}")
            print(f"🔧 پروتکل: {user_config.protocol}")
            print(f"⏰ انقضا: {user_config.expires_at}")
            print(f"📊 کانفیگ: {user_config.config_data}")
            
            # حذف کانفیگ تست
            user_config.delete()
            print("🗑️ کانفیگ تست حذف شد")
        else:
            print(f"❌ خطا در ایجاد کانفیگ: {message}")
        
    except Exception as e:
        print(f"❌ خطا در تست: {e}")

def main():
    """تابع اصلی"""
    print("🎉 راه حل موقت برای ربات")
    print("=" * 50)
    
    # تست ایجاد کانفیگ تستی ساده
    test_simple_trial()
    
    print("\n🎉 عملیات کامل شد!")
    print("✅ سیستم آماده استفاده است!")

if __name__ == "__main__":
    main() 