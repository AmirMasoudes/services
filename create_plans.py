#!/usr/bin/env python3
import os
import sys
import django

# تنظیم Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from plan.models import ConfingPlansModel

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
    
    print("\n   لیست پلن‌های موجود:")
    for plan in ConfingPlansModel.objects.all():
        print(f"  - {plan.name}: {plan.price:,} تومان - {plan.get_traffic_gb():.1f}GB")

if __name__ == "__main__":
    create_plans()
