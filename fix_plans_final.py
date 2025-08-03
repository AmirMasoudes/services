#!/usr/bin/env python3
"""
حل نهایی مشکل پلن‌ها
"""

import os
import sys
import django

# تنظیم Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from plan.models import ConfingPlansModel

def fix_plans_final():
    """حل نهایی مشکل پلن‌ها"""
    print("📦 حل نهایی مشکل پلن‌ها...")
    
    try:
        # بررسی تمام پلن‌ها
        all_plans = ConfingPlansModel.objects.all()
        print(f"📊 تعداد کل پلن‌ها: {all_plans.count()}")
        
        # اصلاح پلن‌ها
        fixed_count = 0
        for plan in all_plans:
            needs_fix = False
            
            # اگر is_deleted None است، آن را False کنیم
            if plan.is_deleted is None:
                plan.is_deleted = False
                needs_fix = True
                print(f"🔧 پلن {plan.name}: is_deleted از None به False تغییر یافت")
            
            # اگر پلن فعال است اما حذف شده، آن را اصلاح کنیم
            elif plan.is_active and plan.is_deleted:
                plan.is_deleted = False
                needs_fix = True
                print(f"🔧 پلن {plan.name}: is_deleted از True به False تغییر یافت")
            
            # اگر پلن غیرفعال است اما حذف نشده، آن را فعال کنیم
            elif not plan.is_active and not plan.is_deleted:
                plan.is_active = True
                needs_fix = True
                print(f"🔧 پلن {plan.name}: is_active از False به True تغییر یافت")
            
            if needs_fix:
                plan.save()
                fixed_count += 1
                print(f"✅ پلن {plan.name} اصلاح شد")
        
        print(f"✅ {fixed_count} پلن اصلاح شد")
        
        # بررسی نهایی
        available_plans = ConfingPlansModel.objects.filter(is_active=True, is_deleted=False)
        print(f"🛒 پلن‌های در دسترس نهایی: {available_plans.count()}")
        
        for plan in available_plans:
            print(f"  ✅ {plan.name} - {plan.price:,} تومان")
        
        # تست کوئری ربات
        bot_plans = ConfingPlansModel.objects.filter(is_deleted=False)
        print(f"🤖 نتیجه کوئری ربات: {bot_plans.count()} پلن")
        
        if bot_plans.count() > 0:
            print("✅ پلن‌ها در دسترس هستند")
            for plan in bot_plans:
                print(f"  - {plan.name} - {plan.price:,} تومان")
        else:
            print("❌ هیچ پلنی در دسترس نیست")
        
    except Exception as e:
        print(f"❌ خطا در حل مشکل پلن‌ها: {e}")

def main():
    """تابع اصلی"""
    print("🎉 حل نهایی مشکل پلن‌ها")
    print("=" * 50)
    
    # حل مشکل پلن‌ها
    fix_plans_final()
    
    print("\n🎉 عملیات کامل شد!")
    print("✅ سیستم آماده استفاده است!")

if __name__ == "__main__":
    main() 