#!/usr/bin/env python3
import os
import sys
import subprocess
import requests
import json

def check_xui_installation():
    """بررسی نصب x-ui"""
    print("🔍 بررسی نصب x-ui...")
    
    # بررسی سرویس x-ui
    print("\n📊 بررسی سرویس x-ui...")
    try:
        result = subprocess.run(['systemctl', 'status', 'x-ui'], 
                              capture_output=True, text=True, timeout=10)
        print(f"کد خروجی: {result.returncode}")
        print(f"خروجی: {result.stdout[:500]}")
    except Exception as e:
        print(f"❌ خطا در بررسی سرویس: {e}")
    
    # بررسی پورت 44
    print("\n📊 بررسی پورت 44...")
    try:
        result = subprocess.run(['netstat', '-tlnp'], 
                              capture_output=True, text=True, timeout=10)
        lines = result.stdout.split('\n')
        for line in lines:
            if ':44' in line:
                print(f"✅ پورت 44: {line.strip()}")
    except Exception as e:
        print(f"❌ خطا در بررسی پورت: {e}")
    
    # بررسی فایل‌های x-ui
    print("\n📊 بررسی فایل‌های x-ui...")
    xui_paths = [
        '/usr/local/x-ui',
        '/etc/x-ui',
        '/opt/x-ui',
        '/root/x-ui'
    ]
    
    for path in xui_paths:
        if os.path.exists(path):
            print(f"✅ مسیر موجود: {path}")
            try:
                files = os.listdir(path)
                print(f"📁 فایل‌ها: {files[:10]}")
            except Exception as e:
                print(f"❌ خطا در خواندن مسیر: {e}")
        else:
            print(f"❌ مسیر موجود نیست: {path}")
    
    # بررسی دیتابیس x-ui
    print("\n📊 بررسی دیتابیس x-ui...")
    db_paths = [
        '/etc/x-ui/x-ui.db',
        '/usr/local/x-ui/x-ui.db',
        '/opt/x-ui/x-ui.db',
        '/root/x-ui/x-ui.db'
    ]
    
    for db_path in db_paths:
        if os.path.exists(db_path):
            print(f"✅ دیتابیس موجود: {db_path}")
            try:
                size = os.path.getsize(db_path)
                print(f"📊 اندازه: {size} بایت")
            except Exception as e:
                print(f"❌ خطا در بررسی اندازه: {e}")
        else:
            print(f"❌ دیتابیس موجود نیست: {db_path}")
    
    # تست اتصال به x-ui
    print("\n📊 تست اتصال به x-ui...")
    try:
        response = requests.get('http://127.0.0.1:44', timeout=5)
        print(f"✅ اتصال موفق: {response.status_code}")
        print(f"📋 محتوای پاسخ: {response.text[:200]}")
    except Exception as e:
        print(f"❌ خطا در اتصال: {e}")
    
    # بررسی لاگ‌های x-ui
    print("\n📊 بررسی لاگ‌های x-ui...")
    log_paths = [
        '/var/log/x-ui.log',
        '/usr/local/x-ui/x-ui.log',
        '/opt/x-ui/x-ui.log'
    ]
    
    for log_path in log_paths:
        if os.path.exists(log_path):
            print(f"✅ لاگ موجود: {log_path}")
            try:
                with open(log_path, 'r') as f:
                    lines = f.readlines()
                    print(f"📊 تعداد خطوط: {len(lines)}")
                    if lines:
                        print(f"📋 آخرین خط: {lines[-1].strip()}")
            except Exception as e:
                print(f"❌ خطا در خواندن لاگ: {e}")
        else:
            print(f"❌ لاگ موجود نیست: {log_path}")
    
    print("\n🎉 بررسی نصب x-ui کامل شد!")

if __name__ == "__main__":
    check_xui_installation() 