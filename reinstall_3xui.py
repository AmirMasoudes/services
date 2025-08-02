#!/usr/bin/env python3
import subprocess
import time
import requests

def reinstall_3xui():
    """نصب مجدد 3X-UI"""
    print("🔧 نصب مجدد 3X-UI...")
    
    # 1. توقف سرویس
    try:
        print("⏹️ توقف سرویس x-ui...")
        subprocess.run(['systemctl', 'stop', 'x-ui'], check=True)
        print("✅ سرویس متوقف شد")
    except Exception as e:
        print(f"❌ خطا در توقف سرویس: {e}")
    
    # 2. حذف فایل‌های قدیمی
    try:
        print("🗑️ حذف فایل‌های قدیمی...")
        subprocess.run(['rm', '-rf', '/usr/local/x-ui'], check=True)
        subprocess.run(['rm', '-rf', '/etc/x-ui'], check=True)
        print("✅ فایل‌های قدیمی حذف شدند")
    except Exception as e:
        print(f"❌ خطا در حذف فایل‌ها: {e}")
    
    # 3. نصب مجدد 3X-UI
    try:
        print("📦 نصب مجدد 3X-UI...")
        install_script = '''bash <(curl -Ls https://github.com/MHSanaei/3x-ui/releases/latest/download/install.sh)'''
        result = subprocess.run(install_script, shell=True, capture_output=True, text=True)
        print("✅ نصب مجدد کامل شد")
        print("📋 خروجی نصب:")
        print(result.stdout)
        if result.stderr:
            print("⚠️ خطاهای نصب:")
            print(result.stderr)
    except Exception as e:
        print(f"❌ خطا در نصب: {e}")
    
    # 4. صبر کردن
    print("⏳ صبر کردن 10 ثانیه...")
    time.sleep(10)
    
    # 5. بررسی وضعیت
    try:
        result = subprocess.run(['systemctl', 'status', 'x-ui'], 
                              capture_output=True, text=True)
        print("📊 وضعیت سرویس:")
        print(result.stdout)
    except Exception as e:
        print(f"❌ خطا در بررسی وضعیت: {e}")
    
    # 6. تست API
    print("\n�� تست API بعد از نصب مجدد...")
    base_url = "http://127.0.0.1:44"
    
    # تست endpoint های مختلف
    endpoints = [
        "",
        "/BerLdbHxpmtoT3xuzu",
        "/xui",
        "/panel"
    ]
    
    for endpoint in endpoints:
        try:
            url = f"{base_url}{endpoint}"
            response = requests.get(url, timeout=5)
            print(f" تست {url}: {response.status_code}")
            if response.status_code == 200:
                print("✅ قابل دسترسی")
            else:
                print("❌ غیرقابل دسترسی")
        except Exception as e:
            print(f"❌ خطا در {url}: {e}")
    
    # 7. تست ورود
    try:
        login_data = {
            "username": "admin",
            "password": "admin123"
        }
        
        session = requests.Session()
        session.headers.update({
            'Content-Type': 'application/json'
        })
        
        # تست ورود
        response = session.post(f"{base_url}/api/login", json=login_data)
        print(f"\n🔍 ورود: {response.status_code}")
        print(f"📋 پاسخ ورود: '{response.text}'")
        
        if response.status_code == 200:
            print("✅ ورود موفق")
            
            # تست دریافت inbound ها
            response = session.get(f"{base_url}/api/v1/inbounds")
            print(f" دریافت inbound ها: {response.status_code}")
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
    reinstall_3xui() 