#!/usr/bin/env python3
"""
تست سیستم ادمین
"""

import os
import sys
import django
from datetime import datetime

# تنظیم Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from xui_servers.models import XUIServer, XUIInbound, XUIClient, UserConfig
from accounts.models import UsersModel
from django.conf import settings

def test_admin_system():
    """تست سیستم ادمین"""
    print("🧪 تست سیستم ادمین...")
    
    try:
        # تست 1: بررسی تنظیمات
        print("\n1️⃣ بررسی تنظیمات:")
        print(f"   ADMIN_BOT_TOKEN: {'✅ تنظیم شده' if hasattr(settings, 'ADMIN_BOT_TOKEN') and settings.ADMIN_BOT_TOKEN != 'YOUR_ADMIN_BOT_TOKEN' else '❌ تنظیم نشده'}")
        print(f"   ADMIN_PASSWORD: {getattr(settings, 'ADMIN_PASSWORD', 'admin123')}")
        print(f"   ADMIN_USER_IDS: {getattr(settings, 'ADMIN_USER_IDS', [])}")
        
        # تست 2: بررسی مدل‌ها
        print("\n2️⃣ بررسی مدل‌ها:")
        
        # تست XUIServer
        servers = XUIServer.objects.filter(is_active=True)
        print(f"   سرورهای فعال: {servers.count()}")
        for server in servers:
            print(f"     - {server.name} ({server.host}:{server.port})")
        
        # تست XUIInbound
        inbounds = XUIInbound.objects.filter(is_active=True)
        print(f"   Inbound های فعال: {inbounds.count()}")
        for inbound in inbounds:
            print(f"     - {inbound.remark} (پورت: {inbound.port}, پروتکل: {inbound.protocol})")
        
        # تست XUIClient
        clients = XUIClient.objects.filter(is_active=True)
        print(f"   کلاینت‌های فعال: {clients.count()}")
        for client in clients:
            print(f"     - {client.email} (کاربر: {client.user.full_name})")
        
        # تست UserConfig
        configs = UserConfig.objects.filter(is_active=True)
        print(f"   کانفیگ‌های فعال: {configs.count()}")
        for config in configs:
            print(f"     - {config.config_name} (کاربر: {config.user.full_name})")
        
        # تست 3: بررسی کاربران
        print("\n3️⃣ بررسی کاربران:")
        users = UsersModel.objects.all()
        print(f"   تعداد کاربران: {users.count()}")
        for user in users[:5]:  # فقط 5 کاربر اول
            print(f"     - {user.full_name} (@{user.username_tel})")
        
        # تست 4: بررسی سرویس‌ها
        print("\n4️⃣ بررسی سرویس‌ها:")
        try:
            from xui_servers.services import XUIService
            print("   ✅ XUIService قابل import است")
        except Exception as e:
            print(f"   ❌ خطا در import XUIService: {e}")
        
        try:
            from xui_servers.enhanced_api_models import XUIEnhancedService
            print("   ✅ XUIEnhancedService قابل import است")
        except Exception as e:
            print(f"   ❌ خطا در import XUIEnhancedService: {e}")
        
        # تست 5: بررسی ربات ادمین
        print("\n5️⃣ بررسی ربات ادمین:")
        try:
            from bot.admin_bot import AdminBot
            print("   ✅ AdminBot قابل import است")
            
            # بررسی تنظیمات ربات
            if hasattr(settings, 'ADMIN_BOT_TOKEN') and settings.ADMIN_BOT_TOKEN != 'YOUR_ADMIN_BOT_TOKEN':
                print("   ✅ TOKEN ربات تنظیم شده")
            else:
                print("   ❌ TOKEN ربات تنظیم نشده")
            
            if hasattr(settings, 'ADMIN_USER_IDS') and settings.ADMIN_USER_IDS:
                print(f"   ✅ {len(settings.ADMIN_USER_IDS)} ادمین تنظیم شده")
            else:
                print("   ❌ هیچ ادمینی تنظیم نشده")
                
        except Exception as e:
            print(f"   ❌ خطا در import AdminBot: {e}")
        
        print("\n✅ تست سیستم ادمین کامل شد!")
        return True
        
    except Exception as e:
        print(f"❌ خطا در تست سیستم ادمین: {e}")
        return False

def test_admin_panel():
    """تست پنل ادمین"""
    print("\n🖥️ تست پنل ادمین Django...")
    
    try:
        # تست import admin
        from xui_servers.admin import XUIServerAdmin, XUIInboundAdmin, XUIClientAdmin, UserConfigAdmin
        print("   ✅ کلاس‌های ادمین قابل import هستند")
        
        # تست مدل‌ها
        from xui_servers.models import XUIServer, XUIInbound, XUIClient, UserConfig
        print("   ✅ مدل‌ها قابل import هستند")
        
        print("✅ پنل ادمین آماده است!")
        return True
        
    except Exception as e:
        print(f"❌ خطا در تست پنل ادمین: {e}")
        return False

def main():
    """تابع اصلی"""
    print("🚀 شروع تست سیستم ادمین X-UI...")
    
    # تست سیستم ادمین
    admin_test_ok = test_admin_system()
    
    # تست پنل ادمین
    panel_test_ok = test_admin_panel()
    
    # نتیجه کلی
    if admin_test_ok and panel_test_ok:
        print("\n🎉 تمام تست‌ها موفق بودند!")
        print("✅ سیستم ادمین آماده استفاده است!")
        
        print("\n📋 مراحل بعدی:")
        print("1. تنظیم TOKEN ربات در config/settings.py")
        print("2. تنظیم ID تلگرام در config/settings.py")
        print("3. اجرای ربات: python start_admin_bot.py")
        print("4. راه‌اندازی سرویس: sudo systemctl start admin-bot")
        
    else:
        print("\n❌ برخی تست‌ها ناموفق بودند!")
        print("🔧 نیاز به بررسی بیشتر!")

if __name__ == "__main__":
    main() 