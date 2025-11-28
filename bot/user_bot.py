import os
import sys
import django
import asyncio
import datetime
from telegram import Update, ReplyKeyboardMarkup, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes, MessageHandler, CallbackQueryHandler, filters
from telegram.error import NetworkError, TimedOut
import time
from dotenv import load_dotenv
import logging
from asgiref.sync import sync_to_async
from django.utils import timezone
from datetime import timedelta

# Load environment variables
load_dotenv('config.env')

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
from xui_servers.models import XUIServer, UserConfig, XUIInbound, XUIClient
from chat_messages.models import MessageDirectory, MessageModel
from xui_servers.services import UserConfigService
from xui_servers.enhanced_api_models import (
    XUIEnhancedService,
    XUIAutoManager,
)
from django.conf import settings

# تنظیم لاگینگ
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# حالت‌های مختلف کاربر
USER_STATES = {}

# بررسی دسترسی ادمین
async def is_admin(user_id):
    """بررسی دسترسی ادمین - از دیتابیس و تنظیمات"""
    # چک کردن از تنظیمات
    ADMIN_USER_IDS = getattr(settings, 'ADMIN_USER_IDS', [])
    if user_id in ADMIN_USER_IDS:
        return True
    
    # چک کردن از دیتابیس
    try:
        user = await sync_to_async(UsersModel.objects.get)(telegram_id=user_id)
        if user.is_admin or user.is_staff:
            return True
    except UsersModel.DoesNotExist:
        pass
    except Exception as e:
        logger.error(f"خطا در بررسی دسترسی ادمین: {e}")
    
    return False

# دکمه‌های کیبورد اصلی
main_keyboard = ReplyKeyboardMarkup([
    ["🎁 پلن تستی", "🛒 خرید پلن"],
    ["📦 پلن‌های من", "ℹ️ اطلاعات من"],
    ["💬 ارتباط با ما", "🆘 پشتیبانی"]
], resize_keyboard=True)

# دکمه‌های کیبورد ادمین
admin_keyboard = ReplyKeyboardMarkup([
    ["📊 داشبورد", "🖥️ سرورها"],
    ["📦 پلن‌ها", "🔗 Inbound ها"],
    ["👤 کلاینت‌ها", "👥 کاربران"],
    ["🧹 پاکسازی", "⏰ منقضی شده"]
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
        try:
            user = await sync_to_async(UsersModel.objects.get)(telegram_id=telegram_id)
            created = False
            # به‌روزرسانی اطلاعات کاربر
            user.id_tel = str(user_data.id)
            user.username_tel = user_data.username or ""
            user.full_name = user_data.full_name or user_data.first_name or "کاربر"
            user.username = user_data.username or ""
            await sync_to_async(user.save)()
        except UsersModel.DoesNotExist:
            # ایجاد کاربر جدید
            user = await sync_to_async(UsersModel.objects.create)(
                telegram_id=telegram_id,
                id_tel=str(user_data.id),
                username_tel=user_data.username or "",
                full_name=user_data.full_name or user_data.first_name or "کاربر",
                username=user_data.username or ""
            )
            created = True
        
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
            
            # اطلاع به همه ادمین‌ها از کاربر جدید
            try:
                from telegram import Bot
                admin_bot_token = getattr(settings, 'ADMIN_BOT_TOKEN', '')
                
                if not admin_bot_token:
                    admin_bot_token = getattr(settings, 'USER_BOT_TOKEN', '')
                    logger.warning("⚠️ ADMIN_BOT_TOKEN تنظیم نشده، از USER_BOT_TOKEN استفاده می‌شود")
                
                if admin_bot_token:
                    bot = Bot(token=admin_bot_token)
                    
                    # دریافت همه ادمین‌ها
                    def get_all_admins():
                        ADMIN_USER_IDS = getattr(settings, 'ADMIN_USER_IDS', [])
                        admins = []
                        
                        # ادمین‌ها از ADMIN_USER_IDS (فقط آنهایی که telegram_id دارند)
                        if ADMIN_USER_IDS:
                            admin_users = UsersModel.objects.filter(telegram_id__in=ADMIN_USER_IDS).exclude(telegram_id__isnull=True)
                            admins.extend(admin_users)
                        
                        # ادمین‌ها از دیتابیس (فقط آنهایی که telegram_id دارند)
                        db_admins = (UsersModel.objects.filter(is_admin=True) | UsersModel.objects.filter(is_staff=True)).exclude(telegram_id__isnull=True)
                        admins.extend(db_admins)
                        
                        # حذف تکراری‌ها و فیلتر کردن ادمین‌هایی که telegram_id معتبر دارند
                        unique_admins = []
                        seen_ids = set()
                        for admin in admins:
                            # بررسی اینکه telegram_id معتبر است (نه None و نه خالی)
                            if admin.telegram_id and admin.telegram_id not in seen_ids:
                                unique_admins.append(admin)
                                seen_ids.add(admin.telegram_id)
                        
                        logger.info(f"🔍 تعداد ادمین‌های یافت شده: {len(unique_admins)}")
                        return unique_admins
                    
                    all_admins = await sync_to_async(get_all_admins)()
                    
                    # پیام اطلاع‌رسانی
                    admin_notification = (
                        f"🆕 **کاربر جدید ثبت‌نام کرد!**\n\n"
                        f"👤 **نام:** {user.full_name}\n"
                        f"🆔 **ID تلگرام:** `{telegram_id}`\n"
                        f"📱 **یوزرنیم:** @{user.username or 'بدون یوزرنیم'}\n"
                        f"📅 **تاریخ ثبت‌نام:** {timezone.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n"
                        f"✅ کاربر با موفقیت در سیستم ثبت شد."
                    )
                    
                    # ارسال به همه ادمین‌ها
                    sent_count = 0
                    for admin_user in all_admins:
                        # بررسی اینکه ادمین telegram_id معتبر دارد
                        if not admin_user.telegram_id:
                            logger.warning(f"⚠️ ادمین {admin_user.id} telegram_id ندارد، رد شد")
                            continue
                        
                        try:
                            await bot.send_message(
                                chat_id=admin_user.telegram_id,
                                text=admin_notification,
                                parse_mode='Markdown'
                            )
                            sent_count += 1
                            logger.info(f"✅ اطلاع کاربر جدید به ادمین ارسال شد: Admin ID: {admin_user.telegram_id}, User ID: {telegram_id}")
                        except Exception as e:
                            logger.error(f"❌ خطا در ارسال به ادمین {admin_user.telegram_id}: {e}")
                    
                    logger.info(f"✅ اطلاع کاربر جدید به {sent_count} ادمین ارسال شد (از {len(all_admins)} ادمین)")
            except Exception as e:
                logger.error(f"❌ خطا در اطلاع کاربر جدید به ادمین‌ها: {e}", exc_info=True)
            
        else:
            # اگر کاربر قبلی است
            trial_status = "✅ در دسترس" if user.can_get_trial() else "❌ استفاده شده"
            
            # بررسی دسترسی ادمین
            if await is_admin(telegram_id):
                welcome_message = (
                    f"🔁 خوش برگشتی {user.full_name}!\n\n"
                    f"🆔 شناسه تلگرام: {telegram_id}\n"
                    f"👤 نام: {user.full_name}\n"
                    f"📱 نام کاربری: @{user.username or 'تعریف نشده'}\n"
                    f"🎁 پلن تستی: {trial_status}\n\n"
                    f"👑 **شما دسترسی ادمین دارید!**\n\n"
                    f"💡 می‌توانید از دستورات ادمین استفاده کنید:\n"
                    f"📊 `/admin_dashboard` - داشبورد ادمین\n"
                    f"🖥️ `/admin_servers` - لیست سرورها\n"
                    f"👥 `/admin_users` - لیست کاربران\n"
                    f"📦 `/admin_plans` - لیست پلن‌ها\n"
                    f"🧹 `/admin_cleanup` - پاکسازی\n"
                    f"⏰ `/admin_check_expired` - بررسی منقضی شده‌ها"
                )
                keyboard = ReplyKeyboardMarkup([
                    ["🛒 خرید پلن", "📊 پروفایل من"],
                    ["📦 پلن‌های من", "⚙️ تنظیمات من"],
                    ["🎁 پلن تستی", "📚 راهنما"],
                    ["📊 داشبورد", "🖥️ سرورها"],
                    ["👥 کاربران", "📦 پلن‌ها"]
                ], resize_keyboard=True)
            else:
                welcome_message = (
                    f"🔁 خوش برگشتی {user.full_name}!\n\n"
                    f"🆔 شناسه تلگرام: {telegram_id}\n"
                    f"👤 نام: {user.full_name}\n"
                    f"📱 نام کاربری: @{user.username or 'تعریف نشده'}\n"
                    f"🎁 پلن تستی: {trial_status}\n\n"
                    f"💡 چه کاری می‌توانم برای شما انجام دهم؟"
                )
                keyboard = main_keyboard
            
            await update.message.reply_text(
                welcome_message,
                reply_markup=keyboard
            )
            
    except Exception as e:
        logger.error(f"خطا در ثبت‌نام: {e}")
        await update.message.reply_text("❌ خطا در ثبت‌نام. لطفا دوباره تلاش کنید.")

# نمایش پروفایل - بهبود شده
# اطلاعات من - نمایش اطلاعات کاربر
async def my_info(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """نمایش اطلاعات کاربر"""
    telegram_id = update.effective_user.id
    try:
        user = await sync_to_async(UsersModel.objects.get)(telegram_id=telegram_id)
        
        # محاسبه آمار کاربر
        total_orders_count = await sync_to_async(OrderUserModel.objects.filter(user=user).count)()
        active_orders_count = await sync_to_async(OrderUserModel.objects.filter(user=user, is_active=True).count)()
        pending_orders_count = await sync_to_async(OrderUserModel.objects.filter(user=user, is_active=False).count)()
        
        # بررسی کانفیگ‌های X-UI
        xui_configs_count = await sync_to_async(UserConfig.objects.filter(user=user, is_active=True).count)()
        
        # بررسی پلن تستی استفاده شده
        trial_used = await sync_to_async(lambda: user.has_used_trial)()
        trial_text = "✅ استفاده شده" if trial_used else "❌ استفاده نشده"
        
        # بررسی کانفیگ تستی فعال
        trial_config_active = False
        try:
            trial_configs = await sync_to_async(list)(UserConfig.objects.filter(user=user, is_active=True))
            for config in trial_configs:
                if not await sync_to_async(config.is_expired)():
                    trial_config_active = True
                    break
        except:
            pass
        
        trial_status = "🟢 فعال" if trial_config_active else "🔴 غیرفعال"
        
        info_text = (
            f"ℹ️ **اطلاعات من**\n\n"
            f"━━━━━━━━━━━━━━━━━━━━\n"
            f"👤 **اطلاعات شخصی:**\n\n"
            f"🆔 **شناسه تلگرام:** `{telegram_id}`\n"
            f"👤 **نام:** {user.full_name}\n"
            f"📱 **نام کاربری:** @{user.username or 'تعریف نشده'}\n"
            f"📅 **تاریخ عضویت:** {user.created_at.strftime('%Y/%m/%d %H:%M')}\n\n"
            f"━━━━━━━━━━━━━━━━━━━━\n"
            f"📦 **سفارشات:**\n\n"
            f"📊 **کل سفارشات:** `{total_orders_count}`\n"
            f"✅ **سفارشات فعال:** `{active_orders_count}`\n"
            f"⏳ **در انتظار تایید:** `{pending_orders_count}`\n\n"
            f"━━━━━━━━━━━━━━━━━━━━\n"
            f"🎁 **پلن تستی:**\n\n"
            f"📋 **وضعیت:** {trial_text}\n"
            f"🔧 **کانفیگ تستی:** {trial_status}\n\n"
            f"━━━━━━━━━━━━━━━━━━━━\n"
            f"🔧 **کانفیگ‌ها:**\n\n"
            f"📊 **کانفیگ‌های فعال:** `{xui_configs_count}`\n\n"
            f"💡 برای مشاهده کانفیگ‌ها از '⚙️ تنظیمات من' استفاده کنید."
        )
        
        keyboard = [
            [InlineKeyboardButton("📦 پلن‌های من", callback_data="view_my_plans")],
            [InlineKeyboardButton("⚙️ تنظیمات من", callback_data="view_my_configs")],
            [InlineKeyboardButton("🔙 بازگشت", callback_data="back_to_main")]
        ]
        
        await update.message.reply_text(
            info_text,
            parse_mode='Markdown',
            reply_markup=InlineKeyboardMarkup(keyboard)
        )
    except UsersModel.DoesNotExist:
        await update.message.reply_text("❌ ابتدا /start را بزنید.")
    except Exception as e:
        logger.error(f"خطا در دریافت اطلاعات: {e}")
        await update.message.reply_text("❌ خطا در دریافت اطلاعات.")

async def profile(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """نمایش پروفایل (برای سازگاری با کد قدیمی)"""
    await my_info(update, context)

# پلن تستی - بهبود شده با X-UI سنایی
async def trial_plan(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """دریافت پلن تستی - فقط یک بار برای هر کاربر"""
    telegram_id = update.effective_user.id
    try:
        user = await sync_to_async(UsersModel.objects.get)(telegram_id=telegram_id)
        
        # بررسی اینکه آیا کاربر قبلاً پلن تستی گرفته است
        can_get_trial = await sync_to_async(user.can_get_trial)()
        if not can_get_trial:
            # بررسی اینکه آیا پلن تستی فعال دارد
            trial_configs = await sync_to_async(list)(UserConfig.objects.filter(user=user, is_active=True))
            has_active_trial = False
            for config in trial_configs:
                if not await sync_to_async(config.is_expired)():
                    remaining_time = await sync_to_async(config.get_remaining_time)()
                    if remaining_time and remaining_time.total_seconds() > 0:
                        hours = int(remaining_time.total_seconds() // 3600)
                        minutes = int((remaining_time.total_seconds() % 3600) // 60)
                        days = int(remaining_time.total_seconds() // 86400)
                        
                        if days > 0:
                            time_text = f"{days} روز"
                        else:
                            time_text = f"{hours} ساعت و {minutes} دقیقه"
                        
                        await update.message.reply_text(
                            f"✅ **شما قبلاً پلن تستی دریافت کرده‌اید!**\n\n"
                            f"⏰ **اعتبار باقی‌مانده:** {time_text}\n\n"
                            f"💡 می‌توانید از بخش '📦 پلن‌های من' کانفیگ خود را مشاهده کنید.",
                            parse_mode='Markdown',
                            reply_markup=main_keyboard
                        )
                        has_active_trial = True
                        break
            
            if not has_active_trial:
                await update.message.reply_text(
                    "❌ **شما قبلاً از پلن تستی استفاده کرده‌اید.**\n\n"
                    "💡 برای استفاده از سرویس، لطفا یکی از پلن‌های پولی را انتخاب کنید:\n"
                    "🛒 خرید پلن",
                    parse_mode='Markdown',
                    reply_markup=main_keyboard
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
        
        # استفاده از سرویس X-UI برای ایجاد کانفیگ تستی
        try:
            from xui_servers.enhanced_api_models import XUIClientManager, XUIInboundManager
            
            # یافتن inbound مناسب
            inbound_manager = XUIInboundManager(server)
            inbound = await sync_to_async(inbound_manager.find_best_inbound)("vless")
            
            if not inbound:
                await update.message.reply_text(
                    "❌ **هیچ inbound مناسبی یافت نشد.**\n\n"
                    "لطفا با ادمین تماس بگیرید.",
                    parse_mode='Markdown'
                )
                return
            
            # ایجاد کانفیگ تستی با X-UI
            client_manager = XUIClientManager(server)
            user_config = await client_manager.create_trial_config_async(user, inbound)
            
            if user_config:
                # علامت‌گذاری استفاده از پلن تستی
                await user.mark_trial_used_async()
                
                await update.message.reply_text(
                    f"🎉 **پلن تستی شما فعال شد!**\n\n"
                    f"📋 **نام:** پلن تستی\n"
                    f"⏰ **اعتبار:** 24 ساعت\n"
                    f"📊 **حجم:** 1 GB\n"
                    f"🖥️ **سرور:** {server.name}\n"
                    f"🔧 **پروتکل:** VLESS\n\n"
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
                    "❌ **خطا در ایجاد کانفیگ تستی در X-UI.**\n\n"
                    "لطفا با ادمین تماس بگیرید.",
                    parse_mode='Markdown'
                )
        
        except Exception as e:
            logger.error(f"خطا در ایجاد کانفیگ تستی: {e}")
            await update.message.reply_text(
                f"❌ **خطا در ایجاد کانفیگ تستی:**\n\n{str(e)}",
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
        
        # دریافت پلن‌های غیرحذف شده از دیتابیس
        # SoftManager به صورت خودکار فقط is_deleted=False یا is_deleted=None را برمی‌گرداند
        def get_plans():
            try:
                # استفاده از objects که SoftManager است
                plans_list = list(ConfingPlansModel.objects.all().order_by('price'))
                logger.info(f"✅ تعداد پلن‌های یافت شده از دیتابیس: {len(plans_list)}")
                
                if plans_list:
                    for p in plans_list:
                        logger.info(f"  📦 پلن: {p.name}, ID: {p.id}, قیمت: {p.price}, is_active: {p.is_active}, is_deleted: {p.is_deleted}")
                else:
                    logger.warning("⚠️ هیچ پلنی در دیتابیس یافت نشد!")
                    # بررسی مستقیم از دیتابیس (بدون manager)
                    try:
                        from django.db import connection
                        with connection.cursor() as cursor:
                            cursor.execute("SELECT COUNT(*) FROM plan_confingplansmodel")
                            count = cursor.fetchone()[0]
                            logger.info(f"📊 تعداد کل رکوردها در جدول plan_confingplansmodel: {count}")
                    except Exception as db_error:
                        logger.error(f"خطا در بررسی مستقیم دیتابیس: {db_error}")
                
                return plans_list
            except Exception as e:
                logger.error(f"❌ خطا در دریافت پلن‌ها از دیتابیس: {e}", exc_info=True)
                return []
        
        plans = await sync_to_async(get_plans)()
        
        # لاگ نهایی
        if plans:
            logger.info(f"✅ {len(plans)} پلن برای نمایش آماده است")
        else:
            logger.error("❌ هیچ پلنی برای نمایش یافت نشد!")
        
        if not plans:
            await update.message.reply_text(
                "❌ **هیچ پلنی در دسترس نیست!**\n\n"
                "💡 لطفاً با ادمین تماس بگیرید.",
                parse_mode='Markdown',
                reply_markup=main_keyboard
            )
            return
        
        # ایجاد دکمه‌های پلن‌ها
        keyboard = []
        for plan in plans:
            try:
                # دریافت حجم به گیگابایت
                def get_traffic():
                    return plan.get_traffic_gb()
                
                traffic_gb = await sync_to_async(get_traffic)()
                price_text = "🆓 رایگان" if plan.price == 0 else f"💰 {plan.price:,} تومان"
                
                # نمایش حجم
                if traffic_gb and traffic_gb > 0:
                    volume_text = f"{traffic_gb:.2f} GB"
                else:
                    volume_text = f"{plan.in_volume:,} MB" if plan.in_volume else "نامحدود"
                
                # نمایش وضعیت پلن
                status_icon = "🟢" if plan.is_active else "🟡"
                plan_name = f"{status_icon} {plan.name}"
                
                keyboard.append([
                    InlineKeyboardButton(
                        f"{plan_name}\n{price_text} - 📊 {volume_text}",
                        callback_data=f"select_plan_{plan.id}"
                    )
                ])
            except Exception as e:
                logger.error(f"خطا در پردازش پلن {plan.id}: {e}")
                # در صورت خطا، پلن را با اطلاعات ساده نمایش می‌دهیم
                price_text = "🆓 رایگان" if plan.price == 0 else f"💰 {plan.price:,} تومان"
                keyboard.append([
                    InlineKeyboardButton(
                        f"{plan.name}\n{price_text}",
                        callback_data=f"select_plan_{plan.id}"
                    )
                ])
        
        if not keyboard:
            await update.message.reply_text(
                "❌ **هیچ پلن معتبری یافت نشد!**\n\n"
                "💡 لطفاً با ادمین تماس بگیرید.",
                parse_mode='Markdown',
                reply_markup=main_keyboard
            )
            return
        
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        # پیام با اطلاعات بیشتر
        message_text = (
            "🛒 **خرید پلن**\n\n"
            "📋 **لطفا پلن مورد نظر خود را انتخاب کنید:**\n\n"
        )
        
        # اضافه کردن توضیحات
        if len(plans) > 0:
            active_count = sum(1 for p in plans if p.is_active)
            message_text += f"📊 **تعداد پلن‌ها:** {len(plans)} ({active_count} فعال)\n\n"
        
        message_text += "💡 *پس از انتخاب، عکس فاکتور پرداخت را ارسال کنید*"
        
        await update.message.reply_text(
            message_text,
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
            # دریافت شماره کارت از تنظیمات (یا استفاده از پیش‌فرض)
            payment_card = getattr(settings, 'PAYMENT_CARD_NUMBER', '1234-5678-9012-3456')
            plan_info += (
                f"💳 **لطفا مبلغ {plan.price:,} تومان را به شماره کارت زیر واریز کنید:**\n\n"
                f"`{payment_card}`\n\n"
                f"📸 **پس از پرداخت، عکس فاکتور/رسید پرداخت را ارسال کنید.**\n\n"
                f"⚠️ **توجه:** پس از تایید ادمین، پلن شما فعال خواهد شد."
            )
            USER_STATES[telegram_id] = "WAITING_PAYMENT_RECEIPT"
            context.user_data['selected_plan_id'] = plan_id
        
        await query.edit_message_text(
            plan_info,
            parse_mode='Markdown'
        )
        
    except Exception as e:
        logger.error(f"خطا در انتخاب پلن: {e}")
        await query.edit_message_text("❌ خطا در انتخاب پلن.")

# تایید پلن رایگان - بهبود شده با X-UI سنایی
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
        
        # استفاده از سرویس X-UI برای ایجاد کانفیگ پولی
        try:
            from xui_servers.enhanced_api_models import XUIClientManager, XUIInboundManager
            
            # یافتن inbound مناسب
            inbound_manager = XUIInboundManager(server)
            inbound = await sync_to_async(inbound_manager.find_best_inbound)("vless")
            
            if not inbound:
                await update.message.reply_text(
                    "❌ **هیچ inbound مناسبی یافت نشد.**\n\n"
                    "لطفا با ادمین تماس بگیرید.",
                    parse_mode='Markdown'
                )
                return
            
            # ایجاد کانفیگ پولی با X-UI
            client_manager = XUIClientManager(server)
            user_config = await client_manager.create_user_config_async(user, plan, inbound)
            
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
                    f"🖥️ سرور: {server.name}\n"
                    f"🔧 پروتکل: VLESS\n\n"
                    f"🔧 **کانفیگ شما:**\n"
                    f"`{user_config.config_data}`",
                    parse_mode='Markdown',
                    reply_markup=main_keyboard
                )
            else:
                await update.message.reply_text(
                    "❌ **خطا در ایجاد کانفیگ در X-UI.**\n\n"
                    "لطفا با ادمین تماس بگیرید.",
                    parse_mode='Markdown'
                )
        
        except Exception as e:
            logger.error(f"خطا در ایجاد کانفیگ پولی: {e}")
            await update.message.reply_text(
                f"❌ **خطا در فعال‌سازی پلن:**\n\n{str(e)}",
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
        
        # دانلود و ذخیره عکس
        import os
        from django.core.files.base import ContentFile
        import io
        
        # ایجاد پوشه payments اگر وجود ندارد
        payments_dir = os.path.join(settings.MEDIA_ROOT, 'payments')
        os.makedirs(payments_dir, exist_ok=True)
        
        # دانلود فایل
        file_bytes = await file.download_as_bytearray()
        file_name = f"payment_{telegram_id}_{timezone.now().strftime('%Y%m%d_%H%M%S')}.jpg"
        
        # ایجاد سفارش
        order = await sync_to_async(OrderUserModel.objects.create)(
            user=user,
            plans=plan,
            is_active=False  # تا تایید ادمین فعال نمی‌شود
        )
        
        # محاسبه کد پرداخت
        def get_next_payment_code():
            last_payment = PayMentModel.objects.order_by('-code_pay').first()
            return (last_payment.code_pay + 1) if last_payment else 1
        
        payment_code = await sync_to_async(get_next_payment_code)()
        
        # ذخیره رسید پرداخت
        def create_payment():
            payment = PayMentModel(
                user=user,
                order=order,
                code_pay=payment_code,
                is_active=True,
                rejected=False
            )
            payment.images.save(file_name, ContentFile(file_bytes), save=False)
            payment.save()
            return payment
        
        payment = await sync_to_async(create_payment)()
        
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
        
        # ارسال به ادمین‌ها
        ADMIN_USER_IDS = getattr(settings, 'ADMIN_USER_IDS', [])
        admin_ids = ADMIN_USER_IDS
        
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
        
        response = "📦 **پلن‌های شما:**\n\n"
        
        # بررسی کانفیگ تستی
        try:
            trial_config = await sync_to_async(lambda: hasattr(user, 'trial_config') and user.trial_config)()
            if trial_config and not await sync_to_async(trial_config.is_expired)():
                remaining_time = await sync_to_async(trial_config.get_remaining_time)()
                hours = int(remaining_time.total_seconds() // 3600)
                minutes = int((remaining_time.total_seconds() % 3600) // 60)
                
                response += (
                    f"🎁 **پلن تستی**\n"
                    f"📊 حجم: 1GB\n"
                    f"⏰ اعتبار: {hours} ساعت و {minutes} دقیقه باقی\n\n"
                )
        except:
            pass
        
        # بررسی کانفیگ‌های X-UI
        xui_configs = await sync_to_async(list)(UserConfig.objects.filter(user=user, is_active=True))
        for config in xui_configs:
            if not await sync_to_async(config.is_expired)():
                remaining_time = await sync_to_async(config.get_remaining_time)()
                if remaining_time:
                    hours = int(remaining_time.total_seconds() // 3600)
                    minutes = int((remaining_time.total_seconds() % 3600) // 60)
                    time_text = f"{hours} ساعت و {minutes} دقیقه باقی"
                else:
                    time_text = "نامحدود"
                
                response += (
                    f"🔧 **{config.config_name}**\n"
                    f"🖥️ سرور: {config.server.name}\n"
                    f"⏰ اعتبار: {time_text}\n\n"
                )
        
        # بررسی سفارشات پولی
        orders = await sync_to_async(list)(OrderUserModel.objects.filter(user=user, is_deleted=False).order_by('-created_at'))
        if orders:
            for order in orders:
                status = "✅ فعال" if order.is_active else "⏳ در انتظار تایید"
                status_emoji = "🟢" if order.is_active else "🟡"
                
                # محاسبه زمان باقی‌مانده
                if order.is_active:
                    remaining = order.end_plane_at - timezone.now()
                    if remaining.total_seconds() > 0:
                        days = int(remaining.total_seconds() // 86400)
                        time_text = f"{days} روز باقی"
                    else:
                        time_text = "منقضی شده"
                else:
                    time_text = "در انتظار تایید"
                
                traffic_gb = await sync_to_async(order.plans.get_traffic_gb)()
                
                response += (
                    f"{status_emoji} **{order.plans.name}**\n"
                    f"💰 قیمت: `{order.plans.price:,}` تومان\n"
                    f"📊 حجم: `{traffic_gb:.2f}` GB\n"
                    f"📅 شروع: {order.start_plane_at.strftime('%Y/%m/%d')}\n"
                    f"📅 پایان: {order.end_plane_at.strftime('%Y/%m/%d')}\n"
                    f"⏰ باقی‌مانده: {time_text}\n"
                    f"🔸 وضعیت: {status}\n\n"
                )
                has_plans = True
        else:
            if not trial_used:
                response += "❗ هیچ پلنی یافت نشد.\n\n"
        
        if not has_plans:
            response += "❗ هیچ پلن فعالی ندارید.\n\n"
        
        response += "💡 برای خرید پلن جدید، گزینه 🛒 خرید پلن را انتخاب کنید."
        
        keyboard = [
            [InlineKeyboardButton("🛒 خرید پلن", callback_data="view_plans")],
            [InlineKeyboardButton("🎁 پلن تستی", callback_data="get_trial")],
            [InlineKeyboardButton("🔙 بازگشت", callback_data="back_to_main")]
        ]
        
        await update.message.reply_text(
            response,
            parse_mode='Markdown',
            reply_markup=InlineKeyboardMarkup(keyboard)
        )
        
    except UsersModel.DoesNotExist:
        await update.message.reply_text("❌ ابتدا /start را بزنید.")
    except Exception as e:
        logger.error(f"خطا در دریافت پلن‌ها: {e}")
        await update.message.reply_text("❌ خطا در دریافت پلن‌ها.")

# ارتباط با ما - ثبت تیکت
async def contact_us(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """ثبت تیکت برای ارتباط با کاربر"""
    telegram_id = update.effective_user.id
    
    try:
        user = await sync_to_async(UsersModel.objects.get)(telegram_id=telegram_id)
        
        # پیدا کردن یا ایجاد ادمین
        ADMIN_USER_IDS = getattr(settings, 'ADMIN_USER_IDS', [])
        
        # اگر ADMIN_USER_IDS خالی است، از اولین ادمین در دیتابیس استفاده می‌کنیم
        if not ADMIN_USER_IDS:
            logger.warning("ADMIN_USER_IDS خالی است، در حال جستجوی ادمین در دیتابیس...")
            # جستجوی ادمین در دیتابیس
            def find_admin():
                return UsersModel.objects.filter(is_admin=True).first() or UsersModel.objects.filter(is_staff=True).first()
            
            admin = await sync_to_async(find_admin)()
            if not admin:
                await update.message.reply_text(
                    "❌ **در حال حاضر امکان ثبت تیکت وجود ندارد!**\n\n"
                    "💡 لطفاً با ادمین تماس بگیرید.",
                    parse_mode='Markdown',
                    reply_markup=main_keyboard
                )
                logger.error("هیچ ادمینی در دیتابیس یافت نشد!")
                return
            logger.info(f"✅ ادمین از دیتابیس یافت شد: {admin.telegram_id}")
        else:
            # استفاده از ADMIN_USER_IDS
            logger.info(f"ADMIN_USER_IDS: {ADMIN_USER_IDS}")
            
            # جستجوی ادمین در دیتابیس با ADMIN_USER_IDS
            def find_admin_by_ids():
                admin_user = UsersModel.objects.filter(telegram_id__in=ADMIN_USER_IDS).first()
                if admin_user:
                    return admin_user
                # اگر ادمین در دیتابیس وجود ندارد، اولین ID را استفاده می‌کنیم و کاربر را ایجاد می‌کنیم
                if ADMIN_USER_IDS:
                    admin_id = ADMIN_USER_IDS[0]
                    # بررسی وجود کاربر
                    try:
                        admin_user = UsersModel.objects.get(telegram_id=admin_id)
                        return admin_user
                    except UsersModel.DoesNotExist:
                        # ایجاد کاربر ادمین
                        admin_user = UsersModel.objects.create(
                            telegram_id=admin_id,
                            id_tel=str(admin_id),
                            username_tel="",
                            full_name="Admin",
                            username="admin",
                            is_admin=True,
                            is_staff=True
                        )
                        logger.info(f"✅ کاربر ادمین ایجاد شد: {admin_id}")
                        return admin_user
                return None
            
            admin = await sync_to_async(find_admin_by_ids)()
            
            if not admin:
                # اگر هنوز ادمین پیدا نشد، از اولین ID استفاده می‌کنیم
                admin_id = ADMIN_USER_IDS[0]
                def create_admin_user():
                    try:
                        return UsersModel.objects.get(telegram_id=admin_id)
                    except UsersModel.DoesNotExist:
                        return UsersModel.objects.create(
                            telegram_id=admin_id,
                            id_tel=str(admin_id),
                            username_tel="",
                            full_name="Admin",
                            username="admin",
                            is_admin=True,
                            is_staff=True
                        )
                
                admin = await sync_to_async(create_admin_user)()
                logger.info(f"✅ ادمین ایجاد/یافت شد: {admin.telegram_id}")
        
        # ایجاد تیکت جدید
        ticket = await sync_to_async(MessageDirectory.objects.create)(
            admin=admin,
            user=user
        )
        
        # ذخیره ticket_id در context برای ارسال پیام‌ها
        context.user_data['active_ticket_id'] = str(ticket.id)
        USER_STATES[telegram_id] = "TICKET_ACTIVE"
        
        await update.message.reply_text(
            f"✅ **تیکت شما با موفقیت ثبت شد!**\n\n"
            f"🆔 **شماره تیکت:** `{ticket.id}`\n\n"
            f"📝 **حالا می‌توانید پیام خود را ارسال کنید:**\n"
            f"• سوال خود را بپرسید\n"
            f"• مشکل را توضیح دهید\n"
            f"• درخواست خود را مطرح کنید\n\n"
            f"💡 پیام شما به صورت خودکار برای ادمین ارسال می‌شود.",
            parse_mode='Markdown',
            reply_markup=main_keyboard
        )
        
        # اطلاع فوری به همه ادمین‌ها
        logger.info(f"🚀 شروع ارسال اطلاع تیکت به ادمین‌ها - Ticket ID: {ticket.id}")
        try:
            from telegram import Bot
            from telegram.error import TelegramError, BadRequest, Forbidden, NetworkError, TimedOut
            
            # استفاده از ADMIN_BOT_TOKEN برای ارسال به ادمین
            admin_bot_token = getattr(settings, 'ADMIN_BOT_TOKEN', '')
            logger.info(f"🔍 ADMIN_BOT_TOKEN از settings: {'موجود' if admin_bot_token else 'خالی'}")
            
            if not admin_bot_token:
                # اگر ADMIN_BOT_TOKEN تنظیم نشده، از USER_BOT_TOKEN استفاده می‌کنیم
                admin_bot_token = getattr(settings, 'USER_BOT_TOKEN', '')
                logger.warning("⚠️ ADMIN_BOT_TOKEN تنظیم نشده، از USER_BOT_TOKEN استفاده می‌شود")
            
            if not admin_bot_token:
                logger.error("❌ هیچ توکنی برای ارسال به ادمین یافت نشد!")
            else:
                logger.info(f"🔑 استفاده از توکن برای ارسال به ادمین: {admin_bot_token[:20]}...")
                bot = Bot(token=admin_bot_token)
                # تست اتصال با getMe (اختیاری)
                try:
                    def get_bot_info():
                        return bot.get_me()
                    bot_info = await sync_to_async(get_bot_info)()
                    logger.info(f"✅ اتصال به ربات برقرار شد: @{bot_info.username if bot_info else 'Unknown'}")
                except Exception as e:
                    logger.warning(f"⚠️ نتوانست اطلاعات ربات را دریافت کند (اما ادامه می‌دهد): {e}")
                
                keyboard = [
                    [
                        InlineKeyboardButton("✅ تایید و ایجاد کلاینت", callback_data=f"approve_ticket_{ticket.id}"),
                        InlineKeyboardButton("💬 پاسخ", callback_data=f"reply_ticket_{ticket.id}")
                    ],
                    [
                        InlineKeyboardButton("❌ بستن", callback_data=f"close_ticket_{ticket.id}"),
                        InlineKeyboardButton("📋 مشاهده تیکت‌ها", callback_data="admin_tickets")
                    ]
                ]
                
                # استفاده از HTML برای جلوگیری از مشکلات Markdown
                admin_message = (
                    f"💬 <b>تیکت جدید ثبت شد!</b>\n\n"
                    f"👤 <b>کاربر:</b> {user.full_name or 'بدون نام'}\n"
                    f"🆔 <b>ID:</b> <code>{user.telegram_id}</code>\n"
                    f"📱 <b>یوزرنیم:</b> @{user.username or 'بدون یوزرنیم'}\n"
                    f"🆔 <b>شماره تیکت:</b> <code>{ticket.id}</code>\n\n"
                    f"💡 منتظر پیام کاربر باشید..."
                )
                
                # ارسال به همه ادمین‌ها
                def get_all_admins():
                    ADMIN_USER_IDS = getattr(settings, 'ADMIN_USER_IDS', [])
                    admins = []
                    
                    # ادمین‌ها از ADMIN_USER_IDS (فقط آنهایی که telegram_id دارند)
                    if ADMIN_USER_IDS:
                        admin_users = UsersModel.objects.filter(telegram_id__in=ADMIN_USER_IDS).exclude(telegram_id__isnull=True)
                        admins.extend(admin_users)
                    
                    # ادمین‌ها از دیتابیس (فقط آنهایی که telegram_id دارند)
                    db_admins = (UsersModel.objects.filter(is_admin=True) | UsersModel.objects.filter(is_staff=True)).exclude(telegram_id__isnull=True)
                    admins.extend(db_admins)
                    
                    # حذف تکراری‌ها و فیلتر کردن ادمین‌هایی که telegram_id معتبر دارند
                    unique_admins = []
                    seen_ids = set()
                    for admin in admins:
                        # بررسی اینکه telegram_id معتبر است (نه None و نه خالی)
                        if admin.telegram_id and admin.telegram_id not in seen_ids:
                            unique_admins.append(admin)
                            seen_ids.add(admin.telegram_id)
                    
                    logger.info(f"🔍 تعداد ادمین‌های یافت شده: {len(unique_admins)}")
                    return unique_admins
                
                all_admins = await sync_to_async(get_all_admins)()
                logger.info(f"📊 تعداد ادمین‌های یافت شده: {len(all_admins) if all_admins else 0}")
                
                if not all_admins:
                    logger.warning("⚠️ هیچ ادمینی برای ارسال تیکت یافت نشد!")
                    logger.warning("⚠️ لطفاً ADMIN_USER_IDS را در config.env بررسی کنید!")
                else:
                    # ارسال به همه ادمین‌ها
                    sent_count = 0
                    failed_count = 0
                    logger.info(f"📤 شروع ارسال به {len(all_admins)} ادمین...")
                    for admin_user in all_admins:
                        logger.info(f"📨 در حال ارسال به ادمین: ID={admin_user.telegram_id}, Name={admin_user.full_name}")
                        # بررسی اینکه ادمین telegram_id معتبر دارد
                        if not admin_user.telegram_id:
                            logger.warning(f"⚠️ ادمین {admin_user.id} telegram_id ندارد، رد شد")
                            continue
                        
                        try:
                            # تلاش برای ارسال با HTML
                            try:
                                logger.info(f"📤 ارسال پیام به ادمین {admin_user.telegram_id}...")
                                result = await bot.send_message(
                                    chat_id=admin_user.telegram_id,
                                    text=admin_message,
                                    parse_mode='HTML',
                                    reply_markup=InlineKeyboardMarkup(keyboard)
                                )
                                sent_count += 1
                                logger.info(f"✅✅✅ اطلاع تیکت به ادمین ارسال شد: Admin ID: {admin_user.telegram_id}, Ticket ID: {ticket.id}, Message ID: {result.message_id}")
                            except BadRequest as e:
                                # اگر HTML مشکل داشت، بدون parse_mode امتحان می‌کنیم
                                logger.warning(f"⚠️ خطا در ارسال با HTML، تلاش بدون parse_mode: {e}")
                                try:
                                    admin_message_plain = (
                                        f"💬 تیکت جدید ثبت شد!\n\n"
                                        f"👤 کاربر: {user.full_name or 'بدون نام'}\n"
                                        f"🆔 ID: {user.telegram_id}\n"
                                        f"📱 یوزرنیم: @{user.username or 'بدون یوزرنیم'}\n"
                                        f"🆔 شماره تیکت: {ticket.id}\n\n"
                                        f"💡 منتظر پیام کاربر باشید..."
                                    )
                                    await bot.send_message(
                                        chat_id=admin_user.telegram_id,
                                        text=admin_message_plain,
                                        reply_markup=InlineKeyboardMarkup(keyboard)
                                    )
                                    sent_count += 1
                                    logger.info(f"✅ اطلاع تیکت به ادمین ارسال شد (بدون parse_mode): Admin ID: {admin_user.telegram_id}, Ticket ID: {ticket.id}")
                                except Exception as e2:
                                    logger.error(f"❌ خطا در ارسال به ادمین {admin_user.telegram_id} (بدون parse_mode): {e2}")
                                    failed_count += 1
                            except Forbidden as e:
                                logger.error(f"❌ ربات توسط ادمین {admin_user.telegram_id} بلاک شده است: {e}")
                                failed_count += 1
                            except (NetworkError, TimedOut) as e:
                                logger.warning(f"⚠️ خطای شبکه در ارسال به ادمین {admin_user.telegram_id}: {e}")
                                # تلاش مجدد یک بار
                                try:
                                    await asyncio.sleep(2)
                                    await bot.send_message(
                                        chat_id=admin_user.telegram_id,
                                        text=admin_message,
                                        parse_mode='HTML',
                                        reply_markup=InlineKeyboardMarkup(keyboard)
                                    )
                                    sent_count += 1
                                    logger.info(f"✅ اطلاع تیکت به ادمین ارسال شد (بعد از retry): Admin ID: {admin_user.telegram_id}, Ticket ID: {ticket.id}")
                                except Exception as e2:
                                    logger.error(f"❌ خطا در ارسال مجدد به ادمین {admin_user.telegram_id}: {e2}")
                                    failed_count += 1
                            except TelegramError as e:
                                logger.error(f"❌ خطای تلگرام در ارسال به ادمین {admin_user.telegram_id}: {e}")
                                failed_count += 1
                            except Exception as e:
                                logger.error(f"❌ خطای غیرمنتظره در ارسال به ادمین {admin_user.telegram_id}: {e}", exc_info=True)
                                failed_count += 1
                        except Exception as e:
                            logger.error(f"❌ خطای غیرمنتظره در پردازش ادمین {admin_user.telegram_id}: {e}", exc_info=True)
                            failed_count += 1
                    
                    logger.info(f"📊 نتیجه ارسال: {sent_count} موفق، {failed_count} ناموفق (از {len(all_admins)} ادمین)")
                    if sent_count == 0:
                        logger.error("❌❌❌ هیچ پیامی به ادمین ارسال نشد! لطفاً لاگ‌های بالا را بررسی کنید!")
                    else:
                        logger.info(f"✅✅✅ {sent_count} پیام با موفقیت به ادمین‌ها ارسال شد!")
        except Exception as e:
            logger.error(f"❌❌❌ خطا در اطلاع به ادمین‌ها: {e}", exc_info=True)
            logger.error(f"❌ نوع خطا: {type(e).__name__}")
            # حتی اگر ارسال به ادمین با خطا مواجه شد، تیکت ثبت شده است
        
    except UsersModel.DoesNotExist:
        await update.message.reply_text("❌ ابتدا /start را بزنید.")
    except Exception as e:
        logger.error(f"خطا در ثبت تیکت: {e}", exc_info=True)
        await update.message.reply_text("❌ خطا در ثبت تیکت. لطفا دوباره تلاش کنید.")

# پشتیبانی
async def support(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """پشتیبانی - راهنمایی و کمک"""
    support_text = (
        "🆘 **پشتیبانی**\n\n"
        "📞 **راه‌های ارتباطی:**\n\n"
        "💬 **تیکت:**\n"
        "از بخش '💬 ارتباط با ما' تیکت ثبت کنید\n\n"
        "📱 **کانال تلگرام:**\n"
        "@vpn_support_channel\n\n"
        "👥 **گروه پشتیبانی:**\n"
        "@vpn_support_group\n\n"
        "📧 **ایمیل:**\n"
        "support@vpnservice.com\n\n"
        "━━━━━━━━━━━━━━━━━━━━\n"
        "⏰ **ساعات کاری:**\n"
        "شنبه تا چهارشنبه: 9 صبح تا 6 عصر\n"
        "پنجشنبه: 9 صبح تا 1 ظهر\n\n"
        "━━━━━━━━━━━━━━━━━━━━\n"
        "💡 **قبل از تماس:**\n"
        "• راهنما را مطالعه کنید\n"
        "• سوالات متداول را بررسی کنید\n"
        "• شماره سفارش خود را آماده کنید"
    )
    
    keyboard = [
        [
            InlineKeyboardButton("💬 ثبت تیکت", callback_data="create_ticket"),
            InlineKeyboardButton("📚 راهنما", callback_data="view_help")
        ],
        [
            InlineKeyboardButton("❓ سوالات متداول", callback_data="faq"),
            InlineKeyboardButton("🔙 بازگشت", callback_data="back_to_main")
        ]
    ]
    
    await update.message.reply_text(
        support_text,
        parse_mode='Markdown',
        reply_markup=InlineKeyboardMarkup(keyboard)
    )

# پردازش پیام‌های متنی (تیکت و تایید پلن)
async def handle_text_messages(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """پردازش پیام‌های متنی برای تیکت و تایید پلن"""
    telegram_id = update.effective_user.id
    text = update.message.text
    
    # بررسی تیکت فعال
    if USER_STATES.get(telegram_id) == "TICKET_ACTIVE":
        # بستن تیکت
        if text.lower() in ['بستن تیکت', 'بستن', 'close ticket', 'close']:
            try:
                user = await sync_to_async(UsersModel.objects.get)(telegram_id=telegram_id)
                ticket = await sync_to_async(
                    MessageDirectory.objects.filter(user=user, is_deleted=False).first
                )()
                
                if ticket:
                    # حذف نرم تیکت
                    ticket.is_deleted = True
                    await sync_to_async(ticket.save)()
                    
                    del USER_STATES[telegram_id]
                    await update.message.reply_text(
                        "✅ **تیکت شما بسته شد!**\n\n"
                        "💡 برای ثبت تیکت جدید، دوباره از '💬 ارتباط با ما' استفاده کنید.",
                        parse_mode='Markdown',
                        reply_markup=main_keyboard
                    )
                else:
                    del USER_STATES[telegram_id]
                    await update.message.reply_text(
                        "✅ تیکت بسته شد.",
                        reply_markup=main_keyboard
                    )
            except Exception as e:
                logger.error(f"خطا در بستن تیکت: {e}")
                await update.message.reply_text("❌ خطا در بستن تیکت.")
        else:
            # ارسال پیام به تیکت
            try:
                user = await sync_to_async(UsersModel.objects.get)(telegram_id=telegram_id)
                
                # دریافت ticket_id از context
                ticket_id = context.user_data.get('active_ticket_id')
                logger.info(f"🔍 جستجوی تیکت برای کاربر {telegram_id}: ticket_id از context = {ticket_id}")
                
                ticket = None
                
                if ticket_id:
                    # دریافت تیکت از دیتابیس با ticket_id (UUID)
                    try:
                        import uuid
                        # تبدیل string به UUID
                        ticket_uuid = uuid.UUID(ticket_id)
                        
                        def get_ticket():
                            return MessageDirectory.objects.get(id=ticket_uuid, is_deleted=False)
                        
                        ticket = await sync_to_async(get_ticket)()
                        logger.info(f"✅ تیکت از دیتابیس یافت شد: Ticket ID = {ticket.id}")
                    except (MessageDirectory.DoesNotExist, ValueError, TypeError) as e:
                        logger.warning(f"⚠️ تیکت با ID {ticket_id} یافت نشد: {e}")
                        ticket = None
                
                # اگر تیکت پیدا نشد، از دیتابیس جستجو می‌کنیم
                if not ticket:
                    logger.info(f"🔍 جستجوی آخرین تیکت فعال برای کاربر {telegram_id}")
                    def find_ticket():
                        # جستجوی آخرین تیکت فعال (غیر حذف شده) برای این کاربر
                        return MessageDirectory.objects.filter(
                            user=user, 
                            is_deleted=False
                        ).order_by('-created_at').first()
                    
                    ticket = await sync_to_async(find_ticket)()
                    
                    if ticket:
                        ticket_id = str(ticket.id)
                        context.user_data['active_ticket_id'] = ticket_id
                        logger.info(f"✅ آخرین تیکت فعال یافت شد: Ticket ID = {ticket.id}")
                    else:
                        # اگر تیکت پیدا نشد، یک تیکت جدید ایجاد می‌کنیم
                        logger.warning(f"⚠️ هیچ تیکت فعالی یافت نشد، در حال ایجاد تیکت جدید...")
                        
                        # پیدا کردن ادمین
                        ADMIN_USER_IDS = getattr(settings, 'ADMIN_USER_IDS', [])
                        
                        def find_or_create_admin():
                            if ADMIN_USER_IDS:
                                admin_user = UsersModel.objects.filter(telegram_id__in=ADMIN_USER_IDS).first()
                                if admin_user:
                                    return admin_user
                                # ایجاد ادمین اگر وجود ندارد
                                admin_id = ADMIN_USER_IDS[0]
                                try:
                                    return UsersModel.objects.get(telegram_id=admin_id)
                                except UsersModel.DoesNotExist:
                                    return UsersModel.objects.create(
                                        telegram_id=admin_id,
                                        id_tel=str(admin_id),
                                        username_tel="",
                                        full_name="Admin",
                                        username="admin",
                                        is_admin=True,
                                        is_staff=True
                                    )
                            else:
                                return UsersModel.objects.filter(is_admin=True).first() or UsersModel.objects.filter(is_staff=True).first()
                        
                        admin = await sync_to_async(find_or_create_admin)()
                        
                        if admin:
                            # ایجاد تیکت جدید
                            ticket = await sync_to_async(MessageDirectory.objects.create)(
                                admin=admin,
                                user=user
                            )
                            ticket_id = str(ticket.id)
                            context.user_data['active_ticket_id'] = ticket_id
                            logger.info(f"✅ تیکت جدید ایجاد شد: Ticket ID = {ticket.id}")
                        else:
                            # اگر ادمین پیدا نشد
                            del USER_STATES[telegram_id]
                            context.user_data.pop('active_ticket_id', None)
                            await update.message.reply_text(
                                "❌ **خطا در ایجاد تیکت!**\n\n"
                                "💡 لطفاً دوباره '💬 ارتباط با ما' را انتخاب کنید.",
                                parse_mode='Markdown',
                                reply_markup=main_keyboard
                            )
                            return
                
                # اطمینان از اینکه ticket موجود است
                if not ticket:
                    del USER_STATES[telegram_id]
                    context.user_data.pop('active_ticket_id', None)
                    await update.message.reply_text(
                        "❌ **خطا در یافتن تیکت!**\n\n"
                        "💡 لطفاً دوباره '💬 ارتباط با ما' را انتخاب کنید.",
                        parse_mode='Markdown',
                        reply_markup=main_keyboard
                    )
                    return
                
                # ذخیره پیام در دیتابیس
                def save_message():
                    return MessageModel.objects.create(
                        directory=ticket,
                        messages=text
                    )
                
                message = await sync_to_async(save_message)()
                logger.info(f"✅ پیام کاربر در دیتابیس ذخیره شد: Message ID: {message.id}, Ticket ID: {ticket.id}")
                
                # ارسال فوری به همه ادمین‌ها
                try:
                    from telegram import Bot
                    from telegram.error import TelegramError, BadRequest, Forbidden, NetworkError, TimedOut
                    
                    # استفاده از ADMIN_BOT_TOKEN برای ارسال به ادمین
                    admin_bot_token = getattr(settings, 'ADMIN_BOT_TOKEN', '')
                    
                    if not admin_bot_token:
                        # اگر ADMIN_BOT_TOKEN تنظیم نشده، از USER_BOT_TOKEN استفاده می‌کنیم
                        admin_bot_token = getattr(settings, 'USER_BOT_TOKEN', '')
                        logger.warning("⚠️ ADMIN_BOT_TOKEN تنظیم نشده، از USER_BOT_TOKEN استفاده می‌شود")
                    
                    if not admin_bot_token:
                        logger.error("❌ هیچ توکنی برای ارسال به ادمین یافت نشد!")
                    else:
                        logger.info(f"🔑 استفاده از توکن برای ارسال پیام تیکت: {admin_bot_token[:20]}...")
                        bot = Bot(token=admin_bot_token)
                        
                        keyboard = [
                            [
                                InlineKeyboardButton("✅ تایید و ایجاد کلاینت", callback_data=f"approve_ticket_{ticket.id}"),
                                InlineKeyboardButton("💬 پاسخ", callback_data=f"reply_ticket_{ticket.id}")
                            ],
                            [
                                InlineKeyboardButton("❌ بستن", callback_data=f"close_ticket_{ticket.id}"),
                                InlineKeyboardButton("📋 مشاهده تیکت‌ها", callback_data="admin_tickets")
                            ]
                        ]
                        
                        # استفاده از HTML برای جلوگیری از مشکلات Markdown
                        # فرار کردن کاراکترهای خاص در متن کاربر
                        text_escaped = text.replace('<', '&lt;').replace('>', '&gt;').replace('&', '&amp;')
                        
                        admin_message = (
                            f"💬 <b>پیام جدید در تیکت #{ticket.id}</b>\n\n"
                            f"👤 <b>کاربر:</b> {user.full_name or 'بدون نام'}\n"
                            f"🆔 <b>ID:</b> <code>{user.telegram_id}</code>\n"
                            f"📱 <b>یوزرنیم:</b> @{user.username or 'بدون یوزرنیم'}\n\n"
                            f"📝 <b>پیام:</b>\n{text_escaped}\n\n"
                            f"🆔 <b>Message ID:</b> <code>{message.id}</code>"
                        )
                        
                        # ارسال به همه ادمین‌ها
                        def get_all_admins():
                            ADMIN_USER_IDS = getattr(settings, 'ADMIN_USER_IDS', [])
                            admins = []
                            
                            # ادمین‌ها از ADMIN_USER_IDS (فقط آنهایی که telegram_id دارند)
                            if ADMIN_USER_IDS:
                                admin_users = UsersModel.objects.filter(telegram_id__in=ADMIN_USER_IDS).exclude(telegram_id__isnull=True)
                                admins.extend(admin_users)
                            
                            # ادمین‌ها از دیتابیس (فقط آنهایی که telegram_id دارند)
                            db_admins = (UsersModel.objects.filter(is_admin=True) | UsersModel.objects.filter(is_staff=True)).exclude(telegram_id__isnull=True)
                            admins.extend(db_admins)
                            
                            # حذف تکراری‌ها و فیلتر کردن ادمین‌هایی که telegram_id معتبر دارند
                            unique_admins = []
                            seen_ids = set()
                            for admin in admins:
                                # بررسی اینکه telegram_id معتبر است (نه None و نه خالی)
                                if admin.telegram_id and admin.telegram_id not in seen_ids:
                                    unique_admins.append(admin)
                                    seen_ids.add(admin.telegram_id)
                            
                            logger.info(f"🔍 تعداد ادمین‌های یافت شده: {len(unique_admins)}")
                            return unique_admins
                        
                        all_admins = await sync_to_async(get_all_admins)()
                        
                        if not all_admins:
                            logger.warning("⚠️ هیچ ادمینی برای ارسال پیام تیکت یافت نشد!")
                        else:
                            # ارسال به همه ادمین‌ها
                            sent_count = 0
                            failed_count = 0
                            for admin_user in all_admins:
                                # بررسی اینکه ادمین telegram_id معتبر دارد
                                if not admin_user.telegram_id:
                                    logger.warning(f"⚠️ ادمین {admin_user.id} telegram_id ندارد، رد شد")
                                    continue
                                
                                try:
                                    # تلاش برای ارسال با HTML
                                    try:
                                        await bot.send_message(
                                            chat_id=admin_user.telegram_id,
                                            text=admin_message,
                                            parse_mode='HTML',
                                            reply_markup=InlineKeyboardMarkup(keyboard)
                                        )
                                        sent_count += 1
                                        logger.info(f"✅ پیام به ادمین ارسال شد: Admin ID: {admin_user.telegram_id}, Ticket ID: {ticket.id}, Message ID: {message.id}")
                                    except BadRequest as e:
                                        # اگر HTML مشکل داشت، بدون parse_mode امتحان می‌کنیم
                                        logger.warning(f"⚠️ خطا در ارسال با HTML، تلاش بدون parse_mode: {e}")
                                        try:
                                            admin_message_plain = (
                                                f"💬 پیام جدید در تیکت #{ticket.id}\n\n"
                                                f"👤 کاربر: {user.full_name or 'بدون نام'}\n"
                                                f"🆔 ID: {user.telegram_id}\n"
                                                f"📱 یوزرنیم: @{user.username or 'بدون یوزرنیم'}\n\n"
                                                f"📝 پیام:\n{text}\n\n"
                                                f"🆔 Message ID: {message.id}"
                                            )
                                            await bot.send_message(
                                                chat_id=admin_user.telegram_id,
                                                text=admin_message_plain,
                                                reply_markup=InlineKeyboardMarkup(keyboard)
                                            )
                                            sent_count += 1
                                            logger.info(f"✅ پیام به ادمین ارسال شد (بدون parse_mode): Admin ID: {admin_user.telegram_id}, Ticket ID: {ticket.id}, Message ID: {message.id}")
                                        except Exception as e2:
                                            logger.error(f"❌ خطا در ارسال به ادمین {admin_user.telegram_id} (بدون parse_mode): {e2}")
                                            failed_count += 1
                                    except Forbidden as e:
                                        logger.error(f"❌ ربات توسط ادمین {admin_user.telegram_id} بلاک شده است: {e}")
                                        failed_count += 1
                                    except (NetworkError, TimedOut) as e:
                                        logger.warning(f"⚠️ خطای شبکه در ارسال به ادمین {admin_user.telegram_id}: {e}")
                                        # تلاش مجدد یک بار
                                        try:
                                            await asyncio.sleep(2)
                                            await bot.send_message(
                                                chat_id=admin_user.telegram_id,
                                                text=admin_message,
                                                parse_mode='HTML',
                                                reply_markup=InlineKeyboardMarkup(keyboard)
                                            )
                                            sent_count += 1
                                            logger.info(f"✅ پیام به ادمین ارسال شد (بعد از retry): Admin ID: {admin_user.telegram_id}, Ticket ID: {ticket.id}, Message ID: {message.id}")
                                        except Exception as e2:
                                            logger.error(f"❌ خطا در ارسال مجدد به ادمین {admin_user.telegram_id}: {e2}")
                                            failed_count += 1
                                    except TelegramError as e:
                                        logger.error(f"❌ خطای تلگرام در ارسال به ادمین {admin_user.telegram_id}: {e}")
                                        failed_count += 1
                                    except Exception as e:
                                        logger.error(f"❌ خطای غیرمنتظره در ارسال به ادمین {admin_user.telegram_id}: {e}", exc_info=True)
                                        failed_count += 1
                                except Exception as e:
                                    logger.error(f"❌ خطای غیرمنتظره در پردازش ادمین {admin_user.telegram_id}: {e}", exc_info=True)
                                    failed_count += 1
                            
                            logger.info(f"✅ پیام تیکت: {sent_count} موفق، {failed_count} ناموفق (از {len(all_admins)} ادمین)")
                except Exception as e:
                    logger.error(f"❌ خطا در ارسال پیام به ادمین‌ها: {e}", exc_info=True)
                    # حتی اگر ارسال به ادمین با خطا مواجه شد، پیام در دیتابیس ذخیره شده است
                
                # بستن state تیکت (کاربر می‌تواند دوباره تیکت جدید ثبت کند)
                del USER_STATES[telegram_id]
                context.user_data.pop('active_ticket_id', None)
                
                await update.message.reply_text(
                    "✅ **پیام شما با موفقیت ارسال شد!**\n\n"
                    "📝 پیام شما در دیتابیس ذخیره شد و برای ادمین ارسال شد.\n\n"
                    "💡 ادمین در اسرع وقت پاسخ خواهد داد.\n\n"
                    "💬 برای ارسال پیام جدید، دوباره '💬 ارتباط با ما' را انتخاب کنید.",
                    parse_mode='Markdown',
                    reply_markup=main_keyboard
                )
                
            except Exception as e:
                logger.error(f"❌ خطا در پردازش پیام تیکت: {e}", exc_info=True)
                await update.message.reply_text("❌ خطا در ارسال پیام. لطفا دوباره تلاش کنید.")
        return
    
    # پردازش تایید پلن رایگان
    if USER_STATES.get(telegram_id) == "FREE_PLAN_CONFIRM":
        await handle_free_plan_confirm(update, context)
        return

# بازگشت به منوی اصلی
async def back_to_main_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """بازگشت به منوی اصلی"""
    query = update.callback_query
    if query:
        await query.answer()
        await query.edit_message_text(
            "🏠 **منوی اصلی**\n\n"
            "لطفاً یکی از گزینه‌های زیر را انتخاب کنید:",
            parse_mode='Markdown'
        )
    else:
        await update.message.reply_text(
            "🏠 **منوی اصلی**\n\n"
            "لطفاً یکی از گزینه‌های زیر را انتخاب کنید:",
            parse_mode='Markdown',
            reply_markup=main_keyboard
        )

# نمایش تنظیمات - بهبود شده با قابلیت کپی
async def my_config(update: Update, context: ContextTypes.DEFAULT_TYPE):
    telegram_id = update.effective_user.id
    try:
        user = await sync_to_async(UsersModel.objects.get)(telegram_id=telegram_id)
        configs = await sync_to_async(list)(ConfigUserModel.objects.filter(user=user, is_active=True))
        
        response = "⚙️ **تنظیمات شما:**\n\n"
        has_configs = False
        
        # بررسی کانفیگ تستی
        try:
            trial_config = await sync_to_async(lambda: hasattr(user, 'trial_config') and user.trial_config)()
            if trial_config and not await sync_to_async(trial_config.is_expired)():
                has_configs = True
                remaining_time = await sync_to_async(trial_config.get_remaining_time)()
                hours = int(remaining_time.total_seconds() // 3600)
                minutes = int((remaining_time.total_seconds() % 3600) // 60)
                
                response += (
                    f"🎁 **کانفیگ تستی**\n"
                    f"⏰ اعتبار: {hours} ساعت و {minutes} دقیقه باقی\n\n"
                )
        except:
            pass
        
        # بررسی کانفیگ‌های X-UI
        xui_configs = await sync_to_async(list)(UserConfig.objects.filter(user=user, is_active=True))
        for config in xui_configs:
            if not await sync_to_async(config.is_expired)():
                has_configs = True
                remaining_time = await sync_to_async(config.get_remaining_time)()
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
                    f"📋 کپی کنید: /copy_{config.id}\n\n"
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

# ========================================
# دستورات ادمین در ربات کاربر
# ========================================

async def admin_dashboard(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """داشبورد ادمین"""
    user_id = update.effective_user.id
    
    if not await is_admin(user_id):
        await update.message.reply_text("❌ شما دسترسی ادمین ندارید!")
        return
    
    try:
        # آمار کلی - استفاده از sync_to_async
        servers_count = await sync_to_async(XUIServer.objects.filter(is_active=True).count)()
        inbounds_count = await sync_to_async(XUIInbound.objects.filter(is_active=True).count)()
        clients_count = await sync_to_async(XUIClient.objects.filter(is_active=True).count)()
        users_count = await sync_to_async(UsersModel.objects.count)()
        configs_count = await sync_to_async(UserConfig.objects.filter(is_active=True).count)()
        
        # آمار کاربران منقضی شده
        expired_configs = await sync_to_async(
            lambda: UserConfig.objects.filter(
                is_active=True,
                expires_at__lt=timezone.now()
            ).count()
        )()
        
        # آمار سرورها
        server_stats = []
        servers = await sync_to_async(list)(XUIServer.objects.filter(is_active=True))
        for server in servers:
            inbounds = await sync_to_async(list)(server.inbounds.filter(is_active=True))
            total_clients = 0
            for inbound in inbounds:
                clients_count_inbound = await sync_to_async(inbound.clients.count)()
                total_clients += clients_count_inbound
            inbounds_count_server = len(inbounds)
            server_stats.append(f"• {server.name}: {inbounds_count_server} inbound, {total_clients} کلاینت")
        
        stats_text = "\n".join(server_stats) if server_stats else "هیچ سروری یافت نشد"
        
        await update.message.reply_text(
            f"📊 **داشبورد ادمین**\n\n"
            f"🖥️ **سرورها:** {servers_count}\n"
            f"🔗 **Inbound ها:** {inbounds_count}\n"
            f"👤 **کلاینت‌ها:** {clients_count}\n"
            f"👥 **کاربران:** {users_count}\n"
            f"📋 **کانفیگ‌ها:** {configs_count}\n"
            f"⏰ **منقضی شده:** {expired_configs}\n\n"
            f"📈 **آمار سرورها:**\n{stats_text}",
            parse_mode='Markdown',
            reply_markup=admin_keyboard
        )
        
    except Exception as e:
        await update.message.reply_text(f"❌ خطا در دریافت آمار: {e}")

async def admin_servers(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """لیست سرورها"""
    user_id = update.effective_user.id
    
    if not is_admin(user_id):
        await update.message.reply_text("❌ شما دسترسی ادمین ندارید!")
        return
    
    try:
        servers = await sync_to_async(list)(XUIServer.objects.filter(is_active=True))
        
        if not servers:
            await update.message.reply_text("❌ هیچ سرور فعالی یافت نشد!")
            return
        
        message = "🖥️ **لیست سرورها:**\n\n"
        
        for server in servers:
            inbounds = await sync_to_async(list)(server.inbounds.filter(is_active=True))
            inbounds_count = len(inbounds)
            total_clients = 0
            for inbound in inbounds:
                clients_count_inbound = await sync_to_async(inbound.clients.count)()
                total_clients += clients_count_inbound
            
            status = "🟢 فعال" if server.is_active else "🔴 غیرفعال"
            
            message += (
                f"**{server.name}**\n"
                f"📍 {server.host}:{server.port}\n"
                f"📊 {inbounds_count} inbound, {total_clients} کلاینت\n"
                f"🔧 {status}\n\n"
            )
        
        await update.message.reply_text(message, parse_mode='Markdown')
        
    except Exception as e:
        await update.message.reply_text(f"❌ خطا در دریافت سرورها: {e}")

async def admin_users(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """لیست کاربران"""
    user_id = update.effective_user.id
    
    if not is_admin(user_id):
        await update.message.reply_text("❌ شما دسترسی ادمین ندارید!")
        return
    
    try:
        users = await sync_to_async(list)(UsersModel.objects.all())
        
        if not users:
            await update.message.reply_text("❌ هیچ کاربری یافت نشد!")
            return
        
        message = "👥 **لیست کاربران:**\n\n"
        
        for user in users:
            configs_count = await sync_to_async(user.xui_configs.filter(is_active=True).count)()
            trial_status = "✅ استفاده شده" if user.has_used_trial else "❌ استفاده نشده"
            status = "🟢 فعال" if user.is_active else "🔴 غیرفعال"
            
            message += (
                f"**{user.full_name}**\n"
                f"🆔 ID تلگرام: {user.telegram_id or 'نامشخص'}\n"
                f"📋 کانفیگ‌ها: {configs_count}\n"
                f"🎁 پلن تستی: {trial_status}\n"
                f"🔧 {status}\n\n"
            )
        
        await update.message.reply_text(message, parse_mode='Markdown')
        
    except Exception as e:
        await update.message.reply_text(f"❌ خطا در دریافت کاربران: {e}")

async def admin_plans(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """لیست پلن‌ها"""
    user_id = update.effective_user.id
    
    if not is_admin(user_id):
        await update.message.reply_text("❌ شما دسترسی ادمین ندارید!")
        return
    
    try:
        # دریافت همه پلن‌های غیرحذف شده (مثل بات ادمین)
        plans = await sync_to_async(list)(ConfingPlansModel.objects.filter(is_deleted=False).order_by('-created_at'))

        if not plans:
            await update.message.reply_text(
                "📦 **مدیریت پلن‌ها**\n\n"
                "⚠️ هیچ پلنی یافت نشد!",
                parse_mode='Markdown'
            )
            return

        message_lines = ["📦 **لیست پلن‌ها:**\n\n"]
        for i, plan in enumerate(plans, 1):
            traffic_gb = await sync_to_async(plan.get_traffic_gb)()
            status_emoji = "🟢" if plan.is_active else "🔴"
            message_lines.append(
                f"{status_emoji} **{i}. {plan.name}**\n"
                f"   💰 قیمت: `{plan.price:,}` تومان\n"
                f"   📶 حجم: `{traffic_gb:.2f}` GB\n"
                f"   📊 حجم (MB): `{plan.in_volume:,}` MB\n"
                f"   🔧 وضعیت: {'فعال' if plan.is_active else 'غیرفعال'}\n"
            )
            if plan.description:
                message_lines.append(f"   📝 {plan.description[:50]}...\n")
            message_lines.append("\n")

        await update.message.reply_text(
            "\n".join(message_lines),
            parse_mode='Markdown'
        )

    except Exception as e:
        logger.error(f"خطا در دریافت پلن‌ها: {e}")
        await update.message.reply_text(f"❌ خطا در دریافت پلن‌ها: {e}")

async def admin_cleanup(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """پاکسازی خودکار"""
    user_id = update.effective_user.id
    
    if not is_admin(user_id):
        await update.message.reply_text("❌ شما دسترسی ادمین ندارید!")
        return
    
    try:
        await update.message.reply_text("🧹 **شروع پاکسازی خودکار...**")
        
        total_cleaned = 0
        servers = await sync_to_async(list)(XUIServer.objects.filter(is_active=True))
        for server in servers:
            try:
                auto_manager = XUIAutoManager(server)
                results = await sync_to_async(auto_manager.run_cleanup)()
                
                if results['total_cleaned'] > 0:
                    await update.message.reply_text(
                        f"✅ سرور {server.name}:\n"
                        f"  • کاربران منقضی شده: {results['expired_users']}\n"
                        f"  • محدودیت ترافیک: {results['traffic_exceeded']}\n"
                        f"  • کل پاکسازی شده: {results['total_cleaned']}"
                    )
                    total_cleaned += results['total_cleaned']
                
            except Exception as e:
                await update.message.reply_text(
                    f"❌ خطا در پاکسازی سرور {server.name}: {e}"
                )
        
        if total_cleaned > 0:
            await update.message.reply_text(
                f"✅ **پاکسازی خودکار کامل شد!**\n\n"
                f"📊 تعداد کل پاکسازی شده: {total_cleaned}",
                parse_mode='Markdown'
            )
        else:
            await update.message.reply_text(
                "✅ **پاکسازی خودکار کامل شد!**\n\n"
                "📊 هیچ کاربری برای پاکسازی یافت نشد.",
                parse_mode='Markdown'
            )
        
    except Exception as e:
        await update.message.reply_text(f"❌ خطا در پاکسازی خودکار: {e}")

async def admin_check_expired(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """بررسی کاربران منقضی شده"""
    user_id = update.effective_user.id
    
    if not is_admin(user_id):
        await update.message.reply_text("❌ شما دسترسی ادمین ندارید!")
        return
    
    try:
        # بررسی کانفیگ‌های منقضی شده
        expired_configs = await sync_to_async(list)(
            UserConfig.objects.filter(
                is_active=True,
                expires_at__lt=timezone.now()
            )[:10]
        )
        
        if not expired_configs:
            await update.message.reply_text(
                "✅ **بررسی کاربران منقضی شده**\n\n"
                "📊 هیچ کانفیگ منقضی شده‌ای یافت نشد.",
                parse_mode='Markdown'
            )
            return
        
        total_expired_count = await sync_to_async(
            lambda: UserConfig.objects.filter(
                is_active=True,
                expires_at__lt=timezone.now()
            ).count()
        )()
        
        message = "⏰ **کانفیگ‌های منقضی شده:**\n\n"
        
        for config in expired_configs:
            days_expired = (timezone.now() - config.expires_at).days
            message += (
                f"**{config.config_name}**\n"
                f"👤 کاربر: {config.user.full_name}\n"
                f"🖥️ سرور: {config.server.name}\n"
                f"📅 منقضی شده: {days_expired} روز پیش\n\n"
            )
        
        if total_expired_count > 10:
            message += f"... و {total_expired_count - 10} مورد دیگر\n\n"
        
        message += f"💡 برای پاکسازی از دستور `/admin_cleanup` استفاده کنید."
        
        await update.message.reply_text(message, parse_mode='Markdown')
        
    except Exception as e:
        await update.message.reply_text(f"❌ خطا در بررسی کاربران منقضی شده: {e}")

# اجرای ربات
async def main():
    # توکن را از Django settings بخوانید
    from django.conf import settings
    TOKEN = getattr(settings, 'USER_BOT_TOKEN', None)
    
    if not TOKEN or TOKEN == 'YOUR_BOT_TOKEN_HERE':
        print("[ERROR] لطفا توکن ربات را در فایل config.env تنظیم کنید!")
        print("مثال: USER_BOT_TOKEN=your_bot_token_here")
        return

    app = ApplicationBuilder().token(TOKEN).build()

    # دستورات اصلی
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("profile", profile))
    app.add_handler(CommandHandler("my_plans", my_plans))
    app.add_handler(CommandHandler("my_config", my_config))
    app.add_handler(CommandHandler("help", show_help)) # اضافه کردن دستور /help
    
    # دستورات ادمین
    app.add_handler(CommandHandler("admin_dashboard", admin_dashboard))
    app.add_handler(CommandHandler("admin_servers", admin_servers))
    app.add_handler(CommandHandler("admin_users", admin_users))
    app.add_handler(CommandHandler("admin_plans", admin_plans))
    app.add_handler(CommandHandler("admin_cleanup", admin_cleanup))
    app.add_handler(CommandHandler("admin_check_expired", admin_check_expired))
    
    # دکمه‌های ادمین
    app.add_handler(MessageHandler(filters.Regex("📊 داشبورد"), admin_dashboard))
    app.add_handler(MessageHandler(filters.Regex("🖥️ سرورها"), admin_servers))
    app.add_handler(MessageHandler(filters.Regex("👥 کاربران"), admin_users))
    app.add_handler(MessageHandler(filters.Regex("📦 پلن‌ها"), admin_plans))
    
    # دکمه‌های منو اصلی
    app.add_handler(MessageHandler(filters.Regex("🎁 پلن تستی"), trial_plan))
    app.add_handler(MessageHandler(filters.Regex("🛒 خرید پلن"), buy_plan))
    app.add_handler(MessageHandler(filters.Regex("📦 پلن‌های من"), my_plans))
    app.add_handler(MessageHandler(filters.Regex("ℹ️ اطلاعات من"), my_info))
    app.add_handler(MessageHandler(filters.Regex("💬 ارتباط با ما"), contact_us))
    app.add_handler(MessageHandler(filters.Regex("🆘 پشتیبانی"), support))
    
    # دکمه‌های قدیمی برای سازگاری
    app.add_handler(MessageHandler(filters.Regex("📊 پروفایل من"), my_info))
    app.add_handler(MessageHandler(filters.Regex("⚙️ تنظیمات من"), my_config))
    app.add_handler(MessageHandler(filters.Regex("📚 راهنما"), show_help))
    
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
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_text_messages))
    
    # پردازش callback های جدید
    app.add_handler(CallbackQueryHandler(lambda u, c: my_plans(u, c), pattern="^view_my_plans$"))
    app.add_handler(CallbackQueryHandler(lambda u, c: my_config(u, c), pattern="^view_my_configs$"))
    app.add_handler(CallbackQueryHandler(lambda u, c: contact_us(u, c), pattern="^create_ticket$"))
    app.add_handler(CallbackQueryHandler(lambda u, c: show_help(u, c), pattern="^view_help$"))
    app.add_handler(CallbackQueryHandler(back_to_main_menu, pattern="^back_to_main$"))

    print("[*] ربات کاربر در حال اجرا...")
    
    # تنظیمات retry برای خطاهای شبکه
    retry_count = 0
    max_retries = 5
    retry_delay = 5  # ثانیه
    
    while retry_count < max_retries:
        try:
            # برای Python 3.14 از start و start_polling استفاده می‌کنیم
            # این روش event loop conflict ندارد
            await app.initialize()
            await app.start()
            await app.updater.start_polling(
                drop_pending_updates=True,
                poll_interval=1.0,
                timeout=10,
                bootstrap_retries=3
            )
            
            retry_count = 0  # reset retry count on success
            
            # نگه داشتن ربات فعال تا Ctrl+C
            try:
                # ایجاد یک event برای نگه داشتن برنامه
                stop_event = asyncio.Event()
                await stop_event.wait()  # منتظر ماندن تا Ctrl+C
            except KeyboardInterrupt:
                pass
            finally:
                # توقف ربات
                await app.updater.stop()
                await app.stop()
                await app.shutdown()
                break
                
        except (NetworkError, TimedOut) as e:
            retry_count += 1
            logger.warning(f"⚠️ خطای شبکه (تلاش {retry_count}/{max_retries}): {e}")
            
            if retry_count < max_retries:
                logger.info(f"⏳ منتظر {retry_delay} ثانیه قبل از تلاش مجدد...")
                await asyncio.sleep(retry_delay)
                retry_delay *= 2  # exponential backoff
            else:
                logger.error("❌ تعداد تلاش‌های مجدد به پایان رسید. ربات متوقف می‌شود.")
                raise
                
        except Exception as e:
            logger.error(f"❌ خطای غیرمنتظره: {e}")
            raise

if __name__ == "__main__":
    try:
        # برای Python 3.14+ از asyncio.run استفاده می‌کنیم
        # که خودش event loop را مدیریت می‌کند
        import asyncio
        
        # اجرای مستقیم main function
        # asyncio.run خودش event loop ایجاد می‌کند و مدیریت می‌کند
        asyncio.run(main())
                
    except KeyboardInterrupt:
        print("\n[*] ربات متوقف شد...")
    except Exception as e:
        print(f"[ERROR] خطا در اجرای ربات: {e}")
        import traceback
        traceback.print_exc()
