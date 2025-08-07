#!/bin/bash

# VPN Bot Services Management Script
# اسکریپت مدیریت سرویس‌های VPN Bot

set -e

# رنگ‌ها برای خروجی
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
PURPLE='\033[0;35m'
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

print_subheader() {
    echo -e "${PURPLE}$1${NC}"
}

# بررسی root بودن
check_root() {
    if [[ $EUID -ne 0 ]]; then
        print_error "این اسکریپت باید با دسترسی root اجرا شود"
        exit 1
    fi
}

# نمایش منو
show_menu() {
    clear
    print_header "مدیریت سرویس‌های VPN Bot"
    echo
    echo "1.  مشاهده وضعیت تمام سرویس‌ها"
    echo "2.  راه‌اندازی تمام سرویس‌ها"
    echo "3.  توقف تمام سرویس‌ها"
    echo "4.  راه‌اندازی مجدد تمام سرویس‌ها"
    echo "5.  مشاهده لاگ‌های Django"
    echo "6.  مشاهده لاگ‌های ربات ادمین"
    echo "7.  مشاهده لاگ‌های ربات کاربران"
    echo "8.  مدیریت سرویس Django"
    echo "9.  مدیریت سرویس ربات ادمین"
    echo "10. مدیریت سرویس ربات کاربران"
    echo "11. بررسی عملکرد سیستم"
    echo "12. پشتیبان‌گیری از تنظیمات"
    echo "13. بازگردانی تنظیمات"
    echo "14. به‌روزرسانی سرویس‌ها"
    echo "0.  خروج"
    echo
    read -p "لطفاً گزینه مورد نظر را انتخاب کنید: " choice
}

# مشاهده وضعیت سرویس‌ها
show_status() {
    print_header "وضعیت سرویس‌ها"
    
    services=("django" "admin-bot" "user-bot")
    
    for service in "${services[@]}"; do
        echo -n "$service: "
        if systemctl is-active --quiet "$service.service"; then
            echo -e "${GREEN}فعال${NC}"
        else
            echo -e "${RED}غیرفعال${NC}"
        fi
        
        if systemctl is-enabled --quiet "$service.service"; then
            echo -e "  ${GREEN}✓ خودکار راه‌اندازی می‌شود${NC}"
        else
            echo -e "  ${RED}✗ خودکار راه‌اندازی نمی‌شود${NC}"
        fi
        echo
    done
    
    read -p "برای ادامه Enter را فشار دهید..."
}

# راه‌اندازی تمام سرویس‌ها
start_all_services() {
    print_header "راه‌اندازی تمام سرویس‌ها"
    
    print_message "راه‌اندازی Django..."
    systemctl start django.service
    sleep 3
    
    print_message "راه‌اندازی ربات ادمین..."
    systemctl start admin-bot.service
    sleep 2
    
    print_message "راه‌اندازی ربات کاربران..."
    systemctl start user-bot.service
    sleep 2
    
    print_message "تمام سرویس‌ها راه‌اندازی شدند"
    show_status
}

# توقف تمام سرویس‌ها
stop_all_services() {
    print_header "توقف تمام سرویس‌ها"
    
    print_message "توقف ربات کاربران..."
    systemctl stop user-bot.service
    
    print_message "توقف ربات ادمین..."
    systemctl stop admin-bot.service
    
    print_message "توقف Django..."
    systemctl stop django.service
    
    print_message "تمام سرویس‌ها متوقف شدند"
    show_status
}

# راه‌اندازی مجدد تمام سرویس‌ها
restart_all_services() {
    print_header "راه‌اندازی مجدد تمام سرویس‌ها"
    
    print_message "راه‌اندازی مجدد Django..."
    systemctl restart django.service
    sleep 3
    
    print_message "راه‌اندازی مجدد ربات ادمین..."
    systemctl restart admin-bot.service
    sleep 2
    
    print_message "راه‌اندازی مجدد ربات کاربران..."
    systemctl restart user-bot.service
    sleep 2
    
    print_message "تمام سرویس‌ها راه‌اندازی مجدد شدند"
    show_status
}

# مشاهده لاگ‌ها
show_logs() {
    local service_name=$1
    local service_display_name=$2
    
    print_header "لاگ‌های $service_display_name"
    echo "برای خروج از لاگ‌ها Ctrl+C را فشار دهید"
    echo
    journalctl -u "$service_name.service" -f --lines=50
}

# مدیریت سرویس خاص
manage_service() {
    local service_name=$1
    local service_display_name=$2
    
    while true; do
        clear
        print_header "مدیریت $service_display_name"
        echo
        echo "1. مشاهده وضعیت"
        echo "2. راه‌اندازی"
        echo "3. توقف"
        echo "4. راه‌اندازی مجدد"
        echo "5. مشاهده لاگ‌ها"
        echo "6. فعال‌سازی خودکار"
        echo "7. غیرفعال‌سازی خودکار"
        echo "0. بازگشت به منوی اصلی"
        echo
        read -p "لطفاً گزینه مورد نظر را انتخاب کنید: " sub_choice
        
        case $sub_choice in
            1)
                systemctl status "$service_name.service"
                read -p "برای ادامه Enter را فشار دهید..."
                ;;
            2)
                systemctl start "$service_name.service"
                print_message "$service_display_name راه‌اندازی شد"
                sleep 2
                ;;
            3)
                systemctl stop "$service_name.service"
                print_message "$service_display_name متوقف شد"
                sleep 2
                ;;
            4)
                systemctl restart "$service_name.service"
                print_message "$service_display_name راه‌اندازی مجدد شد"
                sleep 2
                ;;
            5)
                show_logs "$service_name" "$service_display_name"
                ;;
            6)
                systemctl enable "$service_name.service"
                print_message "$service_display_name برای راه‌اندازی خودکار فعال شد"
                sleep 2
                ;;
            7)
                systemctl disable "$service_name.service"
                print_message "$service_display_name از راه‌اندازی خودکار غیرفعال شد"
                sleep 2
                ;;
            0)
                break
                ;;
            *)
                print_error "گزینه نامعتبر"
                sleep 2
                ;;
        esac
    done
}

# بررسی عملکرد سیستم
check_system_performance() {
    print_header "بررسی عملکرد سیستم"
    
    echo "📊 اطلاعات سیستم:"
    echo "CPU Usage: $(top -bn1 | grep "Cpu(s)" | awk '{print $2}' | cut -d'%' -f1)%"
    echo "Memory Usage: $(free | grep Mem | awk '{printf("%.2f%%", $3/$2 * 100.0)}')"
    echo "Disk Usage: $(df -h / | awk 'NR==2 {print $5}')"
    echo
    
    echo "🔧 وضعیت سرویس‌ها:"
    services=("django" "admin-bot" "user-bot")
    for service in "${services[@]}"; do
        if systemctl is-active --quiet "$service.service"; then
            echo -e "$service: ${GREEN}فعال${NC}"
        else
            echo -e "$service: ${RED}غیرفعال${NC}"
        fi
    done
    echo
    
    echo "📈 آمار سرویس‌ها:"
    for service in "${services[@]}"; do
        if systemctl is-active --quiet "$service.service"; then
            uptime=$(systemctl show "$service.service" --property=ActiveEnterTimestamp | cut -d'=' -f2)
            echo "$service: از $uptime فعال است"
        fi
    done
    
    read -p "برای ادامه Enter را فشار دهید..."
}

# پشتیبان‌گیری از تنظیمات
backup_config() {
    print_header "پشتیبان‌گیری از تنظیمات"
    
    BACKUP_DIR="/opt/vpnbot/backups"
    BACKUP_FILE="vpnbot_config_$(date +%Y%m%d_%H%M%S).tar.gz"
    
    mkdir -p "$BACKUP_DIR"
    
    print_message "ایجاد پشتیبان از تنظیمات..."
    tar -czf "$BACKUP_DIR/$BACKUP_FILE" \
        --exclude='*.pyc' \
        --exclude='__pycache__' \
        --exclude='.git' \
        --exclude='venv' \
        --exclude='*.log' \
        --exclude='db.sqlite3' \
        --exclude='media' \
        --exclude='staticfiles' \
        -C /opt/vpnbot .
    
    print_message "پشتیبان در $BACKUP_DIR/$BACKUP_FILE ایجاد شد"
    
    # کپی فایل‌های سرویس
    cp /etc/systemd/system/django.service "$BACKUP_DIR/"
    cp /etc/systemd/system/admin-bot.service "$BACKUP_DIR/"
    cp /etc/systemd/system/user-bot.service "$BACKUP_DIR/"
    cp /etc/systemd/system/vpnbot.target "$BACKUP_DIR/"
    
    print_message "فایل‌های سرویس نیز پشتیبان‌گیری شدند"
    
    read -p "برای ادامه Enter را فشار دهید..."
}

# بازگردانی تنظیمات
restore_config() {
    print_header "بازگردانی تنظیمات"
    
    BACKUP_DIR="/opt/vpnbot/backups"
    
    if [[ ! -d "$BACKUP_DIR" ]]; then
        print_error "دایرکتوری پشتیبان یافت نشد"
        return
    fi
    
    echo "فایل‌های پشتیبان موجود:"
    ls -la "$BACKUP_DIR"/*.tar.gz 2>/dev/null || echo "هیچ فایل پشتیبانی یافت نشد"
    echo
    
    read -p "نام فایل پشتیبان را وارد کنید: " backup_file
    
    if [[ ! -f "$BACKUP_DIR/$backup_file" ]]; then
        print_error "فایل پشتیبان یافت نشد"
        return
    fi
    
    print_warning "این عملیات تنظیمات فعلی را جایگزین می‌کند"
    read -p "آیا مطمئن هستید؟ (y/n): " -n 1 -r
    echo
    
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        print_message "بازگردانی تنظیمات..."
        
        # توقف سرویس‌ها
        systemctl stop user-bot.service
        systemctl stop admin-bot.service
        systemctl stop django.service
        
        # بازگردانی فایل‌ها
        tar -xzf "$BACKUP_DIR/$backup_file" -C /opt/vpnbot
        
        # بازگردانی فایل‌های سرویس
        if [[ -f "$BACKUP_DIR/django.service" ]]; then
            cp "$BACKUP_DIR/django.service" /etc/systemd/system/
        fi
        if [[ -f "$BACKUP_DIR/admin-bot.service" ]]; then
            cp "$BACKUP_DIR/admin-bot.service" /etc/systemd/system/
        fi
        if [[ -f "$BACKUP_DIR/user-bot.service" ]]; then
            cp "$BACKUP_DIR/user-bot.service" /etc/systemd/system/
        fi
        if [[ -f "$BACKUP_DIR/vpnbot.target" ]]; then
            cp "$BACKUP_DIR/vpnbot.target" /etc/systemd/system/
        fi
        
        # بارگذاری مجدد systemd
        systemctl daemon-reload
        
        # راه‌اندازی مجدد سرویس‌ها
        systemctl start django.service
        systemctl start admin-bot.service
        systemctl start user-bot.service
        
        print_message "تنظیمات با موفقیت بازگردانی شد"
    fi
    
    read -p "برای ادامه Enter را فشار دهید..."
}

# به‌روزرسانی سرویس‌ها
update_services() {
    print_header "به‌روزرسانی سرویس‌ها"
    
    print_message "توقف سرویس‌ها..."
    systemctl stop user-bot.service
    systemctl stop admin-bot.service
    systemctl stop django.service
    
    print_message "به‌روزرسانی فایل‌های سرویس..."
    
    # کپی فایل‌های جدید
    cp services/django.service /etc/systemd/system/
    cp services/admin-bot.service /etc/systemd/system/
    cp services/user-bot.service /etc/systemd/system/
    cp services/vpnbot.target /etc/systemd/system/
    
    # تنظیم مجوزها
    chmod 644 /etc/systemd/system/django.service
    chmod 644 /etc/systemd/system/admin-bot.service
    chmod 644 /etc/systemd/system/user-bot.service
    chmod 644 /etc/systemd/system/vpnbot.target
    
    # بارگذاری مجدد systemd
    systemctl daemon-reload
    
    print_message "راه‌اندازی مجدد سرویس‌ها..."
    systemctl start django.service
    systemctl start admin-bot.service
    systemctl start user-bot.service
    
    print_message "سرویس‌ها با موفقیت به‌روزرسانی شدند"
    
    read -p "برای ادامه Enter را فشار دهید..."
}

# تابع اصلی
main() {
    check_root
    
    while true; do
        show_menu
        
        case $choice in
            1)
                show_status
                ;;
            2)
                start_all_services
                ;;
            3)
                stop_all_services
                ;;
            4)
                restart_all_services
                ;;
            5)
                show_logs "django" "Django"
                ;;
            6)
                show_logs "admin-bot" "ربات ادمین"
                ;;
            7)
                show_logs "user-bot" "ربات کاربران"
                ;;
            8)
                manage_service "django" "Django"
                ;;
            9)
                manage_service "admin-bot" "ربات ادمین"
                ;;
            10)
                manage_service "user-bot" "ربات کاربران"
                ;;
            11)
                check_system_performance
                ;;
            12)
                backup_config
                ;;
            13)
                restore_config
                ;;
            14)
                update_services
                ;;
            0)
                print_message "خروج از برنامه"
                exit 0
                ;;
            *)
                print_error "گزینه نامعتبر"
                sleep 2
                ;;
        esac
    done
}

# اجرای تابع اصلی
main "$@" 