#!/usr/bin/env python3
"""
اسکریپت تست برای تنظیمات خودکار X-UI
این اسکریپت قابلیت‌های جدید سیستم را تست می‌کند
"""

import os
import sys
import django
from datetime import datetime

# تنظیم Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from xui_servers.models import XUIServer
from xui_servers.services import XUIService, UserConfigService, ConfigGenerator
from accounts.models import UsersModel
from plan.models import ConfingPlansModel

def test_settings_import():
    """تست import تنظیمات"""
    try:
        from xui_servers import settings as xui_settings
        print("✅ تنظیمات با موفقیت import شد")
        
        # تست تنظیمات اصلی
        print(f"📋 پروتکل پیش‌فرض: {xui_settings.DEFAULT_PROTOCOL}")
        print(f"📋 پورت‌های پیش‌فرض: {xui_settings.PORT_SETTINGS['default_ports']}")
        print(f"📋 زمان انقضای تستی: {xui_settings.EXPIRY_SETTINGS['trial_hours']} ساعت")
        print(f"📋 زمان انقضای پولی: {xui_settings.EXPIRY_SETTINGS['paid_days']} روز")
        
        return True
    except Exception as e:
        print(f"❌ خطا در import تنظیمات: {e}")
        return False

def test_protocol_settings():
    """تست تنظیمات پروتکل‌ها"""
    try:
        from xui_servers import settings as xui_settings
        
        protocols = ["vmess", "vless", "trojan"]
        for protocol in protocols:
            if protocol in xui_settings.PROTOCOL_SETTINGS:
                config = xui_settings.PROTOCOL_SETTINGS[protocol]
                print(f"✅ پروتکل {protocol}: {config['name']} - {config['description']}")
            else:
                print(f"❌ پروتکل {protocol} یافت نشد")
        
        return True
    except Exception as e:
        print(f"❌ خطا در تست تنظیمات پروتکل: {e}")
        return False

def test_config_generator():
    """تست تولیدکننده کانفیگ"""
    try:
        # تست VMess
        vmess_config = ConfigGenerator.generate_vmess_config(
            "test.example.com", 443, "test-uuid-123"
        )
        print(f"✅ کانفیگ VMess تولید شد: {vmess_config[:50]}...")
        
        # تست VLess
        vless_config = ConfigGenerator.generate_vless_config(
            "test.example.com", 443, "test-uuid-123"
        )
        print(f"✅ کانفیگ VLess تولید شد: {vless_config[:50]}...")
        
        # تست Trojan
        trojan_config = ConfigGenerator.generate_trojan_config(
            "test.example.com", 443, "test-password-123"
        )
        print(f"✅ کانفیگ Trojan تولید شد: {trojan_config[:50]}...")
        
        return True
    except Exception as e:
        print(f"❌ خطا در تست تولیدکننده کانفیگ: {e}")
        return False

def test_xui_service_creation():
    """تست ایجاد سرویس X-UI"""
    try:
        # ایجاد سرور تست
        test_server = XUIServer.objects.create(
            name="سرور تست",
            host="test.example.com",
            port=54321,
            username="admin",
            password="password",
            is_active=True
        )
        print(f"✅ سرور تست ایجاد شد: {test_server.name}")
        
        # ایجاد سرویس X-UI
        xui_service = XUIService(test_server)
        print(f"✅ سرویس X-UI ایجاد شد")
        
        # تست تنظیمات
        print(f"📋 URL سرویس: {xui_service.base_url}")
        print(f"📋 نام سرور: {xui_service.server.name}")
        
        # پاک کردن سرور تست
        test_server.delete()
        print("✅ سرور تست پاک شد")
        
        return True
    except Exception as e:
        print(f"❌ خطا در تست سرویس X-UI: {e}")
        return False

def test_naming_formats():
    """تست فرمت‌های نام‌گذاری"""
    try:
        from xui_servers import settings as xui_settings
        
        # تست نام inbound
        inbound_name = xui_settings.INBOUND_NAMING["format"].format(
            prefix=xui_settings.INBOUND_NAMING["prefix"],
            separator=xui_settings.INBOUND_NAMING["separator"],
            protocol="VMESS",
            port=443
        )
        print(f"✅ نام inbound: {inbound_name}")
        
        # تست ایمیل تستی
        trial_email = xui_settings.EMAIL_SETTINGS["trial_format"].format(
            telegram_id=123456789
        )
        print(f"✅ ایمیل تستی: {trial_email}")
        
        # تست ایمیل پولی
        paid_email = xui_settings.EMAIL_SETTINGS["paid_format"].format(
            telegram_id=123456789,
            plan_id=1
        )
        print(f"✅ ایمیل پولی: {paid_email}")
        
        # تست نام کانفیگ تستی
        trial_config_name = xui_settings.CONFIG_NAMING["trial_format"].format(
            protocol="VMESS"
        )
        print(f"✅ نام کانفیگ تستی: {trial_config_name}")
        
        # تست نام کانفیگ پولی
        paid_config_name = xui_settings.CONFIG_NAMING["paid_format"].format(
            plan_name="پلن طلایی",
            protocol="VMESS"
        )
        print(f"✅ نام کانفیگ پولی: {paid_config_name}")
        
        return True
    except Exception as e:
        print(f"❌ خطا در تست فرمت‌های نام‌گذاری: {e}")
        return False

def test_error_messages():
    """تست پیام‌های خطا"""
    try:
        from xui_servers import settings as xui_settings
        
        error_messages = xui_settings.ERROR_MESSAGES
        print("📋 پیام‌های خطا:")
        for key, message in error_messages.items():
            print(f"  - {key}: {message}")
        
        success_messages = xui_settings.SUCCESS_MESSAGES
        print("📋 پیام‌های موفقیت:")
        for key, message in success_messages.items():
            print(f"  - {key}: {message}")
        
        return True
    except Exception as e:
        print(f"❌ خطا در تست پیام‌ها: {e}")
        return False

def test_port_settings():
    """تست تنظیمات پورت"""
    try:
        from xui_servers import settings as xui_settings
        
        port_settings = xui_settings.PORT_SETTINGS
        print(f"📋 تنظیمات پورت:")
        print(f"  - حداقل پورت: {port_settings['min_port']}")
        print(f"  - حداکثر پورت: {port_settings['max_port']}")
        print(f"  - پورت‌های پیش‌فرض: {port_settings['default_ports']}")
        
        # تست تولید پورت تصادفی
        import random
        random_port = random.randint(
            port_settings['min_port'],
            port_settings['max_port']
        )
        print(f"  - پورت تصادفی تولید شده: {random_port}")
        
        return True
    except Exception as e:
        print(f"❌ خطا در تست تنظیمات پورت: {e}")
        return False

def main():
    """تابع اصلی تست"""
    print("🚀 شروع تست تنظیمات خودکار X-UI Bot")
    print("=" * 50)
    
    tests = [
        ("تست Import تنظیمات", test_settings_import),
        ("تست تنظیمات پروتکل", test_protocol_settings),
        ("تست تولیدکننده کانفیگ", test_config_generator),
        ("تست سرویس X-UI", test_xui_service_creation),
        ("تست فرمت‌های نام‌گذاری", test_naming_formats),
        ("تست پیام‌های خطا", test_error_messages),
        ("تست تنظیمات پورت", test_port_settings),
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        print(f"\n🔍 در حال اجرای {test_name}...")
        if test_func():
            passed += 1
            print(f"✅ {test_name} با موفقیت انجام شد")
        else:
            print(f"❌ {test_name} با خطا مواجه شد")
    
    print("\n" + "=" * 50)
    print(f"📊 نتایج تست:")
    print(f"  - کل تست‌ها: {total}")
    print(f"  - موفق: {passed}")
    print(f"  - ناموفق: {total - passed}")
    print(f"  - درصد موفقیت: {(passed/total)*100:.1f}%")
    
    if passed == total:
        print("🎉 تمام تست‌ها با موفقیت انجام شد!")
        return True
    else:
        print("⚠️ برخی تست‌ها با خطا مواجه شدند")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1) 