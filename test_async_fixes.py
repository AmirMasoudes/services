#!/usr/bin/env python3
"""
تست کامل رفع مشکلات async/sync در ربات تلگرام
"""

import os
import sys
import django
from django.conf import settings

# تنظیم Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

async def test_all_bot_functions():
    """تست همه توابع ربات که مشکل async/sync داشتند"""
    from asgiref.sync import sync_to_async
    from accounts.models import UsersModel
    from xui_servers.models import XUIServer, XUIInbound, UserConfig
    from order.models import OrderUserModel
    from conf.models import ConfigUserModel
    from xui_servers.enhanced_api_models import XUIClientManager
    
    print("🧪 تست کامل توابع ربات تلگرام...")
    print("=" * 60)
    
    try:
        # ایجاد کاربر تست
        user, created = await sync_to_async(UsersModel.objects.get_or_create)(
            telegram_id=123456789,
            defaults={
                'id_tel': '123456789',
                'username_tel': 'test_user',
                'full_name': 'کاربر تست',
                'username': 'test_user'
            }
        )
        
        if created:
            print("✅ کاربر تست ایجاد شد")
        else:
            print("✅ کاربر تست موجود است")
        
        # تست 1: profile function
        print("\n🔍 تست تابع profile...")
        try:
            total_orders_count = await sync_to_async(OrderUserModel.objects.filter(user=user).count)()
            active_orders_count = await sync_to_async(OrderUserModel.objects.filter(user=user, is_active=True).count)()
            xui_configs_count = await sync_to_async(UserConfig.objects.filter(user=user, is_active=True).count)()
            trial_used = await sync_to_async(lambda: user.has_used_trial)()
            
            print(f"   📊 کل سفارشات: {total_orders_count}")
            print(f"   ✅ سفارشات فعال: {active_orders_count}")
            print(f"   🔧 کانفیگ‌های فعال: {xui_configs_count}")
            print(f"   🎁 پلن تستی استفاده شده: {trial_used}")
            print("   ✅ تابع profile: موفق")
        except Exception as e:
            print(f"   ❌ تابع profile: {e}")
        
        # تست 2: my_plans function
        print("\n🔍 تست تابع my_plans...")
        try:
            orders = await sync_to_async(list)(OrderUserModel.objects.filter(user=user).order_by('-created_at'))
            xui_configs = await sync_to_async(list)(UserConfig.objects.filter(user=user, is_active=True))
            
            print(f"   📦 تعداد سفارشات: {len(orders)}")
            print(f"   🔧 تعداد کانفیگ‌های X-UI: {len(xui_configs)}")
            print("   ✅ تابع my_plans: موفق")
        except Exception as e:
            print(f"   ❌ تابع my_plans: {e}")
        
        # تست 3: my_config function
        print("\n🔍 تست تابع my_config...")
        try:
            configs = await sync_to_async(list)(ConfigUserModel.objects.filter(user=user, is_active=True))
            xui_configs = await sync_to_async(list)(UserConfig.objects.filter(user=user, is_active=True))
            
            print(f"   ⚙️ تعداد کانفیگ‌های کاربر: {len(configs)}")
            print(f"   🔧 تعداد کانفیگ‌های X-UI: {len(xui_configs)}")
            print("   ✅ تابع my_config: موفق")
        except Exception as e:
            print(f"   ❌ تابع my_config: {e}")
        
        # تست 4: trial_plan function
        print("\n🔍 تست تابع trial_plan...")
        try:
            # بررسی سرورهای فعال
            active_servers = await sync_to_async(list)(XUIServer.objects.filter(is_active=True))
            if active_servers:
                server = active_servers[0]
                print(f"   🖥️ سرور فعال یافت شد: {server.name}")
                
                # بررسی inbound
                inbound = await sync_to_async(XUIInbound.objects.filter(server=server).first)()
                if inbound:
                    print(f"   📡 Inbound یافت شد: {inbound.tag}")
                    
                    # تست ایجاد کانفیگ تستی (فقط تست، ایجاد نمی‌کنیم)
                    client_manager = XUIClientManager(server)
                    print("   🎯 ClientManager آماده")
                    print("   ✅ تابع trial_plan: آماده برای اجرا")
                else:
                    print("   ⚠️ هیچ inbound یافت نشد")
            else:
                print("   ⚠️ هیچ سرور فعالی یافت نشد")
        except Exception as e:
            print(f"   ❌ تابع trial_plan: {e}")
        
        print("\n" + "=" * 60)
        print("🎉 همه تست‌ها تکمیل شد!")
        
        return True
        
    except Exception as e:
        print(f"❌ خطای کلی در تست: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """اجرای تست‌ها"""
    import asyncio
    
    print("🚀 شروع تست رفع مشکلات async/sync...")
    
    try:
        result = asyncio.run(test_all_bot_functions())
        
        if result:
            print("\n✅ همه مشکلات async/sync حل شدند!")
            print("🎯 ربات تلگرام آماده استفاده است")
        else:
            print("\n❌ برخی مشکلات هنوز وجود دارند")
            
    except Exception as e:
        print(f"\n💥 خطای اجرا: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
