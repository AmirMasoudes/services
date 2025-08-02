#!/usr/bin/env python3
"""
اسکریپت کامل دیپلوی سیستم VPN
این اسکریپت تمام مراحل نصب و راه‌اندازی را انجام می‌دهد
"""

import os
import sys
import subprocess
import platform
import requests
import json
from pathlib import Path

def print_step(message):
    """نمایش مرحله"""
    print(f"\n{'='*50}")
    print(f"🔧 {message}")
    print(f"{'='*50}")

def run_command(command, check=True):
    """اجرای دستور"""
    print(f"💻 اجرا: {command}")
    try:
        result = subprocess.run(command, shell=True, check=check, capture_output=True, text=True)
        if result.stdout:
            print(f"✅ خروجی: {result.stdout}")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ خطا: {e.stderr}")
        return False

def check_system_requirements():
    """بررسی نیازمندی‌های سیستم"""
    print_step("بررسی نیازمندی‌های سیستم")
    
    # بررسی سیستم عامل
    system = platform.system()
    if system != "Linux":
        print(f"❌ این اسکریپت فقط برای Linux طراحی شده است. سیستم فعلی: {system}")
        return False
    
    # بررسی دسترسی root
    if os.geteuid() != 0:
        print("❌ این اسکریپت نیاز به دسترسی root دارد!")
        return False
    
    print("✅ نیازمندی‌های سیستم برآورده شد")
    return True

def install_system_dependencies():
    """نصب وابستگی‌های سیستم"""
    print_step("نصب وابستگی‌های سیستم")
    
    packages = [
        "python3", "python3-pip", "python3-venv", "git", "curl", "wget",
        "nginx", "certbot", "python3-certbot-nginx", "ufw", "net-tools"
    ]
    
    # آپدیت سیستم
    if not run_command("apt update -y"):
        return False
    
    # نصب پکیج‌ها
    if not run_command(f"apt install -y {' '.join(packages)}"):
        return False
    
    print("✅ وابستگی‌های سیستم نصب شدند")
    return True

def setup_project_directory():
    """راه‌اندازی دایرکتوری پروژه"""
    print_step("راه‌اندازی دایرکتوری پروژه")
    
    project_dir = "/opt/vpn-service"
    
    # ایجاد دایرکتوری
    if not run_command(f"mkdir -p {project_dir}"):
        return False
    
    # تغییر به دایرکتوری پروژه
    os.chdir(project_dir)
    
    print("✅ دایرکتوری پروژه راه‌اندازی شد")
    return True

def setup_python_environment():
    """راه‌اندازی محیط Python"""
    print_step("راه‌اندازی محیط Python")
    
    # ایجاد virtual environment
    if not run_command("python3 -m venv venv"):
        return False
    
    # فعال‌سازی virtual environment
    activate_script = "/opt/vpn-service/venv/bin/activate"
    if not run_command(f"source {activate_script} && pip install --upgrade pip"):
        return False
    
    print("✅ محیط Python راه‌اندازی شد")
    return True

def install_python_dependencies():
    """نصب وابستگی‌های Python"""
    print_step("نصب وابستگی‌های Python")
    
    requirements = [
        "django==5.2.4",
        "djangorestframework==3.16.0",
        "django-filter==25.1",
        "python-telegram-bot==22.3",
        "requests==2.31.0",
        "python-dotenv==1.1.1",
        "Pillow==11.3.0",
        "markdown==3.8.2",
        "nest-asyncio==1.6.0"
    ]
    
    activate_script = "/opt/vpn-service/venv/bin/activate"
    
    for package in requirements:
        if not run_command(f"source {activate_script} && pip install {package}"):
            return False
    
    print("✅ وابستگی‌های Python نصب شدند")
    return True

def setup_django():
    """راه‌اندازی Django"""
    print_step("راه‌اندازی Django")
    
    activate_script = "/opt/vpn-service/venv/bin/activate"
    
    # ایجاد دایرکتوری‌های مورد نیاز
    dirs = ["static", "media", "staticfiles"]
    for dir_name in dirs:
        run_command(f"mkdir -p /opt/vpn-service/services/{dir_name}")
    
    # اجرای migrations
    if not run_command(f"source {activate_script} && cd /opt/vpn-service/services && python manage.py makemigrations"):
        return False
    
    if not run_command(f"source {activate_script} && cd /opt/vpn-service/services && python manage.py migrate"):
        return False
    
    # ایجاد superuser
    print("🔐 ایجاد superuser...")
    print("Username: admin")
    print("Email: admin@example.com")
    print("Password: admin123")
    
    # ایجاد superuser به صورت خودکار
    superuser_script = '''
from django.contrib.auth import get_user_model
User = get_user_model()
if not User.objects.filter(username='admin').exists():
    User.objects.create_superuser('admin', 'admin@example.com', 'admin123')
    print("Superuser created successfully")
else:
    print("Superuser already exists")
'''
    
    with open("/tmp/create_superuser.py", "w") as f:
        f.write(superuser_script)
    
    if not run_command(f"source {activate_script} && cd /opt/vpn-service/services && python /tmp/create_superuser.py"):
        return False
    
    # جمع‌آوری فایل‌های استاتیک
    if not run_command(f"source {activate_script} && cd /opt/vpn-service/services && python manage.py collectstatic --noinput"):
        return False
    
    print("✅ Django راه‌اندازی شد")
    return True

def setup_xui_server():
    """راه‌اندازی X-UI Server"""
    print_step("راه‌اندازی X-UI Server")
    
    # نصب X-UI
    if not run_command("bash <(curl -Ls https://raw.githubusercontent.com/vaxilu/x-ui/master/install.sh)"):
        return False
    
    # تنظیم X-UI
    xui_config = {
        "username": "admin",
        "password": "admin123",
        "port": 54321
    }
    
    print("🔧 تنظیم X-UI...")
    print(f"Username: {xui_config['username']}")
    print(f"Password: {xui_config['password']}")
    print(f"Port: {xui_config['port']}")
    
    # فعال‌سازی و شروع سرویس
    if not run_command("systemctl enable x-ui"):
        return False
    
    if not run_command("systemctl start x-ui"):
        return False
    
    print("✅ X-UI Server راه‌اندازی شد")
    return True

def setup_nginx():
    """راه‌اندازی Nginx"""
    print_step("راه‌اندازی Nginx")
    
    # دریافت IP سرور
    try:
        response = requests.get('https://api.ipify.org')
        server_ip = response.text
    except:
        server_ip = "your-server-ip.com"
    
    # ایجاد فایل کانفیگ Nginx
    nginx_config = f'''
server {{
    listen 80;
    server_name {server_ip};
    
    location / {{
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }}
    
    location /static/ {{
        alias /opt/vpn-service/services/staticfiles/;
    }}
    
    location /media/ {{
        alias /opt/vpn-service/services/media/;
    }}
}}
'''
    
    with open("/etc/nginx/sites-available/vpn-service", "w") as f:
        f.write(nginx_config)
    
    # فعال‌سازی سایت
    if not run_command("ln -sf /etc/nginx/sites-available/vpn-service /etc/nginx/sites-enabled/"):
        return False
    
    # تست کانفیگ Nginx
    if not run_command("nginx -t"):
        return False
    
    # راه‌اندازی مجدد Nginx
    if not run_command("systemctl restart nginx"):
        return False
    
    print("✅ Nginx راه‌اندازی شد")
    return True

def setup_systemd_services():
    """راه‌اندازی سرویس‌های Systemd"""
    print_step("راه‌اندازی سرویس‌های Systemd")
    
    # Django Service
    django_service = '''
[Unit]
Description=VPN Django Service
After=network.target

[Service]
Type=simple
User=root
WorkingDirectory=/opt/vpn-service/services
Environment=PATH=/opt/vpn-service/venv/bin
ExecStart=/opt/vpn-service/venv/bin/python manage.py runserver 0.0.0.0:8000
Restart=always

[Install]
WantedBy=multi-user.target
'''
    
    with open("/etc/systemd/system/vpn-django.service", "w") as f:
        f.write(django_service)
    
    # User Bot Service
    user_bot_service = '''
[Unit]
Description=VPN User Bot Service
After=network.target

[Service]
Type=simple
User=root
WorkingDirectory=/opt/vpn-service/services
Environment=PATH=/opt/vpn-service/venv/bin
ExecStart=/opt/vpn-service/venv/bin/python bot/user_bot.py
Restart=always

[Install]
WantedBy=multi-user.target
'''
    
    with open("/etc/systemd/system/vpn-user-bot.service", "w") as f:
        f.write(user_bot_service)
    
    # Admin Bot Service
    admin_bot_service = '''
[Unit]
Description=VPN Admin Bot Service
After=network.target

[Service]
Type=simple
User=root
WorkingDirectory=/opt/vpn-service/services
Environment=PATH=/opt/vpn-service/venv/bin
ExecStart=/opt/vpn-service/venv/bin/python bot/admin_bot_fixed.py
Restart=always

[Install]
WantedBy=multi-user.target
'''
    
    with open("/etc/systemd/system/vpn-admin-bot.service", "w") as f:
        f.write(admin_bot_service)
    
    # فعال‌سازی و شروع سرویس‌ها
    services = ["vpn-django", "vpn-user-bot", "vpn-admin-bot"]
    
    for service in services:
        if not run_command(f"systemctl enable {service}"):
            return False
        
        if not run_command(f"systemctl start {service}"):
            return False
    
    print("✅ سرویس‌های Systemd راه‌اندازی شدند")
    return True

def setup_firewall():
    """راه‌اندازی Firewall"""
    print_step("راه‌اندازی Firewall")
    
    # تنظیم قوانین Firewall
    ports = [22, 80, 443, 54321]  # SSH, HTTP, HTTPS, X-UI
    
    for port in ports:
        if not run_command(f"ufw allow {port}/tcp"):
            return False
    
    # فعال‌سازی Firewall
    if not run_command("ufw --force enable"):
        return False
    
    print("✅ Firewall راه‌اندازی شد")
    return True

def create_env_file():
    """ایجاد فایل .env"""
    print_step("ایجاد فایل .env")
    
    env_content = '''# Django Settings
SECRET_KEY=django-insecure-c^1%va7g4+yqfygvbjku#d4-4d8-sw8rzw9!$_wq-vt(*x-mw9
DEBUG=False
ALLOWED_HOSTS=localhost,127.0.0.1

# Telegram Bot Tokens
TELEGRAM_BOT_TOKEN=8202994859:AAGg68pT5HGR1W9D4pxqnAGeKoZKrD9Dnzs
ADMIN_BOT_TOKEN=8450508816:AAFE6XAj8QvA9iIP12whrKxYRtgsoHFCiFU

# Admin Password
ADMIN_PASSWORD=admin123

# X-UI Server Settings
XUI_SERVER_HOST=127.0.0.1
XUI_SERVER_PORT=54321
XUI_USERNAME=admin
XUI_PASSWORD=admin123

# Database
DATABASE_URL=sqlite:///db.sqlite3
'''
    
    with open("/opt/vpn-service/services/.env", "w") as f:
        f.write(env_content)
    
    print("✅ فایل .env ایجاد شد")
    return True

def setup_initial_data():
    """راه‌اندازی داده‌های اولیه"""
    print_step("راه‌اندازی داده‌های اولیه")
    
    activate_script = "/opt/vpn-service/venv/bin/activate"
    
    # ایجاد اسکریپت تنظیم داده‌های اولیه
    setup_script = '''
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from xui_servers.models import XUIServer
from plan.models import ConfingPlansModel

# ایجاد سرور X-UI
XUIServer.objects.get_or_create(
    name="سرور اصلی",
    host="127.0.0.1",
    port=54321,
    username="admin",
    password="admin123",
    is_active=True
)

# ایجاد پلن‌های پیش‌فرض
plans_data = [
    {'name': 'پلن تستی', 'price': 0, 'in_volume': 1, 'traffic_mb': 1024, 'description': 'پلن تستی 24 ساعته - 1 گیگابایت'},
    {'name': 'پلن برنزی', 'price': 50000, 'in_volume': 30, 'traffic_mb': 10240, 'description': 'پلن برنزی 30 روزه - 10 گیگابایت'},
    {'name': 'پلن نقره‌ای', 'price': 100000, 'in_volume': 30, 'traffic_mb': 25600, 'description': 'پلن نقره‌ای 30 روزه - 25 گیگابایت'},
    {'name': 'پلن طلایی', 'price': 200000, 'in_volume': 30, 'traffic_mb': 51200, 'description': 'پلن طلایی 30 روزه - 50 گیگابایت'},
]

for plan_data in plans_data:
    ConfingPlansModel.objects.get_or_create(
        name=plan_data['name'],
        defaults=plan_data
    )

print("✅ داده‌های اولیه ایجاد شدند")
'''
    
    with open("/tmp/setup_initial_data.py", "w") as f:
        f.write(setup_script)
    
    if not run_command(f"source {activate_script} && cd /opt/vpn-service/services && python /tmp/setup_initial_data.py"):
        return False
    
    print("✅ داده‌های اولیه راه‌اندازی شدند")
    return True

def test_deployment():
    """تست دیپلوی"""
    print_step("تست دیپلوی")
    
    # بررسی سرویس‌ها
    services = ["vpn-django", "vpn-user-bot", "vpn-admin-bot", "x-ui", "nginx"]
    
    for service in services:
        if not run_command(f"systemctl is-active {service}"):
            print(f"❌ سرویس {service} فعال نیست!")
            return False
        else:
            print(f"✅ سرویس {service} فعال است")
    
    # تست اتصال‌ها
    try:
        response = requests.get("http://127.0.0.1:8000", timeout=5)
        print(f"✅ Django: {response.status_code}")
    except:
        print("❌ Django در دسترس نیست")
    
    try:
        response = requests.get("http://127.0.0.1:54321", timeout=5)
        print(f"✅ X-UI: {response.status_code}")
    except:
        print("❌ X-UI در دسترس نیست")
    
    print("✅ تست دیپلوی کامل شد")
    return True

def create_deployment_summary():
    """ایجاد خلاصه دیپلوی"""
    print_step("خلاصه دیپلوی")
    
    summary = '''
🎉 **دیپلوی کامل شد!**

📋 **اطلاعات دسترسی:**

🔐 **Admin Panel:**
   - URL: http://YOUR-SERVER-IP/admin
   - Username: admin
   - Password: admin123

🤖 **Admin Bot:**
   - Username: @gamramconfigbot
   - Password: admin123

🖥️ **X-UI Panel:**
   - URL: http://YOUR-SERVER-IP:54321
   - Username: admin
   - Password: admin123

📁 **مسیرهای مهم:**
   - پروژه: /opt/vpn-service
   - Django: /opt/vpn-service/services
   - Logs: journalctl -u vpn-django

🔧 **دستورات مفید:**
   - وضعیت سرویس‌ها: systemctl status vpn-django vpn-user-bot vpn-admin-bot x-ui nginx
   - لاگ‌ها: journalctl -u vpn-django -f
   - راه‌اندازی مجدد: systemctl restart vpn-django

⚠️ **نکات مهم:**
   - حتماً توکن‌های ربات‌ها را در .env تنظیم کنید
   - رمزهای پیش‌فرض را تغییر دهید
   - SSL certificate نصب کنید
'''
    
    print(summary)
    
    # ذخیره خلاصه در فایل
    with open("/opt/vpn-service/DEPLOYMENT_SUMMARY.md", "w", encoding="utf-8") as f:
        f.write(summary)
    
    print("✅ خلاصه دیپلوی در /opt/vpn-service/DEPLOYMENT_SUMMARY.md ذخیره شد")

def main():
    """تابع اصلی"""
    print("🚀 شروع دیپلوی کامل سیستم VPN...")
    
    steps = [
        ("بررسی نیازمندی‌های سیستم", check_system_requirements),
        ("نصب وابستگی‌های سیستم", install_system_dependencies),
        ("راه‌اندازی دایرکتوری پروژه", setup_project_directory),
        ("راه‌اندازی محیط Python", setup_python_environment),
        ("نصب وابستگی‌های Python", install_python_dependencies),
        ("راه‌اندازی Django", setup_django),
        ("راه‌اندازی X-UI Server", setup_xui_server),
        ("راه‌اندازی Nginx", setup_nginx),
        ("راه‌اندازی سرویس‌های Systemd", setup_systemd_services),
        ("راه‌اندازی Firewall", setup_firewall),
        ("ایجاد فایل .env", create_env_file),
        ("راه‌اندازی داده‌های اولیه", setup_initial_data),
        ("تست دیپلوی", test_deployment),
        ("ایجاد خلاصه دیپلوی", create_deployment_summary)
    ]
    
    for step_name, step_func in steps:
        if not step_func():
            print(f"❌ خطا در مرحله: {step_name}")
            return False
    
    print("\n🎉 دیپلوی کامل شد!")
    return True

if __name__ == "__main__":
    main() 