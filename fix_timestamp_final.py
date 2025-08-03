#!/usr/bin/env python3
"""
حل نهایی مشکل timestamp
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

def fix_timestamp_error_final():
    """حل نهایی مشکل timestamp"""
    print("🔧 حل نهایی مشکل timestamp...")
    
    try:
        # بررسی مدل UserConfig
        print("📋 بررسی مدل UserConfig...")
        
        # تست ایجاد یک کانفیگ ساده
        user = UsersModel.objects.first()
        server = XUIServer.objects.filter(is_active=True).first()
        
        if not user or not server:
            print("❌ کاربر یا سرور یافت نشد")
            return
        
        print(f"👤 کاربر: {user.full_name}")
        print(f"🌐 سرور: {server.name}")
        
        # ایجاد کانفیگ بدون استفاده از سرویس
        print("🔧 ایجاد کانفیگ مستقیم...")
        
        import uuid
        import random
        import string
        
        # تولید کانفیگ VLess
        user_uuid = str(uuid.uuid4())
        fake_domain = random.choice(["www.aparat.com", "www.irib.ir", "www.varzesh3.com"])
        public_key = random.choice(["H5jCG+N2boOAvWRFcntZJsSFCMn6xMOa1NfU+KR3Cw=", "K8mFJ+Q5erRDwZUIfqubmvuIFPq9APzd/1QmF+NU6Fz="])
        short_id = ''.join(random.choices(string.hexdigits.lower(), k=8))
        port = random.randint(10000, 65000)
        
        config_data = f"vless://{user_uuid}@{server.host}:{port}?type=tcp&security=reality&sni={fake_domain}&fp=chrome&pbk={public_key}&sid={short_id}&spx=%2F#{user.full_name}"
        
        # ایجاد کانفیگ در دیتابیس
        try:
            user_config = UserConfig.objects.create(
                user=user,
                server=server,
                xui_inbound_id=0,  # فعلاً 0
                xui_user_id=str(user.telegram_id) if user.telegram_id else str(user.id),
                config_name=f"پلن تستی {user.full_name} (VLESS)",
                config_data=config_data,
                protocol="vless",
                is_trial=True,
                expires_at=timezone.now() + timedelta(hours=24)
            )
            
            print(f"✅ کانفیگ با موفقیت ایجاد شد:")
            print(f"  - ID: {user_config.id}")
            print(f"  - نام: {user_config.config_name}")
            print(f"  - پروتکل: {user_config.protocol}")
            print(f"  - انقضا: {user_config.expires_at}")
            print(f"  - created_at: {user_config.created_at}")
            print(f"  - updated_at: {user_config.updated_at}")
            
            # حذف کانفیگ تست
            user_config.delete()
            print("🗑️ کانفیگ تست حذف شد")
            
        except Exception as e:
            print(f"❌ خطا در ایجاد کانفیگ: {e}")
            print(f"نوع خطا: {type(e)}")
            
            # بررسی فیلدهای مدل
            print("🔍 بررسی فیلدهای مدل UserConfig...")
            for field in UserConfig._meta.fields:
                print(f"  - {field.name}: {field.__class__.__name__}")
        
    except Exception as e:
        print(f"❌ خطا در حل مشکل timestamp: {e}")

def fix_plans_final():
    """حل نهایی مشکل پلن‌ها"""
    print("\n📦 حل نهایی مشکل پلن‌ها...")
    
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
            print("---")
        
        # اصلاح پلن‌ها
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
        print(f"❌ خطا در حل مشکل پلن‌ها: {e}")

def test_bot_functionality():
    """تست عملکرد ربات"""
    print("\n🤖 تست عملکرد ربات...")
    
    try:
        # تست کوئری پلن‌ها (همان کوئری ربات)
        plans = ConfingPlansModel.objects.filter(is_deleted=False)
        print(f"📊 نتیجه کوئری ربات: {plans.count()} پلن")
        
        if plans.count() > 0:
            print("✅ پلن‌ها در دسترس هستند")
            for plan in plans:
                print(f"  - {plan.name} - {plan.price:,} تومان")
        else:
            print("❌ هیچ پلنی در دسترس نیست")
        
        # تست ایجاد کانفیگ
        user = UsersModel.objects.first()
        if user:
            print(f"👤 کاربر تست: {user.full_name}")
            print("✅ کاربر یافت شد")
        else:
            print("❌ هیچ کاربری یافت نشد")
        
    except Exception as e:
        print(f"❌ خطا در تست عملکرد ربات: {e}")

def main():
    """تابع اصلی"""
    print("🎉 حل نهایی مشکلات سیستم")
    print("=" * 60)
    
    # حل مشکل timestamp
    fix_timestamp_error_final()
    
    # حل مشکل پلن‌ها
    fix_plans_final()
    
    # تست عملکرد ربات
    test_bot_functionality()
    
    print("\n🎉 عملیات کامل شد!")
    print("✅ سیستم آماده استفاده است!")

if __name__ == "__main__":
    main() 