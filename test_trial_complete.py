#!/usr/bin/env python3
"""
تست کامل ایجاد پلن تستی
"""

import os
import sys
import django
from django.conf import settings

# تنظیم Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

async def test_complete_trial():
    """تست کامل ایجاد پلن تستی"""
    from asgiref.sync import sync_to_async
    from accounts.models import UsersModel
    from xui_servers.models import XUIServer, XUIInbound
    from xui_servers.enhanced_api_models import XUIClientManager, XUIInboundManager
    
    print("🧪 تست کامل ایجاد پلن تستی...")
    print("=" * 60)
    
    try:
        # 1. دریافت کاربر
        print("👤 دریافت کاربر...")
        user = await sync_to_async(UsersModel.objects.first)()
        if not user:
            print("❌ هیچ کاربری یافت نشد")
            return False
        print(f"✅ کاربر: {user.full_name}")
        
        # 2. بررسی قابلیت دریافت پلن تستی
        print("\n🎁 بررسی قابلیت دریافت پلن تستی...")
        can_get_trial = await sync_to_async(user.can_get_trial)()
        print(f"✅ می‌تواند پلن تستی دریافت کند: {can_get_trial}")
        
        # 3. دریافت سرور فعال
        print("\n🖥️ دریافت سرور فعال...")
        active_servers = await sync_to_async(list)(XUIServer.objects.filter(is_active=True))
        if not active_servers:
            print("❌ هیچ سرور فعالی یافت نشد")
            return False
        server = active_servers[0]
        print(f"✅ سرور: {server.name}")
        
        # 4. یافتن یا ایجاد inbound
        print("\n📡 یافتن inbound...")
        inbound_manager = XUIInboundManager(server)
        
        # همگام‌سازی inbound ها
        print("   🔄 همگام‌سازی inbound ها...")
        sync_result = await sync_to_async(inbound_manager.sync_inbounds)()
        print(f"   📊 نتیجه همگام‌سازی: {sync_result}")
        
        # یافتن بهترین inbound
        inbound = await sync_to_async(inbound_manager.find_best_inbound)("vless")
        
        if not inbound:
            print("   ⚠️ هیچ inbound یافت نشد، ایجاد inbound نمونه...")
            # ایجاد inbound نمونه
            sample_inbound = await sync_to_async(XUIInbound.objects.create)(
                server=server,
                xui_inbound_id=1,
                tag='vless-reality-test',
                protocol='vless',
                port=443,
                settings='{"clients": []}',
                stream_settings='{"network": "tcp"}',
                sniffing='{"enabled": true}',
                is_active=True
            )
            inbound = sample_inbound
            print(f"   ✅ Inbound نمونه ایجاد شد: {inbound.tag}")
        else:
            print(f"✅ Inbound یافت شد: {inbound.tag}")
        
        # 5. ایجاد کانفیگ تستی
        print("\n🔧 ایجاد کانفیگ تستی...")
        client_manager = XUIClientManager(server)
        user_config = await client_manager.create_trial_config_async(user, inbound)
        
        if user_config:
            print(f"🎉 کانفیگ تستی ایجاد شد!")
            print(f"   📋 نام: {user_config.config_name}")
            print(f"   🆔 ID: {user_config.xui_user_id}")
            print(f"   ⏰ انقضا: {user_config.expires_at}")
            print(f"   🔧 پروتکل: {user_config.protocol}")
            print(f"   🖥️ سرور: {user_config.server.name}")
            return True
        else:
            print("❌ خطا در ایجاد کانفیگ تستی")
            return False
            
    except Exception as e:
        print(f"❌ خطا در تست: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """اجرای تست"""
    import asyncio
    
    print("🚀 شروع تست کامل پلن تستی...")
    
    try:
        result = asyncio.run(test_complete_trial())
        
        print("\n" + "=" * 60)
        if result:
            print("✅ تست موفقیت‌آمیز! پلن تستی کاملاً کار می‌کند")
        else:
            print("❌ تست ناموفق! مشکلی در سیستم وجود دارد")
            
    except Exception as e:
        print(f"\n💥 خطای اجرا: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
