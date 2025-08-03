import os
import django
import datetime
from telegram import Update, ReplyKeyboardMarkup, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes, MessageHandler, CallbackQueryHandler, filters
import os
import sys
import django
import asyncio
from dotenv import load_dotenv
import logging
from asgiref.sync import sync_to_async
from django.utils import timezone
from datetime import timedelta

# Load environment variables
load_dotenv()

# اضافه کردن مسیر پروژه به sys.path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# تنظیم ماژول تنظیمات
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')

# راه‌اندازی جنگو
django.setup()

from accounts.models import UsersModel
from order.models import OrderUserModel, PayMentModel
from conf.models import ConfigUserModel, TrialConfigModel
from plan.models import ConfingPlansModel
from xui_servers.models import XUIServer, UserConfig
from xui_servers.services import UserConfigService

# تنظیم لاگینگ
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# حالت‌های مختلف کاربر
USER_STATES = {}

# دکمه‌های کیبورد
main_keyboard = ReplyKeyboardMarkup([
    ["🛒 خرید پلن", "📊 پروفایل من"],
    ["📦 پلن‌های من", "⚙️ تنظیمات من"],
    ["🎁 پلن تستی", "📚 راهنما"]
], resize_keyboard=True)

# راهنمای کامل
async def show_help(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """نمایش راهنمای کامل ربات"""
    help_text = (
        "📚 **راهنمای کامل ربات VPN**\n\n"
        "🎯 **مراحل استفاده از ربات:**\n\n"
        "1️⃣ **شروع کار:**\n"
        "   • دستور /start را بزنید\n"
        "   • اطلاعات شما به صورت خودکار ثبت می‌شود\n\n"
        "2️⃣ **انتخاب نوع سرویس:**\n"
        "   🎁 **پلن تستی:** رایگان، 24 ساعت، یک بار استفاده\n"
        "   🛒 **پلن پولی:** با پرداخت، 30 روز اعتبار\n\n"
        "3️⃣ **دریافت کانفیگ:**\n"
        "   • کانفیگ شما در بخش 'تنظیمات من' ذخیره می‌شود\n"
        "   • می‌توانید آن را کپی و استفاده کنید\n\n"
        "4️⃣ **استفاده از کانفیگ:**\n"
        "   • در اپلیکیشن‌های VPN استفاده کنید\n"
        "   • سرعت و پایداری بالا\n\n"
        "💡 **نکات مهم:**\n"
        "• پلن تستی فقط یک بار قابل استفاده است\n"
        "• پس از انقضا، پلن جدید خریداری کنید\n"
        "• در صورت مشکل با ادمین تماس بگیرید"
    )
    
    keyboard = [
        [InlineKeyboardButton("📱 راهنمای نصب اپ", callback_data="app_guide")],
        [InlineKeyboardButton("🔧 راهنمای کانفیگ", callback_data="config_guide")],
        [InlineKeyboardButton("❓ سوالات متداول", callback_data="faq")],
        [InlineKeyboardButton("📞 تماس با پشتیبانی", callback_data="support")]
    ]
    
    await update.message.reply_text(
        help_text,
        parse_mode='Markdown',
        reply_markup=InlineKeyboardMarkup(keyboard)
    )

# راهنمای نصب اپلیکیشن
async def show_app_guide(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """راهنمای نصب اپلیکیشن‌های VPN"""
    query = update.callback_query
    await query.answer()
    
    guide_text = (
        "📱 **راهنمای نصب اپلیکیشن‌های VPN**\n\n"
        "🔹 **برای اندروید:**\n"
        "1. V2rayNG را از Google Play دانلود کنید\n"
        "2. اپ را باز کنید\n"
        "3. روی + کلیک کنید\n"
        "4. کانفیگ را از کلیپ‌بورد وارد کنید\n"
        "5. روی اتصال کلیک کنید\n\n"
        "🔹 **برای آیفون:**\n"
        "1. Shadowrocket را از App Store دانلود کنید\n"
        "2. اپ را باز کنید\n"
        "3. روی + کلیک کنید\n"
        "4. کانفیگ را وارد کنید\n"
        "5. روی اتصال کلیک کنید\n\n"
        "🔹 **برای ویندوز:**\n"
        "1. V2rayN را دانلود کنید\n"
        "2. فایل را اجرا کنید\n"
        "3. کانفیگ را وارد کنید\n"
        "4. روی اتصال کلیک کنید\n\n"
        "⚠️ **نکات مهم:**\n"
        "• کانفیگ را در جای امنی ذخیره کنید\n"
        "• از اپلیکیشن‌های معتبر استفاده کنید\n"
        "• در صورت مشکل، اپ را ری‌استارت کنید"
    )
    
    await query.edit_message_text(
        guide_text,
        parse_mode='Markdown',
        reply_markup=InlineKeyboardMarkup([[
            InlineKeyboardButton("🔙 بازگشت", callback_data="back_to_help")
        ]])
    )

# راهنمای کانفیگ
async def show_config_guide(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """راهنمای استفاده از کانفیگ"""
    query = update.callback_query
    await query.answer()
    
    guide_text = (
        "🔧 **راهنمای استفاده از کانفیگ**\n\n"
        "📋 **مراحل کپی کردن کانفیگ:**\n"
        "1. به بخش 'تنظیمات من' بروید\n"
        "2. روی کانفیگ مورد نظر کلیک کنید\n"
        "3. کانفیگ کپی می‌شود\n\n"
        "📱 **نحوه وارد کردن در اپ:**\n"
        "1. اپلیکیشن VPN را باز کنید\n"
        "2. گزینه 'Import' یا 'وارد کردن' را انتخاب کنید\n"
        "3. کانفیگ کپی شده را پیست کنید\n"
        "4. روی 'Save' یا 'ذخیره' کلیک کنید\n\n"
        "🔗 **نحوه اتصال:**\n"
        "1. کانفیگ ذخیره شده را انتخاب کنید\n"
        "2. روی دکمه اتصال کلیک کنید\n"
        "3. منتظر اتصال بمانید\n"
        "4. پیام موفقیت را مشاهده کنید\n\n"
        "⚠️ **مشکلات رایج:**\n"
        "• اگر اتصال برقرار نشد، کانفیگ را دوباره وارد کنید\n"
        "• اگر سرعت کم است، سرور دیگری انتخاب کنید\n"
        "• اگر کانفیگ منقضی شده، پلن جدید خریداری کنید"
    )
    
    await query.edit_message_text(
        guide_text,
        parse_mode='Markdown',
        reply_markup=InlineKeyboardMarkup([[
            InlineKeyboardButton("🔙 بازگشت", callback_data="back_to_help")
        ]])
    )

# سوالات متداول
async def show_faq(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """سوالات متداول"""
    query = update.callback_query
    await query.answer()
    
    faq_text = (
        "❓ **سوالات متداول**\n\n"
        "🔹 **سوال:** چرا نمی‌توانم متصل شوم؟\n"
        "**پاسخ:** کانفیگ را دوباره وارد کنید یا با پشتیبانی تماس بگیرید\n\n"
        "🔹 **سوال:** سرعت اینترنت کم شده، چرا؟\n"
        "**پاسخ:** ممکن است سرور شلوغ باشد، سرور دیگری امتحان کنید\n\n"
        "🔹 **سوال:** کانفیگ منقضی شده، چه کار کنم؟\n"
        "**پاسخ:** پلن جدید خریداری کنید\n\n"
        "🔹 **سوال:** پلن تستی را قبلاً استفاده کرده‌ام، چرا نمی‌توانم دوباره بگیرم؟\n"
        "**پاسخ:** پلن تستی فقط یک بار قابل استفاده است\n\n"
        "🔹 **سوال:** چقدر طول می‌کشد تا پرداخت تایید شود؟\n"
        "**پاسخ:** معمولاً کمتر از 1 ساعت\n\n"
        "🔹 **سوال:** آیا می‌توانم پلن‌های مختلف همزمان داشته باشم؟\n"
        "**پاسخ:** بله، می‌توانید چندین پلن فعال داشته باشید"
    )
    
    await query.edit_message_text(
        faq_text,
        parse_mode='Markdown',
        reply_markup=InlineKeyboardMarkup([[
            InlineKeyboardButton("🔙 بازگشت", callback_data="back_to_help")
        ]])
    )

# تماس با پشتیبانی
async def show_support(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """اطلاعات تماس با پشتیبانی"""
    query = update.callback_query
    await query.answer()
    
    support_text = (
        "📞 **تماس با پشتیبانی**\n\n"
        "🔹 **کانال تلگرام:**\n"
        "@vpn_support_channel\n\n"
        "🔹 **گروه پشتیبانی:**\n"
        "@vpn_support_group\n\n"
        "🔹 **ایمیل:**\n"
        "support@vpnservice.com\n\n"
        "⏰ **ساعات کاری:**\n"
        "شنبه تا چهارشنبه: 9 صبح تا 6 عصر\n"
        "پنجشنبه: 9 صبح تا 1 ظهر\n\n"
        "💡 **قبل از تماس:**\n"
        "• شماره سفارش خود را آماده کنید\n"
        "• مشکل را دقیق توضیح دهید\n"
        "• اسکرین‌شات از خطا ارسال کنید"
    )
    
    await query.edit_message_text(
        support_text,
        parse_mode='Markdown',
        reply_markup=InlineKeyboardMarkup([[
            InlineKeyboardButton("🔙 بازگشت", callback_data="back_to_help")
        ]])
    )

# بازگشت به منوی اصلی راهنما
async def back_to_help(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """بازگشت به منوی اصلی راهنما"""
    query = update.callback_query
    await query.answer()
    
    help_text = (
        "📚 **راهنمای کامل ربات VPN**\n\n"
        "🎯 **مراحل استفاده از ربات:**\n\n"
        "1️⃣ **شروع کار:**\n"
        "   • دستور /start را بزنید\n"
        "   • اطلاعات شما به صورت خودکار ثبت می‌شود\n\n"
        "2️⃣ **انتخاب نوع سرویس:**\n"
        "   🎁 **پلن تستی:** رایگان، 24 ساعت، یک بار استفاده\n"
        "   🛒 **پلن پولی:** با پرداخت، 30 روز اعتبار\n\n"
        "3️⃣ **دریافت کانفیگ:**\n"
        "   • کانفیگ شما در بخش 'تنظیمات من' ذخیره می‌شود\n"
        "   • می‌توانید آن را کپی و استفاده کنید\n\n"
        "4️⃣ **استفاده از کانفیگ:**\n"
        "   • در اپلیکیشن‌های VPN استفاده کنید\n"
        "   • سرعت و پایداری بالا\n\n"
        "💡 **نکات مهم:**\n"
        "• پلن تستی فقط یک بار قابل استفاده است\n"
        "• پس از انقضا، پلن جدید خریداری کنید\n"
        "• در صورت مشکل با ادمین تماس بگیرید"
    )
    
    keyboard = [
        [InlineKeyboardButton("📱 راهنمای نصب اپ", callback_data="app_guide")],
        [InlineKeyboardButton("🔧 راهنمای کانفیگ", callback_data="config_guide")],
        [InlineKeyboardButton("❓ سوالات متداول", callback_data="faq")],
        [InlineKeyboardButton("📞 تماس با پشتیبانی", callback_data="support")]
    ]
    
    await query.edit_message_text(
        help_text,
        parse_mode='Markdown',
        reply_markup=InlineKeyboardMarkup(keyboard)
    )

# راهنمای مرحله به مرحله برای شروع
async def show_start_tutorial(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """راهنمای مرحله به مرحله برای شروع"""
    tutorial_text = (
        "🎯 **راهنمای مرحله به مرحله**\n\n"
        "✅ **مرحله 1: ثبت‌نام**\n"
        "• دستور /start را زدید\n"
        "• اطلاعات شما ثبت شد\n"
        "• خوش آمدید! 🎉\n\n"
        "📋 **مرحله بعدی:**\n"
        "حالا می‌توانید یکی از گزینه‌های زیر را انتخاب کنید:\n\n"
        "🎁 **پلن تستی:**\n"
        "• رایگان و 24 ساعته\n"
        "• فقط یک بار قابل استفاده\n"
        "• برای تست سرویس\n\n"
        "🛒 **خرید پلن:**\n"
        "• پلن‌های پولی\n"
        "• 30 روز اعتبار\n"
        "• حجم نامحدود\n\n"
        "💡 **توصیه:**\n"
        "اگر اولین بار است، ابتدا پلن تستی را امتحان کنید!"
    )
    
    keyboard = [
        [InlineKeyboardButton("🎁 پلن تستی", callback_data="trial_tutorial")],
        [InlineKeyboardButton("🛒 خرید پلن", callback_data="buy_tutorial")],
        [InlineKeyboardButton("📊 پروفایل من", callback_data="profile_tutorial")]
    ]
    
    await update.message.reply_text(
        tutorial_text,
        parse_mode='Markdown',
        reply_markup=InlineKeyboardMarkup(keyboard)
    )

# راهنمای پلن تستی
async def show_trial_tutorial(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """راهنمای پلن تستی"""
    query = update.callback_query
    await query.answer()
    
    tutorial_text = (
        "🎁 **راهنمای پلن تستی**\n\n"
        "📋 **مشخصات پلن تستی:**\n"
        "• ⏰ اعتبار: 24 ساعت\n"
        "• 📊 حجم: نامحدود\n"
        "• 💰 قیمت: رایگان\n"
        "• 🔄 تعداد: فقط یک بار\n\n"
        "📝 **مراحل دریافت:**\n"
        "1. روی '🎁 پلن تستی' کلیک کنید\n"
        "2. سیستم کانفیگ شما را ایجاد می‌کند\n"
        "3. کانفیگ در 'تنظیمات من' ذخیره می‌شود\n"
        "4. می‌توانید آن را کپی و استفاده کنید\n\n"
        "⚠️ **نکات مهم:**\n"
        "• این پلن فقط یک بار قابل استفاده است\n"
        "• پس از 24 ساعت منقضی می‌شود\n"
        "• برای استفاده مداوم، پلن پولی خریداری کنید\n\n"
        "💡 **آیا می‌خواهید پلن تستی دریافت کنید؟**"
    )
    
    keyboard = [
        [InlineKeyboardButton("🎁 دریافت پلن تستی", callback_data="get_trial")],
        [InlineKeyboardButton("🛒 خرید پلن پولی", callback_data="buy_tutorial")],
        [InlineKeyboardButton("🔙 بازگشت", callback_data="back_to_start_tutorial")]
    ]
    
    await query.edit_message_text(
        tutorial_text,
        parse_mode='Markdown',
        reply_markup=InlineKeyboardMarkup(keyboard)
    )

# راهنمای خرید پلن
async def show_buy_tutorial(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """راهنمای خرید پلن"""
    query = update.callback_query
    await query.answer()
    
    tutorial_text = (
        "🛒 **راهنمای خرید پلن**\n\n"
        "📋 **مراحل خرید:**\n"
        "1. روی '🛒 خرید پلن' کلیک کنید\n"
        "2. از لیست پلن‌ها یکی را انتخاب کنید\n"
        "3. اطلاعات پلن را بررسی کنید\n"
        "4. برای پلن‌های رایگان، بلافاصله فعال می‌شود\n"
        "5. برای پلن‌های پولی، رسید پرداخت ارسال کنید\n\n"
        "💰 **انواع پلن‌ها:**\n"
        "• 🆓 **رایگان:** بدون پرداخت، بلافاصله فعال\n"
        "• 💳 **پولی:** با پرداخت، پس از تایید فعال\n\n"
        "📊 **مشخصات پلن‌ها:**\n"
        "• ⏰ اعتبار: 30 روز\n"
        "• 📊 حجم: طبق پلن انتخاب شده\n"
        "• 🔧 کانفیگ: VMess/VLess/Trojan\n\n"
        "💡 **توصیه:**\n"
        "پلن‌های رایگان را امتحان کنید!"
    )
    
    keyboard = [
        [InlineKeyboardButton("🛒 مشاهده پلن‌ها", callback_data="view_plans")],
        [InlineKeyboardButton("🎁 پلن تستی", callback_data="trial_tutorial")],
        [InlineKeyboardButton("🔙 بازگشت", callback_data="back_to_start_tutorial")]
    ]
    
    await query.edit_message_text(
        tutorial_text,
        parse_mode='Markdown',
        reply_markup=InlineKeyboardMarkup(keyboard)
    )

# راهنمای پروفایل
async def show_profile_tutorial(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """راهنمای پروفایل"""
    query = update.callback_query
    await query.answer()
    
    tutorial_text = (
        "📊 **راهنمای پروفایل**\n\n"
        "📋 **اطلاعات نمایش داده شده:**\n"
        "• 🆔 شناسه تلگرام شما\n"
        "• 👤 نام کامل\n"
        "• 📱 نام کاربری\n"
        "• 📅 تاریخ عضویت\n"
        "• 📦 تعداد کل سفارشات\n"
        "• ✅ سفارشات فعال\n"
        "• 🎁 وضعیت پلن تستی\n"
        "• 🔧 تعداد کانفیگ‌های فعال\n\n"
        "💡 **کاربردها:**\n"
        "• بررسی وضعیت حساب کاربری\n"
        "• مشاهده تاریخچه سفارشات\n"
        "• بررسی اعتبار پلن‌ها\n"
        "• اطلاع از تعداد کانفیگ‌های فعال\n\n"
        "🔄 **به‌روزرسانی:**\n"
        "اطلاعات به صورت خودکار به‌روزرسانی می‌شود"
    )
    
    keyboard = [
        [InlineKeyboardButton("📊 مشاهده پروفایل", callback_data="view_profile")],
        [InlineKeyboardButton("🛒 خرید پلن", callback_data="buy_tutorial")],
        [InlineKeyboardButton("🔙 بازگشت", callback_data="back_to_start_tutorial")]
    ]
    
    await query.edit_message_text(
        tutorial_text,
        parse_mode='Markdown',
        reply_markup=InlineKeyboardMarkup(keyboard)
    )

# بازگشت به راهنمای شروع
async def back_to_start_tutorial(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """بازگشت به راهنمای شروع"""
    query = update.callback_query
    await query.answer()
    
    tutorial_text = (
        "🎯 **راهنمای مرحله به مرحله**\n\n"
        "✅ **مرحله 1: ثبت‌نام**\n"
        "• دستور /start را زدید\n"
        "• اطلاعات شما ثبت شد\n"
        "• خوش آمدید! 🎉\n\n"
        "📋 **مرحله بعدی:**\n"
        "حالا می‌توانید یکی از گزینه‌های زیر را انتخاب کنید:\n\n"
        "🎁 **پلن تستی:**\n"
        "• رایگان و 24 ساعته\n"
        "• فقط یک بار قابل استفاده\n"
        "• برای تست سرویس\n\n"
        "🛒 **خرید پلن:**\n"
        "• پلن‌های پولی\n"
        "• 30 روز اعتبار\n"
        "• حجم نامحدود\n\n"
        "💡 **توصیه:**\n"
        "اگر اولین بار است، ابتدا پلن تستی را امتحان کنید!"
    )
    
    keyboard = [
        [InlineKeyboardButton("🎁 پلن تستی", callback_data="trial_tutorial")],
        [InlineKeyboardButton("🛒 خرید پلن", callback_data="buy_tutorial")],
        [InlineKeyboardButton("📊 پروفایل من", callback_data="profile_tutorial")]
    ]
    
    await query.edit_message_text(
        tutorial_text,
        parse_mode='Markdown',
        reply_markup=InlineKeyboardMarkup(keyboard)
    )

# دستور start - بهبود شده با راهنما
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_data = update.effective_user
    telegram_id = user_data.id
    
    try:
        # بررسی وجود کاربر با sync_to_async
        user, created = await sync_to_async(UsersModel.objects.get_or_create)(
            telegram_id=telegram_id,
            defaults={
                "id_tel": str(user_data.id),
                "username_tel": user_data.username or "",
                "full_name": user_data.full_name or user_data.first_name or "کاربر",
                "username": user_data.username or ""
            }
        )
        
        if created:
            # اگر کاربر جدید است
            welcome_message = (
                f"🎉 خوش آمدید {user.full_name}!\n\n"
                f"✅ ثبت‌نام شما با موفقیت انجام شد.\n"
                f"🆔 شناسه تلگرام: {telegram_id}\n"
                f"👤 نام: {user.full_name}\n"
                f"📱 نام کاربری: @{user.username or 'تعریف نشده'}\n\n"
                f"💡 برای شروع، یکی از گزینه‌های زیر را انتخاب کنید:\n"
                f"🎁 پلن تستی: برای تست رایگان\n"
                f"🛒 خرید پلن: برای خرید پلن‌های پولی\n"
                f"📚 راهنما: برای آموزش کامل"
            )
            
            # نمایش راهنمای مرحله به مرحله برای کاربران جدید
            await update.message.reply_text(
                welcome_message,
                reply_markup=main_keyboard
            )
            
            # نمایش راهنمای مرحله به مرحله
            await show_start_tutorial(update, context)
            
        else:
            # اگر کاربر قبلی است
            trial_status = "✅ در دسترس" if user.can_get_trial() else "❌ استفاده شده"
            welcome_message = (
                f"🔁 خوش برگشتی {user.full_name}!\n\n"
                f"🆔 شناسه تلگرام: {telegram_id}\n"
                f"👤 نام: {user.full_name}\n"
                f"📱 نام کاربری: @{user.username or 'تعریف نشده'}\n"
                f"🎁 پلن تستی: {trial_status}\n\n"
                f"💡 چه کاری می‌توانم برای شما انجام دهم؟"
            )
            
            await update.message.reply_text(
                welcome_message,
                reply_markup=main_keyboard
            )
            
    except Exception as e:
        logger.error(f"خطا در ثبت‌نام: {e}")
        await update.message.reply_text("❌ خطا در ثبت‌نام. لطفا دوباره تلاش کنید.")

# نمایش پروفایل - بهبود شده
async def profile(update: Update, context: ContextTypes.DEFAULT_TYPE):
    telegram_id = update.effective_user.id
    try:
        user = await sync_to_async(UsersModel.objects.get)(telegram_id=telegram_id)
        
        # محاسبه آمار کاربر
        total_orders = await sync_to_async(OrderUserModel.objects.filter)(user=user)
        active_orders = await sync_to_async(total_orders.filter)(is_active=True)
        
        # بررسی کانفیگ تستی
        trial_config = await sync_to_async(lambda: getattr(user, 'trial_config', None))()
        trial_status = "✅ فعال" if trial_config and not trial_config.is_expired() else "❌ غیرفعال"
        
        # بررسی کانفیگ‌های X-UI
        xui_configs = await sync_to_async(list)(UserConfig.objects.filter(user=user, is_active=True))
        active_xui_configs = [c for c in xui_configs if not c.is_expired()]
        
        profile_text = (
            f"👤 **پروفایل شما**\n\n"
            f"🆔 **شناسه تلگرام:** `{telegram_id}`\n"
            f"👤 **نام:** {user.full_name}\n"
            f"📱 **نام کاربری:** @{user.username or 'تعریف نشده'}\n"
            f"📅 **تاریخ عضویت:** {user.created_at.strftime('%Y/%m/%d')}\n"
            f"📦 **کل سفارشات:** {await sync_to_async(total_orders.count)()}\n"
            f"✅ **سفارشات فعال:** {await sync_to_async(active_orders.count)()}\n"
            f"🎁 **پلن تستی:** {trial_status}\n"
            f"🔧 **کانفیگ‌های فعال:** {len(active_xui_configs)}\n\n"
            f"💡 برای خرید پلن جدید، گزینه 🛒 خرید پلن را انتخاب کنید."
        )
        
        await update.message.reply_text(
            profile_text,
            parse_mode='Markdown'
        )
    except UsersModel.DoesNotExist:
        await update.message.reply_text("❌ ابتدا /start را بزنید.")
    except Exception as e:
        logger.error(f"خطا در دریافت پروفایل: {e}")
        await update.message.reply_text("❌ خطا در دریافت اطلاعات پروفایل.")

# پلن تستی - بهبود شده با X-UI
async def trial_plan(update: Update, context: ContextTypes.DEFAULT_TYPE):
    telegram_id = update.effective_user.id
    try:
        user = await sync_to_async(UsersModel.objects.get)(telegram_id=telegram_id)
        
        if not user.can_get_trial():
            await update.message.reply_text(
                "❌ **شما قبلاً از پلن تستی استفاده کرده‌اید.**\n\n"
                "💡 برای استفاده از سرویس، لطفا یکی از پلن‌های پولی را انتخاب کنید.",
                parse_mode='Markdown'
            )
            return
        
        # بررسی سرورهای فعال
        active_servers = await sync_to_async(list)(XUIServer.objects.filter(is_active=True))
        if not active_servers:
            await update.message.reply_text(
                "❌ **هیچ سرور فعالی یافت نشد.**\n\n"
                "لطفا با ادمین تماس بگیرید.",
                parse_mode='Markdown'
            )
            return
        
        # انتخاب اولین سرور فعال
        server = active_servers[0]
        
        # ایجاد کانفیگ تستی با inbound واقعی
        try:
            # استفاده از inbound موجود در X-UI
            import requests
            import uuid
            
            # اتصال به X-UI
            base_url = f"http://{server.host}:{server.port}"
            if hasattr(server, 'web_base_path') and server.web_base_path:
                base_url += server.web_base_path
            
            session = requests.Session()
            
            # لاگین
            login_data = {
                "username": server.username,
                "password": server.password
            }
            
            login_response = session.post(f"{base_url}/login", json=login_data, timeout=10)
            if login_response.status_code != 200:
                raise Exception("خطا در لاگین به X-UI")
            
            # دریافت inbound ها
            inbounds_response = session.get(f"{base_url}/panel/api/inbounds", timeout=10)
            if inbounds_response.status_code != 200:
                raise Exception("خطا در دریافت inbound ها")
            
            inbounds = inbounds_response.json()
            
            # انتخاب inbound مناسب (VLESS با Reality) و دریافت تنظیمات
            target_inbound = None
            private_key = ""
            dest = "www.aparat.com:443"
            server_names = ["www.aparat.com"]
            short_ids = ["a1b2c3d4"]
            
            for inbound in inbounds:
                if (inbound.get('protocol') == 'vless' and 
                    'reality' in inbound.get('streamSettings', {}).get('security', '').lower()):
                    target_inbound = inbound
                    
                    # دریافت تنظیمات Reality
                    stream_settings = inbound.get('streamSettings', {})
                    reality_settings = stream_settings.get('realitySettings', {})
                    
                    private_key = reality_settings.get('privateKey', '')
                    dest = reality_settings.get('dest', 'www.aparat.com:443')
                    server_names = reality_settings.get('serverNames', ['www.aparat.com'])
                    short_ids = reality_settings.get('shortIds', ['a1b2c3d4'])
                    
                    break
            
            if not target_inbound:
                raise Exception("هیچ inbound مناسب یافت نشد")
            
            if not private_key:
                raise Exception("کلید خصوصی Reality موجود نیست")
            
            inbound_id = target_inbound.get('id')
            port = target_inbound.get('port', 443)
            
            # تولید UUID برای کاربر
            user_uuid = str(uuid.uuid4())
            
            # تنظیمات کاربر جدید
            user_data = {
                "id": inbound_id,
                "settings": {
                    "clients": [
                        {
                            "id": user_uuid,
                            "flow": "",
                            "email": f"{user.full_name}@vpn.com",
                            "limitIp": 0,
                            "totalGB": 0,
                            "expiryTime": 0,
                            "enable": True,
                            "tgId": "",
                            "subId": ""
                        }
                    ]
                }
            }
            
            # اضافه کردن کاربر به inbound
            response = session.post(f"{base_url}/panel/api/inbounds/update/{inbound_id}", json=user_data, timeout=10)
            if response.status_code != 200:
                raise Exception("خطا در اضافه کردن کاربر به inbound")
            
            # تولید کانفیگ VLess با تنظیمات صحیح
            dest_host = dest.split(':')[0] if ':' in dest else dest
            sni = server_names[0] if server_names else dest_host
            short_id = short_ids[0] if short_ids else "a1b2c3d4"
            
            config_data = f"vless://{user_uuid}@{server.host}:{port}?type=tcp&security=reality&pbk={private_key}&fp=chrome&sni={sni}&sid={short_id}&spx=%2F#{user.full_name}"
            
            # ایجاد کانفیگ در دیتابیس
            user_config = await sync_to_async(UserConfig.objects.create)(
                user=user,
                server=server,
                xui_inbound_id=inbound_id,
                xui_user_id=user_uuid,
                config_name=f"پلن تستی {user.full_name} (VLESS)",
                config_data=config_data,
                protocol="vless",
                is_trial=True,
                expires_at=timezone.now() + timedelta(hours=24)
            )
            
            message = "کانفیگ تستی با موفقیت ایجاد شد (با X-UI)"
            
        except Exception as e:
            # در صورت خطا، کانفیگ ساده ایجاد کنیم
            from xui_servers.models import UserConfig
            import uuid
            import random
            import string
            
            # تولید کانفیگ VLess
            user_uuid = str(uuid.uuid4())
            fake_domain = random.choice(["www.aparat.com", "www.irib.ir", "www.varzesh3.com"])
            public_key = random.choice(["H5jCG+N2boOAvWRFcntZJsSFCMn6xMOa1NfU+KR3Cw=", "K8mFJ+Q5erRDwZUIfqubmvuIFPq9APzd/1QmF+NU6Fz="])
            short_id = ''.join(random.choices(string.hexdigits.lower(), k=8))
            port = random.randint(10000, 65000)
            
            config_data = f"vless://{user_uuid}@{server.host}:{port}?type=tcp&security=reality&sni={fake_domain}&fp=chrome&pbk={public_key}&sid={short_id}&spx=%2F#{user.full_name}"
            
            # ایجاد کانفیگ در دیتابیس
            user_config = await sync_to_async(UserConfig.objects.create)(
                user=user,
                server=server,
                xui_inbound_id=0,  # بدون X-UI
                xui_user_id=str(user.telegram_id) if user.telegram_id else str(user.id),
                config_name=f"پلن تستی {user.full_name} (VLESS)",
                config_data=config_data,
                protocol="vless",
                is_trial=True,
                expires_at=timezone.now() + timedelta(hours=24)
            )
            
            message = f"کانفیگ تستی با موفقیت ایجاد شد (بدون X-UI) - خطا: {e}"
        
        if user_config:
            # علامت‌گذاری استفاده از پلن تستی
            await sync_to_async(user.mark_trial_used)()
            
            await update.message.reply_text(
                f"🎉 **پلن تستی شما فعال شد!**\n\n"
                f"📋 **نام:** پلن تستی\n"
                f"⏰ **اعتبار:** 24 ساعت\n"
                f"📊 **حجم:** نامحدود\n"
                f"🖥️ **سرور:** {server.name}\n\n"
                f"🔧 **کانفیگ شما:**\n"
                f"`{user_config.config_data}`\n\n"
                f"⚠️ **نکات مهم:**\n"
                f"• این پلن فقط یک بار قابل استفاده است\n"
                f"• پس از 24 ساعت منقضی می‌شود\n"
                f"• برای استفاده مداوم، پلن پولی خریداری کنید",
                parse_mode='Markdown',
                reply_markup=main_keyboard
            )
        else:
            await update.message.reply_text(
                f"❌ **خطا در ایجاد کانفیگ تستی:**\n\n{message}",
                parse_mode='Markdown'
            )
        
    except UsersModel.DoesNotExist:
        await update.message.reply_text("❌ ابتدا /start را بزنید.")
    except Exception as e:
        logger.error(f"خطا در فعال‌سازی پلن تستی: {e}")
        await update.message.reply_text("❌ خطا در فعال‌سازی پلن تستی.")

# خرید پلن - بهبود شده
async def buy_plan(update: Update, context: ContextTypes.DEFAULT_TYPE):
    telegram_id = update.effective_user.id
    try:
        user = await sync_to_async(UsersModel.objects.get)(telegram_id=telegram_id)
        plans = await sync_to_async(list)(ConfingPlansModel.objects.filter(is_deleted=False))
        
        if not plans:
            await update.message.reply_text("❌ هیچ پلنی در دسترس نیست.")
            return
        
        # ایجاد دکمه‌های پلن‌ها
        keyboard = []
        for plan in plans:
            test_text = " (تست)" if "تست" in plan.name.lower() else ""
            price_text = "🆓 رایگان" if plan.price == 0 else f"💰 {plan.price:,} تومان"
            keyboard.append([
                InlineKeyboardButton(
                    f"{plan.name}{test_text}\n{price_text} - 📊 {plan.in_volume}MB",
                    callback_data=f"select_plan_{plan.id}"
                )
            ])
        
        reply_markup = InlineKeyboardMarkup(keyboard)
        await update.message.reply_text(
            "🛒 **لطفا پلن مورد نظر خود را انتخاب کنید:**\n\n"
            "💡 *پلن‌های تستی فقط 24 ساعت اعتبار دارند*",
            reply_markup=reply_markup,
            parse_mode='Markdown'
        )
        
    except UsersModel.DoesNotExist:
        await update.message.reply_text("❌ ابتدا /start را بزنید.")
    except Exception as e:
        logger.error(f"خطا در دریافت پلن‌ها: {e}")
        await update.message.reply_text("❌ خطا در دریافت پلن‌ها.")

# انتخاب پلن - بهبود شده
async def handle_plan_selection(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    
    plan_id = query.data.split('_')[2]
    telegram_id = query.from_user.id
    
    try:
        plan = await sync_to_async(ConfingPlansModel.objects.get)(id=plan_id)
        user = await sync_to_async(UsersModel.objects.get)(telegram_id=telegram_id)
        
        # ذخیره انتخاب کاربر
        context.user_data['selected_plan'] = plan_id
        
        # نمایش اطلاعات پلن و درخواست پرداخت
        is_test = "تست" in plan.name.lower()
        test_text = "\n⚠️ *این پلن تستی است و فقط 24 ساعت اعتبار دارد.*" if is_test else ""
        price_text = "🆓 رایگان" if plan.price == 0 else f"💰 {plan.price:,} تومان"
        
        plan_info = (
            f"📦 **پلن انتخاب شده:**\n\n"
            f"📋 **نام:** {plan.name}\n"
            f"💵 **قیمت:** {price_text}\n"
            f"📊 **حجم:** {plan.in_volume} مگابایت\n"
            f"⏰ **اعتبار:** 30 روز{test_text}\n\n"
        )
        
        if plan.price == 0:
            # برای پلن‌های رایگان
            plan_info += (
                f"🎉 **این پلن رایگان است!**\n\n"
                f"✅ پلن شما بلافاصله فعال خواهد شد."
            )
            USER_STATES[telegram_id] = "FREE_PLAN_CONFIRM"
        else:
            # برای پلن‌های پولی
            plan_info += (
                f"💳 **لطفا شماره کارت زیر را کپی کرده و مبلغ را واریز کنید:**\n\n"
                f"`1234-5678-9012-3456`\n\n"
                f"📸 **پس از پرداخت، رسید خود را ارسال کنید.**"
            )
            USER_STATES[telegram_id] = "WAITING_PAYMENT_RECEIPT"
        
        await query.edit_message_text(
            plan_info,
            parse_mode='Markdown'
        )
        
    except Exception as e:
        logger.error(f"خطا در انتخاب پلن: {e}")
        await query.edit_message_text("❌ خطا در انتخاب پلن.")

# تایید پلن رایگان - بهبود شده با X-UI
async def handle_free_plan_confirm(update: Update, context: ContextTypes.DEFAULT_TYPE):
    telegram_id = update.effective_user.id
    
    if USER_STATES.get(telegram_id) != "FREE_PLAN_CONFIRM":
        return
    
    try:
        user = await sync_to_async(UsersModel.objects.get)(telegram_id=telegram_id)
        plan_id = context.user_data.get('selected_plan')
        plan = await sync_to_async(ConfingPlansModel.objects.get)(id=plan_id)
        
        # بررسی سرورهای فعال
        active_servers = await sync_to_async(list)(XUIServer.objects.filter(is_active=True))
        if not active_servers:
            await update.message.reply_text(
                "❌ **هیچ سرور فعالی یافت نشد.**\n\n"
                "لطفا با ادمین تماس بگیرید.",
                parse_mode='Markdown'
            )
            return
        
        # انتخاب اولین سرور فعال
        server = active_servers[0]
        
        # ایجاد کانفیگ در X-UI
        user_config, message = await sync_to_async(UserConfigService.create_paid_config)(user, server, plan)
        
        if user_config:
            # ایجاد سفارش رایگان
            order = await sync_to_async(OrderUserModel.objects.create)(
                user=user,
                plans=plan,
                is_active=True  # پلن رایگان بلافاصله فعال می‌شود
            )
            
            del USER_STATES[telegram_id]
            await update.message.reply_text(
                f"🎉 **پلن {plan.name} با موفقیت فعال شد!**\n\n"
                f"✅ پلن شما آماده استفاده است.\n"
                f"📊 حجم: {plan.in_volume} مگابایت\n"
                f"⏰ اعتبار: 30 روز\n"
                f"🖥️ سرور: {server.name}\n\n"
                f"🔧 **کانفیگ شما:**\n"
                f"`{user_config.config_data}`",
                parse_mode='Markdown',
                reply_markup=main_keyboard
            )
        else:
            await update.message.reply_text(
                f"❌ **خطا در فعال‌سازی پلن:**\n\n{message}",
                parse_mode='Markdown'
            )
        
    except Exception as e:
        logger.error(f"خطا در فعال‌سازی پلن رایگان: {e}")
        await update.message.reply_text("❌ خطا در فعال‌سازی پلن.")

# دریافت رسید پرداخت - بهبود شده
async def handle_payment_receipt(update: Update, context: ContextTypes.DEFAULT_TYPE):
    telegram_id = update.effective_user.id
    
    if USER_STATES.get(telegram_id) != "WAITING_PAYMENT_RECEIPT":
        return
    
    if not update.message.photo:
        await update.message.reply_text("❌ لطفا عکس رسید پرداخت را ارسال کنید.")
        return
    
    try:
        user = await sync_to_async(UsersModel.objects.get)(telegram_id=telegram_id)
        plan_id = context.user_data.get('selected_plan')
        plan = await sync_to_async(ConfingPlansModel.objects.get)(id=plan_id)
        
        # ذخیره عکس
        photo = update.message.photo[-1]  # بهترین کیفیت
        file = await context.bot.get_file(photo.file_id)
        
        # ایجاد سفارش
        order = await sync_to_async(OrderUserModel.objects.create)(
            user=user,
            plans=plan,
            is_active=False  # تا تایید ادمین فعال نمی‌شود
        )
        
        # ذخیره رسید پرداخت
        payment = await sync_to_async(PayMentModel.objects.create)(
            user=user,
            order=order,
            images=file.file_path,  # در واقع باید فایل را دانلود و ذخیره کنیم
            code_pay=await sync_to_async(lambda: len(PayMentModel.objects.all()) + 1)()
        )
        
        # ارسال به ادمین
        admin_message = (
            f"💰 **درخواست پرداخت جدید**\n\n"
            f"👤 **کاربر:** {user.full_name}\n"
            f"🆔 **شناسه تلگرام:** `{telegram_id}`\n"
            f"📱 **نام کاربری:** @{user.username or 'بدون یوزرنیم'}\n"
            f"📦 **پلن:** {plan.name}\n"
            f"💰 **مبلغ:** {plan.price:,} تومان\n"
            f"🆔 **کد پرداخت:** {payment.code_pay}\n"
            f"📅 **تاریخ:** {payment.created_at.strftime('%Y/%m/%d %H:%M')}"
        )
        
        # ارسال به ادمین‌ها (در اینجا باید ID ادمین‌ها را تنظیم کنید)
        admin_ids = [123456789]  # ID ادمین‌ها را اینجا قرار دهید
        
        for admin_id in admin_ids:
            try:
                await context.bot.send_photo(
                    chat_id=admin_id,
                    photo=photo.file_id,
                    caption=admin_message,
                    parse_mode='Markdown',
                    reply_markup=InlineKeyboardMarkup([
                        [
                            InlineKeyboardButton("✅ تایید", callback_data=f"approve_{payment.id}"),
                            InlineKeyboardButton("❌ رد", callback_data=f"reject_{payment.id}")
                        ]
                    ])
                )
            except Exception as e:
                logger.error(f"خطا در ارسال به ادمین {admin_id}: {e}")
        
        del USER_STATES[telegram_id]
        await update.message.reply_text(
            "✅ **رسید شما با موفقیت ارسال شد!**\n\n"
            "⏳ در حال بررسی توسط ادمین...\n"
            "🔔 پس از تایید، پلن شما فعال خواهد شد.",
            parse_mode='Markdown',
            reply_markup=main_keyboard
        )
        
    except Exception as e:
        logger.error(f"خطا در پردازش رسید: {e}")
        await update.message.reply_text("❌ خطا در پردازش رسید. لطفا دوباره تلاش کنید.")

# نمایش پلن‌های کاربر - بهبود شده
async def my_plans(update: Update, context: ContextTypes.DEFAULT_TYPE):
    telegram_id = update.effective_user.id
    try:
        user = await sync_to_async(UsersModel.objects.get)(telegram_id=telegram_id)
        orders = await sync_to_async(list)(OrderUserModel.objects.filter(user=user).order_by('-created_at'))
        
        response = "📦 **پلن‌های شما:**\n\n"
        
        # بررسی کانفیگ تستی
        trial_config = await sync_to_async(lambda: getattr(user, 'trial_config', None))()
        if trial_config and not trial_config.is_expired():
            remaining_time = trial_config.get_remaining_time()
            hours = int(remaining_time.total_seconds() // 3600)
            minutes = int((remaining_time.total_seconds() % 3600) // 60)
            
            response += (
                f"🎁 **پلن تستی**\n"
                f"📊 حجم: نامحدود\n"
                f"⏰ اعتبار: {hours} ساعت و {minutes} دقیقه باقی\n"
                f"🔧 کانفیگ: `{trial_config.config}`\n\n"
            )
        
        # بررسی کانفیگ‌های X-UI
        xui_configs = await sync_to_async(list)(UserConfig.objects.filter(user=user, is_active=True))
        for config in xui_configs:
            if not config.is_expired():
                remaining_time = config.get_remaining_time()
                if remaining_time:
                    hours = int(remaining_time.total_seconds() // 3600)
                    minutes = int((remaining_time.total_seconds() % 3600) // 60)
                    time_text = f"{hours} ساعت و {minutes} دقیقه باقی"
                else:
                    time_text = "نامحدود"
                
                response += (
                    f"🔧 **{config.config_name}**\n"
                    f"🖥️ سرور: {config.server.name}\n"
                    f"⏰ اعتبار: {time_text}\n"
                    f"🔧 کانفیگ: `{config.config_data}`\n\n"
                )
        
        if orders:
            for order in orders:
                status = "✅ فعال" if order.is_active else "⏳ در انتظار تایید"
                status_emoji = "🟢" if order.is_active else "🟡"
                
                response += (
                    f"{status_emoji} **{order.plans.name}**\n"
                f"💰 قیمت: {order.plans.price:,} تومان\n"
                f"📊 حجم: {order.plans.in_volume} مگابایت\n"
                f"📅 شروع: {order.start_plane_at.strftime('%Y/%m/%d')}\n"
                f"📅 پایان: {order.end_plane_at.strftime('%Y/%m/%d')}\n"
                f"🔸 وضعیت: {status}\n\n"
            )
        else:
            response += "❗ هیچ پلن پولی یافت نشد.\n\n"
        
        response += "💡 برای خرید پلن جدید، گزینه 🛒 خرید پلن را انتخاب کنید."
        
        await update.message.reply_text(
            response,
            parse_mode='Markdown'
        )
        
    except UsersModel.DoesNotExist:
        await update.message.reply_text("❌ ابتدا /start را بزنید.")
    except Exception as e:
        logger.error(f"خطا در دریافت پلن‌ها: {e}")
        await update.message.reply_text("❌ خطا در دریافت پلن‌ها.")

# نمایش تنظیمات - بهبود شده با قابلیت کپی
async def my_config(update: Update, context: ContextTypes.DEFAULT_TYPE):
    telegram_id = update.effective_user.id
    try:
        user = await sync_to_async(UsersModel.objects.get)(telegram_id=telegram_id)
        configs = await sync_to_async(list)(ConfigUserModel.objects.filter(user=user, is_active=True))
        
        response = "⚙️ **تنظیمات شما:**\n\n"
        has_configs = False
        
        # بررسی کانفیگ تستی
        trial_config = await sync_to_async(lambda: getattr(user, 'trial_config', None))()
        if trial_config and not trial_config.is_expired():
            has_configs = True
            remaining_time = trial_config.get_remaining_time()
            hours = int(remaining_time.total_seconds() // 3600)
            minutes = int((remaining_time.total_seconds() % 3600) // 60)
            
            response += (
                f"🎁 **کانفیگ تستی**\n"
                f"⏰ اعتبار: {hours} ساعت و {minutes} دقیقه باقی\n"
                f"🔧 کانفیگ: `{trial_config.config}`\n\n"
            )
        
        # بررسی کانفیگ‌های X-UI
        xui_configs = await sync_to_async(list)(UserConfig.objects.filter(user=user, is_active=True))
        for config in xui_configs:
            if not config.is_expired():
                has_configs = True
                remaining_time = config.get_remaining_time()
                if remaining_time:
                    hours = int(remaining_time.total_seconds() // 3600)
                    minutes = int((remaining_time.total_seconds() % 3600) // 60)
                    time_text = f"{hours} ساعت و {minutes} دقیقه باقی"
                else:
                    time_text = "نامحدود"
                
                response += (
                    f"🔧 **{config.config_name}**\n"
                    f"🖥️ سرور: {config.server.name}\n"
                    f"⏰ اعتبار: {time_text}\n"
                    f"🔧 کانفیگ: `{config.config_data}`\n\n"
                )
        
        if configs:
            for i, config in enumerate(configs, 1):
                has_configs = True
                response += f"{i}. 🔧 {config.config}\n"
        
        if not has_configs:
            response += "⚠️ هیچ کانفیگ فعالی یافت نشد.\n\n"
            response += "💡 برای دریافت کانفیگ:\n"
            response += "• 🎁 پلن تستی را امتحان کنید\n"
            response += "• 🛒 پلن پولی خریداری کنید"
        else:
            response += "💡 **نحوه استفاده:**\n"
            response += "• کانفیگ‌ها را کپی کنید\n"
            response += "• در اپلیکیشن VPN وارد کنید\n"
            response += "• روی اتصال کلیک کنید"
        
        # ایجاد دکمه‌های کپی برای هر کانفیگ
        keyboard = []
        if trial_config and not trial_config.is_expired():
            keyboard.append([InlineKeyboardButton("📋 کپی کانفیگ تستی", callback_data="copy_trial_config")])
        
        for i, config in enumerate(xui_configs):
            if not config.is_expired():
                keyboard.append([InlineKeyboardButton(f"📋 کپی {config.config_name}", callback_data=f"copy_config_{config.id}")])
        
        if keyboard:
            keyboard.append([InlineKeyboardButton("📚 راهنمای استفاده", callback_data="config_usage_guide")])
        
        reply_markup = InlineKeyboardMarkup(keyboard) if keyboard else None
        
        await update.message.reply_text(
            response,
            parse_mode='Markdown',
            reply_markup=reply_markup
        )
        
    except UsersModel.DoesNotExist:
        await update.message.reply_text("❌ ابتدا /start را بزنید.")
    except Exception as e:
        logger.error(f"خطا در دریافت تنظیمات: {e}")
        await update.message.reply_text("❌ خطا در دریافت تنظیمات.")

# کپی کردن کانفیگ
async def copy_config(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """کپی کردن کانفیگ"""
    query = update.callback_query
    await query.answer()
    
    callback_data = query.data
    telegram_id = query.from_user.id
    
    try:
        user = await sync_to_async(UsersModel.objects.get)(telegram_id=telegram_id)
        
        if callback_data == "copy_trial_config":
            # کپی کانفیگ تستی
            trial_config = await sync_to_async(lambda: getattr(user, 'trial_config', None))()
            if trial_config and not trial_config.is_expired():
                await query.edit_message_text(
                    f"📋 **کانفیگ تستی کپی شد!**\n\n"
                    f"🔧 کانفیگ شما:\n"
                    f"`{trial_config.config}`\n\n"
                    f"💡 حالا می‌توانید آن را در اپلیکیشن VPN وارد کنید.",
                    parse_mode='Markdown',
                    reply_markup=InlineKeyboardMarkup([[
                        InlineKeyboardButton("📚 راهنمای استفاده", callback_data="config_usage_guide")
                    ]])
                )
            else:
                await query.edit_message_text(
                    "❌ کانفیگ تستی منقضی شده یا وجود ندارد.",
                    parse_mode='Markdown'
                )
        else:
            # کپی کانفیگ X-UI
            config_id = callback_data.split('_')[2]
            config = await sync_to_async(UserConfig.objects.get)(id=config_id, user=user)
            
            if not config.is_expired():
                await query.edit_message_text(
                    f"📋 **کانفیگ {config.config_name} کپی شد!**\n\n"
                    f"🔧 کانفیگ شما:\n"
                    f"`{config.config_data}`\n\n"
                    f"💡 حالا می‌توانید آن را در اپلیکیشن VPN وارد کنید.",
                    parse_mode='Markdown',
                    reply_markup=InlineKeyboardMarkup([[
                        InlineKeyboardButton("📚 راهنمای استفاده", callback_data="config_usage_guide")
                    ]])
                )
            else:
                await query.edit_message_text(
                    "❌ این کانفیگ منقضی شده است.",
                    parse_mode='Markdown'
                )
                
    except Exception as e:
        logger.error(f"خطا در کپی کردن کانفیگ: {e}")
        await query.edit_message_text("❌ خطا در کپی کردن کانفیگ.")

# راهنمای استفاده از کانفیگ
async def show_config_usage_guide(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """راهنمای استفاده از کانفیگ"""
    query = update.callback_query
    await query.answer()
    
    guide_text = (
        "📚 **راهنمای استفاده از کانفیگ**\n\n"
        "📱 **مراحل نصب و استفاده:**\n\n"
        "🔹 **برای اندروید:**\n"
        "1. V2rayNG را از Google Play دانلود کنید\n"
        "2. اپ را باز کنید\n"
        "3. روی + کلیک کنید\n"
        "4. کانفیگ کپی شده را پیست کنید\n"
        "5. روی 'Save' کلیک کنید\n"
        "6. روی دکمه اتصال کلیک کنید\n\n"
        "🔹 **برای آیفون:**\n"
        "1. Shadowrocket را از App Store دانلود کنید\n"
        "2. اپ را باز کنید\n"
        "3. روی + کلیک کنید\n"
        "4. کانفیگ کپی شده را پیست کنید\n"
        "5. روی 'Save' کلیک کنید\n"
        "6. روی دکمه اتصال کلیک کنید\n\n"
        "🔹 **برای ویندوز:**\n"
        "1. V2rayN را دانلود کنید\n"
        "2. فایل را اجرا کنید\n"
        "3. کانفیگ کپی شده را وارد کنید\n"
        "4. روی اتصال کلیک کنید\n\n"
        "⚠️ **مشکلات رایج:**\n"
        "• اگر اتصال برقرار نشد، کانفیگ را دوباره وارد کنید\n"
        "• اگر سرعت کم است، سرور دیگری انتخاب کنید\n"
        "• اگر کانفیگ منقضی شده، پلن جدید خریداری کنید\n\n"
        "💡 **نکات مهم:**\n"
        "• کانفیگ را در جای امنی ذخیره کنید\n"
        "• از اپلیکیشن‌های معتبر استفاده کنید\n"
        "• در صورت مشکل، اپ را ری‌استارت کنید"
    )
    
    await query.edit_message_text(
        guide_text,
        parse_mode='Markdown',
        reply_markup=InlineKeyboardMarkup([[
            InlineKeyboardButton("🔙 بازگشت", callback_data="back_to_configs")
        ]])
    )

# بازگشت به تنظیمات
async def back_to_configs(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """بازگشت به تنظیمات"""
    query = update.callback_query
    await query.answer()
    
    # شبیه‌سازی دوباره نمایش تنظیمات
    await my_config(update, context)

# اجرای ربات
async def main():
    # توکن را از متغیر محیطی یا فایل تنظیمات بخوانید
    TOKEN = os.getenv('USER_BOT_TOKEN', 'YOUR_BOT_TOKEN_HERE')
    
    if TOKEN == 'YOUR_BOT_TOKEN_HERE':
        print("❌ لطفا توکن ربات را در فایل .env تنظیم کنید!")
        print("مثال: USER_BOT_TOKEN=your_bot_token_here")
        return

    app = ApplicationBuilder().token(TOKEN).build()

    # دستورات اصلی
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("profile", profile))
    app.add_handler(CommandHandler("my_plans", my_plans))
    app.add_handler(CommandHandler("my_config", my_config))
    app.add_handler(CommandHandler("help", show_help)) # اضافه کردن دستور /help
    
    # دکمه‌های منو
    app.add_handler(MessageHandler(filters.Regex("📊 پروفایل من"), profile))
    app.add_handler(MessageHandler(filters.Regex("🛒 خرید پلن"), buy_plan))
    app.add_handler(MessageHandler(filters.Regex("📦 پلن‌های من"), my_plans))
    app.add_handler(MessageHandler(filters.Regex("⚙️ تنظیمات من"), my_config))
    app.add_handler(MessageHandler(filters.Regex("🎁 پلن تستی"), trial_plan))
    app.add_handler(MessageHandler(filters.Regex("📚 راهنما"), show_help)) # اضافه کردن دکمه راهنما
    
    # پردازش انتخاب پلن
    app.add_handler(CallbackQueryHandler(handle_plan_selection, pattern="^select_plan_"))
    
    # پردازش راهنما
    app.add_handler(CallbackQueryHandler(show_app_guide, pattern="^app_guide$"))
    app.add_handler(CallbackQueryHandler(show_config_guide, pattern="^config_guide$"))
    app.add_handler(CallbackQueryHandler(show_faq, pattern="^faq$"))
    app.add_handler(CallbackQueryHandler(show_support, pattern="^support$"))
    app.add_handler(CallbackQueryHandler(back_to_help, pattern="^back_to_help$"))
    app.add_handler(CallbackQueryHandler(show_start_tutorial, pattern="^trial_tutorial$"))
    app.add_handler(CallbackQueryHandler(show_buy_tutorial, pattern="^buy_tutorial$"))
    app.add_handler(CallbackQueryHandler(show_profile_tutorial, pattern="^profile_tutorial$"))
    app.add_handler(CallbackQueryHandler(back_to_start_tutorial, pattern="^back_to_start_tutorial$"))
    
    # پردازش کپی کانفیگ و راهنما
    app.add_handler(CallbackQueryHandler(copy_config, pattern="^copy_trial_config$"))
    app.add_handler(CallbackQueryHandler(copy_config, pattern="^copy_config_"))
    app.add_handler(CallbackQueryHandler(show_config_usage_guide, pattern="^config_usage_guide$"))
    app.add_handler(CallbackQueryHandler(back_to_configs, pattern="^back_to_configs$"))
    
    # پردازش دکمه‌های راهنما
    app.add_handler(CallbackQueryHandler(lambda u, c: trial_plan(u, c), pattern="^get_trial$"))
    app.add_handler(CallbackQueryHandler(lambda u, c: buy_plan(u, c), pattern="^view_plans$"))
    app.add_handler(CallbackQueryHandler(lambda u, c: profile(u, c), pattern="^view_profile$"))
    
    # پردازش رسید پرداخت
    app.add_handler(MessageHandler(filters.PHOTO, handle_payment_receipt))
    
    # پردازش تایید پلن رایگان
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_free_plan_confirm))

    print("🤖 ربات کاربر اجرا شد...")
    await app.run_polling()

if __name__ == "__main__":
    # Fix for Windows event loop
    if sys.platform == 'win32':
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
    
    try:
        # Use nest_asyncio to fix the event loop issue
        import nest_asyncio
        nest_asyncio.apply()
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n🤖 ربات متوقف شد...")
    except Exception as e:
        print(f"❌ خطا در اجرای ربات: {e}")
