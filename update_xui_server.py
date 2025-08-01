#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import sys
import django

# Add the project directory to the Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Set up Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from xui_servers.models import XUIServer
from xui_servers.services import XUIService

def update_xui_server():
    """به‌روزرسانی تنظیمات سرور X-UI"""
    print("=" * 50)
    print("🔧 به‌روزرسانی تنظیمات سرور X-UI")
    print("=" * 50)
    
    try:
        # حذف سرورهای قبلی
        XUIServer.objects.all().delete()
        print("🗑️ سرورهای قبلی حذف شدند")
        
        # ایجاد سرور جدید با تنظیمات صحیح
        server = XUIServer.objects.create(
            name="سرور اصلی (SSH Tunnel)",
            host="127.0.0.1",  # Local SSH tunnel
            port=8080,         # Local port
            username="admin",
            password="admin123",
            is_active=True
        )
        
        print(f"✅ سرور X-UI ایجاد شد: {server.name}")
        print(f"🖥️ آدرس: {server.host}:{server.port}")
        print(f"👤 نام کاربری: {server.username}")
        
        # تست اتصال
        print("\n🔍 تست اتصال به سرور...")
        xui_service = XUIService(server)
        
        try:
            # تست ورود
            login_result = xui_service.login()
            if login_result:
                print("✅ اتصال موفق!")
                
                # دریافت اطلاعات سرور
                server_info = xui_service.get_server_info()
                if server_info:
                    print(f"📊 اطلاعات سرور: {server_info}")
                
                # دریافت inbound ها
                inbounds = xui_service.get_inbounds()
                if inbounds:
                    print(f"📡 تعداد inbound ها: {len(inbounds)}")
                else:
                    print("📡 هیچ inbound یافت نشد")
                    
            else:
                print("❌ خطا در ورود. لطفا نام کاربری و رمز عبور را بررسی کنید")
                
        except Exception as e:
            print(f"❌ خطا در اتصال: {str(e)}")
            print("💡 اطمینان حاصل کنید که SSH tunnel فعال است:")
            print("   ssh -N -L 8080:127.0.0.1:80 root@38.54.105.144")
        
    except Exception as e:
        print(f"❌ خطا در به‌روزرسانی: {str(e)}")
    
    print("\n" + "=" * 50)
    print("✅ به‌روزرسانی کامل شد!")
    print("🤖 حالا می‌توانید ربات را اجرا کنید:")
    print("python bot/user_bot.py")
    print("=" * 50)

if __name__ == "__main__":
    update_xui_server() 