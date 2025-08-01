#!/usr/bin/env python3
"""
اسکریپت کامل دیپلوی سرویس VPN
این اسکریپت تمام مراحل نصب و راه‌اندازی را انجام می‌دهد
"""

import os
import sys
import subprocess
import platform
import json
import requests
from pathlib import Path

# تنظیمات سرور
SERVER_CONFIG = {
    "django_secret_key": "django-insecure-c^1%va7g4+yqfygvbjku#d4-4d8-sw8rzw9!$_wq-vt(*x-mw9",
    "allowed_hosts": ["*"],
    "debug": False,
    "database": "sqlite3",  # یا postgresql برای production
    "xui_port": 54321,
    "bot_tokens": {
        "user_bot": "8202994859:AAGg68pT5HGR1W9D4pxqnAGeKoZKrD9Dnzs",
        "admin_bot": "8450508816:AAFE6XAj8QvA9iIP12whrKxYRtgsoHFCiFU"
    }
}

def check_system_requirements():
    """بررسی نیازمندی‌های سیستم"""
    print("🔍 بررسی نیازمندی‌های سیستم...")
    
    # بررسی Python
    python_version = sys.version_info
    if python_version.major < 3 or (python_version.major == 3 and python_version.minor < 8):
        print("❌ Python 3.8 یا بالاتر مورد نیاز است")
        return False
    print(f"✅ Python {python_version.major}.{python_version.minor}.{python_version.micro}")
    
    # بررسی سیستم عامل
    system = platform.system()
    if system not in ["Linux", "Windows", "Darwin"]:
        print(f"⚠️ سیستم عامل {system} پشتیبانی نمی‌شود")
    else:
        print(f"✅ سیستم عامل: {system}")
    
    # بررسی دسترسی به اینترنت
    try:
        response = requests.get("https://www.google.com", timeout=5)
        print("✅ اتصال به اینترنت")
    except:
        print("❌ خطا در اتصال به اینترنت")
        return False
    
    return True

def install_system_dependencies():
    """نصب وابستگی‌های سیستم"""
    print("📦 نصب وابستگی‌های سیستم...")
    
    system = platform.system()
    
    if system == "Linux":
        # نصب وابستگی‌های Ubuntu/Debian
        packages = [
            "python3-pip",
            "python3-venv",
            "git",
            "curl",
            "wget",
            "nginx",
            "certbot",
            "python3-certbot-nginx"
        ]
        
        try:
            subprocess.run(["sudo", "apt", "update"], check=True)
            subprocess.run(["sudo", "apt", "install", "-y"] + packages, check=True)
            print("✅ وابستگی‌های سیستم نصب شدند")
        except subprocess.CalledProcessError as e:
            print(f"❌ خطا در نصب وابستگی‌ها: {e}")
            return False
    
    elif system == "Windows":
        print("ℹ️ در ویندوز، لطفا دستی نصب کنید:")
        print("  - Python 3.8+")
        print("  - Git")
        print("  - Visual Studio Build Tools")
    
    return True

def setup_python_environment():
    """راه‌اندازی محیط Python"""
    print("🐍 راه‌اندازی محیط Python...")
    
    # ایجاد virtual environment
    if not os.path.exists("venv"):
        try:
            subprocess.run([sys.executable, "-m", "venv", "venv"], check=True)
            print("✅ Virtual environment ایجاد شد")
        except subprocess.CalledProcessError as e:
            print(f"❌ خطا در ایجاد virtual environment: {e}")
            return False
    
    # فعال‌سازی virtual environment
    if platform.system() == "Windows":
        activate_script = "venv\\Scripts\\activate"
    else:
        activate_script = "venv/bin/activate"
    
    print("✅ Virtual environment آماده است")
    return True

def install_python_dependencies():
    """نصب وابستگی‌های Python"""
    print("📦 نصب وابستگی‌های Python...")
    
    try:
        # نصب pip در virtual environment
        if platform.system() == "Windows":
            pip_cmd = ["venv\\Scripts\\python.exe", "-m", "pip", "install", "--upgrade", "pip"]
        else:
            pip_cmd = ["venv/bin/pip", "install", "--upgrade", "pip"]
        
        subprocess.run(pip_cmd, check=True)
        
        # نصب وابستگی‌ها
        if platform.system() == "Windows":
            pip_cmd = ["venv\\Scripts\\python.exe", "-m", "pip", "install", "-r", "requirements.txt"]
        else:
            pip_cmd = ["venv/bin/pip", "install", "-r", "requirements.txt"]
        
        subprocess.run(pip_cmd, check=True)
        print("✅ وابستگی‌های Python نصب شدند")
        return True
        
    except subprocess.CalledProcessError as e:
        print(f"❌ خطا در نصب وابستگی‌ها: {e}")
        return False

def setup_django():
    """راه‌اندازی Django"""
    print("⚙️ راه‌اندازی Django...")
    
    try:
        # تنظیم متغیرهای محیطی
        os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
        
        # اجرای migrations
        if platform.system() == "Windows":
            python_cmd = ["venv\\Scripts\\python.exe"]
        else:
            python_cmd = ["venv/bin/python"]
        
        subprocess.run(python_cmd + ["manage.py", "makemigrations"], check=True)
        subprocess.run(python_cmd + ["manage.py", "migrate"], check=True)
        
        # ایجاد superuser
        print("👤 ایجاد کاربر ادمین...")
        subprocess.run(python_cmd + ["manage.py", "createsuperuser", "--noinput"], 
                      env={**os.environ, "DJANGO_SUPERUSER_USERNAME": "admin", 
                           "DJANGO_SUPERUSER_EMAIL": "admin@example.com",
                           "DJANGO_SUPERUSER_PASSWORD": "admin123"})
        
        print("✅ Django راه‌اندازی شد")
        return True
        
    except subprocess.CalledProcessError as e:
        print(f"❌ خطا در راه‌اندازی Django: {e}")
        return False

def setup_xui_server():
    """راه‌اندازی سرور X-UI"""
    print("🖥️ راه‌اندازی سرور X-UI...")
    
    try:
        if platform.system() == "Windows":
            python_cmd = ["venv\\Scripts\\python.exe"]
        else:
            python_cmd = ["venv/bin/python"]
        
        # اجرای اسکریپت راه‌اندازی X-UI
        subprocess.run(python_cmd + ["setup_xui_server.py"], check=True)
        
        print("✅ سرور X-UI راه‌اندازی شد")
        return True
        
    except subprocess.CalledProcessError as e:
        print(f"❌ خطا در راه‌اندازی X-UI: {e}")
        return False

def setup_nginx():
    """راه‌اندازی Nginx"""
    print("🌐 راه‌اندازی Nginx...")
    
    if platform.system() != "Linux":
        print("ℹ️ Nginx فقط در Linux پشتیبانی می‌شود")
        return True
    
    try:
        # ایجاد فایل تنظیمات Nginx
        nginx_config = """
server {
    listen 80;
    server_name your-domain.com;
    
    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
    
    location /static/ {
        alias /path/to/your/project/staticfiles/;
    }
}
"""
        
        # ذخیره فایل تنظیمات
        with open("/etc/nginx/sites-available/vpn-bot", "w") as f:
            f.write(nginx_config)
        
        # فعال‌سازی سایت
        subprocess.run(["sudo", "ln", "-s", "/etc/nginx/sites-available/vpn-bot", 
                       "/etc/nginx/sites-enabled/"], check=True)
        
        # تست تنظیمات
        subprocess.run(["sudo", "nginx", "-t"], check=True)
        
        # راه‌اندازی مجدد Nginx
        subprocess.run(["sudo", "systemctl", "restart", "nginx"], check=True)
        
        print("✅ Nginx راه‌اندازی شد")
        return True
        
    except subprocess.CalledProcessError as e:
        print(f"❌ خطا در راه‌اندازی Nginx: {e}")
        return False

def setup_ssl_certificate():
    """راه‌اندازی گواهی SSL"""
    print("🔒 راه‌اندازی گواهی SSL...")
    
    if platform.system() != "Linux":
        print("ℹ️ SSL فقط در Linux پشتیبانی می‌شود")
        return True
    
    try:
        # نصب گواهی SSL با Let's Encrypt
        subprocess.run(["sudo", "certbot", "--nginx", "-d", "your-domain.com"], check=True)
        
        print("✅ گواهی SSL نصب شد")
        return True
        
    except subprocess.CalledProcessError as e:
        print(f"❌ خطا در نصب SSL: {e}")
        return False

def create_systemd_service():
    """ایجاد سرویس systemd"""
    print("🔧 ایجاد سرویس systemd...")
    
    if platform.system() != "Linux":
        print("ℹ️ systemd فقط در Linux پشتیبانی می‌شود")
        return True
    
    try:
        service_config = """
[Unit]
Description=VPN Bot Service
After=network.target

[Service]
Type=simple
User=www-data
Group=www-data
WorkingDirectory=/path/to/your/project
Environment=PATH=/path/to/your/project/venv/bin
ExecStart=/path/to/your/project/venv/bin/python manage.py runserver 0.0.0.0:8000
Restart=always

[Install]
WantedBy=multi-user.target
"""
        
        # ذخیره فایل سرویس
        with open("/etc/systemd/system/vpn-bot.service", "w") as f:
            f.write(service_config)
        
        # فعال‌سازی سرویس
        subprocess.run(["sudo", "systemctl", "daemon-reload"], check=True)
        subprocess.run(["sudo", "systemctl", "enable", "vpn-bot"], check=True)
        subprocess.run(["sudo", "systemctl", "start", "vpn-bot"], check=True)
        
        print("✅ سرویس systemd ایجاد شد")
        return True
        
    except subprocess.CalledProcessError as e:
        print(f"❌ خطا در ایجاد سرویس: {e}")
        return False

def setup_firewall():
    """راه‌اندازی فایروال"""
    print("🔥 راه‌اندازی فایروال...")
    
    if platform.system() != "Linux":
        print("ℹ️ فایروال فقط در Linux پشتیبانی می‌شود")
        return True
    
    try:
        # باز کردن پورت‌های مورد نیاز
        ports = [22, 80, 443, 8000, 54321]  # SSH, HTTP, HTTPS, Django, X-UI
        
        for port in ports:
            subprocess.run(["sudo", "ufw", "allow", str(port)], check=True)
        
        # فعال‌سازی فایروال
        subprocess.run(["sudo", "ufw", "--force", "enable"], check=True)
        
        print("✅ فایروال راه‌اندازی شد")
        return True
        
    except subprocess.CalledProcessError as e:
        print(f"❌ خطا در راه‌اندازی فایروال: {e}")
        return False

def test_deployment():
    """تست دیپلوی"""
    print("🧪 تست دیپلوی...")
    
    try:
        # تست Django
        if platform.system() == "Windows":
            python_cmd = ["venv\\Scripts\\python.exe"]
        else:
            python_cmd = ["venv/bin/python"]
        
        result = subprocess.run(python_cmd + ["manage.py", "check"], 
                              capture_output=True, text=True)
        
        if result.returncode == 0:
            print("✅ Django سالم است")
        else:
            print(f"❌ خطا در Django: {result.stderr}")
            return False
        
        # تست اتصال به X-UI
        try:
            response = requests.get("http://127.0.0.1:54321", timeout=5)
            print("✅ اتصال به X-UI موفق است")
        except:
            print("⚠️ اتصال به X-UI ناموفق است")
        
        print("✅ تست دیپلوی کامل شد")
        return True
        
    except Exception as e:
        print(f"❌ خطا در تست دیپلوی: {e}")
        return False

def create_deployment_summary():
    """ایجاد خلاصه دیپلوی"""
    print("📋 ایجاد خلاصه دیپلوی...")
    
    summary = {
        "deployment_status": "success",
        "system_info": {
            "platform": platform.system(),
            "python_version": f"{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}",
            "architecture": platform.architecture()[0]
        },
        "services": {
            "django": "running",
            "xui": "configured",
            "nginx": "configured" if platform.system() == "Linux" else "not_applicable",
            "ssl": "configured" if platform.system() == "Linux" else "not_applicable",
            "firewall": "configured" if platform.system() == "Linux" else "not_applicable"
        },
        "next_steps": [
            "تنظیم دامنه در فایل‌های تنظیمات",
            "تست ربات‌های تلگرام",
            "بررسی امنیت سرور",
            "تنظیم backup خودکار"
        ]
    }
    
    # ذخیره خلاصه
    with open("deployment_summary.json", "w", encoding="utf-8") as f:
        json.dump(summary, f, indent=2, ensure_ascii=False)
    
    print("✅ خلاصه دیپلوی ایجاد شد")

def main():
    """تابع اصلی دیپلوی"""
    print("=" * 60)
    print("🚀 شروع دیپلوی سرویس VPN")
    print("=" * 60)
    
    steps = [
        ("بررسی نیازمندی‌های سیستم", check_system_requirements),
        ("نصب وابستگی‌های سیستم", install_system_dependencies),
        ("راه‌اندازی محیط Python", setup_python_environment),
        ("نصب وابستگی‌های Python", install_python_dependencies),
        ("راه‌اندازی Django", setup_django),
        ("راه‌اندازی سرور X-UI", setup_xui_server),
        ("راه‌اندازی Nginx", setup_nginx),
        ("راه‌اندازی SSL", setup_ssl_certificate),
        ("ایجاد سرویس systemd", create_systemd_service),
        ("راه‌اندازی فایروال", setup_firewall),
        ("تست دیپلوی", test_deployment),
        ("ایجاد خلاصه دیپلوی", create_deployment_summary)
    ]
    
    for step_name, step_func in steps:
        print(f"\n📋 {step_name}...")
        if not step_func():
            print(f"❌ خطا در {step_name}")
            return False
        print(f"✅ {step_name} تکمیل شد")
    
    print("\n" + "=" * 60)
    print("🎉 دیپلوی با موفقیت تکمیل شد!")
    print("=" * 60)
    print("\n📋 مراحل بعدی:")
    print("1. تنظیم دامنه در فایل‌های تنظیمات")
    print("2. تست ربات‌های تلگرام")
    print("3. بررسی امنیت سرور")
    print("4. تنظیم backup خودکار")
    print("\n🤖 برای اجرای ربات‌ها:")
    print("python bot/user_bot.py")
    print("python bot/admin_boy.py")
    print("=" * 60)
    
    return True

if __name__ == "__main__":
    try:
        success = main()
        if success:
            print("\n✅ دیپلوی موفقیت‌آمیز بود!")
        else:
            print("\n❌ دیپلوی با خطا مواجه شد!")
            sys.exit(1)
    except KeyboardInterrupt:
        print("\n⚠️ دیپلوی توسط کاربر متوقف شد!")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ خطای غیرمنتظره: {e}")
        sys.exit(1) 