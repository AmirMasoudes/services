# راهنمای استارت بات‌های تلگرام

## 🔍 بررسی توکن‌ها

قبل از استارت بات، توکن‌ها را بررسی کنید:

```bash
python start_bot.py --check
```

## 🚀 استارت بات‌ها

### روش 1: استارت جداگانه (توصیه می‌شود)

#### ربات کاربر:
```bash
# Windows
.\venv\Scripts\Activate.ps1
python start_bot.py --user

# Linux/Mac
source venv/bin/activate
python start_bot.py --user
```

#### ربات ادمین:
```bash
# Windows
.\venv\Scripts\Activate.ps1
python start_bot.py --admin

# Linux/Mac
source venv/bin/activate
python start_bot.py --admin
```

### روش 2: استارت مستقیم

#### ربات کاربر:
```bash
python bot/user_bot.py
```

#### ربات ادمین:
```bash
python bot/admin_bot.py
```

### روش 3: استارت همزمان (دو ترمینال)

**ترمینال 1:**
```bash
python start_bot.py --user
```

**ترمینال 2:**
```bash
python start_bot.py --admin
```

## ⚠️ مشکلات رایج

### مشکل 1: توکن تنظیم نشده
```
[ERROR] توکن ربات کاربر تنظیم نشده است!
```

**راه حل:**
1. فایل `config.env` را باز کنید
2. `USER_BOT_TOKEN` و `ADMIN_BOT_TOKEN` را تنظیم کنید
3. دوباره استارت کنید

### مشکل 2: Django setup نشده
```
django.core.exceptions.AppRegistryNotReady
```

**راه حل:**
```bash
# اطمینان از فعال بودن venv
.\venv\Scripts\Activate.ps1  # Windows
source venv/bin/activate      # Linux/Mac

# بررسی Django
python manage.py check
```

### مشکل 3: وابستگی‌ها نصب نشده
```
ModuleNotFoundError: No module named 'telegram'
```

**راه حل:**
```bash
pip install -r requirements.txt
```

### مشکل 4: بات استارت نمی‌شود
```
❌ خطا در اجرای ربات
```

**راه حل:**
1. بررسی توکن‌ها: `python start_bot.py --check`
2. بررسی لاگ‌ها برای خطاهای دقیق
3. اطمینان از اتصال اینترنت
4. بررسی فایروال و پورت‌ها

## 📝 دستورات مفید

### بررسی وضعیت بات:
```bash
python start_bot.py --check
```

### تست اتصال:
```bash
python manage.py shell
>>> from django.conf import settings
>>> print(settings.USER_BOT_TOKEN)
>>> print(settings.ADMIN_BOT_TOKEN)
```

## 🔧 عیب‌یابی

### لاگ‌ها را بررسی کنید:
```bash
# لاگ‌های Django
python manage.py runserver

# لاگ‌های بات (در خروجی ترمینال)
```

### بررسی تنظیمات:
```bash
# بررسی config.env
cat config.env | grep BOT_TOKEN

# بررسی settings.py
python manage.py shell
>>> from django.conf import settings
>>> settings.USER_BOT_TOKEN
```

## 📞 پشتیبانی

اگر مشکل حل نشد:
1. لاگ‌های خطا را ذخیره کنید
2. خروجی `python start_bot.py --check` را بررسی کنید
3. با تیم توسعه تماس بگیرید

