#!/usr/bin/env python3
"""
بررسی وضعیت بات‌ها
"""

import os
import subprocess
from datetime import datetime

def check_bot_files():
    """بررسی فایل‌های بات"""
    print("🤖 بررسی فایل‌های بات:")
    print("=" * 40)
    
    bot_files = [
        "bot/admin_boy.py",
        "bot/user_bot.py"
    ]
    
    for bot_file in bot_files:
        if os.path.exists(bot_file):
            print(f"✅ {bot_file}: موجود")
        else:
            print(f"❌ {bot_file}: موجود نیست")

def check_bot_services():
    """بررسی سرویس‌های بات"""
    print("\n🔧 بررسی سرویس‌های بات:")
    print("=" * 40)
    
    services = [
        ("admin-bot", "Admin Bot"),
        ("user-bot", "User Bot")
    ]
    
    for service, name in services:
        result = subprocess.run(f"systemctl is-active {service}", shell=True, capture_output=True, text=True)
        if result.returncode == 0 and result.stdout.strip() == "active":
            print(f"✅ {name}: فعال")
        else:
            print(f"❌ {name}: غیرفعال")

def check_bot_processes():
    """بررسی پروسه‌های بات"""
    print("\n🔄 بررسی پروسه‌های بات:")
    print("=" * 40)
    
    # بررسی پروسه‌های Python که بات‌ها را اجرا می‌کنند
    result = subprocess.run("ps aux | grep -E '(admin_boy|user_bot)' | grep -v grep", shell=True, capture_output=True, text=True)
    
    if result.returncode == 0:
        processes = result.stdout.strip().split('\n')
        if processes and processes[0]:
            print("✅ پروسه‌های بات در حال اجرا:")
            for process in processes:
                if process.strip():
                    print(f"   🔄 {process.strip()}")
        else:
            print("❌ هیچ پروسه‌ای از بات‌ها یافت نشد")
    else:
        print("❌ هیچ پروسه‌ای از بات‌ها یافت نشد")

def start_bots_manually():
    """راه‌اندازی دستی بات‌ها"""
    print("\n🚀 راه‌اندازی دستی بات‌ها:")
    print("=" * 40)
    
    # بررسی فایل‌های بات
    admin_bot = "bot/admin_boy.py"
    user_bot = "bot/user_bot.py"
    
    if not os.path.exists(admin_bot):
        print(f"❌ فایل {admin_bot} یافت نشد!")
        return
    
    if not os.path.exists(user_bot):
        print(f"❌ فایل {user_bot} یافت نشد!")
        return
    
    print("✅ فایل‌های بات موجود هستند")
    
    # راه‌اندازی Admin Bot
    print("\n🔧 راه‌اندازی Admin Bot...")
    try:
        # اجرای Admin Bot در پس‌زمینه
        admin_process = subprocess.Popen([
            "python", admin_bot
        ], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        
        print(f"✅ Admin Bot راه‌اندازی شد (PID: {admin_process.pid})")
    except Exception as e:
        print(f"❌ خطا در راه‌اندازی Admin Bot: {e}")
    
    # راه‌اندازی User Bot
    print("\n👤 راه‌اندازی User Bot...")
    try:
        # اجرای User Bot در پس‌زمینه
        user_process = subprocess.Popen([
            "python", user_bot
        ], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        
        print(f"✅ User Bot راه‌اندازی شد (PID: {user_process.pid})")
    except Exception as e:
        print(f"❌ خطا در راه‌اندازی User Bot: {e}")
    
    print("\n🎉 بات‌ها با موفقیت راه‌اندازی شدند!")

def restart_bot_services():
    """راه‌اندازی مجدد سرویس‌های بات"""
    print("\n🔄 راه‌اندازی مجدد سرویس‌های بات:")
    print("=" * 40)
    
    services = ["admin-bot", "user-bot"]
    
    for service in services:
        try:
            # توقف سرویس
            subprocess.run(["systemctl", "stop", service], check=True)
            print(f"⏹️ {service}: متوقف شد")
            
            # راه‌اندازی مجدد سرویس
            subprocess.run(["systemctl", "start", service], check=True)
            print(f"▶️ {service}: راه‌اندازی شد")
            
        except Exception as e:
            print(f"❌ خطا در {service}: {e}")

def main():
    """تابع اصلی"""
    print("🎉 بررسی وضعیت بات‌ها")
    print("=" * 60)
    print(f"📅 تاریخ: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 60)
    
    # بررسی فایل‌ها
    check_bot_files()
    
    # بررسی سرویس‌ها
    check_bot_services()
    
    # بررسی پروسه‌ها
    check_bot_processes()
    
    print("\n🎉 بررسی کامل شد!")
    print("=" * 60)
    print("💡 اگر بات‌ها کار نمی‌کنند:")
    print("   1. سرویس‌ها را راه‌اندازی مجدد کنید")
    print("   2. یا بات‌ها را دستی راه‌اندازی کنید")
    print("=" * 60)

if __name__ == "__main__":
    main() 