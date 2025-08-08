#!/usr/bin/env python3
"""
اسکریپت ساده برای تست اتصال به X-UI
"""

import requests
import urllib3
from dotenv import load_dotenv
import os

# Load environment variables
load_dotenv('env_config.env')

def test_connection():
    """تست اتصال ساده به X-UI"""
    print("🔍 تست اتصال ساده به X-UI...")
    
    # دریافت تنظیمات
    host = os.getenv('XUI_DEFAULT_HOST')
    port = int(os.getenv('XUI_DEFAULT_PORT', 54321))
    username = os.getenv('XUI_DEFAULT_USERNAME')
    password = os.getenv('XUI_DEFAULT_PASSWORD')
    web_base_path = os.getenv('XUI_WEB_BASE_PATH', '/')
    use_ssl = os.getenv('XUI_USE_SSL', 'False').lower() == 'true'
    
    print(f"📋 تنظیمات سرور:")
    print(f"   • آدرس: {host}")
    print(f"   • پورت: {port}")
    print(f"   • نام کاربری: {username}")
    print(f"   • مسیر وب: {web_base_path}")
    print(f"   • استفاده از SSL: {use_ssl}")
    
    # تست HTTP
    print("\n🔧 تست HTTP...")
    try:
        protocol = "https" if use_ssl else "http"
        url = f"{protocol}://{host}:{port}{web_base_path}"
        print(f"URL: {url}")
        
        response = requests.get(url, timeout=10, verify=False)
        print(f"✅ HTTP موفق - کد: {response.status_code}")
        print(f"محتوای پاسخ: {response.text[:200]}...")
        
    except requests.exceptions.SSLError as e:
        print(f"❌ خطای SSL: {e}")
    except requests.exceptions.ConnectionError as e:
        print(f"❌ خطای اتصال: {e}")
    except requests.exceptions.Timeout as e:
        print(f"❌ خطای تایم‌اوت: {e}")
    except Exception as e:
        print(f"❌ خطای نامشخص: {e}")
    
    # تست پورت
    print("\n🔧 تست پورت...")
    try:
        import socket
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(10)
        result = sock.connect_ex((host, port))
        sock.close()
        
        if result == 0:
            print(f"✅ پورت {port} باز است")
        else:
            print(f"❌ پورت {port} بسته است")
            
    except Exception as e:
        print(f"❌ خطا در تست پورت: {e}")
    
    # تست DNS
    print("\n🔧 تست DNS...")
    try:
        import socket
        ip = socket.gethostbyname(host)
        print(f"✅ DNS موفق - IP: {ip}")
    except Exception as e:
        print(f"❌ خطای DNS: {e}")

if __name__ == "__main__":
    test_connection()
