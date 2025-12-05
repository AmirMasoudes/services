"""
Error handling utilities for Telegram bots
"""
import logging
from typing import Optional
from telegram import Update
from telegram.ext import ContextTypes

logger = logging.getLogger(__name__)


class BotError(Exception):
    """Base exception for bot errors"""
    pass


class UserNotFoundError(BotError):
    """User not found in database"""
    pass


class PermissionDeniedError(BotError):
    """User doesn't have required permissions"""
    pass


class ConfigNotFoundError(BotError):
    """Config not found"""
    pass


class PlanNotFoundError(BotError):
    """Plan not found"""
    pass


class ServerError(BotError):
    """Server/X-UI error"""
    pass


async def handle_error(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
    error: Exception,
    user_message: Optional[str] = None
) -> None:
    """
    Handle errors and send appropriate messages to users
    
    Args:
        update: Telegram update object
        context: Bot context
        error: Exception that occurred
        user_message: Custom message to send to user (optional)
    """
    logger.error(f"Error occurred: {error}", exc_info=True)
    
    # Default error messages based on error type
    if user_message is None:
        if isinstance(error, UserNotFoundError):
            user_message = "❌ کاربر یافت نشد. لطفا دوباره تلاش کنید."
        elif isinstance(error, PermissionDeniedError):
            user_message = "❌ شما دسترسی لازم را ندارید."
        elif isinstance(error, ConfigNotFoundError):
            user_message = "❌ کانفیگ یافت نشد."
        elif isinstance(error, PlanNotFoundError):
            user_message = "❌ پلن یافت نشد."
        elif isinstance(error, ServerError):
            user_message = "❌ خطا در ارتباط با سرور. لطفا بعدا تلاش کنید."
        else:
            user_message = "❌ خطا رخ داد. لطفا دوباره تلاش کنید."
    
    # Try to send error message
    try:
        if update and update.message:
            await update.message.reply_text(user_message)
        elif update and update.callback_query:
            await update.callback_query.answer(user_message, show_alert=True)
    except Exception as send_error:
        logger.error(f"Failed to send error message: {send_error}")

