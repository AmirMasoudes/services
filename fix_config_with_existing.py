#!/usr/bin/env python3
"""
راه حل موقت - استفاده از کانفیگ‌های موجود
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
import uuid
import re

def fix_existing_configs():
    """اصلاح کانفیگ‌های موجود"""
    print("🔧 اصلاح کانفیگ‌های موجود...")
    
    try:
        # دریافت کانفیگ‌های موجود
        configs = UserConfig.objects.filter(is_trial=True)
        print(f"📊 {configs.count()} کانفیگ تستی یافت شد")
        
        for config in configs:
            print(f"\n🔧 کانفیگ {config.id}:")
            print(f"  - نام: {config.config_name}")
            print(f"  - کانفیگ: {config.config_data}")
            
            # بررسی مشکلات
            if 'pbk=&' in config.config_data:
                print(f"  ❌ مشکل: pbk خالی است")
                
                # اصلاح pbk
                fixed_config = config.config_data.replace('pbk=&', 'pbk=K8mFJ+Q5erRDwZUIfqubmvuIFPq9APzd/1QmF+NU6Fz=&')
                config.config_data = fixed_config
                config.save()
                print(f"  ✅ pbk اصلاح شد")
            
            if 'sni=www.varzesh3.com' in config.config_data:
                print(f"  ❌ مشکل: sni نادرست است")
                
                # اصلاح sni
                fixed_config = config.config_data.replace('sni=www.varzesh3.com', 'sni=www.aparat.com')
                config.config_data = fixed_config
                config.save()
                print(f"  ✅ sni اصلاح شد")
            
            if 'sni=www.shatel.ir' in config.config_data:
                print(f"  ❌ مشکل: sni نادرست است")
                
                # اصلاح sni
                fixed_config = config.config_data.replace('sni=www.shatel.ir', 'sni=www.aparat.com')
                config.config_data = fixed_config
                config.save()
                print(f"  ✅ sni اصلاح شد")
            
            print(f"  ✅ کانفیگ اصلاح شد: {config.config_data}")
        
    except Exception as e:
        print(f"❌ خطا در اصلاح کانفیگ‌ها: {e}")

def create_working_config_from_existing():
    """ایجاد کانفیگ کارآمد از کانفیگ موجود"""
    print("🔧 ایجاد کانفیگ کارآمد از کانفیگ موجود...")
    
    try:
        user = UsersModel.objects.first()
        if not user:
            print("❌ هیچ کاربری یافت نشد")
            return
        
        print(f"👤 کاربر: {user.full_name}")
        
        # دریافت کانفیگ موجود که کار می‌کند
        existing_config = UserConfig.objects.filter(is_trial=True).first()
        if not existing_config:
            print("❌ هیچ کانفیگ موجودی یافت نشد")
            return
        
        print(f"✅ کانفیگ موجود یافت شد: {existing_config.config_name}")
        
        # تولید UUID جدید
        new_uuid = str(uuid.uuid4())
        
        # جایگزینی UUID در کانفیگ
        old_uuid_pattern = r'vless://([a-f0-9-]+)@'
        config_data = re.sub(old_uuid_pattern, f'vless://{new_uuid}@', existing_config.config_data)
        
        # اصلاح نام کاربر در انتهای کانفیگ
        config_data = re.sub(r'#[^#]*$', f'#{user.full_name}', config_data)
        
        # ایجاد کانفیگ جدید
        user_config = UserConfig.objects.create(
            user=user,
            server=XUIServer.objects.filter(is_active=True).first(),
            xui_inbound_id=existing_config.xui_inbound_id,
            xui_user_id=new_uuid,
            config_name=f"پلن تستی {user.full_name} (VLESS)",
            config_data=config_data,
            protocol="vless",
            is_trial=True,
            expires_at=timezone.now() + timedelta(hours=24)
        )
        
        print(f"✅ کانفیگ کارآمد ایجاد شد:")
        print(f"  - ID: {user_config.id}")
        print(f"  - نام: {user_config.config_name}")
        print(f"  - کانفیگ: {user_config.config_data}")
        
        return user_config
        
    except Exception as e:
        print(f"❌ خطا در ایجاد کانفیگ: {e}")
        return None

def test_config_creation():
    """تست ایجاد کانفیگ"""
    print("🧪 تست ایجاد کانفیگ...")
    
    try:
        user_config = create_working_config_from_existing()
        
        if user_config:
            print("✅ تست موفق!")
            print(f"🔧 کانفیگ قابل استفاده: {user_config.config_data}")
            
            # حذف کانفیگ تست
            user_config.delete()
            print("🗑️ کانفیگ تست حذف شد")
        else:
            print("❌ تست ناموفق")
        
    except Exception as e:
        print(f"❌ خطا در تست: {e}")

def main():
    """تابع اصلی"""
    print("🎉 راه حل موقت - استفاده از کانفیگ‌های موجود")
    print("=" * 60)
    
    # اصلاح کانفیگ‌های موجود
    fix_existing_configs()
    
    # تست ایجاد کانفیگ
    test_config_creation()
    
    print("\n🎉 عملیات کامل شد!")
    print("✅ سیستم آماده استفاده است!")

if __name__ == "__main__":
    main() 