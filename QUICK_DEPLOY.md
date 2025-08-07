# 🚀 راهنمای سریع استقرار

## مراحل استقرار روی سرور با Sanaei X-UI

### مرحله 1: انتقال فایل‌ها به سرور

```bash
# انتقال فایل‌ها از کامپیوتر محلی به سرور
scp -r /path/to/local/services user@your_server_ip:/home/user/

# یا کلون کردن از Git
git clone https://github.com/your-repo/services.git
cd services
```

### مرحله 2: اجرای اسکریپت استقرار خودکار

```bash
# قابل اجرا کردن اسکریپت
chmod +x deploy.sh

# اجرای اسکریپت استقرار
./deploy.sh
```

### مرحله 3: تنظیم فایل محیطی

```bash
# ویرایش تنظیمات
nano env_config.env
```

**تنظیمات ضروری:**

```env
# تنظیمات تلگرام
TELEGRAM_BOT_TOKEN=your_bot_token
TELEGRAM_ADMIN_ID=your_admin_id

# تنظیمات X-UI سنایی
XUI_DEFAULT_HOST=localhost
XUI_DEFAULT_PORT=54321
XUI_DEFAULT_USERNAME=admin
XUI_DEFAULT_PASSWORD=your_sanaei_password
XUI_WEB_BASE_PATH=/MsxZ4xuIy5xLfQtsSC/
XUI_DEFAULT_INBOUND_ID=1
```

### مرحله 4: ایجاد کاربر ادمین

```bash
# فعال‌سازی محیط مجازی
source venv/bin/activate

# ایجاد کاربر ادمین Django
python manage.py createsuperuser
```

### مرحله 5: تست سیستم

```bash
# تست اتصال به X-UI
python test_sanaei_connection.py

# بررسی وضعیت سرویس‌ها
sudo supervisorctl status
```

## 🔧 دستورات مفید

### مدیریت سرویس‌ها

```bash
# بررسی وضعیت
sudo supervisorctl status

# راه‌اندازی مجدد
sudo supervisorctl restart django
sudo supervisorctl restart telegram_bot

# مشاهده لاگ‌ها
sudo tail -f /var/log/django.log
sudo tail -f /var/log/telegram_bot.log
```

### مدیریت Django

```bash
# فعال‌سازی محیط مجازی
source venv/bin/activate

# اجرای مایگریشن‌ها
python manage.py migrate

# دسترسی به Django shell
python manage.py shell

# اجرای سرور توسعه
python manage.py runserver 0.0.0.0:8000
```

## 🛠️ عیب‌یابی سریع

### مشکل اتصال به X-UI

```bash
# بررسی وضعیت X-UI
sudo systemctl status x-ui

# تست اتصال
curl -k https://localhost:54321/MsxZ4xuIy5xLfQtsSC/login
```

### مشکل Telegram Bot

```bash
# بررسی لاگ‌های Bot
sudo tail -f /var/log/telegram_bot.log

# تست دستی Bot
source venv/bin/activate
python bot/user_bot.py
```

### مشکل Django

```bash
# بررسی لاگ‌های Django
sudo tail -f /var/log/django.log

# بررسی تنظیمات
python manage.py check --deploy
```

## 📊 بررسی عملکرد

### آدرس‌های مهم

- **وب‌سایت**: `http://your_server_ip`
- **پنل ادمین**: `http://your_server_ip/admin`
- **X-UI سنایی**: `https://your_server_ip:54321/MsxZ4xuIy5xLfQtsSC/`

### بررسی وضعیت

```bash
# بررسی استفاده از منابع
htop

# بررسی فضای دیسک
df -h

# بررسی اتصالات شبکه
sudo netstat -tlnp
```

## ⚠️ نکات مهم

1. **امنیت**: حتماً رمزهای عبور قوی استفاده کنید
2. **پشتیبان‌گیری**: از دیتابیس و فایل‌های مهم پشتیبان تهیه کنید
3. **به‌روزرسانی**: مرتباً سیستم را به‌روزرسانی کنید
4. **مانیتورینگ**: لاگ‌ها را مرتباً بررسی کنید

## 🆘 پشتیبانی

در صورت بروز مشکل:

1. لاگ‌های مربوطه را بررسی کنید
2. تنظیمات را دوباره بررسی کنید
3. از صحت اتصال به X-UI اطمینان حاصل کنید
4. در صورت نیاز، سیستم را راه‌اندازی مجدد کنید

---

**📚 مستندات کامل**: `DEPLOYMENT_GUIDE.md`
**🔧 راهنمای X-UI**: `Sanaei_XUI_Setup_Guide.md`
