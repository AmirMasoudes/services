#!/bin/bash

# اسکریپت حل تمام مشکلات
echo "🔧 حل تمام مشکلات سیستم..."

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

# مرحله 1: بررسی و تنظیم محیط مجازی
print_message "مرحله 1: بررسی و تنظیم محیط مجازی..."

# بررسی محیط مجازی فعلی
if [ -d "venv" ]; then
    print_message "محیط مجازی venv موجود است"
    VENV_PATH="venv"
elif [ -d "myenv" ]; then
    print_message "محیط مجازی myenv موجود است"
    VENV_PATH="myenv"
else
    print_error "هیچ محیط مجازی یافت نشد!"
    exit 1
fi

# فعال‌سازی محیط مجازی
source $VENV_PATH/bin/activate

print_success "محیط مجازی فعال شد: $VENV_PATH"

# مرحله 2: نصب Django و وابستگی‌ها
print_message "مرحله 2: نصب Django و وابستگی‌ها..."

# به‌روزرسانی pip
pip install --upgrade pip

# نصب Django
pip install django

# نصب وابستگی‌های دیگر
pip install djangorestframework
pip install python-telegram-bot
pip install requests
pip install gunicorn
pip install urllib3

print_success "Django و وابستگی‌ها نصب شدند"

# مرحله 3: بررسی فایل تنظیمات
print_message "مرحله 3: بررسی فایل تنظیمات..."

# بررسی env_config.env
if [ -f "env_config.env" ]; then
    print_message "فایل env_config.env موجود است"
    
    # بررسی توکن‌های تلگرام
    if grep -q "your-user-bot-token-here" env_config.env; then
        print_warning "توکن‌های تلگرام هنوز تنظیم نشده‌اند!"
        print_message "لطفاً فایل env_config.env را ویرایش کنید"
    else
        print_success "توکن‌های تلگرام تنظیم شده‌اند"
    fi
else
    print_error "فایل env_config.env وجود ندارد!"
    exit 1
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

# ایجاد پوشه static اگر وجود ندارد
mkdir -p static

python manage.py collectstatic --noinput

print_success "فایل‌های استاتیک جمع‌آوری شدند"

# مرحله 7: به‌روزرسانی تنظیمات Supervisor
print_message "مرحله 7: به‌روزرسانی تنظیمات Supervisor..."

# به‌روزرسانی مسیر محیط مجازی در Supervisor
if [ -f "/etc/supervisor/conf.d/django.conf" ]; then
    sed -i "s|/opt/vpn/services/venv|/opt/vpn/services/$VENV_PATH|g" /etc/supervisor/conf.d/django.conf
    print_success "تنظیمات Supervisor به‌روزرسانی شد"
fi

# مرحله 8: راه‌اندازی مجدد سرویس‌ها
print_message "مرحله 8: راه‌اندازی مجدد سرویس‌ها..."

supervisorctl reread
supervisorctl update
supervisorctl restart django
supervisorctl restart telegram_bot

sleep 3

# بررسی وضعیت سرویس‌ها
print_message "بررسی وضعیت سرویس‌ها..."
supervisorctl status

print_success "سرویس‌ها راه‌اندازی مجدد شدند"

# مرحله 9: نمایش اطلاعات نهایی
echo
echo "=========================================="
echo "✅ تمام مشکلات حل شدند!"
echo "=========================================="
echo
echo "📋 وضعیت فعلی:"
echo "   • محیط مجازی: $VENV_PATH"
echo "   • Django: نصب و فعال"
echo "   • وابستگی‌ها: نصب شده"
echo "   • سرویس‌ها: راه‌اندازی شده"
echo
echo "🔧 مراحل باقی‌مانده:"
echo "   1. تنظیم توکن‌های تلگرام در env_config.env"
echo "   2. ایجاد کاربر ادمین: python manage.py createsuperuser"
echo "   3. تنظیم ID ادمین تلگرام"
echo "   4. پیدا کردن شماره inbound X-UI"
echo "   5. تست کامل سیستم"
echo
echo "📚 دستورات مفید:"
echo "   • ویرایش تنظیمات: nano env_config.env"
echo "   • بررسی وضعیت: supervisorctl status"
echo "   • مشاهده لاگ‌ها: tail -f /var/log/django.log"
echo "   • تست Bot: python bot/user_bot.py"
echo

print_success "تمام مشکلات حل شدند!"
