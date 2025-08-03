#!/usr/bin/env python3
"""
تست مدل‌های جدید API X-UI
"""

import os
import sys
import django
import requests
import json
import random
from datetime import datetime, timedelta

# تنظیم Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from xui_servers.models import XUIServer
from xui_servers.services import XUIService
from xui_servers.api_models import XUIAPIBuilder, XUIAPIClient, XUIClient, XUIInbound

def test_new_api_models():
    """تست مدل‌های جدید API"""
    print("🔧 تست مدل‌های جدید API X-UI...")
    
    try:
        # دریافت سرور فعال
        server = XUIServer.objects.filter(is_active=True).first()
        if not server:
            print("❌ هیچ سرور فعالی یافت نشد")
            return False
        
        print(f"🌐 سرور: {server.name}")
        print(f"🔗 آدرس: {server.host}:{server.port}")
        
        # تست XUI Service
        xui_service = XUIService(server)
        
        # تست لاگین
        print("🔐 تست لاگین...")
        if not xui_service.login():
            print("❌ لاگین ناموفق")
            return False
        
        print("✅ لاگین موفق")
        
        # تست ایجاد Inbound با مدل جدید
        print("\n🔧 تست ایجاد Inbound با مدل جدید...")
        
        # ایجاد Inbound
        inbound_id = xui_service.create_user_specific_inbound(
            user_id=999999,
            protocol="vless",
            port=random.randint(10000, 65000)
        )
        
        if not inbound_id:
            print("❌ خطا در ایجاد Inbound")
            return False
        
        print(f"✅ Inbound با ID {inbound_id} ایجاد شد")
        
        # تست ایجاد Client
        print("\n👤 تست ایجاد Client...")
        
        # ایجاد Client
        client = XUIAPIBuilder.create_client(
            email=f"test_user_{random.randint(1000, 9999)}",
            total_gb=10,
            expiry_time=int((datetime.now() + timedelta(days=30)).timestamp() * 1000)
        )
        
        print(f"✅ Client ایجاد شد: {client.email}")
        
        # اضافه کردن Client به Inbound
        api_client = XUIAPIClient(xui_service.base_url, xui_service.session)
        success = api_client.add_client(inbound_id, client)
        
        if success:
            print(f"✅ Client با موفقیت به Inbound {inbound_id} اضافه شد")
        else:
            print(f"❌ خطا در اضافه کردن Client به Inbound {inbound_id}")
            return False
        
        # تست دریافت Inbound ها
        print("\n📋 تست دریافت Inbound ها...")
        inbounds = xui_service.get_inbounds()
        
        if inbounds:
            print(f"✅ {len(inbounds)} Inbound یافت شد")
            for i, inbound in enumerate(inbounds[:3]):
                print(f"  {i+1}. {inbound.get('remark', 'بدون نام')} - پورت: {inbound.get('port', 'نامشخص')}")
        else:
            print("⚠️ هیچ Inbound یافت نشد")
        
        return True
        
    except Exception as e:
        print(f"❌ خطا در تست: {e}")
        return False

def test_api_builder():
    """تست API Builder"""
    print("\n🔧 تست API Builder...")
    
    try:
        # تست ایجاد Inbound Payload
        inbound = XUIAPIBuilder.create_inbound_payload(
            port=12345,
            protocol="vless",
            remark="Test Inbound"
        )
        
        print("✅ Inbound Payload ایجاد شد")
        print(f"📊 پورت: {inbound.port}")
        print(f"📊 پروتکل: {inbound.protocol}")
        print(f"📊 نام: {inbound.remark}")
        
        # تست ایجاد Client
        client = XUIAPIBuilder.create_client(
            email="test@example.com",
            total_gb=5,
            expiry_time=0
        )
        
        print("✅ Client ایجاد شد")
        print(f"📊 Email: {client.email}")
        print(f"📊 ID: {client.id}")
        print(f"📊 Sub ID: {client.sub_id}")
        
        # تست اضافه کردن Client به Inbound
        inbound.add_client(client)
        print("✅ Client به Inbound اضافه شد")
        
        # تست تبدیل به دیکشنری
        inbound_dict = inbound.to_dict()
        print("✅ Inbound به دیکشنری تبدیل شد")
        print(f"📊 تعداد فیلدها: {len(inbound_dict)}")
        
        return True
        
    except Exception as e:
        print(f"❌ خطا در تست API Builder: {e}")
        return False

def main():
    """تابع اصلی"""
    print("🎉 تست مدل‌های جدید API X-UI")
    print("=" * 50)
    
    # تست API Builder
    builder_success = test_api_builder()
    
    if builder_success:
        print("\n✅ تست API Builder موفق")
        
        # تست مدل‌های جدید
        models_success = test_new_api_models()
        
        if models_success:
            print("\n🎉 تمام تست‌ها موفق بودند!")
        else:
            print("\n❌ خطا در تست مدل‌های جدید")
    else:
        print("\n❌ خطا در تست API Builder")
    
    print("\n🎉 عملیات کامل شد!")

if __name__ == "__main__":
    main() 