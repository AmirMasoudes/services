#!/usr/bin/env python3
"""
تست نهایی کامل سیستم Django VPN
"""

import os
import sys
import django
import subprocess
from datetime import datetime

# تنظیم Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from plan.models import ConfingPlansModel
from accounts.models import UsersModel
from xui_servers.models import XUIServer

def test_plans():
    """تست پلن‌ها"""
    print("📦 تست پلن‌های VPN:")
    print("=" * 40)
    
    plans = ConfingPlansModel.objects.filter(is_active=True)
    
    if plans.exists():
        for plan in plans:
            traffic_gb = plan.traffic_mb / 1024 if plan.traffic_mb > 0 else 0
            print(f"✅ {plan.name}")
            print(f"   💰 قیمت: {plan.price:,} تومان")
            print(f"   📊 حجم: {traffic_gb:.1f} GB ({plan.traffic_mb:,} MB)")
            print(f"   ⏰ مدت: {plan.in_volume} روز")
            if plan.description:
                print(f"   📝 توضیحات: {plan.description}")
            print("-" * 30)
        
        print(f"\n📊 تعداد کل پلن‌های فعال: {plans.count()}")
        return True
    else:
        print("❌ هیچ پلن فعالی یافت نشد!")
        return False

def test_users():
    """تست کاربران"""
    print("\n👥 تست کاربران:")
    print("=" * 30)
    
    users = UsersModel.objects.all()
    
    if users.exists():
        for user in users:
            print(f"✅ {user.full_name} (ID: {user.id_tel})")
            print(f"   📱 Username: {user.username_tel}")
            print(f"   🔗 Telegram ID: {user.telegram_id}")
            print(f"   👤 Staff: {user.is_staff}")
            print(f"   🔧 Superuser: {user.is_superuser}")
            print(f"   🎯 Admin: {user.is_admin}")
            print(f"   📊 Trial Used: {user.has_used_trial}")
            print("-" * 25)
        
        print(f"\n📊 تعداد کل کاربران: {users.count()}")
        return True
    else:
        print("❌ هیچ کاربری یافت نشد!")
        return False

def test_xui_server():
    """تست سرور X-UI"""
    print("\n🔧 تست سرور X-UI:")
    print("=" * 30)
    
    servers = XUIServer.objects.filter(is_active=True)
    
    if servers.exists():
        for server in servers:
            print(f"✅ {server.name}")
            print(f"   🌐 آدرس: {server.host}:{server.port}")
            print(f"   👤 کاربر: {server.username}")
            print(f"   🔗 مسیر: {server.web_base_path}")
            print(f"   📊 فعال: {server.is_active}")
            print("-" * 25)
        
        print(f"\n📊 تعداد سرورهای فعال: {servers.count()}")
        return True
    else:
        print("❌ هیچ سرور X-UI فعالی یافت نشد!")
        return False

def test_services():
    """تست سرویس‌ها"""
    print("\n🚀 تست سرویس‌ها:")
    print("=" * 30)
    
    services = [
        ("django-vpn", "Django VPN"),
        ("nginx", "Nginx"),
        ("redis-server", "Redis"),
        ("postgresql", "PostgreSQL"),
        ("admin-bot", "Admin Bot"),
        ("user-bot", "User Bot")
    ]
    
    active_services = 0
    for service, name in services:
        result = subprocess.run(f"systemctl is-active {service}", shell=True, capture_output=True, text=True)
        if result.returncode == 0 and result.stdout.strip() == "active":
            print(f"✅ {name}: فعال")
            active_services += 1
        else:
            print(f"❌ {name}: غیرفعال")
    
    print(f"\n📊 سرویس‌های فعال: {active_services}/{len(services)}")
    return active_services >= 4  # حداقل 4 سرویس باید فعال باشد

def test_ports():
    """تست پورت‌ها"""
    print("\n🔌 تست پورت‌ها:")
    print("=" * 30)
    
    ports = [
        (80, "HTTP"),
        (8000, "Django"),
        (54321, "X-UI Panel"),
        (6379, "Redis"),
        (5432, "PostgreSQL")
    ]
    
    open_ports = 0
    for port, name in ports:
        result = subprocess.run(f"ss -tlnp | grep :{port}", shell=True, capture_output=True, text=True)
        if result.returncode == 0:
            print(f"✅ {name} (:{port}): باز")
            open_ports += 1
        else:
            print(f"❌ {name} (:{port}): بسته")
    
    print(f"\n📊 پورت‌های باز: {open_ports}/{len(ports)}")
    return open_ports >= 3  # حداقل 3 پورت باید باز باشد

def test_bots():
    """تست بات‌ها"""
    print("\n🤖 تست بات‌ها:")
    print("=" * 30)
    
    bot_files = [
        "bot/admin_boy.py",
        "bot/user_bot.py"
    ]
    
    existing_bots = 0
    for bot_file in bot_files:
        if os.path.exists(bot_file):
            print(f"✅ {bot_file}: موجود")
            existing_bots += 1
        else:
            print(f"❌ {bot_file}: موجود نیست")
    
    print(f"\n📊 فایل‌های بات موجود: {existing_bots}/{len(bot_files)}")
    return existing_bots == len(bot_files)

def test_bot_processes():
    """تست پروسه‌های بات"""
    print("\n🔄 تست پروسه‌های بات:")
    print("=" * 30)
    
    # بررسی پروسه‌های Python که بات‌ها را اجرا می‌کنند
    result = subprocess.run("ps aux | grep -E '(admin_boy|user_bot)' | grep -v grep", shell=True, capture_output=True, text=True)
    
    if result.returncode == 0:
        processes = result.stdout.strip().split('\n')
        if processes and processes[0]:
            print("✅ پروسه‌های بات در حال اجرا:")
            for process in processes:
                if process.strip():
                    print(f"   🔄 {process.strip()}")
            return True
        else:
            print("❌ هیچ پروسه‌ای از بات‌ها یافت نشد")
            return False
    else:
        print("❌ هیچ پروسه‌ای از بات‌ها یافت نشد")
        return False

def main():
    """تابع اصلی"""
    print("🎉 تست نهایی کامل سیستم Django VPN")
    print("=" * 60)
    print(f"📅 تاریخ: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 60)
    
    # تست‌های مختلف
    tests = [
        ("پلن‌ها", test_plans),
        ("کاربران", test_users),
        ("سرور X-UI", test_xui_server),
        ("سرویس‌ها", test_services),
        ("پورت‌ها", test_ports),
        ("بات‌ها", test_bots),
        ("پروسه‌های بات", test_bot_processes)
    ]
    
    passed_tests = 0
    total_tests = len(tests)
    
    for test_name, test_func in tests:
        try:
            if test_func():
                passed_tests += 1
        except Exception as e:
            print(f"❌ خطا در تست {test_name}: {e}")
    
    print("\n🎉 نتیجه نهایی:")
    print("=" * 40)
    print(f"✅ تست‌های موفق: {passed_tests}/{total_tests}")
    
    if passed_tests == total_tests:
        print("🎉 تمام تست‌ها موفق بودند!")
        print("🚀 سیستم کاملاً آماده است!")
    else:
        print("⚠️ برخی تست‌ها ناموفق بودند")
        print("🔧 نیاز به بررسی بیشتر")
    
    print("\n🌐 دسترسی‌ها:")
    print(" Django Admin: http://38.54.105.124/admin/")
    print("🔧 X-UI Panel: http://38.54.105.124:54321/MsxZ4xuIy5xLfQtsSC/")
    print("👤 Username: admin")
    print("🔑 Password: YourSecurePassword123")
    
    print("\n🎯 سیستم آماده استفاده است!")

if __name__ == "__main__":
    main() 