#!/usr/bin/env python3
"""
اسکریپت تست رفع مشکل async/sync در ربات تلگرام
"""

import os
import sys
import django
from django.conf import settings

# تنظیم Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

async def test_trial_config_creation():
    """تست ایجاد کانفیگ تستی در محیط async"""
    from asgiref.sync import sync_to_async
    from accounts.models import UsersModel
    from xui_servers.models import XUIServer, XUIInbound
    from xui_servers.enhanced_api_models import XUIClientManager
    
    try:
        print("🔍 تست ایجاد کانفیگ تستی در محیط async...")
        
        # دریافت کاربر تست
        user = await sync_to_async(UsersModel.objects.first)()
        if not user:
            print("❌ هیچ کاربری یافت نشد")
            return False
        
        # دریافت سرور فعال
        server = await sync_to_async(XUIServer.objects.filter(is_active=True).first)()
        if not server:
            print("❌ هیچ سرور فعالی یافت نشد")
            return False
        
        # دریافت inbound
        inbound = await sync_to_async(XUIInbound.objects.filter(server=server).first)()
        if not inbound:
            print("❌ هیچ inbound یافت نشد")
            return False
        
        print(f"✅ کاربر: {user.full_name}")
        print(f"✅ سرور: {server.name}")
        print(f"✅ Inbound: {inbound.tag}")
        
        # تست ایجاد کانفیگ تستی با متد جدید async
        client_manager = XUIClientManager(server)
        user_config = await client_manager.create_trial_config_async(user, inbound)
        
        if user_config:
            print(f"🎉 کانفیگ تستی با موفقیت ایجاد شد!")
            print(f"   📋 نام: {user_config.config_name}")
            print(f"   🆔 ID: {user_config.xui_user_id}")
            print(f"   ⏰ انقضا: {user_config.expires_at}")
            return True
        else:
            print("❌ خطا در ایجاد کانفیگ تستی")
            return False
            
    except Exception as e:
        print(f"❌ خطا در تست: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_sync_vs_async():
    """مقایسه متدهای sync و async"""
    import asyncio
    
    print("🚀 شروع تست async/sync...")
    print("=" * 50)
    
    # تست async
    result = asyncio.run(test_trial_config_creation())
    
    print("=" * 50)
    print(f"📊 نتیجه: {'✅ موفق' if result else '❌ ناموفق'}")
    
    return result

if __name__ == "__main__":
    try:
        result = test_sync_vs_async()
        if result:
            print("\n🎉 مشکل async/sync حل شد!")
        else:
            print("\n❌ مشکل هنوز وجود دارد")
    except Exception as e:
        print(f"\n💥 خطای کلی: {e}")
        import traceback
        traceback.print_exc()
