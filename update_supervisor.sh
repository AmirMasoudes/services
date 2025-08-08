#!/bin/bash

# اسکریپت به‌روزرسانی Supervisor
echo "🔧 به‌روزرسانی Supervisor..."

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

# مرحله 2: حذف فایل‌های قدیمی Supervisor
print_message "مرحله 2: حذف فایل‌های قدیمی Supervisor..."

rm -f /etc/supervisor/conf.d/django.conf
rm -f /etc/supervisor/conf.d/telegram_bot.conf

print_success "فایل‌های قدیمی حذف شدند"

# مرحله 3: کپی فایل‌های جدید Supervisor
print_message "مرحله 3: کپی فایل‌های جدید Supervisor..."

cp django.conf /etc/supervisor/conf.d/
cp telegram_bot.conf /etc/supervisor/conf.d/

print_success "فایل‌های جدید کپی شدند"

# مرحله 4: بررسی محتوای فایل‌ها
print_message "مرحله 4: بررسی محتوای فایل‌ها..."

echo "📋 محتوای django.conf:"
cat /etc/supervisor/conf.d/django.conf

echo -e "\n📋 محتوای telegram_bot.conf:"
cat /etc/supervisor/conf.d/telegram_bot.conf

# مرحله 5: به‌روزرسانی Supervisor
print_message "مرحله 5: به‌روزرسانی Supervisor..."

supervisorctl reread
supervisorctl update

print_success "Supervisor به‌روزرسانی شد"

# مرحله 6: راه‌اندازی سرویس‌ها
print_message "مرحله 6: راه‌اندازی سرویس‌ها..."

supervisorctl start django
supervisorctl start telegram_bot

sleep 5

# بررسی وضعیت سرویس‌ها
print_message "بررسی وضعیت سرویس‌ها..."
supervisorctl status

print_success "سرویس‌ها راه‌اندازی شدند"

# مرحله 7: نمایش اطلاعات نهایی
echo
echo "=========================================="
echo "✅ Supervisor به‌روزرسانی شد!"
echo "=========================================="
echo
echo "📋 وضعیت فعلی:"
echo "   • محیط مجازی: $VENV_PATH"
echo "   • Django: راه‌اندازی شده"
echo "   • Telegram Bot: راه‌اندازی شده"
echo "   • Supervisor: به‌روزرسانی شده"
echo
echo "🔧 مراحل بعدی:"
echo "   1. بررسی لاگ‌ها: tail -f /var/log/django.log"
echo "   2. تست Bot: python bot/user_bot.py"
echo "   3. ایجاد کاربر ادمین: python manage.py createsuperuser"
echo "   4. تست کامل سیستم"
echo
echo "📚 دستورات مفید:"
echo "   • بررسی وضعیت: supervisorctl status"
echo "   • مشاهده لاگ‌ها: tail -f /var/log/django.log"
echo "   • راه‌اندازی مجدد: supervisorctl restart django"
echo

print_success "Supervisor به‌روزرسانی شد!"
