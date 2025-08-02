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
from plan.models import ConfingPlansModel
from xui_servers import settings as xui_settings

def test_simple_config_system():
    """تست سیستم کانفیگ ساده"""
    print("�� تست سیستم کانفیگ ساده...")
    
    # دریافت سرور X-UI
    server = XUIServer.objects.filter(is_active=True).first()
    if not server:
        print("❌ سرور X-UI فعالی یافت نشد")
        return
    
    print(f"✅ سیستم کانفیگ ایجاد شد")
    print(f"🖥️ سرور: {server.name}")
    
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
    
    print(f"👤 کاربر: {test_user.full_name}")
    
    # تست ایجاد کانفیگ تستی
    print("\n📊 ایجاد کانفیگ تستی...")
    from xui_servers.services import SimpleConfigService
    config_service = SimpleConfigService()
    
    trial_config, message = config_service.create_trial_config(test_user, "vless")
    
    if trial_config:
        print(f"✅ کانفیگ تستی ایجاد شد:")
        print(f"  - نام: {trial_config.config_name}")
        print(f"  - ID: {trial_config.id}")
        print(f"  - پروتکل: {trial_config.protocol}")
        print(f"  - انقضا: {trial_config.expires_at}")
        print(f"\n📋 کانفیگ تستی:")
        print(trial_config.config_data)
    else:
        print(f"❌ خطا در ایجاد کانفیگ تستی: {message}")
    
    # تست ایجاد کانفیگ پولی
    print("\n📊 ایجاد کانفیگ پولی...")
    
    # ایجاد پلن تستی
    test_plan, created = ConfingPlansModel.objects.get_or_create(
        name="پلن تستی",
        defaults={
            'name': 'پلن تستی',
            'traffic_mb': 1024,  # 1GB
            'price': 10000,
            'duration_days': 30,
            'is_active': True
        }
    )
    
    paid_config, message = config_service.create_paid_config(test_user, test_plan, "vless")
    
    if paid_config:
        print(f"✅ کانفیگ پولی ایجاد شد:")
        print(f"  - نام: {paid_config.config_name}")
        print(f"  - ID: {paid_config.id}")
        print(f"  - پروتکل: {paid_config.protocol}")
        print(f"  - انقضا: {paid_config.expires_at}")
        print(f"\n📋 کانفیگ پولی:")
        print(paid_config.config_data)
    else:
        print(f"❌ خطا در ایجاد کانفیگ پولی: {message}")
    
    print("\n�� تست سیستم کانفیگ ساده کامل شد!")

if __name__ == "__main__":
    test_simple_config_system()