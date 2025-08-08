#!/bin/bash

# اسکریپت نصب وابستگی‌ها در محیط مجازی صحیح
echo "🔧 نصب وابستگی‌ها در محیط مجازی صحیح..."

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

# مرحله 2: فعال‌سازی محیط مجازی
print_message "مرحله 2: فعال‌سازی محیط مجازی..."

source $VENV_PATH/bin/activate

print_success "محیط مجازی فعال شد"

# مرحله 3: نصب وابستگی‌ها
print_message "مرحله 3: نصب وابستگی‌ها..."

# به‌روزرسانی pip
pip install --upgrade pip

# نصب Django و وابستگی‌ها
pip install django
pip install djangorestframework
pip install python-telegram-bot
pip install requests
pip install gunicorn
pip install python-dotenv
pip install Pillow
pip install nest-asyncio
pip install urllib3

print_success "وابستگی‌ها نصب شدند"

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

# مرحله 7: نمایش اطلاعات نهایی
echo
echo "=========================================="
echo "✅ وابستگی‌ها نصب شدند!"
echo "=========================================="
echo
echo "📋 وضعیت فعلی:"
echo "   • محیط مجازی: $VENV_PATH"
echo "   • Django: نصب و فعال"
echo "   • وابستگی‌ها: نصب شده"
echo "   • مایگریشن‌ها: اجرا شده"
echo
echo "🔧 مراحل بعدی:"
echo "   1. به‌روزرسانی فایل‌های Supervisor"
echo "   2. راه‌اندازی سرویس‌ها"
echo "   3. ایجاد کاربر ادمین"
echo "   4. تست کامل سیستم"
echo

print_success "وابستگی‌ها نصب شدند!"
