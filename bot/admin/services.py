"""
Admin bot business logic services
"""
import logging
from typing import Optional, List, Dict, Any
from datetime import timedelta
from asgiref.sync import sync_to_async
from django.utils import timezone
from django.conf import settings

from accounts.models import UsersModel
from order.models import OrderUserModel, PayMentModel
from plan.models import ConfingPlansModel
from xui_servers.models import XUIServer, XUIInbound, XUIClient, UserConfig
from bot.shared.errors import (
    UserNotFoundError,
    ConfigNotFoundError,
    PlanNotFoundError,
    ServerError
)

logger = logging.getLogger(__name__)


class AdminBotService:
    """Service class for admin bot business logic"""
    
    @staticmethod
    async def get_dashboard_stats() -> Dict[str, Any]:
        """
        Get dashboard statistics
        
        Returns:
            Dictionary with dashboard statistics
        """
        total_users = await sync_to_async(UsersModel.objects.count)()
        active_users = await sync_to_async(
            UsersModel.objects.filter(is_active=True).count
        )()
        total_orders = await sync_to_async(OrderUserModel.objects.count)()
        active_orders = await sync_to_async(
            OrderUserModel.objects.filter(is_active=True).count
        )()
        pending_payments = await sync_to_async(
            PayMentModel.objects.filter(status='pending').count
        )()
        total_servers = await sync_to_async(XUIServer.objects.filter(is_active=True).count)()
        total_configs = await sync_to_async(UserConfig.objects.filter(is_active=True).count)()
        
        return {
            'total_users': total_users,
            'active_users': active_users,
            'total_orders': total_orders,
            'active_orders': active_orders,
            'pending_payments': pending_payments,
            'total_servers': total_servers,
            'total_configs': total_configs,
        }
    
    @staticmethod
    async def get_all_servers() -> List[XUIServer]:
        """
        Get all active servers
        
        Returns:
            List of active servers
        """
        return await sync_to_async(list)(
            XUIServer.objects.filter(is_active=True)
        )
    
    @staticmethod
    async def get_all_users(limit: Optional[int] = None) -> List[UsersModel]:
        """
        Get all users
        
        Args:
            limit: Optional limit on number of users
        
        Returns:
            List of users
        """
        queryset = UsersModel.objects.all().order_by('-created_at')
        if limit:
            queryset = queryset[:limit]
        return await sync_to_async(list)(queryset)
    
    @staticmethod
    async def get_all_plans() -> List[ConfingPlansModel]:
        """
        Get all plans
        
        Returns:
            List of plans
        """
        return await sync_to_async(list)(
            ConfingPlansModel.objects.all().order_by('price')
        )
    
    @staticmethod
    async def get_pending_payments() -> List[PayMentModel]:
        """
        Get pending payments
        
        Returns:
            List of pending payments
        """
        return await sync_to_async(list)(
            PayMentModel.objects.filter(status='pending').select_related('user', 'order').order_by('-created_at')
        )
    
    @staticmethod
    async def approve_payment(payment_id: int, approver: UsersModel) -> bool:
        """
        Approve a payment
        
        Args:
            payment_id: Payment ID
            approver: Admin user approving the payment
        
        Returns:
            True if approved, False otherwise
        
        Raises:
            UserNotFoundError: If payment not found
        """
        try:
            payment = await sync_to_async(PayMentModel.objects.get)(id=payment_id)
            return await sync_to_async(payment.approve)(approver)
        except PayMentModel.DoesNotExist:
            raise UserNotFoundError(f"Payment with id {payment_id} not found")
    
    @staticmethod
    async def reject_payment(payment_id: int, reason: str = "") -> bool:
        """
        Reject a payment
        
        Args:
            payment_id: Payment ID
            reason: Rejection reason
        
        Returns:
            True if rejected, False otherwise
        
        Raises:
            UserNotFoundError: If payment not found
        """
        try:
            payment = await sync_to_async(PayMentModel.objects.get)(id=payment_id)
            return await sync_to_async(payment.reject)(reason)
        except PayMentModel.DoesNotExist:
            raise UserNotFoundError(f"Payment with id {payment_id} not found")
    
    @staticmethod
    async def get_expired_configs() -> List[UserConfig]:
        """
        Get expired configs
        
        Returns:
            List of expired configs
        """
        configs = await sync_to_async(list)(
            UserConfig.objects.filter(is_active=True)
        )
        expired = []
        for config in configs:
            if await sync_to_async(config.is_expired)():
                expired.append(config)
        return expired
    
    @staticmethod
    async def cleanup_expired_configs() -> int:
        """
        Cleanup expired configs
        
        Returns:
            Number of configs cleaned up
        """
        expired = await AdminBotService.get_expired_configs()
        count = 0
        for config in expired:
            config.is_active = False
            await sync_to_async(config.save)()
            count += 1
        return count

