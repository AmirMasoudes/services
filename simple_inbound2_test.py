#!/usr/bin/env python3
"""
تست ساده برای Inbound 2 و حل مشکل async context
"""

import os
import sys
import django

# تنظیم Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from xui_servers.models import XUIServer, XUIInbound, UserConfig
from xui_servers.enhanced_api_models import XUIClientManager, XUIEnhancedService
from accounts.models import UsersModel

def test_inbound2_connection():
    """تست اتصال به inbound 2"""
    print("🔧 تست اتصال به Inbound 2...")
    
    try:
        # یافتن سرور فعال
        server = XUIServer.objects.filter(is_active=True).first()
        if not server:
            print("❌ هیچ سرور فعالی یافت نشد!")
            return False
        
        print(f"✅ سرور یافت شد: {server.name}")
        
        # بررسی اتصال به X-UI
        enhanced_service = XUIEnhancedService(server)
        if enhanced_service.login():
            print("✅ اتصال به X-UI موفق")
            
            # دریافت لیست inbound ها
            inbounds = enhanced_service.get_inbounds()
            if inbounds:
                print(f"✅ {len(inbounds)} inbound دریافت شد")
                
                # یافتن inbound با ID 2
                inbound2 = None
                for inbound in inbounds:
                    if inbound.get('id') == 2:
                        inbound2 = inbound
                        break
                
                if inbound2:
                    print(f"✅ Inbound 2 یافت شد:")
                    print(f"   🔧 پروتکل: {inbound2.get('protocol')}")
                    print(f"   🌐 پورت: {inbound2.get('port')}")
                    print(f"   📝 نام: {inbound2.get('remark')}")
                    print(f"   👥 کلاینت‌ها: {len(inbound2.get('settings', {}).get('clients', []))}")
                    return True
                else:
                    print("❌ Inbound با ID 2 در X-UI یافت نشد!")
                    return False
            else:
                print("❌ نتوانست لیست inbound ها را دریافت کند!")
                return False
        else:
            print("❌ نتوانست به X-UI متصل شود!")
            return False
            
    except Exception as e:
        print(f"❌ خطا در تست اتصال: {e}")
        return False

def test_trial_config_creation():
    """تست ایجاد کانفیگ تستی"""
    print("\n🧪 تست ایجاد کانفیگ تستی...")
    
    try:
        # یافتن سرور فعال
        server = XUIServer.objects.filter(is_active=True).first()
        if not server:
            print("❌ هیچ سرور فعالی یافت نشد!")
            return False
        
        # یافتن inbound شماره 2
        inbound = XUIInbound.objects.filter(
            server=server,
            xui_inbound_id=2
        ).first()
        
        if not inbound:
            print("❌ Inbound 2 یافت نشد!")
            return False
        
        print(f"✅ Inbound 2 یافت شد: {inbound.remark}")
        
        # یافتن کاربر تست
        test_user = UsersModel.objects.filter(
            telegram_id=999999999
        ).first()
        
        if not test_user:
            # ایجاد کاربر تست
            test_user = UsersModel.objects.create(
                telegram_id=999999999,
                username_tel="test_user",
                full_name="کاربر تست",
                phone_number="09123456789",
                is_active=True,
                has_used_trial=False
            )
            print(f"✅ کاربر تست ایجاد شد: {test_user.full_name}")
        
        # ایجاد client manager
        client_manager = XUIClientManager(server)
        
        # تست ایجاد کانفیگ با روش sync
        print("🔄 تست ایجاد کانفیگ با روش sync...")
        user_config = client_manager.create_trial_config_sync(test_user, inbound)
        
        if user_config:
            print(f"✅ کانفیگ تستی با موفقیت ایجاد شد!")
            print(f"   📋 نام: {user_config.config_name}")
            print(f"   🔧 پروتکل: {user_config.protocol}")
            print(f"   ⏰ انقضا: {user_config.expires_at}")
            print(f"   🆔 X-UI User ID: {user_config.xui_user_id}")
            
            # پاکسازی
            user_config.delete()
            print("✅ کانفیگ تستی حذف شد")
            
            return True
        else:
            print("❌ نتوانست کانفیگ تستی ایجاد کند!")
            return False
            
    except Exception as e:
        print(f"❌ خطا در تست ایجاد کانفیگ: {e}")
        return False

def main():
    """تابع اصلی"""
    print("🎯 تست Inbound 2 و حل مشکل async context")
    print("=" * 50)
    
    # تست اتصال
    connection_success = test_inbound2_connection()
    
    # تست ایجاد کانفیگ
    config_success = test_trial_config_creation()
    
    # نمایش نتایج
    print("\n📊 نتایج تست‌ها:")
    print("-" * 30)
    print(f"اتصال به Inbound 2: {'✅ موفق' if connection_success else '❌ ناموفق'}")
    print(f"ایجاد کانفیگ تستی: {'✅ موفق' if config_success else '❌ ناموفق'}")
    
    if connection_success and config_success:
        print("\n🎉 تمام تست‌ها با موفقیت انجام شد!")
        print("✅ مشکلات async context حل شد")
        print("✅ Inbound 2 قابل استفاده است")
        print("✅ کانفیگ تستی قابل ایجاد است")
    else:
        print("\n⚠️ برخی تست‌ها ناموفق بودند")
        print("لطفا خطاها را بررسی کنید")

if __name__ == "__main__":
    main()
