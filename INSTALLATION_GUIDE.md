# راهنمای کامل نصب و راه‌اندازی سرویس VPN

## 📋 پیش‌نیازها

### سیستم عامل
- ✅ Ubuntu 20.04 LTS یا بالاتر
- ✅ CentOS 8 یا بالاتر
- ✅ Debian 11 یا بالاتر
- ⚠️ Windows (فقط برای توسعه)

### سخت‌افزار
- **CPU**: حداقل 2 هسته
- **RAM**: حداقل 4GB
- **Storage**: حداقل 20GB فضای آزاد
- **Network**: اتصال اینترنت پایدار

### نرم‌افزار
- **Python**: 3.8 یا بالاتر
- **Git**: برای دانلود کد
- **Docker**: اختیاری (برای containerization)

## 🚀 مراحل نصب

### مرحله 1: آماده‌سازی سرور

```bash
# به‌روزرسانی سیستم
sudo apt update && sudo apt upgrade -y

# نصب وابستگی‌های پایه
sudo apt install -y python3 python3-pip python3-venv git curl wget

# نصب Nginx (برای reverse proxy)
sudo apt install -y nginx

# نصب Certbot (برای SSL)
sudo apt install -y certbot python3-certbot-nginx

# نصب فایروال
sudo apt install -y ufw
```

### مرحله 2: دانلود و آماده‌سازی پروژه

```bash
# ایجاد دایرکتوری پروژه
sudo mkdir -p /opt/vpn-service
sudo chown $USER:$USER /opt/vpn-service
cd /opt/vpn-service

# کلون کردن پروژه (اگر از Git استفاده می‌کنید)
git clone https://github.com/your-repo/vpn-service.git .

# یا کپی کردن فایل‌ها
# فایل‌های پروژه را در این دایرکتوری قرار دهید
```

### مرحله 3: راه‌اندازی محیط Python

```bash
# ایجاد virtual environment
python3 -m venv venv

# فعال‌سازی virtual environment
source venv/bin/activate

# به‌روزرسانی pip
pip install --upgrade pip

# نصب وابستگی‌ها
pip install -r requirements.txt
```

### مرحله 4: تنظیم متغیرهای محیطی

```bash
# ایجاد فایل .env
cat > .env << EOF
# Django Settings
SECRET_KEY=your-secret-key-here
DEBUG=False
ALLOWED_HOSTS=your-domain.com,www.your-domain.com

# Telegram Bot Tokens
TELEGRAM_BOT_TOKEN=your-user-bot-token
ADMIN_BOT_TOKEN=your-admin-bot-token

# Admin Password
ADMIN_PASSWORD=your-secure-admin-password

# X-UI Server Settings
XUI_SERVER_HOST=127.0.0.1
XUI_SERVER_PORT=54321
XUI_USERNAME=admin
XUI_PASSWORD=your-xui-password

# Database (optional - for production)
# DATABASE_URL=postgresql://user:password@localhost:5432/dbname
EOF
```

### مرحله 5: راه‌اندازی Django

```bash
# تنظیم متغیر محیطی Django
export DJANGO_SETTINGS_MODULE=config.settings

# اجرای migrations
python manage.py makemigrations
python manage.py migrate

# ایجاد superuser
python manage.py createsuperuser --noinput \
    --username admin \
    --email admin@example.com

# جمع‌آوری فایل‌های static
python manage.py collectstatic --noinput
```

### مرحله 6: نصب و راه‌اندازی X-UI

```bash
# دانلود و نصب X-UI
bash <(curl -Ls https://raw.githubusercontent.com/vaxilu/x-ui/master/install.sh)

# تنظیم X-UI
sudo systemctl enable x-ui
sudo systemctl start x-ui

# تنظیم رمز عبور X-UI
x-ui
```

### مرحله 7: تنظیم Nginx

```bash
# ایجاد فایل تنظیمات Nginx
sudo tee /etc/nginx/sites-available/vpn-service << EOF
server {
    listen 80;
    server_name your-domain.com www.your-domain.com;
    
    # Redirect to HTTPS
    return 301 https://\$server_name\$request_uri;
}

server {
    listen 443 ssl http2;
    server_name your-domain.com www.your-domain.com;
    
    # SSL Configuration
    ssl_certificate /etc/letsencrypt/live/your-domain.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/your-domain.com/privkey.pem;
    
    # Security Headers
    add_header X-Frame-Options "SAMEORIGIN" always;
    add_header X-XSS-Protection "1; mode=block" always;
    add_header X-Content-Type-Options "nosniff" always;
    add_header Referrer-Policy "no-referrer-when-downgrade" always;
    add_header Content-Security-Policy "default-src 'self' http: https: data: blob: 'unsafe-inline'" always;
    
    # Django Application
    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto \$scheme;
    }
    
    # Static Files
    location /static/ {
        alias /opt/vpn-service/staticfiles/;
        expires 1y;
        add_header Cache-Control "public, immutable";
    }
    
    # Media Files
    location /media/ {
        alias /opt/vpn-service/media/;
        expires 1y;
        add_header Cache-Control "public, immutable";
    }
    
    # X-UI Panel (optional - for admin access)
    location /xui/ {
        proxy_pass http://127.0.0.1:54321;
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto \$scheme;
    }
}
EOF

# فعال‌سازی سایت
sudo ln -s /etc/nginx/sites-available/vpn-service /etc/nginx/sites-enabled/

# حذف سایت پیش‌فرض
sudo rm -f /etc/nginx/sites-enabled/default

# تست تنظیمات Nginx
sudo nginx -t

# راه‌اندازی مجدد Nginx
sudo systemctl restart nginx
```

### مرحله 8: نصب SSL Certificate

```bash
# نصب گواهی SSL با Let's Encrypt
sudo certbot --nginx -d your-domain.com -d www.your-domain.com

# تنظیم auto-renewal
sudo crontab -e
# اضافه کردن خط زیر:
# 0 12 * * * /usr/bin/certbot renew --quiet
```

### مرحله 9: تنظیم فایروال

```bash
# باز کردن پورت‌های مورد نیاز
sudo ufw allow 22/tcp    # SSH
sudo ufw allow 80/tcp    # HTTP
sudo ufw allow 443/tcp   # HTTPS
sudo ufw allow 8000/tcp  # Django (development)
sudo ufw allow 54321/tcp # X-UI

# فعال‌سازی فایروال
sudo ufw --force enable

# بررسی وضعیت
sudo ufw status
```

### مرحله 10: ایجاد سرویس systemd

```bash
# ایجاد فایل سرویس برای Django
sudo tee /etc/systemd/system/vpn-django.service << EOF
[Unit]
Description=VPN Django Service
After=network.target

[Service]
Type=simple
User=www-data
Group=www-data
WorkingDirectory=/opt/vpn-service
Environment=PATH=/opt/vpn-service/venv/bin
Environment=DJANGO_SETTINGS_MODULE=config.settings
ExecStart=/opt/vpn-service/venv/bin/python manage.py runserver 0.0.0.0:8000
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
EOF

# ایجاد فایل سرویس برای ربات کاربر
sudo tee /etc/systemd/system/vpn-user-bot.service << EOF
[Unit]
Description=VPN User Bot Service
After=network.target

[Service]
Type=simple
User=www-data
Group=www-data
WorkingDirectory=/opt/vpn-service
Environment=PATH=/opt/vpn-service/venv/bin
Environment=DJANGO_SETTINGS_MODULE=config.settings
ExecStart=/opt/vpn-service/venv/bin/python bot/user_bot.py
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
EOF

# ایجاد فایل سرویس برای ربات ادمین
sudo tee /etc/systemd/system/vpn-admin-bot.service << EOF
[Unit]
Description=VPN Admin Bot Service
After=network.target

[Service]
Type=simple
User=www-data
Group=www-data
WorkingDirectory=/opt/vpn-service
Environment=PATH=/opt/vpn-service/venv/bin
Environment=DJANGO_SETTINGS_MODULE=config.settings
ExecStart=/opt/vpn-service/venv/bin/python bot/admin_boy.py
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
EOF

# فعال‌سازی و راه‌اندازی سرویس‌ها
sudo systemctl daemon-reload
sudo systemctl enable vpn-django vpn-user-bot vpn-admin-bot
sudo systemctl start vpn-django vpn-user-bot vpn-admin-bot
```

## 🧪 تست نصب

### تست Django
```bash
# بررسی وضعیت Django
sudo systemctl status vpn-django

# تست دسترسی به وب‌سایت
curl -I https://your-domain.com
```

### تست ربات‌ها
```bash
# بررسی وضعیت ربات‌ها
sudo systemctl status vpn-user-bot
sudo systemctl status vpn-admin-bot

# بررسی logs
sudo journalctl -u vpn-user-bot -f
sudo journalctl -u vpn-admin-bot -f
```

### تست X-UI
```bash
# بررسی وضعیت X-UI
sudo systemctl status x-ui

# تست اتصال به X-UI
curl -I http://127.0.0.1:54321
```

## 🔧 تنظیمات اضافی

### تنظیم Backup خودکار
```bash
# ایجاد اسکریپت backup
sudo tee /opt/vpn-service/backup.sh << 'EOF'
#!/bin/bash
BACKUP_DIR="/opt/backups/vpn-service"
DATE=$(date +%Y%m%d_%H%M%S)

# ایجاد دایرکتوری backup
mkdir -p $BACKUP_DIR

# Backup دیتابیس
cd /opt/vpn-service
source venv/bin/activate
python manage.py dumpdata > $BACKUP_DIR/db_backup_$DATE.json

# Backup فایل‌های مهم
tar -czf $BACKUP_DIR/files_backup_$DATE.tar.gz \
    --exclude=venv \
    --exclude=*.pyc \
    --exclude=__pycache__ \
    .

# حذف backup های قدیمی (بیش از 7 روز)
find $BACKUP_DIR -name "*.json" -mtime +7 -delete
find $BACKUP_DIR -name "*.tar.gz" -mtime +7 -delete

echo "Backup completed: $DATE"
EOF

# تنظیم مجوز اجرا
sudo chmod +x /opt/vpn-service/backup.sh

# اضافه کردن به crontab
sudo crontab -e
# اضافه کردن خط زیر:
# 0 2 * * * /opt/vpn-service/backup.sh
```

### تنظیم Monitoring
```bash
# نصب monitoring tools
sudo apt install -y htop iotop nethogs

# ایجاد اسکریپت monitoring
sudo tee /opt/vpn-service/monitor.sh << 'EOF'
#!/bin/bash
LOG_FILE="/var/log/vpn-service-monitor.log"

echo "$(date): VPN Service Monitor" >> $LOG_FILE

# بررسی سرویس‌ها
services=("vpn-django" "vpn-user-bot" "vpn-admin-bot" "x-ui" "nginx")
for service in "${services[@]}"; do
    if systemctl is-active --quiet $service; then
        echo "$(date): $service is running" >> $LOG_FILE
    else
        echo "$(date): $service is down - restarting" >> $LOG_FILE
        systemctl restart $service
    fi
done

# بررسی فضای دیسک
DISK_USAGE=$(df / | awk 'NR==2 {print $5}' | sed 's/%//')
if [ $DISK_USAGE -gt 80 ]; then
    echo "$(date): Disk usage is high: ${DISK_USAGE}%" >> $LOG_FILE
fi

# بررسی حافظه
MEMORY_USAGE=$(free | awk 'NR==2{printf "%.2f", $3*100/$2}')
if (( $(echo "$MEMORY_USAGE > 80" | bc -l) )); then
    echo "$(date): Memory usage is high: ${MEMORY_USAGE}%" >> $LOG_FILE
fi
EOF

# تنظیم مجوز اجرا
sudo chmod +x /opt/vpn-service/monitor.sh

# اضافه کردن به crontab
sudo crontab -e
# اضافه کردن خط زیر:
# */5 * * * * /opt/vpn-service/monitor.sh
```

## 🚨 عیب‌یابی

### مشکلات رایج

#### 1. خطا در اتصال به X-UI
```bash
# بررسی وضعیت X-UI
sudo systemctl status x-ui

# بررسی پورت
sudo netstat -tlnp | grep 54321

# بررسی فایروال
sudo ufw status

# راه‌اندازی مجدد X-UI
sudo systemctl restart x-ui
```

#### 2. خطا در ربات‌ها
```bash
# بررسی logs ربات‌ها
sudo journalctl -u vpn-user-bot -n 50
sudo journalctl -u vpn-admin-bot -n 50

# بررسی توکن‌ها
grep -E "TELEGRAM_BOT_TOKEN|ADMIN_BOT_TOKEN" .env

# راه‌اندازی مجدد ربات‌ها
sudo systemctl restart vpn-user-bot vpn-admin-bot
```

#### 3. خطا در Django
```bash
# بررسی logs Django
sudo journalctl -u vpn-django -n 50

# بررسی تنظیمات
python manage.py check

# راه‌اندازی مجدد Django
sudo systemctl restart vpn-django
```

#### 4. خطا در Nginx
```bash
# بررسی تنظیمات Nginx
sudo nginx -t

# بررسی logs Nginx
sudo tail -f /var/log/nginx/error.log

# راه‌اندازی مجدد Nginx
sudo systemctl restart nginx
```

## 📊 بررسی عملکرد

### دستورات مفید
```bash
# بررسی وضعیت تمام سرویس‌ها
sudo systemctl status vpn-django vpn-user-bot vpn-admin-bot x-ui nginx

# بررسی استفاده از منابع
htop
iotop
nethogs

# بررسی logs
sudo journalctl -f -u vpn-django
sudo journalctl -f -u vpn-user-bot
sudo journalctl -f -u vpn-admin-bot

# بررسی اتصالات شبکه
sudo netstat -tlnp
sudo ss -tlnp
```

## ✅ چک‌لیست نهایی

- [ ] تمام سرویس‌ها در حال اجرا هستند
- [ ] SSL certificate نصب شده است
- [ ] فایروال فعال است
- [ ] Backup خودکار تنظیم شده است
- [ ] Monitoring فعال است
- [ ] ربات‌ها پاسخ می‌دهند
- [ ] X-UI قابل دسترس است
- [ ] وب‌سایت قابل دسترس است

## 🎉 تبریک!

سرویس VPN شما با موفقیت نصب و راه‌اندازی شد. حالا می‌توانید:

1. **ربات کاربر** را در تلگرام تست کنید
2. **ربات ادمین** را برای مدیریت استفاده کنید
3. **X-UI** را برای مدیریت کانفیگ‌ها استفاده کنید
4. **وب‌سایت** را برای مدیریت آنلاین استفاده کنید

### اطلاعات مهم:
- **دامنه**: https://your-domain.com
- **X-UI**: https://your-domain.com/xui/
- **ربات کاربر**: @your_user_bot
- **ربات ادمین**: @your_admin_bot

### پشتیبانی:
در صورت بروز مشکل، لطفا logs را بررسی کنید و با تیم پشتیبانی تماس بگیرید. 