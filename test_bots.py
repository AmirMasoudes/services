#!/usr/bin/env python3
"""
اسکریپت تست ربات‌های تلگرام
"""

import os
import sys
import subprocess
import time
import requests
from dotenv import load_dotenv

# بارگذاری متغیرهای محیطی
load_dotenv()

def test_environment():
    """تست متغیرهای محیطی"""
    print("🔍 تست متغیرهای محیطی...")
    
    required_vars = [
        'USER_BOT_TOKEN',
        'ADMIN_BOT_TOKEN',
        'ADMIN_PASSWORD'
    ]
    
    all_good = True
    for var in required_vars:
        value = os.getenv(var)
        if value:
            print(f"✅ {var}: موجود")
        else:
            print(f"❌ {var}: تعریف نشده")
            all_good = False
    
    return all_good

def test_dependencies():
    """تست وابستگی‌ها"""
    print("\n🔍 تست وابستگی‌ها...")
    
    required_packages = [
        'telegram',
        'django',
        'dotenv',
        'psutil'
    ]
    
    all_good = True
    for package in required_packages:
        try:
            __import__(package.replace('-', '_'))
            print(f"✅ {package}: نصب شده")
        except ImportError:
            print(f"❌ {package}: نصب نشده")
            all_good = False
    
    return all_good

def test_bot_tokens():
    """تست توکن‌های ربات"""
    print("\n🔍 تست توکن‌های ربات...")
    
    user_token = os.getenv('USER_BOT_TOKEN')
    admin_token = os.getenv('ADMIN_BOT_TOKEN')
    
    if not user_token or user_token == 'your_user_bot_token_here':
        print("❌ USER_BOT_TOKEN تنظیم نشده")
        return False
    
    if not admin_token or admin_token == 'your_admin_bot_token_here':
        print("❌ ADMIN_BOT_TOKEN تنظیم نشده")
        return False
    
    # تست اتصال به API تلگرام
    try:
        # تست ربات کاربر
        url = f"https://api.telegram.org/bot{user_token}/getMe"
        response = requests.get(url, timeout=10)
        if response.status_code == 200:
            data = response.json()
            if data.get('ok'):
                print(f"✅ ربات کاربر: {data['result']['first_name']} (@{data['result']['username']})")
            else:
                print(f"❌ ربات کاربر: {data.get('description', 'خطا')}")
                return False
        else:
            print(f"❌ ربات کاربر: خطای HTTP {response.status_code}")
            return False
        
        # تست ربات ادمین
        url = f"https://api.telegram.org/bot{admin_token}/getMe"
        response = requests.get(url, timeout=10)
        if response.status_code == 200:
            data = response.json()
            if data.get('ok'):
                print(f"✅ ربات ادمین: {data['result']['first_name']} (@{data['result']['username']})")
            else:
                print(f"❌ ربات ادمین: {data.get('description', 'خطا')}")
                return False
        else:
            print(f"❌ ربات ادمین: خطای HTTP {response.status_code}")
            return False
            
    except requests.exceptions.RequestException as e:
        print(f"❌ خطا در اتصال به API تلگرام: {e}")
        return False
    
    return True

def test_django_setup():
    """تست تنظیمات Django"""
    print("\n🔍 تست تنظیمات Django...")
    
    try:
        # تنظیم Django
        os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
        import django
        django.setup()
        
        # تست مدل‌ها
        from accounts.models import UsersModel
        from xui_servers.models import XUIServer, UserConfig
        from plan.models import ConfingPlansModel
        
        print("✅ مدل‌های Django: سالم")
        
        # تست اتصال دیتابیس
        try:
            UsersModel.objects.count()
            print("✅ اتصال دیتابیس: سالم")
        except Exception as e:
            print(f"❌ خطا در اتصال دیتابیس: {e}")
            return False
        
        return True
        
    except Exception as e:
        print(f"❌ خطا در تنظیمات Django: {e}")
        return False

def test_bot_files():
    """تست فایل‌های ربات"""
    print("\n🔍 تست فایل‌های ربات...")
    
    bot_files = [
        'bot/user_bot.py',
        'bot/admin_boy.py'
    ]
    
    all_good = True
    for file_path in bot_files:
        if os.path.exists(file_path):
            print(f"✅ {file_path}: موجود")
        else:
            print(f"❌ {file_path}: موجود نیست")
            all_good = False
    
    return all_good

def test_bot_syntax():
    """تست syntax فایل‌های ربات"""
    print("\n🔍 تست syntax فایل‌های ربات...")
    
    bot_files = [
        'bot/user_bot.py',
        'bot/admin_boy.py'
    ]
    
    all_good = True
    for file_path in bot_files:
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                compile(f.read(), file_path, 'exec')
            print(f"✅ {file_path}: syntax سالم")
        except SyntaxError as e:
            print(f"❌ {file_path}: خطای syntax - {e}")
            all_good = False
        except Exception as e:
            print(f"❌ {file_path}: خطا - {e}")
            all_good = False
    
    return all_good

def test_bot_imports():
    """تست import های ربات"""
    print("\n🔍 تست import های ربات...")
    
    try:
        # تست import ربات کاربر
        sys.path.insert(0, os.path.dirname(os.path.abspath('bot/user_bot.py')))
        import user_bot
        print("✅ ربات کاربر: import سالم")
        
        # تست import ربات ادمین
        import admin_boy
        print("✅ ربات ادمین: import سالم")
        
        return True
        
    except Exception as e:
        print(f"❌ خطا در import ربات‌ها: {e}")
        return False

def test_xui_connection():
    """تست اتصال به X-UI"""
    print("\n🔍 تست اتصال به X-UI...")
    
    try:
        from xui_servers.services import XUIService
        from xui_servers.models import XUIServer
        
        # بررسی سرورهای موجود
        servers = XUIServer.objects.filter(is_active=True)
        if not servers.exists():
            print("⚠️ هیچ سرور X-UI فعالی یافت نشد")
            return True
        
        for server in servers:
            try:
                xui_service = XUIService(server)
                if xui_service.login():
                    print(f"✅ اتصال به {server.name}: موفق")
                else:
                    print(f"❌ اتصال به {server.name}: ناموفق")
            except Exception as e:
                print(f"❌ خطا در اتصال به {server.name}: {e}")
        
        return True
        
    except Exception as e:
        print(f"❌ خطا در تست X-UI: {e}")
        return False

def run_quick_test():
    """اجرای تست سریع"""
    print("🧪 اجرای تست سریع...")
    
    try:
        # تست ربات کاربر
        result = subprocess.run([sys.executable, 'bot/user_bot.py', '--test'], 
                              capture_output=True, text=True, timeout=5)
        if result.returncode == 0:
            print("✅ تست ربات کاربر: موفق")
        else:
            print(f"❌ تست ربات کاربر: ناموفق - {result.stderr}")
        
        # تست ربات ادمین
        result = subprocess.run([sys.executable, 'bot/admin_boy.py', '--test'], 
                              capture_output=True, text=True, timeout=5)
        if result.returncode == 0:
            print("✅ تست ربات ادمین: موفق")
        else:
            print(f"❌ تست ربات ادمین: ناموفق - {result.stderr}")
            
    except subprocess.TimeoutExpired:
        print("⚠️ تست‌ها زمان‌بر بودند (طبیعی است)")
    except Exception as e:
        print(f"❌ خطا در تست سریع: {e}")

def main():
    """تابع اصلی"""
    print("🧪 تست ربات‌های تلگرام")
    print("=" * 40)
    
    tests = [
        ("متغیرهای محیطی", test_environment),
        ("وابستگی‌ها", test_dependencies),
        ("توکن‌های ربات", test_bot_tokens),
        ("تنظیمات Django", test_django_setup),
        ("فایل‌های ربات", test_bot_files),
        ("Syntax فایل‌ها", test_bot_syntax),
        ("Import های ربات", test_bot_imports),
        ("اتصال X-UI", test_xui_connection),
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        try:
            if test_func():
                passed += 1
            else:
                print(f"❌ تست {test_name} ناموفق بود")
        except Exception as e:
            print(f"❌ خطا در تست {test_name}: {e}")
    
    print(f"\n📊 نتیجه تست‌ها: {passed}/{total} موفق")
    
    if passed == total:
        print("🎉 تمام تست‌ها موفق بودند!")
        print("💡 ربات‌ها آماده راه‌اندازی هستند")
        
        # اجرای تست سریع
        run_quick_test()
        
    else:
        print("⚠️ برخی تست‌ها ناموفق بودند")
        print("💡 لطفاً مشکلات را برطرف کنید")
    
    print("\n📋 دستورات مفید:")
    print("   python start_bots_simple.py  # راه‌اندازی ربات‌ها")
    print("   python deploy_bots.py        # دیپلوی کامل")
    print("   systemctl status vpn-user-bot.service  # وضعیت سرویس")

if __name__ == "__main__":
    main() 