#!/usr/bin/env python3
"""
راه‌اندازی Django
"""

import os
import sys
import subprocess
import django
from django.core.management import execute_from_command_line

def run_cmd(cmd, desc=""):
    print(f"�� {desc}")
    print(f"�� {cmd}")
    result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
    if result.returncode == 0:
        print(f"✅ {desc}")
        return True
    else:
        print(f"❌ {desc}: {result.stderr}")
        return False

def setup_django():
    """راه‌اندازی Django"""
    print("🚀 راه‌اندازی Django...")
    print("=" * 40)
    
    # تنظیم Django
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
    django.setup()
    
    # اجرای migrations
    print("\n📊 اجرای migrations...")
    run_cmd("python manage.py makemigrations", "Make migrations")
    run_cmd("python manage.py migrate", "Apply migrations")
    
    # جمع‌آوری فایل‌های static
    print("\n📁 جمع‌آوری فایل‌های static...")
    run_cmd("python manage.py collectstatic --noinput", "Collect static files")
    
    # ایجاد superuser
    print("\n�� ایجاد superuser...")
    superuser_script = """
from django.contrib.auth import get_user_model
User = get_user_model()

if not User.objects.filter(username='admin').exists():
    User.objects.create_superuser('admin', 'admin@example.com', 'YourSecurePassword123!@#')
    print('Superuser created successfully')
else:
    print('Superuser already exists')
"""
    
    with open("/tmp/create_superuser.py", "w") as f:
        f.write(superuser_script)
    
    run_cmd("python manage.py shell < /tmp/create_superuser.py", "Create superuser")
    run_cmd("rm -f /tmp/create_superuser.py", "Clean up temp file")
    
    print("\n✅ Django آماده است!")

def test_django():
    """تست Django"""
    print("\n🧪 تست Django...")
    
    # تست سرور
    print("�� تست سرور Django...")
    run_cmd("python manage.py check", "Django check")
    
    # تست اتصال دیتابیس
    print("\n��️ تست اتصال دیتابیس...")
    db_test_script = """
from django.db import connection
cursor = connection.cursor()
cursor.execute("SELECT version();")
result = cursor.fetchone()
print(f'Database connection successful: {result[0]}')
"""
    
    with open("/tmp/test_db.py", "w") as f:
        f.write(db_test_script)
    
    run_cmd("python manage.py shell < /tmp/test_db.py", "Test database")
    run_cmd("rm -f /tmp/test_db.py", "Clean up temp file")

def main():
    print("🚀 راه‌اندازی کامل Django")
    print("=" * 50)
    
    # راه‌اندازی Django
    setup_django()
    
    # تست Django
    test_django()
    
    print("\n🎉 Django با موفقیت راه‌اندازی شد!")
    print("=" * 50)
    print("📊 اطلاعات ورود:")
    print("�� Username: admin")
    print("🔑 Password: YourSecurePassword123!@#")
    print("�� Admin URL: http://38.54.105.124:8000/admin/")

if __name__ == "__main__":
    main()
