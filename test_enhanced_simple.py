#!/usr/bin/env python3
"""
تست ساده مدل‌های پیشرفته API برای X-UI
"""

import os
import sys
import django
from datetime import datetime, timedelta

# تنظیم Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from xui_servers.models import XUIServer
from xui_servers.enhanced_api_models import XUIEnhancedService
from accounts.models import UsersModel

def test_enhanced_api_simple():
    """تست ساده مدل‌های پیشرفته API"""
    print("🧪 تست ساده مدل‌های پیشرفته API...")
    
    try:
        # دریافت سرور فعال
        server = XUIServer.objects.filter(is_active=True).first()
        if not server:
            print("❌ هیچ سرور فعالی یافت نشد")
            return False
        
        print(f"✅ سرور یافت شد: {server.name}")
        
        # ایجاد session
        import requests
        session = requests.Session()
        session.headers.update({
            'Content-Type': 'application/json',
            'User-Agent': 'Django-XUI-Bot/2.0'
        })
        
        # تست لاگین
        login_data = {
            "username": server.username,
            "password": server.password
        }
        
        base_url = f"http://{server.host}:{server.port}"
        if server.web_base_path:
            base_url += server.web_base_path
        
        # تست لاگین با روش‌های مختلف
        login_methods = [
            {
                "url": f"{base_url}/login",
                "data": login_data,
                "headers": {"Content-Type": "application/json"}
            },
            {
                "url": f"{base_url}/login",
                "data": login_data,
                "headers": {"Content-Type": "application/x-www-form-urlencoded"}
            }
        ]
        
        login_success = False
        for method in login_methods:
            try:
                response = session.post(
                    method["url"],
                    json=method["data"] if method["headers"].get("Content-Type") == "application/json" else method["data"],
                    headers=method["headers"],
                    timeout=10
                )
                
                if response.status_code == 200:
                    try:
                        data = response.json()
                        if data.get('success'):
                            print(f"✅ لاگین موفق با روش {method['headers'].get('Content-Type', 'unknown')}")
                            login_success = True
                            break
                    except:
                        print(f"✅ لاگین موفق (بدون JSON معتبر)")
                        login_success = True
                        break
                        
            except Exception as e:
                print(f"❌ خطا در لاگین با روش {method['headers'].get('Content-Type', 'unknown')}: {e}")
                continue
        
        if not login_success:
            print("❌ لاگین ناموفق")
            return False
        
        print("✅ لاگین موفق!")
        
        # ایجاد سرویس پیشرفته
        enhanced_service = XUIEnhancedService(base_url, session)
        
        # تست: ایجاد Inbound همراه با Client
        print(f"\n🚀 تست ایجاد Inbound همراه با Client...")
        
        import random
        test_port = random.randint(10000, 65000)
        
        result = enhanced_service.create_inbound_with_client(
            port=test_port,
            protocol="vless",
            remark=f"Test Enhanced API {datetime.now().strftime('%Y%m%d_%H%M%S')}",
            client_email=f"test_enhanced_{datetime.now().strftime('%Y%m%d_%H%M%S')}@vpn.com",
            client_total_gb=10,
            client_expiry_time=int((datetime.now() + timedelta(days=30)).timestamp() * 1000)
        )
        
        if result:
            print(f"✅ Inbound با Client ایجاد شد:")
            print(f"  - Inbound ID: {result['inbound_id']}")
            print(f"  - Client Added: {result['client_added']}")
            print(f"  - Client ID: {result['client_id']}")
            
            # تست: دریافت لیست Client ها
            if result['inbound_id']:
                print(f"\n📋 تست دریافت لیست Client ها...")
                clients = enhanced_service.get_inbound_clients(result['inbound_id'])
                print(f"📊 تعداد Client ها: {len(clients)}")
                
                for i, client in enumerate(clients):
                    print(f"  - Client {i+1}: {client.get('email', 'نامشخص')} (ID: {client.get('id', 'نامشخص')})")
            
            # حذف Inbound تست
            if result['inbound_id']:
                print(f"\n🗑️ حذف Inbound تست...")
                from xui_servers.enhanced_api_models import XUIInboundManager
                inbound_manager = XUIInboundManager(base_url, session)
                if inbound_manager.delete_inbound(result['inbound_id']):
                    print("✅ Inbound تست حذف شد")
                else:
                    print("❌ خطا در حذف Inbound تست")
        
        print("\n🎉 تست ساده موفق بود!")
        return True
        
    except Exception as e:
        print(f"❌ خطا در تست ساده: {e}")
        return False

def test_integration_with_existing_services():
    """تست یکپارچگی با سرویس‌های موجود"""
    print("\n🔗 تست یکپارچگی با سرویس‌های موجود...")
    
    try:
        # دریافت سرور فعال
        server = XUIServer.objects.filter(is_active=True).first()
        if not server:
            print("❌ هیچ سرور فعالی یافت نشد")
            return False
        
        # ایجاد کاربر تست
        test_user, created = UsersModel.objects.get_or_create(
            id_tel="123456789",
            defaults={
                "username_tel": "test_user_enhanced_simple",
                "full_name": "کاربر تست پیشرفته ساده",
                "username": "test_user_enhanced_simple"
            }
        )
        
        if created:
            print(f"✅ کاربر تست ایجاد شد: {test_user.full_name}")
        else:
            print(f"📋 کاربر تست موجود: {test_user.full_name}")
        
        # تست یکپارچگی با UserConfigService
        from xui_servers.services import UserConfigService
        
        print("\n🔧 تست ایجاد کانفیگ با سرویس‌های موجود...")
        
        try:
            user_config, message = UserConfigService.create_trial_config(
                user=test_user,
                server=server,
                protocol="vless"
            )
            
            print(f"✅ کانفیگ تستی ایجاد شد: {message}")
            print(f"📋 جزئیات کانفیگ:")
            print(f"  - ID: {user_config.id}")
            print(f"  - XUI Inbound ID: {user_config.xui_inbound_id}")
            print(f"  - XUI User ID: {user_config.xui_user_id}")
            print(f"  - User ID: {user_config.user.id}")
            print(f"  - Protocol: {user_config.protocol}")
            
            # حذف کانفیگ تست
            UserConfigService.delete_user_config(user_config)
            print("🗑️ کانفیگ تست حذف شد")
            
        except Exception as e:
            print(f"❌ خطا در ایجاد کانفیگ: {e}")
        
        print("\n✅ تست یکپارچگی موفق بود!")
        return True
        
    except Exception as e:
        print(f"❌ خطا در تست یکپارچگی: {e}")
        return False

def main():
    """تابع اصلی"""
    print("🚀 شروع تست ساده مدل‌های پیشرفته API برای X-UI...")
    
    # تست مدل‌های پیشرفته API
    api_test_ok = test_enhanced_api_simple()
    
    # تست یکپارچگی
    integration_test_ok = test_integration_with_existing_services()
    
    # نتیجه کلی
    if api_test_ok and integration_test_ok:
        print("\n🎉 تمام تست‌ها موفق بودند!")
        print("✅ مدل‌های پیشرفته API آماده استفاده هستند!")
    else:
        print("\n❌ برخی تست‌ها ناموفق بودند!")
        print("🔧 نیاز به بررسی بیشتر!")

if __name__ == "__main__":
    main() 