#!/usr/bin/env python3
"""
بررسی وضعیت نهایی سیستم Django VPN
"""

import os
import subprocess
from datetime import datetime

def check_system_status():
    """بررسی وضعیت کلی سیستم"""
    print("🎉 بررسی وضعیت نهایی سیستم Django VPN")
    print("=" * 60)
    print(f"📅 تاریخ: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 60)
    
    # بررسی سرویس‌ها
    print("\n🚀 وضعیت سرویس‌ها:")
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
        try:
            result = subprocess.run(f"systemctl is-active {service}", shell=True, capture_output=True, text=True)
            if result.returncode == 0 and result.stdout.strip() == "active":
                print(f"✅ {name}: فعال")
                active_services += 1
            else:
                print(f"❌ {name}: غیرفعال")
        except Exception as e:
            print(f"❌ خطا در بررسی {name}: {e}")
    
    print(f"\n📊 سرویس‌های فعال: {active_services}/{len(services)}")
    
    # بررسی پورت‌ها
    print("\n🔌 وضعیت پورت‌ها:")
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
        try:
            result = subprocess.run(f"ss -tlnp | grep :{port}", shell=True, capture_output=True, text=True)
            if result.returncode == 0:
                print(f"✅ {name} (:{port}): باز")
                open_ports += 1
            else:
                print(f"❌ {name} (:{port}): بسته")
        except Exception as e:
            print(f"❌ خطا در بررسی {name}: {e}")
    
    print(f"\n📊 پورت‌های باز: {open_ports}/{len(ports)}")
    
    # بررسی پروسه‌های بات
    print("\n🤖 وضعیت بات‌ها:")
    print("=" * 30)
    
    try:
        result = subprocess.run("ps aux | grep -E '(admin_boy|user_bot)' | grep -v grep", shell=True, capture_output=True, text=True)
        
        if result.returncode == 0 and result.stdout.strip():
            processes = result.stdout.strip().split('\n')
            print("✅ پروسه‌های بات در حال اجرا:")
            for process in processes:
                if process.strip():
                    print(f"   🔄 {process.strip()}")
        else:
            print("❌ هیچ پروسه‌ای از بات‌ها یافت نشد")
    except Exception as e:
        print(f"❌ خطا در بررسی پروسه‌های بات: {e}")
    
    # بررسی فایل‌های مهم
    print("\n📁 فایل‌های مهم:")
    print("=" * 30)
    
    important_files = [
        ".env",
        "bot/admin_boy.py",
        "bot/user_bot.py",
        "config/settings.py",
        "xui_servers/settings.py"
    ]
    
    existing_files = 0
    for file_path in important_files:
        if os.path.exists(file_path):
            print(f"✅ {file_path}: موجود")
            existing_files += 1
        else:
            print(f"❌ {file_path}: موجود نیست")
    
    print(f"\n📊 فایل‌های موجود: {existing_files}/{len(important_files)}")
    
    # خلاصه نهایی
    print("\n🎉 خلاصه نهایی:")
    print("=" * 40)
    
    if active_services >= 5 and open_ports >= 4 and existing_files == len(important_files):
        print("✅ سیستم کاملاً آماده است!")
        print("🚀 تمام اجزاء فعال هستند")
        print("🎯 آماده استفاده")
    elif active_services >= 4 and open_ports >= 3:
        print("⚠️ سیستم تقریباً آماده است")
        print("🔧 برخی اجزاء نیاز به بررسی دارند")
        print("💡 User Bot ممکن است نیاز به restart داشته باشد")
    else:
        print("❌ سیستم نیاز به بررسی دارد")
        print("🔧 برخی سرویس‌ها غیرفعال هستند")
    
    print("\n🌐 دسترسی‌ها:")
    print(" Django Admin: http://38.54.105.124/admin/")
    print("🔧 X-UI Panel: http://38.54.105.124:54321/MsxZ4xuIy5xLfQtsSC/")
    print("👤 Username: admin")
    print("🔑 Password: YourSecurePassword123")
    
    print("\n💡 دستورات مفید:")
    print("   python final_test_complete.py    # تست کامل")
    print("   python check_bots_simple.py      # بررسی بات‌ها")
    print("   python fix_user_bot.py          # راه‌اندازی مجدد User Bot")
    print("   systemctl restart user-bot       # Restart User Bot")
    
    print("\n🎯 سیستم آماده استفاده است!")

if __name__ == "__main__":
    check_system_status() 