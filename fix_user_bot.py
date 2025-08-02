#!/usr/bin/env python3
"""
راه‌اندازی مجدد User Bot
"""

import subprocess
import time

def restart_user_bot():
    """راه‌اندازی مجدد User Bot"""
    print("🔄 راه‌اندازی مجدد User Bot...")
    
    try:
        # توقف سرویس
        result = subprocess.run("systemctl stop user-bot", shell=True, capture_output=True, text=True)
        if result.returncode == 0:
            print("✅ User Bot متوقف شد")
        else:
            print("⚠️ User Bot قبلاً متوقف بود")
        
        time.sleep(2)
        
        # راه‌اندازی مجدد سرویس
        result = subprocess.run("systemctl start user-bot", shell=True, capture_output=True, text=True)
        if result.returncode == 0:
            print("✅ User Bot راه‌اندازی شد")
        else:
            print("❌ خطا در راه‌اندازی User Bot")
            print(result.stderr)
            return False
        
        time.sleep(3)
        
        # بررسی وضعیت
        result = subprocess.run("systemctl is-active user-bot", shell=True, capture_output=True, text=True)
        if result.returncode == 0 and result.stdout.strip() == "active":
            print("✅ User Bot فعال است")
            return True
        else:
            print("❌ User Bot فعال نیست")
            return False
            
    except Exception as e:
        print(f"❌ خطا در راه‌اندازی مجدد: {e}")
        return False

def check_user_bot_logs():
    """بررسی لاگ‌های User Bot"""
    print("\n📋 بررسی لاگ‌های User Bot:")
    print("=" * 40)
    
    try:
        result = subprocess.run("journalctl -u user-bot --no-pager -n 10", shell=True, capture_output=True, text=True)
        if result.returncode == 0:
            print(result.stdout)
        else:
            print("❌ خطا در دریافت لاگ‌ها")
    except Exception as e:
        print(f"❌ خطا در بررسی لاگ‌ها: {e}")

def main():
    """تابع اصلی"""
    print("🎉 راه‌اندازی مجدد User Bot")
    print("=" * 50)
    
    # راه‌اندازی مجدد
    success = restart_user_bot()
    
    if success:
        print("\n✅ User Bot با موفقیت راه‌اندازی شد!")
    else:
        print("\n❌ خطا در راه‌اندازی User Bot")
        print("💡 لطفا لاگ‌ها را بررسی کنید")
    
    # بررسی لاگ‌ها
    check_user_bot_logs()
    
    print("\n🎉 عملیات کامل شد!")

if __name__ == "__main__":
    main() 