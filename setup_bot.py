#!/usr/bin/env python
import os
import sys
import django

# اضافه کردن مسیر پروژه به sys.path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# تنظیم ماژول تنظیمات
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')

# راه‌اندازی جنگو
django.setup()

from plan.models import ConfingPlansModel
from accounts.models import UsersModel

def setup_test_plans():
    """ایجاد پلن‌های تستی"""
    try:
        # حذف پلن‌های موجود
        ConfingPlansModel.objects.all().delete()
        
        # ایجاد پلن تستی رایگان
        test_plan = ConfingPlansModel.objects.create(
            name="تست رایگان",
            price=0,
            in_volume=100
        )
        print(f"✅ پلن تستی ایجاد شد: {test_plan.name}")
        
        # ایجاد پلن VIP
        vip_plan = ConfingPlansModel.objects.create(
            name="VIP",
            price=50000,
            in_volume=5000
        )
        print(f"✅ پلن VIP ایجاد شد: {vip_plan.name}")
        
        # ایجاد پلن پریمیوم
        premium_plan = ConfingPlansModel.objects.create(
            name="پریمیوم",
            price=100000,
            in_volume=10000
        )
        print(f"✅ پلن پریمیوم ایجاد شد: {premium_plan.name}")
        
        # ایجاد پلن اقتصادی
        basic_plan = ConfingPlansModel.objects.create(
            name="اقتصادی",
            price=25000,
            in_volume=2500
        )
        print(f"✅ پلن اقتصادی ایجاد شد: {basic_plan.name}")
        
        print("\n🎉 تمام پلن‌ها با موفقیت ایجاد شدند!")
        
    except Exception as e:
        print(f"❌ خطا در ایجاد پلن‌ها: {e}")

def check_database():
    """بررسی وضعیت دیتابیس"""
    try:
        users_count = UsersModel.objects.count()
        plans_count = ConfingPlansModel.objects.count()
        
        print(f"📊 وضعیت دیتابیس:")
        print(f"👥 تعداد کاربران: {users_count}")
        print(f"📦 تعداد پلن‌ها: {plans_count}")
        
        if plans_count > 0:
            print("\n📋 پلن‌های موجود:")
            for plan in ConfingPlansModel.objects.all():
                is_test = " (تست)" if "تست" in plan.name.lower() else ""
                price_text = "🆓 رایگان" if plan.price == 0 else f"💰 {plan.price:,} تومان"
                print(f"- {plan.name}{is_test}: {price_text} - {plan.in_volume}MB")
        
    except Exception as e:
        print(f"❌ خطا در بررسی دیتابیس: {e}")

def test_user_creation():
    """تست ایجاد کاربر"""
    try:
        # ایجاد یک کاربر تست
        user, created = UsersModel.objects.get_or_create(
            telegram_id=999999999,
            defaults={
                "id_tel": "999999999",
                "username_tel": "test_user",
                "full_name": "کاربر تست",
                "username": "test_user"
            }
        )
        
        if created:
            print(f"✅ کاربر تست ایجاد شد: {user.get_display_name()}")
        else:
            print(f"🔄 کاربر تست موجود: {user.get_display_name()}")
            
    except Exception as e:
        print(f"❌ خطا در ایجاد کاربر تست: {e}")

if __name__ == "__main__":
    print("🚀 راه‌اندازی ربات...")
    
    # بررسی وضعیت دیتابیس
    check_database()
    
    # ایجاد پلن‌های تستی
    setup_test_plans()
    
    # تست ایجاد کاربر
    test_user_creation()
    
    # بررسی نهایی
    check_database()
    
    print("\n✅ راه‌اندازی کامل شد!")
    print("🤖 ربات‌ها آماده اجرا هستند!")
    print("\nبرای اجرای ربات کاربر:")
    print("python bot/user_bot.py")
    print("\nبرای اجرای ربات ادمین:")
    print("python bot/admin_boy.py") 