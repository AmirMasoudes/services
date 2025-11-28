#!/usr/bin/env python3
"""
ربات ادمین برای مدیریت X-UI
"""

import os
import sys
import django
import logging
import io
from datetime import datetime, timedelta
from django.utils import timezone
try:
    import qrcode
    from PIL import Image
    QRCODE_AVAILABLE = True
except ImportError:
    QRCODE_AVAILABLE = False
    # این فقط یک اطلاع است، نه خطا - کانفیگ متنی ارسال می‌شود
    pass

# اطمینان از اضافه شدن ریشه پروژه به مسیر پایتون
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

# تنظیم Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from telegram import (
    Update,
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    ReplyKeyboardMarkup,
    KeyboardButton,
    Message,
)
from telegram.ext import Application, CommandHandler, MessageHandler, CallbackQueryHandler, ContextTypes, filters
from telegram.error import NetworkError, TimedOut
import time
from django.conf import settings
from asgiref.sync import sync_to_async
from xui_servers.models import XUIServer, XUIInbound, XUIClient, UserConfig
from accounts.models import UsersModel
from plan.models import ConfingPlansModel
from order.models import PayMentModel, OrderUserModel
from chat_messages.models import MessageDirectory, MessageModel
from xui_servers.services import XUIService, UserConfigService
from xui_servers.enhanced_api_models import (
    XUIEnhancedService,
    XUIClientManager,
    XUIInboundManager,
    XUIAutoManager,
)

# تنظیم لاگینگ
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# تنظیمات ربات ادمین
ADMIN_BOT_TOKEN = getattr(settings, 'ADMIN_BOT_TOKEN', 'YOUR_ADMIN_BOT_TOKEN')
ADMIN_USER_IDS = getattr(settings, 'ADMIN_USER_IDS', [])  # ID های ادمین

class AdminBot:
    def __init__(self):
        logger.info(f"🔧 ایجاد Application با توکن: {ADMIN_BOT_TOKEN[:20]}...")
        self.application = Application.builder().token(ADMIN_BOT_TOKEN).build()
        logger.info("✅ Application ایجاد شد!")
        logger.info("🔧 تنظیم handlers...")
        self.setup_handlers()
        logger.info("✅ Handlers تنظیم شدند!")
    
    def setup_handlers(self):
        """تنظیم هندلرهای ربات"""
        # دستورات اصلی
        self.application.add_handler(CommandHandler("start", self.start_command))
        self.application.add_handler(CommandHandler("dashboard", self.dashboard_command))
        self.application.add_handler(CommandHandler("menu", self.menu_command))
        self.application.add_handler(CommandHandler("cancel", self.cancel_command))
        
        # دستورات مدیریت سرور
        self.application.add_handler(CommandHandler("servers", self.servers_command))
        self.application.add_handler(CommandHandler("inbounds", self.inbounds_command))
        self.application.add_handler(CommandHandler("clients", self.clients_command))
        self.application.add_handler(CommandHandler("users", self.users_command))
        self.application.add_handler(CommandHandler("plans", self.plans_command))
        
        # دستورات مدیریت
        self.application.add_handler(CommandHandler("add_plan", self.add_plan_command))
        self.application.add_handler(CommandHandler("add_server", self.add_server_command))
        self.application.add_handler(CommandHandler("create_inbound", self.create_inbound_command))
        self.application.add_handler(CommandHandler("assign_user", self.assign_user_command))
        self.application.add_handler(CommandHandler("sync_xui", self.sync_xui_command))
        
        # دستورات پاکسازی خودکار
        self.application.add_handler(CommandHandler("cleanup", self.cleanup_command))
        self.application.add_handler(CommandHandler("check_expired", self.check_expired_command))
        
        # دستورات مدیریت پرداخت
        self.application.add_handler(CommandHandler("payments", self.payments_command))
        
        # هندلرهای callback
        self.application.add_handler(CallbackQueryHandler(self.button_callback))
        
        # هندلر پیام‌های متنی برای پاسخ به تیکت (اولویت بالاتر)
        self.application.add_handler(MessageHandler(
            filters.TEXT & ~filters.COMMAND,
            self.handle_admin_message
        ), group=0)
        
        # هندلر پیام‌های متنی (برای سایر عملیات)
        self.application.add_handler(MessageHandler(
            filters.TEXT & ~filters.COMMAND,
            self.handle_message
        ), group=1)
        
        # هندلر برای دریافت همه پیام‌ها (برای لاگ)
        self.application.add_handler(MessageHandler(
            filters.ALL,
            self.handle_all_messages
        ), group=2)
        
        # هندلر برای دریافت همه پیام‌ها (برای لاگ و دیباگ)
        self.application.add_handler(MessageHandler(
            filters.ALL,
            self.handle_all_messages
        ), group=2)
    
    async def start_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """دستور شروع"""
        user_id = update.effective_user.id
        
        if not await self.is_admin(user_id):
            await update.message.reply_text(
                "❌ شما دسترسی ادمین ندارید!\n"
                "برای دسترسی با مدیر سیستم تماس بگیرید."
            )
            return
        
        # منوی اصلی به صورت دکمه‌ای با InlineKeyboard
        keyboard = [
            [InlineKeyboardButton("📊 داشبورد", callback_data="admin_dashboard")],
            [
                InlineKeyboardButton("🖥️ سرورها", callback_data="admin_servers"),
                InlineKeyboardButton("➕ افزودن سرور", callback_data="admin_add_server")
            ],
            [
                InlineKeyboardButton("📦 پلن‌ها", callback_data="admin_plans"),
                InlineKeyboardButton("➕ افزودن پلن", callback_data="admin_add_plan")
            ],
            [
                InlineKeyboardButton("🔗 Inbound ها", callback_data="admin_inbounds"),
                InlineKeyboardButton("➕ افزودن Inbound", callback_data="admin_add_inbound")
            ],
            [
                InlineKeyboardButton("👥 کاربران", callback_data="admin_users"),
                InlineKeyboardButton("👤 کلاینت‌ها", callback_data="admin_clients")
            ],
            [
                InlineKeyboardButton("🔄 همگام‌سازی", callback_data="admin_sync"),
                InlineKeyboardButton("🧹 پاکسازی", callback_data="admin_cleanup")
            ],
            [
                InlineKeyboardButton("⏰ بررسی منقضی شده", callback_data="admin_check_expired"),
                InlineKeyboardButton("💰 پرداخت‌ها", callback_data="admin_payments")
            ],
            [
                InlineKeyboardButton("💬 تیکت‌ها", callback_data="admin_tickets")
            ]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)

        await update.message.reply_text(
            "👑 **پنل مدیریت VPN Bot**\n\n"
            "✨ **خوش آمدید به پنل ادمین!**\n\n"
            "🎯 **دسترسی شما تایید شد** ✅\n\n"
            "📋 **دستورات سریع:**\n"
            "• `/dashboard` - مشاهده آمار کلی\n"
            "• `/add_plan` - افزودن پلن جدید\n"
            "• `/add_server` - افزودن سرور جدید\n"
            "• `/create_inbound` - ایجاد Inbound\n"
            "• `/sync_xui` - همگام‌سازی\n\n"
            "💡 **از دکمه‌های زیر استفاده کنید:**",
            parse_mode='Markdown',
            reply_markup=reply_markup,
        )

    async def menu_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """نمایش منوی دکمه‌ای ادمین"""
        user_id = update.effective_user.id

        if not await self.is_admin(user_id):
            await update.message.reply_text("❌ شما دسترسی ادمین ندارید!")
            return

        keyboard = [
            [InlineKeyboardButton("📊 داشبورد", callback_data="admin_dashboard")],
            [
                InlineKeyboardButton("🖥️ سرورها", callback_data="admin_servers"),
                InlineKeyboardButton("➕ افزودن سرور", callback_data="admin_add_server")
            ],
            [
                InlineKeyboardButton("📦 پلن‌ها", callback_data="admin_plans"),
                InlineKeyboardButton("➕ افزودن پلن", callback_data="admin_add_plan")
            ],
            [
                InlineKeyboardButton("🔗 Inbound ها", callback_data="admin_inbounds"),
                InlineKeyboardButton("➕ افزودن Inbound", callback_data="admin_add_inbound")
            ],
            [
                InlineKeyboardButton("👥 کاربران", callback_data="admin_users"),
                InlineKeyboardButton("👤 کلاینت‌ها", callback_data="admin_clients")
            ],
            [
                InlineKeyboardButton("🔄 همگام‌سازی", callback_data="admin_sync"),
                InlineKeyboardButton("🧹 پاکسازی", callback_data="admin_cleanup")
            ],
            [
                InlineKeyboardButton("⏰ بررسی منقضی شده", callback_data="admin_check_expired"),
                InlineKeyboardButton("💰 پرداخت‌ها", callback_data="admin_payments")
            ],
            [
                InlineKeyboardButton("💬 تیکت‌ها", callback_data="admin_tickets")
            ]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)

        await update.message.reply_text(
            "📋 **منوی مدیریت**\n\n"
            "✨ یکی از گزینه‌های زیر را انتخاب کنید:",
            parse_mode='Markdown',
            reply_markup=reply_markup,
        )
    
    async def dashboard_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """داشبورد کلی"""
        user_id = update.effective_user.id
        
        if not await self.is_admin(user_id):
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
            
            keyboard = [
                [
                    InlineKeyboardButton("🖥️ سرورها", callback_data="admin_servers"),
                    InlineKeyboardButton("📦 پلن‌ها", callback_data="admin_plans")
                ],
                [
                    InlineKeyboardButton("👥 کاربران", callback_data="admin_users"),
                    InlineKeyboardButton("🔗 Inbound ها", callback_data="admin_inbounds")
                ],
                [
                    InlineKeyboardButton("🔄 همگام‌سازی", callback_data="admin_sync"),
                    InlineKeyboardButton("🧹 پاکسازی", callback_data="admin_cleanup")
                ],
                [InlineKeyboardButton("🔙 بازگشت به منو", callback_data="admin_menu")]
            ]
            
            await update.message.reply_text(
                f"📊 **داشبورد مدیریت**\n\n"
                f"━━━━━━━━━━━━━━━━━━━━\n"
                f"📈 **آمار کلی:**\n\n"
                f"🖥️ **سرورها:** `{servers_count}`\n"
                f"🔗 **Inbound ها:** `{inbounds_count}`\n"
                f"👤 **کلاینت‌ها:** `{clients_count}`\n"
                f"👥 **کاربران:** `{users_count}`\n"
                f"📋 **کانفیگ‌ها:** `{configs_count}`\n"
                f"⏰ **منقضی شده:** `{expired_configs}`\n\n"
                f"━━━━━━━━━━━━━━━━━━━━\n"
                f"📊 **آمار سرورها:**\n{stats_text}",
                parse_mode='Markdown',
                reply_markup=InlineKeyboardMarkup(keyboard)
            )
            
        except Exception as e:
            await update.message.reply_text(f"❌ خطا در دریافت آمار: {e}")
    
    async def servers_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """مدیریت سرورها"""
        user_id = update.effective_user.id
        
        if not await self.is_admin(user_id):
            await update.message.reply_text("❌ شما دسترسی ادمین ندارید!")
            return
        
        try:
            servers = await sync_to_async(list)(XUIServer.objects.filter(is_deleted=False).order_by('-created_at'))
            
            if not servers:
                keyboard = [[InlineKeyboardButton("➕ افزودن سرور جدید", callback_data="admin_add_server")]]
                await update.message.reply_text(
                    "🖥️ **مدیریت سرورها**\n\n"
                    "⚠️ هیچ سروری یافت نشد!\n\n"
                    "💡 برای افزودن سرور جدید از دکمه زیر استفاده کنید:",
                    parse_mode='Markdown',
                    reply_markup=InlineKeyboardMarkup(keyboard)
                )
                return
            
            message = "🖥️ **لیست سرورها:**\n\n"
            
            for i, server in enumerate(servers, 1):
                inbounds = await sync_to_async(list)(server.inbounds.filter(is_active=True))
                inbounds_count = len(inbounds)
                total_clients = 0
                for inbound in inbounds:
                    clients_count_inbound = await sync_to_async(inbound.clients.count)()
                    total_clients += clients_count_inbound
                
                status_emoji = "🟢" if server.is_active else "🔴"
                status_text = "فعال" if server.is_active else "غیرفعال"
                
                message += (
                    f"{status_emoji} **{i}. {server.name}**\n"
                    f"   🌐 آدرس: `{server.host}:{server.port}`\n"
                    f"   👤 کاربری: `{server.username}`\n"
                    f"   📊 Inbound ها: `{inbounds_count}` | کلاینت‌ها: `{total_clients}`\n"
                    f"   🔧 وضعیت: {status_text}\n\n"
                )
            
            keyboard = [
                [InlineKeyboardButton("➕ افزودن سرور جدید", callback_data="admin_add_server")],
                [InlineKeyboardButton("🔄 همگام‌سازی", callback_data="admin_sync")],
                [InlineKeyboardButton("🔙 بازگشت به منو", callback_data="admin_menu")]
            ]
            
            await update.message.reply_text(
                message,
                parse_mode='Markdown',
                reply_markup=InlineKeyboardMarkup(keyboard)
            )
            
        except Exception as e:
            await update.message.reply_text(f"❌ خطا در دریافت سرورها: {e}")
    
    async def inbounds_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """مدیریت Inbound ها"""
        user_id = update.effective_user.id
        
        if not await self.is_admin(user_id):
            await update.message.reply_text("❌ شما دسترسی ادمین ندارید!")
            return
        
        try:
            inbounds = await sync_to_async(list)(XUIInbound.objects.filter(is_deleted=False).order_by('-created_at'))
            
            if not inbounds:
                keyboard = [
                    [InlineKeyboardButton("➕ افزودن Inbound", callback_data="admin_add_inbound")],
                    [InlineKeyboardButton("🔄 همگام‌سازی", callback_data="admin_sync")],
                    [InlineKeyboardButton("🔙 بازگشت به منو", callback_data="admin_menu")]
                ]
                await update.message.reply_text(
                    "🔗 **مدیریت Inbound ها**\n\n"
                    "⚠️ هیچ Inbound یافت نشد!\n\n"
                    "💡 برای افزودن Inbound جدید از دکمه زیر استفاده کنید:",
                    parse_mode='Markdown',
                    reply_markup=InlineKeyboardMarkup(keyboard)
                )
                return
            
            message = "🔗 **لیست Inbound ها:**\n\n"
            
            for i, inbound in enumerate(inbounds, 1):
                clients_count = await sync_to_async(inbound.clients.count)()
                available_slots = await sync_to_async(inbound.get_available_slots)()
                status_emoji = "🟢" if inbound.is_active else "🔴"
                status_text = "فعال" if inbound.is_active else "غیرفعال"
                
                message += (
                    f"{status_emoji} **{i}. {inbound.remark}**\n"
                    f"   🖥️ سرور: {inbound.server.name}\n"
                    f"   🔌 پورت: `{inbound.port}`\n"
                    f"   📡 پروتکل: `{inbound.protocol.upper()}`\n"
                    f"   👤 کلاینت‌ها: `{clients_count}/{inbound.max_clients}`\n"
                    f"   📊 اسلات خالی: `{available_slots}`\n"
                    f"   🔧 وضعیت: {status_text}\n\n"
                )
            
            keyboard = [
                [InlineKeyboardButton("➕ افزودن Inbound", callback_data="admin_add_inbound")],
                [InlineKeyboardButton("🔄 همگام‌سازی", callback_data="admin_sync")],
                [InlineKeyboardButton("🔙 بازگشت به منو", callback_data="admin_menu")]
            ]
            
            await update.message.reply_text(
                message,
                parse_mode='Markdown',
                reply_markup=InlineKeyboardMarkup(keyboard)
            )
            
        except Exception as e:
            await update.message.reply_text(f"❌ خطا در دریافت Inbound ها: {e}")
    
    async def clients_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """مدیریت کلاینت‌ها"""
        user_id = update.effective_user.id
        
        if not await self.is_admin(user_id):
            await update.message.reply_text("❌ شما دسترسی ادمین ندارید!")
            return
        
        try:
            clients = await sync_to_async(list)(XUIClient.objects.filter(is_active=True))
            
            if not clients:
                await update.message.reply_text("❌ هیچ کلاینت فعالی یافت نشد!")
                return
            
            message = "👤 **لیست کلاینت‌ها:**\n\n"
            
            for i, client in enumerate(clients[:20], 1):  # فقط 20 کلاینت اول
                remaining_gb = await sync_to_async(client.get_remaining_gb)()
                is_expired = await sync_to_async(client.is_expired)()
                expiry_status_emoji = "⏰" if is_expired else "✅"
                expiry_status = "منقضی شده" if is_expired else "فعال"
                status_emoji = "🟢" if client.is_active else "🔴"
                status_text = "فعال" if client.is_active else "غیرفعال"
                
                message += (
                    f"{status_emoji} **{i}. {client.email}**\n"
                    f"   👤 کاربر: {client.user.full_name}\n"
                    f"   🔗 Inbound: {client.inbound.remark}\n"
                    f"   📊 حجم باقی: `{remaining_gb:.2f}` GB\n"
                    f"   {expiry_status_emoji} انقضا: {expiry_status}\n"
                    f"   🔧 وضعیت: {status_text}\n\n"
                )
            
            if len(clients) > 20:
                message += f"... و {len(clients) - 20} کلاینت دیگر\n\n"
            
            keyboard = [
                [InlineKeyboardButton("🔙 بازگشت به منو", callback_data="admin_menu")]
            ]
            
            await update.message.reply_text(
                message,
                parse_mode='Markdown',
                reply_markup=InlineKeyboardMarkup(keyboard)
            )
            
        except Exception as e:
            await update.message.reply_text(f"❌ خطا در دریافت کلاینت‌ها: {e}")
    
    async def users_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """مدیریت کاربران"""
        user_id = update.effective_user.id
        
        if not await self.is_admin(user_id):
            await update.message.reply_text("❌ شما دسترسی ادمین ندارید!")
            return
        
        try:
            users = await sync_to_async(list)(UsersModel.objects.all())
            
            if not users:
                await update.message.reply_text("❌ هیچ کاربری یافت نشد!")
                return
            
            message = "👥 **لیست کاربران:**\n\n"
            
            for i, user in enumerate(users[:20], 1):  # فقط 20 کاربر اول
                configs_count = await sync_to_async(user.xui_configs.filter(is_active=True).count)()
                trial_status = "✅ استفاده شده" if user.has_used_trial else "❌ استفاده نشده"
                status_emoji = "🟢" if user.is_active else "🔴"
                status_text = "فعال" if user.is_active else "غیرفعال"
                
                message += (
                    f"{status_emoji} **{i}. {user.full_name}**\n"
                    f"   🆔 ID: `{user.telegram_id or 'نامشخص'}`\n"
                    f"   📋 کانفیگ‌ها: `{configs_count}`\n"
                    f"   🎁 پلن تستی: {trial_status}\n"
                    f"   🔧 وضعیت: {status_text}\n\n"
                )
            
            if len(users) > 20:
                message += f"... و {len(users) - 20} کاربر دیگر\n\n"
            
            keyboard = [
                [InlineKeyboardButton("🔙 بازگشت به منو", callback_data="admin_menu")]
            ]
            
            await update.message.reply_text(
                message,
                parse_mode='Markdown',
                reply_markup=InlineKeyboardMarkup(keyboard)
            )
            
        except Exception as e:
            await update.message.reply_text(f"❌ خطا در دریافت کاربران: {e}")

    async def plans_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """مدیریت پلن‌های فروش"""
        user_id = update.effective_user.id

        if not await self.is_admin(user_id):
            await update.message.reply_text("❌ شما دسترسی ادمین ندارید!")
            return

        try:
            plans = await sync_to_async(list)(ConfingPlansModel.objects.filter(is_deleted=False).order_by('-created_at'))

            if not plans:
                keyboard = [[InlineKeyboardButton("➕ افزودن پلن جدید", callback_data="admin_add_plan")]]
                await update.message.reply_text(
                    "📦 **مدیریت پلن‌ها**\n\n"
                    "⚠️ هیچ پلنی یافت نشد!\n\n"
                    "💡 برای افزودن پلن جدید از دکمه زیر استفاده کنید:",
                    parse_mode='Markdown',
                    reply_markup=InlineKeyboardMarkup(keyboard)
                )
                return

            message_lines = ["📦 **لیست پلن‌ها:**\n\n"]
            for i, plan in enumerate(plans, 1):
                try:
                    traffic_gb = await sync_to_async(plan.get_traffic_gb)()
                    status_emoji = "🟢" if plan.is_active else "🔴"
                    message_lines.append(
                        f"{status_emoji} **{i}. {plan.name}**\n"
                        f"   🆔 ID: `{plan.id}`\n"
                        f"   💰 قیمت: `{plan.price:,}` تومان\n"
                        f"   📶 حجم: `{traffic_gb:.2f}` GB\n"
                        f"   📊 حجم (MB): `{plan.in_volume:,}` MB\n"
                        f"   🔧 وضعیت: {'فعال' if plan.is_active else 'غیرفعال'}\n"
                    )
                    if plan.description:
                        message_lines.append(f"   📝 {plan.description[:50]}...\n")
                    message_lines.append("\n")
                except Exception as e:
                    logger.error(f"خطا در پردازش پلن {plan.id}: {e}")
                    message_lines.append(
                        f"⚠️ **{i}. {plan.name}** (خطا در پردازش)\n\n"
                    )

            keyboard = [
                [InlineKeyboardButton("➕ افزودن پلن جدید", callback_data="admin_add_plan")],
                [InlineKeyboardButton("🔙 بازگشت به منو", callback_data="admin_menu")]
            ]

            await update.message.reply_text(
                "\n".join(message_lines),
                parse_mode='Markdown',
                reply_markup=InlineKeyboardMarkup(keyboard)
            )

        except Exception as e:
            await update.message.reply_text(f"❌ خطا در دریافت پلن‌ها: {e}")

    async def add_plan_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """افزودن پلن جدید"""
        user_id = update.effective_user.id
        
        if not await self.is_admin(user_id):
            await update.message.reply_text("❌ شما دسترسی ادمین ندارید!")
            return
        
        context.user_data['admin_state'] = 'adding_plan'
        context.user_data['plan_data'] = {}
        
        await update.message.reply_text(
            "➕ **افزودن پلن جدید**\n\n"
            "📝 لطفاً اطلاعات پلن را به ترتیب زیر ارسال کنید:\n\n"
            "1️⃣ **نام پلن:**\n"
            "   مثال: پلن طلایی\n\n"
            "2️⃣ **قیمت (تومان):**\n"
            "   مثال: 50000\n\n"
            "3️⃣ **حجم (مگابایت):**\n"
            "   مثال: 10240 (برای 10 GB)\n\n"
            "4️⃣ **توضیحات (اختیاری):**\n"
            "   مثال: پلن ویژه با سرعت بالا\n\n"
            "💡 **نکته:** برای لغو، `/cancel` را ارسال کنید.",
            parse_mode='Markdown'
        )
    
    async def add_server_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """افزودن سرور جدید"""
        user_id = update.effective_user.id
        
        if not await self.is_admin(user_id):
            await update.message.reply_text("❌ شما دسترسی ادمین ندارید!")
            return
        
        context.user_data['admin_state'] = 'adding_server'
        context.user_data['server_data'] = {}
        
        await update.message.reply_text(
            "➕ **افزودن سرور X-UI جدید**\n\n"
            "📝 لطفاً اطلاعات سرور را به ترتیب زیر ارسال کنید:\n\n"
            "1️⃣ **نام سرور:**\n"
            "   مثال: سرور اصلی\n\n"
            "2️⃣ **آدرس سرور (IP یا Domain):**\n"
            "   مثال: 192.168.1.1 یا server.example.com\n\n"
            "3️⃣ **پورت X-UI:**\n"
            "   مثال: 54321\n\n"
            "4️⃣ **نام کاربری X-UI:**\n"
            "   مثال: admin\n\n"
            "5️⃣ **رمز عبور X-UI:**\n"
            "   مثال: password123\n\n"
            "6️⃣ **مسیر وب (اختیاری):**\n"
            "   مثال: /MsxZ4xuIy5xLfQtsSC/\n\n"
            "💡 **نکته:** برای لغو، `/cancel` را ارسال کنید.",
            parse_mode='Markdown'
        )
    
    async def create_inbound_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """ایجاد Inbound جدید"""
        user_id = update.effective_user.id
        
        if not await self.is_admin(user_id):
            await update.message.reply_text("❌ شما دسترسی ادمین ندارید!")
            return
        
        # دریافت لیست سرورها
        servers = await sync_to_async(list)(XUIServer.objects.filter(is_active=True))
        
        if not servers:
            await update.message.reply_text(
                "⚠️ **هیچ سرور فعالی یافت نشد!**\n\n"
                "💡 ابتدا یک سرور اضافه کنید: `/add_server`",
                parse_mode='Markdown'
            )
            return
        
        context.user_data['admin_state'] = 'creating_inbound'
        context.user_data['inbound_data'] = {}
        
        # ایجاد دکمه‌های انتخاب سرور
        keyboard = []
        for server in servers:
            keyboard.append([InlineKeyboardButton(
                f"🖥️ {server.name} ({server.host})",
                callback_data=f"select_server_{server.id}"
            )])
        keyboard.append([InlineKeyboardButton("❌ لغو", callback_data="admin_cancel")])
        
        await update.message.reply_text(
            "➕ **ایجاد Inbound جدید**\n\n"
            "🖥️ **لطفاً سرور مورد نظر را انتخاب کنید:**",
            parse_mode='Markdown',
            reply_markup=InlineKeyboardMarkup(keyboard)
        )
    
    async def assign_user_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """تخصیص کاربر به Inbound"""
        user_id = update.effective_user.id
        
        if not await self.is_admin(user_id):
            await update.message.reply_text("❌ شما دسترسی ادمین ندارید!")
            return
        
        await update.message.reply_text(
            "🔄 **تخصیص کاربر به Inbound**\n\n"
            "این قابلیت در حال توسعه است...\n\n"
            "💡 **نکته:** کاربران به صورت خودکار به بهترین Inbound موجود تخصیص داده می‌شوند.",
            parse_mode='Markdown'
        )
    
    async def sync_xui_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """همگام‌سازی با X-UI"""
        user_id = update.effective_user.id
        
        if not await self.is_admin(user_id):
            await update.message.reply_text("❌ شما دسترسی ادمین ندارید!")
            return
        
        try:
            await update.message.reply_text("🔄 **شروع همگام‌سازی با X-UI...**")
            
            total_synced = 0
            servers = await sync_to_async(list)(XUIServer.objects.filter(is_active=True))
            for server in servers:
                try:
                    enhanced_service = XUIEnhancedService(server)
                    synced_count = await sync_to_async(enhanced_service.sync_inbounds_to_database)()
                    total_synced += synced_count
                    
                    await update.message.reply_text(
                        f"✅ سرور {server.name}: {synced_count} inbound همگام‌سازی شد"
                    )
                    
                except Exception as e:
                    await update.message.reply_text(
                        f"❌ خطا در همگام‌سازی سرور {server.name}: {e}"
                    )
            
            await update.message.reply_text(
                f"✅ **همگام‌سازی کامل شد!**\n\n"
                f"📊 تعداد کل inbound های همگام‌سازی شده: {total_synced}",
                parse_mode='Markdown'
            )
            
        except Exception as e:
            await update.message.reply_text(f"❌ خطا در همگام‌سازی: {e}")
    
    async def cleanup_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """پاکسازی خودکار"""
        user_id = update.effective_user.id
        
        if not await self.is_admin(user_id):
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
    
    async def check_expired_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """بررسی کاربران منقضی شده"""
        user_id = update.effective_user.id
        
        if not await self.is_admin(user_id):
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
            
            message += f"💡 برای پاکسازی از دستور `/cleanup` استفاده کنید."
            
            await update.message.reply_text(message, parse_mode='Markdown')
            
        except Exception as e:
            await update.message.reply_text(f"❌ خطا در بررسی کاربران منقضی شده: {e}")
    
    async def payments_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """مدیریت پرداخت‌های در انتظار تایید"""
        user_id = update.effective_user.id
        
        if not await self.is_admin(user_id):
            await update.message.reply_text("❌ شما دسترسی ادمین ندارید!")
            return
        
        try:
            # دریافت پرداخت‌های در انتظار تایید
            pending_payments = await sync_to_async(list)(
                PayMentModel.objects.filter(
                    is_active=True,
                    rejected=False,
                    order__is_active=False
                ).order_by('-created_at')[:10]
            )
            
            if not pending_payments:
                keyboard = [
                    [InlineKeyboardButton("🔙 بازگشت به منو", callback_data="admin_menu")]
                ]
                await update.message.reply_text(
                    "💰 **مدیریت پرداخت‌ها**\n\n"
                    "✅ هیچ پرداخت در انتظار تاییدی یافت نشد!",
                    parse_mode='Markdown',
                    reply_markup=InlineKeyboardMarkup(keyboard)
                )
                return
            
            message = "💰 **پرداخت‌های در انتظار تایید:**\n\n"
            
            for i, payment in enumerate(pending_payments, 1):
                order = payment.order
                plan = order.plans
                user = payment.user
                
                message += (
                    f"**{i}. پرداخت #{payment.code_pay}**\n"
                    f"   👤 کاربر: {user.full_name}\n"
                    f"   🆔 ID: `{user.telegram_id}`\n"
                    f"   📦 پلن: {plan.name}\n"
                    f"   💰 مبلغ: `{plan.price:,}` تومان\n"
                    f"   📅 تاریخ: {payment.created_at.strftime('%Y/%m/%d %H:%M')}\n\n"
                )
            
            keyboard = [
                [InlineKeyboardButton("🔙 بازگشت به منو", callback_data="admin_menu")]
            ]
            
            await update.message.reply_text(
                message,
                parse_mode='Markdown',
                reply_markup=InlineKeyboardMarkup(keyboard)
            )
            
            # ارسال عکس‌های پرداخت
            for payment in pending_payments:
                try:
                    if payment.images:
                        order = payment.order
                        plan = order.plans
                        user = payment.user
                        
                        caption = (
                            f"💰 **پرداخت #{payment.code_pay}**\n\n"
                            f"👤 **کاربر:** {user.full_name}\n"
                            f"🆔 **ID:** `{user.telegram_id}`\n"
                            f"📱 **یوزرنیم:** @{user.username or 'بدون یوزرنیم'}\n"
                            f"📦 **پلن:** {plan.name}\n"
                            f"💰 **مبلغ:** `{plan.price:,}` تومان\n"
                            f"📅 **تاریخ:** {payment.created_at.strftime('%Y/%m/%d %H:%M')}\n\n"
                            f"🆔 **شناسه پرداخت:** `{payment.id}`"
                        )
                        
                        keyboard = [
                            [
                                InlineKeyboardButton("✅ تایید", callback_data=f"approve_{payment.id}"),
                                InlineKeyboardButton("❌ رد", callback_data=f"reject_{payment.id}")
                            ],
                            [InlineKeyboardButton("🔙 بازگشت", callback_data="admin_payments")]
                        ]
                        
                        # ارسال عکس
                        if hasattr(payment.images, 'url'):
                            photo_url = payment.images.url
                            await update.message.reply_photo(
                                photo=photo_url,
                                caption=caption,
                                parse_mode='Markdown',
                                reply_markup=InlineKeyboardMarkup(keyboard)
                            )
                        else:
                            # اگر فایل محلی است
                            await update.message.reply_text(
                                caption,
                                parse_mode='Markdown',
                                reply_markup=InlineKeyboardMarkup(keyboard)
                            )
                except Exception as e:
                    logger.error(f"خطا در ارسال عکس پرداخت {payment.id}: {e}")
            
        except Exception as e:
            logger.error(f"خطا در دریافت پرداخت‌ها: {e}")
            await update.message.reply_text(f"❌ خطا در دریافت پرداخت‌ها: {e}")
    
    async def approve_payment(self, query, context, payment_id):
        """تایید پرداخت و فعال‌سازی پلن"""
        user_id = query.from_user.id
        
        if not await self.is_admin(user_id):
            await query.answer("❌ شما دسترسی ادمین ندارید!", show_alert=True)
            return
        
        try:
            payment = await sync_to_async(PayMentModel.objects.get)(id=payment_id)
            order = payment.order
            plan = order.plans
            user = payment.user
            
            # فعال‌سازی سفارش
            order.is_active = True
            await sync_to_async(order.save)()
            
            # ایجاد کانفیگ برای کاربر
            active_servers = await sync_to_async(list)(XUIServer.objects.filter(is_active=True))
            if active_servers:
                server = active_servers[0]
                from xui_servers.enhanced_api_models import XUIClientManager, XUIInboundManager
                
                inbound_manager = XUIInboundManager(server)
                inbound = await sync_to_async(inbound_manager.find_best_inbound)("vless")
                
                if inbound:
                    client_manager = XUIClientManager(server)
                    user_config = await client_manager.create_user_config_async(user, plan, inbound)
                    
                    if user_config:
                        # ارسال پیام به کاربر
                        try:
                            from telegram import Bot
                            bot = Bot(token=getattr(settings, 'USER_BOT_TOKEN', ''))
                            duration_days = getattr(plan, 'duration_days', 30)
                            expiry_date = user_config.expires_at if user_config.expires_at else timezone.now() + timedelta(days=duration_days)
                            await bot.send_message(
                                chat_id=user.telegram_id,
                                text=(
                                    f"✅ **پرداخت شما تایید شد!**\n\n"
                                    f"📦 **پلن:** {plan.name}\n"
                                    f"💰 **مبلغ:** {plan.price:,} تومان\n"
                                    f"⏰ **اعتبار:** {duration_days} روز\n"
                                    f"📅 **تاریخ انقضا:** {expiry_date.strftime('%Y-%m-%d %H:%M')}\n\n"
                                    f"🔧 **کانفیگ شما:**\n"
                                    f"`{user_config.config_data}`\n\n"
                                    f"💡 می‌توانید از بخش '⚙️ تنظیمات من' کانفیگ را مشاهده کنید."
                                ),
                                parse_mode='Markdown'
                            )
                        except Exception as e:
                            logger.error(f"خطا در ارسال پیام به کاربر: {e}")
            
            await query.edit_message_caption(
                caption=query.message.caption + "\n\n✅ **تایید شد!**",
                reply_markup=InlineKeyboardMarkup([[
                    InlineKeyboardButton("🔙 بازگشت", callback_data="admin_payments")
                ]])
            )
            await query.answer("✅ پرداخت تایید شد!")
            
        except Exception as e:
            logger.error(f"خطا در تایید پرداخت: {e}")
            await query.answer(f"❌ خطا در تایید پرداخت: {e}", show_alert=True)
    
    async def reject_payment(self, query, context, payment_id):
        """رد پرداخت"""
        user_id = query.from_user.id
        
        if not await self.is_admin(user_id):
            await query.answer("❌ شما دسترسی ادمین ندارید!", show_alert=True)
            return
        
        try:
            payment = await sync_to_async(PayMentModel.objects.get)(id=payment_id)
            payment.rejected = True
            payment.is_active = False
            await sync_to_async(payment.save)()
            
            # ارسال پیام به کاربر
            try:
                from telegram import Bot
                bot = Bot(token=getattr(settings, 'USER_BOT_TOKEN', ''))
                await bot.send_message(
                    chat_id=payment.user.telegram_id,
                    text=(
                        f"❌ **پرداخت شما رد شد!**\n\n"
                        f"💰 **کد پرداخت:** {payment.code_pay}\n\n"
                        f"💡 لطفاً با پشتیبانی تماس بگیرید یا رسید جدید ارسال کنید."
                    ),
                    parse_mode='Markdown'
                )
            except Exception as e:
                logger.error(f"خطا در ارسال پیام به کاربر: {e}")
            
            await query.edit_message_caption(
                caption=query.message.caption + "\n\n❌ **رد شد!**",
                reply_markup=InlineKeyboardMarkup([[
                    InlineKeyboardButton("🔙 بازگشت", callback_data="admin_payments")
                ]])
            )
            await query.answer("❌ پرداخت رد شد!")
            
        except Exception as e:
            logger.error(f"خطا در رد پرداخت: {e}")
            await query.answer(f"❌ خطا در رد پرداخت: {e}", show_alert=True)
    
    async def tickets_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """مدیریت تیکت‌های کاربران"""
        user_id = update.effective_user.id
        
        if not await self.is_admin(user_id):
            await update.message.reply_text("❌ شما دسترسی ادمین ندارید!")
            return
        
        try:
            # دریافت تیکت‌های فعال
            tickets = await sync_to_async(list)(
                MessageDirectory.objects.filter(
                    admin__telegram_id=user_id,
                    is_deleted=False
                ).order_by('-created_at')[:20]
            )
            
            if not tickets:
                keyboard = [
                    [InlineKeyboardButton("🔙 بازگشت به منو", callback_data="admin_menu")]
                ]
                await update.message.reply_text(
                    "💬 **مدیریت تیکت‌ها**\n\n"
                    "✅ هیچ تیکت فعالی یافت نشد!",
                    parse_mode='Markdown',
                    reply_markup=InlineKeyboardMarkup(keyboard)
                )
                return
            
            message = "💬 **تیکت‌های فعال:**\n\n"
            
            for i, ticket in enumerate(tickets, 1):
                # شمارش پیام‌ها
                messages_count = await sync_to_async(
                    MessageModel.objects.filter(
                        directory=ticket,
                        is_deleted=False
                    ).count
                )()
                
                message += (
                    f"**{i}. تیکت #{ticket.id}**\n"
                    f"   👤 کاربر: {ticket.user.full_name}\n"
                    f"   🆔 ID: `{ticket.user.telegram_id}`\n"
                    f"   📅 تاریخ: {ticket.created_at.strftime('%Y/%m/%d %H:%M')}\n"
                    f"   💬 پیام‌ها: {messages_count}\n\n"
                )
            
            keyboard = [
                [InlineKeyboardButton("🔙 بازگشت به منو", callback_data="admin_menu")]
            ]
            
            await update.message.reply_text(
                message,
                parse_mode='Markdown',
                reply_markup=InlineKeyboardMarkup(keyboard)
            )
            
            # نمایش پیام‌های هر تیکت
            for ticket in tickets:
                messages = await sync_to_async(list)(
                    MessageModel.objects.filter(
                        directory=ticket,
                        is_deleted=False
                    ).order_by('created_at')
                )
                
                if messages:
                    messages_text = f"💬 **تیکت #{ticket.id}**\n\n"
                    messages_text += f"👤 **کاربر:** {ticket.user.full_name}\n"
                    messages_text += f"🆔 **ID:** `{ticket.user.telegram_id}`\n\n"
                    messages_text += "📝 **پیام‌ها:**\n\n"
                    
                    for msg in messages:
                        messages_text += f"• {msg.messages}\n"
                        messages_text += f"  📅 {msg.created_at.strftime('%Y/%m/%d %H:%M')}\n\n"
                    
                    keyboard = [
                        [
                            InlineKeyboardButton("✅ تایید و ایجاد کلاینت", callback_data=f"approve_ticket_{ticket.id}"),
                            InlineKeyboardButton("💬 پاسخ", callback_data=f"reply_ticket_{ticket.id}")
                        ],
                        [
                            InlineKeyboardButton("❌ بستن", callback_data=f"close_ticket_{ticket.id}"),
                            InlineKeyboardButton("🔙 بازگشت", callback_data="admin_tickets")
                        ]
                    ]
                    
                    await update.message.reply_text(
                        messages_text,
                        parse_mode='Markdown',
                        reply_markup=InlineKeyboardMarkup(keyboard)
                    )
            
        except Exception as e:
            logger.error(f"خطا در دریافت تیکت‌ها: {e}")
            await update.message.reply_text(f"❌ خطا در دریافت تیکت‌ها: {e}")
    
    async def approve_ticket_and_create_client(self, query, context, ticket_id):
        """تایید تیکت و ایجاد کلاینت برای کاربر"""
        user_id = query.from_user.id
        
        if not await self.is_admin(user_id):
            await query.answer("❌ شما دسترسی ادمین ندارید!", show_alert=True)
            return
        
        try:
            ticket = await sync_to_async(MessageDirectory.objects.get)(id=ticket_id)
            user = ticket.user
            
            await query.answer("⏳ در حال ایجاد کلاینت...")
            
            # یافتن سرور فعال
            active_servers = await sync_to_async(list)(XUIServer.objects.filter(is_active=True))
            if not active_servers:
                await query.edit_message_text(
                    "❌ **هیچ سرور فعالی یافت نشد!**\n\n"
                    "لطفاً ابتدا یک سرور اضافه کنید.",
                    parse_mode='Markdown'
                )
                return
            
            server = active_servers[0]
            
            # یافتن پلن پیش‌فرض یا اولین پلن
            def get_default_plan():
                # سعی می‌کنیم پلن پیش‌فرض یا اولین پلن فعال را پیدا کنیم
                plan = ConfingPlansModel.objects.filter(is_active=True).first()
                if not plan:
                    # اگر پلنی وجود ندارد، یک پلن پیش‌فرض ایجاد می‌کنیم
                    plan = ConfingPlansModel.objects.create(
                        name="پلن پیش‌فرض",
                        price=0,
                        in_volume=102400,  # 100 GB به مگابایت
                        traffic_mb=102400,  # 100 GB به مگابایت
                        duration_days=30,  # 30 روز
                        is_active=True
                    )
                return plan
            
            plan = await sync_to_async(get_default_plan)()
            
            # یافتن inbound مناسب
            from xui_servers.enhanced_api_models import XUIClientManager, XUIInboundManager
            
            inbound_manager = XUIInboundManager(server)
            inbound = await sync_to_async(inbound_manager.find_best_inbound)("vless")
            
            if not inbound:
                await query.edit_message_text(
                    "❌ **هیچ inbound مناسبی یافت نشد!**\n\n"
                    "لطفاً ابتدا یک inbound اضافه کنید.",
                    parse_mode='Markdown'
                )
                return
            
            # ایجاد کلاینت
            client_manager = XUIClientManager(server)
            
            # محاسبه حجم به گیگابایت
            traffic_gb = await sync_to_async(plan.get_traffic_gb)()
            # مدت زمان از پلن یا پیش‌فرض 30 روز
            duration_days = getattr(plan, 'duration_days', 30)
            
            # ایجاد تنظیمات کلاینت
            def create_client_settings():
                email = f"{user.username_tel}_{user.telegram_id}"
                return client_manager.service.create_client_settings(
                    email=email,
                    total_gb=traffic_gb,
                    expiry_days=duration_days
                )
            
            client_settings = await sync_to_async(create_client_settings)()
            
            # اضافه کردن کلاینت به inbound
            def add_client():
                return client_manager.service.add_client_to_inbound(inbound.xui_inbound_id, client_settings)
            
            if await sync_to_async(add_client)():
                # ایجاد رکورد در دیتابیس
                client_data = client_settings['clients'][0]
                
                # تولید کانفیگ واقعی از X-UI
                def generate_config():
                    return client_manager._generate_real_config_data(inbound, client_data)
                
                config_data = await sync_to_async(generate_config)()
                
                # ایجاد UserConfig
                def create_user_config():
                    return UserConfig.objects.create(
                        user=user,
                        server=server,
                        inbound=inbound,
                        xui_inbound_id=inbound.xui_inbound_id,
                        xui_user_id=client_data['id'],
                        config_name=f"{user.full_name} - {plan.name}",
                        config_data=config_data,
                        is_active=True,
                        expires_at=timezone.now() + timedelta(days=duration_days),
                        protocol=inbound.protocol,
                        plan=plan,
                        is_trial=False
                    )
                
                user_config = await sync_to_async(create_user_config)()
            else:
                user_config = None
            
            if user_config:
                # ارسال به کاربر
                try:
                    from telegram import Bot
                    bot = Bot(token=getattr(settings, 'USER_BOT_TOKEN', ''))
                    
                    # استفاده از تاریخ انقضای user_config
                    expiry_date = user_config.expires_at if user_config.expires_at else timezone.now() + timedelta(days=duration_days)
                    
                    # ایجاد QR کد (اگر در دسترس باشد)
                    if QRCODE_AVAILABLE:
                        try:
                            qr = qrcode.QRCode(version=1, box_size=10, border=5)
                            qr.add_data(user_config.config_data)
                            qr.make(fit=True)
                            
                            img = qr.make_image(fill_color="black", back_color="white")
                            bio = io.BytesIO()
                            img.save(bio, format='PNG')
                            bio.seek(0)
                            
                            # ارسال QR کد و کانفیگ
                            await bot.send_photo(
                                chat_id=user.telegram_id,
                                photo=bio,
                                caption=(
                                    f"✅ **تیکت شما تایید شد و کلاینت ایجاد شد!**\n\n"
                                    f"👤 **کاربر:** {user.full_name}\n"
                                    f"📦 **پلن:** {plan.name}\n"
                                    f"💰 **قیمت:** {plan.price:,} تومان\n"
                                    f"⏰ **اعتبار:** {duration_days} روز\n"
                                    f"📊 **حجم:** {await sync_to_async(plan.get_traffic_gb)():.2f} GB\n"
                                    f"🖥️ **سرور:** {server.name}\n"
                                    f"🔧 **پروتکل:** {inbound.protocol.upper()}\n"
                                    f"📅 **تاریخ انقضا:** {expiry_date.strftime('%Y-%m-%d %H:%M')}\n\n"
                                    f"🔧 **کانفیگ شما:**\n"
                                    f"`{user_config.config_data}`\n\n"
                                    f"💡 **نحوه استفاده:**\n"
                                    f"• QR کد را اسکن کنید\n"
                                    f"• یا کانفیگ را کپی و در اپلیکیشن VPN وارد کنید\n\n"
                                    f"📱 می‌توانید از بخش '⚙️ تنظیمات من' کانفیگ را مشاهده کنید."
                                ),
                                parse_mode='Markdown'
                            )
                        except Exception as qr_error:
                            logger.warning(f"⚠️ خطا در ایجاد QR کد: {qr_error}")
                            # اگر QR کد ایجاد نشد، فقط کانفیگ را ارسال می‌کنیم
                            await bot.send_message(
                                chat_id=user.telegram_id,
                                text=(
                                    f"✅ **تیکت شما تایید شد و کلاینت ایجاد شد!**\n\n"
                                    f"👤 **کاربر:** {user.full_name}\n"
                                    f"📦 **پلن:** {plan.name}\n"
                                    f"💰 **قیمت:** {plan.price:,} تومان\n"
                                    f"⏰ **اعتبار:** {duration_days} روز\n"
                                    f"📊 **حجم:** {await sync_to_async(plan.get_traffic_gb)():.2f} GB\n"
                                    f"🖥️ **سرور:** {server.name}\n"
                                    f"🔧 **پروتکل:** {inbound.protocol.upper()}\n"
                                    f"📅 **تاریخ انقضا:** {expiry_date.strftime('%Y-%m-%d %H:%M')}\n\n"
                                    f"🔧 **کانفیگ شما:**\n"
                                    f"`{user_config.config_data}`\n\n"
                                    f"💡 **نحوه استفاده:**\n"
                                    f"• کانفیگ را کپی و در اپلیکیشن VPN وارد کنید\n\n"
                                    f"📱 می‌توانید از بخش '⚙️ تنظیمات من' کانفیگ را مشاهده کنید."
                                ),
                                parse_mode='Markdown'
                            )
                    else:
                        # اگر QR کد در دسترس نباشد، فقط کانفیگ را ارسال می‌کنیم
                        traffic_gb_value = await sync_to_async(plan.get_traffic_gb)()
                        await bot.send_message(
                            chat_id=user.telegram_id,
                            text=(
                                f"✅ **تیکت شما تایید شد و کلاینت ایجاد شد!**\n\n"
                                f"👤 **کاربر:** {user.full_name}\n"
                                f"📦 **پلن:** {plan.name}\n"
                                f"💰 **قیمت:** {plan.price:,} تومان\n"
                                f"⏰ **اعتبار:** {duration_days} روز\n"
                                f"📊 **حجم:** {traffic_gb_value:.2f} GB\n"
                                f"🖥️ **سرور:** {server.name}\n"
                                f"🔧 **پروتکل:** {inbound.protocol.upper()}\n"
                                f"📅 **تاریخ انقضا:** {expiry_date.strftime('%Y-%m-%d %H:%M')}\n\n"
                                f"🔧 **کانفیگ شما:**\n"
                                f"`{user_config.config_data}`\n\n"
                                f"💡 **نحوه استفاده:**\n"
                                f"• کانفیگ را کپی و در اپلیکیشن VPN وارد کنید\n\n"
                                f"📱 می‌توانید از بخش '⚙️ تنظیمات من' کانفیگ را مشاهده کنید."
                            ),
                            parse_mode='Markdown'
                        )
                    
                    logger.info(f"✅ کلاینت ایجاد شد و برای کاربر ارسال شد: User ID: {user.telegram_id}, Config ID: {user_config.id}")
                except Exception as e:
                    logger.error(f"❌ خطا در ارسال به کاربر: {e}", exc_info=True)
                    await query.edit_message_text(
                        f"⚠️ **کلاینت ایجاد شد اما خطا در ارسال به کاربر:**\n\n{str(e)}",
                        parse_mode='Markdown'
                    )
                    return
                
                # به‌روزرسانی پیام ادمین
                await query.edit_message_text(
                    f"✅ **تیکت تایید شد و کلاینت ایجاد شد!**\n\n"
                    f"👤 **کاربر:** {user.full_name}\n"
                    f"🆔 **User ID:** `{user.telegram_id}`\n"
                    f"📦 **پلن:** {plan.name}\n"
                    f"🔧 **Config ID:** `{user_config.id}`\n"
                    f"🖥️ **سرور:** {server.name}\n"
                    f"⏰ **اعتبار:** {duration_days} روز\n\n"
                    f"✅ QR کد و کانفیگ برای کاربر ارسال شد!",
                    parse_mode='Markdown',
                    reply_markup=InlineKeyboardMarkup([[
                        InlineKeyboardButton("🔙 بازگشت", callback_data="admin_tickets")
                    ]])
                )
            else:
                await query.edit_message_text(
                    "❌ **خطا در ایجاد کلاینت!**\n\n"
                    "لطفاً لاگ‌ها را بررسی کنید.",
                    parse_mode='Markdown'
                )
                
        except Exception as e:
            logger.error(f"❌ خطا در تایید تیکت و ایجاد کلاینت: {e}", exc_info=True)
            await query.answer(f"❌ خطا: {e}", show_alert=True)
            await query.edit_message_text(
                f"❌ **خطا در تایید تیکت:**\n\n{str(e)}",
                parse_mode='Markdown'
            )
    
    async def start_reply_ticket(self, query, context, ticket_id):
        """شروع پاسخ به تیکت"""
        user_id = query.from_user.id
        
        if not await self.is_admin(user_id):
            await query.answer("❌ شما دسترسی ادمین ندارید!", show_alert=True)
            return
        
        try:
            ticket = await sync_to_async(MessageDirectory.objects.get)(id=ticket_id)
            
            # ذخیره ticket_id در context برای پاسخ
            context.user_data['replying_to_ticket'] = ticket_id
            context.user_data['admin_state'] = 'replying_ticket'
            
            await query.answer("💬 حالا پیام پاسخ را ارسال کنید...")
            await query.edit_message_text(
                f"💬 **پاسخ به تیکت #{ticket_id}**\n\n"
                f"👤 **کاربر:** {ticket.user.full_name}\n"
                f"🆔 **ID:** `{ticket.user.telegram_id}`\n\n"
                f"📝 **پیام پاسخ خود را ارسال کنید:**\n\n"
                f"⚠️ برای لغو، 'لغو' را ارسال کنید.",
                parse_mode='Markdown'
            )
            
        except Exception as e:
            logger.error(f"خطا در شروع پاسخ به تیکت: {e}")
            await query.answer(f"❌ خطا: {e}", show_alert=True)
    
    async def close_ticket(self, query, context, ticket_id):
        """بستن تیکت"""
        user_id = query.from_user.id
        
        if not await self.is_admin(user_id):
            await query.answer("❌ شما دسترسی ادمین ندارید!", show_alert=True)
            return
        
        try:
            ticket = await sync_to_async(MessageDirectory.objects.get)(id=ticket_id)
            
            # حذف نرم تیکت
            ticket.is_deleted = True
            await sync_to_async(ticket.save)()
            
            # اطلاع به کاربر
            try:
                from telegram import Bot
                bot = Bot(token=getattr(settings, 'USER_BOT_TOKEN', ''))
                await bot.send_message(
                    chat_id=ticket.user.telegram_id,
                    text=(
                        f"✅ **تیکت شما بسته شد!**\n\n"
                        f"🆔 **شماره تیکت:** `{ticket_id}`\n\n"
                        f"💡 برای ثبت تیکت جدید، از '💬 ارتباط با ما' استفاده کنید."
                    ),
                    parse_mode='Markdown'
                )
            except Exception as e:
                logger.error(f"خطا در اطلاع به کاربر: {e}")
            
            await query.answer("✅ تیکت بسته شد!")
            await query.edit_message_text(
                f"✅ **تیکت #{ticket_id} بسته شد!**\n\n"
                f"👤 کاربر مطلع شد.",
                parse_mode='Markdown',
                reply_markup=InlineKeyboardMarkup([[
                    InlineKeyboardButton("🔙 بازگشت", callback_data="admin_tickets")
                ]])
            )
            
        except Exception as e:
            logger.error(f"خطا در بستن تیکت: {e}")
            await query.answer(f"❌ خطا: {e}", show_alert=True)
    
    async def cancel_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """لغو عملیات جاری"""
        user_id = update.effective_user.id
        
        if not await self.is_admin(user_id):
            await update.message.reply_text("❌ شما دسترسی ادمین ندارید!")
            return
        
        context.user_data.pop('admin_state', None)
        context.user_data.pop('plan_data', None)
        context.user_data.pop('server_data', None)
        context.user_data.pop('inbound_data', None)
        
        keyboard = [
            [InlineKeyboardButton("🔙 بازگشت به منو", callback_data="admin_menu")]
        ]
        
        await update.message.reply_text(
            "✅ **عملیات لغو شد**\n\n"
            "💡 می‌توانید از منو استفاده کنید: `/menu`",
            parse_mode='Markdown',
            reply_markup=InlineKeyboardMarkup(keyboard)
        )
    
    async def button_callback(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """پردازش callback دکمه‌ها"""
        query = update.callback_query
        await query.answer()
        
        data = query.data
        user_id = query.from_user.id
        logger.info(f"🔔 دریافت callback query: data={data}, user_id={user_id}")
        
        # کلاس کمکی برای تبدیل query به update
        class FakeUpdate:
            def __init__(self, q):
                self.effective_user = q.from_user
                self.message = q.message
                self.update_id = q.id
        
        fake_update = FakeUpdate(query)
        
        # مدیریت منوهای اصلی
        if data == 'admin_dashboard':
            await self.dashboard_command(fake_update, context)
        elif data == 'admin_servers':
            await self.servers_command(fake_update, context)
        elif data == 'admin_plans':
            await self.plans_command(fake_update, context)
        elif data == 'admin_inbounds':
            await self.inbounds_command(fake_update, context)
        elif data == 'admin_users':
            await self.users_command(fake_update, context)
        elif data == 'admin_clients':
            await self.clients_command(fake_update, context)
        elif data == 'admin_sync':
            await self.sync_xui_command(fake_update, context)
        elif data == 'admin_cleanup':
            await self.cleanup_command(fake_update, context)
        elif data == 'admin_check_expired':
            await self.check_expired_command(fake_update, context)
        elif data == 'admin_payments':
            await self.payments_command(fake_update, context)
        elif data == 'admin_tickets':
            await self.tickets_command(fake_update, context)
        elif data.startswith('approve_ticket_'):
            ticket_id = data.split('_')[2]
            logger.info(f"✅ درخواست تایید تیکت و ایجاد کلاینت: {ticket_id}")
            await self.approve_ticket_and_create_client(query, context, ticket_id)
        elif data.startswith('reply_ticket_'):
            ticket_id = data.split('_')[2]
            logger.info(f"📝 درخواست پاسخ به تیکت: {ticket_id}")
            await self.start_reply_ticket(query, context, ticket_id)
        elif data.startswith('close_ticket_'):
            ticket_id = data.split('_')[2]
            logger.info(f"❌ درخواست بستن تیکت: {ticket_id}")
            await self.close_ticket(query, context, ticket_id)
        elif data.startswith('approve_'):
            payment_id = data.split('_')[1]
            await self.approve_payment(query, context, payment_id)
        elif data.startswith('reject_'):
            payment_id = data.split('_')[1]
            await self.reject_payment(query, context, payment_id)
        elif data == 'admin_add_plan':
            await self.add_plan_command(fake_update, context)
        elif data == 'admin_add_server':
            await self.add_server_command(fake_update, context)
        elif data == 'admin_add_inbound':
            await self.create_inbound_command(fake_update, context)
        elif data == 'admin_menu':
            await self.menu_command(fake_update, context)
        elif data == 'admin_cancel':
            context.user_data.pop('admin_state', None)
            context.user_data.pop('plan_data', None)
            context.user_data.pop('server_data', None)
            context.user_data.pop('inbound_data', None)
            await query.edit_message_text("❌ عملیات لغو شد.")
        elif data.startswith('select_server_'):
            server_id = data.split('_')[2]
            context.user_data['inbound_data']['server_id'] = server_id
            await query.edit_message_text(
                "✅ سرور انتخاب شد!\n\n"
                "📝 حالا اطلاعات Inbound را ارسال کنید:\n\n"
                "1️⃣ **نام Inbound:**\n"
                "   مثال: Inbound اصلی\n\n"
                "2️⃣ **پورت:**\n"
                "   مثال: 443\n\n"
                "3️⃣ **پروتکل (vless/vmess/trojan):**\n"
                "   مثال: vless",
                parse_mode='Markdown'
            )
        elif data.startswith('server_'):
            await self.handle_server_callback(query, context, data)
        elif data.startswith('inbound_'):
            await self.handle_inbound_callback(query, context, data)
        elif data.startswith('client_'):
            await self.handle_client_callback(query, context, data)
    
    async def handle_server_callback(self, query, context, data):
        """پردازش callback سرور"""
        server_id = data.split('_')[1]
        action = data.split('_')[2]
        
        try:
            server = await sync_to_async(XUIServer.objects.get)(id=server_id)
            
            if action == 'info':
                inbounds = await sync_to_async(list)(server.inbounds.filter(is_active=True))
                inbounds_count = len(inbounds)
                total_clients = 0
                for inbound in inbounds:
                    clients_count_inbound = await sync_to_async(inbound.clients.count)()
                    total_clients += clients_count_inbound
                
                message = (
                    f"🖥️ **اطلاعات سرور {server.name}**\n\n"
                    f"📍 آدرس: {server.host}:{server.port}\n"
                    f"🔗 Inbound ها: {inbounds_count}\n"
                    f"👤 کلاینت‌ها: {total_clients}\n"
                    f"🔧 وضعیت: {'فعال' if server.is_active else 'غیرفعال'}"
                )
                
                await query.edit_message_text(message, parse_mode='Markdown')
            
        except XUIServer.DoesNotExist:
            await query.edit_message_text("❌ سرور یافت نشد!")
    
    async def handle_inbound_callback(self, query, context, data):
        """پردازش callback inbound"""
        inbound_id = data.split('_')[1]
        action = data.split('_')[2]
        
        try:
            inbound = await sync_to_async(XUIInbound.objects.get)(id=inbound_id)
            
            if action == 'info':
                clients_count = await sync_to_async(inbound.clients.count)()
                available_slots = await sync_to_async(inbound.get_available_slots)()
                
                message = (
                    f"🔗 **اطلاعات Inbound {inbound.remark}**\n\n"
                    f"🖥️ سرور: {inbound.server.name}\n"
                    f"🔌 پورت: {inbound.port}\n"
                    f"📡 پروتکل: {inbound.protocol}\n"
                    f"👤 کلاینت‌ها: {clients_count}/{inbound.max_clients}\n"
                    f"📊 اسلات خالی: {available_slots}\n"
                    f"🔧 وضعیت: {'فعال' if inbound.is_active else 'غیرفعال'}"
                )
                
                await query.edit_message_text(message, parse_mode='Markdown')
            
        except XUIInbound.DoesNotExist:
            await query.edit_message_text("❌ Inbound یافت نشد!")
    
    async def handle_client_callback(self, query, context, data):
        """پردازش callback کلاینت"""
        client_id = data.split('_')[1]
        action = data.split('_')[2]
        
        try:
            client = await sync_to_async(XUIClient.objects.get)(id=client_id)
            
            if action == 'info':
                remaining_gb = await sync_to_async(client.get_remaining_gb)()
                is_expired = await sync_to_async(client.is_expired)()
                expiry_status = "منقضی شده" if is_expired else "فعال"
                
                message = (
                    f"👤 **اطلاعات کلاینت {client.email}**\n\n"
                    f"👤 کاربر: {client.user.full_name}\n"
                    f"🔗 Inbound: {client.inbound.remark}\n"
                    f"📊 حجم باقی‌مانده: {remaining_gb} GB\n"
                    f"⏰ وضعیت انقضا: {expiry_status}\n"
                    f"🔧 وضعیت: {'فعال' if client.is_active else 'غیرفعال'}"
                )
                
                await query.edit_message_text(message, parse_mode='Markdown')
            
        except XUIClient.DoesNotExist:
            await query.edit_message_text("❌ کلاینت یافت نشد!")
    
    async def handle_admin_message(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """پردازش پیام‌های ادمین (پاسخ به تیکت)"""
        user_id = update.effective_user.id
        
        if not await self.is_admin(user_id):
            return
        
        text = update.message.text
        
        # بررسی پاسخ به تیکت
        if context.user_data.get('admin_state') == 'replying_ticket':
            ticket_id = context.user_data.get('replying_to_ticket')
            
            if text.lower() in ['لغو', 'cancel', 'انصراف']:
                context.user_data.pop('admin_state', None)
                context.user_data.pop('replying_to_ticket', None)
                await update.message.reply_text(
                    "❌ **پاسخ لغو شد**",
                    reply_markup=InlineKeyboardMarkup([[
                        InlineKeyboardButton("🔙 بازگشت", callback_data="admin_tickets")
                    ]])
                )
                return
            
            try:
                ticket = await sync_to_async(MessageDirectory.objects.get)(id=ticket_id)
                
                # ذخیره پاسخ در دیتابیس
                def save_reply():
                    return MessageModel.objects.create(
                        directory=ticket,
                        messages=f"👨‍💼 **پاسخ ادمین:**\n{text}"
                    )
                
                message = await sync_to_async(save_reply)()
                logger.info(f"✅ پاسخ ادمین در دیتابیس ذخیره شد: Message ID: {message.id}, Ticket ID: {ticket_id}")
                
                # ارسال پاسخ به کاربر
                try:
                    from telegram import Bot
                    bot = Bot(token=getattr(settings, 'USER_BOT_TOKEN', ''))
                    
                    # پیام با دکمه‌های تعاملی
                    keyboard = [
                        [
                            InlineKeyboardButton("💬 پاسخ", callback_data="create_ticket"),
                            InlineKeyboardButton("✅ تیکت بسته شد", callback_data="ticket_closed")
                        ]
                    ]
                    
                    await bot.send_message(
                        chat_id=ticket.user.telegram_id,
                        text=(
                            f"💬 **پاسخ ادمین به تیکت #{ticket_id}**\n\n"
                            f"👨‍💼 **پاسخ ادمین:**\n{text}\n\n"
                            f"💡 می‌توانید پاسخ دهید یا تیکت را ببندید.\n\n"
                            f"📝 برای پاسخ، از '💬 ارتباط با ما' استفاده کنید."
                        ),
                        parse_mode='Markdown',
                        reply_markup=InlineKeyboardMarkup(keyboard)
                    )
                    logger.info(f"✅ پاسخ به کاربر ارسال شد: User ID: {ticket.user.telegram_id}, Ticket ID: {ticket_id}")
                except Exception as e:
                    logger.error(f"❌ خطا در ارسال پاسخ به کاربر: {e}", exc_info=True)
                
                # پاک کردن state
                context.user_data.pop('admin_state', None)
                context.user_data.pop('replying_to_ticket', None)
                
                await update.message.reply_text(
                    f"✅ **پاسخ شما ارسال شد!**\n\n"
                    f"👤 **کاربر:** {ticket.user.full_name}\n"
                    f"🆔 **Ticket ID:** `{ticket_id}`",
                    parse_mode='Markdown',
                    reply_markup=InlineKeyboardMarkup([[
                        InlineKeyboardButton("🔙 بازگشت", callback_data="admin_tickets")
                    ]])
                )
                
            except Exception as e:
                logger.error(f"خطا در ارسال پاسخ: {e}")
                await update.message.reply_text(f"❌ خطا در ارسال پاسخ: {e}")
            return
    
    async def handle_all_messages(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """هندلر برای دریافت همه پیام‌ها (برای لاگ)"""
        # این handler فقط برای لاگ استفاده می‌شود
        if update.message:
            user_id = update.effective_user.id if update.effective_user else None
            text_preview = update.message.text[:50] if update.message.text else 'None'
            logger.info(f"📨 دریافت پیام در admin_bot: از کاربر {user_id}, متن: {text_preview}...")
        return  # اجازه می‌دهیم handlers دیگر پیام را پردازش کنند
    
    async def handle_message(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """پردازش پیام‌های متنی"""
        user_id = update.effective_user.id
        
        if not await self.is_admin(user_id):
            return
        
        text = update.message.text
        
        # بررسی اینکه آیا این یک پیام forward شده از user_bot است (تیکت جدید)
        if update.message.forward_from or update.message.forward_from_chat:
            # این یک پیام forward شده است، احتمالاً تیکت
            logger.info(f"📨 دریافت پیام forward شده از کاربر: {user_id}")
            # می‌توانیم این را handle کنیم اگر نیاز باشد
            return
        
        # پردازش لغو
        if text.lower() in ['/cancel', 'cancel', 'لغو']:
            context.user_data.pop('admin_state', None)
            context.user_data.pop('plan_data', None)
            context.user_data.pop('server_data', None)
            context.user_data.pop('inbound_data', None)
            context.user_data.pop('replying_to_ticket', None)
            await update.message.reply_text("✅ عملیات لغو شد.")
            return
        
        # پردازش اضافه کردن پلن
        admin_state = context.user_data.get('admin_state')
        if admin_state == 'adding_plan':
            await self.handle_add_plan_message(update, context, text)
            return
        
        # پردازش اضافه کردن سرور
        if admin_state == 'adding_server':
            await self.handle_add_server_message(update, context, text)
            return
        
        # پردازش ایجاد Inbound
        if admin_state == 'creating_inbound':
            await self.handle_create_inbound_message(update, context, text)
            return
        
        # پردازش پیام‌های عادی
        if text.lower() in ['help', 'راهنما', 'کمک']:
            keyboard = [
                [InlineKeyboardButton("📊 داشبورد", callback_data="admin_dashboard")],
                [InlineKeyboardButton("➕ افزودن پلن", callback_data="admin_add_plan")],
                [InlineKeyboardButton("➕ افزودن سرور", callback_data="admin_add_server")],
                [InlineKeyboardButton("🔙 بازگشت به منو", callback_data="admin_menu")]
            ]
            await update.message.reply_text(
                "📚 **راهنمای دستورات ادمین**\n\n"
                "📊 `/dashboard` - داشبورد کلی\n"
                "🖥️ `/servers` - مدیریت سرورها\n"
                "📦 `/plans` - مدیریت پلن‌ها\n"
                "➕ `/add_plan` - افزودن پلن جدید\n"
                "➕ `/add_server` - افزودن سرور جدید\n"
                "🔗 `/create_inbound` - ایجاد Inbound\n"
                "🔄 `/sync_xui` - همگام‌سازی\n"
                "🧹 `/cleanup` - پاکسازی\n"
                "⏰ `/check_expired` - بررسی منقضی شده",
                parse_mode='Markdown',
                reply_markup=InlineKeyboardMarkup(keyboard)
            )
        else:
            await update.message.reply_text(
                "❓ برای مشاهده راهنما، 'help' یا 'راهنما' را تایپ کنید.\n"
                "💡 یا از دکمه‌های منو استفاده کنید: `/menu`"
            )
    
    async def handle_add_plan_message(self, update: Update, context: ContextTypes.DEFAULT_TYPE, text: str):
        """پردازش پیام‌های اضافه کردن پلن"""
        plan_data = context.user_data.get('plan_data', {})
        
        if 'name' not in plan_data:
            plan_data['name'] = text
            context.user_data['plan_data'] = plan_data
            await update.message.reply_text(
                "✅ نام پلن ثبت شد!\n\n"
                "💰 حالا قیمت را به تومان ارسال کنید:\n"
                "مثال: 50000"
            )
        elif 'price' not in plan_data:
            try:
                plan_data['price'] = int(text)
                context.user_data['plan_data'] = plan_data
                await update.message.reply_text(
                    "✅ قیمت ثبت شد!\n\n"
                    "📶 حالا حجم را به مگابایت ارسال کنید:\n"
                    "مثال: 10240 (برای 10 GB)"
                )
            except ValueError:
                await update.message.reply_text("❌ قیمت باید یک عدد باشد! لطفاً دوباره تلاش کنید.")
        elif 'in_volume' not in plan_data:
            try:
                plan_data['in_volume'] = int(text)
                context.user_data['plan_data'] = plan_data
                await update.message.reply_text(
                    "✅ حجم ثبت شد!\n\n"
                    "📝 توضیحات را ارسال کنید (یا برای رد کردن 'skip' بفرستید):"
                )
            except ValueError:
                await update.message.reply_text("❌ حجم باید یک عدد باشد! لطفاً دوباره تلاش کنید.")
        elif 'description' not in plan_data:
            if text.lower() != 'skip':
                plan_data['description'] = text
            context.user_data['plan_data'] = plan_data
            
            # ایجاد پلن در دیتابیس
            try:
                # محاسبه traffic_mb از in_volume (فرض می‌کنیم in_volume به مگابایت است)
                traffic_mb = plan_data['in_volume']
                
                # ایجاد پلن در دیتابیس با sync_to_async
                def create_plan():
                    plan = ConfingPlansModel.objects.create(
                        name=plan_data['name'],
                        price=plan_data['price'],
                        in_volume=plan_data['in_volume'],
                        traffic_mb=traffic_mb,
                        description=plan_data.get('description', ''),
                        is_active=True
                    )
                    # اطمینان از ذخیره شدن
                    plan.save()
                    return plan
                
                plan = await sync_to_async(create_plan)()
                
                # دریافت اطلاعات پلن ذخیره شده
                traffic_gb = await sync_to_async(plan.get_traffic_gb)()
                
                # لاگ ذخیره‌سازی
                logger.info(f"✅ پلن جدید در دیتابیس ذخیره شد: {plan.name} (ID: {plan.id}, Price: {plan.price}, Volume: {plan.in_volume} MB)")
                
                keyboard = [
                    [InlineKeyboardButton("📦 مشاهده پلن‌ها", callback_data="admin_plans")],
                    [InlineKeyboardButton("➕ افزودن پلن دیگر", callback_data="admin_add_plan")],
                    [InlineKeyboardButton("🔙 بازگشت به منو", callback_data="admin_menu")]
                ]
                
                await update.message.reply_text(
                    f"✅ **پلن با موفقیت ایجاد و ذخیره شد!**\n\n"
                    f"📦 **نام:** {plan.name}\n"
                    f"💰 **قیمت:** {plan.price:,} تومان\n"
                    f"📶 **حجم:** {traffic_gb:.2f} GB ({plan.in_volume:,} MB)\n"
                    f"🔧 **وضعیت:** فعال\n"
                    f"🆔 **شناسه:** `{plan.id}`\n\n"
                    f"💾 **وضعیت:** در دیتابیس ذخیره شد ✅",
                    parse_mode='Markdown',
                    reply_markup=InlineKeyboardMarkup(keyboard)
                )
                
                # پاکسازی state
                context.user_data.pop('admin_state', None)
                context.user_data.pop('plan_data', None)
                
            except Exception as e:
                logger.error(f"❌ خطا در ایجاد پلن در دیتابیس: {e}")
                await update.message.reply_text(
                    f"❌ **خطا در ایجاد پلن:**\n\n"
                    f"`{str(e)}`\n\n"
                    f"💡 لطفاً دوباره تلاش کنید یا با پشتیبانی تماس بگیرید.",
                    parse_mode='Markdown'
                )
    
    async def handle_add_server_message(self, update: Update, context: ContextTypes.DEFAULT_TYPE, text: str):
        """پردازش پیام‌های اضافه کردن سرور"""
        server_data = context.user_data.get('server_data', {})
        
        if 'name' not in server_data:
            server_data['name'] = text
            context.user_data['server_data'] = server_data
            await update.message.reply_text(
                "✅ نام سرور ثبت شد!\n\n"
                "🌐 حالا آدرس سرور (IP یا Domain) را ارسال کنید:\n"
                "مثال: 192.168.1.1 یا server.example.com"
            )
        elif 'host' not in server_data:
            server_data['host'] = text
            context.user_data['server_data'] = server_data
            await update.message.reply_text(
                "✅ آدرس سرور ثبت شد!\n\n"
                "🔌 حالا پورت X-UI را ارسال کنید:\n"
                "مثال: 54321"
            )
        elif 'port' not in server_data:
            try:
                server_data['port'] = int(text)
                context.user_data['server_data'] = server_data
                await update.message.reply_text(
                    "✅ پورت ثبت شد!\n\n"
                    "👤 حالا نام کاربری X-UI را ارسال کنید:\n"
                    "مثال: admin"
                )
            except ValueError:
                await update.message.reply_text("❌ پورت باید یک عدد باشد! لطفاً دوباره تلاش کنید.")
        elif 'username' not in server_data:
            server_data['username'] = text
            context.user_data['server_data'] = server_data
            await update.message.reply_text(
                "✅ نام کاربری ثبت شد!\n\n"
                "🔐 حالا رمز عبور X-UI را ارسال کنید:\n"
                "مثال: password123"
            )
        elif 'password' not in server_data:
            server_data['password'] = text
            context.user_data['server_data'] = server_data
            await update.message.reply_text(
                "✅ رمز عبور ثبت شد!\n\n"
                "📁 مسیر وب X-UI را ارسال کنید (یا 'skip' برای استفاده از پیش‌فرض):\n"
                "مثال: /MsxZ4xuIy5xLfQtsSC/"
            )
        elif 'web_base_path' not in server_data:
            if text.lower() != 'skip':
                server_data['web_base_path'] = text
            else:
                server_data['web_base_path'] = "/MsxZ4xuIy5xLfQtsSC/"
            context.user_data['server_data'] = server_data
            
            # ایجاد سرور در دیتابیس
            try:
                # ایجاد سرور در دیتابیس با sync_to_async
                def create_server():
                    server = XUIServer.objects.create(
                        name=server_data['name'],
                        host=server_data['host'],
                        port=server_data['port'],
                        username=server_data['username'],
                        password=server_data['password'],
                        web_base_path=server_data.get('web_base_path', '/MsxZ4xuIy5xLfQtsSC/'),
                        is_active=True
                    )
                    # اطمینان از ذخیره شدن
                    server.save()
                    return server
                
                server = await sync_to_async(create_server)()
                
                # لاگ ذخیره‌سازی
                logger.info(f"✅ سرور جدید در دیتابیس ذخیره شد: {server.name} (ID: {server.id}, Host: {server.host}:{server.port})")
                
                keyboard = [
                    [InlineKeyboardButton("🖥️ مشاهده سرورها", callback_data="admin_servers")],
                    [InlineKeyboardButton("➕ افزودن سرور دیگر", callback_data="admin_add_server")],
                    [InlineKeyboardButton("🔄 همگام‌سازی", callback_data="admin_sync")],
                    [InlineKeyboardButton("🔙 بازگشت به منو", callback_data="admin_menu")]
                ]
                
                await update.message.reply_text(
                    f"✅ **سرور با موفقیت ایجاد و ذخیره شد!**\n\n"
                    f"🖥️ **نام:** {server.name}\n"
                    f"🌐 **آدرس:** {server.host}:{server.port}\n"
                    f"👤 **کاربری:** {server.username}\n"
                    f"📁 **مسیر وب:** {server.web_base_path}\n"
                    f"🔧 **وضعیت:** فعال\n"
                    f"🆔 **شناسه:** `{server.id}`\n\n"
                    f"💾 **وضعیت:** در دیتابیس ذخیره شد ✅\n\n"
                    f"💡 برای همگام‌سازی Inbound ها از دکمه همگام‌سازی استفاده کنید.",
                    parse_mode='Markdown',
                    reply_markup=InlineKeyboardMarkup(keyboard)
                )
                
                # پاکسازی state
                context.user_data.pop('admin_state', None)
                context.user_data.pop('server_data', None)
                
            except Exception as e:
                logger.error(f"❌ خطا در ایجاد سرور در دیتابیس: {e}")
                await update.message.reply_text(
                    f"❌ **خطا در ایجاد سرور:**\n\n"
                    f"`{str(e)}`\n\n"
                    f"💡 لطفاً دوباره تلاش کنید یا با پشتیبانی تماس بگیرید.",
                    parse_mode='Markdown'
                )
    
    async def handle_create_inbound_message(self, update: Update, context: ContextTypes.DEFAULT_TYPE, text: str):
        """پردازش پیام‌های ایجاد Inbound"""
        inbound_data = context.user_data.get('inbound_data', {})
        
        if 'server_id' not in inbound_data:
            await update.message.reply_text("❌ ابتدا سرور را انتخاب کنید!")
            return
        
        if 'remark' not in inbound_data:
            inbound_data['remark'] = text
            context.user_data['inbound_data'] = inbound_data
            await update.message.reply_text(
                "✅ نام Inbound ثبت شد!\n\n"
                "🔌 حالا پورت را ارسال کنید:\n"
                "مثال: 443"
            )
        elif 'port' not in inbound_data:
            try:
                inbound_data['port'] = int(text)
                context.user_data['inbound_data'] = inbound_data
                await update.message.reply_text(
                    "✅ پورت ثبت شد!\n\n"
                    "📡 حالا پروتکل را ارسال کنید (vless/vmess/trojan):\n"
                    "مثال: vless"
                )
            except ValueError:
                await update.message.reply_text("❌ پورت باید یک عدد باشد!")
        elif 'protocol' not in inbound_data:
            protocol = text.lower()
            if protocol not in ['vless', 'vmess', 'trojan']:
                await update.message.reply_text("❌ پروتکل باید یکی از این موارد باشد: vless, vmess, trojan")
                return
            
            inbound_data['protocol'] = protocol
            context.user_data['inbound_data'] = inbound_data
            
            # ایجاد Inbound در X-UI
            try:
                server = await sync_to_async(XUIServer.objects.get)(id=inbound_data['server_id'])
                
                # استفاده از SanaeiXUIAPI برای ایجاد Inbound
                from xui_servers.sanaei_api import SanaeiXUIAPI
                api = SanaeiXUIAPI(
                    host=server.host,
                    port=server.port,
                    username=server.username,
                    password=server.password,
                    web_base_path=server.web_base_path
                )
                
                inbound_id = await sync_to_async(api.create_inbound)(
                    protocol=inbound_data['protocol'],
                    port=inbound_data['port'],
                    remark=inbound_data['remark']
                )
                
                if inbound_id:
                    # ذخیره مستقیم در دیتابیس
                    try:
                        def create_or_update_inbound():
                            inbound_db, created = XUIInbound.objects.get_or_create(
                                server=server,
                                xui_inbound_id=inbound_id,
                                defaults={
                                    'port': inbound_data['port'],
                                    'protocol': inbound_data['protocol'],
                                    'remark': inbound_data['remark'],
                                    'is_active': True,
                                    'max_clients': 100,
                                    'current_clients': 0
                                }
                            )
                            
                            if created:
                                inbound_db.save()
                                logger.info(f"✅ Inbound جدید در دیتابیس ذخیره شد: {inbound_db.remark} (ID: {inbound_db.id}, X-UI ID: {inbound_id})")
                            else:
                                # به‌روزرسانی اطلاعات موجود
                                inbound_db.port = inbound_data['port']
                                inbound_db.protocol = inbound_data['protocol']
                                inbound_db.remark = inbound_data['remark']
                                inbound_db.is_active = True
                                inbound_db.save()
                                logger.info(f"✅ Inbound موجود به‌روزرسانی شد: {inbound_db.remark} (ID: {inbound_db.id})")
                            
                            return inbound_db, created
                        
                        inbound_db, created = await sync_to_async(create_or_update_inbound)()
                        
                    except Exception as db_error:
                        logger.error(f"❌ خطا در ذخیره Inbound در دیتابیس: {db_error}")
                        # حتی اگر ذخیره در دیتابیس خطا داد، همگام‌سازی را انجام می‌دهیم
                        try:
                            enhanced_service = XUIEnhancedService(server)
                            await sync_to_async(enhanced_service.sync_inbounds_to_database)()
                            logger.info(f"✅ همگام‌سازی Inbound انجام شد")
                        except Exception as sync_error:
                            logger.error(f"❌ خطا در همگام‌سازی: {sync_error}")
                    
                    keyboard = [
                        [InlineKeyboardButton("🔗 مشاهده Inbound ها", callback_data="admin_inbounds")],
                        [InlineKeyboardButton("🔄 همگام‌سازی مجدد", callback_data="admin_sync")],
                        [InlineKeyboardButton("🔙 بازگشت به منو", callback_data="admin_menu")]
                    ]
                    
                    # دریافت اطلاعات Inbound از دیتابیس
                    try:
                        inbound_db = await sync_to_async(XUIInbound.objects.get)(
                            server=server,
                            xui_inbound_id=inbound_id
                        )
                        db_id = inbound_db.id
                        db_status = "✅ ذخیره شده در دیتابیس"
                    except XUIInbound.DoesNotExist:
                        db_id = "در حال همگام‌سازی..."
                        db_status = "⚠️ در حال ذخیره..."
                    
                    await update.message.reply_text(
                        f"✅ **Inbound با موفقیت ایجاد و ذخیره شد!**\n\n"
                        f"🆔 **شناسه X-UI:** `{inbound_id}`\n"
                        f"🆔 **شناسه دیتابیس:** `{db_id}`\n"
                        f"🔗 **نام:** {inbound_data['remark']}\n"
                        f"🔌 **پورت:** `{inbound_data['port']}`\n"
                        f"📡 **پروتکل:** `{inbound_data['protocol'].upper()}`\n"
                        f"🖥️ **سرور:** {server.name}\n\n"
                        f"💾 **وضعیت:** {db_status}",
                        parse_mode='Markdown',
                        reply_markup=InlineKeyboardMarkup(keyboard)
                    )
                else:
                    await update.message.reply_text(
                        "❌ **خطا در ایجاد Inbound در X-UI**\n\n"
                        "💡 لطفاً بررسی کنید:\n"
                        "• اتصال به سرور برقرار است\n"
                        "• اطلاعات ورود صحیح است\n"
                        "• پورت در دسترس است",
                        parse_mode='Markdown'
                    )
                
                # پاکسازی state
                context.user_data.pop('admin_state', None)
                context.user_data.pop('inbound_data', None)
                
            except Exception as e:
                logger.error(f"خطا در ایجاد Inbound: {e}")
                await update.message.reply_text(f"❌ خطا در ایجاد Inbound: {e}")
    
    async def is_admin(self, user_id):
        """بررسی دسترسی ادمین - از دیتابیس و تنظیمات"""
        # چک کردن از تنظیمات
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
    
    def run(self):
        """اجرای ربات"""
        import asyncio

        logger.info("ربات ادمین شروع شد...")

        # تنظیمات retry برای خطاهای شبکه
        retry_count = 0
        max_retries = 5
        retry_delay = 5  # ثانیه

        while retry_count < max_retries:
            try:
                self.application.run_polling(
                    drop_pending_updates=True,
                    poll_interval=1.0,
                    timeout=10,
                    bootstrap_retries=3
                )
                retry_count = 0  # reset on success
                break
                
            except (NetworkError, TimedOut) as e:
                retry_count += 1
                logger.warning(f"⚠️ خطای شبکه (تلاش {retry_count}/{max_retries}): {e}")
                
                if retry_count < max_retries:
                    logger.info(f"⏳ منتظر {retry_delay} ثانیه قبل از تلاش مجدد...")
                    time.sleep(retry_delay)
                    retry_delay *= 2  # exponential backoff
                else:
                    logger.error("❌ تعداد تلاش‌های مجدد به پایان رسید. ربات متوقف می‌شود.")
                    raise
                    
            except KeyboardInterrupt:
                logger.info("ربات ادمین متوقف شد (KeyboardInterrupt)")
                break
            except Exception as e:
                logger.error(f"❌ خطا در اجرای ربات: {e}")
                raise

def main():
    """تابع اصلی"""
    logger.info("=" * 60)
    logger.info("🚀 شروع ربات ادمین...")
    logger.info("=" * 60)
    
    if not ADMIN_BOT_TOKEN or ADMIN_BOT_TOKEN == 'YOUR_ADMIN_BOT_TOKEN':
        logger.error("❌ لطفاً ADMIN_BOT_TOKEN را در تنظیمات تنظیم کنید!")
        return
    
    if not ADMIN_USER_IDS:
        logger.error("❌ لطفاً ADMIN_USER_IDS را در تنظیمات تنظیم کنید!")
        return
    
    logger.info(f"✅ توکن ربات: {ADMIN_BOT_TOKEN[:20]}...")
    logger.info(f"✅ ادمین‌ها: {ADMIN_USER_IDS}")
    logger.info("🔄 در حال راه‌اندازی ربات...")
    
    bot = AdminBot()
    logger.info("✅ ربات راه‌اندازی شد!")
    logger.info("📡 در حال اتصال به تلگرام...")
    bot.run()

if __name__ == "__main__":
    main() 