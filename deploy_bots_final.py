#!/usr/bin/env python3
"""
اسکریپت نهایی دیپلوی ربات‌های تلگرام
"""

import os
import sys
import subprocess
import time
import shutil
from pathlib import Path

def setup_environment():
    """تنظیم محیط"""
    print("🔧 تنظیم محیط...")
    
    # ایجاد فایل .env اگر وجود ندارد
    if not os.path.exists('.env'):
        if os.path.exists('env_example.txt'):
            shutil.copy('env_example.txt', '.env')
            print("✅ فایل .env از env_example.txt ایجاد شد")
        else:
            print("⚠️ فایل env_example.txt یافت نشد")
            print("💡 لطفاً فایل .env را دستی ایجاد کنید")
    
    # بررسی وجود فایل .env
    if not os.path.exists('.env'):
        print("❌ فایل .env یافت نشد")
        return False
    
    print("✅ محیط تنظیم شد")
    return True

def install_dependencies():
    """نصب وابستگی‌ها"""
    print("📦 نصب وابستگی‌ها...")
    
    required_packages = [
        'python-telegram-bot',
        'django',
        'python-dotenv',
        'psutil',
        'requests'
    ]
    
    for package in required_packages:
        try:
            print(f"📦 نصب {package}...")
            subprocess.run([sys.executable, '-m', 'pip', 'install', package], 
                         check=True, capture_output=True)
            print(f"✅ {package} نصب شد")
        except subprocess.CalledProcessError as e:
            print(f"❌ خطا در نصب {package}: {e}")
            return False
    
    print("✅ تمام وابستگی‌ها نصب شدند")
    return True

def setup_django():
    """تنظیم Django"""
    print("🔧 تنظیم Django...")
    
    try:
        # اجرای migrations
        subprocess.run([sys.executable, 'manage.py', 'makemigrations'], 
                      check=True, capture_output=True)
        print("✅ makemigrations اجرا شد")
        
        subprocess.run([sys.executable, 'manage.py', 'migrate'], 
                      check=True, capture_output=True)
        print("✅ migrate اجرا شد")
        
        # ایجاد superuser اگر وجود ندارد
        try:
            subprocess.run([sys.executable, 'manage.py', 'createsuperuser', '--noinput'], 
                          check=True, capture_output=True)
            print("✅ superuser ایجاد شد")
        except subprocess.CalledProcessError:
            print("⚠️ superuser قبلاً وجود دارد")
        
        print("✅ Django تنظیم شد")
        return True
        
    except subprocess.CalledProcessError as e:
        print(f"❌ خطا در تنظیم Django: {e}")
        return False

def create_bot_services():
    """ایجاد سرویس‌های systemd"""
    print("🔧 ایجاد سرویس‌های systemd...")
    
    if os.geteuid() != 0:
        print("⚠️ برای ایجاد سرویس‌ها نیاز به دسترسی root است")
        print("💡 می‌توانید از اسکریپت‌های راه‌اندازی استفاده کنید")
        return True
    
    project_path = os.getcwd()
    
    # سرویس ربات کاربر
    user_bot_service = f"""[Unit]
Description=VPN User Bot
After=network.target

[Service]
Type=simple
User=root
WorkingDirectory={project_path}
Environment=PYTHONPATH={project_path}
ExecStart={sys.executable} {project_path}/bot/user_bot.py
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
"""
    
    # سرویس ربات ادمین
    admin_bot_service = f"""[Unit]
Description=VPN Admin Bot
After=network.target

[Service]
Type=simple
User=root
WorkingDirectory={project_path}
Environment=PYTHONPATH={project_path}
ExecStart={sys.executable} {project_path}/bot/admin_boy.py
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
"""
    
    try:
        # نوشتن فایل‌های سرویس
        with open('/etc/systemd/system/vpn-user-bot.service', 'w') as f:
            f.write(user_bot_service)
        
        with open('/etc/systemd/system/vpn-admin-bot.service', 'w') as f:
            f.write(admin_bot_service)
        
        print("✅ فایل‌های سرویس ایجاد شدند")
        return True
        
    except Exception as e:
        print(f"❌ خطا در ایجاد سرویس‌ها: {e}")
        return False

def start_services():
    """راه‌اندازی سرویس‌ها"""
    print("🚀 راه‌اندازی سرویس‌ها...")
    
    if os.geteuid() != 0:
        print("⚠️ برای راه‌اندازی سرویس‌ها نیاز به دسترسی root است")
        return True
    
    try:
        # Reload systemd
        subprocess.run(['systemctl', 'daemon-reload'], check=True)
        
        # Enable services
        subprocess.run(['systemctl', 'enable', 'vpn-user-bot.service'], check=True)
        subprocess.run(['systemctl', 'enable', 'vpn-admin-bot.service'], check=True)
        
        # Start services
        subprocess.run(['systemctl', 'start', 'vpn-user-bot.service'], check=True)
        subprocess.run(['systemctl', 'start', 'vpn-admin-bot.service'], check=True)
        
        print("✅ سرویس‌ها راه‌اندازی شدند")
        return True
        
    except subprocess.CalledProcessError as e:
        print(f"❌ خطا در راه‌اندازی سرویس‌ها: {e}")
        return False

def check_status():
    """بررسی وضعیت"""
    print("🔍 بررسی وضعیت...")
    
    if os.geteuid() == 0:
        services = ['vpn-user-bot.service', 'vpn-admin-bot.service']
        
        for service in services:
            try:
                result = subprocess.run(['systemctl', 'is-active', service], 
                                      capture_output=True, text=True)
                status = result.stdout.strip()
                
                if status == 'active':
                    print(f"✅ {service}: فعال")
                else:
                    print(f"❌ {service}: غیرفعال ({status})")
                    
            except Exception as e:
                print(f"❌ خطا در بررسی {service}: {e}")
    else:
        print("💡 برای بررسی وضعیت سرویس‌ها از دستورات زیر استفاده کنید:")
        print("   systemctl status vpn-user-bot.service")
        print("   systemctl status vpn-admin-bot.service")

def create_launcher_scripts():
    """ایجاد اسکریپت‌های راه‌اندازی"""
    print("🚀 ایجاد اسکریپت‌های راه‌اندازی...")
    
    # اسکریپت راه‌اندازی
    start_script = """#!/bin/bash
# اسکریپت راه‌اندازی ربات‌های تلگرام

PROJECT_PATH="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$PROJECT_PATH"

# بارگذاری متغیرهای محیطی
if [ -f ".env" ]; then
    export $(cat .env | grep -v '^#' | xargs)
fi

# بررسی وجود توکن‌ها
if [ -z "$USER_BOT_TOKEN" ]; then
    echo "❌ USER_BOT_TOKEN تعریف نشده است"
    exit 1
fi

if [ -z "$ADMIN_BOT_TOKEN" ]; then
    echo "❌ ADMIN_BOT_TOKEN تعریف نشده است"
    exit 1
fi

echo "🚀 راه‌اندازی ربات‌های تلگرام..."

# راه‌اندازی ربات کاربر
echo "🤖 راه‌اندازی ربات کاربر..."
python3 bot/user_bot.py &
USER_BOT_PID=$!

# راه‌اندازی ربات ادمین
echo "👨‍💼 راه‌اندازی ربات ادمین..."
python3 bot/admin_boy.py &
ADMIN_BOT_PID=$!

echo "✅ ربات‌ها راه‌اندازی شدند:"
echo "   - ربات کاربر: PID $USER_BOT_PID"
echo "   - ربات ادمین: PID $ADMIN_BOT_PID"

# ذخیره PID ها
echo $USER_BOT_PID > .user_bot.pid
echo $ADMIN_BOT_PID > .admin_bot.pid

# انتظار برای سیگنال توقف
trap 'echo "🛑 توقف ربات‌ها..."; kill $USER_BOT_PID $ADMIN_BOT_PID; exit 0' SIGTERM SIGINT

# انتظار
wait
"""
    
    # اسکریپت توقف
    stop_script = """#!/bin/bash
# اسکریپت توقف ربات‌های تلگرام

PROJECT_PATH="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$PROJECT_PATH"

echo "🛑 توقف ربات‌های تلگرام..."

# توقف ربات کاربر
if [ -f ".user_bot.pid" ]; then
    USER_BOT_PID=$(cat .user_bot.pid)
    if kill -0 $USER_BOT_PID 2>/dev/null; then
        echo "🛑 توقف ربات کاربر (PID: $USER_BOT_PID)..."
        kill $USER_BOT_PID
        rm .user_bot.pid
    else
        echo "❌ ربات کاربر در حال اجرا نیست"
    fi
else
    echo "❌ فایل PID ربات کاربر یافت نشد"
fi

# توقف ربات ادمین
if [ -f ".admin_bot.pid" ]; then
    ADMIN_BOT_PID=$(cat .admin_bot.pid)
    if kill -0 $ADMIN_BOT_PID 2>/dev/null; then
        echo "🛑 توقف ربات ادمین (PID: $ADMIN_BOT_PID)..."
        kill $ADMIN_BOT_PID
        rm .admin_bot.pid
    else
        echo "❌ ربات ادمین در حال اجرا نیست"
    fi
else
    echo "❌ فایل PID ربات ادمین یافت نشد"
fi

echo "✅ ربات‌ها متوقف شدند"
"""
    
    try:
        # نوشتن اسکریپت‌ها
        with open('start_bots.sh', 'w') as f:
            f.write(start_script)
        
        with open('stop_bots.sh', 'w') as f:
            f.write(stop_script)
        
        # اعطای مجوز اجرا
        os.chmod('start_bots.sh', 0o755)
        os.chmod('stop_bots.sh', 0o755)
        
        print("✅ اسکریپت‌های راه‌اندازی ایجاد شدند")
        return True
        
    except Exception as e:
        print(f"❌ خطا در ایجاد اسکریپت‌ها: {e}")
        return False

def show_final_info():
    """نمایش اطلاعات نهایی"""
    print("\n🎉 دیپلوی ربات‌ها کامل شد!")
    print("=" * 50)
    
    print("\n📋 اطلاعات مهم:")
    print("   - فایل تنظیمات: .env")
    print("   - ربات کاربر: bot/user_bot.py")
    print("   - ربات ادمین: bot/admin_boy.py")
    
    print("\n🚀 دستورات راه‌اندازی:")
    print("   # روش 1: اسکریپت راه‌اندازی")
    print("   ./start_bots.sh")
    print("   ./stop_bots.sh")
    
    print("\n   # روش 2: systemd (اگر root هستید)")
    print("   systemctl start vpn-user-bot.service")
    print("   systemctl start vpn-admin-bot.service")
    print("   systemctl stop vpn-user-bot.service")
    print("   systemctl stop vpn-admin-bot.service")
    
    print("\n   # روش 3: مستقیم")
    print("   python bot/user_bot.py &")
    print("   python bot/admin_boy.py &")
    
    print("\n🔍 دستورات بررسی:")
    print("   # وضعیت سرویس‌ها")
    print("   systemctl status vpn-user-bot.service")
    print("   systemctl status vpn-admin-bot.service")
    
    print("\n   # مشاهده لاگ‌ها")
    print("   journalctl -u vpn-user-bot.service -f")
    print("   journalctl -u vpn-admin-bot.service -f")
    
    print("\n📝 نکات مهم:")
    print("   1. توکن‌های ربات را در فایل .env تنظیم کنید")
    print("   2. رمز عبور ادمین را تغییر دهید")
    print("   3. لاگ‌ها را مرتب بررسی کنید")
    print("   4. در صورت مشکل، سرویس‌ها را restart کنید")
    
    print("\n🎯 تست ربات‌ها:")
    print("   1. ربات کاربر را در تلگرام پیدا کنید")
    print("   2. دستور /start را بزنید")
    print("   3. ربات ادمین را پیدا کنید")
    print("   4. رمز عبور ادمین را وارد کنید")

def main():
    """تابع اصلی"""
    print("🤖 دیپلوی نهایی ربات‌های تلگرام")
    print("=" * 50)
    
    steps = [
        ("تنظیم محیط", setup_environment),
        ("نصب وابستگی‌ها", install_dependencies),
        ("تنظیم Django", setup_django),
        ("ایجاد سرویس‌ها", create_bot_services),
        ("راه‌اندازی سرویس‌ها", start_services),
        ("ایجاد اسکریپت‌ها", create_launcher_scripts),
    ]
    
    for step_name, step_func in steps:
        print(f"\n🔧 {step_name}...")
        if not step_func():
            print(f"❌ خطا در {step_name}")
            return
    
    # بررسی وضعیت
    check_status()
    
    # نمایش اطلاعات نهایی
    show_final_info()

if __name__ == "__main__":
    main() 