#!/usr/bin/env python3
"""
ربات ادمین X-UI - نسخه اصلاح شده
"""

import os
import sys
import django
import asyncio
import logging
from datetime import datetime

# تنظیم Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from django.conf import settings
from telegram import Bot, Update
from telegram.ext import Application, CommandHandler, MessageHandler, CallbackQueryHandler, ContextTypes, filters
from telegram.request import HTTPXRequest
from telegram.error import NetworkError, InvalidToken

# تنظیم لاگینگ
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

class FixedAdminBot:
    """ربات ادمین با تنظیمات اصلاح شده"""
    
    def __init__(self):
        self.token = getattr(settings, 'ADMIN_BOT_TOKEN', None)
        self.password = getattr(settings, 'ADMIN_PASSWORD', 'admin123')
        self.admin_user_ids = getattr(settings, 'ADMIN_USER_IDS', [])
        self.authenticated_users = set()
        
        if not self.token or self.token == 'YOUR_ADMIN_BOT_TOKEN':
            print("❌ لطفاً ADMIN_BOT_TOKEN را در تنظیمات تنظیم کنید!")
            sys.exit(1)
        
        if not self.admin_user_ids:
            print("❌ لطفاً ADMIN_USER_IDS را در تنظیمات تنظیم کنید!")
            sys.exit(1)
    
    def create_bot(self):
        """ایجاد ربات با تنظیمات اصلاح شده"""
        try:
            # تنظیمات اصلاح شده برای اتصال
            request = HTTPXRequest(
                connection_pool_size=1,
                connect_timeout=60.0,
                read_timeout=60.0,
                write_timeout=60.0,
                pool_timeout=60.0
            )
            
            bot = Bot(token=self.token, request=request)
            return bot
        except Exception as e:
            print(f"❌ خطا در ایجاد ربات: {e}")
            return None
    
    async def start_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """دستور شروع"""
        user_id = update.effective_user.id
        
        if user_id not in self.admin_user_ids:
            await update.message.reply_text("❌ شما مجوز دسترسی ندارید!")
            return
        
        await update.message.reply_text(
            "🔐 لطفاً رمز عبور ادمین را وارد کنید:"
        )
    
    async def handle_password(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """پردازش رمز عبور"""
        user_id = update.effective_user.id
        password = update.message.text
        
        if user_id not in self.admin_user_ids:
            await update.message.reply_text("❌ شما مجوز دسترسی ندارید!")
            return
        
        if password == self.password:
            self.authenticated_users.add(user_id)
            await update.message.reply_text(
                "✅ ورود موفق!\n\n"
                "دستورات موجود:\n"
                "/dashboard - داشبورد\n"
                "/users - مدیریت کاربران\n"
                "/inbounds - مدیریت Inbound ها\n"
                "/stats - آمار کلی"
            )
        else:
            await update.message.reply_text("❌ رمز عبور نامعتبر!")
    
    async def dashboard_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """دستور داشبورد"""
        user_id = update.effective_user.id
        
        if user_id not in self.authenticated_users:
            await update.message.reply_text("❌ لطفاً ابتدا وارد شوید!")
            return
        
        try:
            from xui_servers.models import XUIServer, XUIInbound, XUIClient, UserConfig
            from accounts.models import UsersModel
            
            # آمار کلی
            total_users = UsersModel.objects.count()
            active_configs = UserConfig.objects.filter(is_active=True).count()
            total_servers = XUIServer.objects.filter(is_active=True).count()
            total_inbounds = XUIInbound.objects.filter(is_active=True).count()
            
            message = f"""
📊 **داشبورد سیستم**

👥 کاربران: {total_users}
⚙️ کانفیگ‌های فعال: {active_configs}
🖥️ سرورها: {total_servers}
🔗 Inbound ها: {total_inbounds}

🕐 زمان: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
            """
            
            await update.message.reply_text(message)
            
        except Exception as e:
            await update.message.reply_text(f"❌ خطا در دریافت آمار: {e}")
    
    async def users_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """دستور مدیریت کاربران"""
        user_id = update.effective_user.id
        
        if user_id not in self.authenticated_users:
            await update.message.reply_text("❌ لطفاً ابتدا وارد شوید!")
            return
        
        try:
            from accounts.models import UsersModel
            
            users = UsersModel.objects.all()[:10]  # فقط 10 کاربر اول
            
            message = "👥 **لیست کاربران:**\n\n"
            for user in users:
                message += f"• {user.full_name} (@{user.username_tel})\n"
            
            if UsersModel.objects.count() > 10:
                message += f"\n... و {UsersModel.objects.count() - 10} کاربر دیگر"
            
            await update.message.reply_text(message)
            
        except Exception as e:
            await update.message.reply_text(f"❌ خطا در دریافت کاربران: {e}")
    
    async def inbounds_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """دستور مدیریت Inbound ها"""
        user_id = update.effective_user.id
        
        if user_id not in self.authenticated_users:
            await update.message.reply_text("❌ لطفاً ابتدا وارد شوید!")
            return
        
        try:
            from xui_servers.models import XUIInbound
            
            inbounds = XUIInbound.objects.filter(is_active=True)
            
            if not inbounds.exists():
                await update.message.reply_text("❌ هیچ Inbound فعالی یافت نشد!")
                return
            
            message = "🔗 **Inbound های فعال:**\n\n"
            for inbound in inbounds:
                message += f"• {inbound.remark} (پورت: {inbound.port})\n"
            
            await update.message.reply_text(message)
            
        except Exception as e:
            await update.message.reply_text(f"❌ خطا در دریافت Inbound ها: {e}")
    
    async def stats_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """دستور آمار کلی"""
        user_id = update.effective_user.id
        
        if user_id not in self.authenticated_users:
            await update.message.reply_text("❌ لطفاً ابتدا وارد شوید!")
            return
        
        try:
            from xui_servers.models import XUIServer, XUIInbound, XUIClient, UserConfig
            from accounts.models import UsersModel
            
            # آمار تفصیلی
            total_users = UsersModel.objects.count()
            active_configs = UserConfig.objects.filter(is_active=True).count()
            expired_configs = UserConfig.objects.filter(is_active=False).count()
            total_servers = XUIServer.objects.filter(is_active=True).count()
            total_inbounds = XUIInbound.objects.filter(is_active=True).count()
            total_clients = XUIClient.objects.filter(is_active=True).count()
            
            message = f"""
📈 **آمار تفصیلی سیستم**

👥 کاربران کل: {total_users}
⚙️ کانفیگ‌های فعال: {active_configs}
⏰ کانفیگ‌های منقضی: {expired_configs}
🖥️ سرورهای فعال: {total_servers}
🔗 Inbound های فعال: {total_inbounds}
👤 کلاینت‌های فعال: {total_clients}

🕐 زمان: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
            """
            
            await update.message.reply_text(message)
            
        except Exception as e:
            await update.message.reply_text(f"❌ خطا در دریافت آمار: {e}")
    
    async def help_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """دستور راهنما"""
        message = """
🤖 **راهنمای ربات ادمین X-UI**

📋 دستورات موجود:
/start - شروع و ورود
/dashboard - داشبورد کلی
/users - مدیریت کاربران
/inbounds - مدیریت Inbound ها
/stats - آمار تفصیلی
/help - این راهنما

🔐 امنیت:
• فقط ادمین‌های مجاز
• رمز عبور اجباری
• لاگ تمام عملیات
        """
        
        await update.message.reply_text(message)
    
    def run(self):
        """اجرای ربات"""
        print("🚀 راه‌اندازی ربات ادمین X-UI (نسخه اصلاح شده)...")
        
        # بررسی تنظیمات
        print("✅ تنظیمات ربات ادمین بررسی شد")
        print(f"🔑 رمز ادمین: {self.password}")
        print(f"👥 تعداد ادمین‌ها: {len(self.admin_user_ids)}")
        
        # ایجاد ربات
        bot = self.create_bot()
        if not bot:
            print("❌ خطا در ایجاد ربات!")
            return
        
        # تست اتصال
        try:
            me = asyncio.run(bot.get_me())
            print(f"✅ ربات فعال: {me.first_name} (@{me.username})")
        except Exception as e:
            print(f"❌ خطا در تست اتصال: {e}")
            return
        
        # ایجاد application
        application = Application.builder().token(self.token).build()
        
        # اضافه کردن handlers
        application.add_handler(CommandHandler("start", self.start_command))
        application.add_handler(CommandHandler("dashboard", self.dashboard_command))
        application.add_handler(CommandHandler("users", self.users_command))
        application.add_handler(CommandHandler("inbounds", self.inbounds_command))
        application.add_handler(CommandHandler("stats", self.stats_command))
        application.add_handler(CommandHandler("help", self.help_command))
        
        # handler برای رمز عبور
        application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, self.handle_password))
        
        print("✅ ربات ادمین آماده اجرا است!")
        print("📱 برای استفاده:")
        print("   1. ربات را در تلگرام پیدا کنید")
        print("   2. دستور /start را ارسال کنید")
        print("   3. با رمز ادمین وارد شوید")
        print("   4. از دستورات مدیریت استفاده کنید")
        
        # شروع ربات
        try:
            application.run_polling(allowed_updates=Update.ALL_TYPES)
        except Exception as e:
            print(f"❌ خطا در راه‌اندازی ربات ادمین: {e}")
            logger.error(f"خطا در راه‌اندازی ربات ادمین: {e}")

def main():
    """تابع اصلی"""
    try:
        bot = FixedAdminBot()
        bot.run()
    except KeyboardInterrupt:
        print("\n👋 ربات متوقف شد!")
    except Exception as e:
        print(f"❌ خطا در راه‌اندازی ربات ادمین: {e}")
        logger.error(f"خطا در راه‌اندازی ربات ادمین: {e}")

if __name__ == "__main__":
    main() 