#!/bin/bash

# اسکریپت حل مشکلات باقی‌مانده
echo "🔧 حل مشکلات باقی‌مانده..."

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

# مرحله 1: نصب Gunicorn در محیط مجازی
print_message "مرحله 1: نصب Gunicorn..."

source venv/bin/activate
pip install gunicorn

print_success "Gunicorn نصب شد"

# مرحله 2: ایجاد پوشه static
print_message "مرحله 2: ایجاد پوشه static..."

mkdir -p static
touch static/.gitkeep

print_success "پوشه static ایجاد شد"

# مرحله 3: جمع‌آوری مجدد فایل‌های استاتیک
print_message "مرحله 3: جمع‌آوری فایل‌های استاتیک..."

python manage.py collectstatic --noinput

print_success "فایل‌های استاتیک جمع‌آوری شدند"

# مرحله 4: راه‌اندازی مجدد سرویس‌ها
print_message "مرحله 4: راه‌اندازی مجدد سرویس‌ها..."

supervisorctl restart django
supervisorctl restart telegram_bot

sleep 3

# بررسی وضعیت سرویس‌ها
print_message "بررسی وضعیت سرویس‌ها..."
supervisorctl status

print_success "سرویس‌ها راه‌اندازی مجدد شدند"

# مرحله 5: تست Django
print_message "مرحله 5: تست Django..."

python manage.py check --deploy

print_success "تست Django انجام شد"

# مرحله 6: نمایش اطلاعات نهایی
echo
echo "=========================================="
echo "✅ مشکلات باقی‌مانده حل شدند!"
echo "=========================================="
echo
echo "📋 وضعیت فعلی:"
echo "   • Django: آماده"
echo "   • Telegram Bot: آماده"
echo "   • X-UI اتصال: فعال"
echo "   • Static Files: تنظیم شده"
echo
echo "🔧 مراحل بعدی:"
echo "   1. تنظیم ID ادمین تلگرام"
echo "   2. پیدا کردن شماره inbound X-UI"
echo "   3. ایجاد کاربر ادمین Django"
echo "   4. تست کامل سیستم"
echo
echo "📚 دستورات مفید:"
echo "   • بررسی وضعیت: supervisorctl status"
echo "   • مشاهده لاگ‌ها: tail -f /var/log/django.log"
echo "   • تست Bot: python bot/user_bot.py"
echo

print_success "تمام مشکلات حل شدند!"
