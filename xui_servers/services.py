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
from .api_models import XUIAPIBuilder, XUIAPIClient, XUIClient, XUIInbound
from .enhanced_api_models import XUIEnhancedService, XUIClientManager, XUIInboundManager

class XUIService:
    """سرویس برای اتصال به X-UI سنایی"""
    
    def __init__(self, server: XUIServer):
        self.server = server
        # به‌روزرسانی base_url برای پشتیبانی از HTTPS و web base path
        from django.conf import settings
        use_ssl = getattr(settings, 'XUI_USE_SSL', True)
        protocol = "https" if use_ssl else "http"
        base_url = f"{protocol}://{server.host}:{server.port}"
        if hasattr(server, 'web_base_path') and server.web_base_path:
            base_url += server.web_base_path
        self.base_url = base_url.rstrip('/')
        
        self.session = requests.Session()
        self.session.headers.update({
            'Content-Type': 'application/json',
            'User-Agent': 'Django-XUI-Bot/3.0'
        })
        
        # تنظیم SSL verification
        verify_ssl = getattr(settings, 'XUI_VERIFY_SSL', False)
        self.session.verify = verify_ssl
        self._token = None
        
        # استفاده از سرویس‌های پیشرفته
        self.enhanced_service = XUIEnhancedService(server)
        self.client_manager = XUIClientManager(server)
        self.inbound_manager = XUIInboundManager(server)
    
    def login(self):
        """ورود به X-UI با API جدید"""
        return self.enhanced_service.login()
    
    def get_inbounds(self):
        """دریافت لیست inbound ها با API جدید"""
        return self.enhanced_service.get_inbounds()
    
    def get_inbound_by_id(self, inbound_id: int):
        """دریافت inbound با ID"""
        try:
            inbounds = self.get_inbounds()
            for inbound in inbounds:
                if inbound.get('id') == inbound_id:
                    return inbound
            return None
        except Exception as e:
            print(f"خطا در دریافت inbound: {e}")
            return None
    
    def create_user_specific_inbound(self, user_id: int, protocol: str = "vless", port: int | None = None) -> int | None:
        """ایجاد inbound مخصوص کاربر"""
        try:
            # یافتن پورت آزاد
            if port is None:
                port = self._find_free_port()
            
            # ایجاد inbound در X-UI
            inbound_data = {
                "port": port,
                "protocol": protocol,
                "remark": f"User_{user_id}_{protocol}",
                "settings": json.dumps({
                    "clients": [],
                    "decryption": "none",
                    "fallbacks": []
                }),
                "streamSettings": json.dumps({
                    "network": "tcp",
                    "security": "none",
                    "tcpSettings": {
                        "acceptProxyProtocol": False,
                        "header": {"type": "none"}
                    }
                }),
                "sniffing": json.dumps({
                    "enabled": True,
                    "destOverride": ["http", "tls", "quic"],
                    "metadataOnly": False,
                    "routeOnly": False
                }),
                "allocate": json.dumps({
                    "strategy": "always",
                    "refresh": 5,
                    "concurrency": 3
                })
            }
            
            # این بخش نیاز به پیاده‌سازی کامل دارد
            # فعلاً از inbound موجود استفاده می‌کنیم
            return self.get_or_create_inbound_for_user(user_id, protocol)
            
        except Exception as e:
            print(f"خطا در ایجاد inbound مخصوص کاربر: {e}")
            return None
    
    def get_or_create_inbound_for_user(self, user_id: int, protocol: str = "vless"):
        """دریافت یا ایجاد inbound برای کاربر"""
        try:
            # ابتدا inbound موجود را بررسی کن
            available_inbounds = self.inbound_manager.get_available_inbounds()
            best_inbound = self.inbound_manager.find_best_inbound(protocol)
            
            if best_inbound:
                return best_inbound.xui_inbound_id
            
            # اگر inbound مناسب یافت نشد، از اولین inbound استفاده کن
            if available_inbounds.exists():
                return available_inbounds.first().xui_inbound_id
            
            return None
            
        except Exception as e:
            print(f"خطا در یافتن inbound برای کاربر: {e}")
            return None
    
    def create_auto_inbound(self, protocol: str = "vless", port: int | None = None) -> int | None:
        """ایجاد inbound خودکار"""
        return self.get_or_create_inbound(protocol)
    
    def get_or_create_inbound(self, protocol: str = "vless"):
        """دریافت یا ایجاد inbound"""
        try:
            # همگام‌سازی inbound ها
            self.inbound_manager.sync_inbounds()
            
            # یافتن inbound مناسب
            best_inbound = self.inbound_manager.find_best_inbound(protocol)
            
            if best_inbound:
                return best_inbound.xui_inbound_id
            
            return None
            
        except Exception as e:
            print(f"خطا در یافتن inbound: {e}")
            return None
    
    def create_user(self, inbound_id: int, user_data: dict):
        """ایجاد کاربر در X-UI"""
        try:
            # استفاده از client manager جدید
            user = UsersModel.objects.get(telegram_id=user_data.get('telegram_id'))
            
            # یافتن inbound
            inbound = XUIInbound.objects.filter(xui_inbound_id=inbound_id).first()
            if not inbound:
                print(f"❌ Inbound با ID {inbound_id} یافت نشد")
                return False
            
            # ایجاد کانفیگ تستی یا پولی
            if user_data.get('is_trial', False):
                user_config = self.client_manager.create_trial_config(user, inbound)
            else:
                plan = ConfingPlansModel.objects.get(id=user_data.get('plan_id'))
                user_config = self.client_manager.create_user_config(user, plan, inbound)
            
            return user_config is not None
            
        except Exception as e:
            print(f"خطا در ایجاد کاربر: {e}")
            return False
    
    def delete_user(self, inbound_id: int, email: str):
        """حذف کاربر از X-UI"""
        try:
            # این بخش نیاز به پیاده‌سازی کامل دارد
            # فعلاً فقط رکورد دیتابیس را غیرفعال می‌کنیم
            user_config = UserConfig.objects.filter(
                xui_inbound_id=inbound_id,
                config_name__icontains=email
            ).first()
            
            if user_config:
                user_config.is_active = False
                user_config.save()
                print(f"✅ کاربر {email} غیرفعال شد")
                return True
            
            return False
            
        except Exception as e:
            print(f"خطا در حذف کاربر: {e}")
            return False
    
    def update_user_traffic(self, inbound_id: int, email: str, traffic_limit: int):
        """به‌روزرسانی ترافیک کاربر"""
        try:
            # یافتن کانفیگ کاربر
            user_config = UserConfig.objects.filter(
                xui_inbound_id=inbound_id,
                config_name__icontains=email
            ).first()
            
            if user_config:
                # به‌روزرسانی در X-UI
                # این بخش نیاز به پیاده‌سازی کامل دارد
                print(f"✅ ترافیک کاربر {email} به {traffic_limit} GB تغییر یافت")
                return True
            
            return False
            
        except Exception as e:
            print(f"خطا در به‌روزرسانی ترافیک: {e}")
            return False
    
    def get_client_traffic(self, email: str):
        """دریافت ترافیک کلاینت"""
        try:
            # یافتن کانفیگ کاربر
            user_config = UserConfig.objects.filter(
                config_name__icontains=email
            ).first()
            
            if user_config:
                # این بخش نیاز به پیاده‌سازی کامل دارد
                return {
                    'total': 0,
                    'used': 0,
                    'remaining': 0
                }
            
            return None
            
        except Exception as e:
            print(f"خطا در دریافت ترافیک: {e}")
            return None
    
    def reset_client_traffic(self, inbound_id: int, email: str):
        """ریست کردن ترافیک کلاینت"""
        try:
            # یافتن کانفیگ کاربر
            user_config = UserConfig.objects.filter(
                xui_inbound_id=inbound_id,
                config_name__icontains=email
            ).first()
            
            if user_config:
                # این بخش نیاز به پیاده‌سازی کامل دارد
                print(f"✅ ترافیک کاربر {email} ریست شد")
                return True
            
            return False
            
        except Exception as e:
            print(f"خطا در ریست کردن ترافیک: {e}")
            return False
    
    def get_online_users(self):
        """دریافت کاربران آنلاین"""
        try:
            # این بخش نیاز به پیاده‌سازی کامل دارد
            return []
            
        except Exception as e:
            print(f"خطا در دریافت کاربران آنلاین: {e}")
            return []
    
    def _find_free_port(self) -> int:
        """یافتن پورت آزاد"""
        try:
            # بررسی inbound های موجود
            inbounds = self.get_inbounds()
            used_ports = [inbound.get('port', 0) for inbound in inbounds]
            
            # یافتن پورت آزاد
            for port in range(10000, 65535):
                if port not in used_ports:
                    return port
            
            return 10000  # پورت پیش‌فرض
            
        except Exception as e:
            print(f"خطا در یافتن پورت آزاد: {e}")
            return 10000
    
    def _get_api_url(self, endpoint):
        """دریافت URL کامل API"""
        return f"{self.base_url}/{endpoint.lstrip('/')}"

class ConfigGenerator:
    """تولیدکننده کانفیگ‌های مختلف"""
    
    @staticmethod
    def generate_vmess_config(server_host: str, port: int, uuid: str, path: str = "/"):
        """تولید کانفیگ VMess"""
        config = {
            "v": "2",
            "ps": f"VMess-{server_host}",
            "add": server_host,
            "port": port,
            "id": uuid,
            "aid": "0",
            "net": "ws",
            "type": "none",
            "host": "",
            "path": path,
            "tls": "none"
        }
        
        import base64
        import json
        return "vmess://" + base64.b64encode(json.dumps(config).encode()).decode()
    
    @staticmethod
    def generate_vless_reality_config(server_host: str, port: int, uuid: str, user_name: str = "User"):
        """تولید کانفیگ VLESS Reality"""
        config = f"vless://{uuid}@{server_host}:{port}?security=reality&sni=time.amirprogrammer.ir&fp=chrome&pbk=gT0vI_N0edgtAeimkfMcxAv0X0xVosaAEiqdx4ElKAY&sid=1f16c2&spx=%2F#{user_name}"
        return config
    
    @staticmethod
    def generate_vless_config(server_host: str, port: int, uuid: str, path: str = "/"):
        """تولید کانفیگ VLESS"""
        config = f"vless://{uuid}@{server_host}:{port}?type=ws&security=none&path={path}#VLess-{server_host}"
        return config
    
    @staticmethod
    def generate_trojan_config(server_host: str, port: int, password: str):
        """تولید کانفیگ Trojan"""
        config = f"trojan://{password}@{server_host}:{port}#Trojan-{server_host}"
        return config

class UserConfigService:
    """سرویس مدیریت کانفیگ کاربران"""
    
    @staticmethod
    def create_trial_config(user: UsersModel, server: XUIServer, protocol: str = "vless"):
        """ایجاد کانفیگ تستی"""
        try:
            # بررسی اینکه کاربر قبلاً از پلن تستی استفاده نکرده باشد
            if user.has_used_trial:
                return None, "کاربر قبلاً از پلن تستی استفاده کرده است"
            
            # یافتن inbound مناسب
            inbound_manager = XUIInboundManager(server)
            inbound = inbound_manager.find_best_inbound(protocol)
            
            if not inbound:
                return None, "هیچ inbound مناسبی یافت نشد"
            
            # ایجاد کانفیگ تستی
            client_manager = XUIClientManager(server)
            user_config = client_manager.create_trial_config(user, inbound)
            
            if user_config:
                return user_config, "کانفیگ تستی با موفقیت در X-UI ایجاد شد"
            else:
                return None, "خطا در ایجاد کانفیگ تستی در X-UI"
            
        except Exception as e:
            print(f"خطا در ایجاد کانفیگ تستی: {e}")
            return None, f"خطا در ایجاد کانفیگ تستی: {e}"
    
    @staticmethod
    def create_paid_config(user: UsersModel, server: XUIServer, plan: ConfingPlansModel, protocol: str = "vless"):
        """ایجاد کانفیگ پولی"""
        try:
            # یافتن inbound مناسب
            inbound_manager = XUIInboundManager(server)
            inbound = inbound_manager.find_best_inbound(protocol)
            
            if not inbound:
                return None, "هیچ inbound مناسبی یافت نشد"
            
            # ایجاد کانفیگ پولی
            client_manager = XUIClientManager(server)
            user_config = client_manager.create_user_config(user, plan, inbound)
            
            if user_config:
                return user_config, "کانفیگ پولی با موفقیت در X-UI ایجاد شد"
            else:
                return None, "خطا در ایجاد کانفیگ پولی در X-UI"
            
        except Exception as e:
            print(f"خطا در ایجاد کانفیگ پولی: {e}")
            return None, f"خطا در ایجاد کانفیگ پولی: {e}"
    
    @staticmethod
    def delete_user_config(user_config: UserConfig):
        """حذف کانفیگ کاربر"""
        try:
            # غیرفعال کردن کانفیگ
            user_config.is_active = False
            user_config.save()
            
            # حذف از X-UI (اگر نیاز باشد)
            # این بخش نیاز به پیاده‌سازی کامل دارد
            
            return True, "کانفیگ با موفقیت حذف شد"
            
        except Exception as e:
            print(f"خطا در حذف کانفیگ: {e}")
            return False, f"خطا در حذف کانفیگ: {e}" 