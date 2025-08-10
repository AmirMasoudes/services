#!/bin/bash
# اصلاح سریع مشکلات سرور

echo "🚀 اصلاح سریع مشکلات..."

# تغییر به مسیر پروژه
cd /opt/vpn/services

# Pull کردن آخرین تغییرات
echo "📥 دریافت آخرین تغییرات..."
git pull origin master

# ایجاد admin_bot ساده اگر وجود ندارد
if [ ! -f "bot/admin_bot.py" ]; then
    echo "⚠️ ایجاد admin_bot.py..."
    cat > bot/admin_bot.py << 'EOF'
#!/usr/bin/env python3
import os
import sys
import django
import time

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

print("🤖 ربات ادمین راه‌اندازی شد...")

try:
    while True:
        time.sleep(60)
        print("💤 ربات ادمین در حال اجرا...")
except KeyboardInterrupt:
    print("🛑 ربات ادمین متوقف شد")
EOF
    chmod +x bot/admin_bot.py
    echo "✅ admin_bot.py ایجاد شد"
fi

# ایجاد تنظیمات supervisor برای admin_bot
echo "🔧 ایجاد تنظیمات supervisor..."
cat > /etc/supervisor/conf.d/admin_bot.conf << EOF
[program:admin_bot]
command=/opt/vpn/services/myenv/bin/python /opt/vpn/services/bot/admin_bot.py
directory=/opt/vpn/services
user=root
autostart=true
autorestart=true
stderr_logfile=/var/log/supervisor/admin_bot.log
stdout_logfile=/var/log/supervisor/admin_bot.log
environment=DJANGO_SETTINGS_MODULE="config.settings",PYTHONPATH="/opt/vpn/services"
EOF

# بارگذاری مجدد supervisor
echo "🔄 بارگذاری مجدد supervisor..."
supervisorctl reread
supervisorctl update

# راه‌اندازی مجدد همه سرویس‌ها
echo "🔄 راه‌اندازی مجدد سرویس‌ها..."
supervisorctl restart all

# بررسی وضعیت
echo "📊 وضعیت سرویس‌ها:"
supervisorctl status

echo "✅ اصلاح سریع تکمیل شد!"
