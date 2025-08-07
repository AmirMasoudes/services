#!/bin/bash

# اسکریپت کامل استقرار سیستم VPN Bot
echo "🚀 شروع استقرار کامل سیستم VPN Bot..."

# رنگ‌ها برای نمایش بهتر
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

print_message() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# مرحله 1: بررسی پیش‌نیازها
print_message "مرحله 1: بررسی پیش‌نیازها..."

# بررسی Python
if ! command -v python3 &> /dev/null; then
    print_error "Python3 نصب نیست!"
    exit 1
fi

# بررسی pip
if ! command -v pip3 &> /dev/null; then
    print_error "pip3 نصب نیست!"
    exit 1
fi

print_success "پیش‌نیازها بررسی شدند"

# مرحله 2: نصب وابستگی‌های سیستم
print_message "مرحله 2: نصب وابستگی‌های سیستم..."

apt update
apt install -y python3-venv nginx supervisor ufw curl

print_success "وابستگی‌های سیستم نصب شدند"

# مرحله 3: تنظیم محیط مجازی
print_message "مرحله 3: تنظیم محیط مجازی..."

if [ ! -d "venv" ]; then
    python3 -m venv venv
    print_success "محیط مجازی ایجاد شد"
else
    print_warning "محیط مجازی قبلاً وجود دارد"
fi

source venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt
pip install gunicorn

print_success "محیط مجازی تنظیم شد"

# مرحله 4: ایجاد پوشه‌های مورد نیاز
print_message "مرحله 4: ایجاد پوشه‌های مورد نیاز..."

mkdir -p staticfiles
mkdir -p media
mkdir -p logs
mkdir -p backups

print_success "پوشه‌های مورد نیاز ایجاد شدند"

# مرحله 5: تنظیم فایل‌های محیطی
print_message "مرحله 5: تنظیم فایل‌های محیطی..."

# کپی کردن فایل تنظیمات
cp env_config_simple.env env_config.env

# تنظیم مجوزهای امنیتی
chmod 600 env_config.env

print_success "فایل‌های محیطی تنظیم شدند"

# مرحله 6: تست Django
print_message "مرحله 6: تست Django..."

python manage.py check --deploy

if [ $? -eq 0 ]; then
    print_success "Django تست شد"
else
    print_warning "برخی هشدارهای Django وجود دارد"
fi

# مرحله 7: اجرای مایگریشن‌ها
print_message "مرحله 7: اجرای مایگریشن‌ها..."

python manage.py migrate

print_success "مایگریشن‌ها اجرا شدند"

# مرحله 8: جمع‌آوری فایل‌های استاتیک
print_message "مرحله 8: جمع‌آوری فایل‌های استاتیک..."

python manage.py collectstatic --noinput

print_success "فایل‌های استاتیک جمع‌آوری شدند"

# مرحله 9: تست اتصال به X-UI
print_message "مرحله 9: تست اتصال به X-UI..."

python test_connection_simple.py

print_success "تست اتصال به X-UI انجام شد"

# مرحله 10: تنظیم Gunicorn
print_message "مرحله 10: تنظیم Gunicorn..."

cat > gunicorn.conf.py << 'EOF'
# gunicorn.conf.py
bind = "127.0.0.1:8000"
workers = 3
worker_class = "sync"
worker_connections = 1000
max_requests = 1000
max_requests_jitter = 50
timeout = 30
keepalive = 2
EOF

print_success "Gunicorn تنظیم شد"

# مرحله 11: تنظیم Supervisor
print_message "مرحله 11: تنظیم Supervisor..."

# ایجاد فایل تنظیمات Django
cat > /etc/supervisor/conf.d/django.conf << EOF
[program:django]
command=$(pwd)/venv/bin/gunicorn --config $(pwd)/gunicorn.conf.py config.wsgi:application
directory=$(pwd)
user=root
autostart=true
autorestart=true
redirect_stderr=true
stdout_logfile=/var/log/django.log
environment=DJANGO_SETTINGS_MODULE="config.settings"
EOF

# ایجاد فایل تنظیمات Telegram Bot
cat > /etc/supervisor/conf.d/telegram_bot.conf << EOF
[program:telegram_bot]
command=$(pwd)/venv/bin/python $(pwd)/bot/user_bot.py
directory=$(pwd)
user=root
autostart=true
autorestart=true
redirect_stderr=true
stdout_logfile=/var/log/telegram_bot.log
environment=DJANGO_SETTINGS_MODULE="config.settings"
EOF

# راه‌اندازی Supervisor
supervisorctl reread
supervisorctl update

print_success "Supervisor تنظیم شد"

# مرحله 12: تنظیم Nginx
print_message "مرحله 12: تنظیم Nginx..."

# ایجاد فایل تنظیمات Nginx
cat > /etc/nginx/sites-available/vpnbot << EOF
server {
    listen 80;
    server_name _;

    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto \$scheme;
    }

    location /static/ {
        alias $(pwd)/staticfiles/;
    }

    location /media/ {
        alias $(pwd)/media/;
    }
}
EOF

# فعال‌سازی سایت
ln -sf /etc/nginx/sites-available/vpnbot /etc/nginx/sites-enabled/
nginx -t
systemctl restart nginx

print_success "Nginx تنظیم شد"

# مرحله 13: تنظیم فایروال
print_message "مرحله 13: تنظیم فایروال..."

ufw default deny incoming
ufw default allow outgoing
ufw allow ssh
ufw allow 80
ufw allow 443
ufw --force enable

print_success "فایروال تنظیم شد"

# مرحله 14: راه‌اندازی سرویس‌ها
print_message "مرحله 14: راه‌اندازی سرویس‌ها..."

supervisorctl start django
supervisorctl start telegram_bot

# بررسی وضعیت سرویس‌ها
sleep 3
supervisorctl status

print_success "سرویس‌ها راه‌اندازی شدند"

# مرحله 15: نمایش اطلاعات نهایی
echo
echo "=========================================="
echo "🎉 استقرار کامل سیستم با موفقیت انجام شد!"
echo "=========================================="
echo
echo "📋 اطلاعات مهم:"
echo "   • آدرس وب: http://$(hostname -I | awk '{print $1}')"
echo "   • مسیر پروژه: $(pwd)"
echo "   • محیط مجازی: $(pwd)/venv"
echo "   • X-UI آدرس: https://time.amirprogrammer.ir:50987/YvIhWQ3Pt6cHGXegE4/"
echo
echo "🔧 دستورات مفید:"
echo "   • بررسی وضعیت: supervisorctl status"
echo "   • راه‌اندازی مجدد: supervisorctl restart django"
echo "   • مشاهده لاگ‌ها: tail -f /var/log/django.log"
echo "   • دسترسی به Django: source venv/bin/activate && python manage.py shell"
echo
echo "⚠️ نکات مهم:"
echo "   1. حتماً کاربر ادمین Django ایجاد کنید: python manage.py createsuperuser"
echo "   2. ID ادمین تلگرام را در env_config.env تنظیم کنید"
echo "   3. شماره inbound X-UI را پیدا کنید"
echo "   4. از سیستم پشتیبان تهیه کنید"
echo
echo "📚 مستندات:"
echo "   • راهنمای کامل: DEPLOYMENT_GUIDE.md"
echo "   • راهنمای X-UI: Sanaei_XUI_Setup_Guide.md"
echo

print_success "استقرار کامل تمام شد!"
