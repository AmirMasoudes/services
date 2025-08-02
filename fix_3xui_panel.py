#!/usr/bin/env python3
import subprocess
import time
import os

def fix_3xui_panel():
    """رفع مشکل پنل 3X-UI"""
    print("�� رفع مشکل پنل 3X-UI...")
    
    # 1. بررسی وضعیت فعلی
    try:
        result = subprocess.run(['x-ui', '14'], capture_output=True, text=True)
        print("📊 وضعیت فعلی:")
        print(result.stdout)
    except Exception as e:
        print(f"❌ خطا در بررسی وضعیت: {e}")
    
    # 2. توقف سرویس‌های موجود
    try:
        print("⏹️ توقف سرویس‌های موجود...")
        subprocess.run(['systemctl', 'stop', 'x-ui'], check=False)
        subprocess.run(['pkill', '-f', 'x-ui'], check=False)
        print("✅ سرویس‌ها متوقف شدند")
    except Exception as e:
        print(f"❌ خطا در توقف سرویس‌ها: {e}")
    
    # 3. صبر کردن
    print("⏳ صبر کردن 3 ثانیه...")
    time.sleep(3)
    
    # 4. بررسی پورت‌های در حال استفاده
    try:
        result = subprocess.run(['netstat', '-tlnp'], capture_output=True, text=True)
        lines = result.stdout.split('\n')
        port_44_lines = [line for line in lines if ':44' in line]
        if port_44_lines:
            print("⚠️ پورت 44 در حال استفاده:")
            for line in port_44_lines:
                print(f"  {line}")
        else:
            print("✅ پورت 44 آزاد است")
    except Exception as e:
        print(f"❌ خطا در بررسی پورت: {e}")
    
    # 5. راه‌اندازی مجدد 3X-UI
    try:
        print("▶️ راه‌اندازی مجدد 3X-UI...")
        
        # استفاده از دستور x-ui برای راه‌اندازی
        result = subprocess.run(['x-ui', '11'], capture_output=True, text=True)
        print("📋 خروجی راه‌اندازی:")
        print(result.stdout)
        if result.stderr:
            print("⚠️ خطاهای راه‌اندازی:")
            print(result.stderr)
            
    except Exception as e:
        print(f"❌ خطا در راه‌اندازی: {e}")
    
    # 6. صبر کردن
    print("⏳ صبر کردن 10 ثانیه...")
    time.sleep(10)
    
    # 7. بررسی وضعیت مجدد
    try:
        result = subprocess.run(['x-ui', '14'], capture_output=True, text=True)
        print("📊 وضعیت جدید:")
        print(result.stdout)
    except Exception as e:
        print(f"❌ خطا در بررسی وضعیت: {e}")
    
    # 8. تست اتصال
    try:
        print("🌐 تست اتصال...")
        result = subprocess.run(['netstat', '-tlnp'], capture_output=True, text=True)
        lines = result.stdout.split('\n')
        xui_lines = [line for line in lines if ':44' in line]
        print(" پورت 44:")
        for line in xui_lines:
            print(line)
    except Exception as e:
        print(f"❌ خطا در بررسی پورت: {e}")
    
    # 9. بررسی لاگ‌ها
    try:
        print("�� بررسی لاگ‌ها...")
        result = subprocess.run(['x-ui', '15'], capture_output=True, text=True)
        print("📋 لاگ‌های اخیر:")
        print(result.stdout)
    except Exception as e:
        print(f"❌ خطا در بررسی لاگ‌ها: {e}")

if __name__ == "__main__":
    fix_3xui_panel() 