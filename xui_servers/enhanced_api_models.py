"""
مدل‌های پیشرفته API برای X-UI
شامل بخش‌های تخصصی برای ایجاد Inbound و مدیریت Client
"""
import json
import uuid
from typing import Dict, List, Optional, Any, Union
from dataclasses import dataclass, asdict
from datetime import datetime, timedelta
from .api_models import XUIClient, XUIInboundSettings, XUIStreamSettings, XUISniffing, XUIAllocate, XUIInbound

@dataclass
class XUIInboundCreationRequest:
    """درخواست ایجاد Inbound جدید"""
    port: int
    protocol: str = "vless"
    remark: str = ""
    up: int = 0
    down: int = 0
    total: int = 0
    enable: bool = True
    expiry_time: int = 0
    listen: str = ""
    
    def to_payload(self) -> Dict[str, Any]:
        """تبدیل به payload برای API"""
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
            "settings": json.dumps({
                "clients": [],
                "decryption": "none",
                "fallbacks": []
            }),
            "streamSettings": json.dumps({
                "network": "tcp",
                "security": "none",
                "externalProxy": [],
                "tcpSettings": {
                    "acceptProxyProtocol": False,
                    "header": {"type": "none"}
                }
            }),
            "sniffing": json.dumps({
                "enabled": False,
                "destOverride": ["http", "tls", "quic", "fakedns"],
                "metadataOnly": False,
                "routeOnly": False
            }),
            "allocate": json.dumps({
                "strategy": "always",
                "refresh": 5,
                "concurrency": 3
            })
        }

@dataclass
class XUIClientCreationRequest:
    """درخواست ایجاد Client جدید"""
    inbound_id: int
    email: str
    total_gb: int = 0
    expiry_time: int = 0
    limit_ip: int = 0
    security: str = "auto"
    enable: bool = True
    tg_id: str = ""
    comment: str = ""
    reset: int = 0
    flow: str = ""
    
    def to_payload(self) -> Dict[str, Any]:
        """تبدیل به payload برای API"""
        client = {
            "id": str(uuid.uuid4()),
            "security": self.security,
            "email": self.email,
            "limitIp": self.limit_ip,
            "totalGB": self.total_gb,
            "expiryTime": self.expiry_time,
            "enable": self.enable,
            "tgId": self.tg_id,
            "subId": str(uuid.uuid4()).replace("-", "")[:16],
            "comment": self.comment,
            "reset": self.reset,
            "flow": self.flow
        }
        
        return {
            "id": self.inbound_id,
            "settings": json.dumps({
                "clients": [client]
            })
        }

class XUIInboundManager:
    """مدیریت Inbound ها"""
    
    def __init__(self, base_url: str, session):
        self.base_url = base_url.rstrip('/')
        self.session = session
    
    def create_inbound(self, request: XUIInboundCreationRequest) -> Optional[int]:
        """
        ایجاد Inbound جدید
        
        Args:
            request: درخواست ایجاد Inbound
            
        Returns:
            ID Inbound ایجاد شده یا None در صورت خطا
        """
        try:
            print(f"🔧 ایجاد Inbound جدید...")
            print(f"📋 جزئیات: پورت {request.port}, پروتکل {request.protocol}, نام {request.remark}")
            
            response = self.session.post(
                f"{self.base_url}/panel/inbound/add",
                data=request.to_payload(),
                headers={'Content-Type': 'application/x-www-form-urlencoded'},
                timeout=10
            )
            
            print(f"📡 وضعیت پاسخ: {response.status_code}")
            
            if response.status_code == 200:
                try:
                    result = response.json()
                    if result.get('success'):
                        inbound_id = result.get('obj', {}).get('id')
                        print(f"✅ Inbound با موفقیت ایجاد شد - ID: {inbound_id}")
                        return inbound_id
                    else:
                        print(f"❌ خطا در ایجاد Inbound: {result.get('msg', 'خطای نامشخص')}")
                except Exception as e:
                    print(f"❌ خطا در پارس پاسخ: {e}")
                    print(f"📄 محتوای پاسخ: {response.text}")
                    
                    # اگر پاسخ خالی است، احتمالاً موفق بوده
                    if not response.text.strip():
                        print(f"✅ احتمالاً Inbound با موفقیت ایجاد شد (پاسخ خالی)")
                        # تلاش برای دریافت لیست inbound ها برای یافتن inbound جدید
                        try:
                            inbounds_response = self.session.get(f"{self.base_url}/panel/api/inbounds/list", timeout=10)
                            if inbounds_response.status_code == 200:
                                inbounds_data = inbounds_response.json()
                                if inbounds_data.get('success'):
                                    inbounds = inbounds_data.get('obj', [])
                                    # یافتن inbound با پورت مورد نظر
                                    for inbound in inbounds:
                                        if inbound.get('port') == request.port and inbound.get('remark') == request.remark:
                                            inbound_id = inbound.get('id')
                                            print(f"✅ Inbound یافت شد با ID: {inbound_id}")
                                            return inbound_id
                        except Exception as e2:
                            print(f"❌ خطا در یافتن inbound جدید: {e2}")
            else:
                print(f"❌ خطای HTTP: {response.status_code}")
                print(f"📄 محتوای پاسخ: {response.text}")
            
            return None
            
        except Exception as e:
            print(f"❌ خطا در ایجاد Inbound: {e}")
            return None
    
    def get_inbound(self, inbound_id: int) -> Optional[Dict]:
        """دریافت اطلاعات Inbound"""
        try:
            response = self.session.get(
                f"{self.base_url}/panel/inbound/get/{inbound_id}",
                timeout=10
            )
            
            if response.status_code == 200:
                try:
                    result = response.json()
                    if result.get('success'):
                        return result.get('obj')
                except:
                    pass
            
            return None
            
        except Exception as e:
            print(f"خطا در دریافت Inbound: {e}")
            return None
    
    def update_inbound(self, inbound_id: int, request: XUIInboundCreationRequest) -> bool:
        """به‌روزرسانی Inbound"""
        try:
            payload = request.to_payload()
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
    
    def delete_inbound(self, inbound_id: int) -> bool:
        """حذف Inbound"""
        try:
            response = self.session.post(
                f"{self.base_url}/panel/inbound/del/{inbound_id}",
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
            print(f"خطا در حذف Inbound: {e}")
            return False

class XUIClientManager:
    """مدیریت Client ها"""
    
    def __init__(self, base_url: str, session):
        self.base_url = base_url.rstrip('/')
        self.session = session
    
    def add_client(self, request: XUIClientCreationRequest) -> bool:
        """
        اضافه کردن Client به Inbound
        
        Args:
            request: درخواست ایجاد Client
            
        Returns:
            True در صورت موفقیت، False در صورت خطا
        """
        try:
            print(f"👤 اضافه کردن Client جدید...")
            print(f"📋 جزئیات: ایمیل {request.email}, حجم {request.total_gb}GB, انقضا {request.expiry_time}")
            
            response = self.session.post(
                f"{self.base_url}/panel/inbound/addClient",
                data=request.to_payload(),
                headers={'Content-Type': 'application/x-www-form-urlencoded'},
                timeout=10
            )
            
            print(f"📡 وضعیت پاسخ: {response.status_code}")
            
            if response.status_code == 200:
                try:
                    result = response.json()
                    if result.get('success'):
                        print(f"✅ Client با موفقیت اضافه شد")
                        return True
                    else:
                        print(f"❌ خطا در اضافه کردن Client: {result.get('msg', 'خطای نامشخص')}")
                except Exception as e:
                    print(f"❌ خطا در پارس پاسخ: {e}")
                    print(f"📄 محتوای پاسخ: {response.text}")
                    
                    # اگر پاسخ خالی است، احتمالاً موفق بوده
                    if not response.text.strip():
                        print(f"✅ احتمالاً Client با موفقیت اضافه شد (پاسخ خالی)")
                        return True
            else:
                print(f"❌ خطای HTTP: {response.status_code}")
                print(f"📄 محتوای پاسخ: {response.text}")
            
            return False
            
        except Exception as e:
            print(f"❌ خطا در اضافه کردن Client: {e}")
            return False
    
    def update_client(self, inbound_id: int, client_id: str, updates: Dict[str, Any]) -> bool:
        """به‌روزرسانی Client"""
        try:
            # ابتدا اطلاعات فعلی Inbound را دریافت می‌کنیم
            inbound_response = self.session.get(
                f"{self.base_url}/panel/inbound/get/{inbound_id}",
                timeout=10
            )
            
            if inbound_response.status_code != 200:
                return False
            
            try:
                inbound_data = inbound_response.json()
                if not inbound_data.get('success'):
                    return False
                
                inbound_obj = inbound_data.get('obj', {})
                settings = json.loads(inbound_obj.get('settings', '{}'))
                clients = settings.get('clients', [])
                
                # به‌روزرسانی Client مورد نظر
                for client in clients:
                    if client.get('id') == client_id:
                        client.update(updates)
                        break
                
                # ارسال به‌روزرسانی
                payload = {
                    "id": inbound_id,
                    "settings": json.dumps(settings)
                }
                
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
                print(f"خطا در به‌روزرسانی Client: {e}")
                return False
                
        except Exception as e:
            print(f"خطا در به‌روزرسانی Client: {e}")
            return False
    
    def delete_client(self, inbound_id: int, client_id: str) -> bool:
        """حذف Client"""
        try:
            # ابتدا اطلاعات فعلی Inbound را دریافت می‌کنیم
            inbound_response = self.session.get(
                f"{self.base_url}/panel/inbound/get/{inbound_id}",
                timeout=10
            )
            
            if inbound_response.status_code != 200:
                return False
            
            try:
                inbound_data = inbound_response.json()
                if not inbound_data.get('success'):
                    return False
                
                inbound_obj = inbound_data.get('obj', {})
                settings = json.loads(inbound_obj.get('settings', '{}'))
                clients = settings.get('clients', [])
                
                # حذف Client مورد نظر
                clients = [c for c in clients if c.get('id') != client_id]
                settings['clients'] = clients
                
                # ارسال به‌روزرسانی
                payload = {
                    "id": inbound_id,
                    "settings": json.dumps(settings)
                }
                
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
                print(f"خطا در حذف Client: {e}")
                return False
                
        except Exception as e:
            print(f"خطا در حذف Client: {e}")
            return False

class XUIEnhancedService:
    """سرویس پیشرفته X-UI با مدیریت Inbound و Client"""
    
    def __init__(self, base_url: str, session):
        self.base_url = base_url.rstrip('/')
        self.session = session
        self.inbound_manager = XUIInboundManager(base_url, session)
        self.client_manager = XUIClientManager(base_url, session)
    
    def create_inbound_with_client(
        self,
        port: int,
        protocol: str = "vless",
        remark: str = "",
        client_email: str = "",
        client_total_gb: int = 0,
        client_expiry_time: int = 0
    ) -> Optional[Dict[str, Any]]:
        """
        ایجاد Inbound جدید همراه با Client
        
        Args:
            port: پورت Inbound
            protocol: پروتکل (vless, vmess, trojan)
            remark: نام Inbound
            client_email: ایمیل Client
            client_total_gb: حجم کل Client (GB)
            client_expiry_time: زمان انقضای Client
            
        Returns:
            دیکشنری شامل ID Inbound و وضعیت Client یا None
        """
        try:
            print(f"🚀 شروع ایجاد Inbound با Client...")
            
            # ایجاد Inbound
            inbound_request = XUIInboundCreationRequest(
                port=port,
                protocol=protocol,
                remark=remark
            )
            
            inbound_id = self.inbound_manager.create_inbound(inbound_request)
            
            if not inbound_id:
                print("❌ خطا در ایجاد Inbound")
                return None
            
            result = {
                "inbound_id": inbound_id,
                "client_added": False,
                "client_id": None
            }
            
            # اضافه کردن Client اگر ایمیل ارائه شده
            if client_email:
                client_request = XUIClientCreationRequest(
                    inbound_id=inbound_id,
                    email=client_email,
                    total_gb=client_total_gb,
                    expiry_time=client_expiry_time
                )
                
                if self.client_manager.add_client(client_request):
                    result["client_added"] = True
                    result["client_id"] = client_request.to_payload()["settings"]["clients"][0]["id"]
                    print(f"✅ Client با موفقیت اضافه شد")
                else:
                    print(f"⚠️ خطا در اضافه کردن Client")
            
            return result
            
        except Exception as e:
            print(f"❌ خطا در ایجاد Inbound با Client: {e}")
            return None
    
    def add_client_to_inbound(
        self,
        inbound_id: int,
        email: str,
        total_gb: int = 0,
        expiry_time: int = 0,
        limit_ip: int = 0
    ) -> bool:
        """
        اضافه کردن Client به Inbound موجود
        
        Args:
            inbound_id: ID Inbound
            email: ایمیل Client
            total_gb: حجم کل (GB)
            expiry_time: زمان انقضا
            limit_ip: محدودیت IP
            
        Returns:
            True در صورت موفقیت
        """
        try:
            client_request = XUIClientCreationRequest(
                inbound_id=inbound_id,
                email=email,
                total_gb=total_gb,
                expiry_time=expiry_time,
                limit_ip=limit_ip
            )
            
            return self.client_manager.add_client(client_request)
            
        except Exception as e:
            print(f"❌ خطا در اضافه کردن Client: {e}")
            return False
    
    def get_inbound_clients(self, inbound_id: int) -> List[Dict]:
        """دریافت لیست Client های Inbound"""
        try:
            inbound_data = self.inbound_manager.get_inbound(inbound_id)
            
            if inbound_data:
                settings = json.loads(inbound_data.get('settings', '{}'))
                return settings.get('clients', [])
            
            return []
            
        except Exception as e:
            print(f"خطا در دریافت Client ها: {e}")
            return []
    
    def update_client_traffic(
        self,
        inbound_id: int,
        client_id: str,
        total_gb: int
    ) -> bool:
        """به‌روزرسانی حجم ترافیک Client"""
        return self.client_manager.update_client(
            inbound_id, client_id, {"totalGB": total_gb}
        )
    
    def update_client_expiry(
        self,
        inbound_id: int,
        client_id: str,
        expiry_time: int
    ) -> bool:
        """به‌روزرسانی زمان انقضای Client"""
        return self.client_manager.update_client(
            inbound_id, client_id, {"expiryTime": expiry_time}
        )
    
    def delete_client_from_inbound(
        self,
        inbound_id: int,
        client_id: str
    ) -> bool:
        """حذف Client از Inbound"""
        return self.client_manager.delete_client(inbound_id, client_id) 