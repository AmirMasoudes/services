#!/usr/bin/env python3
"""
اسکریپت تست ساده اتصال به X-UI سنایی
"""

import requests
import urllib3
from urllib3.exceptions import InsecureRequestWarning

# غیرفعال کردن هشدارهای SSL
urllib3.disable_warnings(InsecureRequestWarning)

def test_xui_connection():
    """تست اتصال ساده به X-UI"""
    print("🔍 تست اتصال ساده به X-UI...")
    
    # تنظیمات سرور
    host = "156.244.31.37"
    port = 50987
    username = "bUZC0Iovb9"
    password = "4jb7doDQZg"
    web_base_path = "/YvIhWQ3Pt6cHGXegE4/"
    
    # تست 1: HTTP
    print("\n📡 تست HTTP...")
    try:
        url = f"http://{host}:{port}{web_base_path}login"
        print(f"آدرس: {url}")
        
        response = requests.get(url, timeout=10, verify=False)
        print(f"کد وضعیت: {response.status_code}")
        print(f"محتوای پاسخ: {response.text[:200]}")
        
    except Exception as e:
        print(f"❌ خطا در HTTP: {e}")
    
    # تست 2: HTTPS
    print("\n📡 تست HTTPS...")
    try:
        url = f"https://{host}:{port}{web_base_path}login"
        print(f"آدرس: {url}")
        
        response = requests.get(url, timeout=10, verify=False)
        print(f"کد وضعیت: {response.status_code}")
        print(f"محتوای پاسخ: {response.text[:200]}")
        
    except Exception as e:
        print(f"❌ خطا در HTTPS: {e}")
    
    # تست 3: اتصال مستقیم
    print("\n📡 تست اتصال مستقیم...")
    try:
        import socket
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(10)
        result = sock.connect_ex((host, port))
        sock.close()
        
        if result == 0:
            print("✅ پورت باز است")
        else:
            print("❌ پورت بسته است")
            
    except Exception as e:
        print(f"❌ خطا در اتصال مستقیم: {e}")

def test_curl_equivalent():
    """تست مشابه curl"""
    print("\n🔧 تست مشابه curl...")
    
    import subprocess
    
    # تست HTTP
    try:
        cmd = f"curl -k -v http://156.244.31.37:50987/YvIhWQ3Pt6cHGXegE4/login"
        print(f"دستور: {cmd}")
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=10)
        print(f"کد خروجی: {result.returncode}")
        print(f"خروجی: {result.stdout[:200]}")
        print(f"خطا: {result.stderr[:200]}")
    except Exception as e:
        print(f"❌ خطا در curl HTTP: {e}")
    
    # تست HTTPS
    try:
        cmd = f"curl -k -v https://156.244.31.37:50987/YvIhWQ3Pt6cHGXegE4/login"
        print(f"دستور: {cmd}")
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=10)
        print(f"کد خروجی: {result.returncode}")
        print(f"خروجی: {result.stdout[:200]}")
        print(f"خطا: {result.stderr[:200]}")
    except Exception as e:
        print(f"❌ خطا در curl HTTPS: {e}")

if __name__ == "__main__":
    print("🚀 شروع تست اتصال ساده...")
    test_xui_connection()
    test_curl_equivalent()
    print("\n✅ تست اتصال ساده تمام شد")
