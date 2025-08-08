#!/bin/bash

# اسکریپت پاک کردن و نگه داشتن فایل‌های اصلی
echo "🧹 پاک کردن و نگه داشتن فایل‌های اصلی..."

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

# مرحله 1: حذف تمام فایل‌های اضافی
print_message "مرحله 1: حذف تمام فایل‌های اضافی..."

# حذف فایل‌های تنظیمات اضافی
rm -f env_config.env
rm -f env_config_simple.env
rm -f env.example
rm -f load_env.py

# حذف فایل‌های اسکریپت اضافی
rm -f fix_final_issues.sh
rm -f fix_remaining_issues.sh
rm -f fix_all_issues.sh
rm -f fix_django_issue.sh
rm -f fix_issues.sh
rm -f complete_setup.sh
rm -f deploy.sh
rm -f setup_env.sh
rm -f install_sudo.sh
rm -f cleanup_project.sh
rm -f final_cleanup.sh

# حذف فایل‌های تست اضافی
rm -f test_connection_simple.py
rm -f test_xui_api.py

# حذف فایل‌های راهنما اضافی
rm -f FINAL_SETTINGS.md
rm -f CURRENT_SETTINGS.md
rm -f QUICK_DEPLOY.md
rm -f DEPLOYMENT_GUIDE.md
rm -f SANAEI_SETUP_GUIDE.md
rm -f ENV_CHANGES_SUMMARY.md
rm -f QUICK_SETUP.md
rm -f ENV_SETUP_GUIDE.md
rm -f XUI_INTEGRATION_GUIDE.md
rm -f SANAEI_API_GUIDE.md

# حذف فایل‌های اضافی
rm -f start_bots.py

print_success "فایل‌های اضافی حذف شدند"

# مرحله 2: نمایش فایل‌های باقی‌مانده
print_message "مرحله 2: نمایش فایل‌های باقی‌مانده..."

echo "📁 فایل‌های اصلی باقی‌مانده:"
echo "   • config.env - تنظیمات اصلی"
echo "   • django.conf - تنظیمات Django Supervisor"
echo "   • telegram_bot.conf - تنظیمات Bot Supervisor"
echo "   • setup_final.sh - راه‌اندازی نهایی"
echo "   • install_dependencies.sh - نصب وابستگی‌ها"
echo "   • update_supervisor.sh - به‌روزرسانی Supervisor"
echo "   • test_sanaei_connection.py - تست اتصال X-UI"
echo "   • README_FINAL.md - راهنمای نهایی"

print_success "فایل‌های اصلی حفظ شدند"

# مرحله 3: ایجاد README ساده
print_message "مرحله 3: ایجاد README ساده..."

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

print_success "README ساده ایجاد شد"

# مرحله 4: حذف README قدیمی
rm -f README_FINAL.md

# مرحله 5: نمایش ساختار نهایی
print_message "مرحله 5: نمایش ساختار نهایی..."

echo "📁 ساختار نهایی پروژه:"
ls -la *.env *.conf *.sh *.py *.md 2>/dev/null | grep -E '\.(env|conf|sh|py|md)$'

print_success "پروژه تمیز شد!"

echo
echo "=========================================="
echo "✅ پروژه تمیز شد!"
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

print_success "پروژه تمیز شد!"
