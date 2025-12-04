"""
Notification service for Telegram notifications
"""
from typing import Optional
from loguru import logger
from telegram import Bot
from telegram.error import TelegramError
from app.core.config import settings


class NotificationService:
    """Service for sending notifications via Telegram"""
    
    def __init__(self):
        """Initialize notification service"""
        self.bot_token = settings.TELEGRAM_BOT_TOKEN
        self.admin_id = settings.TELEGRAM_ADMIN_ID
        self.bot: Optional[Bot] = None
        
        if self.bot_token:
            try:
                self.bot = Bot(token=self.bot_token)
            except Exception as e:
                logger.error(f"Failed to initialize Telegram bot: {str(e)}")
    
    async def send_message(
        self,
        chat_id: str,
        message: str,
        parse_mode: str = "HTML"
    ) -> bool:
        """
        Send a message to a Telegram chat
        
        Args:
            chat_id: Telegram chat ID
            message: Message text
            parse_mode: Message parse mode (HTML or Markdown)
            
        Returns:
            True if sent successfully, False otherwise
        """
        if not self.bot:
            logger.warning("Telegram bot not initialized")
            return False
        
        try:
            await self.bot.send_message(
                chat_id=chat_id,
                text=message,
                parse_mode=parse_mode
            )
            return True
        except TelegramError as e:
            logger.error(f"Failed to send Telegram message: {str(e)}")
            return False
        except Exception as e:
            logger.error(f"Unexpected error sending message: {str(e)}")
            return False
    
    async def send_order_notification(self, order) -> bool:
        """
        Send notification about new order
        
        Args:
            order: Order model instance
            
        Returns:
            True if sent successfully
        """
        if not self.admin_id:
            logger.warning("Admin Telegram ID not configured")
            return False
        
        user_info = f"User: {order.user.username if order.user else 'N/A'} (ID: {order.user_id})" if order.user_id else "Anonymous user"
        
        message = f"""
🛒 <b>New Order Received</b>

Order ID: <code>{order.id}</code>
{user_info}
Amount: ${float(order.amount):.2f}
Profit: ${float(order.profit):.2f}

Status: {order.status.value}
        """.strip()
        
        return await self.send_message(self.admin_id, message)
    
    async def send_ticket_answer(
        self,
        user_tg_id: int,
        telegram_message_id: Optional[int],
        answer: str
    ) -> bool:
        """
        Send ticket answer to user via Telegram
        
        Args:
            user_tg_id: User Telegram ID
            telegram_message_id: Original Telegram message ID (for reply)
            answer: Answer text
            
        Returns:
            True if sent successfully
        """
        message = f"""
💬 <b>Admin Response</b>

{answer}
        """.strip()
        
        try:
            if telegram_message_id and self.bot:
                # Try to reply to original message
                await self.bot.send_message(
                    chat_id=str(user_tg_id),
                    text=message,
                    reply_to_message_id=telegram_message_id,
                    parse_mode="HTML"
                )
                return True
            else:
                return await self.send_message(str(user_tg_id), message)
        except Exception as e:
            logger.error(f"Failed to send ticket answer: {str(e)}")
            return False


# Global notification service instance
notification_service = NotificationService()

