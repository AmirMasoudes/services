#!/bin/bash

# اسکریپت پاک کردن فایل‌های اضافی
echo "🧹 پاک کردن فایل‌های اضافی..."

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

# مرحله 1: پاک کردن فایل‌های تکراری
print_message "مرحله 1: پاک کردن فایل‌های تکراری..."

# فایل‌های تنظیمات تکراری
rm -f env_config_simple.env
rm -f env.example
rm -f load_env.py

# فایل‌های اسکریپت تکراری
rm -f fix_remaining_issues.sh
rm -f fix_django_issue.sh
rm -f fix_all_issues.sh
rm -f fix_final_issues.sh
rm -f complete_setup.sh
rm -f deploy.sh
rm -f setup_env.sh
rm -f install_sudo.sh
rm -f fix_issues.sh

# فایل‌های تست تکراری
rm -f test_connection_simple.py
rm -f test_xui_api.py

# فایل‌های راهنما تکراری
rm -f DEPLOYMENT_GUIDE.md
rm -f QUICK_DEPLOY.md
rm -f QUICK_SETUP.md
rm -f Sanaei_XUI_Setup_Guide.md
rm -f FINAL_SETTINGS.md
rm -f ENV_CHANGES_SUMMARY.md
rm -f ENV_SETUP_GUIDE.md
rm -f XUI_INTEGRATION_GUIDE.md

print_success "فایل‌های تکراری پاک شدند"

# مرحله 2: ادغام فایل‌های تنظیمات
print_message "مرحله 2: ادغام فایل‌های تنظیمات..."

# حفظ فقط env_config.env
print_success "فایل env_config.env حفظ شد"

# مرحله 3: ایجاد فایل تنظیمات نهایی
print_message "مرحله 3: ایجاد فایل تنظیمات نهایی..."

# کپی env_config.env به config.env
cp env_config.env config.env

print_success "فایل config.env ایجاد شد"

# مرحله 4: نمایش ساختار نهایی
print_message "مرحله 4: نمایش ساختار نهایی..."

echo "📁 ساختار نهایی پروژه:"
echo "   • config.env - فایل تنظیمات اصلی"
echo "   • django.conf - تنظیمات Django Supervisor"
echo "   • telegram_bot.conf - تنظیمات Bot Supervisor"
echo "   • install_dependencies.sh - نصب وابستگی‌ها"
echo "   • update_supervisor.sh - به‌روزرسانی Supervisor"
echo "   • cleanup_project.sh - پاک کردن فایل‌های اضافی"
echo "   • test_sanaei_connection.py - تست اتصال X-UI"

print_success "پروژه تمیز شد!"

echo
echo "=========================================="
echo "✅ پروژه تمیز شد!"
echo "=========================================="
echo
echo "📋 فایل‌های باقی‌مانده:"
echo "   • config.env - تنظیمات اصلی"
echo "   • django.conf - Django Supervisor"
echo "   • telegram_bot.conf - Bot Supervisor"
echo "   • install_dependencies.sh - نصب وابستگی‌ها"
echo "   • update_supervisor.sh - به‌روزرسانی Supervisor"
echo
echo "🔧 مراحل بعدی:"
echo "   1. اجرای install_dependencies.sh"
echo "   2. اجرای update_supervisor.sh"
echo "   3. تست سیستم"
echo

print_success "پروژه تمیز شد!"
