#!/bin/bash

# اسکریپت دیپلوی روی سرور
echo "🚀 شروع دیپلوی روی سرور..."

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

# مرحله 1: بررسی سیستم
print_message "مرحله 1: بررسی سیستم..."

# بررسی سیستم عامل
echo "📋 اطلاعات سیستم:"
echo "   • سیستم عامل: $(uname -a)"
echo "   • نسخه Python: $(python3 --version)"
echo "   • فضای دیسک: $(df -h / | tail -1 | awk '{print $4}')"

# بررسی دسترسی root
if [ "$EUID" -ne 0 ]; then
    print_error "این اسکریپت باید با دسترسی root اجرا شود!"
    exit 1
fi

print_success "بررسی سیستم انجام شد"

# مرحله 2: نصب وابستگی‌های سیستم
print_message "مرحله 2: نصب وابستگی‌های سیستم..."

# به‌روزرسانی سیستم
apt update -y

# نصب وابستگی‌های ضروری
apt install -y python3 python3-pip python3-venv nginx supervisor curl wget git

print_success "وابستگی‌های سیستم نصب شدند"

# مرحله 3: ایجاد دایرکتوری پروژه
print_message "مرحله 3: ایجاد دایرکتوری پروژه..."

# ایجاد دایرکتوری پروژه
mkdir -p /opt/vpn/services
cd /opt/vpn/services

print_success "دایرکتوری پروژه ایجاد شد"

# مرحله 4: کپی فایل‌های پروژه
print_message "مرحله 4: کپی فایل‌های پروژه..."

# کپی فایل‌های اصلی
cp config.env /opt/vpn/services/
cp django.conf /opt/vpn/services/
cp telegram_bot.conf /opt/vpn/services/
cp setup_final.sh /opt/vpn/services/
cp install_dependencies.sh /opt/vpn/services/
cp update_supervisor.sh /opt/vpn/services/
cp test_sanaei_connection.py /opt/vpn/services/
cp README.md /opt/vpn/services/

print_success "فایل‌های پروژه کپی شدند"

# مرحله 5: ایجاد محیط مجازی
print_message "مرحله 5: ایجاد محیط مجازی..."

cd /opt/vpn/services
python3 -m venv myenv
source myenv/bin/activate

print_success "محیط مجازی ایجاد شد"

# مرحله 6: نصب وابستگی‌های Python
print_message "مرحله 6: نصب وابستگی‌های Python..."

# اجرای اسکریپت نصب وابستگی‌ها
chmod +x install_dependencies.sh
./install_dependencies.sh

print_success "وابستگی‌های Python نصب شدند"

# مرحله 7: تنظیم Supervisor
print_message "مرحله 7: تنظیم Supervisor..."

# کپی فایل‌های Supervisor
cp django.conf /etc/supervisor/conf.d/
cp telegram_bot.conf /etc/supervisor/conf.d/

# به‌روزرسانی Supervisor
supervisorctl reread
supervisorctl update

print_success "Supervisor تنظیم شد"

# مرحله 8: تنظیم Nginx
print_message "مرحله 8: تنظیم Nginx..."

# ایجاد فایل تنظیمات Nginx
cat > /etc/nginx/sites-available/vpn-bot << 'EOF'
server {
    listen 80;
    server_name _;

    location / {
        proxy_pass http://unix:/opt/vpn/services/django.sock;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    location /static/ {
        alias /opt/vpn/services/staticfiles/;
    }

    location /media/ {
        alias /opt/vpn/services/media/;
    }
}
EOF

# فعال‌سازی سایت
ln -sf /etc/nginx/sites-available/vpn-bot /etc/nginx/sites-enabled/
rm -f /etc/nginx/sites-enabled/default

# تست تنظیمات Nginx
nginx -t

# راه‌اندازی مجدد Nginx
systemctl restart nginx

print_success "Nginx تنظیم شد"

# مرحله 9: تنظیم فایروال
print_message "مرحله 9: تنظیم فایروال..."

# نصب UFW
apt install -y ufw

# تنظیم قوانین فایروال
ufw allow ssh
ufw allow 80
ufw allow 443
ufw --force enable

print_success "فایروال تنظیم شد"

# مرحله 10: راه‌اندازی سرویس‌ها
print_message "مرحله 10: راه‌اندازی سرویس‌ها..."

# راه‌اندازی سرویس‌ها
supervisorctl start django
supervisorctl start telegram_bot

sleep 5

# بررسی وضعیت سرویس‌ها
supervisorctl status

print_success "سرویس‌ها راه‌اندازی شدند"

# مرحله 11: تست سیستم
print_message "مرحله 11: تست سیستم..."

# تست Django
cd /opt/vpn/services
python manage.py check --deploy

# تست Bot
python bot/user_bot.py &
BOT_PID=$!
sleep 3
kill $BOT_PID 2>/dev/null

# تست X-UI
python test_sanaei_connection.py

print_success "تست سیستم انجام شد"

# مرحله 12: نمایش اطلاعات نهایی
echo
echo "=========================================="
echo "✅ دیپلوی کامل شد!"
echo "=========================================="
echo
echo "📋 اطلاعات سرور:"
echo "   • آدرس سرور: $(curl -s ifconfig.me)"
echo "   • مسیر پروژه: /opt/vpn/services"
echo "   • محیط مجازی: myenv"
echo "   • وضعیت سرویس‌ها:"
supervisorctl status
echo
echo "🔧 مراحل باقی‌مانده:"
echo "   1. تنظیم config.env"
echo "   2. ایجاد کاربر ادمین: python manage.py createsuperuser"
echo "   3. تنظیم ID ادمین تلگرام"
echo "   4. پیدا کردن شماره inbound X-UI"
echo
echo "📚 دستورات مفید:"
echo "   • ویرایش تنظیمات: nano /opt/vpn/services/config.env"
echo "   • بررسی وضعیت: supervisorctl status"
echo "   • مشاهده لاگ‌ها: tail -f /var/log/django.log"
echo "   • راه‌اندازی مجدد: supervisorctl restart all"
echo

print_success "دیپلوی کامل شد!"
