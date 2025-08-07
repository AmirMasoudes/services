#!/bin/bash

# اسکریپت استقرار خودکار سیستم VPN Bot
# این اسکریپت سیستم را روی سرور با Sanaei X-UI نصب می‌کند

set -e  # توقف در صورت بروز خطا

# رنگ‌ها برای نمایش بهتر
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# تابع نمایش پیام
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

# بررسی اینکه آیا root هستیم
check_root() {
    if [[ $EUID -eq 0 ]]; then
        print_error "این اسکریپت نباید با root اجرا شود!"
        exit 1
    fi
}

# بررسی پیش‌نیازها
check_prerequisites() {
    print_message "بررسی پیش‌نیازها..."
    
    # بررسی Python
    if ! command -v python3 &> /dev/null; then
        print_error "Python3 نصب نیست!"
        exit 1
    fi
    
    # بررسی pip
    if ! command -v pip3 &> /dev/null; then
        print_error "pip3 نصب نیست!"
        exit 1
    fi
    
    # بررسی git
    if ! command -v git &> /dev/null; then
        print_error "git نصب نیست!"
        exit 1
    fi
    
    print_success "پیش‌نیازها بررسی شدند"
}

# نصب وابستگی‌های سیستم
install_system_dependencies() {
    print_message "نصب وابستگی‌های سیستم..."
    
    sudo apt update
    sudo apt install -y python3-venv nginx supervisor ufw
    
    print_success "وابستگی‌های سیستم نصب شدند"
}

# تنظیم محیط مجازی
setup_virtual_environment() {
    print_message "تنظیم محیط مجازی..."
    
    if [ ! -d "venv" ]; then
        python3 -m venv venv
        print_success "محیط مجازی ایجاد شد"
    else
        print_warning "محیط مجازی قبلاً وجود دارد"
    fi
    
    source venv/bin/activate
    pip install --upgrade pip
    pip install -r requirements.txt
    pip install gunicorn
    
    print_success "محیط مجازی تنظیم شد"
}

# تنظیم فایل‌های محیطی
setup_environment() {
    print_message "تنظیم فایل‌های محیطی..."
    
    if [ ! -f "env_config.env" ]; then
        cp env.example env_config.env
        print_warning "فایل env_config.env ایجاد شد. لطفاً تنظیمات را ویرایش کنید."
        print_message "دستور: nano env_config.env"
    else
        print_warning "فایل env_config.env قبلاً وجود دارد"
    fi
    
    # تنظیم مجوزهای امنیتی
    chmod 600 env_config.env
    
    print_success "فایل‌های محیطی تنظیم شدند"
}

# تنظیم دیتابیس
setup_database() {
    print_message "تنظیم دیتابیس..."
    
    source venv/bin/activate
    
    # اجرای مایگریشن‌ها
    python manage.py migrate
    
    # جمع‌آوری فایل‌های استاتیک
    python manage.py collectstatic --noinput
    
    print_success "دیتابیس تنظیم شد"
}

# تست اتصال به X-UI
test_xui_connection() {
    print_message "تست اتصال به X-UI..."
    
    source venv/bin/activate
    
    if python test_sanaei_connection.py; then
        print_success "اتصال به X-UI موفق بود"
    else
        print_warning "اتصال به X-UI ناموفق بود. لطفاً تنظیمات را بررسی کنید."
    fi
}

# تنظیم Gunicorn
setup_gunicorn() {
    print_message "تنظیم Gunicorn..."
    
    cat > gunicorn.conf.py << 'EOF'
# gunicorn.conf.py
bind = "127.0.0.1:8000"
workers = 3
worker_class = "sync"
worker_connections = 1000
max_requests = 1000
max_requests_jitter = 50
timeout = 30
keepalive = 2
EOF
    
    print_success "Gunicorn تنظیم شد"
}

# تنظیم Supervisor
setup_supervisor() {
    print_message "تنظیم Supervisor..."
    
    # ایجاد فایل تنظیمات Django
    sudo tee /etc/supervisor/conf.d/django.conf > /dev/null << EOF
[program:django]
command=$(pwd)/venv/bin/gunicorn --config $(pwd)/gunicorn.conf.py config.wsgi:application
directory=$(pwd)
user=$USER
autostart=true
autorestart=true
redirect_stderr=true
stdout_logfile=/var/log/django.log
environment=DJANGO_SETTINGS_MODULE="config.settings"
EOF

    # ایجاد فایل تنظیمات Telegram Bot
    sudo tee /etc/supervisor/conf.d/telegram_bot.conf > /dev/null << EOF
[program:telegram_bot]
command=$(pwd)/venv/bin/python $(pwd)/bot/user_bot.py
directory=$(pwd)
user=$USER
autostart=true
autorestart=true
redirect_stderr=true
stdout_logfile=/var/log/telegram_bot.log
environment=DJANGO_SETTINGS_MODULE="config.settings"
EOF

    # راه‌اندازی Supervisor
    sudo supervisorctl reread
    sudo supervisorctl update
    
    print_success "Supervisor تنظیم شد"
}

# تنظیم Nginx
setup_nginx() {
    print_message "تنظیم Nginx..."
    
    # ایجاد فایل تنظیمات Nginx
    sudo tee /etc/nginx/sites-available/vpnbot > /dev/null << EOF
server {
    listen 80;
    server_name _;

    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto \$scheme;
    }

    location /static/ {
        alias $(pwd)/staticfiles/;
    }

    location /media/ {
        alias $(pwd)/media/;
    }
}
EOF

    # فعال‌سازی سایت
    sudo ln -sf /etc/nginx/sites-available/vpnbot /etc/nginx/sites-enabled/
    sudo nginx -t
    sudo systemctl restart nginx
    
    print_success "Nginx تنظیم شد"
}

# تنظیم فایروال
setup_firewall() {
    print_message "تنظیم فایروال..."
    
    sudo ufw default deny incoming
    sudo ufw default allow outgoing
    sudo ufw allow ssh
    sudo ufw allow 80
    sudo ufw allow 443
    sudo ufw --force enable
    
    print_success "فایروال تنظیم شد"
}

# راه‌اندازی سرویس‌ها
start_services() {
    print_message "راه‌اندازی سرویس‌ها..."
    
    sudo supervisorctl start django
    sudo supervisorctl start telegram_bot
    
    # بررسی وضعیت سرویس‌ها
    sleep 3
    sudo supervisorctl status
    
    print_success "سرویس‌ها راه‌اندازی شدند"
}

# نمایش اطلاعات نهایی
show_final_info() {
    echo
    echo "=========================================="
    echo "🎉 استقرار سیستم با موفقیت انجام شد!"
    echo "=========================================="
    echo
    echo "📋 اطلاعات مهم:"
    echo "   • آدرس وب: http://$(hostname -I | awk '{print $1}')"
    echo "   • مسیر پروژه: $(pwd)"
    echo "   • محیط مجازی: $(pwd)/venv"
    echo
    echo "🔧 دستورات مفید:"
    echo "   • بررسی وضعیت: sudo supervisorctl status"
    echo "   • راه‌اندازی مجدد: sudo supervisorctl restart django"
    echo "   • مشاهده لاگ‌ها: sudo tail -f /var/log/django.log"
    echo "   • دسترسی به Django: source venv/bin/activate && python manage.py shell"
    echo
    echo "⚠️ نکات مهم:"
    echo "   1. حتماً فایل env_config.env را ویرایش کنید"
    echo "   2. کاربر ادمین Django ایجاد کنید: python manage.py createsuperuser"
    echo "   3. تنظیمات X-UI را بررسی کنید"
    echo "   4. از سیستم پشتیبان تهیه کنید"
    echo
    echo "📚 مستندات:"
    echo "   • راهنمای کامل: DEPLOYMENT_GUIDE.md"
    echo "   • راهنمای X-UI: Sanaei_XUI_Setup_Guide.md"
    echo
}

# تابع اصلی
main() {
    echo "🚀 شروع استقرار سیستم VPN Bot..."
    echo
    
    check_root
    check_prerequisites
    install_system_dependencies
    setup_virtual_environment
    setup_environment
    setup_database
    test_xui_connection
    setup_gunicorn
    setup_supervisor
    setup_nginx
    setup_firewall
    start_services
    show_final_info
}

# اجرای تابع اصلی
main "$@"
