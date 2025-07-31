import requests
import json
import base64
from datetime import datetime, timedelta
from django.utils import timezone
from .models import XUIServer, UserConfig

class XUIService:
    """سرویس برای اتصال به X-UI"""
    
    def __init__(self, server: XUIServer):
        self.server = server
        self.base_url = f"http://{server.host}:{server.port}"
        self.session = requests.Session()
        self.session.headers.update({
            'Content-Type': 'application/json',
            'User-Agent': 'Django-XUI-Bot/1.0'
        })
    
    def login(self):
        """ورود به X-UI"""
        try:
            login_data = {
                "username": self.server.username,
                "password": self.server.password
            }
            
            response = self.session.post(
                f"{self.base_url}/login",
                json=login_data,
                timeout=10
            )
            
            if response.status_code == 200:
                data = response.json()
                if data.get('success'):
                    return True
            return False
            
        except Exception as e:
            print(f"خطا در ورود به X-UI: {e}")
            return False
    
    def get_inbounds(self):
        """دریافت لیست inbound ها"""
        try:
            response = self.session.get(f"{self.base_url}/panel/api/inbounds/list")
            if response.status_code == 200:
                data = response.json()
                return data.get('obj', [])
            return []
            
        except Exception as e:
            print(f"خطا در دریافت inbound ها: {e}")
            return []
    
    def create_user(self, inbound_id: int, user_data: dict):
        """ایجاد کاربر در X-UI"""
        try:
            payload = {
                "id": inbound_id,
                "settings": {
                    "clients": [user_data]
                }
            }
            
            response = self.session.post(
                f"{self.base_url}/panel/api/inbounds/updateClient/{inbound_id}",
                json=payload,
                timeout=10
            )
            
            if response.status_code == 200:
                data = response.json()
                return data.get('success', False)
            return False
            
        except Exception as e:
            print(f"خطا در ایجاد کاربر: {e}")
            return False
    
    def delete_user(self, inbound_id: int, email: str):
        """حذف کاربر از X-UI"""
        try:
            payload = {
                "id": inbound_id,
                "email": email
            }
            
            response = self.session.post(
                f"{self.base_url}/panel/api/inbounds/delClient",
                json=payload,
                timeout=10
            )
            
            if response.status_code == 200:
                data = response.json()
                return data.get('success', False)
            return False
            
        except Exception as e:
            print(f"خطا در حذف کاربر: {e}")
            return False
    
    def update_user_traffic(self, inbound_id: int, email: str, traffic_limit: int):
        """به‌روزرسانی محدودیت ترافیک کاربر"""
        try:
            payload = {
                "id": inbound_id,
                "email": email,
                "limit": traffic_limit
            }
            
            response = self.session.post(
                f"{self.base_url}/panel/api/inbounds/updateClient",
                json=payload,
                timeout=10
            )
            
            if response.status_code == 200:
                data = response.json()
                return data.get('success', False)
            return False
            
        except Exception as e:
            print(f"خطا در به‌روزرسانی ترافیک: {e}")
            return False

class ConfigGenerator:
    """تولیدکننده کانفیگ"""
    
    @staticmethod
    def generate_vmess_config(server_host: str, port: int, uuid: str, path: str = "/"):
        """تولید کانفیگ VMess"""
        config = {
            "v": "2",
            "ps": "VPN Config",
            "add": server_host,
            "port": port,
            "id": uuid,
            "aid": "0",
            "net": "ws",
            "type": "none",
            "host": "",
            "path": path,
            "tls": "tls"
        }
        
        config_str = json.dumps(config)
        encoded = base64.b64encode(config_str.encode()).decode()
        return f"vmess://{encoded}"
    
    @staticmethod
    def generate_vless_config(server_host: str, port: int, uuid: str, path: str = "/"):
        """تولید کانفیگ VLess"""
        return f"vless://{uuid}@{server_host}:{port}?type=ws&security=tls&path={path}#VPN Config"
    
    @staticmethod
    def generate_trojan_config(server_host: str, port: int, password: str):
        """تولید کانفیگ Trojan"""
        return f"trojan://{password}@{server_host}:{port}?security=tls#VPN Config"

class UserConfigService:
    """سرویس مدیریت کانفیگ کاربران"""
    
    @staticmethod
    def create_trial_config(user: 'UsersModel', server: XUIServer):
        """ایجاد کانفیگ تستی برای کاربر"""
        try:
            # ورود به X-UI
            xui_service = XUIService(server)
            if not xui_service.login():
                return None, "خطا در ورود به X-UI"
            
            # دریافت inbound ها
            inbounds = xui_service.get_inbounds()
            if not inbounds:
                return None, "هیچ inbound یافت نشد"
            
            # انتخاب اولین inbound
            inbound = inbounds[0]
            inbound_id = inbound.get('id')
            
            # تولید اطلاعات کاربر
            import uuid
            user_uuid = str(uuid.uuid4())
            user_email = f"trial_{user.telegram_id}@vpn.com"
            
            # ایجاد کاربر در X-UI
            user_data = {
                "id": user_uuid,
                "email": user_email,
                "limitIp": 1,
                "totalGB": 0,  # نامحدود برای تست
                "expiryTime": int((timezone.now() + timedelta(hours=24)).timestamp() * 1000)
            }
            
            if not xui_service.create_user(inbound_id, user_data):
                return None, "خطا در ایجاد کاربر در X-UI"
            
            # تولید کانفیگ
            config_data = ConfigGenerator.generate_vmess_config(
                server.host,
                inbound.get('port', 443),
                user_uuid
            )
            
            # ذخیره در دیتابیس
            user_config = UserConfig.objects.create(
                user=user,
                server=server,
                xui_inbound_id=inbound_id,
                xui_user_id=user.id,
                config_name="پلن تستی",
                config_data=config_data,
                expires_at=timezone.now() + timedelta(hours=24)
            )
            
            return user_config, "کانفیگ تستی با موفقیت ایجاد شد"
            
        except Exception as e:
            return None, f"خطا در ایجاد کانفیگ: {str(e)}"
    
    @staticmethod
    def create_paid_config(user: 'UsersModel', server: XUIServer, plan: 'ConfingPlansModel'):
        """ایجاد کانفیگ پولی برای کاربر"""
        try:
            # ورود به X-UI
            xui_service = XUIService(server)
            if not xui_service.login():
                return None, "خطا در ورود به X-UI"
            
            # دریافت inbound ها
            inbounds = xui_service.get_inbounds()
            if not inbounds:
                return None, "هیچ inbound یافت نشد"
            
            # انتخاب اولین inbound
            inbound = inbounds[0]
            inbound_id = inbound.get('id')
            
            # تولید اطلاعات کاربر
            import uuid
            user_uuid = str(uuid.uuid4())
            user_email = f"paid_{user.telegram_id}_{plan.id}@vpn.com"
            
            # محاسبه حجم (تبدیل MB به GB)
            total_gb = plan.in_volume / 1024
            
            # ایجاد کاربر در X-UI
            user_data = {
                "id": user_uuid,
                "email": user_email,
                "limitIp": 1,
                "totalGB": total_gb,
                "expiryTime": int((timezone.now() + timedelta(days=30)).timestamp() * 1000)
            }
            
            if not xui_service.create_user(inbound_id, user_data):
                return None, "خطا در ایجاد کاربر در X-UI"
            
            # تولید کانفیگ
            config_data = ConfigGenerator.generate_vmess_config(
                server.host,
                inbound.get('port', 443),
                user_uuid
            )
            
            # ذخیره در دیتابیس
            user_config = UserConfig.objects.create(
                user=user,
                server=server,
                xui_inbound_id=inbound_id,
                xui_user_id=user.id,
                config_name=plan.name,
                config_data=config_data,
                expires_at=timezone.now() + timedelta(days=30)
            )
            
            return user_config, "کانفیگ پولی با موفقیت ایجاد شد"
            
        except Exception as e:
            return None, f"خطا در ایجاد کانفیگ: {str(e)}"
    
    @staticmethod
    def delete_user_config(user_config: UserConfig):
        """حذف کانفیگ کاربر"""
        try:
            xui_service = XUIService(user_config.server)
            if not xui_service.login():
                return False, "خطا در ورود به X-UI"
            
            # حذف از X-UI
            email = f"trial_{user_config.user.telegram_id}@vpn.com"
            if "paid_" in user_config.config_name:
                email = f"paid_{user_config.user.telegram_id}_{user_config.xui_user_id}@vpn.com"
            
            if xui_service.delete_user(user_config.xui_inbound_id, email):
                user_config.delete()
                return True, "کانفیگ با موفقیت حذف شد"
            else:
                return False, "خطا در حذف از X-UI"
                
        except Exception as e:
            return False, f"خطا در حذف کانفیگ: {str(e)}" 