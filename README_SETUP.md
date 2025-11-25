# راهنمای نصب و راه‌اندازی سیستم VPN Bot

## 📋 پیش‌نیازها

- Python 3.8 یا بالاتر
- pip
- دسترسی به سرور X-UI

## 🚀 نصب خودکار (توصیه می‌شود)

### Windows:
```powershell
.\auto_setup.ps1
```

### Linux/Mac:
```bash
chmod +x auto_setup.sh
./auto_setup.sh
```

## 📝 نصب دستی

### 1. ایجاد محیط مجازی
```bash
# Windows
python -m venv venv
.\venv\Scripts\Activate.ps1

# Linux/Mac
python3 -m venv venv
source venv/bin/activate
```

### 2. نصب وابستگی‌ها
```bash
pip install -r requirements.txt
```

### 3. تنظیم فایل config.env
فایل `config.env` را باز کرده و تنظیمات خود را وارد کنید:
- توکن‌های ربات تلگرام
- اطلاعات سرور X-UI
- IP و دامنه سرور

### 4. اجرای Migrations
```bash
python manage.py migrate
```

### 5. جمع‌آوری Static Files
```bash
python manage.py collectstatic --noinput
```

### 6. بارگذاری داده‌های اولیه
```bash
python load_initial_data.py
```

## ⚙️ تنظیمات

### فایل config.env

تمام تنظیمات در فایل `config.env` قرار دارد:

```env
# تنظیمات ربات‌های تلگرام
ADMIN_BOT_TOKEN=8496586253:AAFJLxxstDIqIOosPZ78V2ibdfMYlBNws1I
USER_BOT_TOKEN=8496586253:AAFJLxxstDIqIOosPZ78V2ibdfMYlBNws1I
ADMIN_PASSWORD=admin123
ADMIN_USER_IDS=936877715

# تنظیمات سرور X-UI
XUI_DEFAULT_HOST=time.amirprogrammer.ir
XUI_DEFAULT_PORT=50987
XUI_DEFAULT_USERNAME=bUZC0Iovb9
XUI_DEFAULT_PASSWORD=4jb7doDQZg
XUI_WEB_BASE_PATH=/YvIhWQ3Pt6cHGXegE4/

# تنظیمات IP و سرور
SERVER_IP=156.244.31.37
SERVER_DOMAIN=time.amirprogrammer.ir
SERVER_PORT=8000
```

## 🎯 اجرای سرور

### Development:
```bash
python manage.py runserver 0.0.0.0:8000
```

### Production (با Gunicorn):
```bash
gunicorn config.wsgi:application --bind 0.0.0.0:8000
```

## 📊 دسترسی به پنل ادمین

بعد از نصب و بارگذاری داده‌های اولیه:

- **URL**: http://localhost:8000/admin/
- **Username**: admin
- **Password**: admin123 (یا همان چیزی که در config.env تنظیم کرده‌اید)

## 📦 داده‌های اولیه

اسکریپت `load_initial_data.py` به صورت خودکار:
- ✅ Superuser ایجاد می‌کند
- ✅ پلن‌های پیش‌فرض ایجاد می‌کند:
  - پلن تستی (رایگان)
  - پلن یک ماهه - 50 گیگ
  - پلن یک ماهه - 100 گیگ
  - پلن یک ماهه - 200 گیگ
  - پلن یک ماهه - نامحدود
- ✅ سرور X-UI پیش‌فرض ایجاد می‌کند

## 🔧 عیب‌یابی

### مشکل در نصب وابستگی‌ها:
```bash
pip install --upgrade pip
pip install -r requirements.txt --force-reinstall
```

### مشکل در Migrations:
```bash
python manage.py makemigrations
python manage.py migrate
```

### مشکل در Static Files:
```bash
python manage.py collectstatic --noinput --clear
```

## 📞 پشتیبانی

برای مشکلات و سوالات، لطفا با تیم توسعه تماس بگیرید.

