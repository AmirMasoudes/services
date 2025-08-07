#!/usr/bin/env python3
"""
اسکریپت راه‌اندازی ربات‌ها
این اسکریپت هر دو ربات کاربر و ادمین را همزمان اجرا می‌کند
"""

import os
import sys
import asyncio
import subprocess
import signal
import time
from pathlib import Path

# اضافه کردن مسیر پروژه
project_root = Path(__file__).parent
sys.path.append(str(project_root))

# تنظیم متغیر محیطی Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')

def start_bot(bot_script):
    """شروع یک ربات در پروسه جداگانه"""
    try:
        process = subprocess.Popen([
            sys.executable, 
            str(project_root / 'bot' / bot_script)
        ], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        return process
    except Exception as e:
        print(f"خطا در شروع {bot_script}: {e}")
        return None

def signal_handler(signum, frame):
    """مدیریت سیگنال‌های خروج"""
    print("\nدر حال خروج از ربات‌ها...")
    sys.exit(0)

def main():
    """تابع اصلی"""
    print("🤖 راه‌اندازی ربات‌های تلگرام...")
    print("=" * 50)
    
    # تنظیم handler برای سیگنال‌ها
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    
    # شروع ربات‌ها
    user_bot_process = start_bot('user_bot.py')
    admin_bot_process = start_bot('admin_bot.py')
    
    if user_bot_process:
        print("✅ ربات کاربران شروع شد")
    else:
        print("❌ خطا در شروع ربات کاربران")
    
    if admin_bot_process:
        print("✅ ربات ادمین شروع شد")
    else:
        print("❌ خطا در شروع ربات ادمین")
    
    print("\n🔄 ربات‌ها در حال اجرا هستند...")
    print("برای خروج Ctrl+C را فشار دهید")
    print("=" * 50)
    
    try:
        # نگه داشتن اسکریپت فعال
        while True:
            time.sleep(1)
            
            # بررسی وضعیت پروسه‌ها
            if user_bot_process and user_bot_process.poll() is not None:
                print("⚠️ ربات کاربران متوقف شد")
                user_bot_process = None
            
            if admin_bot_process and admin_bot_process.poll() is not None:
                print("⚠️ ربات ادمین متوقف شد")
                admin_bot_process = None
            
            # اگر هر دو ربات متوقف شدند، خروج
            if not user_bot_process and not admin_bot_process:
                print("❌ هر دو ربات متوقف شدند")
                break
                
    except KeyboardInterrupt:
        print("\n🛑 در حال توقف ربات‌ها...")
        
        # توقف ربات‌ها
        if user_bot_process:
            user_bot_process.terminate()
            print("✅ ربات کاربران متوقف شد")
        
        if admin_bot_process:
            admin_bot_process.terminate()
            print("✅ ربات ادمین متوقف شد")
    
    print("👋 خروج از برنامه")

if __name__ == "__main__":
    main() 