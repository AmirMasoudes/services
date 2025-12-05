"""
Decorators for bot handlers
"""
import logging
from functools import wraps
from telegram import Update
from telegram.ext import ContextTypes
from asgiref.sync import sync_to_async
from django.conf import settings
from accounts.models import UsersModel

logger = logging.getLogger(__name__)


def error_handler(func):
    """
    Decorator to handle errors in bot handlers
    
    Usage:
        @error_handler
        async def my_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
            # handler code
    """
    @wraps(func)
    async def wrapper(update: Update, context: ContextTypes.DEFAULT_TYPE, *args, **kwargs):
        try:
            return await func(update, context, *args, **kwargs)
        except Exception as e:
            logger.error(f"Error in {func.__name__}: {e}", exc_info=True)
            
            # Try to send error message to user
            try:
                if update and update.message:
                    await update.message.reply_text(
                        "❌ خطا رخ داد. لطفا دوباره تلاش کنید.\n"
                        "اگر مشکل ادامه داشت، با پشتیبانی تماس بگیرید."
                    )
                elif update and update.callback_query:
                    await update.callback_query.answer(
                        "❌ خطا رخ داد. لطفا دوباره تلاش کنید.",
                        show_alert=True
                    )
            except Exception as send_error:
                logger.error(f"Failed to send error message: {send_error}")
            
            return None
    
    return wrapper


async def is_admin(user_id: int) -> bool:
    """
    Check if user is admin
    
    Args:
        user_id: Telegram user ID
    
    Returns:
        True if user is admin, False otherwise
    """
    # Check settings first
    ADMIN_USER_IDS = getattr(settings, 'ADMIN_USER_IDS', [])
    if user_id in ADMIN_USER_IDS:
        return True
    
    # Check database
    try:
        user = await sync_to_async(UsersModel.objects.get)(telegram_id=user_id)
        if user.is_admin or user.is_staff:
            return True
    except UsersModel.DoesNotExist:
        pass
    except Exception as e:
        logger.error(f"Error checking admin status: {e}")
    
    return False


def admin_required(func):
    """
    Decorator to require admin access for bot handlers
    
    Usage:
        @admin_required
        async def admin_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
            # handler code
    """
    @wraps(func)
    @error_handler
    async def wrapper(update: Update, context: ContextTypes.DEFAULT_TYPE, *args, **kwargs):
        user_id = update.effective_user.id
        
        if not await is_admin(user_id):
            await update.message.reply_text(
                "❌ شما دسترسی ادمین ندارید.\n"
                "لطفا با ادمین سیستم تماس بگیرید."
            )
            return None
        
        return await func(update, context, *args, **kwargs)
    
    return wrapper


def user_required(func):
    """
    Decorator to ensure user exists in database
    
    Usage:
        @user_required
        async def user_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
            # handler code
            # user object is available in context.user_data['user']
    """
    @wraps(func)
    @error_handler
    async def wrapper(update: Update, context: ContextTypes.DEFAULT_TYPE, *args, **kwargs):
        from accounts.models import UsersModel
        from asgiref.sync import sync_to_async
        
        user_id = update.effective_user.id
        
        try:
            user = await sync_to_async(UsersModel.objects.get)(telegram_id=user_id)
            context.user_data['user'] = user
        except UsersModel.DoesNotExist:
            # Create user if doesn't exist
            user_data = update.effective_user
            user = await sync_to_async(UsersModel.objects.create)(
                telegram_id=user_id,
                id_tel=str(user_data.id),
                username_tel=user_data.username or "",
                full_name=user_data.full_name or user_data.first_name or "کاربر",
                username=user_data.username or ""
            )
            context.user_data['user'] = user
        
        return await func(update, context, *args, **kwargs)
    
    return wrapper

