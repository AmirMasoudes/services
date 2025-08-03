# 🔧 راهنمای حل مشکلات سیستم

## 🚨 مشکلات شناسایی شده:

### 1. خطای "timestamp" در ایجاد کانفیگ
**مشکل:** خطای timestamp در زمان ایجاد کانفیگ VPN

**علت:** تنظیم دستی فیلد `created_at` در کد

**راه حل:**
```bash
# اجرای اسکریپت حل مشکل
cd /opt/vpn-service/services
python test_complete_system.py
```

### 2. مشکل "هیچ پلنی در دسترس نیست"
**مشکل:** ربات پیام "هیچ پلنی در دسترس نیست" نمایش می‌دهد

**علت:** فیلتر `is_deleted=False` در کوئری ربات

**راه حل:**
```bash
# بررسی و اصلاح پلن‌ها
cd /opt/vpn-service/services
python check_plans_issue.py
```

## 🔧 مراحل حل مشکلات:

### مرحله 1: حل مشکل timestamp
```bash
cd /opt/vpn-service/services
python fix_timestamp_error.py
```

### مرحله 2: حل مشکل پلن‌ها
```bash
cd /opt/vpn-service/services
python check_plans_issue.py
```

### مرحله 3: تست کامل سیستم
```bash
cd /opt/vpn-service/services
python test_complete_system.py
```

### مرحله 4: راه‌اندازی مجدد بات‌ها
```bash
# راه‌اندازی مجدد User Bot
systemctl restart user-bot

# بررسی وضعیت
systemctl status user-bot
```

## 📋 بررسی دستی مشکلات:

### بررسی پلن‌ها:
```python
# در Django shell
python manage.py shell

from plan.models import ConfingPlansModel

# بررسی تمام پلن‌ها
plans = ConfingPlansModel.objects.all()
print(f"تعداد کل پلن‌ها: {plans.count()}")

# بررسی پلن‌های فعال
active_plans = ConfingPlansModel.objects.filter(is_active=True)
print(f"پلن‌های فعال: {active_plans.count()}")

# بررسی پلن‌های غیرحذف شده
non_deleted = ConfingPlansModel.objects.filter(is_deleted=False)
print(f"پلن‌های غیرحذف شده: {non_deleted.count()}")

# بررسی پلن‌های در دسترس
available = ConfingPlansModel.objects.filter(is_active=True, is_deleted=False)
print(f"پلن‌های در دسترس: {available.count()}")
```

### اصلاح دستی پلن‌ها:
```python
# اصلاح پلن‌های فعال که حذف شده‌اند
plans_to_fix = ConfingPlansModel.objects.filter(is_active=True, is_deleted=True)
for plan in plans_to_fix:
    plan.is_deleted = False
    plan.save()
    print(f"پلن {plan.name} اصلاح شد")

# فعال کردن پلن‌های غیرفعال
inactive_plans = ConfingPlansModel.objects.filter(is_active=False, is_deleted=False)
for plan in inactive_plans:
    plan.is_active = True
    plan.save()
    print(f"پلن {plan.name} فعال شد")
```

## 🎯 تست نهایی:

### تست ربات:
1. به ربات تلگرام بروید
2. دستور `/start` را بزنید
3. روی "🛒 خرید پلن" کلیک کنید
4. پلن‌ها باید نمایش داده شوند

### تست ایجاد کانفیگ:
1. روی "🎁 پلن تستی" کلیک کنید
2. کانفیگ باید بدون خطا ایجاد شود

## 📞 در صورت بروز مشکل:

### بررسی لاگ‌ها:
```bash
# لاگ‌های User Bot
journalctl -u user-bot --no-pager -n 20

# لاگ‌های Django
tail -f /opt/vpn-service/services/logs/app.log
```

### بررسی وضعیت سرویس‌ها:
```bash
# وضعیت تمام سرویس‌ها
systemctl status django-vpn nginx redis-server postgresql admin-bot user-bot
```

## ✅ پس از حل مشکلات:

1. **پلن‌ها نمایش داده می‌شوند**
2. **کانفیگ‌ها بدون خطا ایجاد می‌شوند**
3. **ربات کاملاً کار می‌کند**

## 🎉 سیستم آماده استفاده است! 