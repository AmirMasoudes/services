"""
API Manager برای X-UI سنایی
این فایل شامل تمام متدهای مورد نیاز برای اتصال به X-UI سنایی است
"""

import requests
import json
import uuid
import random
import string
import base64
from datetime import datetime, timedelta
from django.utils import timezone
from typing import Optional, Dict, List, Any

class SanaeiXUIAPI:
    """کلاس اصلی برای اتصال به X-UI سنایی"""
    
    def __init__(self, host: str, port: int, username: str, password: str, web_base_path: str = "/MsxZ4xuIy5xLfQtsSC/", use_ssl: bool = True):
        self.host = host
        self.port = port
        self.username = username
        self.password = password
        self.web_base_path = web_base_path.rstrip('/')
        self.use_ssl = use_ssl
        
        # ساخت URL پایه با پشتیبانی از HTTPS
        protocol = "https" if use_ssl else "http"
        self.base_url = f"{protocol}://{host}:{port}{web_base_path}"
        
        # تنظیم session
        self.session = requests.Session()
        self.session.headers.update({
            'Content-Type': 'application/json',
            'User-Agent': 'Django-XUI-Bot/3.0'
        })
        
        # تنظیم SSL verification
        self.session.verify = False  # برای X-UI معمولاً self-signed certificate دارد
        
        self._token = None
        self._logged_in = False
    
    def login(self) -> bool:
        """ورود به X-UI"""
        try:
            login_data = {
                "username": self.username,
                "password": self.password
            }
            
            response = self.session.post(
                f"{self.base_url}/login",
                json=login_data,
                timeout=30,
                verify=False
            )
            
            if response.status_code == 200:
                try:
                    data = response.json()
                    if data.get('success'):
                        # ذخیره توکن
                        self._token = data.get('token') or data.get('obj', {}).get('token')
                        if self._token:
                            self.session.headers.update({'Authorization': f'Bearer {self._token}'})
                        self._logged_in = True
                        print(f"✅ لاگین موفق به سرور {self.host}")
                        return True
                except:
                    # اگر JSON نامعتبر بود، احتمالاً لاگین موفق بوده
                    self._logged_in = True
                    print(f"✅ لاگین موفق (بدون JSON معتبر)")
                    return True
            
            print(f"❌ خطا در لاگین: {response.status_code} - {response.text}")
            return False
            
        except Exception as e:
            print(f"خطا در ورود به X-UI: {e}")
            return False
    
    def ensure_login(self) -> bool:
        """اطمینان از لاگین بودن"""
        if not self._logged_in:
            return self.login()
        return True
    
    def get_inbounds(self) -> List[Dict[str, Any]]:
        """دریافت لیست inbound ها"""
        try:
            if not self.ensure_login():
                return []
            
            # endpoint صحیح که کار می‌کند
            endpoints_to_try = [
                "/xui/API/inbounds/list",
                "/inbounds/list",
                "/panel/api/inbounds/list", 
                "/inbounds",
                "/api/inbounds"
            ]
            
            response = None
            for endpoint in endpoints_to_try:
                try:
                    response = self.session.get(
                        f"{self.base_url}{endpoint}",
                        timeout=30,
                        verify=False
                    )
                    if response.status_code == 200 and response.text.strip():
                        break
                except:
                    continue
            
            if response and response.status_code == 200:
                try:
                    data = response.json()
                    if data.get('success'):
                        return data.get('obj', [])
                    else:
                        print(f"❌ API response not successful: {data}")
                        return []
                except ValueError as e:
                    print(f"❌ JSON parse error: {e}, response: {response.text[:200]}")
                    return []
            
            status_code = response.status_code if response else "No response"
            print(f"❌ خطا در دریافت inbound ها: {status_code}")
            return []
            
        except Exception as e:
            print(f"خطا در دریافت inbound ها: {e}")
            return []
    
    def get_inbound_by_id(self, inbound_id: int) -> Optional[Dict[str, Any]]:
        """دریافت inbound با ID"""
        try:
            if not self.ensure_login():
                return None
            
            response = self.session.get(
                f"{self.base_url}/panel/api/inbounds/get/{inbound_id}",
                timeout=30,
                verify=False
            )
            
            if response.status_code == 200:
                data = response.json()
                if data.get('success'):
                    return data.get('obj')
            
            return None
            
        except Exception as e:
            print(f"خطا در دریافت inbound {inbound_id}: {e}")
            return None
    
    def create_inbound(self, protocol: str = "vless", port: Optional[int] = None, remark: str = "Auto Created") -> Optional[int]:
        """ایجاد inbound جدید"""
        try:
            if not self.ensure_login():
                return None
            
            # تولید پورت تصادفی اگر مشخص نشده
            if port is None:
                port = random.randint(10000, 65000)
            
            # ساخت inbound جدید
            inbound_data = {
                "up": 0,
                "down": 0,
                "total": 0,
                "remark": remark,
                "enable": True,
                "expiryTime": 0,
                "listen": "",
                "port": port,
                "protocol": protocol,
                "settings": {
                    "clients": [],
                    "decryption": "none",
                    "fallbacks": []
                },
                "streamSettings": {
                    "network": "tcp",
                    "security": "none",
                    "tcpSettings": {
                        "header": {
                            "type": "none"
                        }
                    }
                },
                "sniffing": {
                    "enabled": True,
                    "destOverride": ["http", "tls"]
                }
            }
            
            response = self.session.post(
                f"{self.base_url}/panel/api/inbounds/add",
                json=inbound_data,
                timeout=30,
                verify=False
            )
            
            if response.status_code == 200:
                data = response.json()
                if data.get('success'):
                    inbound_id = data.get('obj', {}).get('id')
                    print(f"✅ Inbound جدید ایجاد شد: {inbound_id}")
                    return inbound_id
            
            print(f"❌ خطا در ایجاد inbound: {response.status_code}")
            return None
            
        except Exception as e:
            print(f"خطا در ایجاد inbound: {e}")
            return None
    
    def create_client_data(self, username: str, uuid: str = None, limit_ip: int = 0, total_gb_mb: int = 0, expiry_days: int = 0) -> Dict[str, Any]:
        """ایجاد client data با format صحیح
        
        Args:
            username (str): نام کاربری که به عنوان email و UUID استفاده می‌شود
            uuid (str, optional): UUID دستی (اگر نخواهید از username استفاده کنید)
            limit_ip (int): محدودیت IP (پیش‌فرض: 0 = بدون محدودیت)
            total_gb_mb (int): محدودیت حجم به مگابایت (پیش‌فرض: 0 = بدون محدودیت)
            expiry_days (int): روزهای انقضا (پیش‌فرض: 0 = بدون محدودیت)
        
        Returns:
            Dict: client data آماده برای ارسال به X-UI
        """
        import uuid as uuid_module
        from datetime import datetime, timedelta
        
        # اگر UUID مشخص نشده، از username استفاده کن
        if not uuid:
            uuid = username
            
        # محاسبه زمان انقضا
        expiry_time = 0
        if expiry_days > 0:
            expiry_date = datetime.now() + timedelta(days=expiry_days)
            expiry_time = int(expiry_date.timestamp() * 1000)  # میلی‌ثانیه
            
        client_data = {
            "clients": [{
                "id": uuid,
                "flow": "",
                "email": username,  # نام کاربری به عنوان email
                "limitIp": limit_ip,
                "totalGB": total_gb_mb * 1024 * 1024,  # تبدیل MB به byte
                "expiryTime": expiry_time,
                "enable": True,
                "tgId": "",
                "subId": "",
                "comment": f"User: {username}, Limit: {total_gb_mb}MB, Days: {expiry_days}",
                "reset": 0
            }]
        }
        return client_data
    
    def add_client_to_inbound(self, inbound_id: int, client_data: Dict[str, Any]) -> bool:
        """اضافه کردن کلاینت به inbound"""
        try:
            if not self.ensure_login():
                return False
            
            # استفاده از API جدید برای اضافه کردن کلاینت
            # تنظیم payload مطابق با format مورد نیاز X-UI
            payload = {
                "id": str(inbound_id),
                "settings": json.dumps(client_data)
            }
            
            response = self.session.post(
                f"{self.base_url}/panel/inbound/addClient",
                data=payload,  # استفاده از data بجای json
                timeout=30,
                verify=False
            )
            
            if response.status_code == 200:
                data = response.json()
                if data.get('success'):
                    print(f"✅ کلاینت {client_data.get('clients', [{}])[0].get('email')} اضافه شد")
                    return True
            
            print(f"❌ خطا در اضافه کردن کلاینت: {response.status_code} - {response.text}")
            return False
            
        except Exception as e:
            print(f"خطا در اضافه کردن کلاینت: {e}")
            return False
    
    def add_client(self, inbound_id: int, username: str, uuid: str = None, limit_ip: int = 0, total_gb_mb: int = 0, expiry_days: int = 0) -> bool:
        """تابع آسان برای اضافه کردن کلاینت
        
        Args:
            inbound_id (int): شناسه inbound
            username (str): نام کاربری (به عنوان email و UUID استفاده می‌شود)
            uuid (str, optional): UUID دستی
            limit_ip (int): محدودیت IP
            total_gb_mb (int): محدودیت حجم به مگابایت
            expiry_days (int): روزهای انقضا
            
        Returns:
            bool: موفقیت عملیات
            
        مثال:
            api.add_client(2, "user123", total_gb_mb=1024, expiry_days=30)
        """
        client_data = self.create_client_data(username, uuid, limit_ip, total_gb_mb, expiry_days)
        return self.add_client_to_inbound(inbound_id, client_data)
    
    def create_sample_clients(self, inbound_id: int) -> bool:
        """ایجاد نمونه کلاینت‌ها برای تست"""
        print("🔧 ایجاد نمونه کلاینت‌ها...")
        
        # نمونه 1: کلاینت با محدودیت حجم
        success1 = self.add_client(
            inbound_id=inbound_id,
            username="user_1gb_30days", 
            total_gb_mb=1024,  # 1 گیگابایت
            expiry_days=30,    # 30 روز
            limit_ip=1         # 1 IP
        )
        
        # نمونه 2: کلاینت با محدودیت زمان
        success2 = self.add_client(
            inbound_id=inbound_id,
            username="user_7days", 
            total_gb_mb=0,     # بدون محدودیت حجم
            expiry_days=7,     # 7 روز
            limit_ip=2         # 2 IP
        )
        
        # نمونه 3: کلاینت بدون محدودیت
        success3 = self.add_client(
            inbound_id=inbound_id,
            username="user_unlimited", 
            total_gb_mb=0,     # بدون محدودیت حجم
            expiry_days=0,     # بدون محدودیت زمان
            limit_ip=0         # بدون محدودیت IP
        )
        
        results = [success1, success2, success3]
        successful = sum(results)
        print(f"✅ {successful}/3 کلاینت نمونه ایجاد شد")
        
        return all(results)
    
    def remove_client_from_inbound(self, inbound_id: int, email: str) -> bool:
        """حذف کلاینت از inbound"""
        try:
            if not self.ensure_login():
                return False
            
            # دریافت inbound فعلی
            inbound = self.get_inbound_by_id(inbound_id)
            if not inbound:
                return False
            
            # حذف کلاینت از لیست
            clients = inbound['settings']['clients']
            inbound['settings']['clients'] = [
                client for client in clients if client.get('email') != email
            ]
            
            # به‌روزرسانی inbound
            response = self.session.post(
                f"{self.base_url}/panel/api/inbounds/update/{inbound_id}",
                json=inbound,
                timeout=30,
                verify=False
            )
            
            if response.status_code == 200:
                data = response.json()
                if data.get('success'):
                    print(f"✅ کلاینت {email} حذف شد")
                    return True
            
            print(f"❌ خطا در حذف کلاینت: {response.status_code}")
            return False
            
        except Exception as e:
            print(f"خطا در حذف کلاینت: {e}")
            return False
    
    def update_client_traffic(self, inbound_id: int, email: str, total_gb: int) -> bool:
        """به‌روزرسانی ترافیک کلاینت"""
        try:
            if not self.ensure_login():
                return False
            
            # دریافت inbound فعلی
            inbound = self.get_inbound_by_id(inbound_id)
            if not inbound:
                return False
            
            # به‌روزرسانی ترافیک کلاینت
            clients = inbound['settings']['clients']
            for client in clients:
                if client.get('email') == email:
                    client['totalGB'] = total_gb
                    break
            
            # به‌روزرسانی inbound
            response = self.session.post(
                f"{self.base_url}/panel/api/inbounds/update/{inbound_id}",
                json=inbound,
                timeout=30,
                verify=False
            )
            
            if response.status_code == 200:
                data = response.json()
                if data.get('success'):
                    print(f"✅ ترافیک کلاینت {email} به‌روزرسانی شد")
                    return True
            
            print(f"❌ خطا در به‌روزرسانی ترافیک: {response.status_code}")
            return False
            
        except Exception as e:
            print(f"خطا در به‌روزرسانی ترافیک: {e}")
            return False
    
    def get_client_traffic(self, email: str) -> Optional[Dict[str, Any]]:
        """دریافت ترافیک کلاینت"""
        try:
            if not self.ensure_login():
                return None
            
            response = self.session.get(
                f"{self.base_url}/panel/api/inbounds/getClientTraffics/{email}",
                timeout=30,
                verify=False
            )
            
            if response.status_code == 200:
                data = response.json()
                if data.get('success'):
                    return data.get('obj')
            
            return None
            
        except Exception as e:
            print(f"خطا در دریافت ترافیک کلاینت {email}: {e}")
            return None
    
    def reset_client_traffic(self, inbound_id: int, email: str) -> bool:
        """ریست کردن ترافیک کلاینت"""
        try:
            if not self.ensure_login():
                return False
            
            response = self.session.post(
                f"{self.base_url}/panel/api/inbounds/{inbound_id}/resetClientTraffic/{email}",
                timeout=30,
                verify=False
            )
            
            if response.status_code == 200:
                data = response.json()
                if data.get('success'):
                    print(f"✅ ترافیک کلاینت {email} ریست شد")
                    return True
            
            print(f"❌ خطا در ریست ترافیک: {response.status_code}")
            return False
            
        except Exception as e:
            print(f"خطا در ریست ترافیک: {e}")
            return False
    
    def get_online_clients(self) -> List[str]:
        """دریافت کلاینت‌های آنلاین"""
        try:
            if not self.ensure_login():
                return []
            
            response = self.session.post(
                f"{self.base_url}/panel/api/inbounds/onlines",
                timeout=30,
                verify=False
            )
            
            if response.status_code == 200:
                data = response.json()
                if data.get('success'):
                    return data.get('obj', [])
            
            return []
            
        except Exception as e:
            print(f"خطا در دریافت کلاینت‌های آنلاین: {e}")
            return []
    
    def create_backup(self) -> Optional[str]:
        """ایجاد backup"""
        try:
            if not self.ensure_login():
                return None
            
            response = self.session.get(
                f"{self.base_url}/panel/api/inbounds/createbackup",
                timeout=30,
                verify=False
            )
            
            if response.status_code == 200:
                data = response.json()
                if data.get('success'):
                    return data.get('obj')
            
            return None
            
        except Exception as e:
            print(f"خطا در ایجاد backup: {e}")
            return None

class SanaeiConfigGenerator:
    """تولیدکننده کانفیگ‌های مختلف برای X-UI سنایی"""
    
    @staticmethod
    def generate_vmess_config(server_host: str, port: int, uuid: str, path: str = "/") -> str:
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
    def generate_vless_config(server_host: str, port: int, uuid: str, user_name: str = "User") -> str:
        """تولید کانفیگ VLess"""
        # انتخاب دامنه فیک تصادفی
        fake_domains = [
            "www.google.com", "www.youtube.com", "www.facebook.com",
            "www.twitter.com", "www.instagram.com", "www.linkedin.com"
        ]
        fake_domain = random.choice(fake_domains)
        
        # انتخاب کلید عمومی تصادفی
        public_keys = [
            "j8x0cIrRkct3vDFT5lYQeO3Zk3Xe2SSZCmxaFCMeiY=",
            "RrxsOOp4cQdwqPPjQOp4cQdwqPPjQOp4cQdwqPPjQ=",
            "YzI0Y2ZiYmYtOGYzNy00NjNhLWIyMTAtMzMzYzY3ZGVkNGFk"
        ]
        public_key = random.choice(public_keys)
        
        # تولید shortId تصادفی
        short_id = ''.join(random.choices(string.hexdigits.lower(), k=8))
        
        # تولید کانفیگ VLess Reality
        config = f"vless://{uuid}@{server_host}:{port}?type=tcp&security=reality&sni={fake_domain}&fp=chrome&pbk={public_key}&sid={short_id}&spx=%2F#{user_name}"
        
        return config
    
    @staticmethod
    def generate_trojan_config(server_host: str, port: int, password: str, user_name: str = "User") -> str:
        """تولید کانفیگ Trojan"""
        return f"trojan://{password}@{server_host}:{port}?security=tls#{user_name}"
    
    @staticmethod
    def generate_shadowsocks_config(server_host: str, port: int, password: str, method: str = "aes-256-gcm", user_name: str = "User") -> str:
        """تولید کانفیگ Shadowsocks"""
        config = {
            "server": server_host,
            "server_port": port,
            "password": password,
            "method": method,
            "plugin": "",
            "plugin_opts": "",
            "remarks": user_name
        }
        
        config_str = json.dumps(config)
        encoded = base64.b64encode(config_str.encode()).decode()
        return f"ss://{encoded}" 