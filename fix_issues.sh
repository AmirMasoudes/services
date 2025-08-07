#!/bin/bash

# اسکریپت حل مشکلات سیستم
echo "🔧 حل مشکلات سیستم..."

# 1. ایجاد پوشه staticfiles اگر وجود ندارد
echo "📁 بررسی پوشه staticfiles..."
if [ ! -d "staticfiles" ]; then
    mkdir -p staticfiles
    echo "✅ پوشه staticfiles ایجاد شد"
else
    echo "✅ پوشه staticfiles قبلاً وجود دارد"
fi

# 2. ایجاد پوشه media اگر وجود ندارد
echo "📁 بررسی پوشه media..."
if [ ! -d "media" ]; then
    mkdir -p media
    echo "✅ پوشه media ایجاد شد"
else
    echo "✅ پوشه media قبلاً وجود دارد"
fi

# 3. ایجاد پوشه logs اگر وجود ندارد
echo "📁 بررسی پوشه logs..."
if [ ! -d "logs" ]; then
    mkdir -p logs
    echo "✅ پوشه logs ایجاد شد"
else
    echo "✅ پوشه logs قبلاً وجود دارد"
fi

# 4. بررسی فایل manage.py
echo "📄 بررسی فایل manage.py..."
if [ -f "manage.py" ]; then
    echo "✅ فایل manage.py موجود است"
else
    echo "❌ فایل manage.py موجود نیست"
fi

# 5. تست Django
echo "🧪 تست Django..."
python manage.py check --deploy

# 6. اجرای مایگریشن‌ها
echo "🗄️ اجرای مایگریشن‌ها..."
python manage.py migrate

# 7. جمع‌آوری فایل‌های استاتیک
echo "📦 جمع‌آوری فایل‌های استاتیک..."
python manage.py collectstatic --noinput

echo "✅ تمام مشکلات حل شدند!"
