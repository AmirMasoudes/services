#!/usr/bin/env python
import os
import sys
import django

sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from accounts.models import UsersModel
from plan.models import ConfingPlansModel
from order.models import OrderUserModel, PayMentModel

def test_improved_functionality():
    """تست عملکرد بهبود یافته"""
    print("🧪 تست عملکرد بهبود یافته...")
    
    try:
        # تست مدل کاربر
        print("\n1. تست مدل کاربر:")
        users = UsersModel.objects.all()
        print(f"   تعداد کاربران: {users.count()}")
        
        for user in users[:3]:  # نمایش 3 کاربر اول
            print(f"   - {user.get_display_name()}")
            print(f"     ID: {user.telegram_id}")
            print(f"     Username: @{user.username or 'بدون یوزرنیم'}")
        
        # تست پلن‌ها
        print("\n2. تست پلن‌ها:")
        plans = ConfingPlansModel.objects.filter(is_deleted=False)
        print(f"   تعداد پلن‌ها: {plans.count()}")
        
        for plan in plans:
            price_text = "🆓 رایگان" if plan.price == 0 else f"💰 {plan.price:,} تومان"
            print(f"   - {plan.name}: {price_text} - {plan.in_volume}MB")
        
        # تست سفارشات
        print("\n3. تست سفارشات:")
        orders = OrderUserModel.objects.all()
        print(f"   تعداد سفارشات: {orders.count()}")
        print(f"   سفارشات فعال: {orders.filter(is_active=True).count()}")
        
        # تست پرداخت‌ها
        print("\n4. تست پرداخت‌ها:")
        payments = PayMentModel.objects.all()
        print(f"   تعداد پرداخت‌ها: {payments.count()}")
        print(f"   پرداخت‌های در انتظار: {payments.filter(is_active=True).count()}")
        
        print("\n✅ تمام تست‌ها موفق بودند!")
        return True
        
    except Exception as e:
        print(f"\n❌ خطا در تست: {e}")
        return False

def test_user_creation():
    """تست ایجاد کاربر جدید"""
    print("\n🧪 تست ایجاد کاربر جدید...")
    
    try:
        # شبیه‌سازی اطلاعات تلگرام
        telegram_data = {
            'id': 123456789,
            'username': 'test_user',
            'full_name': 'کاربر تست',
            'first_name': 'کاربر'
        }
        
        # ایجاد کاربر
        user, created = UsersModel.objects.get_or_create(
            telegram_id=telegram_data['id'],
            defaults={
                "id_tel": str(telegram_data['id']),
                "username_tel": telegram_data['username'] or "",
                "full_name": telegram_data['full_name'] or telegram_data['first_name'] or "کاربر",
                "username": telegram_data['username'] or ""
            }
        )
        
        if created:
            print(f"   ✅ کاربر جدید ایجاد شد: {user.get_display_name()}")
        else:
            print(f"   🔄 کاربر موجود: {user.get_display_name()}")
        
        # تست متدهای جدید
        print(f"   نام نمایشی: {user.get_display_name()}")
        telegram_info = user.get_telegram_info()
        print(f"   اطلاعات تلگرام: {telegram_info}")
        
        return True
        
    except Exception as e:
        print(f"   ❌ خطا در ایجاد کاربر: {e}")
        return False

def test_plan_creation():
    """تست ایجاد پلن جدید"""
    print("\n🧪 تست ایجاد پلن جدید...")
    
    try:
        # ایجاد پلن تستی
        plan = ConfingPlansModel.objects.create(
            name="پلن تست بهبود یافته",
            price=25000,
            in_volume=2500
        )
        
        print(f"   ✅ پلن ایجاد شد: {plan.name}")
        print(f"   قیمت: {plan.price:,} تومان")
        print(f"   حجم: {plan.in_volume}MB")
        
        # حذف پلن تستی
        plan.delete()
        print("   🗑️ پلن تستی حذف شد")
        
        return True
        
    except Exception as e:
        print(f"   ❌ خطا در ایجاد پلن: {e}")
        return False

if __name__ == "__main__":
    print("🚀 شروع تست‌های بهبود یافته...")
    
    # تست عملکرد کلی
    test1 = test_improved_functionality()
    
    # تست ایجاد کاربر
    test2 = test_user_creation()
    
    # تست ایجاد پلن
    test3 = test_plan_creation()
    
    print("\n" + "="*50)
    if all([test1, test2, test3]):
        print("🎉 تمام تست‌ها موفق بودند!")
        print("✅ ربات آماده اجرا است.")
    else:
        print("❌ برخی تست‌ها ناموفق بودند.")
        print("🔧 لطفا مشکلات را بررسی کنید.")
    
    print("="*50) 