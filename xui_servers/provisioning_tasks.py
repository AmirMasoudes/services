"""
Celery Tasks for Subscription Provisioning
Handles provisioning, revoking, and syncing subscriptions with S-UI/X-UI
"""
import logging
from typing import Optional, Dict, Any
from celery import shared_task
from django.db import transaction
from django.utils import timezone
from django.conf import settings

from .models import UserConfig, XUIServer, XUIInbound
from accounts.models import UsersModel
from plan.models import ConfingPlansModel
from order.models import OrderUserModel
from .sui_managers import SUIProvisionService
from .enhanced_api_models import XUIClientManager, XUIInboundManager

logger = logging.getLogger(__name__)


@shared_task(bind=True, max_retries=3, default_retry_delay=60)
def provision_subscription(
    self,
    user_config_id: str,
    idempotency_key: Optional[str] = None
) -> Dict[str, Any]:
    """
    Provision a subscription on S-UI/X-UI
    
    Args:
        user_config_id: UserConfig UUID
        idempotency_key: Idempotency key to prevent duplicates
        
    Returns:
        Dict with success status and details
    """
    try:
        user_config = UserConfig.objects.get(id=user_config_id)
        
        # Check if already provisioned (idempotency)
        if user_config.status == 'active' and user_config.external_id:
            logger.info(f"Subscription {user_config_id} already provisioned (idempotency)")
            return {
                'success': True,
                'message': 'Already provisioned',
                'user_config_id': str(user_config_id),
                'subscription_url': user_config.subscription_url
            }
        
        # Get server
        server = user_config.server
        
        # Determine if S-UI or X-UI
        if server.server_type == 'sui':
            # Use S-UI provisioning
            provision_service = SUIProvisionService(server)
            
            if user_config.is_trial:
                result = provision_service.provision_trial_config(
                    user=user_config.user,
                    protocol=user_config.protocol
                )
            else:
                if not user_config.plan:
                    raise ValueError("Plan required for paid config")
                result = provision_service.provision_paid_config(
                    user=user_config.user,
                    plan=user_config.plan,
                    protocol=user_config.protocol
                )
        else:
            # Use X-UI provisioning
            inbound = user_config.inbound
            if not inbound:
                # Find or create inbound
                inbound_manager = XUIInboundManager(server)
                inbound = inbound_manager.find_best_inbound(user_config.protocol)
                if not inbound:
                    inbound_manager.sync_inbounds()
                    inbound = inbound_manager.find_best_inbound(user_config.protocol)
            
            if not inbound:
                raise ValueError("No available inbound")
            
            client_manager = XUIClientManager(server)
            
            if user_config.is_trial:
                result = client_manager.create_trial_config_sync(
                    user=user_config.user,
                    inbound=inbound
                )
            else:
                if not user_config.plan:
                    raise ValueError("Plan required for paid config")
                result = client_manager.create_user_config_sync(
                    user=user_config.user,
                    plan=user_config.plan,
                    inbound=inbound
                )
        
        if result:
            # Update user_config with provisioned data
            with transaction.atomic():
                user_config.status = 'active'
                user_config.is_active = True
                user_config.external_id = idempotency_key or f"{user_config.user.telegram_id}_{user_config.plan.id if user_config.plan else 'trial'}"
                user_config.last_sync_at = timezone.now()
                user_config.sync_required = False
                user_config.provision_retry_count = 0
                user_config.last_provision_error = None
                
                # Generate subscription URL if not set
                if not user_config.subscription_url:
                    from django.conf import settings
                    base_url = getattr(settings, 'SERVER_DOMAIN', 'localhost')
                    user_config.subscription_url = f"https://{base_url}/api/subscription/{user_config.xui_user_id}"
                
                user_config.save()
            
            logger.info(f"Successfully provisioned subscription {user_config_id}")
            
            # Send notification (if configured)
            send_provision_notification.delay(str(user_config.id))
            
            return {
                'success': True,
                'message': 'Provisioned successfully',
                'user_config_id': str(user_config_id),
                'subscription_url': user_config.subscription_url
            }
        else:
            raise Exception("Provisioning returned None")
            
    except UserConfig.DoesNotExist:
        logger.error(f"UserConfig {user_config_id} not found")
        return {
            'success': False,
            'message': 'UserConfig not found',
            'user_config_id': str(user_config_id)
        }
    except Exception as e:
        logger.error(f"Error provisioning subscription {user_config_id}: {e}", exc_info=True)
        
        # Update retry count
        try:
            user_config = UserConfig.objects.get(id=user_config_id)
            user_config.provision_retry_count += 1
            user_config.last_provision_error = str(e)
            user_config.save()
        except:
            pass
        
        # Retry if not exceeded max retries
        if self.request.retries < self.max_retries:
            raise self.retry(exc=e)
        
        return {
            'success': False,
            'message': str(e),
            'user_config_id': str(user_config_id)
        }


@shared_task(bind=True, max_retries=3, default_retry_delay=60)
def revoke_subscription(
    self,
    user_config_id: str
) -> Dict[str, Any]:
    """
    Revoke a subscription from S-UI/X-UI
    
    Args:
        user_config_id: UserConfig UUID
        
    Returns:
        Dict with success status
    """
    try:
        user_config = UserConfig.objects.get(id=user_config_id)
        
        if user_config.status == 'cancelled':
            logger.info(f"Subscription {user_config_id} already revoked")
            return {
                'success': True,
                'message': 'Already revoked',
                'user_config_id': str(user_config_id)
            }
        
        # Get server
        server = user_config.server
        
        # Determine if S-UI or X-UI
        if server.server_type == 'sui':
            provision_service = SUIProvisionService(server)
            success = provision_service.deprovision_config(user_config)
        else:
            # X-UI deprovisioning
            client_manager = XUIClientManager(server)
            success = client_manager.delete_user_config(user_config)
        
        if success:
            with transaction.atomic():
                user_config.status = 'cancelled'
                user_config.is_active = False
                user_config.save()
            
            logger.info(f"Successfully revoked subscription {user_config_id}")
            
            return {
                'success': True,
                'message': 'Revoked successfully',
                'user_config_id': str(user_config_id)
            }
        else:
            raise Exception("Deprovisioning returned False")
            
    except UserConfig.DoesNotExist:
        logger.error(f"UserConfig {user_config_id} not found")
        return {
            'success': False,
            'message': 'UserConfig not found',
            'user_config_id': str(user_config_id)
        }
    except Exception as e:
        logger.error(f"Error revoking subscription {user_config_id}: {e}", exc_info=True)
        
        if self.request.retries < self.max_retries:
            raise self.retry(exc=e)
        
        return {
            'success': False,
            'message': str(e),
            'user_config_id': str(user_config_id)
        }


@shared_task
def sync_server_stats(server_id: str) -> Dict[str, Any]:
    """
    Sync server statistics from S-UI/X-UI
    
    Args:
        server_id: XUIServer UUID
        
    Returns:
        Dict with sync results
    """
    try:
        server = XUIServer.objects.get(id=server_id)
        
        if server.server_type == 'sui':
            from .sui_managers import SUIInboundManager
            inbound_manager = SUIInboundManager(server)
            synced_count = inbound_manager.sync_inbounds()
        else:
            from .enhanced_api_models import XUIInboundManager
            inbound_manager = XUIInboundManager(server)
            synced_count = inbound_manager.sync_inbounds()
        
        # Update server sync time
        server.last_sync_at = timezone.now()
        server.save()
        
        logger.info(f"Synced {synced_count} inbounds for server {server.name}")
        
        return {
            'success': True,
            'server_id': str(server_id),
            'synced_count': synced_count
        }
        
    except XUIServer.DoesNotExist:
        logger.error(f"Server {server_id} not found")
        return {
            'success': False,
            'message': 'Server not found',
            'server_id': str(server_id)
        }
    except Exception as e:
        logger.error(f"Error syncing server {server_id}: {e}", exc_info=True)
        return {
            'success': False,
            'message': str(e),
            'server_id': str(server_id)
        }


@shared_task
def sync_client_usage(user_config_id: str) -> Dict[str, Any]:
    """
    Sync client usage statistics from S-UI/X-UI
    
    Args:
        user_config_id: UserConfig UUID
        
    Returns:
        Dict with usage data
    """
    try:
        user_config = UserConfig.objects.get(id=user_config_id)
        
        if not user_config.is_active:
            return {
                'success': False,
                'message': 'Config not active',
                'user_config_id': str(user_config_id)
            }
        
        server = user_config.server
        
        if server.server_type == 'sui':
            from .sui_managers import SUIProvisionService
            provision_service = SUIProvisionService(server)
            success = provision_service.sync_client_usage(user_config)
        else:
            # X-UI usage sync
            # TODO: Implement X-UI usage sync
            success = False
        
        if success:
            user_config.last_sync_at = timezone.now()
            user_config.sync_required = False
            user_config.save()
            
            return {
                'success': True,
                'user_config_id': str(user_config_id)
            }
        else:
            return {
                'success': False,
                'message': 'Sync failed',
                'user_config_id': str(user_config_id)
            }
            
    except UserConfig.DoesNotExist:
        logger.error(f"UserConfig {user_config_id} not found")
        return {
            'success': False,
            'message': 'UserConfig not found',
            'user_config_id': str(user_config_id)
        }
    except Exception as e:
        logger.error(f"Error syncing usage for {user_config_id}: {e}", exc_info=True)
        return {
            'success': False,
            'message': str(e),
            'user_config_id': str(user_config_id)
        }


@shared_task
def send_provision_notification(user_config_id: str) -> None:
    """
    Send notification when subscription is provisioned
    
    Args:
        user_config_id: UserConfig UUID
    """
    try:
        user_config = UserConfig.objects.get(id=user_config_id)
        user = user_config.user
        
        # Send Telegram notification if bot token available
        token = getattr(settings, 'USER_BOT_TOKEN', None)
        if token and user.telegram_id:
            from telegram import Bot
            
            bot = Bot(token=token)
            message = (
                f"✅ **کانفیگ شما آماده است!**\n\n"
                f"📋 نام: {user_config.config_name}\n"
                f"🔗 لینک اشتراک:\n`{user_config.subscription_url}`\n\n"
                f"⏰ اعتبار: {user_config.expires_at.strftime('%Y-%m-%d %H:%M') if user_config.expires_at else 'نامحدود'}"
            )
            
            try:
                bot.send_message(
                    chat_id=user.telegram_id,
                    text=message,
                    parse_mode='Markdown'
                )
            except Exception as e:
                logger.error(f"Failed to send notification: {e}")
        
    except Exception as e:
        logger.error(f"Error sending provision notification: {e}", exc_info=True)


@shared_task
def process_paid_order(order_id: str) -> Dict[str, Any]:
    """
    Process a paid order and provision subscription
    
    Args:
        order_id: OrderUserModel UUID
        
    Returns:
        Dict with processing results
    """
    try:
        order = OrderUserModel.objects.get(id=order_id)
        
        if order.status != 'paid':
            return {
                'success': False,
                'message': 'Order not paid',
                'order_id': str(order_id)
            }
        
        # Find or create active server
        server = XUIServer.objects.filter(is_active=True, server_type__in=['xui', 'sui']).first()
        if not server:
            raise ValueError("No active server available")
        
        # Create UserConfig
        user_config = UserConfig.objects.create(
            user=order.user,
            server=server,
            plan=order.plan,
            config_name=f"{order.user.full_name} - {order.plan.name}",
            is_active=False,  # Will be activated after provisioning
            status='pending',
            expires_at=order.end_plane_at,
            protocol='vless',  # Default protocol
            is_trial=False,
            external_id=f"order_{order.order_number}"
        )
        
        # Queue provisioning
        provision_subscription.delay(
            str(user_config.id),
            idempotency_key=f"order_{order.order_number}"
        )
        
        return {
            'success': True,
            'order_id': str(order_id),
            'user_config_id': str(user_config.id)
        }
        
    except OrderUserModel.DoesNotExist:
        logger.error(f"Order {order_id} not found")
        return {
            'success': False,
            'message': 'Order not found',
            'order_id': str(order_id)
        }
    except Exception as e:
        logger.error(f"Error processing order {order_id}: {e}", exc_info=True)
        return {
            'success': False,
            'message': str(e),
            'order_id': str(order_id)
        }

