#!/usr/bin/env python3
"""
اسکریپت راه‌اندازی کامل Django VPN Service
این اسکریپت تمام سرویس‌های مورد نیاز را راه‌اندازی می‌کند
"""

import os
import sys
import subprocess
import json
from pathlib import Path

def run_command(command, description=""):
    """اجرای دستور و نمایش نتیجه"""
    print(f"🔧 {description}")
    print(f"📝 اجرا: {command}")
    
    try:
        result = subprocess.run(command, shell=True, capture_output=True, text=True)
        if result.returncode == 0:
            print(f"✅ موفق: {description}")
            if result.stdout.strip():
                print(f"📄 خروجی: {result.stdout.strip()}")
        else:
            print(f"❌ خطا: {description}")
            print(f"📄 خطا: {result.stderr.strip()}")
        return result.returncode == 0
    except Exception as e:
        print(f"❌ خطا در اجرا: {e}")
        return False

def create_systemd_service():
    """ایجاد فایل systemd service برای Django"""
    
    service_content = """[Unit]
Description=Django VPN Management Service
After=network.target postgresql.service redis.service
Wants=postgresql.service redis.service

[Service]
Type=simple
User=root
Group=root
WorkingDirectory=/opt/vpn-service/services
Environment=PATH=/opt/vpn-service/services/venv/bin
ExecStart=/opt/vpn-service/services/venv/bin/python manage.py runserver 0.0.0.0:8000
ExecReload=/bin/kill -HUP $MAINPID
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
"""
    
    service_file = "/etc/systemd/system/django-vpn.service"
    
    try:
        with open(service_file, 'w') as f:
            f.write(service_content)
        print(f"✅ فایل systemd service ایجاد شد: {service_file}")
        return True
    except Exception as e:
        print(f"❌ خطا در ایجاد فایل service: {e}")
        return False

def create_nginx_config():
    """ایجاد تنظیمات Nginx"""
    
    nginx_config = """server {
    listen 80;
    server_name 38.54.105.124;
    
    # Django Admin Panel
    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
    
    # X-UI Panel
    location /xui/ {
        proxy_pass http://127.0.0.1:54321/MsxZ4xuIy5xLfQtsSC/;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
    
    # Static files
    location /static/ {
        alias /opt/vpn-service/services/staticfiles/;
        expires 30d;
        add_header Cache-Control "public, immutable";
    }
    
    # Media files
    location /media/ {
        alias /opt/vpn-service/services/media/;
        expires 30d;
        add_header Cache-Control "public, immutable";
    }
}
"""
    
    config_file = "/etc/nginx/sites-available/django-vpn"
    
    try:
        with open(config_file, 'w') as f:
            f.write(nginx_config)
        print(f"✅ فایل Nginx config ایجاد شد: {config_file}")
        return True
    except Exception as e:
        print(f"❌ خطا در ایجاد فایل Nginx: {e}")
        return False

def setup_database():
    """راه‌اندازی دیتابیس PostgreSQL"""
    
    commands = [
        "sudo -u postgres psql -c \"CREATE DATABASE configvpn_db;\"",
        "sudo -u postgres psql -c \"CREATE USER configvpn_user WITH PASSWORD 'YourSecurePassword123!@#';\"",
        "sudo -u postgres psql -c \"GRANT ALL PRIVILEGES ON DATABASE configvpn_db TO configvpn_user;\"",
        "sudo -u postgres psql -c \"ALTER USER configvpn_user CREATEDB;\""
    ]
    
    for cmd in commands:
        if not run_command(cmd, "تنظیم دیتابیس PostgreSQL"):
            return False
    return True

def install_dependencies():
    """نصب وابستگی‌های سیستم"""
    
    commands = [
        "apt update",
        "apt install -y nginx postgresql postgresql-contrib redis-server python3-pip python3-venv git curl",
        "systemctl enable postgresql",
        "systemctl start postgresql",
        "systemctl enable redis",
        "systemctl start redis"
    ]
    
    for cmd in commands:
        if not run_command(cmd, "نصب وابستگی‌ها"):
            return False
    return True

def setup_django():
    """راه‌اندازی Django"""
    
    commands = [
        "cd /opt/vpn-service/services && python manage.py collectstatic --noinput",
        "cd /opt/vpn-service/services && python manage.py migrate",
        "cd /opt/vpn-service/services && python manage.py createsuperuser --noinput --username admin --email admin@example.com"
    ]
    
    for cmd in commands:
        if not run_command(cmd, "راه‌اندازی Django"):
            return False
    return True

def enable_services():
    """فعال‌سازی سرویس‌ها"""
    
    commands = [
        "systemctl daemon-reload",
        "systemctl enable django-vpn",
        "systemctl start django-vpn",
        "ln -sf /etc/nginx/sites-available/django-vpn /etc/nginx/sites-enabled/",
        "rm -f /etc/nginx/sites-enabled/default",
        "systemctl reload nginx",
        "systemctl enable nginx"
    ]
    
    for cmd in commands:
        if not run_command(cmd, "فعال‌سازی سرویس‌ها"):
            return False
    return True

def create_ssl_cert():
    """ایجاد گواهی SSL (اختیاری)"""
    
    print("🔐 آیا می‌خواهید SSL certificate ایجاد کنید؟ (y/n)")
    response = input().lower()
    
    if response == 'y':
        domain = input("🌐 نام دامنه را وارد کنید: ")
        commands = [
            f"certbot --nginx -d {domain} --non-interactive --agree-tos --email admin@{domain}",
            "systemctl reload nginx"
        ]
        
        for cmd in commands:
            run_command(cmd, "ایجاد SSL certificate")

def main():
    """تابع اصلی"""
    
    print("🚀 شروع راه‌اندازی کامل Django VPN Service")
    print("=" * 50)
    
    # بررسی root بودن
    if os.geteuid() != 0:
        print("❌ این اسکریپت باید با دسترسی root اجرا شود")
        sys.exit(1)
    
    steps = [
        ("نصب وابستگی‌ها", install_dependencies),
        ("راه‌اندازی دیتابیس", setup_database),
        ("ایجاد systemd service", create_systemd_service),
        ("ایجاد Nginx config", create_nginx_config),
        ("راه‌اندازی Django", setup_django),
        ("فعال‌سازی سرویس‌ها", enable_services)
    ]
    
    for step_name, step_func in steps:
        print(f"\n📋 مرحله: {step_name}")
        print("-" * 30)
        
        if not step_func():
            print(f"❌ خطا در مرحله: {step_name}")
            return False
    
    # ایجاد SSL (اختیاری)
    create_ssl_cert()
    
    print("\n🎉 راه‌اندازی کامل شد!")
    print("=" * 50)
    print("📊 وضعیت سرویس‌ها:")
    run_command("systemctl status django-vpn --no-pager -l", "وضعیت Django")
    run_command("systemctl status nginx --no-pager -l", "وضعیت Nginx")
    run_command("systemctl status postgresql --no-pager -l", "وضعیت PostgreSQL")
    run_command("systemctl status redis --no-pager -l", "وضعیت Redis")
    
    print("\n🌐 دسترسی‌ها:")
    print("   Django Admin: http://38.54.105.124/admin/")
    print("   X-UI Panel: http://38.54.105.124:54321/MsxZ4xuIy5xLfQtsSC/")
    print("   Django API: http://38.54.105.124:8000/")
    
    return True

if __name__ == "__main__":
    main() 