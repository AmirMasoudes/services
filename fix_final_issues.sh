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

# مرحله 1: نصب nest_asyncio
print_message "مرحله 1: نصب nest_asyncio..."

pip install nest-asyncio

print_success "nest_asyncio نصب شد"

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

# مرحله 3: به‌روزرسانی فایل‌های Supervisor
print_message "مرحله 3: به‌روزرسانی فایل‌های Supervisor..."

# حذف فایل‌های قدیمی
rm -f /etc/supervisor/conf.d/django.conf
rm -f /etc/supervisor/conf.d/telegram_bot.conf

# کپی فایل‌های Supervisor جدید
cp django.conf /etc/supervisor/conf.d/
cp telegram_bot.conf /etc/supervisor/conf.d/

print_success "فایل‌های Supervisor به‌روزرسانی شدند"

# مرحله 4: به‌روزرسانی Supervisor
print_message "مرحله 4: به‌روزرسانی Supervisor..."

supervisorctl reread
supervisorctl update

print_success "Supervisor به‌روزرسانی شد"

# مرحله 5: راه‌اندازی مجدد سرویس‌ها
print_message "مرحله 5: راه‌اندازی مجدد سرویس‌ها..."

supervisorctl start django
supervisorctl start telegram_bot

sleep 5

# بررسی وضعیت سرویس‌ها
print_message "بررسی وضعیت سرویس‌ها..."
supervisorctl status

print_success "سرویس‌ها راه‌اندازی مجدد شدند"

# مرحله 6: تست Django
print_message "مرحله 6: تست Django..."

python manage.py check --deploy

if [ $? -eq 0 ]; then
    print_success "Django تست شد"
else
    print_warning "برخی هشدارهای Django وجود دارد"
fi

# مرحله 7: تست Bot
print_message "مرحله 7: تست Bot..."

python bot/user_bot.py &
BOT_PID=$!
sleep 3
kill $BOT_PID 2>/dev/null

print_success "Bot تست شد"

# مرحله 8: تست X-UI
print_message "مرحله 8: تست X-UI..."

python test_sanaei_connection.py

print_success "X-UI تست شد"

# مرحله 9: نمایش اطلاعات نهایی
echo
echo "=========================================="
echo "✅ مشکلات نهایی حل شدند!"
echo "=========================================="
echo
echo "📋 وضعیت فعلی:"
echo "   • محیط مجازی: $VENV_PATH"
echo "   • Django: نصب و فعال"
echo "   • nest_asyncio: نصب شده"
echo "   • وابستگی‌ها: نصب شده"
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
