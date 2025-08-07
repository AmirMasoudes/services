# تنظیمات فعلی سیستم

## 🔧 تنظیمات X-UI سنایی

- **آدرس سرور**: `156.244.31.37`
- **پورت**: `50987`
- **نام کاربری**: `bUZC0Iovb9`
- **رمز عبور**: `4jb7doDQZg`
- **مسیر وب**: `/YvIhWQ3Pt6cHGXegE4/`
- **آدرس دسترسی**: `https://time.amirprogrammer.ir:50987/YvIhWQ3Pt6cHGXegE4/`
- **SSL**: فعال

## 🤖 تنظیمات ربات‌های تلگرام

### ربات ادمین

- **توکن**: `8450508816:AAFE6XAj8QvA9iIP12whrKxYRtgsoHFCiFU`

### ربات کاربران

- **توکن**: `8202994859:AAGg68pT5HGR1W9D4pxqnAGeKoZKrD9Dnzs`

## ⚠️ موارد باقی‌مانده

تنها موردی که باید تنظیم کنید:

1. **TELEGRAM_ADMIN_ID**: ID تلگرام شما (از @userinfobot دریافت کنید)
2. **XUI_DEFAULT_INBOUND_ID**: شماره inbound موجود در X-UI

## 🚀 مراحل بعدی

```bash
# 1. تنظیم ID ادمین در فایل env_config.env
nano env_config.env

# 2. اجرای اسکریپت استقرار
./deploy.sh

# 3. ایجاد کاربر ادمین
source venv/bin/activate
python manage.py createsuperuser

# 4. تست سیستم
python test_sanaei_connection.py
```

## 📋 دستورات مفید

```bash
# بررسی وضعیت سرویس‌ها
sudo supervisorctl status

# راه‌اندازی مجدد
sudo supervisorctl restart django
sudo supervisorctl restart telegram_bot

# مشاهده لاگ‌ها
sudo tail -f /var/log/django.log
sudo tail -f /var/log/telegram_bot.log
```
