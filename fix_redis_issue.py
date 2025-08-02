#!/usr/bin/env python3
"""
راه‌اندازی مجدد Redis و حل مشکل systemd
"""

import subprocess
import os

def run_cmd(cmd, desc=""):
    print(f"🔧 {desc}")
    print(f"📝 {cmd}")
    result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
    if result.returncode == 0:
        print(f"✅ {desc}")
        return True
    else:
        print(f"❌ {desc}: {result.stderr}")
        return False

def fix_redis():
    """حل مشکل Redis"""
    
    print("🔧 حل مشکل Redis...")
    print("=" * 40)
    
    # بررسی وضعیت Redis
    print("\n📊 بررسی وضعیت Redis...")
    run_cmd("systemctl status redis", "وضعیت Redis")
    
    # حذف alias های قدیمی
    print("\n🗑️ حذف alias های قدیمی...")
    run_cmd("systemctl disable redis", "Disable Redis")
    run_cmd("systemctl stop redis", "Stop Redis")
    
    # بررسی فایل‌های سرویس
    print("\n📁 بررسی فایل‌های سرویس...")
    run_cmd("ls -la /etc/systemd/system/redis*", "Redis service files")
    
    # حذف فایل‌های اضافی
    run_cmd("rm -f /etc/systemd/system/redis.service", "Remove old Redis service")
    run_cmd("rm -f /etc/systemd/system/redis-server.service", "Remove old Redis server service")
    
    # راه‌اندازی مجدد systemd
    print("\n🔄 راه‌اندازی مجدد systemd...")
    run_cmd("systemctl daemon-reload", "Reload systemd")
    
    # فعال‌سازی مجدد Redis
    print("\n🚀 فعال‌سازی مجدد Redis...")
    run_cmd("systemctl enable redis-server", "Enable Redis server")
    run_cmd("systemctl start redis-server", "Start Redis server")
    
    # بررسی وضعیت نهایی
    print("\n📊 بررسی وضعیت نهایی...")
    run_cmd("systemctl status redis-server", "Final Redis status")
    
    print("\n🎉 حل مشکل Redis کامل شد!")

def setup_postgresql():
    """راه‌اندازی PostgreSQL"""
    
    print("\n🗄️ راه‌اندازی PostgreSQL...")
    print("=" * 40)
    
    # بررسی وضعیت PostgreSQL
    run_cmd("systemctl status postgresql", "PostgreSQL status")
    
    # ایجاد دیتابیس و کاربر (بدون sudo)
    print("\n📊 ایجاد دیتابیس...")
    run_cmd('su - postgres -c "psql -c \\"CREATE DATABASE configvpn_db;\\""', "Create database")
    run_cmd('su - postgres -c "psql -c \\"CREATE USER configvpn_user WITH PASSWORD \\'YourSecurePassword123!@#';\\""', "Create user")
    run_cmd('su - postgres -c "psql -c \\"GRANT ALL PRIVILEGES ON DATABASE configvpn_db TO configvpn_user;\\""', "Grant privileges")
    
    print("\n✅ PostgreSQL آماده است!")

def main():
    """تابع اصلی"""
    
    print("🚀 حل مشکلات سرویس‌ها")
    print("=" * 50)
    
    # حل مشکل Redis
    fix_redis()
    
    # راه‌اندازی PostgreSQL
    setup_postgresql()
    
    print("\n🎉 تمام مشکلات حل شد!")
    print("=" * 50)
    print("📊 وضعیت سرویس‌ها:")
    run_cmd("systemctl status redis-server", "Redis status")
    run_cmd("systemctl status postgresql", "PostgreSQL status")

if __name__ == "__main__":
    main() 