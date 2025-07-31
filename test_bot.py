#!/usr/bin/env python
import os
import sys
import django

sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from accounts.models import UsersModel
from plan.models import ConfingPlansModel

def test_database():
    try:
        users_count = UsersModel.objects.count()
        plans_count = ConfingPlansModel.objects.count()
        print(f"✅ دیتابیس OK - کاربران: {users_count}, پلن‌ها: {plans_count}")
        return True
    except Exception as e:
        print(f"❌ خطا دیتابیس: {e}")
        return False

def test_environment():
    required = ['TELEGRAM_BOT_TOKEN', 'ADMIN_BOT_TOKEN']
    missing = [var for var in required if not os.getenv(var)]
    if missing:
        print(f"❌ متغیرهای محیطی: {missing}")
        return False
    print("✅ متغیرهای محیطی OK")
    return True

if __name__ == "__main__":
    print("🧪 تست ربات...")
    env_ok = test_environment()
    db_ok = test_database()
    
    if env_ok and db_ok:
        print("🎉 ربات آماده است!")
    else:
        print("❌ مشکلاتی وجود دارد.") 
 