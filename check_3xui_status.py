#!/usr/bin/env python3
import requests
import subprocess
import os

def check_3xui_status():
    """بررسی وضعیت 3X-UI"""
    print("🔍 بررسی وضعیت 3X-UI...")
    
    # 1. بررسی سرویس
    try:
        result = subprocess.run(['systemctl', 'status', 'x-ui'], 
                              capture_output=True, text=True)
        print("📊 وضعیت سرویس x-ui:")
        print(result.stdout)
    except Exception as e:
        print(f"❌ خطا در بررسی سرویس: {e}")
    
    # 2. بررسی پورت
    try:
        result = subprocess.run(['netstat', '-tlnp'], 
                              capture_output=True, text=True)
        lines = result.stdout.split('\n')
        xui_lines = [line for line in lines if ':44' in line]
        print(f"\n�� پورت 44:")
        for line in xui_lines:
            print(line)
    except Exception as e:
        print(f"❌ خطا در بررسی پورت: {e}")
    
    # 3. بررسی فایل‌های 3X-UI
    paths = [
        '/usr/local/x-ui',
        '/etc/x-ui',
        '/opt/x-ui'
    ]
    
    for path in paths:
        if os.path.exists(path):
            print(f"\n�� محتویات {path}:")
            try:
                files = os.listdir(path)
                for file in files:
                    print(f"  - {file}")
            except Exception as e:
                print(f"❌ خطا در خواندن {path}: {e}")
    
    # 4. تست endpoint های مختلف
    base_urls = [
        "http://127.0.0.1:44",
        "http://127.0.0.1:44/BerLdbHxpmtoT3xuzu",
        "http://127.0.0.1:44/xui",
        "http://127.0.0.1:44/panel"
    ]
    
    for base_url in base_urls:
        try:
            response = requests.get(base_url, timeout=5)
            print(f"\n�� تست {base_url}:")
            print(f"کد پاسخ: {response.status_code}")
            print(f"نوع محتوا: {response.headers.get('content-type', 'نامشخص')}")
            if response.status_code == 200:
                print("✅ قابل دسترسی")
            else:
                print("❌ غیرقابل دسترسی")
        except Exception as e:
            print(f"❌ خطا در {base_url}: {e}")

if __name__ == "__main__":
    check_3xui_status() 