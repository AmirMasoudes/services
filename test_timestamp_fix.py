#!/usr/bin/env python3
"""
تست رفع مشکل timestamp
"""

import os
import sys
import django

# تنظیم Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from xui_servers import settings as xui_settings
from datetime import datetime, timedelta
from django.utils import timezone

def test_email_formats():
    """تست فرمت‌های ایمیل"""
    print("🧪 تست فرمت‌های ایمیل...")
    
    try:
        # تست فرمت ایمیل تستی
        timestamp = timezone.now().strftime(xui_settings.EMAIL_SETTINGS["timestamp_format"])
        trial_email = xui_settings.EMAIL_SETTINGS["trial_format"].format(
            telegram_id="123456789",
            timestamp=timestamp
        )
        print(f"✅ ایمیل تستی: {trial_email}")
        
        # تست فرمت ایمیل پولی
        paid_email = xui_settings.EMAIL_SETTINGS["paid_format"].format(
            telegram_id="123456789",
            plan_id=1,
            timestamp=timestamp
        )
        print(f"✅ ایمیل پولی: {paid_email}")
        
        return True
        
    except Exception as e:
        print(f"❌ خطا در فرمت‌های ایمیل: {e}")
        return False

def test_config_naming():
    """تست نام‌گذاری کانفیگ"""
    print("\n🧪 تست نام‌گذاری کانفیگ...")
    
    try:
        # تست فرمت نام تستی
        expiry_date = timezone.now() + timedelta(hours=24)
        trial_config_name = xui_settings.CONFIG_NAMING["trial_format"].format(
            protocol="VLESS",
            user_name="کاربر تستی",
            expiry=expiry_date.strftime(xui_settings.CONFIG_NAMING["expiry_format"])
        )
        print(f"✅ نام کانفیگ تستی: {trial_config_name}")
        
        # تست فرمت نام پولی
        paid_config_name = xui_settings.CONFIG_NAMING["paid_format"].format(
            plan_name="پلن طلایی",
            user_name="کاربر پولی",
            protocol="VLESS",
            expiry=expiry_date.strftime(xui_settings.CONFIG_NAMING["expiry_format"])
        )
        print(f"✅ نام کانفیگ پولی: {paid_config_name}")
        
        return True
        
    except Exception as e:
        print(f"❌ خطا در نام‌گذاری کانفیگ: {e}")
        return False

def test_success_messages():
    """تست پیام‌های موفقیت"""
    print("\n🧪 تست پیام‌های موفقیت...")
    
    try:
        # تست پیام تستی
        trial_message = xui_settings.SUCCESS_MESSAGES["trial_created"].format(
            protocol="VLESS",
            duration=xui_settings.EXPIRY_SETTINGS["trial_hours"]
        )
        print(f"✅ پیام تستی: {trial_message}")
        
        # تست پیام پولی
        paid_message = xui_settings.SUCCESS_MESSAGES["paid_created"].format(
            protocol="VLESS",
            duration=xui_settings.EXPIRY_SETTINGS["paid_days"],
            traffic=10.5
        )
        print(f"✅ پیام پولی: {paid_message}")
        
        return True
        
    except Exception as e:
        print(f"❌ خطا در پیام‌های موفقیت: {e}")
        return False

def main():
    """تابع اصلی"""
    print("🔧 تست رفع مشکل timestamp...")
    
    # تست فرمت‌های ایمیل
    email_ok = test_email_formats()
    
    # تست نام‌گذاری کانفیگ
    naming_ok = test_config_naming()
    
    # تست پیام‌های موفقیت
    messages_ok = test_success_messages()
    
    # نتیجه کلی
    if email_ok and naming_ok and messages_ok:
        print("\n✅ تمام تست‌ها موفق بودند!")
        print("🎉 مشکل timestamp حل شد!")
    else:
        print("\n❌ برخی تست‌ها ناموفق بودند!")
        print("🔧 نیاز به بررسی بیشتر!")

if __name__ == "__main__":
    main() 