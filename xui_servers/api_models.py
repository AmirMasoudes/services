"""
مدل‌های API برای X-UI
"""
import json
import uuid
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, asdict
from datetime import datetime, timedelta

@dataclass
class XUIClient:
    """مدل کلاینت X-UI"""
    id: str
    email: str
    security: str = "auto"
    limit_ip: int = 0
    total_gb: int = 0
    expiry_time: int = 0
    enable: bool = True
    tg_id: str = ""
    sub_id: str = ""
    comment: str = ""
    reset: int = 0
    flow: str = ""
    
    def to_dict(self) -> Dict[str, Any]:
        """تبدیل به دیکشنری"""
        return {
            "id": self.id,
            "security": self.security,
            "email": self.email,
            "limitIp": self.limit_ip,
            "totalGB": self.total_gb,
            "expiryTime": self.expiry_time,
            "enable": self.enable,
            "tgId": self.tg_id,
            "subId": self.sub_id,
            "comment": self.comment,
            "reset": self.reset,
            "flow": self.flow
        }

@dataclass
class XUIInboundSettings:
    """تنظیمات Inbound"""
    clients: List[XUIClient]
    decryption: str = "none"
    fallbacks: List[Dict] = None
    
    def __post_init__(self):
        if self.fallbacks is None:
            self.fallbacks = []
    
    def to_dict(self) -> Dict[str, Any]:
        """تبدیل به دیکشنری"""
        return {
            "clients": [client.to_dict() for client in self.clients],
            "decryption": self.decryption,
            "fallbacks": self.fallbacks
        }

@dataclass
class XUIStreamSettings:
    """تنظیمات Stream"""
    network: str = "tcp"
    security: str = "none"
    external_proxy: List[Dict] = None
    tcp_settings: Dict[str, Any] = None
    
    def __post_init__(self):
        if self.external_proxy is None:
            self.external_proxy = []
        if self.tcp_settings is None:
            self.tcp_settings = {
                "acceptProxyProtocol": False,
                "header": {"type": "none"}
            }
    
    def to_dict(self) -> Dict[str, Any]:
        """تبدیل به دیکشنری"""
        return {
            "network": self.network,
            "security": self.security,
            "externalProxy": self.external_proxy,
            "tcpSettings": self.tcp_settings
        }

@dataclass
class XUISniffing:
    """تنظیمات Sniffing"""
    enabled: bool = False
    dest_override: List[str] = None
    metadata_only: bool = False
    route_only: bool = False
    
    def __post_init__(self):
        if self.dest_override is None:
            self.dest_override = ["http", "tls", "quic", "fakedns"]
    
    def to_dict(self) -> Dict[str, Any]:
        """تبدیل به دیکشنری"""
        return {
            "enabled": self.enabled,
            "destOverride": self.dest_override,
            "metadataOnly": self.metadata_only,
            "routeOnly": self.route_only
        }

@dataclass
class XUIAllocate:
    """تنظیمات Allocate"""
    strategy: str = "always"
    refresh: int = 5
    concurrency: int = 3
    
    def to_dict(self) -> Dict[str, Any]:
        """تبدیل به دیکشنری"""
        return {
            "strategy": self.strategy,
            "refresh": self.refresh,
            "concurrency": self.concurrency
        }

@dataclass
class XUIInbound:
    """مدل کامل Inbound"""
    up: int = 0
    down: int = 0
    total: int = 0
    remark: str = ""
    enable: bool = True
    expiry_time: int = 0
    listen: str = ""
    port: int = 0
    protocol: str = "vless"
    settings: XUIInboundSettings = None
    stream_settings: XUIStreamSettings = None
    sniffing: XUISniffing = None
    allocate: XUIAllocate = None
    
    def __post_init__(self):
        if self.settings is None:
            self.settings = XUIInboundSettings(clients=[])
        if self.stream_settings is None:
            self.stream_settings = XUIStreamSettings()
        if self.sniffing is None:
            self.sniffing = XUISniffing()
        if self.allocate is None:
            self.allocate = XUIAllocate()
    
    def to_dict(self) -> Dict[str, Any]:
        """تبدیل به دیکشنری برای ارسال به API"""
        return {
            "up": self.up,
            "down": self.down,
            "total": self.total,
            "remark": self.remark,
            "enable": self.enable,
            "expiryTime": self.expiry_time,
            "listen": self.listen,
            "port": self.port,
            "protocol": self.protocol,
            "settings": json.dumps(self.settings.to_dict()),
            "streamSettings": json.dumps(self.stream_settings.to_dict()),
            "sniffing": json.dumps(self.sniffing.to_dict()),
            "allocate": json.dumps(self.allocate.to_dict())
        }
    
    def add_client(self, client: XUIClient):
        """اضافه کردن کلاینت به Inbound"""
        self.settings.clients.append(client)
    
    def remove_client(self, client_id: str):
        """حذف کلاینت از Inbound"""
        self.settings.clients = [c for c in self.settings.clients if c.id != client_id]

class XUIAPIBuilder:
    """سازنده API های X-UI"""
    
    @staticmethod
    def create_inbound_payload(
        port: int,
        protocol: str = "vless",
        remark: str = "",
        client: Optional[XUIClient] = None
    ) -> XUIInbound:
        """ایجاد payload برای ایجاد Inbound"""
        inbound = XUIInbound(
            port=port,
            protocol=protocol,
            remark=remark
        )
        
        if client:
            inbound.add_client(client)
        
        return inbound
    
    @staticmethod
    def create_client_payload(
        inbound_id: int,
        client: XUIClient
    ) -> Dict[str, Any]:
        """ایجاد payload برای اضافه کردن Client"""
        return {
            "id": inbound_id,
            "settings": json.dumps({
                "clients": [client.to_dict()]
            })
        }
    
    @staticmethod
    def create_client(
        email: str,
        total_gb: int = 0,
        expiry_time: int = 0,
        limit_ip: int = 0
    ) -> XUIClient:
        """ایجاد کلاینت جدید"""
        return XUIClient(
            id=str(uuid.uuid4()),
            email=email,
            total_gb=total_gb,
            expiry_time=expiry_time,
            limit_ip=limit_ip,
            sub_id=str(uuid.uuid4()).replace("-", "")[:16]
        )

class XUIAPIClient:
    """کلاینت API برای X-UI"""
    
    def __init__(self, base_url: str, session):
        self.base_url = base_url.rstrip('/')
        self.session = session
    
    def create_inbound(self, inbound: XUIInbound) -> Optional[int]:
        """ایجاد Inbound جدید"""
        try:
            response = self.session.post(
                f"{self.base_url}/panel/inbound/add",
                data=inbound.to_dict(),
                headers={'Content-Type': 'application/x-www-form-urlencoded'},
                timeout=10
            )
            
            if response.status_code == 200:
                try:
                    result = response.json()
                    if result.get('success'):
                        return result.get('obj', {}).get('id')
                except:
                    pass
            
            return None
            
        except Exception as e:
            print(f"خطا در ایجاد Inbound: {e}")
            return None
    
    def add_client(self, inbound_id: int, client: XUIClient) -> bool:
        """اضافه کردن Client به Inbound"""
        try:
            payload = XUIAPIBuilder.create_client_payload(inbound_id, client)
            
            response = self.session.post(
                f"{self.base_url}/panel/inbound/addClient",
                data=payload,
                headers={'Content-Type': 'application/x-www-form-urlencoded'},
                timeout=10
            )
            
            if response.status_code == 200:
                try:
                    result = response.json()
                    return result.get('success', False)
                except:
                    pass
            
            return False
            
        except Exception as e:
            print(f"خطا در اضافه کردن Client: {e}")
            return False
    
    def update_inbound(self, inbound_id: int, inbound: XUIInbound) -> bool:
        """به‌روزرسانی Inbound"""
        try:
            payload = inbound.to_dict()
            payload['id'] = inbound_id
            
            response = self.session.post(
                f"{self.base_url}/panel/inbound/update/{inbound_id}",
                data=payload,
                headers={'Content-Type': 'application/x-www-form-urlencoded'},
                timeout=10
            )
            
            if response.status_code == 200:
                try:
                    result = response.json()
                    return result.get('success', False)
                except:
                    pass
            
            return False
            
        except Exception as e:
            print(f"خطا در به‌روزرسانی Inbound: {e}")
            return False 