"""
Notification tasks
"""
from celery import shared_task
from loguru import logger
from app.core.celery_app import celery_app
from app.services.notification import NotificationService


@shared_task(bind=True, max_retries=3)
def send_order_notification_task(self, order_id: int):
    """
    Send order notification to admin via Telegram
    
    Args:
        order_id: Order ID
    """
    try:
        from sqlalchemy.ext.asyncio import AsyncSession
        from app.core.database import AsyncSessionLocal
        from app.crud.order import order_crud
        
        async def send_notification():
            async with AsyncSessionLocal() as db:
                order = await order_crud.get_with_relations(db, order_id)
                if order:
                    notification_service = NotificationService()
                    await notification_service.send_order_notification(order)
        
        import asyncio
        asyncio.run(send_notification())
        
    except Exception as e:
        logger.error(f"Failed to send order notification: {str(e)}")
        raise self.retry(exc=e, countdown=60)


@shared_task
def send_ticket_answer_task(user_tg_id: int, telegram_message_id: int, answer: str):
    """
    Send ticket answer to user via Telegram
    
    Args:
        user_tg_id: User Telegram ID
        telegram_message_id: Telegram message ID
        answer: Answer text
    """
    try:
        import asyncio
        from app.services.notification import NotificationService
        
        async def send_answer():
            notification_service = NotificationService()
            await notification_service.send_ticket_answer(
                user_tg_id,
                telegram_message_id,
                answer
            )
        
        asyncio.run(send_answer())
        
    except Exception as e:
        logger.error(f"Failed to send ticket answer: {str(e)}")

