# bot_admin.py

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
    text = update.message.text

    if user_id in ADMINS:
        await show_admin_panel(update)
        return

    if text == ADMIN_PASSWORD:
        ADMINS.add(user_id)
        await update.message.reply_text("✅ ورود با موفقیت انجام شد.")
        await show_admin_panel(update)
    else:
        await update.message.reply_text("❌ رمز اشتباه است.")

# منوی اصلی ادمین
async def show_admin_panel(update: Update):
    keyboard = [
        ["👥 لیست کاربران", "📦 لیست پلن‌ها"],
        ["➕ افزودن پلن", "💰 درخواست‌های پرداخت"],
        ["📨 ارسال پیام به کاربران", "📊 آمار کلی"],
        ["🎁 مدیریت پلن‌های تستی", "🖥️ مدیریت سرورهای X-UI"]
    ]
    markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
    await update.message.reply_text("پنل ادمین:", reply_markup=markup)

# مدیریت سرورهای X-UI - جدید
async def manage_xui_servers(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        servers = XUIServer.objects.all().order_by('-created_at')
        
        if not servers.exists():
            await update.message.reply_text(
                "❌ **هیچ سرور X-UI یافت نشد.**\n\n"
                "برای اضافه کردن سرور، گزینه '➕ افزودن سرور X-UI' را انتخاب کنید.",
                parse_mode='Markdown'
            )
            return
        
        msg = "🖥️ **سرورهای X-UI:**\n\n"
        
        for server in servers:
            status = "🟢 فعال" if server.is_active else "🔴 غیرفعال"
            msg += (
                f"🖥️ **{server.name}**\n"
                f"📍 آدرس: `{server.host}:{server.port}`\n"
                f"👤 نام کاربری: {server.username}\n"
                f"🔸 وضعیت: {status}\n"
                f"📅 ایجاد: {server.created_at.strftime('%Y/%m/%d')}\n\n"
            )
        
        await update.message.reply_text(msg, parse_mode='Markdown')
        
    except Exception as e:
        logger.error(f"خطا در مدیریت سرورهای X-UI: {e}")
        await update.message.reply_text(f"❌ خطا در مدیریت سرورهای X-UI: {str(e)}")

# افزودن سرور X-UI - جدید
async def add_xui_server(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.from_user.id
    ADMIN_STATES[user_id] = "WAITING_XUI_SERVER_INFO"
    
    await update.message.reply_text(
        "🖥️ **افزودن سرور X-UI جدید**\n\n"
        "اطلاعات سرور را به صورت زیر وارد کنید:\n\n"
        "**فرمت:** نام,آدرس,پورت,نام‌کاربری,رمزعبور\n\n"
        "**مثال:**\n"
        "`سرور اصلی,192.168.1.100,54321,admin,password123`\n\n"
        "⚠️ **نکات مهم:**\n"
        "• آدرس سرور باید قابل دسترس باشد\n"
        "• پورت پیش‌فرض X-UI: 54321\n"
        "• نام کاربری و رمز عبور X-UI را وارد کنید",
        parse_mode='Markdown'
    )

# پردازش اطلاعات سرور X-UI - جدید
async def handle_xui_server_input(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.from_user.id
    
    if user_id not in ADMINS:
        return
    
    if ADMIN_STATES.get(user_id) == "WAITING_XUI_SERVER_INFO":
        try:
            name, host, port, username, password = update.message.text.split(",")
            
            server = XUIServer.objects.create(
                name=name.strip(),
                host=host.strip(),
                port=int(port.strip()),
                username=username.strip(),
                password=password.strip(),
                is_active=True
            )
            
            del ADMIN_STATES[user_id]
            
            # تست اتصال
            xui_service = XUIService(server)
            connection_status = "✅ متصل" if xui_service.login() else "❌ خطا در اتصال"
            
            await update.message.reply_text(
                f"✅ **سرور X-UI با موفقیت اضافه شد!**\n\n"
                f"🖥️ نام: {server.name}\n"
                f"📍 آدرس: {server.host}:{server.port}\n"
                f"👤 نام کاربری: {server.username}\n"
                f"🔸 وضعیت اتصال: {connection_status}",
                parse_mode='Markdown'
            )
            
        except Exception as e:
            logger.error(f"خطا در افزودن سرور X-UI: {e}")
            await update.message.reply_text(f"❌ خطا در افزودن سرور: {str(e)}")
        return

# تست اتصال سرورهای X-UI - جدید
async def test_xui_connections(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        servers = XUIServer.objects.filter(is_active=True)
        
        if not servers.exists():
            await update.message.reply_text("❌ هیچ سرور فعالی یافت نشد.")
            return
        
        msg = "🔍 **تست اتصال سرورهای X-UI:**\n\n"
        
        for server in servers:
            try:
                xui_service = XUIService(server)
                
                if xui_service.login():
                    inbounds = xui_service.get_inbounds()
                    inbound_count = len(inbounds) if inbounds else 0
                    
                    msg += (
                        f"✅ **{server.name}**\n"
                        f"📍 {server.host}:{server.port}\n"
                        f"📋 تعداد inbound: {inbound_count}\n\n"
                    )
                else:
                    msg += (
                        f"❌ **{server.name}**\n"
                        f"📍 {server.host}:{server.port}\n"
                        f"🔸 خطا در ورود\n\n"
                    )
                    
            except Exception as e:
                msg += (
                    f"❌ **{server.name}**\n"
                    f"📍 {server.host}:{server.port}\n"
                    f"🔸 خطا: {str(e)}\n\n"
                )
        
        await update.message.reply_text(msg, parse_mode='Markdown')
        
    except Exception as e:
        logger.error(f"خطا در تست اتصال: {e}")
        await update.message.reply_text(f"❌ خطا در تست اتصال: {str(e)}")

# نمایش لیست کاربران - بهبود شده
async def list_users(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        users = UsersModel.objects.all().order_by('-created_at')
        if not users:
            await update.message.reply_text("هیچ کاربری ثبت‌نام نکرده است.")
            return
        
        msg = "👥 **کاربران:**\n\n"
        for user in users:
            status = '🟢 فعال' if user.is_active else '🔴 غیرفعال'
            username = user.username or user.username_tel or str(user.telegram_id)
            display_name = user.get_display_name()
            trial_status = "✅ استفاده شده" if user.has_used_trial else "🎁 در دسترس"
            
            # بررسی کانفیگ‌های فعال
            active_configs = UserConfig.objects.filter(user=user, is_active=True)
            config_count = sum(1 for c in active_configs if not c.is_expired())
            
            msg += (
                f"👤 **{display_name}**\n"
                f"🆔 ID: `{user.telegram_id or 'نامشخص'}`\n"
                f"📱 @{username}\n"
                f"📅 {user.created_at.strftime('%Y/%m/%d')}\n"
                f"🎁 پلن تستی: {trial_status}\n"
                f"🔧 کانفیگ‌های فعال: {config_count}\n"
                f"🔸 {status}\n\n"
            )
        
        await update.message.reply_text(msg, parse_mode='Markdown')
    except Exception as e:
        logger.error(f"خطا در دریافت لیست کاربران: {e}")
        await update.message.reply_text(f"❌ خطا در دریافت لیست کاربران: {str(e)}")

# نمایش پلن‌ها - بهبود شده
async def list_plans(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        plans = ConfingPlansModel.objects.filter(is_deleted=False)
        if not plans:
            await update.message.reply_text("هیچ پلنی تعریف نشده است.")
            return
        
        msg = "📦 **پلن‌ها:**\n\n"
        for plan in plans:
            is_test = " (تست)" if "تست" in plan.name.lower() else ""
            price_text = "🆓 رایگان" if plan.price == 0 else f"💰 {plan.price:,} تومان"
            msg += (
                f"📋 **{plan.name}{is_test}**\n"
                f"💵 {price_text}\n"
                f"📊 حجم: {plan.in_volume}MB\n\n"
            )
        await update.message.reply_text(msg, parse_mode='Markdown')
    except Exception as e:
        logger.error(f"خطا در دریافت لیست پلن‌ها: {e}")
        await update.message.reply_text(f"❌ خطا در دریافت لیست پلن‌ها: {str(e)}")

# افزودن پلن - بهبود شده
async def add_plan(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.from_user.id
    ADMIN_STATES[user_id] = "WAITING_PLAN_INFO"
    await update.message.reply_text(
        "📝 **افزودن پلن جدید**\n\n"
        "نام، قیمت و حجم پلن را به صورت زیر وارد کنید:\n\n"
        "**فرمت:** نام,قیمت,حجم\n\n"
        "**مثال‌ها:**\n"
        "`VIP,50000,5000`\n"
        "`تست رایگان,0,100`\n"
        "`پریمیوم,100000,10000`",
        parse_mode='Markdown'
    )

async def handle_plan_input(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.from_user.id
    
    if user_id not in ADMINS:
        return
    
    if ADMIN_STATES.get(user_id) == "WAITING_PLAN_INFO":
        try:
            name, price, volume = update.message.text.split(",")
            plan = ConfingPlansModel.objects.create(
                name=name.strip(), 
                price=int(price), 
                in_volume=int(volume)
            )
            del ADMIN_STATES[user_id]
            
            price_text = "🆓 رایگان" if plan.price == 0 else f"💰 {plan.price:,} تومان"
            await update.message.reply_text(
                f"✅ **پلن با موفقیت اضافه شد!**\n\n"
                f"📋 نام: {plan.name}\n"
                f"💵 قیمت: {price_text}\n"
                f"📊 حجم: {plan.in_volume}MB",
                parse_mode='Markdown'
            )
        except Exception as e:
            logger.error(f"خطا در افزودن پلن: {e}")
            await update.message.reply_text(f"❌ خطا در افزودن پلن: {str(e)}")
        return

# مدیریت پلن‌های تستی - بهبود شده
async def manage_trial_plans(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        # آمار پلن‌های تستی
        total_users = UsersModel.objects.count()
        users_with_trial = UsersModel.objects.filter(has_used_trial=True).count()
        active_trials = TrialConfigModel.objects.filter(is_active=True).count()
        active_xui_configs = UserConfig.objects.filter(is_active=True).count()
        
        # کانفیگ‌های تستی فعال
        active_trial_configs = TrialConfigModel.objects.filter(is_active=True).order_by('-created_at')
        active_xui_trials = UserConfig.objects.filter(config_name__icontains="تستی", is_active=True).order_by('-created_at')
        
        msg = (
            f"🎁 **مدیریت پلن‌های تستی**\n\n"
            f"📊 **آمار کلی:**\n"
            f"👥 کل کاربران: {total_users}\n"
            f"🎁 استفاده از پلن تستی: {users_with_trial}\n"
            f"✅ کانفیگ‌های قدیمی فعال: {active_trials}\n"
            f"🔧 کانفیگ‌های X-UI فعال: {active_xui_configs}\n\n"
        )
        
        if active_xui_trials:
            msg += "**کانفیگ‌های تستی X-UI فعال:**\n\n"
            for config in active_xui_trials[:5]:  # نمایش 5 مورد اول
                remaining_time = config.get_remaining_time()
                if remaining_time:
                    hours = int(remaining_time.total_seconds() // 3600)
                    minutes = int((remaining_time.total_seconds() % 3600) // 60)
                    time_text = f"{hours} ساعت و {minutes} دقیقه باقی"
                else:
                    time_text = "نامحدود"
                
                msg += (
                    f"👤 {config.user.get_display_name()}\n"
                    f"🆔 ID: `{config.user.telegram_id}`\n"
                    f"🖥️ سرور: {config.server.name}\n"
                    f"⏰ باقی‌مانده: {time_text}\n"
                    f"📅 ایجاد: {config.created_at.strftime('%Y/%m/%d %H:%M')}\n\n"
                )
        else:
            msg += "❌ هیچ کانفیگ تستی فعالی وجود ندارد.\n\n"
        
        await update.message.reply_text(msg, parse_mode='Markdown')
        
    except Exception as e:
        logger.error(f"خطا در مدیریت پلن‌های تستی: {e}")
        await update.message.reply_text(f"❌ خطا در مدیریت پلن‌های تستی: {str(e)}")

# نمایش درخواست‌های پرداخت - بهبود شده
async def show_payment_requests(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        payments = PayMentModel.objects.filter(is_active=True).order_by('-created_at')
        if not payments.exists():
            await update.message.reply_text("هیچ درخواست پرداختی وجود ندارد.")
            return
        
        msg = "💰 **درخواست‌های پرداخت:**\n\n"
        for payment in payments:
            status = "⏳ در انتظار بررسی"
            if payment.order.is_active:
                status = "✅ تایید شده"
            elif hasattr(payment, 'rejected') and payment.rejected:
                status = "❌ رد شده"
            
            user_info = payment.user.get_telegram_info()
            msg += (
                f"🆔 **کد:** {payment.code_pay}\n"
                f"👤 **کاربر:** {payment.user.get_display_name()}\n"
                f"🆔 **ID تلگرام:** `{user_info['id']}`\n"
                f"📱 **یوزرنیم:** @{user_info['username'] or 'بدون یوزرنیم'}\n"
                f"📦 **پلن:** {payment.order.plans.name}\n"
                f"💰 **مبلغ:** {payment.order.plans.price:,} تومان\n"
                f"🔸 **وضعیت:** {status}\n"
                f"📅 **تاریخ:** {payment.created_at.strftime('%Y/%m/%d %H:%M')}\n\n"
            )
        
        await update.message.reply_text(msg, parse_mode='Markdown')
    except Exception as e:
        logger.error(f"خطا در دریافت درخواست‌ها: {e}")
        await update.message.reply_text(f"❌ خطا در دریافت درخواست‌ها: {str(e)}")

# تایید یا رد پرداخت - بهبود شده
async def handle_payment_decision(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    
    action, payment_id = query.data.split('_')
    payment_id = int(payment_id)
    
    try:
        payment = PayMentModel.objects.get(id=payment_id)
        
        if action == "approve":
            # تایید پرداخت
            payment.order.is_active = True
            payment.order.save()
            payment.is_active = False
            payment.save()
            
            # ارسال پیام به کاربر
            try:
                user_info = payment.user.get_telegram_info()
                await context.bot.send_message(
                    chat_id=payment.user.telegram_id,
                    text=(
                        f"✅ **پرداخت شما تایید شد!**\n\n"
                        f"📦 پلن: {payment.order.plans.name}\n"
                        f"💰 مبلغ: {payment.order.plans.price:,} تومان\n"
                        f"📊 حجم: {payment.order.plans.in_volume}MB\n\n"
                        f"🎉 پلن شما فعال شد و آماده استفاده است!"
                    ),
                    parse_mode='Markdown'
                )
            except Exception as e:
                logger.error(f"خطا در ارسال پیام به کاربر: {e}")
            
            await query.edit_message_caption(
                query.message.caption + "\n\n✅ **تایید شد**",
                parse_mode='Markdown'
            )
            
        elif action == "reject":
            # رد پرداخت
            payment.is_active = False
            payment.rejected = True
            payment.save()
            
            # ارسال پیام به کاربر
            try:
                await context.bot.send_message(
                    chat_id=payment.user.telegram_id,
                    text=(
                        "❌ **پرداخت شما رد شد.**\n\n"
                        "لطفا با پشتیبانی تماس بگیرید یا دوباره تلاش کنید."
                    ),
                    parse_mode='Markdown'
                )
            except Exception as e:
                logger.error(f"خطا در ارسال پیام به کاربر: {e}")
            
            await query.edit_message_caption(
                query.message.caption + "\n\n❌ **رد شد**",
                parse_mode='Markdown'
            )
            
    except Exception as e:
        logger.error(f"خطا در پردازش تصمیم پرداخت: {e}")
        await query.edit_message_text("❌ خطا در پردازش درخواست.")

# ارسال پیام به کاربران - بهبود شده
async def send_message_to_users(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.from_user.id
    ADMIN_STATES[user_id] = "WAITING_USER_SELECTION"
    
    # نمایش لیست کاربران برای انتخاب
    users = UsersModel.objects.filter(telegram_id__isnull=False).order_by('-created_at')
    keyboard = []
    for user in users:
        display_name = user.get_display_name()
        keyboard.append([
            InlineKeyboardButton(
                f"{display_name} (@{user.username or 'بدون یوزرنیم'})",
                callback_data=f"select_user_{user.telegram_id}"
            )
        ])
    
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text(
        "👤 **لطفا کاربر مورد نظر را انتخاب کنید:**",
        reply_markup=reply_markup,
        parse_mode='Markdown'
    )

# انتخاب کاربر برای ارسال پیام
async def handle_user_selection(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    
    user_id = query.data.split('_')[2]
    admin_id = query.from_user.id
    
    ADMIN_STATES[admin_id] = f"WAITING_MESSAGE_{user_id}"
    
    await query.edit_message_text(
        f"✍️ **لطفا پیام خود را برای کاربر ارسال کنید:**"
    )

# دریافت پیام برای ارسال به کاربر
async def handle_message_to_user(update: Update, context: ContextTypes.DEFAULT_TYPE):
    admin_id = update.message.from_user.id
    
    if admin_id not in ADMINS:
        return
    
    state = ADMIN_STATES.get(admin_id)
    if not state or not state.startswith("WAITING_MESSAGE_"):
        return
    
    target_user_id = state.split("_")[2]
    message_text = update.message.text
    
    try:
        # ارسال پیام به کاربر
        await context.bot.send_message(
            chat_id=target_user_id,
            text=f"📨 **پیام از ادمین:**\n\n{message_text}",
            parse_mode='Markdown'
        )
        
        del ADMIN_STATES[admin_id]
        await update.message.reply_text("✅ پیام با موفقیت ارسال شد.")
        
    except Exception as e:
        logger.error(f"خطا در ارسال پیام به کاربر: {e}")
        await update.message.reply_text("❌ خطا در ارسال پیام.")

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
            f"📊 **آمار کلی:**\n\n"
            f"👥 **کل کاربران:** {total_users}\n"
            f"🟢 **کاربران فعال:** {active_users}\n"
            f"📦 **پلن‌های فعال:** {active_orders}\n"
            f"💰 **درخواست‌های در انتظار:** {pending_payments}\n"
            f"📋 **تعداد پلن‌ها:** {total_plans}\n"
            f"🎁 **استفاده از پلن تستی:** {users_with_trial}\n"
            f"✅ **کانفیگ‌های تستی فعال:** {active_trials}\n"
            f"🔧 **کانفیگ‌های X-UI فعال:** {active_xui_configs}\n"
            f"🖥️ **کل سرورها:** {total_servers}\n"
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
    app.add_handler(MessageHandler(filters.Regex("👥 لیست کاربران"), list_users))
    app.add_handler(MessageHandler(filters.Regex("📦 لیست پلن‌ها"), list_plans))
    app.add_handler(MessageHandler(filters.Regex("➕ افزودن پلن"), add_plan))
    app.add_handler(MessageHandler(filters.Regex("💰 درخواست‌های پرداخت"), show_payment_requests))
    app.add_handler(MessageHandler(filters.Regex("📨 ارسال پیام به کاربران"), send_message_to_users))
    app.add_handler(MessageHandler(filters.Regex("📊 آمار کلی"), show_statistics))
    app.add_handler(MessageHandler(filters.Regex("🎁 مدیریت پلن‌های تستی"), manage_trial_plans))
    app.add_handler(MessageHandler(filters.Regex("🖥️ مدیریت سرورهای X-UI"), manage_xui_servers))
    
    # پردازش انتخاب کاربر
    app.add_handler(CallbackQueryHandler(handle_user_selection, pattern="^select_user_"))
    
    # پردازش تصمیم پرداخت
    app.add_handler(CallbackQueryHandler(handle_payment_decision, pattern="^(approve|reject)_"))
    
    # پردازش ورودی پلن
    app.add_handler(MessageHandler(filters.TEXT & filters.User(user_id=ADMINS), handle_plan_input))
    
    # پردازش پیام به کاربر
    app.add_handler(MessageHandler(filters.TEXT & filters.User(user_id=ADMINS), handle_message_to_user))
    
    # پردازش ورودی سرور X-UI
    app.add_handler(MessageHandler(filters.TEXT & filters.User(user_id=ADMINS), handle_xui_server_input))

    print("🤖 Admin Bot is running...")
    
    # Fix for Windows event loop
    if sys.platform == 'win32':
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
    
    try:
        # Use nest_asyncio to fix the event loop issue
        import nest_asyncio
        nest_asyncio.apply()
        asyncio.run(app.run_polling())
    except KeyboardInterrupt:
        print("\n🤖 ربات ادمین متوقف شد...")
    except Exception as e:
        print(f"❌ خطا در اجرای ربات ادمین: {e}") 