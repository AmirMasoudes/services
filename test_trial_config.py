#!/usr/bin/env python3
"""
تست ایجاد کانفیگ تستی
"""

import os
import sys
import django

# تنظیم Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from accounts.models import UsersModel
from xui_servers.models import XUIServer
from xui_servers.services import UserConfigService

def test_trial_config():
    """تست ایجاد کانفیگ تستی"""
    print("🧪 تست ایجاد کانفیگ تستی...")
    
    try:
        # دریافت کاربر
        user = UsersModel.objects.first()
        if not user:
            print("❌ هیچ کاربری یافت نشد")
            return
        
        print(f"👤 کاربر: {user.full_name}")
        print(f"📱 Telegram ID: {user.telegram_id}")
        print(f"🎁 می‌تواند تست بگیرد: {user.can_get_trial()}")
        
        # دریافت سرور
        server = XUIServer.objects.filter(is_active=True).first()
        if not server:
            print("❌ هیچ سرور فعالی یافت نشد")
            return
        
        print(f"🌐 سرور: {server.name}")
        print(f"🔗 آدرس: {server.host}:{server.port}")
        
        # تست ایجاد کانفیگ
        print("\n🔧 ایجاد کانفیگ تستی...")
        user_config, message = UserConfigService.create_trial_config(user, server, "vless")
        
        if user_config:
            print("✅ کانفیگ با موفقیت ایجاد شد!")
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
        import traceback
        traceback.print_exc()

def test_user_trial_status():
    """تست وضعیت تست کاربر"""
    print("\n👤 بررسی وضعیت تست کاربران...")
    
    try:
        users = UsersModel.objects.all()
        print(f"📊 تعداد کاربران: {users.count()}")
        
        for user in users:
            print(f"👤 {user.full_name}:")
            print(f"  - Telegram ID: {user.telegram_id}")
            print(f"  - تست استفاده شده: {user.has_used_trial}")
            print(f"  - می‌تواند تست بگیرد: {user.can_get_trial()}")
            print("---")
        
    except Exception as e:
        print(f"❌ خطا در بررسی کاربران: {e}")

def test_servers():
    """تست سرورها"""
    print("\n🌐 بررسی سرورها...")
    
    try:
        servers = XUIServer.objects.all()
        print(f"📊 تعداد سرورها: {servers.count()}")
        
        for server in servers:
            print(f"🌐 {server.name}:")
            print(f"  - آدرس: {server.host}:{server.port}")
            print(f"  - فعال: {server.is_active}")
            print(f"  - نام کاربری: {server.username}")
            print("---")
        
    except Exception as e:
        print(f"❌ خطا در بررسی سرورها: {e}")

def main():
    """تابع اصلی"""
    print("🎉 تست کامل سیستم کانفیگ تستی")
    print("=" * 60)
    
    # تست سرورها
    test_servers()
    
    # تست وضعیت کاربران
    test_user_trial_status()
    
    # تست ایجاد کانفیگ
    test_trial_config()
    
    print("\n🎉 تست کامل شد!")

if __name__ == "__main__":
    main() 