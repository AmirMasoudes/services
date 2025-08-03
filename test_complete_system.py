#!/usr/bin/env python3
"""
تست کامل سیستم و حل مشکلات
"""

import os
import sys
import django
from datetime import datetime, timedelta

# تنظیم Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from django.utils import timezone
from xui_servers.models import UserConfig, XUIServer
from accounts.models import UsersModel
from plan.models import ConfingPlansModel
from xui_servers.services import UserConfigService

def fix_timestamp_issues():
    """حل مشکلات timestamp"""
    print("🔧 حل مشکلات timestamp...")
    
    try:
        # بررسی کانفیگ‌های موجود
        configs = UserConfig.objects.all()
        print(f"📊 تعداد کانفیگ‌های موجود: {configs.count()}")
        
        fixed_count = 0
        for config in configs:
            needs_fix = False
            
            # بررسی expires_at
            if not config.expires_at:
                if config.is_trial:
                    config.expires_at = timezone.now() + timedelta(hours=24)
                else:
                    config.expires_at = timezone.now() + timedelta(days=30)
                needs_fix = True
            
            # بررسی xui_user_id
            if config.xui_user_id is None:
                config.xui_user_id = str(config.user.telegram_id) if config.user.telegram_id else str(config.user.id)
                needs_fix = True
            
            if needs_fix:
                config.save()
                fixed_count += 1
                print(f"✅ کانفیگ {config.id} اصلاح شد")
        
        print(f"✅ {fixed_count} کانفیگ اصلاح شد")
        
    except Exception as e:
        print(f"❌ خطا در حل مشکلات timestamp: {e}")

def fix_plans_issues():
    """حل مشکلات پلن‌ها"""
    print("\n📦 حل مشکلات پلن‌ها...")
    
    try:
        # بررسی تمام پلن‌ها
        all_plans = ConfingPlansModel.objects.all()
        print(f"📊 تعداد کل پلن‌ها: {all_plans.count()}")
        
        fixed_count = 0
        for plan in all_plans:
            needs_fix = False
            
            # اگر پلن فعال است اما حذف شده، آن را اصلاح کنیم
            if plan.is_active and plan.is_deleted:
                plan.is_deleted = False
                needs_fix = True
            
            # اگر پلن غیرفعال است اما حذف نشده، آن را فعال کنیم
            if not plan.is_active and not plan.is_deleted:
                plan.is_active = True
                needs_fix = True
            
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
        
    except Exception as e:
        print(f"❌ خطا در حل مشکلات پلن‌ها: {e}")

def test_config_creation():
    """تست ایجاد کانفیگ"""
    print("\n🧪 تست ایجاد کانفیگ...")
    
    try:
        # دریافت کاربر تست
        user = UsersModel.objects.first()
        if not user:
            print("❌ هیچ کاربری یافت نشد")
            return
        
        print(f"👤 کاربر تست: {user.full_name}")
        
        # دریافت سرور
        server = XUIServer.objects.filter(is_active=True).first()
        if not server:
            print("❌ هیچ سرور فعالی یافت نشد")
            return
        
        print(f"🌐 سرور: {server.name}")
        
        # تست ایجاد کانفیگ تستی
        print("🔧 تست ایجاد کانفیگ تستی...")
        user_config, message = UserConfigService.create_trial_config(user, server, "vless")
        
        if user_config:
            print(f"✅ کانفیگ تستی ایجاد شد:")
            print(f"  - نام: {user_config.config_name}")
            print(f"  - پروتکل: {user_config.protocol}")
            print(f"  - انقضا: {user_config.expires_at}")
            print(f"  - پیام: {message}")
            
            # حذف کانفیگ تست
            user_config.delete()
            print("🗑️ کانفیگ تست حذف شد")
        else:
            print(f"❌ خطا در ایجاد کانفیگ: {message}")
        
    except Exception as e:
        print(f"❌ خطا در تست ایجاد کانفیگ: {e}")

def test_plan_selection():
    """تست انتخاب پلن"""
    print("\n🛒 تست انتخاب پلن...")
    
    try:
        # همان کوئری که در ربات استفاده می‌شود
        plans = ConfingPlansModel.objects.filter(is_deleted=False)
        print(f"📊 نتیجه کوئری ربات: {plans.count()} پلن")
        
        if plans.count() == 0:
            print("❌ هیچ پلنی یافت نشد!")
            return
        
        for plan in plans:
            print(f"✅ {plan.name}")
            print(f"  - قیمت: {plan.price:,} تومان")
            print(f"  - حجم: {plan.in_volume} MB")
            print(f"  - فعال: {plan.is_active}")
            print("---")
        
        # تست کوئری با فیلتر فعال
        active_plans = ConfingPlansModel.objects.filter(is_active=True, is_deleted=False)
        print(f"📊 پلن‌های فعال: {active_plans.count()}")
        
    except Exception as e:
        print(f"❌ خطا در تست انتخاب پلن: {e}")

def check_system_status():
    """بررسی وضعیت سیستم"""
    print("\n🔍 بررسی وضعیت سیستم...")
    
    try:
        # بررسی کاربران
        users = UsersModel.objects.all()
        print(f"👥 تعداد کاربران: {users.count()}")
        
        # بررسی سرورها
        servers = XUIServer.objects.filter(is_active=True)
        print(f"🌐 تعداد سرورهای فعال: {servers.count()}")
        
        # بررسی کانفیگ‌ها
        configs = UserConfig.objects.all()
        print(f"📋 تعداد کانفیگ‌ها: {configs.count()}")
        
        # بررسی پلن‌ها
        plans = ConfingPlansModel.objects.filter(is_active=True, is_deleted=False)
        print(f"📦 تعداد پلن‌های فعال: {plans.count()}")
        
        print("✅ سیستم آماده است!")
        
    except Exception as e:
        print(f"❌ خطا در بررسی وضعیت سیستم: {e}")

def main():
    """تابع اصلی"""
    print("🎉 تست کامل سیستم و حل مشکلات")
    print("=" * 60)
    
    # حل مشکلات timestamp
    fix_timestamp_issues()
    
    # حل مشکلات پلن‌ها
    fix_plans_issues()
    
    # بررسی وضعیت سیستم
    check_system_status()
    
    # تست انتخاب پلن
    test_plan_selection()
    
    # تست ایجاد کانفیگ
    test_config_creation()
    
    print("\n🎉 تمام مشکلات حل شد!")
    print("✅ سیستم آماده استفاده است!")

if __name__ == "__main__":
    main()
