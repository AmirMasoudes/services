"""
S-UI API Client Implementation
Proper integration for S-UI panel (API v2)
"""
import requests
import json
import time
import logging
from typing import Optional, Dict, List, Any
from datetime import datetime, timedelta
from django.utils import timezone
from django.conf import settings
from functools import wraps
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

logger = logging.getLogger(__name__)


def retry_with_backoff(max_retries: int = 3, backoff_factor: float = 1.0):
    """Decorator for retry logic with exponential backoff"""
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            last_exception = None
            for attempt in range(max_retries):
                try:
                    return func(*args, **kwargs)
                except Exception as e:
                    last_exception = e
                    if attempt < max_retries - 1:
                        wait_time = backoff_factor * (2 ** attempt)
                        logger.warning(
                            f"Attempt {attempt + 1}/{max_retries} failed for {func.__name__}: {e}. "
                            f"Retrying in {wait_time}s..."
                        )
                        time.sleep(wait_time)
                    else:
                        logger.error(f"All {max_retries} attempts failed for {func.__name__}")
            raise last_exception
        return wrapper
    return decorator


class SUIClient:
    """
    S-UI API Client for managing S-UI panel operations
    
    Supports:
    - Authentication with API token
    - Inbound management
    - Client management
    - Usage tracking
    - Health checks
    """
    
    def __init__(
        self,
        host: str,
        port: int = 2095,
        api_token: Optional[str] = None,
        use_ssl: bool = False,
        base_path: str = "/app",
        timeout: int = 30
    ):
        """
        Initialize S-UI client
        
        Args:
            host: S-UI server host
            port: S-UI server port (default: 2095)
            api_token: API token for authentication
            use_ssl: Use HTTPS (default: False)
            base_path: Base path for API (default: /app)
            timeout: Request timeout in seconds
        """
        self.host = host
        self.port = port
        self.api_token = api_token or getattr(settings, 'SUI_API_TOKEN', '')
        self.use_ssl = use_ssl
        self.base_path = base_path.rstrip('/')
        self.timeout = timeout
        
        # Build base URL
        protocol = "https" if use_ssl else "http"
        self.base_url = f"{protocol}://{host}:{port}{base_path}"
        
        # Create session with retry strategy
        self.session = requests.Session()
        retry_strategy = Retry(
            total=3,
            backoff_factor=1,
            status_forcelist=[429, 500, 502, 503, 504],
            allowed_methods=["GET", "POST", "PUT", "DELETE"]
        )
        adapter = HTTPAdapter(max_retries=retry_strategy)
        self.session.mount("http://", adapter)
        self.session.mount("https://", adapter)
        
        # Set default headers
        self.session.headers.update({
            'Content-Type': 'application/json',
            'Accept': 'application/json',
            'User-Agent': 'Django-SUI-Bot/1.0'
        })
        
        # Add API token if available
        if self.api_token:
            self.session.headers.update({
                'Authorization': f'Bearer {self.api_token}'
            })
        
        # SSL verification
        self.session.verify = getattr(settings, 'SUI_VERIFY_SSL', False)
        
        self._authenticated = False
    
    def _make_request(
        self,
        method: str,
        endpoint: str,
        data: Optional[Dict] = None,
        params: Optional[Dict] = None
    ) -> Optional[Dict[str, Any]]:
        """
        Make HTTP request to S-UI API
        
        Args:
            method: HTTP method (GET, POST, PUT, DELETE)
            endpoint: API endpoint
            data: Request body data
            params: Query parameters
            
        Returns:
            Response JSON data or None on error
        """
        url = f"{self.base_url}{endpoint}"
        
        try:
            response = self.session.request(
                method=method,
                url=url,
                json=data,
                params=params,
                timeout=self.timeout
            )
            
            # Check status code
            if response.status_code == 401:
                logger.error("Authentication failed - invalid API token")
                self._authenticated = False
                return None
            
            if response.status_code == 404:
                logger.warning(f"Endpoint not found: {endpoint}")
                return None
            
            if response.status_code >= 500:
                logger.error(f"Server error {response.status_code}: {response.text}")
                return None
            
            # Parse JSON response
            try:
                result = response.json()
                if response.status_code in [200, 201]:
                    self._authenticated = True
                    return result
                else:
                    logger.warning(f"API returned {response.status_code}: {result}")
                    return None
            except json.JSONDecodeError:
                logger.error(f"Invalid JSON response: {response.text[:200]}")
                return None
                
        except requests.exceptions.Timeout:
            logger.error(f"Request timeout for {endpoint}")
            return None
        except requests.exceptions.ConnectionError as e:
            logger.error(f"Connection error for {endpoint}: {e}")
            return None
        except Exception as e:
            logger.error(f"Unexpected error in {endpoint}: {e}")
            return None
    
    @retry_with_backoff(max_retries=3, backoff_factor=1.0)
    def login(self) -> bool:
        """
        Authenticate with S-UI panel
        
        Returns:
            True if authentication successful
        """
        if not self.api_token:
            logger.error("No API token provided for S-UI authentication")
            return False
        
        # S-UI API v2 uses token-based auth, so we just verify the token works
        result = self._make_request('GET', '/api/v2/system/info')
        
        if result:
            self._authenticated = True
            logger.info(f"Successfully authenticated with S-UI at {self.host}:{self.port}")
            return True
        
        return False
    
    def ensure_authenticated(self) -> bool:
        """Ensure client is authenticated"""
        if not self._authenticated:
            return self.login()
        return True
    
    @retry_with_backoff(max_retries=3, backoff_factor=1.0)
    def get_inbounds(self) -> List[Dict[str, Any]]:
        """
        Get list of all inbounds
        
        Returns:
            List of inbound dictionaries
        """
        if not self.ensure_authenticated():
            return []
        
        result = self._make_request('GET', '/api/v2/inbounds')
        
        if result and result.get('success'):
            return result.get('data', [])
        
        return []
    
    @retry_with_backoff(max_retries=3, backoff_factor=1.0)
    def get_inbound_by_id(self, inbound_id: int) -> Optional[Dict[str, Any]]:
        """
        Get inbound by ID
        
        Args:
            inbound_id: Inbound ID
            
        Returns:
            Inbound dictionary or None
        """
        if not self.ensure_authenticated():
            return None
        
        result = self._make_request('GET', f'/api/v2/inbounds/{inbound_id}')
        
        if result and result.get('success'):
            return result.get('data')
        
        return None
    
    @retry_with_backoff(max_retries=3, backoff_factor=1.0)
    def create_inbound(
        self,
        protocol: str = "vless",
        port: Optional[int] = None,
        remark: str = "Auto Created",
        settings: Optional[Dict] = None
    ) -> Optional[int]:
        """
        Create new inbound
        
        Args:
            protocol: Protocol (vless, vmess, trojan)
            port: Port number (auto-assigned if None)
            remark: Inbound remark/name
            settings: Additional settings
            
        Returns:
            Created inbound ID or None
        """
        if not self.ensure_authenticated():
            return None
        
        # Default settings
        if settings is None:
            settings = {
                "clients": [],
                "decryption": "none",
                "fallbacks": []
            }
        
        payload = {
            "protocol": protocol,
            "port": port or 0,  # 0 = auto-assign
            "remark": remark,
            "settings": json.dumps(settings),
            "streamSettings": json.dumps({
                "network": "tcp",
                "security": "none",
                "tcpSettings": {
                    "header": {"type": "none"}
                }
            }),
            "sniffing": json.dumps({
                "enabled": True,
                "destOverride": ["http", "tls"]
            })
        }
        
        result = self._make_request('POST', '/api/v2/inbounds', data=payload)
        
        if result and result.get('success'):
            inbound_id = result.get('data', {}).get('id')
            logger.info(f"Created inbound {inbound_id} with protocol {protocol}")
            return inbound_id
        
        return None
    
    @retry_with_backoff(max_retries=3, backoff_factor=1.0)
    def add_client_to_inbound(
        self,
        inbound_id: int,
        email: str,
        uuid: Optional[str] = None,
        total_gb: int = 0,
        expiry_days: int = 0,
        limit_ip: int = 0,
        idempotency_key: Optional[str] = None
    ) -> bool:
        """
        Add client to inbound with idempotency support
        
        Args:
            inbound_id: Inbound ID
            email: Client email/identifier
            uuid: Client UUID (auto-generated if None)
            total_gb: Traffic limit in GB (0 = unlimited)
            expiry_days: Expiry in days (0 = no expiry)
            limit_ip: IP limit (0 = unlimited)
            idempotency_key: Idempotency key to prevent duplicates
            
        Returns:
            True if successful
        """
        if not self.ensure_authenticated():
            return False
        
        # Check if client already exists (idempotency)
        inbound = self.get_inbound_by_id(inbound_id)
        if inbound:
            settings = json.loads(inbound.get('settings', '{}'))
            clients = settings.get('clients', [])
            if any(c.get('email') == email for c in clients):
                logger.info(f"Client {email} already exists in inbound {inbound_id} (idempotency)")
                return True
        
        # Generate UUID if not provided
        if not uuid:
            import uuid as uuid_module
            uuid = str(uuid_module.uuid4())
        
        # Calculate expiry timestamp
        expiry_time = 0
        if expiry_days > 0:
            expiry_time = int((timezone.now() + timedelta(days=expiry_days)).timestamp() * 1000)
        
        # Create client data
        client_data = {
            "id": uuid,
            "email": email,
            "limitIp": limit_ip,
            "totalGB": total_gb * 1024 * 1024 * 1024,  # Convert GB to bytes
            "expiryTime": expiry_time,
            "enable": True,
            "subId": idempotency_key or f"{email}_{int(time.time())}"
        }
        
        # Get current inbound settings
        inbound = self.get_inbound_by_id(inbound_id)
        if not inbound:
            logger.error(f"Inbound {inbound_id} not found")
            return False
        
        settings = json.loads(inbound.get('settings', '{}'))
        clients = settings.get('clients', [])
        clients.append(client_data)
        settings['clients'] = clients
        
        # Update inbound
        payload = {
            "id": inbound_id,
            "settings": json.dumps(settings)
        }
        
        result = self._make_request('PUT', f'/api/v2/inbounds/{inbound_id}', data=payload)
        
        if result and result.get('success'):
            logger.info(f"Added client {email} to inbound {inbound_id}")
            return True
        
        return False
    
    @retry_with_backoff(max_retries=3, backoff_factor=1.0)
    def remove_client_from_inbound(self, inbound_id: int, email: str) -> bool:
        """
        Remove client from inbound
        
        Args:
            inbound_id: Inbound ID
            email: Client email
            
        Returns:
            True if successful
        """
        if not self.ensure_authenticated():
            return False
        
        inbound = self.get_inbound_by_id(inbound_id)
        if not inbound:
            return False
        
        settings = json.loads(inbound.get('settings', '{}'))
        clients = settings.get('clients', [])
        
        # Filter out the client
        original_count = len(clients)
        clients = [c for c in clients if c.get('email') != email]
        
        if len(clients) == original_count:
            logger.warning(f"Client {email} not found in inbound {inbound_id}")
            return False
        
        settings['clients'] = clients
        
        payload = {
            "id": inbound_id,
            "settings": json.dumps(settings)
        }
        
        result = self._make_request('PUT', f'/api/v2/inbounds/{inbound_id}', data=payload)
        
        if result and result.get('success'):
            logger.info(f"Removed client {email} from inbound {inbound_id}")
            return True
        
        return False
    
    @retry_with_backoff(max_retries=3, backoff_factor=1.0)
    def get_client_traffic(self, email: str) -> Optional[Dict[str, Any]]:
        """
        Get client traffic statistics
        
        Args:
            email: Client email
            
        Returns:
            Traffic statistics dictionary
        """
        if not self.ensure_authenticated():
            return None
        
        result = self._make_request('GET', f'/api/v2/clients/{email}/traffic')
        
        if result and result.get('success'):
            return result.get('data')
        
        return None
    
    @retry_with_backoff(max_retries=3, backoff_factor=1.0)
    def get_client_stats(self, inbound_id: int, email: str) -> Optional[Dict[str, Any]]:
        """
        Get detailed client statistics
        
        Args:
            inbound_id: Inbound ID
            email: Client email
            
        Returns:
            Client statistics dictionary
        """
        if not self.ensure_authenticated():
            return None
        
        result = self._make_request(
            'GET',
            f'/api/v2/inbounds/{inbound_id}/clients/{email}/stats'
        )
        
        if result and result.get('success'):
            return result.get('data')
        
        return None
    
    @retry_with_backoff(max_retries=3, backoff_factor=1.0)
    def update_client_limits(
        self,
        inbound_id: int,
        email: str,
        total_gb: Optional[int] = None,
        expiry_days: Optional[int] = None,
        limit_ip: Optional[int] = None
    ) -> bool:
        """
        Update client limits
        
        Args:
            inbound_id: Inbound ID
            email: Client email
            total_gb: New traffic limit in GB
            expiry_days: New expiry in days
            limit_ip: New IP limit
            
        Returns:
            True if successful
        """
        if not self.ensure_authenticated():
            return False
        
        inbound = self.get_inbound_by_id(inbound_id)
        if not inbound:
            return False
        
        settings = json.loads(inbound.get('settings', '{}'))
        clients = settings.get('clients', [])
        
        # Find and update client
        updated = False
        for client in clients:
            if client.get('email') == email:
                if total_gb is not None:
                    client['totalGB'] = total_gb * 1024 * 1024 * 1024
                if expiry_days is not None:
                    if expiry_days > 0:
                        client['expiryTime'] = int(
                            (timezone.now() + timedelta(days=expiry_days)).timestamp() * 1000
                        )
                    else:
                        client['expiryTime'] = 0
                if limit_ip is not None:
                    client['limitIp'] = limit_ip
                updated = True
                break
        
        if not updated:
            logger.warning(f"Client {email} not found in inbound {inbound_id}")
            return False
        
        settings['clients'] = clients
        
        payload = {
            "id": inbound_id,
            "settings": json.dumps(settings)
        }
        
        result = self._make_request('PUT', f'/api/v2/inbounds/{inbound_id}', data=payload)
        
        if result and result.get('success'):
            logger.info(f"Updated limits for client {email} in inbound {inbound_id}")
            return True
        
        return False
    
    def health_check(self) -> bool:
        """
        Check S-UI server health
        
        Returns:
            True if server is healthy
        """
        try:
            result = self._make_request('GET', '/api/v2/system/info')
            return result is not None and result.get('success', False)
        except Exception as e:
            logger.error(f"Health check failed: {e}")
            return False

