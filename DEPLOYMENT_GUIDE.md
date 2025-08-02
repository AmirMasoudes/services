# 🚀 راهنمای راه‌اندازی Django VPN Service

## 📋 خلاصه

این سیستم یک پنل مدیریت VPN کامل است که Django را با X-UI panel ادغام می‌کند.

## ✅ وضعیت فعلی

- ✅ **اتصال X-UI**: کار می‌کند
- ✅ **ایجاد Inbound**: کار می‌کند
- ✅ **API Communication**: کار می‌کند
- ✅ **Django Models**: آماده
- ✅ **Telegram Bots**: آماده

## 🛠️ پیش‌نیازها

```bash
# سرور Ubuntu/Debian
# دسترسی root
# حداقل 2GB RAM
# حداقل 20GB فضای دیسک
```

## 🚀 راه‌اندازی سریع

### 1. کلون پروژه

```bash
cd /opt
git clone https://github.com/AmirMasoudes/services.git vpn-service
cd vpn-service/services
```

### 2. نصب Python dependencies

```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### 3. تنظیم فایل .env

```bash
cat > .env << 'EOF'
# Django Settings
SECRET_KEY=django-insecure-c^1%va7g4+yqfygvbjku#d4-4d8-sw8rzw9!$_wq-vt(*x-mw9
DEBUG=False
ALLOWED_HOSTS=38.54.105.124,your-domain.com,www.your-domain.com,localhost,127.0.0.1

# Database Settings
DATABASE_URL=postgresql://configvpn_user:YourSecurePassword123!@#@localhost/configvpn_db

# Telegram Bot Tokens
ADMIN_BOT_TOKEN=your-admin-bot-token-here
USER_BOT_TOKEN=your-user-bot-token-here

# Admin Password
ADMIN_PASSWORD=your-secure-admin-password

# X-UI Settings
XUI_DEFAULT_PROTOCOL=vless
XUI_DEFAULT_PORT=443
XUI_PANEL_URL=http://38.54.105.124:54321
XUI_PANEL_PATH=/MsxZ4xuIy5xLfQtsSC/
XUI_PANEL_USERNAME=admin
XUI_PANEL_PASSWORD=YourSecurePassword123!@#

REDIS_URL=redis://localhost:6379/0

LOG_LEVEL=INFO
LOG_FILE=/opt/configvpn/logs/app.log

ENABLE_SSL=False
SSL_CERT_PATH=/etc/letsencrypt/live/your-domain.com/fullchain.pem
SSL_KEY_PATH=/etc/letsencrypt/live/your-domain.com/privkey.pem

# Performance Settings
ENABLE_CACHE=True
CACHE_TIMEOUT=300
MAX_CONNECTIONS=100

# X-UI Server Configuration
XUI_SERVER_HOST=38.54.105.124
XUI_SERVER_PORT=54321
XUI_SERVER_USERNAME=admin
XUI_SERVER_PASSWORD=YourSecurePassword123!@#
XUI_SERVER_WEB_BASE_PATH=/MsxZ4xuIy5xLfQtsSC/
EOF
```

### 4. راه‌اندازی X-UI

```bash
# نصب X-UI
bash <(curl -Ls https://raw.githubusercontent.com/mhsanaei/3x-ui/master/install.sh)

# تنظیم X-UI
x-ui
# 1. Set Panel Port: 54321
# 2. Set Panel Path: /MsxZ4xuIy5xLfQtsSC/
# 3. Set Username: admin
# 4. Set Password: YourSecurePassword123!@#
```

### 5. تست اتصال X-UI

```bash
python test_simple_inbound.py
python setup_xui_server.py
```

### 6. راه‌اندازی Django

```bash
# Migrations
python manage.py makemigrations
python manage.py migrate

# Create superuser
python manage.py createsuperuser

# Collect static files
python manage.py collectstatic --noinput
```

### 7. راه‌اندازی سرویس‌ها

```bash
# اجرای اسکریپت راه‌اندازی
python quick_setup.py
```

## 🌐 دسترسی‌ها

### Django Admin Panel

- **URL**: http://38.54.105.124/admin/
- **Username**: admin
- **Password**: (از مرحله 6)

### X-UI Panel

- **URL**: http://38.54.105.124:54321/MsxZ4xuIy5xLfQtsSC/
- **Username**: admin
- **Password**: YourSecurePassword123!@#

### Django API

- **URL**: http://38.54.105.124:8000/

## 📊 مدیریت سرویس‌ها

### وضعیت سرویس‌ها

```bash
systemctl status django-vpn
systemctl status nginx
systemctl status postgresql
systemctl status redis
```

### راه‌اندازی مجدد

```bash
systemctl restart django-vpn
systemctl restart nginx
```

### مشاهده لاگ‌ها

```bash
journalctl -u django-vpn -f
tail -f /var/log/nginx/access.log
```

## 🔧 تنظیمات پیشرفته

### SSL Certificate

```bash
# نصب Certbot
apt install certbot python3-certbot-nginx

# ایجاد SSL certificate
certbot --nginx -d your-domain.com
```

### Firewall

```bash
# باز کردن پورت‌های مورد نیاز
ufw allow 80/tcp
ufw allow 443/tcp
ufw allow 54321/tcp
ufw allow 8000/tcp
ufw enable
```

### Database Backup

```bash
# Backup
pg_dump configvpn_db > backup.sql

# Restore
psql configvpn_db < backup.sql
```

## 🐛 عیب‌یابی

### مشکل اتصال X-UI

```bash
# تست اتصال
curl -s http://38.54.105.124:54321/MsxZ4xuIy5xLfQtsSC/

# بررسی لاگ‌ها
journalctl -u x-ui -f
```

### مشکل Django

```bash
# تست Django
python manage.py check

# بررسی لاگ‌ها
tail -f /opt/vpn-service/services/logs/django.log
```

### مشکل Nginx

```bash
# تست تنظیمات
nginx -t

# بررسی لاگ‌ها
tail -f /var/log/nginx/error.log
```

## 📈 مانیتورینگ

### System Resources

```bash
# CPU و Memory
htop

# Disk Usage
df -h

# Network
iftop
```

### Application Logs

```bash
# Django logs
tail -f /opt/vpn-service/services/logs/app.log

# X-UI logs
journalctl -u x-ui -f

# Nginx logs
tail -f /var/log/nginx/access.log
```

## 🔄 به‌روزرسانی

### به‌روزرسانی کد

```bash
cd /opt/vpn-service/services
git pull origin master
python manage.py migrate
systemctl restart django-vpn
```

### به‌روزرسانی X-UI

```bash
x-ui update
systemctl restart x-ui
```

## 📞 پشتیبانی

### اطلاعات مفید

- **Server IP**: 38.54.105.124
- **X-UI Port**: 54321
- **Django Port**: 8000
- **Nginx Port**: 80/443

### لاگ‌های مهم

- Django: `/opt/vpn-service/services/logs/`
- X-UI: `journalctl -u x-ui`
- Nginx: `/var/log/nginx/`
- System: `journalctl -u django-vpn`

## 🎯 ویژگی‌های سیستم

### ✅ پیاده‌سازی شده

- [x] اتصال Django به X-UI
- [x] ایجاد خودکار inbound
- [x] مدیریت کاربران
- [x] سیستم پلن‌ها
- [x] Telegram bots
- [x] API endpoints
- [x] Admin panel

### 🔄 در حال توسعه

- [ ] سیستم پرداخت
- [ ] اعلان‌های خودکار
- [ ] مانیتورینگ پیشرفته
- [ ] Backup خودکار
- [ ] SSL خودکار

## 📝 نکات مهم

1. **امنیت**: حتماً پسوردهای پیش‌فرض را تغییر دهید
2. **Backup**: مرتباً از دیتابیس backup بگیرید
3. **Monitoring**: سیستم را تحت نظر داشته باشید
4. **Updates**: مرتباً سیستم را به‌روزرسانی کنید
5. **Logs**: لاگ‌ها را بررسی کنید

## 🎉 نتیجه

سیستم شما آماده است! حالا می‌توانید:

- کاربران را مدیریت کنید
- پلن‌ها را تنظیم کنید
- inbound ها را ایجاد کنید
- از طریق Telegram با سیستم کار کنید
