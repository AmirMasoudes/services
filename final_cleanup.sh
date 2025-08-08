#!/bin/bash

# اسکریپت پاک کردن نهایی
echo "🧹 پاک کردن نهایی..."

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

# مرحله 1: حذف فایل‌های اضافی باقی‌مانده
print_message "مرحله 1: حذف فایل‌های اضافی باقی‌مانده..."

# حذف فایل‌های اضافی
rm -f cleanup_main.sh
rm -f start_bots.py
rm -f README.md

print_success "فایل‌های اضافی حذف شدند"

# مرحله 2: ایجاد README نهایی
print_message "مرحله 2: ایجاد README نهایی..."

cat > README.md << 'EOF'
# VPN Bot System

## فایل‌های اصلی:

### تنظیمات:
- `config.env` - تنظیمات اصلی سیستم

### Supervisor:
- `django.conf` - تنظیمات Django
- `telegram_bot.conf` - تنظیمات Bot

### اسکریپت‌ها:
- `setup_final.sh` - راه‌اندازی نهایی
- `install_dependencies.sh` - نصب وابستگی‌ها
- `update_supervisor.sh` - به‌روزرسانی Supervisor

### تست:
- `test_sanaei_connection.py` - تست اتصال X-UI

## مراحل راه‌اندازی:

1. اجرای setup_final.sh:
```bash
chmod +x setup_final.sh
./setup_final.sh
```

2. تنظیم config.env:
```bash
nano config.env
```

3. ایجاد کاربر ادمین:
```bash
python manage.py createsuperuser
```

4. تست سیستم:
```bash
supervisorctl status
python bot/user_bot.py
python test_sanaei_connection.py
```

## دستورات مفید:

- بررسی وضعیت: `supervisorctl status`
- مشاهده لاگ‌ها: `tail -f /var/log/django.log`
- ویرایش تنظیمات: `nano config.env`
EOF

print_success "README نهایی ایجاد شد"

# مرحله 3: نمایش ساختار نهایی
print_message "مرحله 3: نمایش ساختار نهایی..."

echo "📁 ساختار نهایی پروژه:"
ls -la *.env *.conf *.sh *.py *.md 2>/dev/null | grep -E '\.(env|conf|sh|py|md)$'

print_success "پروژه تمیز شد!"

echo
echo "=========================================="
echo "✅ پروژه کاملاً تمیز شد!"
echo "=========================================="
echo
echo "📋 فایل‌های نهایی:"
echo "   • config.env - تنظیمات اصلی"
echo "   • django.conf - Django Supervisor"
echo "   • telegram_bot.conf - Bot Supervisor"
echo "   • setup_final.sh - راه‌اندازی نهایی"
echo "   • install_dependencies.sh - نصب وابستگی‌ها"
echo "   • update_supervisor.sh - به‌روزرسانی Supervisor"
echo "   • test_sanaei_connection.py - تست اتصال X-UI"
echo "   • README.md - راهنمای نهایی"
echo
echo "🔧 مراحل بعدی:"
echo "   1. اجرای setup_final.sh"
echo "   2. تنظیم config.env"
echo "   3. ایجاد کاربر ادمین"
echo "   4. تست سیستم"
echo

print_success "پروژه کاملاً تمیز شد!"
