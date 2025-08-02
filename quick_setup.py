#!/usr/bin/env python3
"""
اسکریپت راه‌اندازی سریع Django VPN Service
"""

import os
import subprocess
import sys

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

def main():
    print("🚀 راه‌اندازی سریع Django VPN Service")
    print("=" * 40)
    
    # 1. نصب وابستگی‌ها
    print("\n📦 نصب وابستگی‌ها...")
    run_cmd("apt update", "Update package list")
    run_cmd("apt install -y nginx postgresql postgresql-contrib redis-server", "Install dependencies")
    
    # 2. راه‌اندازی PostgreSQL
    print("\n🗄️ راه‌اندازی PostgreSQL...")
    run_cmd("systemctl enable postgresql", "Enable PostgreSQL")
    run_cmd("systemctl start postgresql", "Start PostgreSQL")
    run_cmd('sudo -u postgres psql -c "CREATE DATABASE configvpn_db;"', "Create database")
    run_cmd('sudo -u postgres psql -c "CREATE USER configvpn_user WITH PASSWORD \'YourSecurePassword123!@#\';"', "Create user")
    run_cmd('sudo -u postgres psql -c "GRANT ALL PRIVILEGES ON DATABASE configvpn_db TO configvpn_user;"', "Grant privileges")
    
    # 3. راه‌اندازی Redis
    print("\n🔴 راه‌اندازی Redis...")
    run_cmd("systemctl enable redis", "Enable Redis")
    run_cmd("systemctl start redis", "Start Redis")
    
    # 4. Django setup
    print("\n🐍 راه‌اندازی Django...")
    run_cmd("cd /opt/vpn-service/services && python manage.py collectstatic --noinput", "Collect static files")
    run_cmd("cd /opt/vpn-service/services && python manage.py migrate", "Run migrations")
    
    # 5. ایجاد systemd service
    print("\n⚙️ ایجاد systemd service...")
    service_content = """[Unit]
Description=Django VPN Service
After=network.target

[Service]
Type=simple
User=root
WorkingDirectory=/opt/vpn-service/services
ExecStart=/opt/vpn-service/services/venv/bin/python manage.py runserver 0.0.0.0:8000
Restart=always

[Install]
WantedBy=multi-user.target
"""
    
    with open("/etc/systemd/system/django-vpn.service", "w") as f:
        f.write(service_content)
    
    # 6. فعال‌سازی سرویس
    print("\n🚀 فعال‌سازی سرویس...")
    run_cmd("systemctl daemon-reload", "Reload systemd")
    run_cmd("systemctl enable django-vpn", "Enable Django service")
    run_cmd("systemctl start django-vpn", "Start Django service")
    
    # 7. تنظیم Nginx
    print("\n🌐 تنظیم Nginx...")
    nginx_config = """server {
    listen 80;
    server_name 38.54.105.124;
    
    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
    
    location /xui/ {
        proxy_pass http://127.0.0.1:54321/MsxZ4xuIy5xLfQtsSC/;
        proxy_set_header Host $host;
    }
}"""
    
    with open("/etc/nginx/sites-available/django-vpn", "w") as f:
        f.write(nginx_config)
    
    run_cmd("ln -sf /etc/nginx/sites-available/django-vpn /etc/nginx/sites-enabled/", "Enable Nginx site")
    run_cmd("rm -f /etc/nginx/sites-enabled/default", "Remove default site")
    run_cmd("systemctl reload nginx", "Reload Nginx")
    
    print("\n🎉 راه‌اندازی کامل شد!")
    print("=" * 40)
    print("🌐 دسترسی‌ها:")
    print("   Django Admin: http://38.54.105.124/admin/")
    print("   X-UI Panel: http://38.54.105.124:54321/MsxZ4xuIy5xLfQtsSC/")
    print("   Django API: http://38.54.105.124:8000/")
    
    print("\n📊 وضعیت سرویس‌ها:")
    run_cmd("systemctl status django-vpn --no-pager -l", "Django status")
    run_cmd("systemctl status nginx --no-pager -l", "Nginx status")

if __name__ == "__main__":
    main() 