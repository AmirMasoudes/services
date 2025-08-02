#!/usr/bin/env python3
import os
import sys
import django
import uuid
import random
import string

# تنظیم Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from xui_servers.models import XUIServer, UserConfig
from accounts.models import UsersModel
from xui_servers import settings as xui_settings

def create_simple_user_config():
    """ایجاد کانفیگ ساده برای کاربر"""
    print("🔧 ایجاد کانفیگ ساده برای کاربر...")
    
    # دریافت سرور X-UI
    server = XUIServer.objects.filter(is_active=True).first()
    if not server:
        print("❌ سرور X-UI فعالی یافت نشد")
        return
    
    print(f"🖥️ سرور: {server.name}")
    print(f" آدرس: {server.host}:{server.port}")
    
    # ایجاد کاربر تستی
    test_user, created = UsersModel.objects.get_or_create(
        telegram_id=999999,
        defaults={
            'id_tel': '999999',
            'username_tel': 'testuser',
            'full_name': 'کاربر تست ساده',
            'username': 'testuser'
        }
    )
    
    print(f"👤 کاربر: {test_user.full_name} (ID: {test_user.id})")
    
    # تولید کانفیگ ساده
    print("\n📊 تولید کانفیگ ساده...")
    
    # انتخاب دامنه فیک تصادفی
    fake_domain = random.choice(xui_settings.FAKE_DOMAINS)
    
    # انتخاب کلید عمومی تصادفی
    public_key = random.choice(xui_settings.REALITY_PUBLIC_KEYS)
    
    # تولید shortId تصادفی
    short_id = ''.join(random.choices(string.hexdigits.lower(), k=8))
    
    # تولید UUID برای کاربر
    user_uuid = str(uuid.uuid4())
    
    # تولید پورت تصادفی
    port = random.randint(10000, 65000)
    
    # تولید کانفیگ VLess Reality
    config_data = f"vless://{user_uuid}@{server.host}:{port}?type=tcp&security=reality&sni={fake_domain}&fp=chrome&pbk={public_key}&sid={short_id}&spx=%2F#{test_user.full_name}"
    
    print(f"📋 کانفیگ تولید شده:")
    print(f"  - پورت: {port}")
    print(f"  - دامنه: {fake_domain}")
    print(f"  - کلید عمومی: {public_key[:20]}...")
    print(f"  - Short ID: {short_id}")
    print(f"  - UUID: {user_uuid}")
    
    # ذخیره در دیتابیس
    print("\n📊 ذخیره در دیتابیس...")
    
    config_name = f"پلن تستی {test_user.full_name} (VLESS)"
    
    user_config = UserConfig.objects.create(
        user=test_user,
        server=server,
        xui_inbound_id=0,  # فعلاً 0 قرار می‌دهیم
        xui_user_id=test_user.id,
        config_name=config_name,
        config_data=config_data,
        protocol="vless",
        is_trial=True,
        created_at=django.utils.timezone.now()
    )
    
    print(f"✅ کانفیگ با موفقیت ایجاد شد:")
    print(f"  - نام: {user_config.config_name}")
    print(f"  - ID: {user_config.id}")
    print(f"  - پروتکل: {user_config.protocol}")
    print(f"  - تستی: {user_config.is_trial}")
    
    # نمایش کانفیگ
    print(f"\n📋 کانفیگ کامل:")
    print(config_data)
    
    print("\n🎉 ایجاد کانفیگ ساده کامل شد!")

def create_multiple_user_configs():
    """ایجاد کانفیگ برای چندین کاربر"""
    print("\n🔧 ایجاد کانفیگ برای چندین کاربر...")
    
    # دریافت سرور X-UI
    server = XUIServer.objects.filter(is_active=True).first()
    if not server:
        print("❌ سرور X-UI فعالی یافت نشد")
        return
    
    # ایجاد چندین کاربر تستی
    test_users = []
    for i in range(1, 4):
        user, created = UsersModel.objects.get_or_create(
            telegram_id=999000 + i,
            defaults={
                'id_tel': f'99900{i}',
                'username_tel': f'testuser{i}',
                'full_name': f'کاربر تست {i}',
                'username': f'testuser{i}'
            }
        )
        test_users.append(user)
        print(f"👤 کاربر {i}: {user.full_name} (ID: {user.id})")
    
    # ایجاد کانفیگ برای هر کاربر
    for i, user in enumerate(test_users, 1):
        print(f"\n📊 ایجاد کانفیگ برای کاربر {i}...")
        
        # انتخاب دامنه فیک تصادفی
        fake_domain = random.choice(xui_settings.FAKE_DOMAINS)
        
        # انتخاب کلید عمومی تصادفی
        public_key = random.choice(xui_settings.REALITY_PUBLIC_KEYS)
        
        # تولید shortId تصادفی
        short_id = ''.join(random.choices(string.hexdigits.lower(), k=8))
        
        # تولید UUID برای کاربر
        user_uuid = str(uuid.uuid4())
        
        # تولید پورت تصادفی
        port = random.randint(10000, 65000)
        
        # تولید کانفیگ VLess Reality
        config_data = f"vless://{user_uuid}@{server.host}:{port}?type=tcp&security=reality&sni={fake_domain}&fp=chrome&pbk={public_key}&sid={short_id}&spx=%2F#{user.full_name}"
        
        # ذخیره در دیتابیس
        config_name = f"پلن تستی {user.full_name} (VLESS)"
        
        user_config = UserConfig.objects.create(
            user=user,
            server=server,
            xui_inbound_id=i,  # شماره کاربر
            xui_user_id=user.id,
            config_name=config_name,
            config_data=config_data,
            protocol="vless",
            is_trial=True,
            created_at=django.utils.timezone.now()
        )
        
        print(f"✅ کانفیگ کاربر {i} ایجاد شد:")
        print(f"  - نام: {user_config.config_name}")
        print(f"  - پورت: {port}")
        print(f"  - دامنه: {fake_domain}")
    
    print("\n🎉 ایجاد کانفیگ برای چندین کاربر کامل شد!")

if __name__ == "__main__":
    create_simple_user_config()
    create_multiple_user_configs() 