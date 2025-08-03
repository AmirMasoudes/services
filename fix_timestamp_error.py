#!/usr/bin/env python3
"""
حل مشکل timestamp در ایجاد کانفیگ
"""

import os
import sys
import django
from datetime import datetime, timedelta

# تنظیم Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from django.utils import timezone
from xui_servers.models import UserConfig
from accounts.models import UsersModel
from plan.models import ConfingPlansModel
from xui_servers.services import UserConfigService

def fix_timestamp_error():
    """حل مشکل timestamp در ایجاد کانفیگ"""
    print("🔧 حل مشکل timestamp در ایجاد کانفیگ...")
    
    try:
        # بررسی کانفیگ‌های موجود
        configs = UserConfig.objects.all()
        print(f"📊 تعداد کانفیگ‌های موجود: {configs.count()}")
        
        # بررسی فیلدهای timestamp
        for config in configs:
            print(f"🔍 بررسی کانفیگ {config.id}:")
            print(f"  - created_at: {config.created_at}")
            print(f"  - updated_at: {config.updated_at}")
            print(f"  - expires_at: {config.expires_at}")
            
            # اگر expires_at خالی است، آن را تنظیم کنیم
            if not config.expires_at:
                if config.is_trial:
                    config.expires_at = timezone.now() + timedelta(hours=24)
                else:
                    config.expires_at = timezone.now() + timedelta(days=30)
                config.save()
                print(f"  ✅ expires_at تنظیم شد: {config.expires_at}")
        
        print("✅ مشکل timestamp حل شد!")
        
    except Exception as e:
        print(f"❌ خطا در حل مشکل timestamp: {e}")

def test_config_creation():
    """تست ایجاد کانفیگ"""
    print("\n🧪 تست ایجاد کانفیگ...")
    
    try:
        # دریافت کاربر تست
        user = UsersModel.objects.first()
        if not user:
            print("❌ هیچ کاربری یافت نشد")
            return
        
        print(f"👤 کاربر تست: {user.full_name}")
        
        # دریافت سرور
        from xui_servers.models import XUIServer
        server = XUIServer.objects.filter(is_active=True).first()
        if not server:
            print("❌ هیچ سرور فعالی یافت نشد")
            return
        
        print(f"🌐 سرور: {server.name}")
        
        # تست ایجاد کانفیگ تستی
        print("🔧 تست ایجاد کانفیگ تستی...")
        user_config, message = UserConfigService.create_trial_config(user, server, "vless")
        
        if user_config:
            print(f"✅ کانفیگ تستی ایجاد شد:")
            print(f"  - نام: {user_config.config_name}")
            print(f"  - پروتکل: {user_config.protocol}")
            print(f"  - انقضا: {user_config.expires_at}")
            print(f"  - پیام: {message}")
            
            # حذف کانفیگ تست
            user_config.delete()
            print("🗑️ کانفیگ تست حذف شد")
        else:
            print(f"❌ خطا در ایجاد کانفیگ: {message}")
        
    except Exception as e:
        print(f"❌ خطا در تست ایجاد کانفیگ: {e}")

def check_plans():
    """بررسی پلن‌ها"""
    print("\n📦 بررسی پلن‌ها...")
    
    try:
        plans = ConfingPlansModel.objects.filter(is_deleted=False)
        print(f"📊 تعداد پلن‌های فعال: {plans.count()}")
        
        for plan in plans:
            print(f"✅ {plan.name}")
            print(f"  - قیمت: {plan.price:,} تومان")
            print(f"  - حجم: {plan.in_volume} MB")
            print(f"  - فعال: {plan.is_active}")
            print(f"  - حذف شده: {plan.is_deleted}")
            print("---")
        
    except Exception as e:
        print(f"❌ خطا در بررسی پلن‌ها: {e}")

def main():
    """تابع اصلی"""
    print("🎉 حل مشکل timestamp و بررسی سیستم")
    print("=" * 50)
    
    # حل مشکل timestamp
    fix_timestamp_error()
    
    # بررسی پلن‌ها
    check_plans()
    
    # تست ایجاد کانفیگ
    test_config_creation()
    
    print("\n🎉 عملیات کامل شد!")

if __name__ == "__main__":
    main() 