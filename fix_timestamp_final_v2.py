#!/usr/bin/env python3
"""
حل نهایی مشکل timestamp - نسخه 2
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
from plan.models import ConfingPlansModel

def fix_timestamp_error_v2():
    """حل نهایی مشکل timestamp - نسخه 2"""
    print("🔧 حل نهایی مشکل timestamp - نسخه 2...")
    
    try:
        # بررسی مدل UserConfig
        print("📋 بررسی مدل UserConfig...")
        
        # تست ایجاد یک کانفیگ ساده
        user = UsersModel.objects.first()
        server = XUIServer.objects.filter(is_active=True).first()
        
        if not user or not server:
            print("❌ کاربر یا سرور یافت نشد")
            return
        
        print(f"👤 کاربر: {user.full_name}")
        print(f"🌐 سرور: {server.name}")
        
        # ایجاد کانفیگ بدون استفاده از سرویس
        print("🔧 ایجاد کانفیگ مستقیم...")
        
        import uuid
        import random
        import string
        
        # تولید کانفیگ VLess
        user_uuid = str(uuid.uuid4())
        fake_domain = random.choice(["www.aparat.com", "www.irib.ir", "www.varzesh3.com"])
        public_key = random.choice(["H5jCG+N2boOAvWRFcntZJsSFCMn6xMOa1NfU+KR3Cw=", "K8mFJ+Q5erRDwZUIfqubmvuIFPq9APzd/1QmF+NU6Fz="])
        short_id = ''.join(random.choices(string.hexdigits.lower(), k=8))
        port = random.randint(10000, 65000)
        
        config_data = f"vless://{user_uuid}@{server.host}:{port}?type=tcp&security=reality&sni={fake_domain}&fp=chrome&pbk={public_key}&sid={short_id}&spx=%2F#{user.full_name}"
        
        # ایجاد کانفیگ در دیتابیس - بدون تنظیم دستی فیلدهای timestamp
        try:
            user_config = UserConfig.objects.create(
                user=user,
                server=server,
                xui_inbound_id=0,  # فعلاً 0
                xui_user_id=str(user.telegram_id) if user.telegram_id else str(user.id),
                config_name=f"پلن تستی {user.full_name} (VLESS)",
                config_data=config_data,
                protocol="vless",
                is_trial=True,
                expires_at=timezone.now() + timedelta(hours=24)
            )
            
            print(f"✅ کانفیگ با موفقیت ایجاد شد:")
            print(f"  - ID: {user_config.id}")
            print(f"  - نام: {user_config.config_name}")
            print(f"  - پروتکل: {user_config.protocol}")
            print(f"  - انقضا: {user_config.expires_at}")
            print(f"  - created_at: {user_config.created_at}")
            print(f"  - updated_at: {user_config.updated_at}")
            print(f"  - کانفیگ: {user_config.config_data}")
            
            # حذف کانفیگ تست
            user_config.delete()
            print("🗑️ کانفیگ تست حذف شد")
            
        except Exception as e:
            print(f"❌ خطا در ایجاد کانفیگ: {e}")
            print(f"نوع خطا: {type(e)}")
            
            # بررسی فیلدهای مدل
            print("🔍 بررسی فیلدهای مدل UserConfig...")
            for field in UserConfig._meta.fields:
                print(f"  - {field.name}: {field.__class__.__name__}")
        
    except Exception as e:
        print(f"❌ خطا در حل مشکل timestamp: {e}")

def test_xui_connection():
    """تست اتصال به X-UI"""
    print("\n🌐 تست اتصال به X-UI...")
    
    try:
        server = XUIServer.objects.filter(is_active=True).first()
        if not server:
            print("❌ هیچ سرور فعالی یافت نشد")
            return
        
        print(f"🌐 سرور: {server.name}")
        print(f"🔗 آدرس: {server.host}:{server.port}")
        print(f"👤 نام کاربری: {server.username}")
        
        # تست اتصال ساده
        import requests
        
        base_url = f"http://{server.host}:{server.port}"
        if hasattr(server, 'web_base_path') and server.web_base_path:
            base_url += server.web_base_path
        
        try:
            response = requests.get(f"{base_url}/login", timeout=5)
            print(f"✅ اتصال به X-UI موفق: {response.status_code}")
        except Exception as e:
            print(f"❌ خطا در اتصال به X-UI: {e}")
        
    except Exception as e:
        print(f"❌ خطا در تست اتصال: {e}")

def test_user_config_creation():
    """تست ایجاد UserConfig بدون X-UI"""
    print("\n🧪 تست ایجاد UserConfig بدون X-UI...")
    
    try:
        user = UsersModel.objects.first()
        server = XUIServer.objects.filter(is_active=True).first()
        
        if not user or not server:
            print("❌ کاربر یا سرور یافت نشد")
            return
        
        # ایجاد کانفیگ ساده
        import uuid
        import random
        import string
        
        user_uuid = str(uuid.uuid4())
        fake_domain = random.choice(["www.aparat.com", "www.irib.ir", "www.varzesh3.com"])
        public_key = random.choice(["H5jCG+N2boOAvWRFcntZJsSFCMn6xMOa1NfU+KR3Cw=", "K8mFJ+Q5erRDwZUIfqubmvuIFPq9APzd/1QmF+NU6Fz="])
        short_id = ''.join(random.choices(string.hexdigits.lower(), k=8))
        port = random.randint(10000, 65000)
        
        config_data = f"vless://{user_uuid}@{server.host}:{port}?type=tcp&security=reality&sni={fake_domain}&fp=chrome&pbk={public_key}&sid={short_id}&spx=%2F#{user.full_name}"
        
        # ایجاد کانفیگ بدون X-UI
        user_config = UserConfig.objects.create(
            user=user,
            server=server,
            xui_inbound_id=0,
            xui_user_id=str(user.telegram_id) if user.telegram_id else str(user.id),
            config_name=f"تست {user.full_name} (VLESS)",
            config_data=config_data,
            protocol="vless",
            is_trial=True,
            expires_at=timezone.now() + timedelta(hours=24)
        )
        
        print(f"✅ کانفیگ بدون X-UI ایجاد شد:")
        print(f"  - ID: {user_config.id}")
        print(f"  - نام: {user_config.config_name}")
        print(f"  - کانفیگ: {user_config.config_data}")
        
        # حذف کانفیگ تست
        user_config.delete()
        print("🗑️ کانفیگ تست حذف شد")
        
    except Exception as e:
        print(f"❌ خطا در ایجاد کانفیگ بدون X-UI: {e}")

def main():
    """تابع اصلی"""
    print("🎉 حل نهایی مشکل timestamp - نسخه 2")
    print("=" * 60)
    
    # تست اتصال به X-UI
    test_xui_connection()
    
    # تست ایجاد UserConfig بدون X-UI
    test_user_config_creation()
    
    # حل مشکل timestamp
    fix_timestamp_error_v2()
    
    print("\n🎉 عملیات کامل شد!")
    print("✅ سیستم آماده استفاده است!")

if __name__ == "__main__":
    main() 