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
        # به‌روزرسانی base_url برای پشتیبانی از web base path
        base_url = f"http://{server.host}:{server.port}"
        if hasattr(server, 'web_base_path') and server.web_base_path:
            base_url += server.web_base_path
        self.base_url = base_url.rstrip('/')
        
        self.session = requests.Session()
        self.session.headers.update({
            'Content-Type': 'application/json',
            'User-Agent': 'Django-XUI-Bot/2.0'
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
                timeout=xui_settings.XUI_CONNECTION_SETTINGS["timeout"],
                verify=xui_settings.XUI_CONNECTION_SETTINGS.get("verify_ssl", False)
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
            # تست endpoint های مختلف با web base path
            endpoints = [
                "/api/inbounds/list",
                "/inbounds/list", 
                "/api/inbound/list",
                "/inbound/list",
                "/panel/api/inbounds/list",
                "/panel/inbounds/list"
            ]
            
            for endpoint in endpoints:
                try:
                    response = self.session.get(
                        f"{self.base_url}{endpoint}",
                        timeout=xui_settings.XUI_CONNECTION_SETTINGS["timeout"]
                    )
                    if response.status_code == 200:
                        data = response.json()
                        return data.get('obj', [])
                except Exception:
                    continue
            
            return []
            
        except Exception as e:
            print(f"خطا در دریافت inbound ها: {e}")
            return []
    
    def create_user_specific_inbound(self, user_id: int, protocol: str = "vless", port: int | None = None) -> int | None:
        """ایجاد inbound جداگانه برای هر کاربر"""
        try:
            if not self.login():
                print("❌ خطا در ورود به X-UI")
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
                print(f"❌ پروتکل {protocol} پشتیبانی نمی‌شود")
                return None
            
            # تنظیمات stream و settings از فایل تنظیمات
            settings = dict(protocol_config.get("settings", {}))
            stream_settings = dict(protocol_config.get("stream_settings", {}))
            
            # برای VLess Reality، تنظیمات تصادفی اضافه کن
            if protocol.lower() == "vless":
                # انتخاب دامنه فیک تصادفی
                fake_domain = random.choice(xui_settings.FAKE_DOMAINS)
                stream_settings["realitySettings"]["serverNames"] = [fake_domain]
                
                # انتخاب کلید عمومی تصادفی
                public_key = random.choice(xui_settings.REALITY_PUBLIC_KEYS)
                stream_settings["realitySettings"]["publicKey"] = public_key
                
                # تولید shortId تصادفی
                short_id = ''.join(random.choices(string.hexdigits.lower(), k=8))
                stream_settings["realitySettings"]["shortIds"] = [short_id]
            
            # نام inbound مخصوص کاربر
            inbound_name = f"User-{user_id}-{protocol.upper()}-{port}"
            
            # فرمت صحیح برای X-UI فعلی
            inbound_data = {
                "remark": inbound_name,
                "port": port,
                "protocol": protocol,
                "settings": json.dumps(settings),  # تبدیل به JSON string
                "streamSettings": json.dumps(stream_settings),  # تبدیل به JSON string
                "sniffing": xui_settings.INBOUND_SETTINGS["sniffing"],  # استفاده از فرمت صحیح
                "enable": True,
                "expiryTime": 0,
                "listen": "",
                "up": 0,  # تغییر از آرایه به عدد
                "down": 0,  # تغییر از آرایه به عدد
                "total": 0
            }
            
            print(f"📤 ارسال درخواست ایجاد inbound: {inbound_name}")
            print(f"📊 داده ارسالی: {json.dumps(inbound_data, indent=2)}")
            
            # تست endpoint های مختلف برای ایجاد inbound
            add_endpoints = [
                "/api/inbounds/add",
                "/inbounds/add",
                "/api/inbound/add", 
                "/inbound/add",
                "/panel/api/inbounds/add",
                "/panel/inbounds/add"
            ]
            
            for endpoint in add_endpoints:
                try:
                    print(f"🔗 تست endpoint: {endpoint}")
                    response = self.session.post(
                        f"{self.base_url}{endpoint}",
                        json=inbound_data,
                        timeout=xui_settings.XUI_CONNECTION_SETTINGS["timeout"]
                    )
                    
                    print(f"📊 وضعیت پاسخ: {response.status_code}")
                    
                    if response.status_code == 200:
                        try:
                            data = response.json()
                            print(f"📄 پاسخ JSON: {json.dumps(data, indent=2)}")
                            
                            if data.get('success'):
                                inbound_id = data.get('obj', {}).get('id')
                                print(f"✅ Inbound با موفقیت ایجاد شد - ID: {inbound_id}")
                                return inbound_id
                            else:
                                print(f"❌ خطا در پاسخ: {data.get('msg', 'خطای نامشخص')}")
                        except json.JSONDecodeError:
                            print(f"❌ پاسخ JSON نامعتبر: {response.text}")
                    else:
                        print(f"❌ خطای HTTP: {response.status_code}")
                        print(f"📄 محتوای پاسخ: {response.text}")
                        
                except Exception as e:
                    print(f"❌ خطا در endpoint {endpoint}: {e}")
                    continue
            
            print("❌ هیچ endpoint کارآمدی یافت نشد")
            return None
            
        except Exception as e:
            print(f"❌ خطا در ایجاد inbound کاربر: {e}")
            return None
    
    def get_or_create_inbound_for_user(self, user_id: int, protocol: str = "vless"):
        """دریافت یا ایجاد inbound جداگانه برای هر کاربر"""
        try:
            # ابتدا inbound های موجود را بررسی کن
            inbounds = self.get_inbounds()
            
            # inbound مخصوص کاربر را پیدا کن
            user_inbound = None
            for inbound in inbounds:
                if (inbound.get('remark', '').startswith(f"User-{user_id}-") and 
                    inbound.get('protocol') == protocol):
                    user_inbound = inbound
                    break
            
            if user_inbound:
                # از inbound موجود کاربر استفاده کن
                return user_inbound.get('id')
            else:
                # inbound جدید برای کاربر ایجاد کن
                return self.create_user_specific_inbound(user_id, protocol)
                
        except Exception as e:
            print(f"خطا در دریافت/ایجاد inbound کاربر: {e}")
            return None
    
    def create_auto_inbound(self, protocol: str = "vless", port: int | None = None) -> int | None:
        """ایجاد خودکار inbound با تنظیمات پیش‌فرض (برای سازگاری)"""
        return self.create_user_specific_inbound(0, protocol, port)
    
    def get_or_create_inbound(self, protocol: str = "vless"):
        """دریافت یا ایجاد inbound خودکار (برای سازگاری)"""
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
            
            # تست endpoint های مختلف برای ایجاد کاربر
            update_endpoints = [
                "/api/inbounds/updateClient",
                "/inbounds/updateClient",
                "/api/inbound/updateClient",
                "/inbound/updateClient",
                "/panel/api/inbounds/updateClient",
                "/panel/inbounds/updateClient"
            ]
            
            for endpoint in update_endpoints:
                try:
                    response = self.session.post(
                        f"{self.base_url}{endpoint}",
                        json=payload,
                        timeout=10
                    )
                    
                    if response.status_code == 200:
                        data = response.json()
                        return data.get('success', False)
                except Exception:
                    continue
            
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
            
            # تست endpoint های مختلف برای حذف کاربر
            update_endpoints = [
                "/api/inbounds/updateClient",
                "/inbounds/updateClient",
                "/api/inbound/updateClient",
                "/inbound/updateClient",
                "/panel/api/inbounds/updateClient",
                "/panel/inbounds/updateClient"
            ]
            
            for endpoint in update_endpoints:
                try:
                    response = self.session.post(
                        f"{self.base_url}{endpoint}",
                        json=payload,
                        timeout=10
                    )
                    
                    if response.status_code == 200:
                        data = response.json()
                        return data.get('success', False)
                except Exception:
                    continue
            
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
            
            # تست endpoint های مختلف برای به‌روزرسانی کاربر
            update_endpoints = [
                "/api/inbounds/updateClient",
                "/inbounds/updateClient",
                "/api/inbound/updateClient",
                "/inbound/updateClient",
                "/panel/api/inbounds/updateClient",
                "/panel/inbounds/updateClient"
            ]
            
            for endpoint in update_endpoints:
                try:
                    response = self.session.post(
                        f"{self.base_url}{endpoint}",
                        json=payload,
                        timeout=10
                    )
                    
                    if response.status_code == 200:
                        data = response.json()
                        return data.get('success', False)
                except Exception:
                    continue
            
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
            
            # دریافت یا ایجاد inbound جداگانه برای کاربر
            inbound_id = xui_service.get_or_create_inbound_for_user(user.id, protocol)
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
            
            # دریافت یا ایجاد inbound جداگانه برای کاربر
            inbound_id = xui_service.get_or_create_inbound_for_user(user.id, protocol)
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