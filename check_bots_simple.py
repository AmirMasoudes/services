#!/usr/bin/env python3
"""
بررسی ساده وضعیت بات‌ها
"""

import os
import subprocess
from datetime import datetime

def check_bot_services():
    """بررسی سرویس‌های بات"""
    print("🔧 بررسی سرویس‌های بات:")
    print("=" * 40)
    
    services = [
        ("admin-bot", "Admin Bot"),
        ("user-bot", "User Bot")
    ]
    
    for service, name in services:
        try:
            result = subprocess.run(f"systemctl is-active {service}", shell=True, capture_output=True, text=True)
            if result.returncode == 0 and result.stdout.strip() == "active":
                print(f"✅ {name}: فعال")
            else:
                print(f"❌ {name}: غیرفعال")
        except Exception as e:
            print(f"❌ خطا در بررسی {name}: {e}")

def check_bot_processes():
    """بررسی پروسه‌های بات"""
    print("\n🔄 بررسی پروسه‌های بات:")
    print("=" * 40)
    
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
        print(f"❌ خطا در بررسی پروسه‌ها: {e}")

def check_bot_logs():
    """بررسی لاگ‌های بات"""
    print("\n📋 بررسی لاگ‌های بات:")
    print("=" * 40)
    
    services = ["admin-bot", "user-bot"]
    
    for service in services:
        try:
            result = subprocess.run(f"journalctl -u {service} --no-pager -n 5", shell=True, capture_output=True, text=True)
            if result.returncode == 0:
                print(f"\n📋 لاگ‌های {service}:")
                print(result.stdout)
            else:
                print(f"❌ خطا در دریافت لاگ‌های {service}")
        except Exception as e:
            print(f"❌ خطا در بررسی لاگ‌های {service}: {e}")

def test_bot_connection():
    """تست اتصال بات‌ها"""
    print("\n🔗 تست اتصال بات‌ها:")
    print("=" * 40)
    
    # بررسی فایل .env
    env_file = ".env"
    if os.path.exists(env_file):
        with open(env_file, 'r') as f:
            content = f.read()
        
        if 'ADMIN_BOT_TOKEN=' in content and 'your-admin-bot-token-here' not in content:
            print("✅ توکن Admin Bot تنظیم شده است")
        else:
            print("❌ توکن Admin Bot تنظیم نشده است")
        
        if 'USER_BOT_TOKEN=' in content and 'your-user-bot-token-here' not in content:
            print("✅ توکن User Bot تنظیم شده است")
        else:
            print("❌ توکن User Bot تنظیم نشده است")
    else:
        print("❌ فایل .env یافت نشد")

def main():
    """تابع اصلی"""
    print("🎉 بررسی وضعیت بات‌ها")
    print("=" * 60)
    print(f"📅 تاریخ: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 60)
    
    check_bot_services()
    check_bot_processes()
    check_bot_logs()
    test_bot_connection()
    
    print("\n🎉 بررسی کامل شد!")
    print("=" * 60)
    print("💡 اگر بات‌ها کار نمی‌کنند:")
    print("   1. سرویس‌ها را restart کنید")
    print("   2. توکن‌ها را بررسی کنید")
    print("   3. لاگ‌ها را بررسی کنید")
    print("=" * 60)

if __name__ == "__main__":
    main() 