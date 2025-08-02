#!/usr/bin/env python3
"""
ایجاد superuser
"""

import os
import django

# تنظیم Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from django.contrib.auth import get_user_model
User = get_user_model()

def create_superuser():
    """ایجاد superuser"""
    print("   ایجاد superuser...")
    
    try:
        # بررسی وجود superuser
        if User.objects.filter(username='admin').exists():
            print("✅ Superuser قبلاً موجود است")
            return
        
        # ایجاد superuser
        user = User.objects.create_user(
            username='admin',
            email='admin@example.com',
            password='YourSecurePassword123!@#'
        )
        user.is_staff = True
        user.is_superuser = True
        user.save()
        
        print("✅ Superuser با موفقیت ایجاد شد")
        print("   Username: admin")
        print("🔑 Password: YourSecurePassword123!@#")
        
    except Exception as e:
        print(f"❌ خطا در ایجاد superuser: {e}")

if __name__ == "__main__":
    create_superuser()
