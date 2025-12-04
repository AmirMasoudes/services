"""
Integration tests for provisioning flow
"""
import pytest
from unittest.mock import Mock, patch, MagicMock
from django.test import TestCase
from django.utils import timezone
from datetime import timedelta

from accounts.models import UsersModel
from plan.models import ConfingPlansModel
from order.models import OrderUserModel
from xui_servers.models import XUIServer, UserConfig, XUIInbound
from xui_servers.provisioning_tasks import (
    provision_subscription,
    revoke_subscription,
    process_paid_order
)


@pytest.mark.django_db
class TestProvisioningFlow:
    """Test provisioning flow end-to-end"""
    
    @pytest.fixture
    def user(self):
        """Create test user"""
        return UsersModel.objects.create(
            telegram_id=123456789,
            id_tel='123456789',
            username_tel='testuser',
            full_name='Test User'
        )
    
    @pytest.fixture
    def plan(self):
        """Create test plan"""
        return ConfingPlansModel.objects.create(
            name='Test Plan',
            price=10000,
            traffic_mb=10240,
            duration_days=30
        )
    
    @pytest.fixture
    def server(self):
        """Create test server"""
        return XUIServer.objects.create(
            name='Test Server',
            host='test.example.com',
            port=2095,
            username='admin',
            password='password',
            server_type='sui',
            api_token='test-token'
        )
    
    @pytest.fixture
    def inbound(self, server):
        """Create test inbound"""
        return XUIInbound.objects.create(
            server=server,
            xui_inbound_id=1,
            port=443,
            protocol='vless',
            remark='Test Inbound',
            max_clients=100
        )
    
    @patch('xui_servers.provisioning_tasks.SUIProvisionService')
    def test_provision_subscription_success(self, mock_service_class, user, plan, server, inbound):
        """Test successful subscription provisioning"""
        # Setup mock
        mock_service = Mock()
        mock_service.provision_paid_config.return_value = Mock(
            id='test-config-id',
            subscription_url='https://example.com/sub/test'
        )
        mock_service_class.return_value = mock_service
        
        # Create user config
        user_config = UserConfig.objects.create(
            user=user,
            server=server,
            plan=plan,
            inbound=inbound,
            xui_inbound_id=1,
            xui_user_id='test@example.com',
            config_name='Test Config',
            status='pending',
            protocol='vless'
        )
        
        # Provision
        result = provision_subscription(str(user_config.id))
        
        # Verify
        assert result['success'] is True
        user_config.refresh_from_db()
        assert user_config.status == 'active'
        assert user_config.subscription_url is not None
    
    @patch('xui_servers.provisioning_tasks.SUIProvisionService')
    def test_provision_idempotency(self, mock_service_class, user, plan, server, inbound):
        """Test that provisioning is idempotent"""
        # Setup mock
        mock_service = Mock()
        mock_service.provision_paid_config.return_value = Mock(
            id='test-config-id',
            subscription_url='https://example.com/sub/test'
        )
        mock_service_class.return_value = mock_service
        
        # Create already-active user config
        user_config = UserConfig.objects.create(
            user=user,
            server=server,
            plan=plan,
            inbound=inbound,
            xui_inbound_id=1,
            xui_user_id='test@example.com',
            config_name='Test Config',
            status='active',
            external_id='test-key',
            subscription_url='https://example.com/sub/test',
            protocol='vless'
        )
        
        # Try to provision again
        result = provision_subscription(str(user_config.id), idempotency_key='test-key')
        
        # Should return success without re-provisioning
        assert result['success'] is True
        assert result['message'] == 'Already provisioned'
    
    @patch('xui_servers.provisioning_tasks.SUIProvisionService')
    def test_revoke_subscription(self, mock_service_class, user, plan, server, inbound):
        """Test subscription revocation"""
        # Setup mock
        mock_service = Mock()
        mock_service.deprovision_config.return_value = True
        mock_service_class.return_value = mock_service
        
        # Create active user config
        user_config = UserConfig.objects.create(
            user=user,
            server=server,
            plan=plan,
            inbound=inbound,
            xui_inbound_id=1,
            xui_user_id='test@example.com',
            config_name='Test Config',
            status='active',
            is_active=True,
            protocol='vless'
        )
        
        # Revoke
        result = revoke_subscription(str(user_config.id))
        
        # Verify
        assert result['success'] is True
        user_config.refresh_from_db()
        assert user_config.status == 'cancelled'
        assert user_config.is_active is False
    
    @patch('xui_servers.provisioning_tasks.provision_subscription')
    def test_process_paid_order(self, mock_provision, user, plan, server):
        """Test processing paid order"""
        # Create paid order
        order = OrderUserModel.objects.create(
            user=user,
            plan=plan,
            status='paid',
            total_amount=plan.price,
            paid_amount=plan.price
        )
        
        # Process order
        result = process_paid_order(str(order.id))
        
        # Verify
        assert result['success'] is True
        assert 'user_config_id' in result
        
        # Verify UserConfig created
        user_config = UserConfig.objects.get(external_id=f"order_{order.order_number}")
        assert user_config.user == user
        assert user_config.plan == plan
        
        # Verify provisioning was queued
        mock_provision.delay.assert_called_once()

