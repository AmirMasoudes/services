#!/bin/bash

# VPN Bot Services Installation Script
# این اسکریپت سرویس‌های systemd را نصب و راه‌اندازی می‌کند

set -e

# رنگ‌ها برای خروجی
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# تابع نمایش پیام
print_message() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

print_header() {
    echo -e "${BLUE}================================${NC}"
    echo -e "${BLUE}$1${NC}"
    echo -e "${BLUE}================================${NC}"
}

# بررسی root بودن
check_root() {
    if [[ $EUID -ne 0 ]]; then
        print_error "این اسکریپت باید با دسترسی root اجرا شود"
        exit 1
    fi
}

# بررسی وجود systemd
check_systemd() {
    if ! command -v systemctl &> /dev/null; then
        print_error "systemd در این سیستم نصب نیست"
        exit 1
    fi
}

# بررسی مسیر پروژه
check_project_path() {
    PROJECT_PATH="/opt/vpnbot"
    
    if [[ ! -d "$PROJECT_PATH" ]]; then
        print_warning "مسیر پروژه $PROJECT_PATH یافت نشد"
        read -p "آیا می‌خواهید مسیر پروژه را تغییر دهید؟ (y/n): " -n 1 -r
        echo
        if [[ $REPLY =~ ^[Yy]$ ]]; then
            read -p "مسیر جدید پروژه را وارد کنید: " PROJECT_PATH
        else
            print_error "لطفاً ابتدا پروژه را در مسیر صحیح نصب کنید"
            exit 1
        fi
    fi
    
    # به‌روزرسانی مسیر در فایل‌های سرویس
    update_service_paths
}

# به‌روزرسانی مسیرها در فایل‌های سرویس
update_service_paths() {
    print_message "به‌روزرسانی مسیرها در فایل‌های سرویس..."
    
    # کپی فایل‌های سرویس به مسیر موقت
    cp services/django.service /tmp/django.service
    cp services/admin-bot.service /tmp/admin-bot.service
    cp services/user-bot.service /tmp/user-bot.service
    
    # جایگزینی مسیرها
    sed -i "s|/opt/vpnbot|$PROJECT_PATH|g" /tmp/django.service
    sed -i "s|/opt/vpnbot|$PROJECT_PATH|g" /tmp/admin-bot.service
    sed -i "s|/opt/vpnbot|$PROJECT_PATH|g" /tmp/user-bot.service
    
    print_message "مسیرها به‌روزرسانی شدند"
}

# ایجاد کاربر و گروه
create_user() {
    print_message "ایجاد کاربر و گروه..."
    
    if ! id "www-data" &>/dev/null; then
        useradd -r -s /bin/false -d /opt/vpnbot www-data
        print_message "کاربر www-data ایجاد شد"
    else
        print_message "کاربر www-data از قبل وجود دارد"
    fi
    
    # تغییر مالکیت فایل‌ها
    chown -R www-data:www-data "$PROJECT_PATH"
    chmod -R 755 "$PROJECT_PATH"
    
    # ایجاد دایرکتوری‌های مورد نیاز
    mkdir -p "$PROJECT_PATH/logs"
    mkdir -p "$PROJECT_PATH/backups"
    mkdir -p "$PROJECT_PATH/media"
    mkdir -p "$PROJECT_PATH/staticfiles"
    
    chown -R www-data:www-data "$PROJECT_PATH/logs"
    chown -R www-data:www-data "$PROJECT_PATH/backups"
    chown -R www-data:www-data "$PROJECT_PATH/media"
    chown -R www-data:www-data "$PROJECT_PATH/staticfiles"
}

# نصب فایل‌های سرویس
install_services() {
    print_message "نصب فایل‌های سرویس..."
    
    # کپی فایل‌های سرویس
    cp /tmp/django.service /etc/systemd/system/
    cp /tmp/admin-bot.service /etc/systemd/system/
    cp /tmp/user-bot.service /etc/systemd/system/
    cp services/vpnbot.target /etc/systemd/system/
    
    # تنظیم مجوزها
    chmod 644 /etc/systemd/system/django.service
    chmod 644 /etc/systemd/system/admin-bot.service
    chmod 644 /etc/systemd/system/user-bot.service
    chmod 644 /etc/systemd/system/vpnbot.target
    
    # بارگذاری مجدد systemd
    systemctl daemon-reload
    
    print_message "فایل‌های سرویس نصب شدند"
}

# فعال‌سازی سرویس‌ها
enable_services() {
    print_message "فعال‌سازی سرویس‌ها..."
    
    systemctl enable django.service
    systemctl enable admin-bot.service
    systemctl enable user-bot.service
    systemctl enable vpnbot.target
    
    print_message "سرویس‌ها فعال شدند"
}

# راه‌اندازی سرویس‌ها
start_services() {
    print_message "راه‌اندازی سرویس‌ها..."
    
    systemctl start django.service
    sleep 5
    
    systemctl start admin-bot.service
    sleep 3
    
    systemctl start user-bot.service
    sleep 3
    
    print_message "سرویس‌ها راه‌اندازی شدند"
}

# بررسی وضعیت سرویس‌ها
check_services_status() {
    print_header "بررسی وضعیت سرویس‌ها"
    
    services=("django" "admin-bot" "user-bot")
    
    for service in "${services[@]}"; do
        if systemctl is-active --quiet "$service.service"; then
            print_message "$service: فعال ✅"
        else
            print_error "$service: غیرفعال ❌"
        fi
    done
    
    echo
    print_message "برای مشاهده لاگ‌ها از دستور زیر استفاده کنید:"
    echo "journalctl -u django.service -f"
    echo "journalctl -u admin-bot.service -f"
    echo "journalctl -u user-bot.service -f"
}

# نمایش راهنما
show_help() {
    print_header "راهنمای مدیریت سرویس‌ها"
    
    echo "دستورات مفید:"
    echo
    echo "📋 مشاهده وضعیت:"
    echo "   systemctl status django.service"
    echo "   systemctl status admin-bot.service"
    echo "   systemctl status user-bot.service"
    echo
    echo "🔄 راه‌اندازی مجدد:"
    echo "   systemctl restart django.service"
    echo "   systemctl restart admin-bot.service"
    echo "   systemctl restart user-bot.service"
    echo
    echo "⏹️ توقف:"
    echo "   systemctl stop django.service"
    echo "   systemctl stop admin-bot.service"
    echo "   systemctl stop user-bot.service"
    echo
    echo "📊 مشاهده لاگ‌ها:"
    echo "   journalctl -u django.service -f"
    echo "   journalctl -u admin-bot.service -f"
    echo "   journalctl -u user-bot.service -f"
    echo
    echo "🔧 مدیریت تمام سرویس‌ها:"
    echo "   systemctl start vpnbot.target"
    echo "   systemctl stop vpnbot.target"
    echo "   systemctl restart vpnbot.target"
}

# تابع اصلی
main() {
    print_header "نصب سرویس‌های VPN Bot"
    
    check_root
    check_systemd
    check_project_path
    create_user
    install_services
    enable_services
    start_services
    check_services_status
    
    print_header "نصب با موفقیت انجام شد"
    show_help
}

# اجرای تابع اصلی
main "$@" 