# 🚀 راهنمای کامل دیپلوی سیستم VPN

## 📋 پیش‌نیازها

### 🖥️ سرور:

- **سیستم عامل:** Ubuntu 20.04+ یا Debian 11+
- **RAM:** حداقل 2GB
- **CPU:** حداقل 2 هسته
- **Storage:** حداقل 20GB
- **دسترسی:** Root

### 🌐 دامنه (اختیاری):

- دامنه برای SSL certificate

## 🚀 مراحل دیپلوی

### 1️⃣ کلون پروژه

```bash
# اتصال به سرور
ssh root@YOUR-SERVER-IP

# کلون پروژه
cd /opt
git clone https://github.com/YOUR-USERNAME/configvpn.git vpn-service
cd vpn-service
```

### 2️⃣ اجرای اسکریپت دیپلوی

```bash
# اجرای اسکریپت کامل دیپلوی
python3 deploy_complete_system.py
```

### 3️⃣ تنظیمات نهایی

#### 🔧 تنظیم توکن‌های ربات‌ها

```bash
# ویرایش فایل .env
nano /opt/vpn-service/services/.env
```

مقادیر زیر را تغییر دهید:

```env
# Telegram Bot Tokens
TELEGRAM_BOT_TOKEN=YOUR_USER_BOT_TOKEN
ADMIN_BOT_TOKEN=YOUR_ADMIN_BOT_TOKEN
```

#### 🔐 تغییر رمزهای پیش‌فرض

```bash
# تغییر رمز Django Admin
cd /opt/vpn-service/services
source ../venv/bin/activate
python manage.py changepassword admin

# تغییر رمز X-UI
x-ui
# سپس گزینه 2 را انتخاب کنید
```

### 4️⃣ تست سیستم

```bash
# بررسی وضعیت سرویس‌ها
systemctl status vpn-django vpn-user-bot vpn-admin-bot x-ui nginx

# تست اتصال‌ها
curl -I http://YOUR-SERVER-IP
curl -I http://YOUR-SERVER-IP:54321
```

## 📊 اطلاعات دسترسی

### 🔐 Admin Panel

- **URL:** `http://YOUR-SERVER-IP/admin`
- **Username:** `admin`
- **Password:** `admin123`

### 🤖 Admin Bot

- **Username:** `@gamramconfigbot`
- **Password:** `admin123`

### 🖥️ X-UI Panel

- **URL:** `http://YOUR-SERVER-IP:54321`
- **Username:** `admin`
- **Password:** `admin123`

## 🔧 ویژگی‌های سیستم

### 👤 برای کاربران:

- ✅ **تست اتوماتیک:** هر کاربر فقط 1 بار
- ✅ **خرید پلن:** شماره کارت + رسید
- ✅ **کانفیگ اتوماتیک:** پس از تایید ادمین

### 🔐 برای ادمین:

- ✅ **تایید/رد پرداخت‌ها**
- ✅ **چت با کاربران**
- ✅ **مدیریت سیستم**

### 🔧 برای سیستم:

- ✅ **Inbound اتوماتیک**
- ✅ **کانفیگ اتوماتیک**
- ✅ **ارسال خودکار**

## 📁 ساختار پروژه

```
/opt/vpn-service/
├── services/                 # کدهای Django
│   ├── accounts/            # مدل‌های کاربران
│   ├── plan/               # مدل‌های پلن‌ها
│   ├── order/              # مدل‌های سفارشات
│   ├── xui_servers/        # مدل‌های سرورهای X-UI
│   ├── bot/                # ربات‌های تلگرام
│   └── config/             # تنظیمات Django
├── venv/                   # محیط Python
└── DEPLOYMENT_SUMMARY.md   # خلاصه دیپلوی
```

## 🔧 دستورات مفید

### 📊 بررسی وضعیت

```bash
# وضعیت سرویس‌ها
systemctl status vpn-django vpn-user-bot vpn-admin-bot x-ui nginx

# لاگ‌های Django
journalctl -u vpn-django -f

# لاگ‌های ربات‌ها
journalctl -u vpn-user-bot -f
journalctl -u vpn-admin-bot -f
```

### 🔄 راه‌اندازی مجدد

```bash
# راه‌اندازی مجدد Django
systemctl restart vpn-django

# راه‌اندازی مجدد ربات‌ها
systemctl restart vpn-user-bot vpn-admin-bot

# راه‌اندازی مجدد X-UI
systemctl restart x-ui
```

### 🔧 مدیریت Django

```bash
cd /opt/vpn-service/services
source ../venv/bin/activate

# اجرای migrations
python manage.py makemigrations
python manage.py migrate

# ایجاد superuser
python manage.py createsuperuser

# جمع‌آوری فایل‌های استاتیک
python manage.py collectstatic --noinput
```

## 🛠️ عیب‌یابی

### ❌ مشکل در اتصال به X-UI

```bash
# بررسی وضعیت X-UI
systemctl status x-ui

# بررسی پورت
netstat -tlnp | grep 54321

# راه‌اندازی مجدد X-UI
systemctl restart x-ui
```

### ❌ مشکل در ربات‌ها

```bash
# بررسی لاگ‌های ربات‌ها
journalctl -u vpn-user-bot --no-pager -n 50
journalctl -u vpn-admin-bot --no-pager -n 50

# بررسی توکن‌ها
cat /opt/vpn-service/services/.env | grep BOT_TOKEN
```

### ❌ مشکل در Django

```bash
# بررسی لاگ‌های Django
journalctl -u vpn-django --no-pager -n 50

# تست Django
cd /opt/vpn-service/services
source ../venv/bin/activate
python manage.py check
```

## 🔒 امنیت

### 🔐 تغییر رمزهای پیش‌فرض

```bash
# تغییر رمز Django Admin
cd /opt/vpn-service/services
source ../venv/bin/activate
python manage.py changepassword admin

# تغییر رمز X-UI
x-ui
# گزینه 2: تغییر رمز
```

### 🛡️ تنظیم Firewall

```bash
# بررسی وضعیت Firewall
ufw status

# اضافه کردن پورت‌های جدید
ufw allow PORT_NUMBER/tcp
```

### 🔒 نصب SSL Certificate

```bash
# نصب Certbot
apt install certbot python3-certbot-nginx

# دریافت SSL certificate
certbot --nginx -d YOUR-DOMAIN.com
```

## 📈 مانیتورینگ

### 📊 آمار سیستم

```bash
# بررسی استفاده از CPU و RAM
htop

# بررسی فضای دیسک
df -h

# بررسی پورت‌های باز
netstat -tlnp
```

### 📈 آمار Django

```bash
cd /opt/vpn-service/services
source ../venv/bin/activate

# تعداد کاربران
python manage.py shell -c "from accounts.models import UsersModel; print(UsersModel.objects.count())"

# تعداد سفارشات
python manage.py shell -c "from order.models import OrderUserModel; print(OrderUserModel.objects.count())"
```

## 🔄 آپدیت سیستم

### 📦 آپدیت کدها

```bash
cd /opt/vpn-service
git pull origin main

# راه‌اندازی مجدد سرویس‌ها
systemctl restart vpn-django vpn-user-bot vpn-admin-bot
```

### 📦 آپدیت X-UI

```bash
x-ui update
systemctl restart x-ui
```

## 📞 پشتیبانی

### 🆘 مشکلات رایج

1. **ربات‌ها کار نمی‌کنند:**

   - بررسی توکن‌ها در فایل .env
   - بررسی اتصال اینترنت
   - بررسی لاگ‌های ربات‌ها

2. **X-UI در دسترس نیست:**

   - بررسی وضعیت سرویس x-ui
   - بررسی پورت 54321
   - بررسی Firewall

3. **Django خطا می‌دهد:**
   - بررسی migrations
   - بررسی فایل‌های استاتیک
   - بررسی لاگ‌های Django

### 📞 تماس با پشتیبانی

- **ایمیل:** support@example.com
- **تلگرام:** @support_bot

## 📝 تغییرات اخیر

### 🔄 نسخه 2.0.0

- ✅ سیستم تست اتوماتیک
- ✅ Inbound اتوماتیک
- ✅ کانفیگ اتوماتیک
- ✅ Admin Bot بهبود یافته
- ✅ User Bot بهبود یافته

---

**🎉 سیستم VPN شما آماده است!**
