# راهنمای سریع تنظیم فایل .env

## 🚀 مراحل سریع

### 1. کپی کردن فایل نمونه
```bash
cp env_config.env .env
```

### 2. ویرایش فایل .env
فایل `.env` را باز کرده و مقادیر زیر را تنظیم کنید:

#### 🔑 تنظیمات اجباری
```bash
# کلید امنیتی Django - حتماً تغییر دهید!
SECRET_KEY=your-very-secure-secret-key-here

# توکن ربات ادمین - از @BotFather دریافت کنید
ADMIN_BOT_TOKEN=1234567890:ABCdefGHIjklMNOpqrsTUVwxyz

# توکن ربات کاربران - از @BotFather دریافت کنید
USER_BOT_TOKEN=1234567890:XYZabcDEFghiJKLmnoPQRstuVWXyz

# رمز عبور ادمین
ADMIN_PASSWORD=your-secure-admin-password

# ID های ادمین تلگرام (با کاما جدا کنید)
ADMIN_USER_IDS=123456789,987654321

# آدرس سرور X-UI
XUI_DEFAULT_HOST=your-xui-server.com

# نام کاربری X-UI
XUI_DEFAULT_USERNAME=admin

# رمز عبور X-UI
XUI_DEFAULT_PASSWORD=your-xui-password
```

### 3. تست تنظیمات
```bash
python load_env.py
```

### 4. اجرای پروژه
```bash
# نصب وابستگی‌ها
pip install -r requirements.txt

# اجرای مایگریشن‌ها
python manage.py makemigrations
python manage.py migrate

# ایجاد سوپر یوزر
python manage.py createsuperuser

# اجرای سرور
python manage.py runserver

# اجرای ربات‌ها
python start_bots.py
```

## 📋 چک‌لیست تنظیمات

- [ ] فایل `.env` ایجاد شده
- [ ] `SECRET_KEY` تغییر یافته
- [ ] `ADMIN_BOT_TOKEN` تنظیم شده
- [ ] `USER_BOT_TOKEN` تنظیم شده
- [ ] `ADMIN_PASSWORD` تنظیم شده
- [ ] `ADMIN_USER_IDS` تنظیم شده
- [ ] `XUI_DEFAULT_HOST` تنظیم شده
- [ ] `XUI_DEFAULT_USERNAME` تنظیم شده
- [ ] `XUI_DEFAULT_PASSWORD` تنظیم شده

## 🔒 نکات امنیتی

1. **هرگز فایل `.env` را در Git قرار ندهید**
2. **کلیدهای امنیتی قوی انتخاب کنید**
3. **توکن‌های ربات را محافظت کنید**
4. **رمزهای عبور قوی استفاده کنید**

## 🆘 عیب‌یابی

### خطای "ModuleNotFoundError: No module named 'dotenv'"
```bash
pip install python-dotenv
```

### خطای "Invalid token"
- توکن ربات را از @BotFather دریافت کنید
- مطمئن شوید که ربات فعال است

### خطای اتصال به X-UI
- آدرس و پورت سرور را بررسی کنید
- نام کاربری و رمز عبور را چک کنید

## 📞 پشتیبانی

برای اطلاعات بیشتر، فایل `ENV_SETUP_GUIDE.md` را مطالعه کنید. 