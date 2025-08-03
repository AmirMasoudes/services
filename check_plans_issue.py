#!/usr/bin/env python3
"""
بررسی مشکل پلن‌ها در ربات
"""

import os
import sys
import django

# تنظیم Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from plan.models import ConfingPlansModel
from django.db import models

def check_plans_issue():
    """بررسی مشکل پلن‌ها"""
    print("🔍 بررسی مشکل پلن‌ها...")
    
    try:
        # بررسی تمام پلن‌ها
        all_plans = ConfingPlansModel.objects.all()
        print(f"📊 تعداد کل پلن‌ها: {all_plans.count()}")
        
        for plan in all_plans:
            print(f"📦 {plan.name}")
            print(f"  - ID: {plan.id}")
            print(f"  - قیمت: {plan.price:,} تومان")
            print(f"  - حجم: {plan.in_volume} MB")
            print(f"  - فعال: {plan.is_active}")
            print(f"  - حذف شده: {plan.is_deleted}")
            print(f"  - created_at: {plan.created_at}")
            print(f"  - updated_at: {plan.updated_at}")
            print("---")
        
        # بررسی پلن‌های فعال
        active_plans = ConfingPlansModel.objects.filter(is_active=True)
        print(f"\n✅ پلن‌های فعال: {active_plans.count()}")
        
        # بررسی پلن‌های غیرحذف شده
        non_deleted_plans = ConfingPlansModel.objects.filter(is_deleted=False)
        print(f"🗑️ پلن‌های غیرحذف شده: {non_deleted_plans.count()}")
        
        # بررسی پلن‌های فعال و غیرحذف شده
        available_plans = ConfingPlansModel.objects.filter(is_active=True, is_deleted=False)
        print(f"🛒 پلن‌های در دسترس: {available_plans.count()}")
        
        if available_plans.count() == 0:
            print("❌ هیچ پلن در دسترسی یافت نشد!")
            print("🔧 بررسی فیلدهای پلن‌ها...")
            
            for plan in all_plans:
                print(f"🔍 {plan.name}:")
                print(f"  - is_active: {plan.is_active}")
                print(f"  - is_deleted: {plan.is_deleted}")
                
                # اگر پلن فعال است اما حذف شده، آن را اصلاح کنیم
                if plan.is_active and plan.is_deleted:
                    plan.is_deleted = False
                    plan.save()
                    print(f"  ✅ is_deleted به False تغییر یافت")
        
    except Exception as e:
        print(f"❌ خطا در بررسی پلن‌ها: {e}")

def fix_plans():
    """اصلاح پلن‌ها"""
    print("\n🔧 اصلاح پلن‌ها...")
    
    try:
        # بررسی و اصلاح پلن‌های فعال که حذف شده‌اند
        plans = ConfingPlansModel.objects.filter(is_active=True, is_deleted=True)
        print(f"📊 تعداد پلن‌های فعال که حذف شده‌اند: {plans.count()}")
        
        for plan in plans:
            plan.is_deleted = False
            plan.save()
            print(f"✅ {plan.name} اصلاح شد")
        
        # بررسی پلن‌های غیرفعال که حذف نشده‌اند
        inactive_plans = ConfingPlansModel.objects.filter(is_active=False, is_deleted=False)
        print(f"📊 تعداد پلن‌های غیرفعال: {inactive_plans.count()}")
        
        for plan in inactive_plans:
            plan.is_active = True
            plan.save()
            print(f"✅ {plan.name} فعال شد")
        
        # بررسی نهایی
        available_plans = ConfingPlansModel.objects.filter(is_active=True, is_deleted=False)
        print(f"✅ پلن‌های در دسترس نهایی: {available_plans.count()}")
        
    except Exception as e:
        print(f"❌ خطا در اصلاح پلن‌ها: {e}")

def test_bot_plan_query():
    """تست کوئری ربات برای پلن‌ها"""
    print("\n🤖 تست کوئری ربات برای پلن‌ها...")
    
    try:
        # همان کوئری که در ربات استفاده می‌شود
        plans = ConfingPlansModel.objects.filter(is_deleted=False)
        print(f"📊 نتیجه کوئری ربات: {plans.count()} پلن")
        
        for plan in plans:
            print(f"✅ {plan.name} - {plan.price:,} تومان")
        
        # تست کوئری با فیلتر فعال
        active_plans = ConfingPlansModel.objects.filter(is_active=True, is_deleted=False)
        print(f"📊 پلن‌های فعال: {active_plans.count()}")
        
    except Exception as e:
        print(f"❌ خطا در تست کوئری: {e}")

def main():
    """تابع اصلی"""
    print("🎉 بررسی و حل مشکل پلن‌ها")
    print("=" * 50)
    
    # بررسی مشکل
    check_plans_issue()
    
    # اصلاح پلن‌ها
    fix_plans()
    
    # تست کوئری ربات
    test_bot_plan_query()
    
    print("\n🎉 عملیات کامل شد!")

if __name__ == "__main__":
    main() 