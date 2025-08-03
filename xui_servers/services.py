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
            
            # تست روش‌های مختلف لاگین
            login_methods = [
                {
                    "url": f"{self.base_url}/login",
                    "data": login_data,
                    "headers": {"Content-Type": "application/json"}
                },
                {
                    "url": f"{self.base_url}/login",
                    "data": login_data,
                    "headers": {"Content-Type": "application/x-www-form-urlencoded"}
                }
            ]
            
            for method in login_methods:
                try:
                    response = self.session.post(
                        method["url"],
                        json=method["data"] if method["headers"].get("Content-Type") == "application/json" else method["data"],
                        headers=method["headers"],
                        timeout=xui_settings.XUI_CONNECTION_SETTINGS["timeout"],
                        verify=xui_settings.XUI_CONNECTION_SETTINGS.get("verify_ssl", False)
                    )
                    
                    if response.status_code == 200:
                        try:
                            data = response.json()
                            if data.get('success'):
                                print(f"✅ لاگین موفق با روش {method['headers'].get('Content-Type', 'unknown')}")
                                return True
                        except:
                            # اگر JSON نامعتبر بود، احتمالاً لاگین موفق بوده
                            print(f"✅ لاگین موفق (بدون JSON معتبر)")
                            return True
                            
                except Exception as e:
                    print(f"❌ خطا در لاگین با روش {method['headers'].get('Content-Type', 'unknown')}: {e}")
                    continue
            
            return False
            
        except Exception as e:
            print(f"خطا در ورود به X-UI: {e}")
            return False
    
    def get_inbounds(self):
        """دریافت لیست inbound ها"""
        try:
            # تست endpoint های مختلف با web base path
            endpoints = [
                "/panel/api/inbounds/list",
                "/panel/inbounds/list",
                "/api/inbounds/list",
                "/inbounds/list", 
                "/api/inbound/list",
                "/inbound/list",
                "/panel/api/inbounds",
                "/api/inbounds"
            ]
            
            for endpoint in endpoints:
                try:
                    response = self.session.get(
                        f"{self.base_url}{endpoint}",
                        timeout=xui_settings.XUI_CONNECTION_SETTINGS["timeout"]
                    )
                    
                    if response.status_code == 200:
                        # بررسی محتوای پاسخ
                        content = response.text.strip()
                        if not content:
                            print(f"⚠️ پاسخ خالی از endpoint: {endpoint}")
                            continue
                        
                        try:
                            data = response.json()
                            # بررسی ساختار داده
                            if isinstance(data, list):
                                print(f"✅ دریافت {len(data)} inbound از {endpoint}")
                                return data
                            elif isinstance(data, dict) and 'obj' in data:
                                print(f"✅ دریافت {len(data['obj'])} inbound از {endpoint}")
                                return data.get('obj', [])
                            elif isinstance(data, dict) and 'data' in data:
                                print(f"✅ دریافت {len(data['data'])} inbound از {endpoint}")
                                return data.get('data', [])
                            else:
                                print(f"⚠️ ساختار نامعتبر از {endpoint}: {type(data)}")
                                continue
                                
                        except json.JSONDecodeError as e:
                            print(f"❌ خطا در پارس JSON از {endpoint}: {e}")
                            print(f"📄 محتوا: {content[:200]}...")
                            continue
                            
                except Exception as e:
                    print(f"❌ خطا در endpoint {endpoint}: {e}")
                    continue
            
            print("❌ هیچ endpoint معتبری یافت نشد")
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
            
            # ایجاد inbound با مدل جدید
            inbound = XUIAPIBuilder.create_inbound_payload(
                port=port,
                protocol=protocol,
                remark=f"User_{user_id}_{protocol}"
            )
            
            # ایجاد API کلاینت
            api_client = XUIAPIClient(self.base_url, self.session)
            
            # ارسال درخواست ایجاد inbound
            inbound_id = api_client.create_inbound(inbound)
            
            if inbound_id:
                print(f"✅ Inbound با موفقیت ایجاد شد - ID: {inbound_id}")
                return inbound_id
            else:
                print("❌ خطا در ایجاد inbound")
                return None
            
        except Exception as e:
            print(f"خطا در ایجاد inbound: {e}")
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
            # تبدیل user_data به XUIClient
            client = XUIClient(
                id=user_data.get('id', str(uuid.uuid4())),
                email=user_data.get('email', ''),
                security=user_data.get('security', 'auto'),
                limit_ip=user_data.get('limitIp', 0),
                total_gb=user_data.get('totalGB', 0),
                expiry_time=user_data.get('expiryTime', 0),
                enable=user_data.get('enable', True),
                tg_id=user_data.get('tgId', ''),
                sub_id=user_data.get('subId', str(uuid.uuid4()).replace("-", "")[:16]),
                comment=user_data.get('comment', ''),
                reset=user_data.get('reset', 0),
                flow=user_data.get('flow', '')
            )
            
            # ایجاد API کلاینت
            api_client = XUIAPIClient(self.base_url, self.session)
            
            # اضافه کردن کلاینت به inbound
            success = api_client.add_client(inbound_id, client)
            
            if success:
                print(f"✅ کاربر با موفقیت به Inbound {inbound_id} اضافه شد")
            else:
                print(f"❌ خطا در اضافه کردن کاربر به Inbound {inbound_id}")
            
            return success
            
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

    def _get_api_url(self, endpoint):
        """دریافت URL کامل API"""
        # استفاده از مسیر صحیح /panel/ به جای /api/
        return f"{self.base_url}panel/{endpoint}"

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
            print(f"🔧 شروع ایجاد کانفیگ تستی برای کاربر {user.get_display_name()}")
            
            # ورود به X-UI
            xui_service = XUIService(server)
            print("🔐 تلاش برای ورود به X-UI...")
            if not xui_service.login():
                print("❌ خطا در ورود به X-UI")
                return None, xui_settings.ERROR_MESSAGES["xui_login_failed"]
            
            print("✅ ورود به X-UI موفق")
            
            # دریافت یا ایجاد inbound جداگانه برای کاربر
            print(f"🔧 تلاش برای ایجاد inbound برای کاربر {user.id}...")
            inbound_id = xui_service.get_or_create_inbound_for_user(user.id, protocol)
            if not inbound_id:
                print("❌ خطا در ایجاد inbound")
                return None, xui_settings.ERROR_MESSAGES["inbound_creation_failed"]
            
            print(f"✅ Inbound با ID {inbound_id} ایجاد شد")
            
            # دریافت اطلاعات inbound
            print("📋 دریافت اطلاعات inbound...")
            inbounds = xui_service.get_inbounds()
            inbound = next((i for i in inbounds if i.get('id') == inbound_id), None)
            if not inbound:
                print("❌ خطا در دریافت اطلاعات inbound")
                return None, "خطا در دریافت اطلاعات inbound"
            
            print(f"✅ اطلاعات inbound دریافت شد: پورت {inbound.get('port', 'نامشخص')}")
            
            # تولید اطلاعات کاربر
            user_uuid = str(uuid.uuid4())
            timestamp = timezone.now().strftime(xui_settings.EMAIL_SETTINGS["timestamp_format"])
            user_email = xui_settings.EMAIL_SETTINGS["trial_format"].format(
                telegram_id=user.telegram_id,
                timestamp=timestamp
            )
            
            print(f"👤 ایجاد کاربر با UUID: {user_uuid}")
            
            # ایجاد کاربر در X-UI
            user_data = {
                **xui_settings.USER_DEFAULT_SETTINGS,
                "id": user_uuid,
                "email": user_email,
                "expiryTime": int((timezone.now() + timedelta(hours=xui_settings.EXPIRY_SETTINGS["trial_hours"])).timestamp() * 1000)
            }
            
            print("🔧 تلاش برای ایجاد کاربر در X-UI...")
            if not xui_service.create_user(inbound_id, user_data):
                print("❌ خطا در ایجاد کاربر در X-UI")
                return None, xui_settings.ERROR_MESSAGES["user_creation_failed"]
            
            print("✅ کاربر در X-UI ایجاد شد")
            
            # تولید کانفیگ بر اساس پروتکل
            print(f"🔧 تولید کانفیگ {protocol.upper()}...")
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
                print(f"❌ پروتکل نامعتبر: {protocol}")
                return None, xui_settings.ERROR_MESSAGES["invalid_protocol"]
            
            print("✅ کانفیگ تولید شد")
            
            # ذخیره در دیتابیس
            expiry_date = timezone.now() + timedelta(hours=24)
            config_name = xui_settings.CONFIG_NAMING["trial_format"].format(
                protocol=protocol.upper(),
                user_name=user.get_display_name(),
                expiry=expiry_date.strftime(xui_settings.CONFIG_NAMING["expiry_format"])
            )
            
            print(f"💾 ذخیره کانفیگ در دیتابیس: {config_name}")
            
            user_config = UserConfig.objects.create(
                user=user,
                server=server,
                xui_inbound_id=inbound_id,
                xui_user_id=str(user.telegram_id) if user.telegram_id else str(user.id),
                config_name=config_name,
                config_data=config_data,
                protocol=protocol,
                is_trial=True,
                expires_at=timezone.now() + timedelta(hours=24)
            )
            
            return user_config, xui_settings.SUCCESS_MESSAGES["trial_created"].format(
                protocol=protocol.upper(),
                duration=xui_settings.EXPIRY_SETTINGS["trial_hours"]
            )
            
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
            timestamp = timezone.now().strftime(xui_settings.EMAIL_SETTINGS["timestamp_format"])
            user_email = xui_settings.EMAIL_SETTINGS["paid_format"].format(
                telegram_id=user.telegram_id,
                plan_id=plan.id,
                timestamp=timestamp
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
            expiry_date = timezone.now() + timedelta(days=xui_settings.EXPIRY_SETTINGS["paid_days"])
            config_name = xui_settings.CONFIG_NAMING["paid_format"].format(
                plan_name=plan.name,
                user_name=user.get_display_name(),
                protocol=protocol.upper(),
                expiry=expiry_date.strftime(xui_settings.CONFIG_NAMING["expiry_format"])
            )
            
            user_config = UserConfig.objects.create(
                user=user,
                server=server,
                xui_inbound_id=inbound_id,
                xui_user_id=str(user.telegram_id) if user.telegram_id else str(user.id),
                config_name=config_name,
                config_data=config_data,
                protocol=protocol,
                plan=plan,
                is_trial=False,
                expires_at=timezone.now() + timedelta(days=30)
            )
            
            return user_config, xui_settings.SUCCESS_MESSAGES["paid_created"].format(
                protocol=protocol.upper(),
                duration=xui_settings.EXPIRY_SETTINGS["paid_days"],
                traffic=traffic_gb
            )
            
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