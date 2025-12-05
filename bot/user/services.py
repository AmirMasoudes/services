"""
User bot business logic services
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
from conf.models import ConfigUserModel, TrialConfigModel
from xui_servers.models import XUIServer, UserConfig, XUIInbound, XUIClient
from xui_servers.services import UserConfigService
from bot.shared.errors import (
    UserNotFoundError,
    ConfigNotFoundError,
    PlanNotFoundError,
    ServerError
)

logger = logging.getLogger(__name__)


class UserBotService:
    """Service class for user bot business logic"""
    
    @staticmethod
    async def get_or_create_user(telegram_id: int, user_data: Any) -> tuple[UsersModel, bool]:
        """
        Get or create user from database
        
        Args:
            telegram_id: Telegram user ID
            user_data: Telegram user object
        
        Returns:
            Tuple of (user, created)
        """
        try:
            user = await sync_to_async(UsersModel.objects.get)(telegram_id=telegram_id)
            # Update user info
            user.id_tel = str(user_data.id)
            user.username_tel = user_data.username or ""
            user.full_name = user_data.full_name or user_data.first_name or "کاربر"
            user.username = user_data.username or ""
            await sync_to_async(user.save)()
            return user, False
        except UsersModel.DoesNotExist:
            # Create new user
            user = await sync_to_async(UsersModel.objects.create)(
                telegram_id=telegram_id,
                id_tel=str(user_data.id),
                username_tel=user_data.username or "",
                full_name=user_data.full_name or user_data.first_name or "کاربر",
                username=user_data.username or ""
            )
            return user, True
    
    @staticmethod
    async def get_user(telegram_id: int) -> UsersModel:
        """
        Get user by telegram ID
        
        Args:
            telegram_id: Telegram user ID
        
        Returns:
            UsersModel instance
        
        Raises:
            UserNotFoundError: If user not found
        """
        try:
            return await sync_to_async(UsersModel.objects.get)(telegram_id=telegram_id)
        except UsersModel.DoesNotExist:
            raise UserNotFoundError(f"User with telegram_id {telegram_id} not found")
    
    @staticmethod
    async def get_user_stats(user: UsersModel) -> Dict[str, Any]:
        """
        Get user statistics
        
        Args:
            user: UsersModel instance
        
        Returns:
            Dictionary with user statistics
        """
        total_orders = await sync_to_async(OrderUserModel.objects.filter(user=user).count)()
        active_orders = await sync_to_async(
            OrderUserModel.objects.filter(user=user, is_active=True).count
        )()
        pending_orders = await sync_to_async(
            OrderUserModel.objects.filter(user=user, is_active=False).count
        )()
        xui_configs = await sync_to_async(
            UserConfig.objects.filter(user=user, is_active=True).count
        )()
        trial_used = await sync_to_async(lambda: user.has_used_trial)()
        
        return {
            'total_orders': total_orders,
            'active_orders': active_orders,
            'pending_orders': pending_orders,
            'xui_configs': xui_configs,
            'trial_used': trial_used,
        }
    
    @staticmethod
    async def get_user_plans(user: UsersModel) -> List[OrderUserModel]:
        """
        Get user's active plans
        
        Args:
            user: UsersModel instance
        
        Returns:
            List of active orders
        """
        return await sync_to_async(list)(
            OrderUserModel.objects.filter(user=user, is_active=True).select_related('plan')
        )
    
    @staticmethod
    async def get_user_configs(user: UsersModel) -> List[UserConfig]:
        """
        Get user's active configs
        
        Args:
            user: UsersModel instance
        
        Returns:
            List of active configs
        """
        configs = await sync_to_async(list)(
            UserConfig.objects.filter(user=user, is_active=True).select_related('server', 'inbound')
        )
        # Filter out expired configs
        active_configs = []
        for config in configs:
            if not await sync_to_async(config.is_expired)():
                active_configs.append(config)
        return active_configs
    
    @staticmethod
    async def can_get_trial(user: UsersModel) -> bool:
        """
        Check if user can get trial plan
        
        Args:
            user: UsersModel instance
        
        Returns:
            True if user can get trial, False otherwise
        """
        return await sync_to_async(lambda: user.can_get_trial)()
    
    @staticmethod
    async def get_available_plans() -> List[ConfingPlansModel]:
        """
        Get all available plans
        
        Returns:
            List of available plans
        """
        return await sync_to_async(list)(
            ConfingPlansModel.objects.filter(is_active=True).order_by('price')
        )
    
    @staticmethod
    async def get_plan(plan_id: int) -> ConfingPlansModel:
        """
        Get plan by ID
        
        Args:
            plan_id: Plan ID
        
        Returns:
            ConfingPlansModel instance
        
        Raises:
            PlanNotFoundError: If plan not found
        """
        try:
            return await sync_to_async(ConfingPlansModel.objects.get)(id=plan_id, is_active=True)
        except ConfingPlansModel.DoesNotExist:
            raise PlanNotFoundError(f"Plan with id {plan_id} not found")
    
    @staticmethod
    async def create_trial_config(user: UsersModel) -> UserConfig:
        """
        Create trial config for user
        
        Args:
            user: UsersModel instance
        
        Returns:
            UserConfig instance
        
        Raises:
            ServerError: If config creation fails
        """
        if not await UserBotService.can_get_trial(user):
            raise ServerError("User has already used trial plan")
        
        try:
            # Get available server
            servers = await sync_to_async(list)(
                XUIServer.objects.filter(is_active=True)
            )
            if not servers:
                raise ServerError("No active servers available")
            
            server = servers[0]  # Use first available server
            
            # Create trial config using service
            service = UserConfigService()
            config = await sync_to_async(service.create_trial_config)(user, server)
            
            # Mark trial as used
            await sync_to_async(user.mark_trial_used)()
            
            return config
        except Exception as e:
            logger.error(f"Error creating trial config: {e}", exc_info=True)
            raise ServerError(f"Failed to create trial config: {str(e)}")
    
    @staticmethod
    async def create_order(user: UsersModel, plan: ConfingPlansModel) -> OrderUserModel:
        """
        Create order for user
        
        Args:
            user: UsersModel instance
            plan: ConfingPlansModel instance
        
        Returns:
            OrderUserModel instance
        """
        order = await sync_to_async(OrderUserModel.objects.create)(
            user=user,
            plan=plan,
            status='pending',
            total_amount=plan.price
        )
        return order
    
    @staticmethod
    async def create_payment(
        user: UsersModel,
        order: OrderUserModel,
        code_pay: int,
        image: Any
    ) -> PayMentModel:
        """
        Create payment record
        
        Args:
            user: UsersModel instance
            order: OrderUserModel instance
            code_pay: Payment code
            image: Payment receipt image
        
        Returns:
            PayMentModel instance
        """
        payment = await sync_to_async(PayMentModel.objects.create)(
            user=user,
            order=order,
            code_pay=code_pay,
            images=image,
            status='pending'
        )
        return payment

