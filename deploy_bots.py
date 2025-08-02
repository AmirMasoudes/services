#!/usr/bin/env python3
"""
اسکریپت دیپلوی ربات‌های تلگرام
این اسکریپت ربات‌های کاربر و ادمین را راه‌اندازی می‌کند
"""

import os
import sys
import subprocess
import time
import signal
import psutil
from pathlib import Path

def check_environment():
    """بررسی متغیرهای محیطی مورد نیاز"""
    print("🔍 بررسی متغیرهای محیطی...")
    
    required_vars = [
        'USER_BOT_TOKEN',
        'ADMIN_BOT_TOKEN', 
        'ADMIN_PASSWORD'
    ]
    
    missing_vars = []
    for var in required_vars:
        if not os.getenv(var):
            missing_vars.append(var)
    
    if missing_vars:
        print(f"❌ متغیرهای محیطی زیر تعریف نشده‌اند:")
        for var in missing_vars:
            print(f"   - {var}")
        print("\n📝 لطفاً فایل .env را بررسی کنید.")
        return False
    
    print("✅ تمام متغیرهای محیطی موجود هستند.")
    return True

def check_dependencies():
    """بررسی وابستگی‌های مورد نیاز"""
    print("🔍 بررسی وابستگی‌ها...")
    
    required_packages = [
        'python-telegram-bot',
        'django',
        'python-dotenv',
        'psutil'
    ]
    
    missing_packages = []
    for package in required_packages:
        try:
            __import__(package.replace('-', '_'))
        except ImportError:
            missing_packages.append(package)
    
    if missing_packages:
        print(f"❌ پکیج‌های زیر نصب نشده‌اند:")
        for package in missing_packages:
            print(f"   - {package}")
        
        install = input("\n🤔 آیا می‌خواهید نصب شوند؟ (y/n): ")
        if install.lower() == 'y':
            for package in missing_packages:
                print(f"📦 نصب {package}...")
                subprocess.run([sys.executable, '-m', 'pip', 'install', package])
        else:
            return False
    
    print("✅ تمام وابستگی‌ها موجود هستند.")
    return True

def create_bot_services():
    """ایجاد سرویس‌های systemd برای ربات‌ها"""
    print("🔧 ایجاد سرویس‌های systemd...")
    
    # مسیر پروژه
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
    
    # نوشتن فایل‌های سرویس
    with open('/etc/systemd/system/vpn-user-bot.service', 'w') as f:
        f.write(user_bot_service)
    
    with open('/etc/systemd/system/vpn-admin-bot.service', 'w') as f:
        f.write(admin_bot_service)
    
    print("✅ فایل‌های سرویس ایجاد شدند.")

def start_bot_services():
    """راه‌اندازی سرویس‌های ربات"""
    print("🚀 راه‌اندازی سرویس‌های ربات...")
    
    try:
        # Reload systemd
        subprocess.run(['systemctl', 'daemon-reload'], check=True)
        
        # Enable services
        subprocess.run(['systemctl', 'enable', 'vpn-user-bot.service'], check=True)
        subprocess.run(['systemctl', 'enable', 'vpn-admin-bot.service'], check=True)
        
        # Start services
        subprocess.run(['systemctl', 'start', 'vpn-user-bot.service'], check=True)
        subprocess.run(['systemctl', 'start', 'vpn-admin-bot.service'], check=True)
        
        print("✅ سرویس‌های ربات راه‌اندازی شدند.")
        return True
        
    except subprocess.CalledProcessError as e:
        print(f"❌ خطا در راه‌اندازی سرویس‌ها: {e}")
        return False

def check_bot_status():
    """بررسی وضعیت ربات‌ها"""
    print("🔍 بررسی وضعیت ربات‌ها...")
    
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

def show_bot_logs():
    """نمایش لاگ‌های ربات‌ها"""
    print("📋 لاگ‌های ربات‌ها:")
    
    services = ['vpn-user-bot.service', 'vpn-admin-bot.service']
    
    for service in services:
        print(f"\n🔍 لاگ‌های {service}:")
        try:
            result = subprocess.run(['journalctl', '-u', service, '-n', '10', '--no-pager'], 
                                  capture_output=True, text=True)
            print(result.stdout)
        except Exception as e:
            print(f"❌ خطا در نمایش لاگ‌ها: {e}")

def create_bot_config():
    """ایجاد فایل تنظیمات ربات"""
    print("⚙️ ایجاد فایل تنظیمات ربات...")
    
    config_content = """# تنظیمات ربات‌های تلگرام

# ربات کاربر
USER_BOT_TOKEN=your_user_bot_token_here
USER_BOT_NAME=VPN User Bot

# ربات ادمین
ADMIN_BOT_TOKEN=your_admin_bot_token_here
ADMIN_BOT_NAME=VPN Admin Bot
ADMIN_PASSWORD=admin123

# تنظیمات عمومی
BOT_WEBHOOK_URL=https://your-domain.com/webhook
BOT_WEBHOOK_PATH=/webhook

# تنظیمات لاگینگ
LOG_LEVEL=INFO
LOG_FILE=/var/log/vpn-bots.log

# تنظیمات امنیتی
ALLOWED_USERS=[]
ADMIN_USERS=[]

# تنظیمات کانفیگ
DEFAULT_PROTOCOL=vless
DEFAULT_PLAN=trial
TRIAL_DURATION_HOURS=24
PAID_DURATION_DAYS=30

# تنظیمات X-UI
XUI_SERVER_HOST=localhost
XUI_SERVER_PORT=54321
XUI_USERNAME=admin
XUI_PASSWORD=admin
"""
    
    with open('bot_config.env', 'w', encoding='utf-8') as f:
        f.write(config_content)
    
    print("✅ فایل تنظیمات ربات ایجاد شد.")

def create_bot_launcher():
    """ایجاد اسکریپت راه‌اندازی ربات"""
    print("🚀 ایجاد اسکریپت راه‌اندازی...")
    
    launcher_content = """#!/bin/bash
# اسکریپت راه‌اندازی ربات‌های تلگرام

# تنظیم مسیر پروژه
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

# راه‌اندازی ربات کاربر
echo "🚀 راه‌اندازی ربات کاربر..."
python3 bot/user_bot.py &
USER_BOT_PID=$!

# راه‌اندازی ربات ادمین
echo "🚀 راه‌اندازی ربات ادمین..."
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
    
    with open('start_bots.sh', 'w') as f:
        f.write(launcher_content)
    
    # اعطای مجوز اجرا
    os.chmod('start_bots.sh', 0o755)
    
    print("✅ اسکریپت راه‌اندازی ایجاد شد.")

def create_stop_script():
    """ایجاد اسکریپت توقف ربات"""
    print("🛑 ایجاد اسکریپت توقف...")
    
    stop_content = """#!/bin/bash
# اسکریپت توقف ربات‌های تلگرام

PROJECT_PATH="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$PROJECT_PATH"

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
    
    with open('stop_bots.sh', 'w') as f:
        f.write(stop_content)
    
    # اعطای مجوز اجرا
    os.chmod('stop_bots.sh', 0o755)
    
    print("✅ اسکریپت توقف ایجاد شد.")

def test_bots():
    """تست ربات‌ها"""
    print("🧪 تست ربات‌ها...")
    
    # تست ربات کاربر
    print("🔍 تست ربات کاربر...")
    try:
        result = subprocess.run([sys.executable, 'bot/user_bot.py', '--test'], 
                              capture_output=True, text=True, timeout=10)
        if result.returncode == 0:
            print("✅ ربات کاربر سالم است")
        else:
            print(f"❌ ربات کاربر مشکل دارد: {result.stderr}")
    except Exception as e:
        print(f"❌ خطا در تست ربات کاربر: {e}")
    
    # تست ربات ادمین
    print("🔍 تست ربات ادمین...")
    try:
        result = subprocess.run([sys.executable, 'bot/admin_boy.py', '--test'], 
                              capture_output=True, text=True, timeout=10)
        if result.returncode == 0:
            print("✅ ربات ادمین سالم است")
        else:
            print(f"❌ ربات ادمین مشکل دارد: {result.stderr}")
    except Exception as e:
        print(f"❌ خطا در تست ربات ادمین: {e}")

def main():
    """تابع اصلی"""
    print("🤖 دیپلوی ربات‌های تلگرام")
    print("=" * 50)
    
    # بررسی محیط
    if not check_environment():
        return
    
    # بررسی وابستگی‌ها
    if not check_dependencies():
        return
    
    # ایجاد فایل‌های تنظیمات
    create_bot_config()
    create_bot_launcher()
    create_stop_script()
    
    # ایجاد سرویس‌ها (اگر root هستیم)
    if os.geteuid() == 0:
        create_bot_services()
        
        # راه‌اندازی سرویس‌ها
        if start_bot_services():
            print("\n⏳ انتظار برای راه‌اندازی...")
            time.sleep(5)
            
            # بررسی وضعیت
            check_bot_status()
            
            # نمایش لاگ‌ها
            show_bot_logs()
        else:
            print("❌ خطا در راه‌اندازی سرویس‌ها")
    else:
        print("⚠️ برای ایجاد سرویس‌های systemd نیاز به دسترسی root است")
        print("💡 می‌توانید از اسکریپت‌های راه‌اندازی استفاده کنید:")
        print("   ./start_bots.sh")
        print("   ./stop_bots.sh")
    
    # تست ربات‌ها
    test_bots()
    
    print("\n🎉 دیپلوی ربات‌ها کامل شد!")
    print("\n📋 دستورات مفید:")
    print("   systemctl status vpn-user-bot.service")
    print("   systemctl status vpn-admin-bot.service")
    print("   journalctl -u vpn-user-bot.service -f")
    print("   journalctl -u vpn-admin-bot.service -f")
    print("   ./start_bots.sh")
    print("   ./stop_bots.sh")

if __name__ == "__main__":
    main() 