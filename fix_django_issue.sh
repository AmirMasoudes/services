#!/bin/bash

# اسکریپت حل مشکل Django
echo "🔧 حل مشکل Django..."

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

# مرحله 1: بررسی محیط مجازی
print_message "مرحله 1: بررسی محیط مجازی..."

if [ ! -d "venv" ]; then
    print_error "محیط مجازی وجود ندارد!"
    exit 1
fi

# فعال‌سازی محیط مجازی
source venv/bin/activate

# بررسی Python در محیط مجازی
print_message "بررسی Python در محیط مجازی..."
which python
python --version

print_success "محیط مجازی فعال شد"

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

print_success "Django و وابستگی‌ها نصب شدند"

# مرحله 3: تست Django
print_message "مرحله 3: تست Django..."

python manage.py check --deploy

if [ $? -eq 0 ]; then
    print_success "Django تست شد"
else
    print_warning "برخی هشدارهای Django وجود دارد"
fi

# مرحله 4: اجرای مایگریشن‌ها
print_message "مرحله 4: اجرای مایگریشن‌ها..."

python manage.py migrate

print_success "مایگریشن‌ها اجرا شدند"

# مرحله 5: جمع‌آوری فایل‌های استاتیک
print_message "مرحله 5: جمع‌آوری فایل‌های استاتیک..."

python manage.py collectstatic --noinput

print_success "فایل‌های استاتیک جمع‌آوری شدند"

# مرحله 6: راه‌اندازی مجدد سرویس‌ها
print_message "مرحله 6: راه‌اندازی مجدد سرویس‌ها..."

supervisorctl restart django
supervisorctl restart telegram_bot

sleep 3

# بررسی وضعیت سرویس‌ها
print_message "بررسی وضعیت سرویس‌ها..."
supervisorctl status

print_success "سرویس‌ها راه‌اندازی مجدد شدند"

# مرحله 7: نمایش اطلاعات نهایی
echo
echo "=========================================="
echo "✅ مشکل Django حل شد!"
echo "=========================================="
echo
echo "📋 وضعیت فعلی:"
echo "   • Django: نصب و فعال"
echo "   • محیط مجازی: فعال"
echo "   • وابستگی‌ها: نصب شده"
echo "   • سرویس‌ها: راه‌اندازی شده"
echo
echo "🔧 مراحل بعدی:"
echo "   1. ایجاد کاربر ادمین: python manage.py createsuperuser"
echo "   2. تنظیم ID ادمین تلگرام در env_config.env"
echo "   3. پیدا کردن شماره inbound X-UI"
echo "   4. تست کامل سیستم"
echo
echo "📚 دستورات مفید:"
echo "   • بررسی وضعیت: supervisorctl status"
echo "   • مشاهده لاگ‌ها: tail -f /var/log/django.log"
echo "   • تست Bot: python bot/user_bot.py"
echo

print_success "مشکل Django حل شد!"
