#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
اسکریپت بارگذاری داده‌های اولیه
این اسکریپت داده‌های اولیه را به صورت خودکار در دیتابیس قرار می‌دهد
"""

import os
import sys
import django

# تنظیم encoding برای Windows
if sys.platform == 'win32':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

# تنظیم Django
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from accounts.models import UsersModel
from plan.models import ConfingPlansModel
from xui_servers.models import XUIServer
from django.conf import settings
from django.contrib.auth import get_user_model

def create_superuser():
    """ایجاد superuser برای پنل ادمین"""
    User = get_user_model()
    
    # بررسی وجود superuser
    if not User.objects.filter(is_superuser=True).exists():
        print("[*] ایجاد superuser...")
        try:
            superuser = User.objects.create_superuser(
                id_tel='admin',
                username_tel='admin',
                full_name='مدیر سیستم',
                password=settings.ADMIN_PASSWORD,
                telegram_id=settings.ADMIN_USER_IDS[0] if settings.ADMIN_USER_IDS else None,
                username='admin'
            )
            superuser.is_staff = True
            superuser.is_admin = True
            superuser.save()
            print(f"[OK] Superuser ایجاد شد: admin / {settings.ADMIN_PASSWORD}")
        except Exception as e:
            print(f"[WARN] Superuser از قبل وجود دارد یا خطا: {e}")
    else:
        print("[OK] Superuser از قبل وجود دارد")

def create_default_plans():
    """ایجاد پلن‌های پیش‌فرض"""
    print("[*] ایجاد پلن‌های پیش‌فرض...")
    
    plans_data = [
        {
            'name': 'پلن تستی',
            'price': 0,
            'in_volume': 0,
            'traffic_mb': 0,
            'is_active': True,
            'description': 'پلن تستی 24 ساعته رایگان'
        },
        {
            'name': 'پلن یک ماهه - 50 گیگ',
            'price': 50000,
            'in_volume': 50,
            'traffic_mb': 51200,  # 50 GB
            'is_active': True,
            'description': 'پلن یک ماهه با حجم 50 گیگابایت'
        },
        {
            'name': 'پلن یک ماهه - 100 گیگ',
            'price': 80000,
            'in_volume': 100,
            'traffic_mb': 102400,  # 100 GB
            'is_active': True,
            'description': 'پلن یک ماهه با حجم 100 گیگابایت'
        },
        {
            'name': 'پلن یک ماهه - 200 گیگ',
            'price': 120000,
            'in_volume': 200,
            'traffic_mb': 204800,  # 200 GB
            'is_active': True,
            'description': 'پلن یک ماهه با حجم 200 گیگابایت'
        },
        {
            'name': 'پلن یک ماهه - نامحدود',
            'price': 150000,
            'in_volume': 0,
            'traffic_mb': 0,  # نامحدود
            'is_active': True,
            'description': 'پلن یک ماهه با حجم نامحدود'
        },
    ]
    
    created_count = 0
    for plan_data in plans_data:
        plan, created = ConfingPlansModel.objects.get_or_create(
            name=plan_data['name'],
            defaults=plan_data
        )
        if created:
            created_count += 1
            print(f"  [OK] پلن ایجاد شد: {plan.name}")
        else:
            print(f"  [SKIP] پلن از قبل وجود دارد: {plan.name}")
    
    print(f"[OK] {created_count} پلن جدید ایجاد شد")

def create_xui_server():
    """ایجاد سرور X-UI پیش‌فرض"""
    print("[*] ایجاد سرور X-UI پیش‌فرض...")
    
    server_data = {
        'name': 'سرور اصلی علی رضا',
        'host': settings.XUI_DEFAULT_HOST,
        'port': settings.XUI_DEFAULT_PORT,
        'username': settings.XUI_DEFAULT_USERNAME,
        'password': settings.XUI_DEFAULT_PASSWORD,
        'web_base_path': settings.XUI_WEB_BASE_PATH,
        'is_active': True
    }
    
    server, created = XUIServer.objects.get_or_create(
        host=server_data['host'],
        port=server_data['port'],
        defaults=server_data
    )
    
    if created:
        print(f"[OK] سرور X-UI ایجاد شد: {server.name}")
    else:
        # به‌روزرسانی اطلاعات
        for key, value in server_data.items():
            setattr(server, key, value)
        server.save()
        print(f"[OK] سرور X-UI به‌روزرسانی شد: {server.name}")
    
    return server

def main():
    """تابع اصلی"""
    print("=" * 60)
    print("[*] شروع بارگذاری داده‌های اولیه...")
    print("=" * 60)
    
    try:
        # ایجاد superuser
        create_superuser()
        print()
        
        # ایجاد پلن‌های پیش‌فرض
        create_default_plans()
        print()
        
        # ایجاد سرور X-UI
        create_xui_server()
        print()
        
        print("=" * 60)
        print("[OK] بارگذاری داده‌های اولیه با موفقیت انجام شد!")
        print("=" * 60)
        print("\n[*] اطلاعات ورود به پنل ادمین:")
        print(f"   URL: http://localhost:8000/admin/")
        print(f"   Username: admin")
        print(f"   Password: {settings.ADMIN_PASSWORD}")
        print()
        
    except Exception as e:
        print(f"[ERROR] خطا در بارگذاری داده‌ها: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == '__main__':
    main()

