#!/bin/bash

# اسکریپت نصب و راه‌اندازی خودکار سیستم VPN Bot
# این اسکریپت تمام مراحل نصب و راه‌اندازی را به صورت خودکار انجام می‌دهد

set -e  # در صورت خطا متوقف شود

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

# بررسی Python
print_message "بررسی Python..."
if ! command -v python3 &> /dev/null; then
    print_error "Python3 نصب نیست! لطفا ابتدا Python3 را نصب کنید."
    exit 1
fi
PYTHON_VERSION=$(python3 --version)
print_success "Python پیدا شد: $PYTHON_VERSION"

# بررسی pip
print_message "بررسی pip..."
if ! command -v pip3 &> /dev/null; then
    print_error "pip3 نصب نیست! لطفا ابتدا pip3 را نصب کنید."
    exit 1
fi
print_success "pip پیدا شد"

# ایجاد محیط مجازی
print_message "ایجاد محیط مجازی..."
if [ ! -d "venv" ]; then
    python3 -m venv venv
    print_success "محیط مجازی ایجاد شد"
else
    print_warning "محیط مجازی از قبل وجود دارد"
fi

# فعال‌سازی محیط مجازی
print_message "فعال‌سازی محیط مجازی..."
source venv/bin/activate
print_success "محیط مجازی فعال شد"

# به‌روزرسانی pip
print_message "به‌روزرسانی pip..."
pip install --upgrade pip --quiet
print_success "pip به‌روزرسانی شد"

# نصب وابستگی‌ها
print_message "نصب وابستگی‌ها..."
pip install -r requirements.txt --quiet
print_success "وابستگی‌ها نصب شدند"

# ایجاد دایرکتوری‌های لازم
print_message "ایجاد دایرکتوری‌های لازم..."
mkdir -p static media logs backups
print_success "دایرکتوری‌ها ایجاد شدند"

# اجرای migrations
print_message "اجرای migrations..."
python manage.py migrate --noinput
print_success "Migrations اجرا شدند"

# جمع‌آوری static files
print_message "جمع‌آوری static files..."
python manage.py collectstatic --noinput --clear
print_success "Static files جمع‌آوری شدند"

# بارگذاری داده‌های اولیه
print_message "بارگذاری داده‌های اولیه..."
python load_initial_data.py
print_success "داده‌های اولیه بارگذاری شدند"

# بررسی سیستم
print_message "بررسی سیستم..."
python manage.py check
print_success "بررسی سیستم بدون خطا انجام شد"

print ""
print "=" * 60
print_success "✅ نصب و راه‌اندازی با موفقیت انجام شد!"
print "=" * 60
print ""
print "📋 اطلاعات ورود به پنل ادمین:"
print "   URL: http://localhost:8000/admin/"
print "   Username: admin"
print "   Password: $(grep ADMIN_PASSWORD config.env | cut -d'=' -f2)"
print ""
print "🚀 برای اجرای سرور:"
print "   source venv/bin/activate"
print "   python manage.py runserver 0.0.0.0:8000"
print ""

