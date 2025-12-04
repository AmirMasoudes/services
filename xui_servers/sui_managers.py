"""
S-UI Managers for Inbound and Provision Management
"""
import logging
from typing import Optional, Dict, List, Any
from django.utils import timezone
from django.db import transaction
from .sui_client import SUIClient
from .models import XUIServer, XUIInbound, XUIClient, UserConfig
from accounts.models import UsersModel
from plan.models import ConfingPlansModel

logger = logging.getLogger(__name__)


class SUIInboundManager:
    """
    Manager for S-UI inbound operations
    Handles inbound selection, creation, and management
    """
    
    def __init__(self, server: XUIServer):
        """
        Initialize S-UI inbound manager
        
        Args:
            server: XUIServer instance (can be S-UI or X-UI)
        """
        self.server = server
        self.client = SUIClient(
            host=server.host,
            port=server.port,
            use_ssl=getattr(server, 'use_ssl', False),
            base_path=getattr(server, 'web_base_path', '/app')
        )
    
    def get_available_inbounds(self, protocol: Optional[str] = None):
        """
        Get available inbounds from database
        
        Args:
            protocol: Filter by protocol (optional)
            
        Returns:
            QuerySet of available inbounds
        """
        queryset = XUIInbound.objects.filter(
            server=self.server,
            is_active=True,
            is_deleted=False
        )
        
        if protocol:
            queryset = queryset.filter(protocol=protocol)
        
        return queryset
    
    def find_best_inbound(self, protocol: str = "vless") -> Optional[XUIInbound]:
        """
        Find best available inbound for a client
        
        Args:
            protocol: Required protocol
            
        Returns:
            Best inbound or None
        """
        inbounds = self.get_available_inbounds(protocol=protocol)
        
        # Prioritize inbounds with available slots
        for inbound in inbounds:
            if inbound.can_accept_client():
                return inbound
        
        # If no inbound with slots, return first available
        return inbounds.first()
    
    def sync_inbounds(self) -> int:
        """
        Sync inbounds from S-UI to database
        
        Returns:
            Number of inbounds synced
        """
        try:
            if not self.client.login():
                logger.error(f"Failed to login to S-UI server {self.server.name}")
                return 0
            
            inbounds = self.client.get_inbounds()
            synced_count = 0
            
            for inbound_data in inbounds:
                inbound_id = inbound_data.get('id')
                if not inbound_id:
                    continue
                
                # Get or create inbound in database
                inbound, created = XUIInbound.objects.get_or_create(
                    server=self.server,
                    xui_inbound_id=inbound_id,
                    defaults={
                        'port': inbound_data.get('port', 0),
                        'protocol': inbound_data.get('protocol', 'vless'),
                        'remark': inbound_data.get('remark', f'Inbound {inbound_id}'),
                        'is_active': inbound_data.get('enable', True),
                        'max_clients': 100,  # Default
                        'current_clients': len(inbound_data.get('clientStats', []))
                    }
                )
                
                if not created:
                    # Update existing inbound
                    inbound.port = inbound_data.get('port', inbound.port)
                    inbound.protocol = inbound_data.get('protocol', inbound.protocol)
                    inbound.remark = inbound_data.get('remark', inbound.remark)
                    inbound.is_active = inbound_data.get('enable', inbound.is_active)
                    inbound.current_clients = len(inbound_data.get('clientStats', []))
                    inbound.save()
                
                synced_count += 1
            
            logger.info(f"Synced {synced_count} inbounds from S-UI server {self.server.name}")
            return synced_count
            
        except Exception as e:
            logger.error(f"Error syncing inbounds: {e}")
            return 0
    
    def create_inbound(
        self,
        protocol: str = "vless",
        port: Optional[int] = None,
        remark: str = "Auto Created"
    ) -> Optional[XUIInbound]:
        """
        Create new inbound in S-UI and database
        
        Args:
            protocol: Protocol type
            port: Port number (auto if None)
            remark: Inbound remark
            
        Returns:
            Created XUIInbound instance or None
        """
        try:
            if not self.client.login():
                return None
            
            inbound_id = self.client.create_inbound(
                protocol=protocol,
                port=port,
                remark=remark
            )
            
            if inbound_id:
                # Create database record
                inbound = XUIInbound.objects.create(
                    server=self.server,
                    xui_inbound_id=inbound_id,
                    port=port or 0,
                    protocol=protocol,
                    remark=remark,
                    is_active=True,
                    max_clients=100,
                    current_clients=0
                )
                
                logger.info(f"Created inbound {inbound_id} on S-UI server {self.server.name}")
                return inbound
            
            return None
            
        except Exception as e:
            logger.error(f"Error creating inbound: {e}")
            return None


class SUIProvisionService:
    """
    Service for provisioning clients on S-UI
    Handles trial and paid config creation
    """
    
    def __init__(self, server: XUIServer):
        """
        Initialize provision service
        
        Args:
            server: XUIServer instance
        """
        self.server = server
        self.client = SUIClient(
            host=server.host,
            port=server.port,
            use_ssl=getattr(server, 'use_ssl', False),
            base_path=getattr(server, 'web_base_path', '/app')
        )
        self.inbound_manager = SUIInboundManager(server)
    
    @transaction.atomic
    def provision_trial_config(
        self,
        user: UsersModel,
        protocol: str = "vless"
    ) -> Optional[UserConfig]:
        """
        Provision trial configuration for user
        
        Args:
            user: User instance
            protocol: Protocol type
            
        Returns:
            UserConfig instance or None
        """
        try:
            # Check if user already used trial
            if user.has_used_trial:
                logger.warning(f"User {user.telegram_id} already used trial")
                return None
            
            # Find or create inbound
            inbound = self.inbound_manager.find_best_inbound(protocol)
            if not inbound:
                # Try to sync inbounds first
                self.inbound_manager.sync_inbounds()
                inbound = self.inbound_manager.find_best_inbound(protocol)
            
            if not inbound:
                logger.error(f"No available inbound for trial config")
                return None
            
            # Generate client email
            email = f"trial_{user.username_tel}_{user.telegram_id}"
            
            # Add client to S-UI
            if not self.client.login():
                logger.error("Failed to login to S-UI")
                return None
            
            success = self.client.add_client_to_inbound(
                inbound_id=inbound.xui_inbound_id,
                email=email,
                total_gb=1,  # 1 GB for trial
                expiry_days=1,  # 1 day trial
                idempotency_key=f"trial_{user.telegram_id}"
            )
            
            if not success:
                logger.error(f"Failed to add trial client to S-UI")
                return None
            
            # Create UserConfig
            from datetime import timedelta
            user_config = UserConfig.objects.create(
                user=user,
                server=self.server,
                inbound=inbound,
                xui_inbound_id=inbound.xui_inbound_id,
                xui_user_id=email,
                config_name=f"{user.full_name} - تستی",
                config_data=self._generate_config_link(inbound, email),
                is_active=True,
                expires_at=timezone.now() + timedelta(days=1),
                protocol=protocol,
                is_trial=True
            )
            
            # Mark trial as used
            user.has_used_trial = True
            user.save()
            
            logger.info(f"Provisioned trial config for user {user.telegram_id}")
            return user_config
            
        except Exception as e:
            logger.error(f"Error provisioning trial config: {e}")
            return None
    
    @transaction.atomic
    def provision_paid_config(
        self,
        user: UsersModel,
        plan: ConfingPlansModel,
        protocol: str = "vless"
    ) -> Optional[UserConfig]:
        """
        Provision paid configuration for user
        
        Args:
            user: User instance
            plan: Plan instance
            protocol: Protocol type
            
        Returns:
            UserConfig instance or None
        """
        try:
            # Find or create inbound
            inbound = self.inbound_manager.find_best_inbound(protocol)
            if not inbound:
                self.inbound_manager.sync_inbounds()
                inbound = self.inbound_manager.find_best_inbound(protocol)
            
            if not inbound:
                logger.error(f"No available inbound for paid config")
                return None
            
            # Generate client email
            email = f"{user.username_tel}_{user.telegram_id}"
            
            # Add client to S-UI
            if not self.client.login():
                logger.error("Failed to login to S-UI")
                return None
            
            success = self.client.add_client_to_inbound(
                inbound_id=inbound.xui_inbound_id,
                email=email,
                total_gb=plan.get_traffic_gb(),
                expiry_days=getattr(plan, 'duration_days', 30),
                idempotency_key=f"paid_{user.telegram_id}_{plan.id}"
            )
            
            if not success:
                logger.error(f"Failed to add paid client to S-UI")
                return None
            
            # Create UserConfig
            from datetime import timedelta
            user_config = UserConfig.objects.create(
                user=user,
                server=self.server,
                inbound=inbound,
                xui_inbound_id=inbound.xui_inbound_id,
                xui_user_id=email,
                config_name=f"{user.full_name} - {plan.name}",
                config_data=self._generate_config_link(inbound, email),
                is_active=True,
                expires_at=timezone.now() + timedelta(days=getattr(plan, 'duration_days', 30)),
                protocol=protocol,
                plan=plan,
                is_trial=False
            )
            
            logger.info(f"Provisioned paid config for user {user.telegram_id}, plan {plan.id}")
            return user_config
            
        except Exception as e:
            logger.error(f"Error provisioning paid config: {e}")
            return None
    
    def _generate_config_link(self, inbound: XUIInbound, email: str) -> str:
        """
        Generate subscription/config link for user
        
        Args:
            inbound: Inbound instance
            email: Client email
            
        Returns:
            Config link string
        """
        # This should generate proper subscription link
        # For now, return a placeholder
        from django.conf import settings
        base_url = getattr(settings, 'SERVER_DOMAIN', 'localhost')
        return f"https://{base_url}/api/subscription/{email}"
    
    def sync_client_usage(self, user_config: UserConfig) -> bool:
        """
        Sync client usage from S-UI to database
        
        Args:
            user_config: UserConfig instance
            
        Returns:
            True if sync successful
        """
        try:
            if not self.client.login():
                return False
            
            stats = self.client.get_client_stats(
                inbound_id=user_config.xui_inbound_id,
                email=user_config.xui_user_id
            )
            
            if stats:
                # Update usage in database
                # This would update XUIClient if it exists
                # For now, just log
                logger.info(f"Synced usage for {user_config.xui_user_id}: {stats}")
                return True
            
            return False
            
        except Exception as e:
            logger.error(f"Error syncing client usage: {e}")
            return False
    
    def deprovision_config(self, user_config: UserConfig) -> bool:
        """
        Deprovision (remove) user configuration
        
        Args:
            user_config: UserConfig instance
            
        Returns:
            True if successful
        """
        try:
            if not self.client.login():
                return False
            
            success = self.client.remove_client_from_inbound(
                inbound_id=user_config.xui_inbound_id,
                email=user_config.xui_user_id
            )
            
            if success:
                user_config.is_active = False
                user_config.save()
                logger.info(f"Deprovisioned config for {user_config.xui_user_id}")
            
            return success
            
        except Exception as e:
            logger.error(f"Error deprovisioning config: {e}")
            return False

