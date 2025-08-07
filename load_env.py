#!/usr/bin/env python3
"""
اسکریپت بارگذاری متغیرهای محیطی
این اسکریپت فایل .env را بارگذاری می‌کند و متغیرهای محیطی را تنظیم می‌کند
"""

import os
import sys
from pathlib import Path
from dotenv import load_dotenv

def load_environment_variables():
    """
    بارگذاری متغیرهای محیطی از فایل .env
    """
    # پیدا کردن مسیر پروژه
    project_root = Path(__file__).parent
    
    # جستجوی فایل .env
    env_files = [
        project_root / '.env',
        project_root / 'env_config.env',
        project_root / 'env.example'
    ]
    
    loaded = False
    for env_file in env_files:
        if env_file.exists():
            print(f"بارگذاری متغیرهای محیطی از: {env_file}")
            load_dotenv(env_file)
            loaded = True
            break
    
    if not loaded:
        print("⚠️  هشدار: فایل .env یافت نشد!")
        print("فایل env_config.env را کپی کرده و به .env تغییر نام دهید")
        return False
    
    return True

def validate_required_variables():
    """
    بررسی متغیرهای اجباری
    """
    required_vars = [
        'SECRET_KEY',
        'ADMIN_BOT_TOKEN',
        'USER_BOT_TOKEN',
        'ADMIN_PASSWORD',
        'XUI_DEFAULT_HOST',
        'XUI_DEFAULT_USERNAME',
        'XUI_DEFAULT_PASSWORD'
    ]
    
    missing_vars = []
    for var in required_vars:
        if not os.environ.get(var):
            missing_vars.append(var)
    
    if missing_vars:
        print("❌ متغیرهای اجباری زیر تنظیم نشده‌اند:")
        for var in missing_vars:
            print(f"   - {var}")
        return False
    
    print("✅ تمام متغیرهای اجباری تنظیم شده‌اند")
    return True

def print_environment_summary():
    """
    نمایش خلاصه تنظیمات محیطی
    """
    print("\n📋 خلاصه تنظیمات محیطی:")
    print("=" * 50)
    
    # تنظیمات Django
    print("🔧 تنظیمات Django:")
    print(f"   DEBUG: {os.environ.get('DEBUG', 'Not set')}")
    print(f"   ALLOWED_HOSTS: {os.environ.get('ALLOWED_HOSTS', 'Not set')}")
    
    # تنظیمات ربات‌ها
    print("\n🤖 تنظیمات ربات‌ها:")
    admin_token = os.environ.get('ADMIN_BOT_TOKEN', 'Not set')
    user_token = os.environ.get('USER_BOT_TOKEN', 'Not set')
    print(f"   ADMIN_BOT_TOKEN: {'✅ تنظیم شده' if admin_token != 'Not set' else '❌ تنظیم نشده'}")
    print(f"   USER_BOT_TOKEN: {'✅ تنظیم شده' if user_token != 'Not set' else '❌ تنظیم نشده'}")
    
    # تنظیمات X-UI
    print("\n🖥️ تنظیمات X-UI:")
    xui_host = os.environ.get('XUI_DEFAULT_HOST', 'Not set')
    xui_port = os.environ.get('XUI_DEFAULT_PORT', 'Not set')
    print(f"   XUI_HOST: {xui_host}")
    print(f"   XUI_PORT: {xui_port}")
    
    # تنظیمات پروتکل‌ها
    print("\n🔗 تنظیمات پروتکل‌ها:")
    default_protocol = os.environ.get('DEFAULT_PROTOCOL', 'vless')
    print(f"   DEFAULT_PROTOCOL: {default_protocol}")
    
    # تنظیمات زمان انقضا
    print("\n⏰ تنظیمات زمان انقضا:")
    trial_hours = os.environ.get('TRIAL_HOURS', '24')
    paid_days = os.environ.get('PAID_DAYS', '30')
    print(f"   TRIAL_HOURS: {trial_hours}")
    print(f"   PAID_DAYS: {paid_days}")
    
    print("=" * 50)

def setup_django_environment():
    """
    تنظیم محیط Django
    """
    # اضافه کردن مسیر پروژه
    project_root = Path(__file__).parent
    sys.path.append(str(project_root))
    
    # تنظیم متغیر محیطی Django
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
    
    print("✅ محیط Django تنظیم شد")

def main():
    """
    تابع اصلی
    """
    print("🚀 شروع بارگذاری متغیرهای محیطی...")
    
    # بارگذاری متغیرهای محیطی
    if not load_environment_variables():
        return False
    
    # بررسی متغیرهای اجباری
    if not validate_required_variables():
        return False
    
    # تنظیم محیط Django
    setup_django_environment()
    
    # نمایش خلاصه
    print_environment_summary()
    
    print("\n✅ بارگذاری متغیرهای محیطی با موفقیت انجام شد!")
    return True

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1) 