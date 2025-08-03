#!/usr/bin/env python3
"""
ریست کردن وضعیت تست کاربر
"""

import os
import sys
import django

# تنظیم Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from accounts.models import UsersModel

def reset_trial_status():
    """ریست کردن وضعیت تست کاربر"""
    print("🔄 ریست کردن وضعیت تست کاربر...")
    
    try:
        # دریافت کاربر
        user = UsersModel.objects.first()
        if not user:
            print("❌ هیچ کاربری یافت نشد")
            return
        
        print(f"👤 کاربر: {user.full_name}")
        print(f"📱 Telegram ID: {user.telegram_id}")
        print(f"🎁 وضعیت فعلی تست: {user.has_used_trial}")
        
        # ریست کردن وضعیت تست
        user.has_used_trial = False
        user.save()
        
        print(f"✅ وضعیت تست ریست شد!")
        print(f"🎁 وضعیت جدید تست: {user.has_used_trial}")
        print(f"✅ می‌تواند تست بگیرد: {user.can_get_trial()}")
        
    except Exception as e:
        print(f"❌ خطا در ریست کردن وضعیت: {e}")

def show_all_users():
    """نمایش تمام کاربران"""
    print("\n👥 تمام کاربران:")
    
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
        print(f"❌ خطا در نمایش کاربران: {e}")

def main():
    """تابع اصلی"""
    print("🎉 ریست کردن وضعیت تست")
    print("=" * 50)
    
    # نمایش کاربران
    show_all_users()
    
    # ریست کردن وضعیت تست
    reset_trial_status()
    
    print("\n🎉 عملیات کامل شد!")

if __name__ == "__main__":
    main() 