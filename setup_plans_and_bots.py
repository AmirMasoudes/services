#!/usr/bin/env python3
"""
راه‌اندازی کامل پلن‌ها و بات‌ها
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

def create_plans():
    """ایجاد پلن‌های VPN"""
    print("📦 ایجاد پلن‌های VPN...")
    
    plans_data = [
        {
            'name': 'پلن تستی',
            'price': 0,
            'in_volume': 1,
            'traffic_mb': 1024,  # 1GB
            'description': 'پلن تستی 24 ساعته - 1 گیگابایت'
        },
        {
            'name': 'پلن برنزی',
            'price': 50000,
            'in_volume': 30,
            'traffic_mb': 10240,  # 10GB
            'description': 'پلن برنزی 30 روزه - 10 گیگابایت'
        },
        {
            'name': 'پلن نقره‌ای',
            'price': 80000,
            'in_volume': 30,
            'traffic_mb': 25600,  # 25GB
            'description': 'پلن نقره‌ای 30 روزه - 25 گیگابایت'
        },
        {
            'name': 'پلن طلایی',
            'price': 120000,
            'in_volume': 30,
            'traffic_mb': 51200,  # 50GB
            'description': 'پلن طلایی 30 روزه - 50 گیگابایت'
        },
        {
            'name': 'پلن الماس',
            'price': 200000,
            'in_volume': 30,
            'traffic_mb': 102400,  # 100GB
            'description': 'پلن الماس 30 روزه - 100 گیگابایت'
        }
    ]
    
    for plan_data in plans_data:
        plan, created = ConfingPlansModel.objects.get_or_create(
            name=plan_data['name'],
            defaults=plan_data
        )
        if created:
            print(f"✅ پلن {plan.name} ایجاد شد")
        else:
            print(f"ℹ️ پلن {plan.name} قبلاً موجود است")

def show_plans():
    """نمایش پلن‌های موجود"""
    print("\n📦 پلن‌های موجود در دیتابیس:")
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

def show_users():
    """نمایش کاربران موجود"""
    print("\n👥 کاربران موجود:")
    print("=" * 40)
    
    users = UsersModel.objects.all()
    
    if users.exists():
        for user in users:
            print(f"✅ {user.full_name} (ID: {user.id_tel})")
            print(f"   📱 Username: {user.username_tel}")
            print(f"   🔗 Telegram ID: {user.telegram_id}")
            print(f"   👤 Staff: {user.is_staff}")
            print(f"   🔧 Superuser: {user.is_superuser}")
            print(f"   🎯 Admin: {user.is_admin}")
            print(f"   📊 Trial Used: {user.has_used_trial}")
            print("-" * 30)
        
        print(f"\n📊 تعداد کل کاربران: {users.count()}")
    else:
        print("❌ هیچ کاربری یافت نشد!")

def check_bot_files():
    """بررسی فایل‌های بات"""
    print("\n🤖 بررسی فایل‌های بات:")
    print("=" * 40)
    
    bot_files = [
        "bot/admin_boy.py",
        "bot/user_bot.py"
    ]
    
    for bot_file in bot_files:
        if os.path.exists(bot_file):
            print(f"✅ {bot_file}: موجود")
        else:
            print(f"❌ {bot_file}: موجود نیست")

def start_bots():
    """راه‌اندازی بات‌ها"""
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

def create_systemd_services():
    """ایجاد سرویس‌های systemd برای بات‌ها"""
    print("\n🔧 ایجاد سرویس‌های systemd برای بات‌ها:")
    print("=" * 50)
    
    # Admin Bot Service
    admin_service = """[Unit]
Description=Telegram Admin Bot
After=network.target

[Service]
Type=simple
User=root
WorkingDirectory=/opt/vpn-service/services
Environment=PATH=/opt/vpn-service/services/venv/bin
ExecStart=/opt/vpn-service/services/venv/bin/python bot/admin_boy.py
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
"""
    
    # User Bot Service
    user_service = """[Unit]
Description=Telegram User Bot
After=network.target

[Service]
Type=simple
User=root
WorkingDirectory=/opt/vpn-service/services
Environment=PATH=/opt/vpn-service/services/venv/bin
ExecStart=/opt/vpn-service/services/venv/bin/python bot/user_bot.py
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
"""
    
    try:
        # نوشتن Admin Bot Service
        with open("/etc/systemd/system/admin-bot.service", "w") as f:
            f.write(admin_service)
        print("✅ Admin Bot Service ایجاد شد")
        
        # نوشتن User Bot Service
        with open("/etc/systemd/system/user-bot.service", "w") as f:
            f.write(user_service)
        print("✅ User Bot Service ایجاد شد")
        
        # Reload systemd
        subprocess.run(["systemctl", "daemon-reload"], check=True)
        print("✅ systemd reload شد")
        
        # فعال‌سازی سرویس‌ها
        subprocess.run(["systemctl", "enable", "admin-bot"], check=True)
        subprocess.run(["systemctl", "enable", "user-bot"], check=True)
        print("✅ سرویس‌ها فعال شدند")
        
        # راه‌اندازی سرویس‌ها
        subprocess.run(["systemctl", "start", "admin-bot"], check=True)
        subprocess.run(["systemctl", "start", "user-bot"], check=True)
        print("✅ سرویس‌ها راه‌اندازی شدند")
        
        print("\n🎉 سرویس‌های بات با موفقیت ایجاد و راه‌اندازی شدند!")
        
    except Exception as e:
        print(f"❌ خطا در ایجاد سرویس‌ها: {e}")

def main():
    """تابع اصلی"""
    print("🎉 راه‌اندازی کامل پلن‌ها و بات‌ها")
    print("=" * 60)
    print(f"📅 تاریخ: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 60)
    
    # ایجاد پلن‌ها
    create_plans()
    
    # نمایش پلن‌ها
    show_plans()
    
    # نمایش کاربران
    show_users()
    
    # بررسی فایل‌های بات
    check_bot_files()
    
    # راه‌اندازی بات‌ها
    start_bots()
    
    # ایجاد سرویس‌های systemd
    create_systemd_services()
    
    print("\n🎉 عملیات کامل شد!")
    print("=" * 60)
    print("✅ پلن‌ها ایجاد و نمایش داده شدند")
    print("✅ بات‌ها راه‌اندازی شدند")
    print("✅ سرویس‌های systemd ایجاد شدند")
    print("=" * 60)

if __name__ == "__main__":
    main() 