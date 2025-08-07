#!/usr/bin/env python3
"""
ربات ادمین برای مدیریت X-UI
"""

import os
import sys
import django
import logging
from datetime import datetime, timedelta
from django.utils import timezone

# تنظیم Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, CallbackQueryHandler, ContextTypes, filters
from django.conf import settings
from xui_servers.models import XUIServer, XUIInbound, XUIClient, UserConfig
from accounts.models import UsersModel
from xui_servers.services import XUIService, UserConfigService
from xui_servers.enhanced_api_models import XUIEnhancedService, XUIClientManager, XUIInboundManager, XUIAutoManager

# تنظیم لاگینگ
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# تنظیمات ربات ادمین
ADMIN_BOT_TOKEN = getattr(settings, 'ADMIN_BOT_TOKEN', 'YOUR_ADMIN_BOT_TOKEN')
ADMIN_PASSWORD = getattr(settings, 'ADMIN_PASSWORD', 'admin123')  # رمز ادمین
ADMIN_USER_IDS = getattr(settings, 'ADMIN_USER_IDS', [])  # ID های ادمین

class AdminBot:
    def __init__(self):
        self.application = Application.builder().token(ADMIN_BOT_TOKEN).build()
        self.setup_handlers()
    
    def setup_handlers(self):
        """تنظیم هندلرهای ربات"""
        # دستورات اصلی
        self.application.add_handler(CommandHandler("start", self.start_command))
        self.application.add_handler(CommandHandler("login", self.login_command))
        self.application.add_handler(CommandHandler("logout", self.logout_command))
        self.application.add_handler(CommandHandler("dashboard", self.dashboard_command))
        
        # دستورات مدیریت سرور
        self.application.add_handler(CommandHandler("servers", self.servers_command))
        self.application.add_handler(CommandHandler("inbounds", self.inbounds_command))
        self.application.add_handler(CommandHandler("clients", self.clients_command))
        self.application.add_handler(CommandHandler("users", self.users_command))
        
        # دستورات مدیریت
        self.application.add_handler(CommandHandler("create_inbound", self.create_inbound_command))
        self.application.add_handler(CommandHandler("assign_user", self.assign_user_command))
        self.application.add_handler(CommandHandler("sync_xui", self.sync_xui_command))
        
        # دستورات پاکسازی خودکار
        self.application.add_handler(CommandHandler("cleanup", self.cleanup_command))
        self.application.add_handler(CommandHandler("check_expired", self.check_expired_command))
        
        # هندلرهای callback
        self.application.add_handler(CallbackQueryHandler(self.button_callback))
        
        # هندلر پیام‌های متنی
        self.application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, self.handle_message))
    
    async def start_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """دستور شروع"""
        user_id = update.effective_user.id
        
        if not self.is_admin(user_id):
            await update.message.reply_text(
                "❌ شما دسترسی ادمین ندارید!\n"
                "برای دسترسی با مدیر سیستم تماس بگیرید."
            )
            return
        
        # اگر کاربر ادمین است، به صورت خودکار وارد شود
        context.user_data['logged_in'] = True
        context.user_data['login_time'] = datetime.now()
        
        await update.message.reply_text(
            "🔐 **ربات ادمین X-UI**\n\n"
            "✅ **ورود خودکار موفق!**\n\n"
            "حالا می‌توانید از دستورات زیر استفاده کنید:\n\n"
            "📊 `/dashboard` - داشبورد کلی\n"
            "🖥️ `/servers` - مدیریت سرورها\n"
            "🔗 `/inbounds` - مدیریت Inbound ها\n"
            "👤 `/clients` - مدیریت کلاینت‌ها\n"
            "👥 `/users` - مدیریت کاربران\n"
            "➕ `/create_inbound` - ایجاد Inbound جدید\n"
            "🔗 `/assign_user` - تخصیص کاربر به Inbound\n"
            "🔄 `/sync_xui` - همگام‌سازی با X-UI\n"
            "🧹 `/cleanup` - پاکسازی خودکار\n"
            "⏰ `/check_expired` - بررسی کاربران منقضی شده\n"
            "🚪 `/logout` - خروج از سیستم",
            parse_mode='Markdown'
        )
    
    async def login_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """دستور ورود"""
        user_id = update.effective_user.id
        
        if not self.is_admin(user_id):
            await update.message.reply_text("❌ شما دسترسی ادمین ندارید!")
            return
        
        # اگر کاربر ادمین است و قبلاً وارد نشده، به صورت خودکار وارد شود
        if not context.user_data.get('logged_in'):
            context.user_data['logged_in'] = True
            context.user_data['login_time'] = datetime.now()
            
            await update.message.reply_text(
                "✅ **ورود خودکار موفق!**\n\n"
                "حالا می‌توانید از دستورات زیر استفاده کنید:\n\n"
                "📊 `/dashboard` - داشبورد کلی\n"
                "🖥️ `/servers` - مدیریت سرورها\n"
                "🔗 `/inbounds` - مدیریت Inbound ها\n"
                "👤 `/clients` - مدیریت کلاینت‌ها\n"
                "👥 `/users` - مدیریت کاربران\n"
                "➕ `/create_inbound` - ایجاد Inbound جدید\n"
                "🔗 `/assign_user` - تخصیص کاربر به Inbound\n"
                "🔄 `/sync_xui` - همگام‌سازی با X-UI\n"
                "🧹 `/cleanup` - پاکسازی خودکار\n"
                "⏰ `/check_expired` - بررسی کاربران منقضی شده\n"
                "🚪 `/logout` - خروج از سیستم",
                parse_mode='Markdown'
            )
            return
        
        # اگر کاربر قبلاً وارد شده، پیام مناسب نمایش دهد
        await update.message.reply_text(
            "✅ **شما قبلاً وارد شده‌اید!**\n\n"
            "برای خروج از سیستم از دستور `/logout` استفاده کنید.",
            parse_mode='Markdown'
        )
    
    async def logout_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """دستور خروج"""
        user_id = update.effective_user.id
        
        if not self.is_admin(user_id):
            await update.message.reply_text("❌ شما دسترسی ادمین ندارید!")
            return
        
        context.user_data.clear()
        await update.message.reply_text("✅ **خروج موفق!**")
    
    async def dashboard_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """داشبورد کلی"""
        user_id = update.effective_user.id
        
        if not self.is_admin(user_id):
            await update.message.reply_text("❌ شما دسترسی ادمین ندارید!")
            return
        
        if not context.user_data.get('logged_in'):
            await update.message.reply_text("❌ لطفاً ابتدا وارد شوید: `/login`", parse_mode='Markdown')
            return
        
        try:
            # آمار کلی
            servers_count = XUIServer.objects.filter(is_active=True).count()
            inbounds_count = XUIInbound.objects.filter(is_active=True).count()
            clients_count = XUIClient.objects.filter(is_active=True).count()
            users_count = UsersModel.objects.count()
            configs_count = UserConfig.objects.filter(is_active=True).count()
            
            # آمار کاربران منقضی شده
            expired_configs = UserConfig.objects.filter(
                is_active=True,
                expires_at__lt=timezone.now()
            ).count()
            
            # آمار سرورها
            server_stats = []
            for server in XUIServer.objects.filter(is_active=True):
                inbounds = server.inbounds.filter(is_active=True)
                total_clients = sum(inbound.clients.count() for inbound in inbounds)
                server_stats.append(f"• {server.name}: {inbounds.count()} inbound, {total_clients} کلاینت")
            
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
                parse_mode='Markdown'
            )
            
        except Exception as e:
            await update.message.reply_text(f"❌ خطا در دریافت آمار: {e}")
    
    async def servers_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """مدیریت سرورها"""
        user_id = update.effective_user.id
        
        if not self.is_admin(user_id):
            await update.message.reply_text("❌ شما دسترسی ادمین ندارید!")
            return
        
        if not context.user_data.get('logged_in'):
            await update.message.reply_text("❌ لطفاً ابتدا وارد شوید: `/login`", parse_mode='Markdown')
            return
        
        try:
            servers = XUIServer.objects.filter(is_active=True)
            
            if not servers.exists():
                await update.message.reply_text("❌ هیچ سرور فعالی یافت نشد!")
                return
            
            message = "🖥️ **لیست سرورها:**\n\n"
            
            for server in servers:
                inbounds_count = server.inbounds.filter(is_active=True).count()
                total_clients = 0
                for inbound in server.inbounds.filter(is_active=True):
                    total_clients += inbound.clients.count()
                
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
    
    async def inbounds_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """مدیریت Inbound ها"""
        user_id = update.effective_user.id
        
        if not self.is_admin(user_id):
            await update.message.reply_text("❌ شما دسترسی ادمین ندارید!")
            return
        
        if not context.user_data.get('logged_in'):
            await update.message.reply_text("❌ لطفاً ابتدا وارد شوید: `/login`", parse_mode='Markdown')
            return
        
        try:
            inbounds = XUIInbound.objects.filter(is_active=True)
            
            if not inbounds.exists():
                await update.message.reply_text("❌ هیچ Inbound فعالی یافت نشد!")
                return
            
            message = "🔗 **لیست Inbound ها:**\n\n"
            
            for inbound in inbounds:
                clients_count = inbound.clients.count()
                available_slots = inbound.get_available_slots()
                status = "🟢 فعال" if inbound.is_active else "🔴 غیرفعال"
                
                message += (
                    f"**{inbound.remark}**\n"
                    f"🖥️ سرور: {inbound.server.name}\n"
                    f"🔌 پورت: {inbound.port}\n"
                    f"📡 پروتکل: {inbound.protocol}\n"
                    f"👤 کلاینت‌ها: {clients_count}/{inbound.max_clients}\n"
                    f"📊 اسلات خالی: {available_slots}\n"
                    f"🔧 {status}\n\n"
                )
            
            await update.message.reply_text(message, parse_mode='Markdown')
            
        except Exception as e:
            await update.message.reply_text(f"❌ خطا در دریافت Inbound ها: {e}")
    
    async def clients_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """مدیریت کلاینت‌ها"""
        user_id = update.effective_user.id
        
        if not self.is_admin(user_id):
            await update.message.reply_text("❌ شما دسترسی ادمین ندارید!")
            return
        
        if not context.user_data.get('logged_in'):
            await update.message.reply_text("❌ لطفاً ابتدا وارد شوید: `/login`", parse_mode='Markdown')
            return
        
        try:
            clients = XUIClient.objects.filter(is_active=True)
            
            if not clients.exists():
                await update.message.reply_text("❌ هیچ کلاینت فعالی یافت نشد!")
                return
            
            message = "👤 **لیست کلاینت‌ها:**\n\n"
            
            for client in clients:
                remaining_gb = client.get_remaining_gb()
                expiry_status = "منقضی شده" if client.is_expired() else "فعال"
                status = "🟢 فعال" if client.is_active else "🔴 غیرفعال"
                
                message += (
                    f"**{client.email}**\n"
                    f"👤 کاربر: {client.user.full_name}\n"
                    f"🔗 Inbound: {client.inbound.remark}\n"
                    f"📊 حجم باقی‌مانده: {remaining_gb} GB\n"
                    f"⏰ وضعیت انقضا: {expiry_status}\n"
                    f"🔧 {status}\n\n"
                )
            
            await update.message.reply_text(message, parse_mode='Markdown')
            
        except Exception as e:
            await update.message.reply_text(f"❌ خطا در دریافت کلاینت‌ها: {e}")
    
    async def users_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """مدیریت کاربران"""
        user_id = update.effective_user.id
        
        if not self.is_admin(user_id):
            await update.message.reply_text("❌ شما دسترسی ادمین ندارید!")
            return
        
        if not context.user_data.get('logged_in'):
            await update.message.reply_text("❌ لطفاً ابتدا وارد شوید: `/login`", parse_mode='Markdown')
            return
        
        try:
            users = UsersModel.objects.all()
            
            if not users.exists():
                await update.message.reply_text("❌ هیچ کاربری یافت نشد!")
                return
            
            message = "👥 **لیست کاربران:**\n\n"
            
            for user in users:
                configs_count = user.xui_configs.filter(is_active=True).count()
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
    
    async def create_inbound_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """ایجاد Inbound جدید"""
        user_id = update.effective_user.id
        
        if not self.is_admin(user_id):
            await update.message.reply_text("❌ شما دسترسی ادمین ندارید!")
            return
        
        if not context.user_data.get('logged_in'):
            await update.message.reply_text("❌ لطفاً ابتدا وارد شوید: `/login`", parse_mode='Markdown')
            return
        
        await update.message.reply_text(
            "🔄 **ایجاد Inbound جدید**\n\n"
            "این قابلیت در حال توسعه است...\n\n"
            "💡 **نکته:** شما می‌توانید Inbound ها را مستقیماً در X-UI ایجاد کنید و سپس با دستور `/sync_xui` آن‌ها را همگام‌سازی کنید.",
            parse_mode='Markdown'
        )
    
    async def assign_user_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """تخصیص کاربر به Inbound"""
        user_id = update.effective_user.id
        
        if not self.is_admin(user_id):
            await update.message.reply_text("❌ شما دسترسی ادمین ندارید!")
            return
        
        if not context.user_data.get('logged_in'):
            await update.message.reply_text("❌ لطفاً ابتدا وارد شوید: `/login`", parse_mode='Markdown')
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
        
        if not self.is_admin(user_id):
            await update.message.reply_text("❌ شما دسترسی ادمین ندارید!")
            return
        
        if not context.user_data.get('logged_in'):
            await update.message.reply_text("❌ لطفاً ابتدا وارد شوید: `/login`", parse_mode='Markdown')
            return
        
        try:
            await update.message.reply_text("🔄 **شروع همگام‌سازی با X-UI...**")
            
            total_synced = 0
            for server in XUIServer.objects.filter(is_active=True):
                try:
                    enhanced_service = XUIEnhancedService(server)
                    synced_count = enhanced_service.sync_inbounds_to_database()
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
        
        if not self.is_admin(user_id):
            await update.message.reply_text("❌ شما دسترسی ادمین ندارید!")
            return
        
        if not context.user_data.get('logged_in'):
            await update.message.reply_text("❌ لطفاً ابتدا وارد شوید: `/login`", parse_mode='Markdown')
            return
        
        try:
            await update.message.reply_text("🧹 **شروع پاکسازی خودکار...**")
            
            total_cleaned = 0
            for server in XUIServer.objects.filter(is_active=True):
                try:
                    auto_manager = XUIAutoManager(server)
                    results = auto_manager.run_cleanup()
                    
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
        
        if not self.is_admin(user_id):
            await update.message.reply_text("❌ شما دسترسی ادمین ندارید!")
            return
        
        if not context.user_data.get('logged_in'):
            await update.message.reply_text("❌ لطفاً ابتدا وارد شوید: `/login`", parse_mode='Markdown')
            return
        
        try:
            # بررسی کانفیگ‌های منقضی شده
            expired_configs = UserConfig.objects.filter(
                is_active=True,
                expires_at__lt=timezone.now()
            )
            
            if not expired_configs.exists():
                await update.message.reply_text(
                    "✅ **بررسی کاربران منقضی شده**\n\n"
                    "📊 هیچ کانفیگ منقضی شده‌ای یافت نشد.",
                    parse_mode='Markdown'
                )
                return
            
            message = "⏰ **کانفیگ‌های منقضی شده:**\n\n"
            
            for config in expired_configs[:10]:  # فقط 10 مورد اول
                days_expired = (timezone.now() - config.expires_at).days
                message += (
                    f"**{config.config_name}**\n"
                    f"👤 کاربر: {config.user.full_name}\n"
                    f"🖥️ سرور: {config.server.name}\n"
                    f"📅 منقضی شده: {days_expired} روز پیش\n\n"
                )
            
            if expired_configs.count() > 10:
                message += f"... و {expired_configs.count() - 10} مورد دیگر\n\n"
            
            message += f"💡 برای پاکسازی از دستور `/cleanup` استفاده کنید."
            
            await update.message.reply_text(message, parse_mode='Markdown')
            
        except Exception as e:
            await update.message.reply_text(f"❌ خطا در بررسی کاربران منقضی شده: {e}")
    
    async def button_callback(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """پردازش callback دکمه‌ها"""
        query = update.callback_query
        await query.answer()
        
        data = query.data
        
        if data.startswith('server_'):
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
            server = XUIServer.objects.get(id=server_id)
            
            if action == 'info':
                inbounds_count = server.inbounds.filter(is_active=True).count()
                total_clients = 0
                for inbound in server.inbounds.filter(is_active=True):
                    total_clients += inbound.clients.count()
                
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
            inbound = XUIInbound.objects.get(id=inbound_id)
            
            if action == 'info':
                clients_count = inbound.clients.count()
                available_slots = inbound.get_available_slots()
                
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
            client = XUIClient.objects.get(id=client_id)
            
            if action == 'info':
                remaining_gb = client.get_remaining_gb()
                expiry_status = "منقضی شده" if client.is_expired() else "فعال"
                
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
    
    async def handle_message(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """پردازش پیام‌های متنی"""
        user_id = update.effective_user.id
        
        if not self.is_admin(user_id):
            return
        
        if not context.user_data.get('logged_in'):
            await update.message.reply_text("❌ لطفاً ابتدا وارد شوید: `/login`", parse_mode='Markdown')
            return
        
        # پردازش پیام‌های متنی
        text = update.message.text
        
        if text.lower() in ['help', 'راهنما', 'کمک']:
            await update.message.reply_text(
                "📚 **راهنمای دستورات ادمین:**\n\n"
                "🔐 `/login` - ورود خودکار به سیستم\n"
                "🚪 `/logout` - خروج از سیستم\n"
                "📊 `/dashboard` - داشبورد کلی\n"
                "🖥️ `/servers` - مدیریت سرورها\n"
                "🔗 `/inbounds` - مدیریت Inbound ها\n"
                "👤 `/clients` - مدیریت کلاینت‌ها\n"
                "👥 `/users` - مدیریت کاربران\n"
                "➕ `/create_inbound` - ایجاد Inbound جدید\n"
                "🔗 `/assign_user` - تخصیص کاربر به Inbound\n"
                "🔄 `/sync_xui` - همگام‌سازی با X-UI\n"
                "🧹 `/cleanup` - پاکسازی خودکار\n"
                "⏰ `/check_expired` - بررسی کاربران منقضی شده\n\n"
                "💡 **نکته:** کاربران ادمین به صورت خودکار وارد می‌شوند و نیازی به رمز عبور ندارند.",
                parse_mode='Markdown'
            )
        else:
            await update.message.reply_text(
                "❓ برای مشاهده راهنما، 'help' یا 'راهنما' را تایپ کنید."
            )
    
    def is_admin(self, user_id):
        """بررسی دسترسی ادمین"""
        return user_id in ADMIN_USER_IDS
    
    def run(self):
        """اجرای ربات"""
        logger.info("ربات ادمین شروع شد...")
        self.application.run_polling()

def main():
    """تابع اصلی"""
    if not ADMIN_BOT_TOKEN or ADMIN_BOT_TOKEN == 'YOUR_ADMIN_BOT_TOKEN':
        logger.error("لطفاً ADMIN_BOT_TOKEN را در تنظیمات تنظیم کنید!")
        return
    
    if not ADMIN_USER_IDS:
        logger.error("لطفاً ADMIN_USER_IDS را در تنظیمات تنظیم کنید!")
        return
    
    bot = AdminBot()
    bot.run()

if __name__ == "__main__":
    main() 