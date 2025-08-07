#!/usr/bin/env python3
"""
تست API جدید X-UI
"""

import os
import sys
import django
import requests
import json
from datetime import datetime

# تنظیم Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from xui_servers.models import XUIServer
from xui_servers.enhanced_api_models import XUIEnhancedService, XUIClientManager, XUIInboundManager

def test_xui_connection():
    """تست اتصال به X-UI"""
    print("🔧 تست اتصال به X-UI...")
    
    # یافتن سرور فعال
    server = XUIServer.objects.filter(is_active=True).first()
    if not server:
        print("❌ هیچ سرور فعالی یافت نشد!")
        return False
    
    print(f"🖥️ سرور: {server.name} ({server.host}:{server.port})")
    
    # تست سرویس پیشرفته
    enhanced_service = XUIEnhancedService(server)
    
    # تست لاگین
    print("🔐 تلاش برای ورود...")
    if enhanced_service.login():
        print("✅ ورود موفق!")
    else:
        print("❌ خطا در ورود!")
        return False
    
    # تست دریافت inbound ها
    print("📋 دریافت inbound ها...")
    inbounds = enhanced_service.get_inbounds()
    print(f"✅ {len(inbounds)} inbound دریافت شد")
    
    for inbound in inbounds:
        print(f"  • {inbound.get('remark', 'نامشخص')} (پورت: {inbound.get('port', 'نامشخص')})")
    
    return True

def test_client_creation():
    """تست ایجاد کلاینت"""
    print("\n👤 تست ایجاد کلاینت...")
    
    server = XUIServer.objects.filter(is_active=True).first()
    if not server:
        print("❌ هیچ سرور فعالی یافت نشد!")
        return False
    
    enhanced_service = XUIEnhancedService(server)
    
    # لاگین
    if not enhanced_service.login():
        print("❌ خطا در ورود!")
        return False
    
    # دریافت inbound ها
    inbounds = enhanced_service.get_inbounds()
    if not inbounds:
        print("❌ هیچ inbound یافت نشد!")
        return False
    
    # انتخاب اولین inbound
    inbound = inbounds[0]
    inbound_id = inbound.get('id')
    
    print(f"🔗 انتخاب inbound: {inbound.get('remark')} (ID: {inbound_id})")
    
    # ایجاد تنظیمات کلاینت تستی
    client_settings = enhanced_service.create_client_settings(
        email="test_user_123",
        total_gb=1,
        expiry_days=1
    )
    
    print("🔧 تنظیمات کلاینت ایجاد شد:")
    print(json.dumps(client_settings, indent=2, ensure_ascii=False))
    
    # اضافه کردن کلاینت
    print("➕ اضافه کردن کلاینت به inbound...")
    if enhanced_service.add_client_to_inbound(inbound_id, client_settings):
        print("✅ کلاینت با موفقیت اضافه شد!")
        return True
    else:
        print("❌ خطا در اضافه کردن کلاینت!")
        return False

def test_inbound_manager():
    """تست مدیر inbound"""
    print("\n🔗 تست مدیر inbound...")
    
    server = XUIServer.objects.filter(is_active=True).first()
    if not server:
        print("❌ هیچ سرور فعالی یافت نشد!")
        return False
    
    inbound_manager = XUIInboundManager(server)
    
    # همگام‌سازی inbound ها
    print("🔄 همگام‌سازی inbound ها...")
    synced_count = inbound_manager.sync_inbounds()
    print(f"✅ {synced_count} inbound همگام‌سازی شد")
    
    # یافتن inbound مناسب
    print("🔍 یافتن inbound مناسب...")
    best_inbound = inbound_manager.find_best_inbound("vless")
    if best_inbound:
        print(f"✅ بهترین inbound: {best_inbound.remark} (پورت: {best_inbound.port})")
    else:
        print("❌ هیچ inbound مناسبی یافت نشد!")
    
    return True

def test_client_manager():
    """تست مدیر کلاینت"""
    print("\n👤 تست مدیر کلاینت...")
    
    server = XUIServer.objects.filter(is_active=True).first()
    if not server:
        print("❌ هیچ سرور فعالی یافت نشد!")
        return False
    
    client_manager = XUIClientManager(server)
    
    # یافتن inbound مناسب
    inbound_manager = XUIInboundManager(server)
    inbound = inbound_manager.find_best_inbound("vless")
    
    if not inbound:
        print("❌ هیچ inbound مناسبی یافت نشد!")
        return False
    
    print(f"🔗 استفاده از inbound: {inbound.remark}")
    
    # تست تولید کانفیگ
    print("🔧 تست تولید کانفیگ...")
    config_data = client_manager._generate_config_data(inbound, {
        "id": "test-uuid-123",
        "email": "test@example.com"
    })
    
    print(f"✅ کانفیگ تولید شد: {config_data[:100]}...")
    
    return True

def main():
    """تابع اصلی"""
    print("🚀 شروع تست API جدید X-UI")
    print("=" * 50)
    
    # تست اتصال
    if not test_xui_connection():
        print("❌ تست اتصال ناموفق!")
        return
    
    # تست مدیر inbound
    if not test_inbound_manager():
        print("❌ تست مدیر inbound ناموفق!")
        return
    
    # تست مدیر کلاینت
    if not test_client_manager():
        print("❌ تست مدیر کلاینت ناموفق!")
        return
    
    # تست ایجاد کلاینت (اختیاری)
    print("\n⚠️ تست ایجاد کلاینت (اختیاری)...")
    test_client_creation()
    
    print("\n✅ تمام تست‌ها با موفقیت انجام شد!")

if __name__ == "__main__":
    main() 