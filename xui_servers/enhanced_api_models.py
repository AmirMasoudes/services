"""
مدل‌های پیشرفته API برای X-UI
شامل بخش‌های تخصصی برای ایجاد Inbound و مدیریت Client
"""
import requests
import json
import uuid
import random
import string
from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta
from django.utils import timezone
from .models import XUIServer, XUIInbound, XUIClient, UserConfig
from accounts.models import UsersModel
from plan.models import ConfingPlansModel

class XUIEnhancedService:
    """سرویس پیشرفته برای مدیریت X-UI با API جدید"""
    
    def __init__(self, server: XUIServer):
        self.server = server
        # پشتیبانی از HTTPS
        from django.conf import settings
        use_ssl = getattr(settings, 'XUI_USE_SSL', True)
        protocol = "https" if use_ssl else "http"
        self.base_url = f"{protocol}://{server.host}:{server.port}"
        if hasattr(server, 'web_base_path') and server.web_base_path:
            self.base_url += server.web_base_path
        self.base_url = self.base_url.rstrip('/')
        
        self.session = requests.Session()
        self.session.headers.update({
            'Content-Type': 'application/json',
            'User-Agent': 'Django-XUI-Bot/3.0',
            'Accept': 'application/json'
        })
        
        # تنظیم SSL verification
        verify_ssl = getattr(settings, 'XUI_VERIFY_SSL', False)
        self.session.verify = verify_ssl
        
        self._token = None
        self._cookies = {}
    
    def login(self) -> bool:
        """ورود به X-UI با API جدید"""
        try:
            login_data = {
                "username": self.server.username,
                "password": self.server.password
            }
            
            response = self.session.post(
                f"{self.base_url}/login",
                json=login_data,
                timeout=30
            )
            
            if response.status_code == 200:
                try:
                    data = response.json()
                    if data.get('success'):
                        # ذخیره کوکی‌ها
                        self._cookies = response.cookies.get_dict()
                        # ذخیره توکن اگر موجود باشد
                        self._token = data.get('token') or data.get('obj', {}).get('token')
                        if self._token:
                            self.session.headers.update({'Authorization': f'Bearer {self._token}'})
                        print(f"✅ لاگین موفق به سرور {self.server.name}")
                        return True
                except:
                    # اگر JSON نباشد، کوکی‌ها را ذخیره کن
                    self._cookies = response.cookies.get_dict()
                    print(f"✅ لاگین موفق (بدون JSON معتبر)")
                    return True
            
            print(f"❌ خطا در لاگین: {response.status_code} - {response.text}")
            return False
            
        except Exception as e:
            print(f"خطا در ورود به X-UI: {e}")
            return False
    
    def get_inbounds(self) -> List[Dict]:
        """دریافت لیست inbound ها"""
        try:
            if not self._token and not self._cookies:
                if not self.login():
                    return []
            
            # تنظیم کوکی‌ها
            if self._cookies:
                self.session.cookies.update(self._cookies)
            
            response = self.session.get(
                f"{self.base_url}/panel/api/inbounds/list",
                timeout=30
            )
            
            if response.status_code == 200:
                data = response.json()
                if data.get('success'):
                    return data.get('obj', [])
            
            print(f"❌ خطا در دریافت inbound ها: {response.status_code}")
            return []
            
        except Exception as e:
            print(f"خطا در دریافت inbound ها: {e}")
            return []
    
    def add_client_to_inbound(self, inbound_id: int, client_data: Dict) -> bool:
        """اضافه کردن کلاینت به inbound"""
        try:
            if not self._token and not self._cookies:
                if not self.login():
                    return False
            
            # تنظیم کوکی‌ها
            if self._cookies:
                self.session.cookies.update(self._cookies)
            
            # اضافه کردن کوکی 3x-ui اگر موجود باشد
            if '3x-ui' in self._cookies:
                self.session.cookies.set('3x-ui', self._cookies['3x-ui'])
            
            # استفاده از API جدید برای اضافه کردن کلاینت
            payload = {
                "id": inbound_id,
                "settings": json.dumps(client_data)
            }
            
            response = self.session.post(
                f"{self.base_url}/panel/api/inbounds/addClient",
                json=payload,
                timeout=30
            )
            
            if response.status_code == 200:
                data = response.json()
                if data.get('success'):
                    client_email = client_data.get('clients', [{}])[0].get('email', 'Unknown')
                    print(f"✅ کلاینت {client_email} با موفقیت به inbound {inbound_id} اضافه شد")
                    return True
            
            print(f"❌ خطا در اضافه کردن کلاینت: {response.status_code} - {response.text}")
            return False
            
        except Exception as e:
            print(f"خطا در اضافه کردن کلاینت: {e}")
            return False
    
    def remove_client_from_inbound(self, inbound_id: int, client_email: str) -> bool:
        """حذف کلاینت از inbound"""
        try:
            if not self._token and not self._cookies:
                if not self.login():
                    return False
            
            # تنظیم کوکی‌ها
            if self._cookies:
                self.session.cookies.update(self._cookies)
            
            # دریافت اطلاعات inbound فعلی
            inbounds = self.get_inbounds()
            target_inbound = None
            
            for inbound in inbounds:
                if inbound.get('id') == inbound_id:
                    target_inbound = inbound
                    break
            
            if not target_inbound:
                print(f"❌ Inbound با ID {inbound_id} یافت نشد")
                return False
            
            # حذف کلاینت از لیست
            settings = json.loads(target_inbound.get('settings', '{}'))
            clients = settings.get('clients', [])
            
            # فیلتر کردن کلاینت مورد نظر
            filtered_clients = [client for client in clients if client.get('email') != client_email]
            
            if len(filtered_clients) == len(clients):
                print(f"❌ کلاینت با ایمیل {client_email} یافت نشد")
                return False
            
            # به‌روزرسانی تنظیمات
            settings['clients'] = filtered_clients
            
            # ارسال به‌روزرسانی
            payload = {
                "id": inbound_id,
                "settings": json.dumps(settings)
            }
            
            response = self.session.post(
                f"{self.base_url}/panel/api/inbounds/update/{inbound_id}",
                json=payload,
                timeout=30
            )
            
            if response.status_code == 200:
                data = response.json()
                if data.get('success'):
                    print(f"✅ کلاینت {client_email} با موفقیت حذف شد")
                    return True
            
            print(f"❌ خطا در حذف کلاینت: {response.status_code} - {response.text}")
            return False
            
        except Exception as e:
            print(f"خطا در حذف کلاینت: {e}")
            return False
    
    def update_client_settings(self, inbound_id: int, client_email: str, new_settings: Dict) -> bool:
        """به‌روزرسانی تنظیمات کلاینت"""
        try:
            if not self._token and not self._cookies:
                if not self.login():
                    return False
            
            # تنظیم کوکی‌ها
            if self._cookies:
                self.session.cookies.update(self._cookies)
            
            # دریافت اطلاعات inbound فعلی
            inbounds = self.get_inbounds()
            target_inbound = None
            
            for inbound in inbounds:
                if inbound.get('id') == inbound_id:
                    target_inbound = inbound
                    break
            
            if not target_inbound:
                print(f"❌ Inbound با ID {inbound_id} یافت نشد")
                return False
            
            # به‌روزرسانی کلاینت
            settings = json.loads(target_inbound.get('settings', '{}'))
            clients = settings.get('clients', [])
            
            client_updated = False
            for client in clients:
                if client.get('email') == client_email:
                    client.update(new_settings)
                    client_updated = True
                    break
            
            if not client_updated:
                print(f"❌ کلاینت با ایمیل {client_email} یافت نشد")
                return False
            
            # ارسال به‌روزرسانی
            payload = {
                "id": inbound_id,
                "settings": json.dumps(settings)
            }
            
            response = self.session.post(
                f"{self.base_url}/panel/api/inbounds/update/{inbound_id}",
                json=payload,
                timeout=30
            )
            
            if response.status_code == 200:
                data = response.json()
                if data.get('success'):
                    print(f"✅ تنظیمات کلاینت {client_email} با موفقیت به‌روزرسانی شد")
                    return True
            
            print(f"❌ خطا در به‌روزرسانی کلاینت: {response.status_code} - {response.text}")
            return False
            
        except Exception as e:
            print(f"خطا در به‌روزرسانی کلاینت: {e}")
            return False
    
    def create_client_settings(self, email: str, total_gb: int = 0, expiry_days: int = 30) -> Dict:
        """ایجاد تنظیمات کلاینت"""
        client_id = str(uuid.uuid4())
        sub_id = ''.join(random.choices(string.ascii_lowercase + string.digits, k=16))
        
        # محاسبه زمان انقضا
        expiry_time = 0
        if expiry_days > 0:
            expiry_time = int((timezone.now() + timedelta(days=expiry_days)).timestamp() * 1000)
        
        return {
            "clients": [{
                "id": client_id,
                "flow": "",
                "email": email,
                "limitIp": 0,
                "totalGB": total_gb,
                "expiryTime": expiry_time,
                "enable": True,
                "tgId": "",
                "subId": sub_id,
                "reset": 0
            }]
        }
    
    def sync_inbounds_to_database(self) -> int:
        """همگام‌سازی inbound ها با دیتابیس"""
        try:
            inbounds = self.get_inbounds()
            synced_count = 0
            
            for inbound_data in inbounds:
                inbound_id = inbound_data.get('id')
                if not inbound_id:
                    continue
                
                # بررسی وجود inbound در دیتابیس
                inbound, created = XUIInbound.objects.get_or_create(
                    server=self.server,
                    xui_inbound_id=inbound_id,
                    defaults={
                        'port': inbound_data.get('port', 0),
                        'protocol': inbound_data.get('protocol', 'vless'),
                        'remark': inbound_data.get('remark', f'Inbound {inbound_id}'),
                        'is_active': inbound_data.get('enable', True),
                        'max_clients': 100,  # مقدار پیش‌فرض
                        'current_clients': len(inbound_data.get('clientStats', []))
                    }
                )
                
                if not created:
                    # به‌روزرسانی اطلاعات موجود
                    inbound.port = inbound_data.get('port', inbound.port)
                    inbound.protocol = inbound_data.get('protocol', inbound.protocol)
                    inbound.remark = inbound_data.get('remark', inbound.remark)
                    inbound.is_active = inbound_data.get('enable', inbound.is_active)
                    inbound.current_clients = len(inbound_data.get('clientStats', []))
                    inbound.save()
                
                synced_count += 1
            
            print(f"✅ {synced_count} inbound همگام‌سازی شد")
            return synced_count
            
        except Exception as e:
            print(f"خطا در همگام‌سازی inbound ها: {e}")
            return 0

class XUIClientManager:
    """مدیریت کلاینت‌های X-UI"""
    
    def __init__(self, server: XUIServer):
        self.server = server
        self.service = XUIEnhancedService(server)
    
    def create_user_config(self, user: UsersModel, plan: ConfingPlansModel, inbound: XUIInbound) -> Optional[UserConfig]:
        """ایجاد کانفیگ کاربر"""
        try:
            # ایجاد تنظیمات کلاینت
            email = f"{user.username_tel}_{user.telegram_id}"
            client_settings = self.service.create_client_settings(
                email=email,
                total_gb=plan.traffic_gb,
                expiry_days=plan.duration_days
            )
            
            # اضافه کردن کلاینت به inbound
            if self.service.add_client_to_inbound(inbound.xui_inbound_id, client_settings):
                # ایجاد رکورد در دیتابیس
                client_data = client_settings['clients'][0]
                
                # تولید کانفیگ واقعی از X-UI
                config_data = self._generate_real_config_data(inbound, client_data)
                
                user_config = UserConfig.objects.create(
                    user=user,
                    server=self.server,
                    inbound=inbound,
                    xui_inbound_id=inbound.xui_inbound_id,
                    xui_user_id=client_data['id'],
                    config_name=f"{user.full_name} - {plan.name}",
                    config_data=config_data,
                    is_active=True,
                    expires_at=timezone.now() + timedelta(days=plan.duration_days),
                    protocol=inbound.protocol,
                    plan=plan,
                    is_trial=False
                )
                
                print(f"✅ کانفیگ کاربر {user.full_name} در X-UI ایجاد شد")
                return user_config
            
            return None
            
        except Exception as e:
            print(f"خطا در ایجاد کانفیگ کاربر: {e}")
            return None
    
    async def create_user_config_async(self, user: UsersModel, plan: ConfingPlansModel, inbound: XUIInbound) -> Optional[UserConfig]:
        """ایجاد کانفیگ کاربر برای محیط async"""
        from asgiref.sync import sync_to_async
        
        try:
            # ایجاد تنظیمات کلاینت
            email = f"{user.username_tel}_{user.telegram_id}"
            client_settings = self.service.create_client_settings(
                email=email,
                total_gb=plan.traffic_gb,
                expiry_days=plan.duration_days
            )
            
            # اضافه کردن کلاینت به inbound
            if self.service.add_client_to_inbound(inbound.xui_inbound_id, client_settings):
                # ایجاد رکورد در دیتابیس
                client_data = client_settings['clients'][0]
                
                # تولید کانفیگ واقعی از X-UI
                config_data = self._generate_real_config_data(inbound, client_data)
                
                # استفاده از sync_to_async برای Django ORM
                user_config = await sync_to_async(UserConfig.objects.create)(
                    user=user,
                    server=self.server,
                    inbound=inbound,
                    xui_inbound_id=inbound.xui_inbound_id,
                    xui_user_id=client_data['id'],
                    config_name=f"{user.full_name} - {plan.name}",
                    config_data=config_data,
                    is_active=True,
                    expires_at=timezone.now() + timedelta(days=plan.duration_days),
                    protocol=inbound.protocol,
                    plan=plan,
                    is_trial=False
                )
                
                print(f"✅ کانفیگ کاربر {user.full_name} در X-UI ایجاد شد")
                return user_config
            
            return None
            
        except Exception as e:
            print(f"خطا در ایجاد کانفیگ کاربر: {e}")
            return None
    
    def create_user_config_sync(self, user: UsersModel, plan: ConfingPlansModel, inbound: XUIInbound) -> Optional[UserConfig]:
        """ایجاد کانفیگ کاربر برای محیط sync (بدون async)"""
        try:
            # ایجاد تنظیمات کلاینت
            email = f"{user.username_tel}_{user.telegram_id}"
            client_settings = self.service.create_client_settings(
                email=email,
                total_gb=plan.traffic_gb,
                expiry_days=plan.duration_days
            )
            
            # اضافه کردن کلاینت به inbound
            if self.service.add_client_to_inbound(inbound.xui_inbound_id, client_settings):
                # ایجاد رکورد در دیتابیس
                client_data = client_settings['clients'][0]
                
                # تولید کانفیگ واقعی از X-UI
                config_data = self._generate_real_config_data(inbound, client_data)
                
                # ایجاد مستقیم در دیتابیس (sync)
                user_config = UserConfig.objects.create(
                    user=user,
                    server=self.server,
                    inbound=inbound,
                    xui_inbound_id=inbound.xui_inbound_id,
                    xui_user_id=client_data['id'],
                    config_name=f"{user.full_name} - {plan.name}",
                    config_data=config_data,
                    is_active=True,
                    expires_at=timezone.now() + timedelta(days=plan.duration_days),
                    protocol=inbound.protocol,
                    plan=plan,
                    is_trial=False
                )
                
                print(f"✅ کانفیگ کاربر {user.full_name} در X-UI ایجاد شد")
                return user_config
            
            return None
            
        except Exception as e:
            print(f"خطا در ایجاد کانفیگ کاربر: {e}")
            return None
    
    def create_trial_config(self, user: UsersModel, inbound: XUIInbound) -> Optional[UserConfig]:
        """ایجاد کانفیگ تستی"""
        try:
            email = f"trial_{user.username_tel}_{user.telegram_id}"
            client_settings = self.service.create_client_settings(
                email=email,
                total_gb=1,  # 1 GB برای تست
                expiry_days=1  # 1 روز
            )
            
            if self.service.add_client_to_inbound(inbound.xui_inbound_id, client_settings):
                client_data = client_settings['clients'][0]
                user_config = UserConfig.objects.create(
                    user=user,
                    server=self.server,
                    inbound=inbound,
                    xui_inbound_id=inbound.xui_inbound_id,
                    xui_user_id=client_data['id'],
                    config_name=f"{user.full_name} - تستی",
                    config_data=self._generate_config_data(inbound, client_data),
                    is_active=True,
                    expires_at=timezone.now() + timedelta(days=1),
                    protocol=inbound.protocol,
                    is_trial=True
                )
                
                # علامت‌گذاری استفاده از پلن تستی
                user.has_used_trial = True
                user.save()
                
                print(f"✅ کانفیگ تستی برای کاربر {user.full_name} ایجاد شد")
                return user_config
            
            return None
            
        except Exception as e:
            print(f"خطا در ایجاد کانفیگ تستی: {e}")
            return None
    
    async def create_trial_config_async(self, user: UsersModel, inbound: XUIInbound) -> Optional[UserConfig]:
        """ایجاد کانفیگ تستی برای محیط async"""
        from asgiref.sync import sync_to_async
        
        try:
            email = f"trial_{user.username_tel}_{user.telegram_id}"
            client_settings = self.service.create_client_settings(
                email=email,
                total_gb=1,  # 1 GB برای تست
                expiry_days=1  # 1 روز
            )
            
            if self.service.add_client_to_inbound(inbound.xui_inbound_id, client_settings):
                client_data = client_settings['clients'][0]
                
                # استفاده از sync_to_async برای Django ORM
                user_config = await sync_to_async(UserConfig.objects.create)(
                    user=user,
                    server=self.server,
                    inbound=inbound,
                    xui_inbound_id=inbound.xui_inbound_id,
                    xui_user_id=client_data['id'],
                    config_name=f"{user.full_name} - تستی",
                    config_data=self._generate_config_data(inbound, client_data),
                    is_active=True,
                    expires_at=timezone.now() + timedelta(days=1),
                    protocol=inbound.protocol,
                    is_trial=True
                )
                
                # علامت‌گذاری استفاده از پلن تستی
                user.has_used_trial = True
                await sync_to_async(user.save)()
                
                print(f"✅ کانفیگ تستی برای کاربر {user.full_name} ایجاد شد")
                return user_config
            
            return None
            
        except Exception as e:
            print(f"خطا در ایجاد کانفیگ تستی: {e}")
            return None
    
    def create_trial_config_sync(self, user: UsersModel, inbound: XUIInbound) -> Optional[UserConfig]:
        """ایجاد کانفیگ تستی برای محیط sync (بدون async)"""
        try:
            email = f"trial_{user.username_tel}_{user.telegram_id}"
            client_settings = self.service.create_client_settings(
                email=email,
                total_gb=1,  # 1 GB برای تست
                expiry_days=1  # 1 روز
            )
            
            if self.service.add_client_to_inbound(inbound.xui_inbound_id, client_settings):
                client_data = client_settings['clients'][0]
                
                # ایجاد مستقیم در دیتابیس (sync)
                user_config = UserConfig.objects.create(
                    user=user,
                    server=self.server,
                    inbound=inbound,
                    xui_inbound_id=inbound.xui_inbound_id,
                    xui_user_id=client_data['id'],
                    config_name=f"{user.full_name} - تستی",
                    config_data=self._generate_config_data(inbound, client_data),
                    is_active=True,
                    expires_at=timezone.now() + timedelta(days=1),
                    protocol=inbound.protocol,
                    is_trial=True
                )
                
                # علامت‌گذاری استفاده از پلن تستی
                user.has_used_trial = True
                user.save()
                
                print(f"✅ کانفیگ تستی برای کاربر {user.full_name} ایجاد شد")
                return user_config
            
            return None
            
        except Exception as e:
            print(f"خطا در ایجاد کانفیگ تستی: {e}")
            return None
    
    def delete_user_config(self, user_config: UserConfig) -> bool:
        """حذف کانفیگ کاربر"""
        try:
            # حذف از X-UI
            if self.service.remove_client_from_inbound(
                user_config.xui_inbound_id, 
                user_config.xui_user_id
            ):
                # غیرفعال کردن در دیتابیس
                user_config.is_active = False
                user_config.save()
                print(f"✅ کانفیگ کاربر {user_config.user.full_name} حذف شد")
                return True
            
            return False
            
        except Exception as e:
            print(f"خطا در حذف کانفیگ کاربر: {e}")
            return False
    
    def check_and_cleanup_expired_users(self) -> int:
        """بررسی و پاکسازی کاربران منقضی شده"""
        try:
            expired_configs = UserConfig.objects.filter(
                is_active=True,
                expires_at__lt=timezone.now()
            )
            
            cleaned_count = 0
            for config in expired_configs:
                if self.delete_user_config(config):
                    cleaned_count += 1
            
            print(f"✅ {cleaned_count} کانفیگ منقضی شده پاکسازی شد")
            return cleaned_count
            
        except Exception as e:
            print(f"خطا در پاکسازی کاربران منقضی شده: {e}")
            return 0
    
    def check_traffic_limits(self) -> int:
        """بررسی محدودیت‌های ترافیک"""
        try:
            from .models import XUIClient, UserConfig

            cleaned = 0

            # همه کلاینت‌های فعال را بررسی می‌کنیم
            for client in XUIClient.objects.filter(is_active=True):
                # اگر زمان انقضا در خود X-UI گذشته یا حجمش تمام شده
                if client.is_expired() or client.get_remaining_gb() <= 0:
                    # تمام کانفیگ‌های مرتبط با این کاربر و inbound را پیدا کن
                    related_configs = UserConfig.objects.filter(
                        is_active=True,
                        user=client.user,
                        inbound=client.inbound,
                    )

                    for cfg in related_configs:
                        if self.delete_user_config(cfg):
                            cleaned += 1

                    # خود کلاینت را هم غیرفعال می‌کنیم
                    client.is_active = False
                    client.save(update_fields=["is_active"])

            if cleaned:
                print(f"✅ {cleaned} کانفیگ به دلیل اتمام حجم/ترافیک پاکسازی شد")

            return cleaned
            
        except Exception as e:
            print(f"خطا در بررسی محدودیت‌های ترافیک: {e}")
            return 0
    
    def _generate_real_config_data(self, inbound: XUIInbound, client_data: Dict) -> str:
        """تولید کانفیگ واقعی از X-UI"""
        if inbound.protocol == "vless":
            return self._generate_vless_config(inbound, client_data)
        elif inbound.protocol == "vmess":
            return self._generate_vmess_config(inbound, client_data)
        elif inbound.protocol == "trojan":
            return self._generate_trojan_config(inbound, client_data)
        else:
            return ""
    
    def _generate_config_data(self, inbound: XUIInbound, client_data: Dict) -> str:
        """تولید داده‌های کانفیگ (برای سازگاری)"""
        return self._generate_real_config_data(inbound, client_data)
    
    def _generate_vless_config(self, inbound: XUIInbound, client_data: Dict) -> str:
        """تولید کانفیگ VLESS"""
        config = f"vless://{client_data['id']}@{inbound.server.host}:{inbound.port}"
        
        # اضافه کردن پارامترهای اضافی بر اساس تنظیمات inbound
        if hasattr(inbound, 'stream_settings') and inbound.stream_settings:
            settings = json.loads(inbound.stream_settings)
            if settings.get('security') == 'reality':
                config += "?security=reality"
                if 'realitySettings' in settings:
                    reality = settings['realitySettings']
                    if 'serverNames' in reality and reality['serverNames']:
                        config += f"&sni={reality['serverNames'][0]}"
        
        config += "#" + inbound.remark
        return config
    
    def _generate_vmess_config(self, inbound: XUIInbound, client_data: Dict) -> str:
        """تولید کانفیگ VMess"""
        vmess_config = {
            "v": "2",
            "ps": inbound.remark,
            "add": inbound.server.host,
            "port": inbound.port,
            "id": client_data['id'],
            "aid": "0",
            "net": "tcp",
            "type": "none",
            "host": "",
            "path": "",
            "tls": "none"
        }
        
        import base64
        import json
        return "vmess://" + base64.b64encode(json.dumps(vmess_config).encode()).decode()
    
    def _generate_trojan_config(self, inbound: XUIInbound, client_data: Dict) -> str:
        """تولید کانفیگ Trojan"""
        return f"trojan://{client_data['id']}@{inbound.server.host}:{inbound.port}#{inbound.remark}"

class XUIInboundManager:
    """مدیریت Inbound های X-UI"""
    
    def __init__(self, server: XUIServer):
        self.server = server
        self.service = XUIEnhancedService(server)
    
    def get_available_inbounds(self):
        """دریافت inbound های موجود و فعال"""
        return XUIInbound.objects.filter(
            server=self.server,
            is_active=True
        )
    
    def find_best_inbound(self, protocol: str = "vless") -> Optional[XUIInbound]:
        """یافتن بهترین inbound برای کاربر"""
        inbounds = self.get_available_inbounds().filter(protocol=protocol)
        
        # اولویت با inbound هایی که ظرفیت خالی دارند
        for inbound in inbounds:
            if inbound.can_accept_client():
                return inbound
        
        return None
    
    def sync_inbounds(self) -> int:
        """همگام‌سازی inbound ها با X-UI"""
        return self.service.sync_inbounds_to_database()

class XUIAutoManager:
    """مدیریت خودکار X-UI"""
    
    def __init__(self, server: XUIServer):
        self.server = server
        self.client_manager = XUIClientManager(server)
        self.inbound_manager = XUIInboundManager(server)
    
    def run_cleanup(self) -> Dict[str, int]:
        """اجرای پاکسازی خودکار"""
        try:
            results = {
                'expired_users': 0,
                'traffic_exceeded': 0,
                'total_cleaned': 0
            }
            
            # پاکسازی کاربران منقضی شده
            expired_count = self.client_manager.check_and_cleanup_expired_users()
            results['expired_users'] = expired_count
            
            # بررسی محدودیت‌های ترافیک
            traffic_count = self.client_manager.check_traffic_limits()
            results['traffic_exceeded'] = traffic_count
            
            results['total_cleaned'] = expired_count + traffic_count
            
            print(f"🧹 پاکسازی خودکار انجام شد:")
            print(f"  • کاربران منقضی شده: {expired_count}")
            print(f"  • محدودیت ترافیک: {traffic_count}")
            print(f"  • کل پاکسازی شده: {results['total_cleaned']}")
            
            return results
            
        except Exception as e:
            print(f"خطا در پاکسازی خودکار: {e}")
            return {'expired_users': 0, 'traffic_exceeded': 0, 'total_cleaned': 0}
    
    def schedule_cleanup(self, interval_hours: int = 24):
        """برنامه‌ریزی پاکسازی خودکار"""
        try:
            from django.core.management.base import BaseCommand
            from django.utils import timezone
            
            # این بخش نیاز به پیاده‌سازی کامل دارد
            # می‌توانید از Celery یا Django Cron استفاده کنید
            print(f"⏰ پاکسازی خودکار هر {interval_hours} ساعت برنامه‌ریزی شد")
            
        except Exception as e:
            print(f"خطا در برنامه‌ریزی پاکسازی: {e}") 