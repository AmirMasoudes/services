#!/bin/bash

# اسکریپت تنظیم سریع محیط
echo "🔧 تنظیم فایل محیطی..."

# کپی کردن فایل تنظیمات ساده
cp env_config_simple.env env_config.env

echo "✅ فایل env_config.env ایجاد شد"
echo ""
echo "📝 لطفاً موارد زیر را در فایل env_config.env تنظیم کنید:"
echo ""
echo "1. TELEGRAM_BOT_TOKEN=your_telegram_bot_token_here"
echo "2. TELEGRAM_ADMIN_ID=your_admin_telegram_id_here"
echo "3. XUI_DEFAULT_PASSWORD=your_sanaei_password_here"
echo ""
echo "برای ویرایش فایل:"
echo "nano env_config.env"
echo ""
echo "بعد از تنظیم، می‌توانید اسکریپت استقرار را اجرا کنید:"
echo "./deploy.sh"
