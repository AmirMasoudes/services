#!/usr/bin/env python3
"""
اسکریپت ساده راه‌اندازی ربات‌های تلگرام
"""

import os
import sys
import subprocess
import time
import signal
import threading
from dotenv import load_dotenv

# بارگذاری متغیرهای محیطی
load_dotenv()

def check_tokens():
    """بررسی توکن‌های ربات"""
    print("🔍 بررسی توکن‌های ربات...")
    
    user_token = os.getenv('USER_BOT_TOKEN')
    admin_token = os.getenv('ADMIN_BOT_TOKEN')
    
    if not user_token:
        print("❌ USER_BOT_TOKEN تعریف نشده است")
        print("💡 لطفاً در فایل .env تعریف کنید:")
        print("   USER_BOT_TOKEN=your_user_bot_token_here")
        return False
    
    if not admin_token:
        print("❌ ADMIN_BOT_TOKEN تعریف نشده است")
        print("💡 لطفاً در فایل .env تعریف کنید:")
        print("   ADMIN_BOT_TOKEN=your_admin_bot_token_here")
        return False
    
    print("✅ توکن‌های ربات موجود هستند")
    return True

def run_user_bot():
    """اجرای ربات کاربر"""
    print("🚀 راه‌اندازی ربات کاربر...")
    try:
        subprocess.run([sys.executable, 'bot/user_bot.py'], check=True)
    except KeyboardInterrupt:
        print("🛑 ربات کاربر متوقف شد")
    except Exception as e:
        print(f"❌ خطا در ربات کاربر: {e}")

def run_admin_bot():
    """اجرای ربات ادمین"""
    print("🚀 راه‌اندازی ربات ادمین...")
    try:
        subprocess.run([sys.executable, 'bot/admin_boy.py'], check=True)
    except KeyboardInterrupt:
        print("🛑 ربات ادمین متوقف شد")
    except Exception as e:
        print(f"❌ خطا در ربات ادمین: {e}")

def main():
    """تابع اصلی"""
    print("🤖 راه‌اندازی ربات‌های تلگرام")
    print("=" * 40)
    
    # بررسی توکن‌ها
    if not check_tokens():
        return
    
    print("\n📋 اطلاعات ربات‌ها:")
    print(f"   - ربات کاربر: {os.getenv('USER_BOT_TOKEN', 'نامشخص')[:20]}...")
    print(f"   - ربات ادمین: {os.getenv('ADMIN_BOT_TOKEN', 'نامشخص')[:20]}...")
    
    # راه‌اندازی ربات‌ها در thread های جداگانه
    user_thread = threading.Thread(target=run_user_bot, daemon=True)
    admin_thread = threading.Thread(target=run_admin_bot, daemon=True)
    
    try:
        # شروع ربات‌ها
        user_thread.start()
        admin_thread.start()
        
        print("\n✅ ربات‌ها راه‌اندازی شدند!")
        print("💡 برای توقف، Ctrl+C را فشار دهید")
        
        # انتظار
        while True:
            time.sleep(1)
            
    except KeyboardInterrupt:
        print("\n🛑 توقف ربات‌ها...")
        print("✅ ربات‌ها متوقف شدند")

if __name__ == "__main__":
    main() 