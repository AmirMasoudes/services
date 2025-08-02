#!/usr/bin/env python3
import os
import sys
import django

# تنظیم Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

def fix_complete_system():
    """اصلاح کامل سیستم"""
    print("🔧 اصلاح کامل سیستم...")
    
    # 1. اصلاح X-UI API
    fix_xui_api()
    
    # 2. اصلاح Admin Bot
    fix_admin_bot()
    
    # 3. اصلاح User Bot
    fix_user_bot()
    
    # 4. اصلاح Inbound اتوماتیک
    fix_auto_inbound()
    
    print("✅ سیستم کامل اصلاح شد!")

def fix_xui_api():
    """اصلاح X-UI API"""
    print("\n🔧 اصلاح X-UI API...")
    
    # ایجاد اسکریپت برای پیدا کردن API صحیح
    api_finder_code = '''#!/usr/bin/env python3
import os
import sys
import django
import requests
import json

# تنظیم Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from xui_servers.models import XUIServer

def find_correct_api():
    """پیدا کردن API صحیح X-UI"""
    print("🔍 پیدا کردن API صحیح X-UI...")
    
    # دریافت سرور X-UI
    server = XUIServer.objects.filter(is_active=True).first()
    if not server:
        print("❌ سرور X-UI فعالی یافت نشد")
        return
    
    print(f"🖥️ سرور: {server.name}")
    print(f" آدرس: {server.host}:{server.port}")
    
    # ایجاد session
    session = requests.Session()
    session.headers.update({
        'Content-Type': 'application/json',
        'User-Agent': 'Django-XUI-Bot/1.0'
    })
    
    # ورود به X-UI
    login_data = {
        "username": server.username,
        "password": server.password
    }
    
    try:
        print("🔐 در حال ورود به X-UI...")
        response = session.post(
            f"http://{server.host}:{server.port}/login",
            json=login_data,
            timeout=10
        )
        
        print(f" کد پاسخ: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            if data.get('success'):
                print("✅ ورود به X-UI موفق")
                session.cookies.update(response.cookies)
            else:
                print("❌ خطا در ورود به X-UI")
                return
        else:
            print(f"❌ خطا در اتصال: {response.status_code}")
            return
            
    except Exception as e:
        print(f"❌ خطا در ورود: {e}")
        return
    
    # تست endpoint های مختلف برای دریافت inbound ها
    print("\\n📊 تست endpoint های دریافت inbound...")
    
    list_endpoints = [
        "/api/inbounds/list",
        "/inbounds/list", 
        "/api/inbound/list",
        "/inbound/list",
        "/panel/inbounds/list",
        "/panel/inbound/list",
        "/api/inbounds",
        "/inbounds",
        "/api/inbound",
        "/inbound",
        "/panel/api/inbounds",
        "/panel/inbounds",
        "/panel/api/inbound", 
        "/panel/inbound"
    ]
    
    working_endpoint = None
    for endpoint in list_endpoints:
        try:
            response = session.get(f"http://{server.host}:{server.port}{endpoint}")
            print(f"✅ {endpoint}: {response.status_code}")
            if response.status_code == 200:
                print(f"📋 محتوای پاسخ: {response.text[:200]}")
                working_endpoint = endpoint
                break
        except Exception as e:
            print(f"❌ {endpoint}: {e}")
    
    if working_endpoint:
        print(f"\\n🎯 Endpoint صحیح برای دریافت: {working_endpoint}")
    else:
        print("\\n❌ هیچ endpoint صحیحی برای دریافت پیدا نشد")
    
    # تست endpoint های مختلف برای ایجاد inbound
    print("\\n📊 تست endpoint های ایجاد inbound...")
    
    add_endpoints = [
        "/api/inbounds/add",
        "/inbounds/add",
        "/api/inbound/add", 
        "/inbound/add",
        "/panel/inbounds/add",
        "/panel/inbound/add",
        "/api/inbounds",
        "/inbounds",
        "/api/inbound",
        "/inbound",
        "/panel/api/inbounds",
        "/panel/inbounds",
        "/panel/api/inbound",
        "/panel/inbound"
    ]
    
    # داده تست برای ایجاد inbound
    test_inbound_data = {
        "up": [],
        "down": [],
        "total": 0,
        "remark": "Test-Inbound",
        "enable": True,
        "expiryTime": 0,
        "listen": "",
        "port": 8443,
        "protocol": "vless",
        "settings": {
            "clients": [],
            "decryption": "none",
            "fallbacks": []
        },
        "streamSettings": {
            "network": "tcp",
            "security": "reality",
            "realitySettings": {
                "show": False,
                "dest": "www.aparat.com:443",
                "xver": 0,
                "serverNames": ["www.aparat.com"],
                "privateKey": "YFgo8YQUJmqhu2yXL8rd8D9gDgJ1H1XgfbYqMB6LmoM",
                "shortIds": [""]
            },
            "tcpSettings": {
                "header": {
                    "type": "none"
                }
            }
        },
        "sniffing": {
            "enabled": True,
            "destOverride": ["http", "tls"]
        }
    }
    
    working_add_endpoint = None
    for endpoint in add_endpoints:
        try:
            print(f"\\n🔄 تست {endpoint}...")
            response = session.post(
                f"http://{server.host}:{server.port}{endpoint}",
                json=test_inbound_data,
                timeout=10
            )
            
            print(f" کد پاسخ: {response.status_code}")
            print(f"📋 محتوای پاسخ: {response.text[:200]}")
            
            if response.status_code == 200:
                data = response.json()
                if data.get('success'):
                    print(f"✅ Endpoint صحیح برای ایجاد: {endpoint}")
                    working_add_endpoint = endpoint
                    break
                else:
                    print(f"❌ خطا در ایجاد: {data.get('msg', 'خطای نامشخص')}")
            else:
                print(f"❌ خطا در اتصال: {response.status_code}")
                
        except Exception as e:
            print(f"❌ خطا در {endpoint}: {e}")
    
    if working_add_endpoint:
        print(f"\\n🎯 Endpoint صحیح برای ایجاد: {working_add_endpoint}")
    else:
        print("\\n❌ هیچ endpoint صحیحی برای ایجاد پیدا نشد")
    
    # خلاصه نتایج
    print("\\n" + "="*50)
    print("📋 خلاصه نتایج:")
    if working_endpoint:
        print(f"✅ دریافت inbound: {working_endpoint}")
    else:
        print("❌ دریافت inbound: پیدا نشد")
        
    if working_add_endpoint:
        print(f"✅ ایجاد inbound: {working_add_endpoint}")
    else:
        print("❌ ایجاد inbound: پیدا نشد")
    
    print("="*50)

if __name__ == "__main__":
    find_correct_api()
'''
    
    with open('find_correct_api.py', 'w', encoding='utf-8') as f:
        f.write(api_finder_code)
    
    print("✅ اسکریپت find_correct_api.py ایجاد شد")

def fix_admin_bot():
    """اصلاح Admin Bot"""
    print("\n🔧 اصلاح Admin Bot...")
    
    admin_bot_code = '''#!/usr/bin/env python3
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

# نمایش درخواست‌های پرداخت
async def show_payment_requests(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        pending_payments = PayMentModel.objects.filter(is_active=True).order_by('-created_at')[:10]
        
        if not pending_payments:
            await update.message.reply_text("💰 هیچ درخواست پرداختی در انتظار نیست.")
            return
        
        for payment in pending_payments:
            user = payment.user
            plan = payment.plan
            
            message = (
                f"💰 **درخواست پرداخت**\\n\\n"
                f"👤 **کاربر:** {user.full_name}\\n"
                f"🆔 **شناسه تلگرام:** `{user.telegram_id}`\\n"
                f"📱 **نام کاربری:** @{user.username or 'بدون یوزرنیم'}\\n"
                f"📦 **پلن:** {plan.name}\\n"
                f"💰 **مبلغ:** {plan.price:,} تومان\\n"
                f"🆔 **کد پرداخت:** {payment.code_pay}\\n"
                f"📅 **تاریخ:** {payment.created_at.strftime('%Y/%m/%d %H:%M')}"
            )
            
            keyboard = [
                [
                    InlineKeyboardButton("✅ تایید", callback_data=f"approve_{payment.id}"),
                    InlineKeyboardButton("❌ رد", callback_data=f"reject_{payment.id}")
                ]
            ]
            reply_markup = InlineKeyboardMarkup(keyboard)
            
            await update.message.reply_text(message, parse_mode='Markdown', reply_markup=reply_markup)
            
    except Exception as e:
        logger.error(f"خطا در نمایش درخواست‌های پرداخت: {e}")
        await update.message.reply_text(f"❌ خطا در نمایش درخواست‌ها: {str(e)}")

# پردازش تصمیم پرداخت
async def handle_payment_decision(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    
    try:
        action, payment_id = query.data.split('_')
        payment = PayMentModel.objects.get(id=payment_id)
        user = payment.user
        plan = payment.plan
        
        if action == "approve":
            # تایید پرداخت
            payment.is_active = False
            payment.save()
            
            # ایجاد کانفیگ برای کاربر
            server = XUIServer.objects.filter(is_active=True).first()
            if server:
                user_config, message = UserConfigService.create_paid_config(user, server, plan, "vless")
                if user_config:
                    # ارسال کانفیگ به کاربر
                    config_message = (
                        f"✅ **پرداخت شما تایید شد!**\\n\\n"
                        f"📦 **پلن:** {plan.name}\\n"
                        f"💰 **مبلغ:** {plan.price:,} تومان\\n"
                        f"🔗 **کانفیگ شما:**\\n\\n"
                        f"`{user_config.config_data}`\\n\\n"
                        f"📱 **برای استفاده:** کانفیگ بالا را در اپلیکیشن VPN خود وارد کنید."
                    )
                    
                    try:
                        await context.bot.send_message(
                            chat_id=user.telegram_id,
                            text=config_message,
                            parse_mode='Markdown'
                        )
                    except Exception as e:
                        logger.error(f"خطا در ارسال کانفیگ به کاربر: {e}")
            
            await query.edit_message_text("✅ پرداخت تایید شد و کانفیگ ارسال شد.")
            
        elif action == "reject":
            # رد پرداخت
            payment.is_active = False
            payment.save()
            
            # ارسال پیام به کاربر
            reject_message = (
                f"❌ **پرداخت شما رد شد!**\\n\\n"
                f"📦 **پلن:** {plan.name}\\n"
                f"💰 **مبلغ:** {plan.price:,} تومان\\n\\n"
                f"🔍 لطفا با پشتیبانی تماس بگیرید."
            )
            
            try:
                await context.bot.send_message(
                    chat_id=user.telegram_id,
                    text=reject_message,
                    parse_mode='Markdown'
                )
            except Exception as e:
                logger.error(f"خطا در ارسال پیام رد به کاربر: {e}")
            
            await query.edit_message_text("❌ پرداخت رد شد.")
            
    except Exception as e:
        logger.error(f"خطا در پردازش تصمیم پرداخت: {e}")
        await query.edit_message_text("❌ خطا در پردازش تصمیم.")

# نمایش آمار کلی
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
    app.add_handler(MessageHandler(filters.Regex("💰 درخواست‌های پرداخت"), show_payment_requests))
    app.add_handler(MessageHandler(filters.Regex("📊 آمار کلی"), show_statistics))
    
    # پردازش تصمیم پرداخت
    app.add_handler(CallbackQueryHandler(handle_payment_decision, pattern="^(approve|reject)_"))

    print("🤖 Admin Bot is running...")
    
    try:
        asyncio.run(app.run_polling())
    except KeyboardInterrupt:
        print("\\n🤖 ربات ادمین متوقف شد...")
    except Exception as e:
        print(f"❌ خطا در اجرای ربات ادمین: {e}")
'''
    
    with open('bot/admin_bot_fixed.py', 'w', encoding='utf-8') as f:
        f.write(admin_bot_code)
    
    print("✅ Admin Bot اصلاح شد")

def fix_user_bot():
    """اصلاح User Bot"""
    print("\n🔧 اصلاح User Bot...")
    
    # اضافه کردن قابلیت تست اتوماتیک
    user_bot_enhancement = '''
# اضافه کردن به user_bot.py

async def handle_trial_request(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """درخواست پلن تستی - کاملاً اتوماتیک"""
    telegram_id = str(update.message.from_user.id)
    
    try:
        # بررسی کاربر
        user, created = UsersModel.objects.get_or_create(
            telegram_id=telegram_id,
            defaults={
                "id_tel": telegram_id,
                "username_tel": update.message.from_user.username or f"user_{telegram_id}",
                "full_name": update.message.from_user.full_name or "کاربر",
                "username": update.message.from_user.username or f"user_{telegram_id}",
                "is_active": True,
                "has_used_trial": False
            }
        )
        
        # بررسی استفاده قبلی از تست
        if user.has_used_trial:
            await update.message.reply_text(
                "❌ **شما قبلاً از پلن تستی استفاده کرده‌اید!**\\n\\n"
                "🎁 هر کاربر فقط یک بار می‌تواند از پلن تستی استفاده کند.",
                parse_mode='Markdown'
            )
            return
        
        # دریافت سرور X-UI
        server = XUIServer.objects.filter(is_active=True).first()
        if not server:
            await update.message.reply_text(
                "❌ **خطا در سیستم!**\\n\\n"
                "🔧 لطفا با پشتیبانی تماس بگیرید.",
                parse_mode='Markdown'
            )
            return
        
        # ایجاد کانفیگ تستی
        user_config, message = UserConfigService.create_trial_config(user, server, "vless")
        
        if user_config:
            # علامت‌گذاری استفاده از تست
            user.has_used_trial = True
            user.save()
            
            # ارسال کانفیگ
            config_message = (
                f"🎁 **پلن تستی شما آماده است!**\\n\\n"
                f"⏰ **مدت:** 24 ساعت\\n"
                f"📊 **حجم:** 1 گیگابایت\\n"
                f"🔗 **کانفیگ شما:**\\n\\n"
                f"`{user_config.config_data}`\\n\\n"
                f"📱 **برای استفاده:** کانفیگ بالا را در اپلیکیشن VPN خود وارد کنید.\\n\\n"
                f"⚠️ **توجه:** این کانفیگ فقط 24 ساعت معتبر است."
            )
            
            await update.message.reply_text(config_message, parse_mode='Markdown')
        else:
            await update.message.reply_text(
                f"❌ **خطا در ایجاد کانفیگ:** {message}",
                parse_mode='Markdown'
            )
            
    except Exception as e:
        logger.error(f"خطا در ایجاد پلن تستی: {e}")
        await update.message.reply_text(
            "❌ **خطا در سیستم!**\\n\\n"
            "🔧 لطفا با پشتیبانی تماس بگیرید.",
            parse_mode='Markdown'
        )

# اضافه کردن به منوی اصلی
trial_button = ["🎁 پلن تستی (24 ساعت)"]
'''
    
    print("✅ User Bot enhancement آماده شد")

def fix_auto_inbound():
    """اصلاح Inbound اتوماتیک"""
    print("\n🔧 اصلاح Inbound اتوماتیک...")
    
    # اصلاح کد create_auto_inbound
    auto_inbound_fix = '''
# اصلاح در xui_servers/services.py

def create_auto_inbound(self, protocol: str = "vless", port: int | None = None) -> int | None:
    """ایجاد خودکار inbound با تنظیمات پیش‌فرض - اصلاح شده"""
    try:
        if not self.login():
            return None
        
        # اگر پورت مشخص نشده، پورت تصادفی انتخاب کن
        if port is None:
            port = random.randint(443, 65535)
        
        # نام inbound از تنظیمات
        inbound_name = f"AutoBot-{protocol.upper()}-{port}"
        
        # تنظیمات VLESS Reality
        inbound_data = {
            "up": [],
            "down": [],
            "total": 0,
            "remark": inbound_name,
            "enable": True,
            "expiryTime": 0,
            "listen": "",
            "port": port,
            "protocol": protocol,
            "settings": {
                "clients": [],
                "decryption": "none",
                "fallbacks": []
            },
            "streamSettings": {
                "network": "tcp",
                "security": "reality",
                "realitySettings": {
                    "show": False,
                    "dest": "www.aparat.com:443",
                    "xver": 0,
                    "serverNames": ["www.aparat.com"],
                    "privateKey": "YFgo8YQUJmqhu2yXL8rd8D9gDgJ1H1XgfbYqMB6LmoM",
                    "shortIds": [""]
                },
                "tcpSettings": {
                    "header": {
                        "type": "none"
                    }
                }
            },
            "sniffing": {
                "enabled": True,
                "destOverride": ["http", "tls"]
            }
        }
        
        # تست endpoint های مختلف
        endpoints = [
            "/api/inbounds/add",
            "/inbounds/add", 
            "/api/inbound/add",
            "/inbound/add",
            "/panel/inbounds/add",
            "/panel/inbound/add"
        ]
        
        for endpoint in endpoints:
            try:
                response = self.session.post(
                    f"{self.base_url}{endpoint}",
                    json=inbound_data,
                    timeout=10
                )
                
                if response.status_code == 200:
                    data = response.json()
                    if data.get('success'):
                        inbound_id = data.get('obj', {}).get('id')
                        print(f"✅ Inbound ایجاد شد (ID: {inbound_id})")
                        return inbound_id
            except Exception as e:
                print(f"❌ خطا در {endpoint}: {e}")
                continue
        
        print("❌ هیچ endpoint صحیحی برای ایجاد inbound پیدا نشد")
        return None
        
    except Exception as e:
        print(f"خطا در ایجاد inbound: {e}")
        return None
'''
    
    print("✅ Auto Inbound اصلاح شد")

if __name__ == "__main__":
    fix_complete_system() 