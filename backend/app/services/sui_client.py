"""
S-UI Panel Client
Handles all interactions with S-UI panel API
"""
import httpx
from typing import Optional, Dict, List, Any
from loguru import logger
from app.core.config import settings


class SUIClientError(Exception):
    """S-UI client error"""
    pass


class SUIClient:
    """
    S-UI Panel API Client
    
    Handles communication with S-UI panel including:
    - Client management (list, create, delete)
    - Usage tracking
    - Limit management
    - Server health checks
    """
    
    def __init__(
        self,
        panel_url: str,
        api_key: str,
        timeout: int = None,
        max_retries: int = None
    ):
        """
        Initialize S-UI client
        
        Args:
            panel_url: S-UI panel base URL
            api_key: S-UI API key
            timeout: Request timeout in seconds
            max_retries: Maximum number of retries
        """
        self.panel_url = panel_url.rstrip("/")
        self.api_key = api_key
        self.timeout = timeout or settings.SUI_DEFAULT_TIMEOUT
        self.max_retries = max_retries or settings.SUI_MAX_RETRIES
        self.base_url = f"{self.panel_url}/api/v1"
    
    def _get_headers(self) -> Dict[str, str]:
        """Get request headers"""
        return {
            "Content-Type": "application/json",
            "X-API-Key": self.api_key,
        }
    
    async def _request(
        self,
        method: str,
        endpoint: str,
        data: Optional[Dict] = None,
        retry_count: int = 0
    ) -> Dict[str, Any]:
        """
        Make HTTP request with retry logic
        
        Args:
            method: HTTP method
            endpoint: API endpoint
            data: Request data
            retry_count: Current retry attempt
            
        Returns:
            Response data
            
        Raises:
            SUIClientError: If request fails after retries
        """
        url = f"{self.base_url}/{endpoint.lstrip('/')}"
        
        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.request(
                    method=method,
                    url=url,
                    headers=self._get_headers(),
                    json=data if data else None
                )
                response.raise_for_status()
                return response.json()
        
        except httpx.HTTPStatusError as e:
            logger.error(f"S-UI API error: {e.response.status_code} - {e.response.text}")
            if retry_count < self.max_retries:
                logger.info(f"Retrying request (attempt {retry_count + 1}/{self.max_retries})")
                return await self._request(method, endpoint, data, retry_count + 1)
            raise SUIClientError(f"API request failed: {e.response.status_code}")
        
        except httpx.RequestError as e:
            logger.error(f"S-UI connection error: {str(e)}")
            if retry_count < self.max_retries:
                logger.info(f"Retrying request (attempt {retry_count + 1}/{self.max_retries})")
                return await self._request(method, endpoint, data, retry_count + 1)
            raise SUIClientError(f"Connection error: {str(e)}")
        
        except Exception as e:
            logger.error(f"Unexpected error in S-UI client: {str(e)}")
            raise SUIClientError(f"Unexpected error: {str(e)}")
    
    async def check_health(self) -> bool:
        """
        Check if S-UI panel is accessible
        
        Returns:
            True if panel is healthy, False otherwise
        """
        try:
            response = await self._request("GET", "/health")
            return response.get("status") == "ok"
        except Exception as e:
            logger.error(f"Health check failed: {str(e)}")
            return False
    
    async def list_clients(self) -> List[Dict[str, Any]]:
        """
        Get list of all clients
        
        Returns:
            List of client dictionaries
        """
        try:
            response = await self._request("GET", "/clients")
            return response.get("clients", [])
        except Exception as e:
            logger.error(f"Failed to list clients: {str(e)}")
            raise
    
    async def get_client(self, client_id: str) -> Optional[Dict[str, Any]]:
        """
        Get client by ID
        
        Args:
            client_id: Client ID
            
        Returns:
            Client data or None if not found
        """
        try:
            response = await self._request("GET", f"/clients/{client_id}")
            return response
        except httpx.HTTPStatusError as e:
            if e.response.status_code == 404:
                return None
            raise
    
    async def create_client(
        self,
        email: str,
        config_type: str,
        data_limit_gb: Optional[float] = None,
        expire_at: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Create a new client/config
        
        Args:
            email: Client email/identifier
            config_type: Config type (vmess, vless, trojan)
            data_limit_gb: Data limit in GB (None for unlimited)
            expire_at: Expiration date (ISO format)
            
        Returns:
            Created client data
        """
        data = {
            "email": email,
            "type": config_type,
        }
        
        if data_limit_gb is not None:
            data["limit"] = data_limit_gb * 1024 * 1024 * 1024  # Convert GB to bytes
        
        if expire_at:
            data["expire"] = expire_at
        
        try:
            response = await self._request("POST", "/clients", data=data)
            return response
        except Exception as e:
            logger.error(f"Failed to create client: {str(e)}")
            raise
    
    async def delete_client(self, client_id: str) -> bool:
        """
        Delete a client
        
        Args:
            client_id: Client ID
            
        Returns:
            True if deleted successfully
        """
        try:
            await self._request("DELETE", f"/clients/{client_id}")
            return True
        except httpx.HTTPStatusError as e:
            if e.response.status_code == 404:
                return False
            raise
    
    async def update_client_limit(
        self,
        client_id: str,
        data_limit_gb: Optional[float] = None
    ) -> Dict[str, Any]:
        """
        Update client data limit
        
        Args:
            client_id: Client ID
            data_limit_gb: New data limit in GB (None for unlimited)
            
        Returns:
            Updated client data
        """
        data = {}
        if data_limit_gb is not None:
            data["limit"] = data_limit_gb * 1024 * 1024 * 1024  # Convert GB to bytes
        else:
            data["limit"] = 0  # Unlimited
        
        try:
            response = await self._request("PUT", f"/clients/{client_id}/limit", data=data)
            return response
        except Exception as e:
            logger.error(f"Failed to update client limit: {str(e)}")
            raise
    
    async def update_client_expiry(
        self,
        client_id: str,
        expire_at: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Update client expiration date
        
        Args:
            client_id: Client ID
            expire_at: New expiration date (ISO format, None to remove expiry)
            
        Returns:
            Updated client data
        """
        data = {"expire": expire_at} if expire_at else {"expire": None}
        
        try:
            response = await self._request("PUT", f"/clients/{client_id}/expire", data=data)
            return response
        except Exception as e:
            logger.error(f"Failed to update client expiry: {str(e)}")
            raise
    
    async def get_client_usage(self, client_id: str) -> Dict[str, Any]:
        """
        Get client usage statistics
        
        Args:
            client_id: Client ID
            
        Returns:
            Usage data including used_data_gb
        """
        try:
            response = await self._request("GET", f"/clients/{client_id}/usage")
            return response
        except Exception as e:
            logger.error(f"Failed to get client usage: {str(e)}")
            raise
    
    async def get_all_usage(self) -> Dict[str, float]:
        """
        Get usage for all clients
        
        Returns:
            Dictionary mapping client_id to used_data_gb
        """
        try:
            clients = await self.list_clients()
            usage_data = {}
            
            for client in clients:
                client_id = client.get("id")
                if client_id:
                    try:
                        usage = await self.get_client_usage(client_id)
                        used_bytes = usage.get("used", 0)
                        usage_data[client_id] = used_bytes / (1024 ** 3)  # Convert to GB
                    except Exception as e:
                        logger.warning(f"Failed to get usage for client {client_id}: {str(e)}")
                        continue
            
            return usage_data
        except Exception as e:
            logger.error(f"Failed to get all usage: {str(e)}")
            raise

