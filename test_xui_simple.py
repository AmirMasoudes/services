#!/usr/bin/env python3
"""
تست ساده اتصال XUI
"""

import os
import sys
import django
import requests
import json

# تنظیم Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from xui_servers.models import XUIServer
from xui_servers.services import XUIService

def test_xui_simple():
    """تست ساده اتصال XUI"""
    print("🔍 تست ساده اتصال XUI...")
    
    try:
        # دریافت سرور فعال
        server = XUIServer.objects.filter(is_active=True).first()
        if not server:
            print("❌ هیچ سرور فعالی یافت نشد")
            return False
        
        print(f"🌐 سرور: {server.name}")
        print(f"🔗 آدرس: {server.host}:{server.port}")
        print(f"👤 نام کاربری: {server.username}")
        print(f"🔑 رمز عبور: {server.password}")
        print(f"🌐 مسیر وب: {server.web_base_path}")
        
        # تست اتصال ساده
        base_url = f"http://{server.host}:{server.port}"
        if server.web_base_path:
            base_url += server.web_base_path
        
        print(f"🌐 URL کامل: {base_url}")
        
        # تست اتصال HTTP
        try:
            response = requests.get(f"{base_url}/", timeout=10)
            print(f"✅ اتصال HTTP: {response.status_code}")
            if response.status_code == 200:
                print("✅ سرور قابل دسترسی است")
            else:
                print(f"❌ سرور غیرقابل دسترسی: {response.status_code}")
                return False
        except Exception as e:
            print(f"❌ خطا در اتصال HTTP: {e}")
            return False
        
        # تست XUI Service
        print("\n🔧 تست XUI Service...")
        xui_service = XUIService(server)
        
        # تست لاگین
        print("🔐 تست لاگین...")
        if xui_service.login():
            print("✅ لاگین موفق")
            
            # تست دریافت inbound ها
            print("📋 تست دریافت inbound ها...")
            inbounds = xui_service.get_inbounds()
            
            if inbounds:
                print(f"✅ {len(inbounds)} inbound یافت شد")
                for i, inbound in enumerate(inbounds[:3]):
                    print(f"  {i+1}. {inbound.get('remark', 'بدون نام')} - پورت: {inbound.get('port', 'نامشخص')}")
            else:
                print("⚠️ هیچ inbound یافت نشد")
                
            return True
        else:
            print("❌ لاگین ناموفق")
            return False
            
    except Exception as e:
        print(f"❌ خطا در تست: {e}")
        return False

def test_user_creation():
    """تست ایجاد کاربر"""
    print("\n👤 تست ایجاد کاربر...")
    
    try:
        from accounts.models import UsersModel
        
        # دریافت سرور فعال
        server = XUIServer.objects.filter(is_active=True).first()
        if not server:
            print("❌ هیچ سرور فعالی یافت نشد")
            return False
        
        # ایجاد کاربر تستی
        test_user, created = UsersModel.objects.get_or_create(
            telegram_id=999999999,
            defaults={
                "first_name": "تست",
                "last_name": "کاربر",
                "username": "test_user"
            }
        )
        
        if created:
            print(f"✅ کاربر تستی ایجاد شد: {test_user.get_display_name()}")
        else:
            print(f"📋 کاربر تستی موجود: {test_user.get_display_name()}")
        
        # تست ایجاد کانفیگ
        from xui_servers.services import UserConfigService
        
        print("🔧 تست ایجاد کانفیگ تستی...")
        config, error = UserConfigService.create_trial_config(test_user, server, "vless")
        
        if config:
            print("✅ کانفیگ تستی ایجاد شد")
            print(f"📄 کانفیگ: {config.config_name}")
            return True
        else:
            print(f"❌ خطا در ایجاد کانفیگ: {error}")
            return False
            
    except Exception as e:
        print(f"❌ خطا در تست ایجاد کاربر: {e}")
        return False

def main():
    """تابع اصلی"""
    print("🎉 تست ساده اتصال XUI")
    print("=" * 50)
    
    # تست اتصال
    connection_success = test_xui_simple()
    
    if connection_success:
        print("\n✅ اتصال موفق - تست ایجاد کاربر...")
        user_creation_success = test_user_creation()
        
        if user_creation_success:
            print("\n🎉 تمام تست‌ها موفق بودند!")
        else:
            print("\n❌ خطا در تست ایجاد کاربر")
    else:
        print("\n❌ خطا در اتصال")
    
    print("\n🎉 عملیات کامل شد!")

if __name__ == "__main__":
    main() 