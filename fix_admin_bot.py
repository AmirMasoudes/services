#!/usr/bin/env python3
import os
import sys
import django

# تنظیم Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from bot.admin_boy import *

def fix_admin_bot():
    """اصلاح Admin Bot"""
    print("🔧 اصلاح Admin Bot...")
    
    # بررسی توکن
    token = os.getenv('ADMIN_BOT_TOKEN')
    if not token or token == 'YOUR_ADMIN_BOT_TOKEN_HERE':
        print("❌ توکن Admin Bot تنظیم نشده!")
        print("در فایل .env این خط را اضافه کنید:")
        print("ADMIN_BOT_TOKEN=8450508816:AAFE6XAj8QvA9iIP12whrKxYRtgsoHFCiFU")
        return False
    
    print(f"✅ توکن Admin Bot: {token[:20]}...")
    
    # بررسی رمز ادمین
    admin_password = os.getenv('ADMIN_PASSWORD', 'admin123')
    print(f"✅ رمز ادمین: {admin_password}")
    
    # تست اتصال به تلگرام
    try:
        import requests
        response = requests.get(f'https://api.telegram.org/bot{token}/getMe')
        if response.status_code == 200:
            data = response.json()
            if data.get('ok'):
                bot_info = data['result']
                print(f"✅ اتصال به تلگرام موفق")
                print(f"🤖 نام ربات: {bot_info.get('first_name', 'Unknown')}")
                print(f"👤 نام کاربری: @{bot_info.get('username', 'Unknown')}")
                return True
            else:
                print(f"❌ خطا در تلگرام: {data.get('description', 'Unknown error')}")
                return False
        else:
            print(f"❌ خطا در اتصال: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ خطا در تست اتصال: {e}")
        return False

def create_fixed_admin_bot():
    """ایجاد نسخه اصلاح شده Admin Bot"""
    print("\n🔧 ایجاد نسخه اصلاح شده Admin Bot...")
    
    fixed_code = '''#!/usr/bin/env python3
import os
import django
import logging
import sys
import asyncio
from dotenv import load_dotenv

from telegram import Update, ReplyKeyboardMarkup, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes, MessageHandler, CallbackQueryHandler, filters

# اضافه کردن مسیر پروژه به sys.path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Load environment variables
load_dotenv()

# Django setup
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")
django.setup()

from accounts.models import UsersModel
from plan.models import ConfingPlansModel
from order.models import OrderUserModel, PayMentModel
from conf.models import TrialConfigModel
from xui_servers.models import XUIServer, UserConfig
from xui_servers.services import XUIService, UserConfigService

# Logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# فقط یک رمز برای ورود ادمین
ADMIN_PASSWORD = os.getenv('ADMIN_PASSWORD', 'admin123')
ADMINS = set()

# حالت‌های مختلف ادمین
ADMIN_STATES = {}

# ورود ادمین
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("سلام. لطفا رمز عبور ادمین را وارد کنید:")

async def auth_admin(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.from_user.id
    password = update.message.text
    
    if password == ADMIN_PASSWORD:
        ADMINS.add(user_id)
        await show_admin_panel(update)
    else:
        await update.message.reply_text("❌ رمز عبور اشتباه است!")

async def show_admin_panel(update: Update):
    keyboard = [
        ["👥 لیست کاربران", "📦 لیست پلن‌ها"],
        ["➕ افزودن پلن", "💰 درخواست‌های پرداخت"],
        ["📨 ارسال پیام به کاربران", "📊 آمار کلی"],
        ["🎁 مدیریت پلن‌های تستی", "🖥️ مدیریت سرورهای X-UI"]
    ]
    reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
    await update.message.reply_text("🔐 **پنل ادمین**", reply_markup=reply_markup, parse_mode='Markdown')

# نمایش آمار کلی - بهبود شده
async def show_statistics(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        total_users = UsersModel.objects.count()
        active_users = UsersModel.objects.filter(is_active=True).count()
        active_orders = OrderUserModel.objects.filter(is_active=True).count()
        pending_payments = PayMentModel.objects.filter(is_active=True).count()
        total_plans = ConfingPlansModel.objects.filter(is_deleted=False).count()
        users_with_trial = UsersModel.objects.filter(has_used_trial=True).count()
        active_trials = TrialConfigModel.objects.filter(is_active=True).count()
        active_xui_configs = UserConfig.objects.filter(is_active=True).count()
        total_servers = XUIServer.objects.count()
        active_servers = XUIServer.objects.filter(is_active=True).count()
        
        stats = (
            f"📊 **آمار کلی:**\\n\\n"
            f"👥 **کل کاربران:** {total_users}\\n"
            f"🟢 **کاربران فعال:** {active_users}\\n"
            f"📦 **پلن‌های فعال:** {active_orders}\\n"
            f"💰 **درخواست‌های در انتظار:** {pending_payments}\\n"
            f"📋 **تعداد پلن‌ها:** {total_plans}\\n"
            f"🎁 **استفاده از پلن تستی:** {users_with_trial}\\n"
            f"✅ **کانفیگ‌های تستی فعال:** {active_trials}\\n"
            f"🔧 **کانفیگ‌های X-UI فعال:** {active_xui_configs}\\n"
            f"🖥️ **کل سرورها:** {total_servers}\\n"
            f"🟢 **سرورهای فعال:** {active_servers}"
        )
        
        await update.message.reply_text(stats, parse_mode='Markdown')
        
    except Exception as e:
        logger.error(f"خطا در دریافت آمار: {e}")
        await update.message.reply_text(f"❌ خطا در دریافت آمار: {str(e)}")

# راه‌اندازی برنامه
if __name__ == "__main__":
    TOKEN = os.getenv('ADMIN_BOT_TOKEN', 'YOUR_ADMIN_BOT_TOKEN_HERE')
    
    if TOKEN == 'YOUR_ADMIN_BOT_TOKEN_HERE':
        print("❌ لطفا توکن ربات ادمین را در فایل .env تنظیم کنید!")
        print("مثال: ADMIN_BOT_TOKEN=your_admin_bot_token_here")
        exit()

    app = ApplicationBuilder().token(TOKEN).build()

    # دستورات اصلی
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & (~filters.COMMAND), auth_admin))

    # دکمه‌های منو
    app.add_handler(MessageHandler(filters.Regex("📊 آمار کلی"), show_statistics))

    print("🤖 Admin Bot is running...")
    
    try:
        asyncio.run(app.run_polling())
    except KeyboardInterrupt:
        print("\\n🤖 ربات ادمین متوقف شد...")
    except Exception as e:
        print(f"❌ خطا در اجرای ربات ادمین: {e}")
'''
    
    with open('bot/admin_bot_fixed.py', 'w', encoding='utf-8') as f:
        f.write(fixed_code)
    
    print("✅ فایل admin_bot_fixed.py ایجاد شد")

if __name__ == "__main__":
    if fix_admin_bot():
        create_fixed_admin_bot()
        print("\n✅ Admin Bot اصلاح شد!")
        print("برای تست:")
        print("python bot/admin_bot_fixed.py")
    else:
        print("\n❌ Admin Bot اصلاح نشد!") 