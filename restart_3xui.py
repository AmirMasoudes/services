#!/usr/bin/env python3
import subprocess
import time
import requests

def restart_3xui():
    """راه‌اندازی مجدد 3X-UI"""
    print("�� راه‌اندازی مجدد 3X-UI...")
    
    # 1. توقف سرویس
    try:
        print("⏹️ توقف سرویس x-ui...")
        result = subprocess.run(['systemctl', 'stop', 'x-ui'], 
                              capture_output=True, text=True)
        if result.returncode == 0:
            print("✅ سرویس متوقف شد")
        else:
            print(f"❌ خطا در توقف سرویس: {result.stderr}")
    except Exception as e:
        print(f"❌ خطا در توقف سرویس: {e}")
    
    # 2. صبر کردن
    print("⏳ صبر کردن 3 ثانیه...")
    time.sleep(3)
    
    # 3. راه‌اندازی مجدد
    try:
        print("▶️ راه‌اندازی مجدد سرویس x-ui...")
        result = subprocess.run(['systemctl', 'start', 'x-ui'], 
                              capture_output=True, text=True)
        if result.returncode == 0:
            print("✅ سرویس راه‌اندازی شد")
        else:
            print(f"❌ خطا در راه‌اندازی سرویس: {result.stderr}")
    except Exception as e:
        print(f"❌ خطا در راه‌اندازی سرویس: {e}")
    
    # 4. صبر کردن
    print("⏳ صبر کردن 5 ثانیه...")
    time.sleep(5)
    
    # 5. بررسی وضعیت
    try:
        result = subprocess.run(['systemctl', 'status', 'x-ui'], 
                              capture_output=True, text=True)
        print("📊 وضعیت سرویس:")
        print(result.stdout)
    except Exception as e:
        print(f"❌ خطا در بررسی وضعیت: {e}")
    
    # 6. تست API
    print("\n�� تست API بعد از راه‌اندازی مجدد...")
    base_url = "http://127.0.0.1:44/BerLdbHxpmtoT3xuzu"
    
    # ورود
    login_data = {
        "username": "admin",
        "password": "admin123"
    }
    
    session = requests.Session()
    session.headers.update({
        'Content-Type': 'application/json'
    })
    
    try:
        response = session.post(f"{base_url}/api/login", json=login_data)
        print(f"🔍 ورود: {response.status_code}")
        print(f"📋 پاسخ ورود: '{response.text}'")
        
        if response.status_code == 200:
            print("✅ ورود موفق")
            
            # تست دریافت inbound ها
            response = session.get(f"{base_url}/api/v1/inbounds")
            print(f"�� دریافت inbound ها: {response.status_code}")
            print(f"📋 پاسخ: '{response.text}'")
            
            if response.status_code == 200 and response.text.strip():
                print("✅ API کار می‌کند")
            else:
                print("❌ API هنوز مشکل دارد")
        else:
            print("❌ ورود ناموفق")
    except Exception as e:
        print(f"❌ خطا در تست API: {e}")

if __name__ == "__main__":
    restart_3xui() 