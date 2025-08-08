#!/usr/bin/env python3
"""
اسکریپت تست اتصال به X-UI سنایی
این اسکریپت برای بررسی اتصال و عملکرد API سنایی استفاده می‌شود
"""

import os
import sys
import django
from dotenv import load_dotenv

# Load environment variables
load_dotenv('config.env')

# اضافه کردن مسیر پروژه به sys.path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# تنظیم ماژول تنظیمات
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')

# راه‌اندازی جنگو
django.setup()

from xui_servers.sanaei_api import SanaeiXUIAPI
from xui_servers.enhanced_api_models import XUIEnhancedService
from xui_servers.models import XUIServer

def test_sanaei_connection():
    """تست اتصال به X-UI سنایی"""
    print("🔍 تست اتصال به X-UI سنایی...")
    
    # دریافت تنظیمات از متغیرهای محیطی
    host = os.getenv('XUI_DEFAULT_HOST')
    port = int(os.getenv('XUI_DEFAULT_PORT', 54321))
    username = os.getenv('XUI_DEFAULT_USERNAME')
    password = os.getenv('XUI_DEFAULT_PASSWORD')
    web_base_path = os.getenv('XUI_WEB_BASE_PATH', '/MsxZ4xuIy5xLfQtsSC/')
    
    print(f"📋 تنظیمات سرور:")
    print(f"   • آدرس: {host}")
    print(f"   • پورت: {port}")
    print(f"   • نام کاربری: {username}")
    print(f"   • مسیر وب: {web_base_path}")
    
    if not all([host, username, password]):
        print("❌ تنظیمات ناقص است. لطفا فایل env_config.env را بررسی کنید.")
        return False
    
    try:
        # تست با API مستقیم
        print("\n🔧 تست با API مستقیم...")
        api = SanaeiXUIAPI(host, port, username, password, web_base_path)
        
        # تست لاگین
        if api.login():
            print("✅ لاگین موفق")
            
            # دریافت inbound ها
            inbounds = api.get_inbounds()
            print(f"📊 تعداد inbound ها: {len(inbounds)}")
            
            for inbound in inbounds:
                print(f"   • ID: {inbound.get('id')}, نام: {inbound.get('remark')}, پورت: {inbound.get('port')}")
            
            return True
        else:
            print("❌ لاگین ناموفق")
            return False
            
    except Exception as e:
        print(f"❌ خطا در اتصال: {e}")
        return False

def test_enhanced_service():
    """تست سرویس پیشرفته"""
    print("\n🔧 تست سرویس پیشرفته...")
    
    try:
        # ایجاد سرور تست
        server = XUIServer(
            name="سرور تست سنایی",
            host=os.getenv('XUI_DEFAULT_HOST'),
            port=int(os.getenv('XUI_DEFAULT_PORT', 54321)),
            username=os.getenv('XUI_DEFAULT_USERNAME'),
            password=os.getenv('XUI_DEFAULT_PASSWORD'),
            web_base_path=os.getenv('XUI_WEB_BASE_PATH', '/MsxZ4xuIy5xLfQtsSC/'),
            is_active=True
        )
        
        # تست سرویس پیشرفته
        service = XUIEnhancedService(server)
        
        if service.login():
            print("✅ لاگین سرویس پیشرفته موفق")
            
            # دریافت inbound ها
            inbounds = service.get_inbounds()
            print(f"📊 تعداد inbound ها: {len(inbounds)}")
            
            return True
        else:
            print("❌ لاگین سرویس پیشرفته ناموفق")
            return False
            
    except Exception as e:
        print(f"❌ خطا در سرویس پیشرفته: {e}")
        return False

def test_client_creation():
    """تست ایجاد کلاینت"""
    print("\n🔧 تست ایجاد کلاینت...")
    
    try:
        # ایجاد سرور تست
        server = XUIServer(
            name="سرور تست سنایی",
            host=os.getenv('XUI_DEFAULT_HOST'),
            port=int(os.getenv('XUI_DEFAULT_PORT', 54321)),
            username=os.getenv('XUI_DEFAULT_USERNAME'),
            password=os.getenv('XUI_DEFAULT_PASSWORD'),
            web_base_path=os.getenv('XUI_WEB_BASE_PATH', '/MsxZ4xuIy5xLfQtsSC/'),
            is_active=True
        )
        
        # تست ایجاد کلاینت
        api = SanaeiXUIAPI(server.host, server.port, server.username, server.password, server.web_base_path)
        
        if api.login():
            # دریافت inbound ها
            inbounds = api.get_inbounds()
            if inbounds:
                inbound_id = inbounds[0]['id']
                print(f"📋 استفاده از inbound ID: {inbound_id}")
                
                # ایجاد تنظیمات کلاینت تست
                import uuid
                client_data = {
                    "clients": [{
                        "id": str(uuid.uuid4()),
                        "flow": "",
                        "email": f"test_user_{uuid.uuid4().hex[:8]}",
                        "limitIp": 0,
                        "totalGB": 1,
                        "expiryTime": 0,
                        "enable": True,
                        "tgId": "",
                        "subId": "",
                        "reset": 0
                    }]
                }
                
                # اضافه کردن کلاینت
                if api.add_client_to_inbound(inbound_id, client_data):
                    print("✅ کلاینت تست با موفقیت اضافه شد")
                    
                    # حذف کلاینت تست
                    client_email = client_data['clients'][0]['email']
                    if api.remove_client_from_inbound(inbound_id, client_email):
                        print("✅ کلاینت تست با موفقیت حذف شد")
                    else:
                        print("⚠️ خطا در حذف کلاینت تست")
                    
                    return True
                else:
                    print("❌ خطا در اضافه کردن کلاینت تست")
                    return False
            else:
                print("❌ هیچ inbound یافت نشد")
                return False
        else:
            print("❌ لاگین ناموفق")
            return False
            
    except Exception as e:
        print(f"❌ خطا در تست ایجاد کلاینت: {e}")
        return False

def main():
    """تابع اصلی"""
    print("🚀 شروع تست اتصال به X-UI سنایی...\n")
    
    # تست 1: اتصال مستقیم
    test1_result = test_sanaei_connection()
    
    # تست 2: سرویس پیشرفته
    test2_result = test_enhanced_service()
    
    # تست 3: ایجاد کلاینت
    test3_result = test_client_creation()
    
    print("\n" + "="*50)
    print("📊 نتایج تست:")
    print(f"   • اتصال مستقیم: {'✅ موفق' if test1_result else '❌ ناموفق'}")
    print(f"   • سرویس پیشرفته: {'✅ موفق' if test2_result else '❌ ناموفق'}")
    print(f"   • ایجاد کلاینت: {'✅ موفق' if test3_result else '❌ ناموفق'}")
    
    if all([test1_result, test2_result, test3_result]):
        print("\n🎉 تمام تست‌ها موفق بودند!")
        print("✅ سیستم آماده استفاده از X-UI سنایی است.")
    else:
        print("\n⚠️ برخی تست‌ها ناموفق بودند.")
        print("🔧 لطفا تنظیمات را بررسی کنید.")

if __name__ == "__main__":
    main() 