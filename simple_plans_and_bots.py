#!/usr/bin/env python3
"""
نمایش پلن‌ها و راه‌اندازی بات‌ها - نسخه ساده
"""

import os
import sys
import django
import subprocess
from datetime import datetime

# تنظیم Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from plan.models import ConfingPlansModel
from accounts.models import UsersModel

def show_plans():
    """نمایش پلن‌های موجود"""
    print("📦 پلن‌های موجود در دیتابیس:")
    print("=" * 60)
    
    plans = ConfingPlansModel.objects.filter(is_active=True)
    
    if plans.exists():
        for plan in plans:
            traffic_gb = plan.traffic_mb / 1024 if plan.traffic_mb > 0 else 0
            print(f"✅ {plan.name}")
            print(f"   💰 قیمت: {plan.price:,} تومان")
            print(f"   📊 حجم: {traffic_gb:.1f} GB ({plan.traffic_mb:,} MB)")
            print(f"   ⏰ مدت: {plan.in_volume} روز")
            if plan.description:
                print(f"   📝 توضیحات: {plan.description}")
            print("-" * 40)
        
        print(f"\n📊 تعداد کل پلن‌های فعال: {plans.count()}")
    else:
        print("❌ هیچ پلن فعالی یافت نشد!")
        print("💡 برای ایجاد پلن‌ها از اسکریپت create_plans.py استفاده کنید")

def show_users():
    """نمایش کاربران موجود"""
    print("\n👥 کاربران موجود:")
    print("=" * 40)
    
    users = UsersModel.objects.all()
    
    if users.exists():
        for user in users:
            print(f"✅ {user.full_name} (ID: {user.id_tel})")
            print(f"   📱 Username: {user.username_tel}")
            print(f"   📧 Email: {user.email}")
            print(f"   👤 Staff: {user.is_staff}")
            print(f"   🔧 Superuser: {user.is_superuser}")
            print("-" * 30)
        
        print(f"\n📊 تعداد کل کاربران: {users.count()}")
    else:
        print("❌ هیچ کاربری یافت نشد!")

def start_bots_simple():
    """راه‌اندازی ساده بات‌ها"""
    print("\n🚀 راه‌اندازی بات‌ها:")
    print("=" * 40)
    
    # بررسی فایل‌های بات
    admin_bot = "bot/admin_boy.py"
    user_bot = "bot/user_bot.py"
    
    if not os.path.exists(admin_bot):
        print(f"❌ فایل {admin_bot} یافت نشد!")
        return
    
    if not os.path.exists(user_bot):
        print(f"❌ فایل {user_bot} یافت نشد!")
        return
    
    print("✅ فایل‌های بات موجود هستند")
    
    # راه‌اندازی Admin Bot
    print("\n🔧 راه‌اندازی Admin Bot...")
    try:
        # اجرای Admin Bot در پس‌زمینه
        admin_process = subprocess.Popen([
            "python", admin_bot
        ], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        
        print(f"✅ Admin Bot راه‌اندازی شد (PID: {admin_process.pid})")
    except Exception as e:
        print(f"❌ خطا در راه‌اندازی Admin Bot: {e}")
    
    # راه‌اندازی User Bot
    print("\n👤 راه‌اندازی User Bot...")
    try:
        # اجرای User Bot در پس‌زمینه
        user_process = subprocess.Popen([
            "python", user_bot
        ], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        
        print(f"✅ User Bot راه‌اندازی شد (PID: {user_process.pid})")
    except Exception as e:
        print(f"❌ خطا در راه‌اندازی User Bot: {e}")
    
    print("\n🎉 بات‌ها با موفقیت راه‌اندازی شدند!")

def main():
    """تابع اصلی"""
    print("🎉 نمایش پلن‌ها و راه‌اندازی بات‌ها")
    print("=" * 60)
    print(f"📅 تاریخ: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 60)
    
    # نمایش پلن‌ها
    show_plans()
    
    # نمایش کاربران
    show_users()
    
    # راه‌اندازی بات‌ها
    start_bots_simple()
    
    print("\n🎉 عملیات کامل شد!")
    print("=" * 60)
    print("✅ پلن‌ها نمایش داده شدند")
    print("✅ بات‌ها راه‌اندازی شدند")
    print("=" * 60)

if __name__ == "__main__":
    main() 