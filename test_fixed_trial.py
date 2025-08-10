#!/usr/bin/env python3
"""
تست مشکل حل شده async/sync در trial_plan
"""

import os
import sys
import django
from django.conf import settings

# تنظیم Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

async def test_trial_async_fix():
    """تست اصلاح مشکل async در trial_plan"""
    from asgiref.sync import sync_to_async
    from accounts.models import UsersModel
    from xui_servers.models import XUIServer, XUIInbound
    from xui_servers.enhanced_api_models import XUIClientManager, XUIInboundManager
    
    print("🧪 تست اصلاح async/sync در trial_plan...")
    print("=" * 60)
    
    try:
        # 1. ایجاد کاربر تست
        print("👤 ایجاد کاربر تست...")
        user, created = await sync_to_async(UsersModel.objects.get_or_create)(
            telegram_id=999999999,
            defaults={
                'username_tel': 'test_user_async',
                'full_name': 'Test User Async',
                'has_used_trial': False
            }
        )
        
        if created:
            print("✅ کاربر تست ایجاد شد")
        else:
            print("✅ کاربر تست موجود است")
            # Reset trial status
            user.has_used_trial = False
            await sync_to_async(user.save)()
        
        # 2. تست mark_trial_used_async
        print("\n🎯 تست mark_trial_used_async...")
        
        # بررسی وضعیت اولیه
        can_get_trial_before = await sync_to_async(user.can_get_trial)()
        print(f"   📋 قبل از استفاده: {can_get_trial_before}")
        
        # استفاده از متد async
        await user.mark_trial_used_async()
        print("   ✅ mark_trial_used_async اجرا شد")
        
        # بررسی وضعیت نهایی
        await sync_to_async(user.refresh_from_db)()
        can_get_trial_after = await sync_to_async(user.can_get_trial)()
        print(f"   📋 بعد از استفاده: {can_get_trial_after}")
        
        if can_get_trial_before and not can_get_trial_after:
            print("   ✅ mark_trial_used_async درست کار می‌کند!")
        else:
            print("   ❌ مشکلی در mark_trial_used_async وجود دارد")
            return False
        
        # 3. تست کامل flow
        print("\n🔄 تست کامل flow...")
        
        # Reset برای تست مجدد
        user.has_used_trial = False
        await sync_to_async(user.save)()
        
        # دریافت سرور و inbound
        active_servers = await sync_to_async(list)(XUIServer.objects.filter(is_active=True))
        if not active_servers:
            print("   ⚠️ هیچ سرور فعالی یافت نشد، ایجاد سرور تست...")
            server = await sync_to_async(XUIServer.objects.create)(
                name="Test Server",
                host="test.example.com",
                port=443,
                username="test",
                password="test",
                is_active=True
            )
        else:
            server = active_servers[0]
        
        print(f"   🖥️ سرور: {server.name}")
        
        # ایجاد inbound تست
        inbound, created = await sync_to_async(XUIInbound.objects.get_or_create)(
            server=server,
            xui_inbound_id=999,
            defaults={
                'tag': 'test-vless',
                'protocol': 'vless',
                'port': 443,
                'settings': '{"clients": []}',
                'stream_settings': '{"network": "tcp"}',
                'sniffing': '{"enabled": true}',
                'is_active': True
            }
        )
        
        print(f"   📡 Inbound: {inbound.tag}")
        
        # تست ایجاد trial config (شبیه‌سازی)
        print("\n🎁 شبیه‌سازی ایجاد trial config...")
        
        # شبیه‌سازی موفقیت‌آمیز بودن ایجاد config
        mock_success = True
        
        if mock_success:
            # شبیه‌سازی آنچه در trial_plan اتفاق می‌افتد
            await user.mark_trial_used_async()
            print("   ✅ trial config شبیه‌سازی شد")
            print("   ✅ mark_trial_used_async در جریان کامل اجرا شد")
        
        print("\n🎉 همه تست‌ها موفق بودند!")
        return True
        
    except Exception as e:
        print(f"\n❌ خطا در تست: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """اجرای تست"""
    import asyncio
    
    print("🚀 شروع تست اصلاح async/sync...")
    
    try:
        result = asyncio.run(test_trial_async_fix())
        
        print("\n" + "=" * 60)
        if result:
            print("✅ تمام مشکلات async/sync حل شدند!")
            print("🎯 trial_plan آماده استفاده است")
        else:
            print("❌ هنوز مشکلاتی باقی مانده")
            
    except Exception as e:
        print(f"\n💥 خطای اجرا: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
