# راهنمای استقرار سیستم روی سرور

## 📋 پیش‌نیازها

قبل از شروع، اطمینان حاصل کنید که موارد زیر روی سرور موجود است:

- **Python 3.8+** نصب شده
- **Sanaei X-UI** نصب و فعال است
- **Git** نصب شده
- **Nginx** (اختیاری، برای production)
- **Supervisor** یا **systemd** (برای مدیریت سرویس‌ها)

## 🚀 مراحل استقرار

### مرحله 1: آماده‌سازی سرور

```bash
# به‌روزرسانی سیستم
sudo apt update && sudo apt upgrade -y

# نصب پیش‌نیازها
sudo apt install -y python3 python3-pip python3-venv git nginx supervisor

# ایجاد کاربر برای اجرای برنامه
sudo useradd -m -s /bin/bash vpnbot
sudo usermod -aG sudo vpnbot
```

### مرحله 2: انتقال کد به سرور

```bash
# ورود به سرور
ssh user@your_server_ip

# تغییر به کاربر vpnbot
sudo su - vpnbot

# کلون کردن پروژه (یا انتقال فایل‌ها)
git clone https://github.com/your-repo/services.git
cd services

# یا انتقال فایل‌ها از طریق SCP
# scp -r /path/to/local/services user@server_ip:/home/vpnbot/
```

### مرحله 3: تنظیم محیط مجازی

```bash
# ایجاد محیط مجازی
python3 -m venv venv

# فعال‌سازی محیط مجازی
source venv/bin/activate

# نصب وابستگی‌ها
pip install -r requirements.txt

# نصب Gunicorn برای production
pip install gunicorn
```

### مرحله 4: تنظیم متغیرهای محیطی

```bash
# کپی کردن فایل تنظیمات
cp env.example env_config.env

# ویرایش تنظیمات
nano env_config.env
```

محتویات فایل `env_config.env`:

```env
# ========================================
# تنظیمات جنگو
# ========================================
DEBUG=False
SECRET_KEY=your_very_long_secret_key_here
ALLOWED_HOSTS=your_server_ip,your_domain.com

# ========================================
# تنظیمات دیتابیس
# ========================================
DATABASE_URL=sqlite:///db.sqlite3
# یا برای PostgreSQL:
# DATABASE_URL=postgresql://user:password@localhost/dbname

# ========================================
# تنظیمات تلگرام
# ========================================
TELEGRAM_BOT_TOKEN=your_telegram_bot_token
TELEGRAM_ADMIN_ID=your_admin_telegram_id

# ========================================
# تنظیمات سرور X-UI سنایی
# ========================================
XUI_DEFAULT_HOST=localhost
XUI_DEFAULT_PORT=54321
XUI_DEFAULT_USERNAME=admin
XUI_DEFAULT_PASSWORD=your_sanaei_password
XUI_WEB_BASE_PATH=/MsxZ4xuIy5xLfQtsSC/
XUI_DEFAULT_INBOUND_ID=1
XUI_USE_SSL=False
XUI_VERIFY_SSL=False
XUI_TIMEOUT=30
```

### مرحله 5: تنظیم دیتابیس

```bash
# فعال‌سازی محیط مجازی
source venv/bin/activate

# اجرای مایگریشن‌ها
python manage.py migrate

# ایجاد کاربر ادمین
python manage.py createsuperuser

# جمع‌آوری فایل‌های استاتیک
python manage.py collectstatic --noinput
```

### مرحله 6: تست اتصال به X-UI

```bash
# تست اتصال به X-UI سنایی
python test_sanaei_connection.py
```

### مرحله 7: تنظیم سرویس‌ها

#### تنظیم Django با Gunicorn

ایجاد فایل `gunicorn.conf.py`:

```python
# gunicorn.conf.py
bind = "127.0.0.1:8000"
workers = 3
worker_class = "sync"
worker_connections = 1000
max_requests = 1000
max_requests_jitter = 50
timeout = 30
keepalive = 2
```

#### تنظیم Supervisor برای Django

ایجاد فایل `/etc/supervisor/conf.d/django.conf`:

```ini
[program:django]
command=/home/vpnbot/services/venv/bin/gunicorn --config /home/vpnbot/services/gunicorn.conf.py config.wsgi:application
directory=/home/vpnbot/services
user=vpnbot
autostart=true
autorestart=true
redirect_stderr=true
stdout_logfile=/var/log/django.log
environment=DJANGO_SETTINGS_MODULE="config.settings"
```

#### تنظیم Supervisor برای Telegram Bot

ایجاد فایل `/etc/supervisor/conf.d/telegram_bot.conf`:

```ini
[program:telegram_bot]
command=/home/vpnbot/services/venv/bin/python /home/vpnbot/services/bot/user_bot.py
directory=/home/vpnbot/services
user=vpnbot
autostart=true
autorestart=true
redirect_stderr=true
stdout_logfile=/var/log/telegram_bot.log
environment=DJANGO_SETTINGS_MODULE="config.settings"
```

#### تنظیم Nginx (اختیاری)

ایجاد فایل `/etc/nginx/sites-available/vpnbot`:

```nginx
server {
    listen 80;
    server_name your_domain.com your_server_ip;

    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    location /static/ {
        alias /home/vpnbot/services/staticfiles/;
    }

    location /media/ {
        alias /home/vpnbot/services/media/;
    }
}
```

فعال‌سازی سایت:

```bash
sudo ln -s /etc/nginx/sites-available/vpnbot /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl restart nginx
```

### مرحله 8: راه‌اندازی سرویس‌ها

```bash
# راه‌اندازی Supervisor
sudo supervisorctl reread
sudo supervisorctl update
sudo supervisorctl start django
sudo supervisorctl start telegram_bot

# بررسی وضعیت سرویس‌ها
sudo supervisorctl status
```

### مرحله 9: تنظیم فایروال

```bash
# باز کردن پورت‌های مورد نیاز
sudo ufw allow 80
sudo ufw allow 443
sudo ufw allow 22
sudo ufw enable
```

## 🔧 مدیریت سرویس‌ها

### دستورات مفید Supervisor

```bash
# بررسی وضعیت سرویس‌ها
sudo supervisorctl status

# راه‌اندازی مجدد سرویس
sudo supervisorctl restart django
sudo supervisorctl restart telegram_bot

# توقف سرویس
sudo supervisorctl stop django
sudo supervisorctl stop telegram_bot

# شروع سرویس
sudo supervisorctl start django
sudo supervisorctl start telegram_bot

# مشاهده لاگ‌ها
sudo tail -f /var/log/django.log
sudo tail -f /var/log/telegram_bot.log
```

### دستورات مفید Django

```bash
# فعال‌سازی محیط مجازی
source venv/bin/activate

# اجرای سرور توسعه
python manage.py runserver 0.0.0.0:8000

# اجرای مایگریشن‌ها
python manage.py migrate

# ایجاد کاربر ادمین
python manage.py createsuperuser

# دسترسی به Django shell
python manage.py shell

# بررسی وضعیت
python manage.py check
```

## 🛠️ عیب‌یابی

### مشکلات رایج

#### 1. خطای اتصال به X-UI

```bash
# بررسی وضعیت X-UI
sudo systemctl status x-ui

# بررسی پورت X-UI
sudo netstat -tlnp | grep 54321

# تست اتصال
curl -k https://localhost:54321/MsxZ4xuIy5xLfQtsSC/login
```

#### 2. خطای Django

```bash
# بررسی لاگ‌های Django
sudo tail -f /var/log/django.log

# بررسی تنظیمات
python manage.py check --deploy
```

#### 3. خطای Telegram Bot

```bash
# بررسی لاگ‌های Bot
sudo tail -f /var/log/telegram_bot.log

# تست Bot به صورت دستی
python bot/user_bot.py
```

#### 4. خطای دیتابیس

```bash
# بررسی فایل دیتابیس
ls -la db.sqlite3

# پاک کردن و ایجاد مجدد دیتابیس
rm db.sqlite3
python manage.py migrate
```

## 📊 مانیتورینگ

### بررسی وضعیت سیستم

```bash
# بررسی استفاده از CPU و RAM
htop

# بررسی فضای دیسک
df -h

# بررسی لاگ‌های سیستم
sudo journalctl -f

# بررسی اتصالات شبکه
sudo netstat -tlnp
```

### بررسی عملکرد X-UI

```bash
# تست API X-UI
python test_sanaei_connection.py

# بررسی inbound ها
curl -k -X GET "https://localhost:54321/MsxZ4xuIy5xLfQtsSC/panel/api/inbounds/list" \
  -H "Cookie: session=your_session_cookie"
```

## 🔒 امنیت

### تنظیمات امنیتی

```bash
# تغییر مجوزهای فایل‌ها
chmod 600 env_config.env
chmod 644 db.sqlite3

# تنظیم فایروال
sudo ufw default deny incoming
sudo ufw default allow outgoing
sudo ufw allow ssh
sudo ufw allow 80
sudo ufw allow 443
sudo ufw enable
```

### به‌روزرسانی خودکار

ایجاد فایل `/etc/cron.daily/update-system`:

```bash
#!/bin/bash
apt update && apt upgrade -y
systemctl restart django
systemctl restart telegram_bot
```

## 📝 نکات مهم

1. **پشتیبان‌گیری**: حتماً از دیتابیس و فایل‌های مهم پشتیبان تهیه کنید
2. **به‌روزرسانی**: مرتباً سیستم و وابستگی‌ها را به‌روزرسانی کنید
3. **مانیتورینگ**: لاگ‌ها را مرتباً بررسی کنید
4. **امنیت**: رمزهای عبور قوی استفاده کنید و فایل‌های حساس را محافظت کنید
5. **تست**: قبل از استقرار در production، حتماً در محیط تست بررسی کنید

## 🆘 پشتیبانی

در صورت بروز مشکل:

1. لاگ‌های مربوطه را بررسی کنید
2. تنظیمات را دوباره بررسی کنید
3. از صحت اتصال به X-UI اطمینان حاصل کنید
4. در صورت نیاز، سیستم را راه‌اندازی مجدد کنید

---

**نکته**: این راهنما برای استقرار روی سرور Ubuntu/Debian نوشته شده است. برای سایر توزیع‌های لینوکس، دستورات ممکن است متفاوت باشد.
