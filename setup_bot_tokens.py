#!/usr/bin/env python3
"""
تنظیم توکن‌های بات تلگرام
"""

import os
import subprocess

def setup_bot_tokens():
    """تنظیم توکن‌های بات"""
    print("🤖 تنظیم توکن‌های بات تلگرام")
    print("=" * 50)
    
    # بررسی فایل .env
    env_file = ".env"
    
    if not os.path.exists(env_file):
        print(f"❌ فایل {env_file} یافت نشد!")
        print("💡 فایل .env را ایجاد کنید")
        return
    
    print("✅ فایل .env موجود است")
    
    # خواندن محتوای فایل .env
    with open(env_file, 'r') as f:
        content = f.read()
    
    # بررسی توکن‌های موجود
    if 'ADMIN_BOT_TOKEN=your-admin-bot-token-here' in content:
        print("⚠️ توکن Admin Bot تنظیم نشده است")
        print("💡 لطفا توکن Admin Bot را در فایل .env تنظیم کنید")
    else:
        print("✅ توکن Admin Bot تنظیم شده است")
    
    if 'USER_BOT_TOKEN=your-user-bot-token-here' in content:
        print("⚠️ توکن User Bot تنظیم نشده است")
        print("💡 لطفا توکن User Bot را در فایل .env تنظیم کنید")
    else:
        print("✅ توکن User Bot تنظیم شده است")
    
    print("\n📝 راهنمای تنظیم توکن‌ها:")
    print("1. به @BotFather در تلگرام پیام دهید")
    print("2. دستور /newbot را اجرا کنید")
    print("3. نام بات را وارد کنید")
    print("4. نام کاربری بات را وارد کنید")
    print("5. توکن دریافتی را در فایل .env قرار دهید")
    print("\nمثال:")
    print("ADMIN_BOT_TOKEN=1234567890:ABCdefGHIjklMNOpqrsTUVwxyz")
    print("USER_BOT_TOKEN=0987654321:ZYXwvuTSRqpONMlkjIHGfedCBA")

def test_bot_connection():
    """تست اتصال بات‌ها"""
    print("\n🔗 تست اتصال بات‌ها:")
    print("=" * 40)
    
    # بررسی فایل‌های بات
    admin_bot = "bot/admin_boy.py"
    user_bot = "bot/user_bot.py"
    
    if not os.path.exists(admin_bot):
        print(f"❌ فایل {admin_bot} یافت نشد!")
        return
    
    if not os.path.exists(user_bot):
        print(f"❌ فایل {user_bot} یافت نشد!")
        return
    
    print("✅ فایل‌های بات موجود هستند")
    
    # تست اجرای Admin Bot
    print("\n🔧 تست Admin Bot...")
    try:
        result = subprocess.run([
            "python", "-c", 
            "import os; from dotenv import load_dotenv; load_dotenv(); print('ADMIN_BOT_TOKEN:', os.getenv('ADMIN_BOT_TOKEN', 'NOT_SET'))"
        ], capture_output=True, text=True)
        
        if "NOT_SET" in result.stdout:
            print("❌ توکن Admin Bot تنظیم نشده است")
        else:
            print("✅ توکن Admin Bot تنظیم شده است")
            
    except Exception as e:
        print(f"❌ خطا در تست Admin Bot: {e}")
    
    # تست اجرای User Bot
    print("\n👤 تست User Bot...")
    try:
        result = subprocess.run([
            "python", "-c", 
            "import os; from dotenv import load_dotenv; load_dotenv(); print('USER_BOT_TOKEN:', os.getenv('USER_BOT_TOKEN', 'NOT_SET'))"
        ], capture_output=True, text=True)
        
        if "NOT_SET" in result.stdout:
            print("❌ توکن User Bot تنظیم نشده است")
        else:
            print("✅ توکن User Bot تنظیم شده است")
            
    except Exception as e:
        print(f"❌ خطا در تست User Bot: {e}")

def create_sample_env():
    """ایجاد فایل .env نمونه"""
    print("\n📝 ایجاد فایل .env نمونه:")
    print("=" * 40)
    
    sample_env = """# Django Settings
SECRET_KEY=django-insecure-c^1%va7g4+yqfygvbjku#d4-4d8-sw8rzw9!$_wq-vt(*x-mw9
DEBUG=False
ALLOWED_HOSTS=38.54.105.124,your-domain.com,www.your-domain.com,localhost,127.0.0.1

# Database Settings
DATABASE_URL=postgresql://configvpn_user:your-db-password@localhost/configvpn_db

# Telegram Bot Tokens
ADMIN_BOT_TOKEN=your-admin-bot-token-here
USER_BOT_TOKEN=your-user-bot-token-here

# Admin Password
ADMIN_PASSWORD=YourSecurePassword123

# X-UI Settings
XUI_DEFAULT_PROTOCOL=vless
XUI_DEFAULT_PORT=443
XUI_PANEL_URL=http://38.54.105.124:54321
XUI_PANEL_PATH=/MsxZ4xuIy5xLfQtsSC/
XUI_PANEL_USERNAME=admin
XUI_PANEL_PASSWORD=YourSecurePassword123!@#

# Redis Settings
REDIS_URL=redis://localhost:6379/0

# Log Settings
LOG_LEVEL=INFO
LOG_FILE=/opt/configvpn/logs/app.log

# SSL Settings
ENABLE_SSL=False
SSL_CERT_PATH=/etc/letsencrypt/live/your-domain.com/fullchain.pem
SSL_KEY_PATH=/etc/letsencrypt/live/your-domain.com/privkey.pem

# Performance Settings
ENABLE_CACHE=True
CACHE_TIMEOUT=300
MAX_CONNECTIONS=100

# X-UI Server Configuration
XUI_SERVER_HOST=38.54.105.124
XUI_SERVER_PORT=54321
XUI_SERVER_USERNAME=admin
XUI_SERVER_PASSWORD=YourSecurePassword123!@#
XUI_SERVER_WEB_BASE_PATH=/MsxZ4xuIy5xLfQtsSC/
"""
    
    try:
        with open(".env", "w") as f:
            f.write(sample_env)
        print("✅ فایل .env نمونه ایجاد شد")
        print("💡 لطفا توکن‌های بات را در این فایل تنظیم کنید")
    except Exception as e:
        print(f"❌ خطا در ایجاد فایل .env: {e}")

def main():
    """تابع اصلی"""
    print("🎉 تنظیم توکن‌های بات تلگرام")
    print("=" * 60)
    
    # بررسی فایل .env
    if not os.path.exists(".env"):
        print("❌ فایل .env یافت نشد!")
        create_sample_env()
    else:
        setup_bot_tokens()
    
    # تست اتصال
    test_bot_connection()
    
    print("\n🎉 بررسی کامل شد!")
    print("=" * 60)
    print("💡 برای راه‌اندازی بات‌ها:")
    print("   1. توکن‌های بات را در فایل .env تنظیم کنید")
    print("   2. سرویس‌های بات را راه‌اندازی کنید")
    print("   3. یا بات‌ها را دستی اجرا کنید")
    print("=" * 60)

if __name__ == "__main__":
    main() 