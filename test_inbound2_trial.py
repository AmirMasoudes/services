#!/usr/bin/env python3
"""
تست کامل برای Inbound 2 و ایجاد کانفیگ تستی
این فایل مشکلات async context را حل می‌کند و تست کامل برای inbound 2 ارائه می‌دهد
"""

import os
import sys
import django
from datetime import datetime, timedelta

# تنظیم Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from django.test import TestCase
from django.utils import timezone
from xui_servers.models import XUIServer, XUIInbound, UserConfig
from xui_servers.enhanced_api_models import XUIClientManager, XUIEnhancedService
from accounts.models import UsersModel
from plan.models import ConfingPlansModel

class Inbound2TrialTest:
    """کلاس تست برای Inbound 2 و کانفیگ تستی"""
    
    def __init__(self):
        self.server = None
        self.inbound = None
        self.test_user = None
        self.client_manager = None
        
    def setup_test_environment(self):
        """تنظیم محیط تست"""
        print("🔧 تنظیم محیط تست...")
        
        try:
            # یافتن سرور فعال
            self.server = XUIServer.objects.filter(is_active=True).first()
            if not self.server:
                print("❌ هیچ سرور فعالی یافت نشد!")
                return False
            
            print(f"✅ سرور یافت شد: {self.server.name}")
            
            # یافتن inbound شماره 2 یا ایجاد آن
            self.inbound = self._get_or_create_inbound2()
            if not self.inbound:
                print("❌ نتوانست inbound 2 را ایجاد یا یافت کند!")
                return False
            
            print(f"✅ Inbound 2 یافت شد: {self.inbound.remark}")
            
            # یافتن کاربر تست
            self.test_user = self._get_or_create_test_user()
            if not self.test_user:
                print("❌ نتوانست کاربر تست را ایجاد کند!")
                return False
            
            print(f"✅ کاربر تست یافت شد: {self.test_user.full_name}")
            
            # ایجاد client manager
            self.client_manager = XUIClientManager(self.server)
            
            return True
            
        except Exception as e:
            print(f"❌ خطا در تنظیم محیط تست: {e}")
            return False
    
    def _get_or_create_inbound2(self):
        """یافتن یا ایجاد inbound شماره 2"""
        try:
            # ابتدا سعی در یافتن inbound موجود
            inbound = XUIInbound.objects.filter(
                server=self.server,
                xui_inbound_id=2
            ).first()
            
            if inbound:
                return inbound
            
            # اگر موجود نبود، سعی در ایجاد آن
            print("🔄 سعی در ایجاد inbound 2...")
            
            # بررسی اتصال به X-UI
            enhanced_service = XUIEnhancedService(self.server)
            if not enhanced_service.login():
                print("❌ نتوانست به X-UI متصل شود!")
                return None
            
            # دریافت لیست inbound ها
            inbounds = enhanced_service.get_inbounds()
            if not inbounds:
                print("❌ هیچ inbound ای در X-UI یافت نشد!")
                return None
            
            # یافتن inbound با ID 2
            for inbound_data in inbounds:
                if inbound_data.get('id') == 2:
                    # ایجاد رکورد در دیتابیس
                    inbound = XUIInbound.objects.create(
                        server=self.server,
                        xui_inbound_id=2,
                        port=inbound_data.get('port', 443),
                        protocol=inbound_data.get('protocol', 'vless'),
                        remark=inbound_data.get('remark', 'Inbound 2'),
                        is_active=True,
                        max_clients=100,
                        current_clients=0
                    )
                    print(f"✅ Inbound 2 در دیتابیس ایجاد شد")
                    return inbound
            
            print("❌ Inbound با ID 2 در X-UI یافت نشد!")
            return None
            
        except Exception as e:
            print(f"❌ خطا در یافتن/ایجاد inbound 2: {e}")
            return None
    
    def _get_or_create_test_user(self):
        """یافتن یا ایجاد کاربر تست"""
        try:
            # یافتن کاربر تست موجود
            test_user = UsersModel.objects.filter(
                telegram_id=999999999  # ID تست
            ).first()
            
            if test_user:
                return test_user
            
            # ایجاد کاربر تست جدید
            test_user = UsersModel.objects.create(
                telegram_id=999999999,
                username_tel="test_user",
                full_name="کاربر تست",
                phone_number="09123456789",
                is_active=True,
                has_used_trial=False
            )
            
            print(f"✅ کاربر تست ایجاد شد: {test_user.full_name}")
            return test_user
            
        except Exception as e:
            print(f"❌ خطا در ایجاد کاربر تست: {e}")
            return None
    
    def test_trial_config_creation_sync(self):
        """تست ایجاد کانفیگ تستی با روش sync"""
        print("\n🧪 تست ایجاد کانفیگ تستی (Sync)...")
        
        try:
            # استفاده از روش sync
            user_config = self.client_manager.create_trial_config_sync(
                self.test_user, 
                self.inbound
            )
            
            if user_config:
                print(f"✅ کانفیگ تستی با موفقیت ایجاد شد!")
                print(f"   📋 نام: {user_config.config_name}")
                print(f"   🔧 پروتکل: {user_config.protocol}")
                print(f"   ⏰ انقضا: {user_config.expires_at}")
                print(f"   🆔 X-UI User ID: {user_config.xui_user_id}")
                print(f"   📊 کانفیگ: {user_config.config_data[:100]}...")
                
                # بررسی در دیتابیس
                db_config = UserConfig.objects.filter(id=user_config.id).first()
                if db_config:
                    print("✅ کانفیگ در دیتابیس ذخیره شد")
                else:
                    print("❌ کانفیگ در دیتابیس یافت نشد!")
                
                return True
            else:
                print("❌ نتوانست کانفیگ تستی ایجاد کند!")
                return False
                
        except Exception as e:
            print(f"❌ خطا در تست sync: {e}")
            return False
    
    def test_trial_config_creation_async(self):
        """تست ایجاد کانفیگ تستی با روش async"""
        print("\n🧪 تست ایجاد کانفیگ تستی (Async)...")
        
        try:
            import asyncio
            
            async def async_test():
                # استفاده از روش async
                user_config = await self.client_manager.create_trial_config_async(
                    self.test_user, 
                    self.inbound
                )
                
                if user_config:
                    print(f"✅ کانفیگ تستی async با موفقیت ایجاد شد!")
                    print(f"   📋 نام: {user_config.config_name}")
                    print(f"   🔧 پروتکل: {user_config.protocol}")
                    return True
                else:
                    print("❌ نتوانست کانفیگ تستی async ایجاد کند!")
                    return False
            
            # اجرای تست async
            result = asyncio.run(async_test())
            return result
            
        except Exception as e:
            print(f"❌ خطا در تست async: {e}")
            return False
    
    def test_inbound2_connection(self):
        """تست اتصال به inbound 2"""
        print("\n🧪 تست اتصال به Inbound 2...")
        
        try:
            # بررسی اتصال به X-UI
            enhanced_service = XUIEnhancedService(self.server)
            if enhanced_service.login():
                print("✅ اتصال به X-UI موفق")
                
                # دریافت لیست inbound ها
                inbounds = enhanced_service.get_inbounds()
                if inbounds:
                    print(f"✅ {len(inbounds)} inbound دریافت شد")
                    
                    # یافتن inbound 2
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
                        print("❌ Inbound 2 در X-UI یافت نشد!")
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
    
    def cleanup_test_data(self):
        """پاکسازی داده‌های تست"""
        print("\n🧹 پاکسازی داده‌های تست...")
        
        try:
            # حذف کانفیگ‌های تستی
            test_configs = UserConfig.objects.filter(
                user=self.test_user,
                is_trial=True
            )
            deleted_count = test_configs.count()
            test_configs.delete()
            print(f"✅ {deleted_count} کانفیگ تستی حذف شد")
            
            # بازگرداندن وضعیت کاربر
            self.test_user.has_used_trial = False
            self.test_user.save()
            print("✅ وضعیت کاربر تست بازگردانده شد")
            
        except Exception as e:
            print(f"❌ خطا در پاکسازی: {e}")
    
    def run_all_tests(self):
        """اجرای تمام تست‌ها"""
        print("🚀 شروع تست‌های Inbound 2...")
        print("=" * 50)
        
        # تنظیم محیط
        if not self.setup_test_environment():
            print("❌ تنظیم محیط تست ناموفق بود!")
            return False
        
        results = []
        
        # تست اتصال
        results.append(("اتصال به Inbound 2", self.test_inbound2_connection()))
        
        # تست ایجاد کانفیگ sync
        results.append(("ایجاد کانفیگ تستی (Sync)", self.test_trial_config_creation_sync()))
        
        # تست ایجاد کانفیگ async
        results.append(("ایجاد کانفیگ تستی (Async)", self.test_trial_config_creation_async()))
        
        # نمایش نتایج
        print("\n📊 نتایج تست‌ها:")
        print("-" * 50)
        
        passed = 0
        total = len(results)
        
        for test_name, result in results:
            status = "✅ موفق" if result else "❌ ناموفق"
            print(f"{test_name}: {status}")
            if result:
                passed += 1
        
        print("-" * 50)
        print(f"نتایج: {passed}/{total} تست موفق")
        
        # پاکسازی
        self.cleanup_test_data()
        
        return passed == total

def main():
    """تابع اصلی"""
    print("🎯 تست Inbound 2 و کانفیگ تستی")
    print("این تست مشکلات async context را حل می‌کند")
    print("=" * 60)
    
    # ایجاد نمونه تست
    tester = Inbound2TrialTest()
    
    # اجرای تست‌ها
    success = tester.run_all_tests()
    
    if success:
        print("\n🎉 تمام تست‌ها با موفقیت انجام شد!")
        print("✅ مشکلات async context حل شد")
        print("✅ Inbound 2 قابل استفاده است")
        print("✅ کانفیگ تستی قابل ایجاد است")
    else:
        print("\n⚠️ برخی تست‌ها ناموفق بودند")
        print("لطفا خطاها را بررسی کنید")
    
    return success

if __name__ == "__main__":
    main()
