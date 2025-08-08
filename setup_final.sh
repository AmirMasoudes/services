#!/bin/bash

# اسکریپت نهایی راه‌اندازی سیستم
echo "🚀 راه‌اندازی نهایی سیستم VPN Bot..."

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

# مرحله 1: پاک کردن فایل‌های اضافی
print_message "مرحله 1: پاک کردن فایل‌های اضافی..."

# اجرای اسکریپت پاک کردن
chmod +x cleanup_project.sh
./cleanup_project.sh

print_success "فایل‌های اضافی پاک شدند"

# مرحله 2: نصب وابستگی‌ها
print_message "مرحله 2: نصب وابستگی‌ها..."

# اجرای اسکریپت نصب وابستگی‌ها
chmod +x install_dependencies.sh
./install_dependencies.sh

print_success "وابستگی‌ها نصب شدند"

# مرحله 3: به‌روزرسانی Supervisor
print_message "مرحله 3: به‌روزرسانی Supervisor..."

# اجرای اسکریپت به‌روزرسانی Supervisor
chmod +x update_supervisor.sh
./update_supervisor.sh

print_success "Supervisor به‌روزرسانی شد"

# مرحله 4: تست سیستم
print_message "مرحله 4: تست سیستم..."

# تست Django
python manage.py check --deploy

# تست Bot
python bot/user_bot.py &
BOT_PID=$!
sleep 3
kill $BOT_PID 2>/dev/null

# تست X-UI
python test_sanaei_connection.py

print_success "تست سیستم انجام شد"

# مرحله 5: نمایش اطلاعات نهایی
echo
echo "=========================================="
echo "✅ سیستم راه‌اندازی شد!"
echo "=========================================="
echo
echo "📋 فایل‌های نهایی:"
echo "   • config.env - تنظیمات اصلی"
echo "   • django.conf - Django Supervisor"
echo "   • telegram_bot.conf - Bot Supervisor"
echo "   • install_dependencies.sh - نصب وابستگی‌ها"
echo "   • update_supervisor.sh - به‌روزرسانی Supervisor"
echo "   • cleanup_project.sh - پاک کردن فایل‌های اضافی"
echo "   • setup_final.sh - راه‌اندازی نهایی"
echo "   • test_sanaei_connection.py - تست اتصال X-UI"
echo
echo "🔧 مراحل باقی‌مانده:"
echo "   1. ایجاد کاربر ادمین: python manage.py createsuperuser"
echo "   2. تنظیم ID ادمین تلگرام در config.env"
echo "   3. پیدا کردن شماره inbound X-UI"
echo "   4. تست کامل سیستم"
echo
echo "📚 دستورات مفید:"
echo "   • ویرایش تنظیمات: nano config.env"
echo "   • بررسی وضعیت: supervisorctl status"
echo "   • مشاهده لاگ‌ها: tail -f /var/log/django.log"
echo "   • تست Bot: python bot/user_bot.py"
echo "   • تست X-UI: python test_sanaei_connection.py"
echo

print_success "سیستم راه‌اندازی شد!"
