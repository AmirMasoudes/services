#!/usr/bin/env python3
"""
اسکریپت راه‌اندازی سرور X-UI
"""

import os
import sys
import django
from dotenv import load_dotenv

# اضافه کردن مسیر پروژه به sys.path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Load environment variables
load_dotenv()

# تنظیم ماژول تنظیمات
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')

# راه‌اندازی جنگو
django.setup()

from xui_servers.models import XUIServer
from xui_servers.services import XUIService

def setup_xui_server():
    """راه‌اندازی سرور X-UI"""
    print("🚀 راه‌اندازی سرور X-UI...")
    
    # بررسی سرورهای موجود
    existing_servers = XUIServer.objects.filter(is_active=True)
    if existing_servers.exists():
        print("📊 سرورهای موجود:")
        for server in existing_servers:
            print(f"  - {server.name} ({server.host}:{server.port})")
        return
    
    # ایجاد سرور پیش‌فرض
    try:
        server = XUIServer.objects.create(
            name="سرور اصلی",
            host="your-server-ip.com",  # آدرس سرور خود را اینجا قرار دهید
            port=54321,  # پورت X-UI
            username="admin",  # نام کاربری X-UI
            password="your-password",  # رمز عبور X-UI
            is_active=True
        )
        
        print(f"✅ سرور X-UI ایجاد شد: {server.name}")
        print(f"🖥️ آدرس: {server.host}:{server.port}")
        print(f"👤 نام کاربری: {server.username}")
        
        # تست اتصال
        print("\n🔍 تست اتصال به سرور...")
        xui_service = XUIService(server)
        
        if xui_service.login():
            print("✅ اتصال به سرور موفق بود!")
            
            # دریافت inbound ها
            inbounds = xui_service.get_inbounds()
            if inbounds:
                print(f"📋 تعداد inbound ها: {len(inbounds)}")
                for inbound in inbounds:
                    print(f"  - ID: {inbound.get('id')}, Port: {inbound.get('port')}")
            else:
                print("⚠️ هیچ inbound یافت نشد. لطفا در X-UI inbound ایجاد کنید.")
        else:
            print("❌ خطا در اتصال به سرور. لطفا تنظیمات را بررسی کنید.")
            
    except Exception as e:
        print(f"❌ خطا در ایجاد سرور: {e}")

def test_xui_connection():
    """تست اتصال به سرورهای X-UI"""
    print("\n🔍 تست اتصال به سرورهای X-UI...")
    
    servers = XUIServer.objects.filter(is_active=True)
    if not servers.exists():
        print("❌ هیچ سرور فعالی یافت نشد.")
        return
    
    for server in servers:
        print(f"\n🖥️ تست سرور: {server.name}")
        print(f"📍 آدرس: {server.host}:{server.port}")
        
        try:
            xui_service = XUIService(server)
            
            # تست ورود
            if xui_service.login():
                print("✅ ورود موفق")
                
                # دریافت inbound ها
                inbounds = xui_service.get_inbounds()
                if inbounds:
                    print(f"📋 تعداد inbound ها: {len(inbounds)}")
                    for inbound in inbounds[:3]:  # نمایش 3 مورد اول
                        print(f"  - ID: {inbound.get('id')}, Port: {inbound.get('port')}")
                else:
                    print("⚠️ هیچ inbound یافت نشد")
            else:
                print("❌ خطا در ورود")
                
        except Exception as e:
            print(f"❌ خطا در اتصال: {e}")

def show_help():
    """نمایش راهنما"""
    print("""
🔧 راهنمای راه‌اندازی X-UI:

1. ابتدا X-UI را روی سرور خود نصب کنید:
   https://github.com/vaxilu/x-ui

2. تنظیمات سرور را در فایل .env قرار دهید:
   XUI_SERVER_HOST=your-server-ip.com
   XUI_SERVER_PORT=54321
   XUI_USERNAME=admin
   XUI_PASSWORD=your-password

3. این اسکریپت را اجرا کنید:
   python setup_xui_server.py

4. در X-UI یک inbound ایجاد کنید (VMess/VLess)

5. ربات را اجرا کنید:
   python bot/user_bot.py

📋 نکات مهم:
• حتماً inbound در X-UI ایجاد کنید
• پورت 443 برای HTTPS ضروری است
• SSL certificate باید معتبر باشد
• فایروال سرور را باز کنید
""")

if __name__ == "__main__":
    print("=" * 50)
    print("🔧 راه‌اندازی سیستم X-UI")
    print("=" * 50)
    
    if len(sys.argv) > 1 and sys.argv[1] == "help":
        show_help()
    else:
        setup_xui_server()
        test_xui_connection()
        
        print("\n" + "=" * 50)
        print("✅ راه‌اندازی کامل شد!")
        print("🤖 حالا می‌توانید ربات را اجرا کنید:")
        print("python bot/user_bot.py")
        print("=" * 50) 