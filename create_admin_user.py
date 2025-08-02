#!/usr/bin/env python3
"""
ایجاد superuser برای مدل سفارشی
"""

import os
import django

# تنظیم Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from accounts.models import UsersModel

def create_admin_user():
    """ایجاد superuser"""
    print("�� ایجاد superuser...")
    
    try:
        # بررسی وجود superuser
        if UsersModel.objects.filter(id_tel='admin').exists():
            print("✅ Superuser قبلاً موجود است")
            return
        
        # ایجاد superuser با فیلدهای مورد نیاز
        user = UsersModel.objects.create_superuser(
            id_tel='admin',
            username_tel='admin',
            full_name='Administrator',
            password='YourSecurePassword123!@#'
        )
        
        print("✅ Superuser با موفقیت ایجاد شد")
        print("�� Username: admin")
        print("🔑 Password: YourSecurePassword123!@#")
        print("�� ID Telegram: admin")
        
    except Exception as e:
        print(f"❌ خطا در ایجاد superuser: {e}")

if __name__ == "__main__":
    create_admin_user()
