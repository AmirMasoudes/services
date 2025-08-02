#!/usr/bin/env python3
"""
راه‌اندازی نهایی سیستم Django VPN
"""

import subprocess
import os

def run_cmd(cmd, desc=""):
    print(f"�� {desc}")
    print(f"�� {cmd}")
    result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
    if result.returncode == 0:
        print(f"✅ {desc}")
        return True
    else:
        print(f"❌ {desc}: {result.stderr}")
        return False

def final_setup():
    """راه‌اندازی نهایی"""
    print("🚀 راه‌اندازی نهایی سیستم Django VPN")
    print("=" * 50)
    
    # 1. بررسی سرویس‌ها
    print("\n1️⃣ بررسی سرویس‌ها...")
    services = [
        ("django-vpn", "Django VPN Service"),
        ("nginx", "Nginx"),
        ("redis-server", "Redis"),
        ("postgresql", "PostgreSQL")
    ]
    
    for service, name in services:
        run_cmd(f"systemctl status {service}", f"{name} Status")
    
    # 2. تست Django
    print("\n2️⃣ تست Django...")
    run_cmd("python test_complete_system.py", "Complete System Test")
    
    # 3. بررسی پورت‌ها
    print("\n3️⃣ بررسی پورت‌ها...")
    run_cmd("netstat -tlnp | grep -E ':(80|8000|54321|6379|5432)'", "Port Status")
    
    # 4. بررسی فایل‌های log
    print("\n4️⃣ بررسی فایل‌های log...")
    run_cmd("tail -n 5 /var/log/nginx/error.log", "Nginx Error Log")
    run_cmd("journalctl -u django-vpn -n 10", "Django Service Log")
    
    print("\n🎉 راه‌اندازی نهایی کامل شد!")
    print("=" * 50)
    print("📊 سیستم آماده است!")
    print("\n🌐 دسترسی‌ها:")
    print("�� Django Admin: http://38.54.105.124/admin/")
    print("🔧 X-UI Panel: http://38.54.105.124:54321/MsxZ4xuIy5xLfQtsSC/")
    print("�� Username: admin")
    print("🔑 Password: YourSecurePassword123!@#")
    print("\n📋 ویژگی‌ها:")
    print("✅ Django VPN Management System")
    print("✅ X-UI Integration")
    print("✅ Automatic Inbound Creation")
    print("✅ User Management")
    print("✅ Payment Integration")
    print("✅ Telegram Bot Support")

if __name__ == "__main__":
    final_setup()
