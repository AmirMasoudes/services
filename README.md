# 🚀 Django VPN Management System

سیستم مدیریت VPN با Django و X-UI Panel

## 📋 ویژگی‌ها

- ✅ **Django VPN Management System**
- ✅ **X-UI Integration**
- ✅ **Automatic Inbound Creation**
- ✅ **Custom User Model**
- ✅ **Web Services**
- ✅ **Database Management**
- ✅ **User Management**
- ✅ **Plan Management**
- ✅ **Telegram Bots**
- ✅ **All Services Running**

## 🌐 دسترسی‌ها

### Django Admin

- **URL**: http://38.54.105.124/admin/
- **Username**: admin
- **Password**: YourSecurePassword123

### X-UI Panel

- **URL**: http://38.54.105.124:54321/MsxZ4xuIy5xLfQtsSC/
- **Username**: admin
- **Password**: YourSecurePassword123!@#

## 📦 پلن‌های VPN

1. **پلن تستی** - 0 تومان - 1 روز - 1 GB
2. **پلن برنزی** - 50,000 تومان - 30 روز - 10 GB
3. **پلن نقره‌ای** - 80,000 تومان - 30 روز - 25 GB
4. **پلن طلایی** - 120,000 تومان - 30 روز - 50 GB
5. **پلن الماس** - 200,000 تومان - 30 روز - 100 GB

## 🔧 سرویس‌ها

### فعال

- ✅ Django VPN
- ✅ Nginx
- ✅ Redis Server
- ✅ PostgreSQL
- ✅ Admin Bot
- ✅ User Bot

### پورت‌های باز

- ✅ HTTP (80)
- ✅ Django (8000)
- ✅ X-UI Panel (54321)
- ✅ Redis (6379)
- ✅ PostgreSQL (5432)

## 🤖 بات‌های تلگرام

### Admin Bot

- **فایل**: `bot/admin_boy.py`
- **وظایف**: مدیریت کاربران، پلن‌ها، درخواست‌های پرداخت

### User Bot

- **فایل**: `bot/user_bot.py`
- **وظایف**: دریافت کانفیگ VPN، بررسی مصرف

## 📁 ساختار پروژه

```
configvpn/
├── accounts/          # مدیریت کاربران
├── plan/             # مدیریت پلن‌ها
├── xui_servers/      # مدیریت سرورهای X-UI
├── bot/              # بات‌های تلگرام
├── config/           # تنظیمات Django
├── .env              # متغیرهای محیطی
└── final_test_complete.py  # تست نهایی
```

## 🚀 راه‌اندازی

### پیش‌نیازها

- Python 3.11+
- PostgreSQL
- Redis
- Nginx
- X-UI Panel

### نصب

```bash
# کلون پروژه
git clone https://github.com/AmirMasoudes/services.git
cd services

# نصب وابستگی‌ها
pip install -r requirements.txt

# تنظیم متغیرهای محیطی
cp .env.example .env
# ویرایش فایل .env

# اجرای مایگریشن‌ها
python manage.py migrate

# ایجاد سوپر یوزر
python manage.py createsuperuser

# تست سیستم
python final_test_complete.py
```

## 🔧 تنظیمات

### فایل .env

```env
# Django Settings
SECRET_KEY=your-secret-key
DEBUG=False
ALLOWED_HOSTS=your-domain.com

# Database
DATABASE_URL=postgresql://user:password@localhost/dbname

# Telegram Bots
ADMIN_BOT_TOKEN=your-admin-bot-token
USER_BOT_TOKEN=your-user-bot-token

# X-UI Settings
XUI_PANEL_URL=http://your-server:54321
XUI_PANEL_USERNAME=admin
XUI_PANEL_PASSWORD=your-password
```

## 📊 تست سیستم

برای تست کامل سیستم:

```bash
python final_test_complete.py
```

این اسکریپت موارد زیر را بررسی می‌کند:

- ✅ پلن‌های VPN
- ✅ کاربران
- ✅ سرور X-UI
- ✅ سرویس‌ها
- ✅ پورت‌ها
- ✅ بات‌ها
- ✅ وب سرویس‌ها

## 🛠️ عیب‌یابی

### مشکل بات‌ها

```bash
# بررسی وضعیت بات‌ها
python check_bots_status.py

# تنظیم توکن‌ها
python setup_bot_tokens.py
```

### مشکل X-UI

```bash
# تست اتصال X-UI
python test_xui_connection.py

# تنظیم سرور X-UI
python setup_xui_server.py
```

## 📞 پشتیبانی

برای گزارش مشکلات یا درخواست ویژگی‌های جدید، لطفاً issue ایجاد کنید.

## 📄 لایسنس

این پروژه تحت لایسنس MIT منتشر شده است.

---

**🎉 سیستم آماده است!**
