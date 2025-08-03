#!/usr/bin/env python3
"""
ربات ادمین برای مدیریت X-UI
"""

import os
import sys
import django
import logging
from datetime import datetime, timedelta

# تنظیم Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, CallbackQueryHandler, ContextTypes, filters
from django.conf import settings
from xui_servers.models import XUIServer, XUIInbound, XUIClient, UserConfig
from accounts.models import UsersModel
from xui_servers.services import XUIService, UserConfigService
from xui_servers.enhanced_api_models import XUIEnhancedService

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
        
        await update.message.reply_text(
            "🔐 **ربات ادمین X-UI**\n\n"
            "برای ورود به سیستم از دستور زیر استفاده کنید:\n"
            "`/login [رمز عبور]`\n\n"
            "مثال:\n"
            "`/login admin123`",
            parse_mode='Markdown'
        )
    
    async def login_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """دستور ورود"""
        user_id = update.effective_user.id
        
        if not self.is_admin(user_id):
            await update.message.reply_text("❌ شما دسترسی ادمین ندارید!")
            return
        
        if len(context.args) < 1:
            await update.message.reply_text(
                "❌ لطفاً رمز عبور را وارد کنید:\n"
                "`/login [رمز عبور]`",
                parse_mode='Markdown'
            )
            return
        
        password = context.args[0]
        
        if password == ADMIN_PASSWORD:
            # ذخیره وضعیت لاگین
            context.user_data['logged_in'] = True
            context.user_data['login_time'] = datetime.now()
            
            await update.message.reply_text(
                "✅ **ورود موفق!**\n\n"
                "حالا می‌توانید از دستورات زیر استفاده کنید:\n\n"
                "📊 `/dashboard` - داشبورد کلی\n"
                "🖥️ `/servers` - مدیریت سرورها\n"
                "🔗 `/inbounds` - مدیریت Inbound ها\n"
                "👤 `/clients` - مدیریت کلاینت‌ها\n"
                "👥 `/users` - مدیریت کاربران\n"
                "➕ `/create_inbound` - ایجاد Inbound جدید\n"
                "🔗 `/assign_user` - تخصیص کاربر به Inbound\n"
                "🔄 `/sync_xui` - همگام‌سازی با X-UI\n"
                "🚪 `/logout` - خروج از سیستم",
                parse_mode='Markdown'
            )
        else:
            await update.message.reply_text(
                "❌ **رمز عبور نامعتبر!**\n\n"
                "لطفاً رمز عبور صحیح را وارد کنید.",
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
            await update.message.reply_text("❌ لطفاً ابتدا وارد شوید: `/login [رمز عبور]`", parse_mode='Markdown')
            return
        
        try:
            # آمار کلی
            servers_count = XUIServer.objects.filter(is_active=True).count()
            inbounds_count = XUIInbound.objects.filter(is_active=True).count()
            clients_count = XUIClient.objects.filter(is_active=True).count()
            users_count = UsersModel.objects.count()
            configs_count = UserConfig.objects.filter(is_active=True).count()
            
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
                f"📋 **کانفیگ‌ها:** {configs_count}\n\n"
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
            await update.message.reply_text("❌ لطفاً ابتدا وارد شوید: `/login [رمز عبور]`", parse_mode='Markdown')
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
            await update.message.reply_text("❌ لطفاً ابتدا وارد شوید: `/login [رمز عبور]`", parse_mode='Markdown')
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
            await update.message.reply_text("❌ لطفاً ابتدا وارد شوید: `/login [رمز عبور]`", parse_mode='Markdown')
            return
        
        try:
            clients = XUIClient.objects.filter(is_active=True)[:10]  # فقط 10 مورد اول
            
            if not clients.exists():
                await update.message.reply_text("❌ هیچ کلاینت فعالی یافت نشد!")
                return
            
            message = "👤 **لیست کلاینت‌ها (10 مورد اول):**\n\n"
            
            for client in clients:
                remaining_gb = client.get_remaining_gb()
                expiry_status = "منقضی شده" if client.is_expired() else "فعال"
                
                message += (
                    f"**{client.email}**\n"
                    f"👤 کاربر: {client.user.full_name}\n"
                    f"🔗 Inbound: {client.inbound.remark}\n"
                    f"📊 حجم: {remaining_gb} GB باقی‌مانده\n"
                    f"⏰ انقضا: {expiry_status}\n\n"
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
            await update.message.reply_text("❌ لطفاً ابتدا وارد شوید: `/login [رمز عبور]`", parse_mode='Markdown')
            return
        
        try:
            users = UsersModel.objects.all()[:10]  # فقط 10 مورد اول
            
            if not users.exists():
                await update.message.reply_text("❌ هیچ کاربری یافت نشد!")
                return
            
            message = "👥 **لیست کاربران (10 مورد اول):**\n\n"
            
            for user in users:
                configs_count = user.xui_configs.filter(is_active=True).count()
                clients_count = user.xui_clients.filter(is_active=True).count()
                
                message += (
                    f"**{user.full_name}**\n"
                    f"📱 تلگرام: @{user.username_tel}\n"
                    f"📋 کانفیگ‌ها: {configs_count}\n"
                    f"👤 کلاینت‌ها: {clients_count}\n\n"
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
            await update.message.reply_text("❌ لطفاً ابتدا وارد شوید: `/login [رمز عبور]`", parse_mode='Markdown')
            return
        
        if len(context.args) < 4:
            await update.message.reply_text(
                "❌ لطفاً پارامترهای مورد نیاز را وارد کنید:\n"
                "`/create_inbound [سرور] [پورت] [پروتکل] [نام]`\n\n"
                "مثال:\n"
                "`/create_inbound سرور1 12345 vless Test Inbound`",
                parse_mode='Markdown'
            )
            return
        
        try:
            server_name = context.args[0]
            port = int(context.args[1])
            protocol = context.args[2]
            remark = " ".join(context.args[3:])
            
            # یافتن سرور
            server = XUIServer.objects.filter(name=server_name, is_active=True).first()
            if not server:
                await update.message.reply_text(f"❌ سرور '{server_name}' یافت نشد!")
                return
            
            # بررسی تکراری نبودن پورت
            if XUIInbound.objects.filter(server=server, port=port).exists():
                await update.message.reply_text(f"❌ پورت {port} در سرور {server_name} قبلاً استفاده شده!")
                return
            
            # ایجاد Inbound در X-UI
            xui_service = XUIService(server)
            if not xui_service.login():
                await update.message.reply_text(f"❌ خطا در ورود به سرور {server_name}!")
                return
            
            # ایجاد Inbound با استفاده از مدل‌های پیشرفته
            from xui_servers.enhanced_api_models import XUIInboundCreationRequest, XUIInboundManager
            import requests
            
            session = requests.Session()
            base_url = server.get_full_url()
            
            # لاگین
            login_data = {
                "username": server.username,
                "password": server.password
            }
            
            response = session.post(
                f"{base_url}/login",
                json=login_data,
                headers={'Content-Type': 'application/json'},
                timeout=10
            )
            
            if response.status_code == 200:
                inbound_request = XUIInboundCreationRequest(
                    port=port,
                    protocol=protocol,
                    remark=remark
                )
                
                inbound_manager = XUIInboundManager(base_url, session)
                inbound_id = inbound_manager.create_inbound(inbound_request)
                
                if inbound_id:
                    # ایجاد رکورد در دیتابیس
                    XUIInbound.objects.create(
                        server=server,
                        xui_inbound_id=inbound_id,
                        port=port,
                        protocol=protocol,
                        remark=remark,
                        is_active=True
                    )
                    
                    await update.message.reply_text(
                        f"✅ **Inbound جدید ایجاد شد!**\n\n"
                        f"📝 نام: {remark}\n"
                        f"🖥️ سرور: {server_name}\n"
                        f"🔌 پورت: {port}\n"
                        f"📡 پروتکل: {protocol}\n"
                        f"🆔 ID: {inbound_id}",
                        parse_mode='Markdown'
                    )
                else:
                    await update.message.reply_text("❌ خطا در ایجاد Inbound در X-UI!")
            else:
                await update.message.reply_text("❌ خطا در ورود به X-UI!")
                
        except ValueError:
            await update.message.reply_text("❌ پورت باید عدد باشد!")
        except Exception as e:
            await update.message.reply_text(f"❌ خطا در ایجاد Inbound: {e}")
    
    async def assign_user_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """تخصیص کاربر به Inbound"""
        user_id = update.effective_user.id
        
        if not self.is_admin(user_id):
            await update.message.reply_text("❌ شما دسترسی ادمین ندارید!")
            return
        
        if not context.user_data.get('logged_in'):
            await update.message.reply_text("❌ لطفاً ابتدا وارد شوید: `/login [رمز عبور]`", parse_mode='Markdown')
            return
        
        if len(context.args) < 2:
            await update.message.reply_text(
                "❌ لطفاً پارامترهای مورد نیاز را وارد کنید:\n"
                "`/assign_user [شناسه کاربر] [شناسه Inbound]`\n\n"
                "مثال:\n"
                "`/assign_user 123456789 1`",
                parse_mode='Markdown'
            )
            return
        
        try:
            user_tel_id = context.args[0]
            inbound_id = int(context.args[1])
            
            # یافتن کاربر
            user = UsersModel.objects.filter(id_tel=user_tel_id).first()
            if not user:
                await update.message.reply_text(f"❌ کاربر با شناسه {user_tel_id} یافت نشد!")
                return
            
            # یافتن Inbound
            inbound = XUIInbound.objects.filter(id=inbound_id, is_active=True).first()
            if not inbound:
                await update.message.reply_text(f"❌ Inbound با شناسه {inbound_id} یافت نشد!")
                return
            
            # بررسی ظرفیت Inbound
            if not inbound.can_accept_client():
                await update.message.reply_text(f"❌ Inbound {inbound.remark} ظرفیت ندارد!")
                return
            
            # ایجاد کلاینت در X-UI
            from xui_servers.enhanced_api_models import XUIClientCreationRequest, XUIClientManager
            import requests
            
            session = requests.Session()
            base_url = inbound.server.get_full_url()
            
            # لاگین
            login_data = {
                "username": inbound.server.username,
                "password": inbound.server.password
            }
            
            response = session.post(
                f"{base_url}/login",
                json=login_data,
                headers={'Content-Type': 'application/json'},
                timeout=10
            )
            
            if response.status_code == 200:
                client_request = XUIClientCreationRequest(
                    inbound_id=inbound.xui_inbound_id,
                    email=f"{user.username_tel}@vpn.com",
                    total_gb=0,  # نامحدود
                    expiry_time=0  # نامحدود
                )
                
                client_manager = XUIClientManager(base_url, session)
                if client_manager.add_client(client_request):
                    # ایجاد رکورد کلاینت
                    client = XUIClient.objects.create(
                        inbound=inbound,
                        user=user,
                        xui_client_id=client_request.to_payload()["settings"]["clients"][0]["id"],
                        email=client_request.email,
                        total_gb=0,
                        expiry_time=0
                    )
                    
                    # به‌روزرسانی تعداد کلاینت‌ها
                    inbound.current_clients += 1
                    inbound.save()
                    
                    await update.message.reply_text(
                        f"✅ **کاربر با موفقیت تخصیص داده شد!**\n\n"
                        f"👤 کاربر: {user.full_name}\n"
                        f"🔗 Inbound: {inbound.remark}\n"
                        f"📧 ایمیل: {client.email}\n"
                        f"🆔 کلاینت ID: {client.xui_client_id}",
                        parse_mode='Markdown'
                    )
                else:
                    await update.message.reply_text("❌ خطا در ایجاد کلاینت در X-UI!")
            else:
                await update.message.reply_text("❌ خطا در ورود به X-UI!")
                
        except ValueError:
            await update.message.reply_text("❌ شناسه Inbound باید عدد باشد!")
        except Exception as e:
            await update.message.reply_text(f"❌ خطا در تخصیص کاربر: {e}")
    
    async def sync_xui_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """همگام‌سازی با X-UI"""
        user_id = update.effective_user.id
        
        if not self.is_admin(user_id):
            await update.message.reply_text("❌ شما دسترسی ادمین ندارید!")
            return
        
        if not context.user_data.get('logged_in'):
            await update.message.reply_text("❌ لطفاً ابتدا وارد شوید: `/login [رمز عبور]`", parse_mode='Markdown')
            return
        
        try:
            await update.message.reply_text("🔄 در حال همگام‌سازی با X-UI...")
            
            synced_count = 0
            error_count = 0
            
            for server in XUIServer.objects.filter(is_active=True):
                try:
                    xui_service = XUIService(server)
                    if xui_service.login():
                        # همگام‌سازی Inbound ها
                        inbounds = xui_service.get_inbounds()
                        for xui_inbound in inbounds:
                            inbound, created = XUIInbound.objects.get_or_create(
                                server=server,
                                xui_inbound_id=xui_inbound.get('id'),
                                defaults={
                                    'port': xui_inbound.get('port'),
                                    'protocol': xui_inbound.get('protocol'),
                                    'remark': xui_inbound.get('remark'),
                                    'is_active': True
                                }
                            )
                            
                            if not created:
                                # به‌روزرسانی اطلاعات موجود
                                inbound.port = xui_inbound.get('port', inbound.port)
                                inbound.remark = xui_inbound.get('remark', inbound.remark)
                                inbound.protocol = xui_inbound.get('protocol', inbound.protocol)
                                inbound.save()
                            
                            synced_count += 1
                except Exception as e:
                    error_count += 1
                    logger.error(f"خطا در همگام‌سازی سرور {server.name}: {e}")
            
            await update.message.reply_text(
                f"✅ **همگام‌سازی کامل شد!**\n\n"
                f"📊 تعداد همگام‌سازی شده: {synced_count}\n"
                f"❌ تعداد خطا: {error_count}",
                parse_mode='Markdown'
            )
            
        except Exception as e:
            await update.message.reply_text(f"❌ خطا در همگام‌سازی: {e}")
    
    async def button_callback(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """پاسخ به دکمه‌های inline"""
        query = update.callback_query
        await query.answer()
        
        # پردازش callback data
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
        """پردازش callback Inbound"""
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
            await update.message.reply_text("❌ لطفاً ابتدا وارد شوید: `/login [رمز عبور]`", parse_mode='Markdown')
            return
        
        # پردازش پیام‌های متنی
        text = update.message.text
        
        if text.lower() in ['help', 'راهنما', 'کمک']:
            await update.message.reply_text(
                "📚 **راهنمای دستورات ادمین:**\n\n"
                "🔐 `/login [رمز]` - ورود به سیستم\n"
                "🚪 `/logout` - خروج از سیستم\n"
                "📊 `/dashboard` - داشبورد کلی\n"
                "🖥️ `/servers` - مدیریت سرورها\n"
                "🔗 `/inbounds` - مدیریت Inbound ها\n"
                "👤 `/clients` - مدیریت کلاینت‌ها\n"
                "👥 `/users` - مدیریت کاربران\n"
                "➕ `/create_inbound` - ایجاد Inbound جدید\n"
                "🔗 `/assign_user` - تخصیص کاربر به Inbound\n"
                "🔄 `/sync_xui` - همگام‌سازی با X-UI",
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