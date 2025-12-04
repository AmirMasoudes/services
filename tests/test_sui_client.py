"""
Unit tests for S-UI Client
"""
import pytest
from unittest.mock import Mock, patch, MagicMock
import requests
from xui_servers.sui_client import SUIClient, retry_with_backoff


class TestSUIClient:
    """Test suite for SUIClient"""
    
    @pytest.fixture
    def mock_response(self):
        """Create a mock response"""
        response = Mock()
        response.status_code = 200
        response.json.return_value = {'success': True, 'data': []}
        response.cookies = {}
        return response
    
    @pytest.fixture
    def sui_client(self):
        """Create a test SUIClient instance"""
        return SUIClient(
            host='test-host',
            port=2095,
            api_token='test-token',
            use_ssl=False
        )
    
    def test_init(self, sui_client):
        """Test SUIClient initialization"""
        assert sui_client.host == 'test-host'
        assert sui_client.port == 2095
        assert sui_client.api_token == 'test-token'
        assert 'Authorization' in sui_client.session.headers
    
    @patch('xui_servers.sui_client.requests.Session.request')
    def test_login_success(self, mock_request, sui_client, mock_response):
        """Test successful login"""
        mock_response.json.return_value = {'success': True, 'data': {'version': '1.0'}}
        mock_request.return_value = mock_response
        
        result = sui_client.login()
        
        assert result is True
        assert sui_client._authenticated is True
    
    @patch('xui_servers.sui_client.requests.Session.request')
    def test_login_failure(self, mock_request, sui_client):
        """Test failed login"""
        mock_response = Mock()
        mock_response.status_code = 401
        mock_request.return_value = mock_response
        
        result = sui_client.login()
        
        assert result is False
        assert sui_client._authenticated is False
    
    @patch('xui_servers.sui_client.requests.Session.request')
    def test_get_inbounds(self, mock_request, sui_client, mock_response):
        """Test getting inbounds"""
        mock_response.json.return_value = {
            'success': True,
            'data': [
                {'id': 1, 'port': 443, 'protocol': 'vless'},
                {'id': 2, 'port': 80, 'protocol': 'vmess'}
            ]
        }
        mock_request.return_value = mock_response
        sui_client._authenticated = True
        
        inbounds = sui_client.get_inbounds()
        
        assert len(inbounds) == 2
        assert inbounds[0]['id'] == 1
    
    @patch('xui_servers.sui_client.requests.Session.request')
    def test_add_client_to_inbound(self, mock_request, sui_client, mock_response):
        """Test adding client to inbound"""
        # Mock get_inbound_by_id response
        mock_response.json.return_value = {
            'success': True,
            'data': {
                'id': 1,
                'settings': '{"clients": []}'
            }
        }
        mock_request.return_value = mock_response
        sui_client._authenticated = True
        
        result = sui_client.add_client_to_inbound(
            inbound_id=1,
            email='test@example.com',
            total_gb=10,
            expiry_days=30
        )
        
        assert result is True
    
    @patch('xui_servers.sui_client.requests.Session.request')
    def test_health_check(self, mock_request, sui_client, mock_response):
        """Test health check"""
        mock_response.json.return_value = {'success': True}
        mock_request.return_value = mock_response
        
        result = sui_client.health_check()
        
        assert result is True
    
    def test_retry_decorator(self):
        """Test retry decorator"""
        call_count = 0
        
        @retry_with_backoff(max_retries=3, backoff_factor=0.1)
        def failing_function():
            nonlocal call_count
            call_count += 1
            if call_count < 3:
                raise Exception("Test error")
            return True
        
        result = failing_function()
        
        assert result is True
        assert call_count == 3


class TestIdempotency:
    """Test idempotency features"""
    
    @patch('xui_servers.sui_client.requests.Session.request')
    def test_idempotent_client_creation(self, mock_request):
        """Test that creating client twice with same key doesn't duplicate"""
        client = SUIClient(host='test', port=2095, api_token='token')
        client._authenticated = True
        
        # First call - inbound has no clients
        mock_response1 = Mock()
        mock_response1.status_code = 200
        mock_response1.json.return_value = {
            'success': True,
            'data': {'id': 1, 'settings': '{"clients": []}'}
        }
        
        # Second call - inbound already has the client
        mock_response2 = Mock()
        mock_response2.status_code = 200
        mock_response2.json.return_value = {
            'success': True,
            'data': {
                'id': 1,
                'settings': '{"clients": [{"email": "test@example.com"}]}'
            }
        }
        
        mock_request.side_effect = [mock_response1, mock_response2, mock_response2]
        
        # First creation
        result1 = client.add_client_to_inbound(
            inbound_id=1,
            email='test@example.com',
            idempotency_key='test-key'
        )
        
        # Second creation with same key (should detect existing)
        result2 = client.add_client_to_inbound(
            inbound_id=1,
            email='test@example.com',
            idempotency_key='test-key'
        )
        
        assert result1 is True
        assert result2 is True  # Should succeed due to idempotency check

