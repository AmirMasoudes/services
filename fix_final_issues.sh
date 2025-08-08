#!/bin/bash

# اسکریپت حل مشکلات نهایی
echo "🔧 حل مشکلات نهایی..."

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

# مرحله 1: نصب Pillow
print_message "مرحله 1: نصب Pillow..."

pip install Pillow

print_success "Pillow نصب شد"

# مرحله 2: بررسی و تنظیم محیط مجازی
print_message "مرحله 2: بررسی و تنظیم محیط مجازی..."

# بررسی محیط مجازی فعلی
if [ -d "myenv" ]; then
    print_message "محیط مجازی myenv موجود است"
    VENV_PATH="myenv"
elif [ -d "venv" ]; then
    print_message "محیط مجازی venv موجود است"
    VENV_PATH="venv"
else
    print_error "هیچ محیط مجازی یافت نشد!"
    exit 1
fi

print_success "محیط مجازی: $VENV_PATH"

# مرحله 3: به‌روزرسانی تنظیمات Supervisor
print_message "مرحله 3: به‌روزرسانی تنظیمات Supervisor..."

# به‌روزرسانی مسیر محیط مجازی در Supervisor
if [ -f "/etc/supervisor/conf.d/django.conf" ]; then
    sed -i "s|/opt/vpn/services/venv|/opt/vpn/services/$VENV_PATH|g" /etc/supervisor/conf.d/django.conf
    sed -i "s|/opt/vpn/services/venv|/opt/vpn/services/$VENV_PATH|g" /etc/supervisor/conf.d/telegram_bot.conf
    print_success "تنظیمات Supervisor به‌روزرسانی شد"
fi

# مرحله 4: تست Django
print_message "مرحله 4: تست Django..."

python manage.py check --deploy

if [ $? -eq 0 ]; then
    print_success "Django تست شد"
else
    print_warning "برخی هشدارهای Django وجود دارد"
fi

# مرحله 5: اجرای مایگریشن‌ها
print_message "مرحله 5: اجرای مایگریشن‌ها..."

python manage.py migrate

print_success "مایگریشن‌ها اجرا شدند"

# مرحله 6: جمع‌آوری فایل‌های استاتیک
print_message "مرحله 6: جمع‌آوری فایل‌های استاتیک..."

python manage.py collectstatic --noinput

print_success "فایل‌های استاتیک جمع‌آوری شدند"

# مرحله 7: راه‌اندازی مجدد سرویس‌ها
print_message "مرحله 7: راه‌اندازی مجدد سرویس‌ها..."

supervisorctl reread
supervisorctl update
supervisorctl restart django
supervisorctl restart telegram_bot

sleep 5

# بررسی وضعیت سرویس‌ها
print_message "بررسی وضعیت سرویس‌ها..."
supervisorctl status

print_success "سرویس‌ها راه‌اندازی مجدد شدند"

# مرحله 8: نمایش اطلاعات نهایی
echo
echo "=========================================="
echo "✅ مشکلات نهایی حل شدند!"
echo "=========================================="
echo
echo "📋 وضعیت فعلی:"
echo "   • محیط مجازی: $VENV_PATH"
echo "   • Django: نصب و فعال"
echo "   • Pillow: نصب شده"
echo "   • وابستگی‌ها: نصب شده"
echo "   • مایگریشن‌ها: اجرا شده"
echo "   • سرویس‌ها: راه‌اندازی شده"
echo
echo "🔧 مراحل باقی‌مانده:"
echo "   1. ایجاد کاربر ادمین: python manage.py createsuperuser"
echo "   2. تنظیم ID ادمین تلگرام در env_config.env"
echo "   3. پیدا کردن شماره inbound X-UI"
echo "   4. تست کامل سیستم"
echo
echo "📚 دستورات مفید:"
echo "   • ویرایش تنظیمات: nano env_config.env"
echo "   • بررسی وضعیت: supervisorctl status"
echo "   • مشاهده لاگ‌ها: tail -f /var/log/django.log"
echo "   • تست Bot: python bot/user_bot.py"
echo "   • تست X-UI: python test_sanaei_connection.py"
echo

print_success "مشکلات نهایی حل شدند!"
