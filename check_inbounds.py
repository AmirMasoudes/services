#!/usr/bin/env python3
"""
بررسی وضعیت inbound ها در سیستم
"""

import os
import sys
import django
from django.conf import settings

# تنظیم Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

def check_inbounds():
    """بررسی inbound ها"""
    from xui_servers.models import XUIServer, XUIInbound
    from xui_servers.enhanced_api_models import XUIInboundManager
    
    print("🔍 بررسی وضعیت inbound ها...")
    print("=" * 50)
    
    # بررسی سرورهای فعال
    active_servers = XUIServer.objects.filter(is_active=True)
    print(f"📊 تعداد سرورهای فعال: {active_servers.count()}")
    
    for server in active_servers:
        print(f"\n🖥️ سرور: {server.name}")
        print(f"   🌐 آدرس: {server.host}:{server.port}")
        print(f"   🔧 مسیر: {server.web_base_path}")
        
        # بررسی inbound های موجود در دیتابیس
        db_inbounds = XUIInbound.objects.filter(server=server)
        print(f"   📦 Inbound های دیتابیس: {db_inbounds.count()}")
        
        for inbound in db_inbounds:
            print(f"      - {inbound.tag} (ID: {inbound.xui_inbound_id}, Protocol: {inbound.protocol})")
        
        # تست اتصال به X-UI API
        try:
            inbound_manager = XUIInboundManager(server)
            print(f"   🔗 ایجاد InboundManager: ✅")
            
            # همگام‌سازی inbound ها
            sync_result = inbound_manager.sync_inbounds()
            print(f"   🔄 همگام‌سازی inbound ها: {sync_result}")
            
            # بررسی دوباره پس از همگام‌سازی
            db_inbounds_after = XUIInbound.objects.filter(server=server)
            print(f"   📦 Inbound های جدید: {db_inbounds_after.count()}")
            
            # یافتن بهترین inbound
            best_inbound = inbound_manager.find_best_inbound("vless")
            if best_inbound:
                print(f"   ✅ بهترین inbound: {best_inbound.tag} (ID: {best_inbound.xui_inbound_id})")
            else:
                print(f"   ❌ هیچ inbound مناسبی یافت نشد")
                
                # بررسی همه inbound ها
                all_inbounds = inbound_manager.find_best_inbound()  # بدون protocol filter
                if all_inbounds:
                    print(f"   📋 اولین inbound موجود: {all_inbounds.tag}")
                else:
                    print(f"   ❌ هیچ inbound اصلاً یافت نشد")
        
        except Exception as e:
            print(f"   ❌ خطا در اتصال به X-UI: {e}")
    
    print("\n" + "=" * 50)
    print("✅ بررسی تکمیل شد")

def create_sample_inbound():
    """ایجاد inbound نمونه برای تست"""
    from xui_servers.models import XUIServer, XUIInbound
    
    try:
        server = XUIServer.objects.filter(is_active=True).first()
        if not server:
            print("❌ هیچ سرور فعالی یافت نشد")
            return
        
        # ایجاد inbound نمونه
        sample_inbound, created = XUIInbound.objects.get_or_create(
            server=server,
            xui_inbound_id=1,
            defaults={
                'tag': 'vless-reality',
                'protocol': 'vless',
                'port': 443,
                'settings': '{"clients": []}',
                'stream_settings': '{"network": "tcp"}',
                'sniffing': '{"enabled": true}',
                'is_active': True
            }
        )
        
        if created:
            print(f"✅ Inbound نمونه ایجاد شد: {sample_inbound.tag}")
        else:
            print(f"✅ Inbound موجود است: {sample_inbound.tag}")
            
        return sample_inbound
        
    except Exception as e:
        print(f"❌ خطا در ایجاد inbound نمونه: {e}")
        return None

if __name__ == "__main__":
    print("🚀 شروع بررسی inbound ها...")
    check_inbounds()
    
    print("\n🔧 ایجاد inbound نمونه...")
    create_sample_inbound()
    
    print("\n🔍 بررسی مجدد...")
    check_inbounds()
