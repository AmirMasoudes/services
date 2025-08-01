import requests
import json
import base64
import uuid
import random
import string
from datetime import datetime, timedelta
from django.utils import timezone
from .models import XUIServer, UserConfig
from . import settings as xui_settings
from accounts.models import UsersModel
from plan.models import ConfingPlansModel

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
    
    def create_auto_inbound(self, protocol: str = "vless", port: int | None = None) -> int | None:
        """ایجاد خودکار inbound با تنظیمات پیش‌فرض"""
        try:
            if not self.login():
                return None
            
            # اگر پورت مشخص نشده، پورت تصادفی انتخاب کن
            if port is None:
                port = random.randint(
                    int(xui_settings.PORT_SETTINGS["min_port"]),
                    int(xui_settings.PORT_SETTINGS["max_port"])
                )
            
            # دریافت تنظیمات پروتکل
            protocol_config = xui_settings.PROTOCOL_SETTINGS.get(protocol.lower())
            if not protocol_config:
                return None
            
            # تنظیمات stream و settings از فایل تنظیمات
            settings = dict(protocol_config.get("settings", {}))
            stream_settings = dict(protocol_config.get("stream_settings", {}))
            
            # برای VLess Reality، تنظیمات تصادفی اضافه کن
            if protocol.lower() == "vless":
                # انتخاب دامنه فیک تصادفی
                fake_domain = random.choice(xui_settings.FAKE_DOMAINS)
                stream_settings["realitySettings"]["serverName"] = fake_domain
                
                # انتخاب کلید عمومی تصادفی
                public_key = random.choice(xui_settings.REALITY_PUBLIC_KEYS)
                stream_settings["realitySettings"]["publicKey"] = public_key
                
                # تولید shortId تصادفی
                short_id = ''.join(random.choices(string.hexdigits.lower(), k=8))
                stream_settings["realitySettings"]["shortId"] = short_id
                
                # تنظیم آدرس سرور
                settings["vnext"][0]["address"] = self.server.host
                settings["vnext"][0]["port"] = port
            
            # نام inbound از تنظیمات
            inbound_name = xui_settings.INBOUND_NAMING["format"].format(
                prefix=xui_settings.INBOUND_NAMING["prefix"],
                separator=xui_settings.INBOUND_NAMING["separator"],
                protocol=protocol.upper(),
                port=port
            )
            
            inbound_data = {
                **xui_settings.INBOUND_SETTINGS,
                "remark": inbound_name,
                "port": port,
                "protocol": protocol,
                "settings": settings,
                "streamSettings": stream_settings
            }
            
            response = self.session.post(
                f"{self.base_url}/panel/api/inbounds/add",
                json=inbound_data,
                timeout=10
            )
            
            if response.status_code == 200:
                data = response.json()
                if data.get('success'):
                    return data.get('obj', {}).get('id')
            return None
            
        except Exception as e:
            print(f"خطا در ایجاد inbound: {e}")
            return None
    
    def get_or_create_inbound(self, protocol: str = "vless"):
        """دریافت یا ایجاد inbound خودکار"""
        try:
            # ابتدا inbound های موجود را بررسی کن
            inbounds = self.get_inbounds()
            
            # inbound های خودکار را پیدا کن
            auto_inbounds = [
                i for i in inbounds 
                if i.get('remark', '').startswith(xui_settings.INBOUND_NAMING["prefix"]) 
                and i.get('protocol') == protocol
            ]
            
            if auto_inbounds:
                # از اولین inbound موجود استفاده کن
                return auto_inbounds[0].get('id')
            else:
                # inbound جدید ایجاد کن
                return self.create_auto_inbound(protocol)
                
        except Exception as e:
            print(f"خطا در دریافت/ایجاد inbound: {e}")
            return None
    
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
                f"{self.base_url}/panel/api/inbounds/updateClient",
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
                "settings": {
                    "clients": []
                }
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
            print(f"خطا در حذف کاربر: {e}")
            return False
    
    def update_user_traffic(self, inbound_id: int, email: str, traffic_limit: int):
        """به‌روزرسانی حجم داده کاربر"""
        try:
            payload = {
                "id": inbound_id,
                "settings": {
                    "clients": [{
                        "email": email,
                        "totalGB": traffic_limit
                    }]
                }
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
            print(f"خطا در به‌روزرسانی حجم داده: {e}")
            return False

class ConfigGenerator:
    """تولیدکننده کانفیگ‌های مختلف"""
    
    @staticmethod
    def generate_vmess_config(server_host: str, port: int, uuid: str, path: str = "/"):
        """تولید کانفیگ VMess"""
        config = {
            **xui_settings.CONFIG_SETTINGS["vmess"],
            "ps": "VPN Config",
            "add": server_host,
            "port": port,
            "id": uuid,
            "host": "",
            "path": path
        }
        
        config_str = json.dumps(config)
        encoded = base64.b64encode(config_str.encode()).decode()
        return f"vmess://{encoded}"
    
    @staticmethod
    def generate_vless_reality_config(server_host: str, port: int, uuid: str, user_name: str = "User"):
        """تولید کانفیگ VLess Reality"""
        # انتخاب دامنه فیک تصادفی
        fake_domain = random.choice(xui_settings.FAKE_DOMAINS)
        
        # انتخاب کلید عمومی تصادفی
        public_key = random.choice(xui_settings.REALITY_PUBLIC_KEYS)
        
        # تولید shortId تصادفی
        short_id = ''.join(random.choices(string.hexdigits.lower(), k=8))
        
        # تولید کانفیگ VLess Reality
        config = f"vless://{uuid}@{server_host}:{port}?type=tcp&security=reality&sni={fake_domain}&fp=chrome&pbk={public_key}&sid={short_id}&spx=%2F#{user_name}"
        
        return config
    
    @staticmethod
    def generate_vless_config(server_host: str, port: int, uuid: str, path: str = "/"):
        """تولید کانفیگ VLess (قدیمی)"""
        return f"vless://{uuid}@{server_host}:{port}?type=ws&security=tls&path={path}#VPN Config"
    
    @staticmethod
    def generate_trojan_config(server_host: str, port: int, password: str):
        """تولید کانفیگ Trojan"""
        return f"trojan://{password}@{server_host}:{port}?security=tls#VPN Config"

class UserConfigService:
    """سرویس مدیریت کانفیگ کاربران"""
    
    @staticmethod
    def create_trial_config(user: UsersModel, server: XUIServer, protocol: str = "vless"):
        """ایجاد کانفیگ تستی برای کاربر"""
        try:
            # ورود به X-UI
            xui_service = XUIService(server)
            if not xui_service.login():
                return None, xui_settings.ERROR_MESSAGES["xui_login_failed"]
            
            # دریافت یا ایجاد inbound خودکار
            inbound_id = xui_service.get_or_create_inbound(protocol)
            if not inbound_id:
                return None, xui_settings.ERROR_MESSAGES["inbound_creation_failed"]
            
            # دریافت اطلاعات inbound
            inbounds = xui_service.get_inbounds()
            inbound = next((i for i in inbounds if i.get('id') == inbound_id), None)
            if not inbound:
                return None, "خطا در دریافت اطلاعات inbound"
            
            # تولید اطلاعات کاربر
            user_uuid = str(uuid.uuid4())
            user_email = xui_settings.EMAIL_SETTINGS["trial_format"].format(
                telegram_id=user.telegram_id
            )
            
            # ایجاد کاربر در X-UI
            user_data = {
                **xui_settings.USER_DEFAULT_SETTINGS,
                "id": user_uuid,
                "email": user_email,
                "expiryTime": int((timezone.now() + timedelta(hours=xui_settings.EXPIRY_SETTINGS["trial_hours"])).timestamp() * 1000)
            }
            
            if not xui_service.create_user(inbound_id, user_data):
                return None, xui_settings.ERROR_MESSAGES["user_creation_failed"]
            
            # تولید کانفیگ بر اساس پروتکل
            if protocol.lower() == "vmess":
                config_data = ConfigGenerator.generate_vmess_config(
                    server.host,
                    inbound.get('port', 443),
                    user_uuid
                )
            elif protocol.lower() == "vless":
                config_data = ConfigGenerator.generate_vless_reality_config(
                    server.host,
                    inbound.get('port', 443),
                    user_uuid,
                    user.get_display_name()
                )
            elif protocol.lower() == "trojan":
                config_data = ConfigGenerator.generate_trojan_config(
                    server.host,
                    inbound.get('port', 443),
                    user_uuid
                )
            else:
                return None, xui_settings.ERROR_MESSAGES["invalid_protocol"]
            
            # ذخیره در دیتابیس
            config_name = xui_settings.CONFIG_NAMING["trial_format"].format(
                protocol=protocol.upper(),
                user_name=user.get_display_name()
            )
            
            user_config = UserConfig.objects.create(
                user=user,
                server=server,
                xui_inbound_id=inbound_id,
                xui_user_id=user.id,
                config_name=config_name,
                config_data=config_data,
                protocol=protocol,
                is_trial=True,
                created_at=timezone.now()
            )
            
            return user_config, xui_settings.SUCCESS_MESSAGES["trial_created"].format(protocol=protocol.upper())
            
        except Exception as e:
            print(f"خطا در ایجاد کانفیگ تستی: {e}")
            return None, f"خطا در ایجاد کانفیگ: {e}"
    
    @staticmethod
    def create_paid_config(user: UsersModel, server: XUIServer, plan: ConfingPlansModel, protocol: str = "vless"):
        """ایجاد کانفیگ پولی برای کاربر"""
        try:
            # ورود به X-UI
            xui_service = XUIService(server)
            if not xui_service.login():
                return None, xui_settings.ERROR_MESSAGES["xui_login_failed"]
            
            # دریافت یا ایجاد inbound خودکار
            inbound_id = xui_service.get_or_create_inbound(protocol)
            if not inbound_id:
                return None, xui_settings.ERROR_MESSAGES["inbound_creation_failed"]
            
            # دریافت اطلاعات inbound
            inbounds = xui_service.get_inbounds()
            inbound = next((i for i in inbounds if i.get('id') == inbound_id), None)
            if not inbound:
                return None, "خطا در دریافت اطلاعات inbound"
            
            # تولید اطلاعات کاربر
            user_uuid = str(uuid.uuid4())
            user_email = xui_settings.EMAIL_SETTINGS["paid_format"].format(
                telegram_id=user.telegram_id,
                plan_id=plan.id
            )
            
            # محاسبه حجم داده (تبدیل MB به GB)
            traffic_gb = plan.traffic_mb / xui_settings.TRAFFIC_SETTINGS["mb_to_gb_conversion"]
            
            # ایجاد کاربر در X-UI
            user_data = {
                **xui_settings.USER_DEFAULT_SETTINGS,
                "id": user_uuid,
                "email": user_email,
                "totalGB": traffic_gb,
                "expiryTime": int((timezone.now() + timedelta(days=xui_settings.EXPIRY_SETTINGS["paid_days"])).timestamp() * 1000)
            }
            
            if not xui_service.create_user(inbound_id, user_data):
                return None, xui_settings.ERROR_MESSAGES["user_creation_failed"]
            
            # تولید کانفیگ بر اساس پروتکل
            if protocol.lower() == "vmess":
                config_data = ConfigGenerator.generate_vmess_config(
                    server.host,
                    inbound.get('port', 443),
                    user_uuid
                )
            elif protocol.lower() == "vless":
                config_data = ConfigGenerator.generate_vless_reality_config(
                    server.host,
                    inbound.get('port', 443),
                    user_uuid,
                    user.get_display_name()
                )
            elif protocol.lower() == "trojan":
                config_data = ConfigGenerator.generate_trojan_config(
                    server.host,
                    inbound.get('port', 443),
                    user_uuid
                )
            else:
                return None, xui_settings.ERROR_MESSAGES["invalid_protocol"]
            
            # ذخیره در دیتابیس
            config_name = xui_settings.CONFIG_NAMING["paid_format"].format(
                plan_name=plan.name,
                user_name=user.get_display_name(),
                protocol=protocol.upper()
            )
            
            user_config = UserConfig.objects.create(
                user=user,
                server=server,
                xui_inbound_id=inbound_id,
                xui_user_id=user.id,
                config_name=config_name,
                config_data=config_data,
                protocol=protocol,
                plan=plan,
                is_trial=False,
                created_at=timezone.now()
            )
            
            return user_config, xui_settings.SUCCESS_MESSAGES["paid_created"].format(protocol=protocol.upper())
            
        except Exception as e:
            print(f"خطا در ایجاد کانفیگ پولی: {e}")
            return None, f"خطا در ایجاد کانفیگ: {e}"
    
    @staticmethod
    def delete_user_config(user_config: UserConfig):
        """حذف کانفیگ کاربر"""
        try:
            # حذف از X-UI
            xui_service = XUIService(user_config.server)
            if xui_service.login():
                xui_service.delete_user(user_config.xui_inbound_id, user_config.xui_user_id)
            
            # حذف از دیتابیس
            user_config.delete()
            return True, xui_settings.SUCCESS_MESSAGES["config_deleted"]
            
        except Exception as e:
            print(f"خطا در حذف کانفیگ: {e}")
            return False, xui_settings.ERROR_MESSAGES["xui_deletion_failed"] 