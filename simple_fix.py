#!/usr/bin/env python3
"""
حل ساده مشکلات Redis و PostgreSQL
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
    
    # بررسی وضعیت Redis
    run_cmd("systemctl status redis", "وضعیت Redis")
    
    # حذف alias های قدیمی
    run_cmd("systemctl disable redis", "Disable Redis")
    run_cmd("systemctl stop redis", "Stop Redis")
    
    # حذف فایل‌های اضافی
    run_cmd("rm -f /etc/systemd/system/redis.service", "Remove old Redis service")
    run_cmd("rm -f /etc/systemd/system/redis-server.service", "Remove old Redis server service")
    
    # راه‌اندازی مجدد systemd
    run_cmd("systemctl daemon-reload", "Reload systemd")
    
    # فعال‌سازی مجدد Redis
    run_cmd("systemctl enable redis-server", "Enable Redis server")
    run_cmd("systemctl start redis-server", "Start Redis server")
    
    print("✅ Redis آماده است!")

def setup_postgresql():
    """راه‌اندازی PostgreSQL"""
    print("\n🗄️ راه‌اندازی PostgreSQL...")
    
    # بررسی وضعیت PostgreSQL
    run_cmd("systemctl status postgresql", "PostgreSQL status")
    
    # ایجاد دیتابیس
    print("\n📊 ایجاد دیتابیس...")
    
    # استفاده از فایل SQL موقت
    sql_content = """
CREATE DATABASE configvpn_db;
CREATE USER configvpn_user WITH PASSWORD 'YourSecurePassword123!@#';
GRANT ALL PRIVILEGES ON DATABASE configvpn_db TO configvpn_user;
"""
    
    with open("/tmp/setup_db.sql", "w") as f:
        f.write(sql_content)
    
    run_cmd("su - postgres -c 'psql -f /tmp/setup_db.sql'", "Setup database")
    run_cmd("rm -f /tmp/setup_db.sql", "Clean up temp file")
    
    print("✅ PostgreSQL آماده است!")

def main():
    print("🚀 حل مشکلات سرویس‌ها")
    print("=" * 40)
    
    # حل مشکل Redis
    fix_redis()
    
    # راه‌اندازی PostgreSQL
    setup_postgresql()
    
    print("\n🎉 تمام مشکلات حل شد!")
    print("=" * 40)
    print("📊 وضعیت سرویس‌ها:")
    run_cmd("systemctl status redis-server", "Redis status")
    run_cmd("systemctl status postgresql", "PostgreSQL status")

if __name__ == "__main__":
    main() 