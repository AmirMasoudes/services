# Enhanced X-UI API Documentation

## 📋 **مدل‌های پیشرفته API برای X-UI**

### **🎯 هدف**

این مدل‌ها برای مدیریت پیشرفته Inbound ها و Client ها در X-UI طراحی شده‌اند و شامل بخش‌های تخصصی برای:

- ایجاد Inbound های جدید
- مدیریت Client ها
- به‌روزرسانی تنظیمات
- حذف و پاکسازی

---

## 🏗️ **مدل‌های جدید**

### **1. XUIInboundCreationRequest**

```python
@dataclass
class XUIInboundCreationRequest:
    port: int                    # پورت Inbound
    protocol: str = "vless"      # پروتکل (vless, vmess, trojan)
    remark: str = ""             # نام Inbound
    up: int = 0                  # آپلود
    down: int = 0                # دانلود
    total: int = 0               # کل
    enable: bool = True          # فعال/غیرفعال
    expiry_time: int = 0         # زمان انقضا
    listen: str = ""             # آدرس گوش دادن
```

**مثال استفاده:**

```python
inbound_request = XUIInboundCreationRequest(
    port=12345,
    protocol="vless",
    remark="Test Inbound",
    enable=True
)
```

### **2. XUIClientCreationRequest**

```python
@dataclass
class XUIClientCreationRequest:
    inbound_id: int              # ID Inbound
    email: str                   # ایمیل Client
    total_gb: int = 0           # حجم کل (GB)
    expiry_time: int = 0        # زمان انقضا
    limit_ip: int = 0           # محدودیت IP
    security: str = "auto"      # نوع امنیت
    enable: bool = True         # فعال/غیرفعال
    tg_id: str = ""            # ID تلگرام
    comment: str = ""           # توضیحات
    reset: int = 0             # تعداد ریست
    flow: str = ""             # نوع جریان
```

**مثال استفاده:**

```python
client_request = XUIClientCreationRequest(
    inbound_id=1,
    email="user@example.com",
    total_gb=10,
    expiry_time=int((datetime.now() + timedelta(days=30)).timestamp() * 1000),
    limit_ip=1
)
```

---

## 🔧 **مدیریت Inbound ها**

### **XUIInboundManager**

#### **1. ایجاد Inbound جدید**

```python
inbound_manager = XUIInboundManager(base_url, session)

inbound_request = XUIInboundCreationRequest(
    port=12345,
    protocol="vless",
    remark="Test Inbound"
)

inbound_id = inbound_manager.create_inbound(inbound_request)
if inbound_id:
    print(f"Inbound ایجاد شد با ID: {inbound_id}")
```

#### **2. دریافت اطلاعات Inbound**

```python
inbound_data = inbound_manager.get_inbound(inbound_id)
if inbound_data:
    print(f"نام: {inbound_data.get('remark')}")
    print(f"پورت: {inbound_data.get('port')}")
    print(f"پروتکل: {inbound_data.get('protocol')}")
```

#### **3. به‌روزرسانی Inbound**

```python
updated_request = XUIInboundCreationRequest(
    port=12345,
    protocol="vless",
    remark="Updated Inbound"
)

success = inbound_manager.update_inbound(inbound_id, updated_request)
```

#### **4. حذف Inbound**

```python
success = inbound_manager.delete_inbound(inbound_id)
```

---

## 👤 **مدیریت Client ها**

### **XUIClientManager**

#### **1. اضافه کردن Client**

```python
client_manager = XUIClientManager(base_url, session)

client_request = XUIClientCreationRequest(
    inbound_id=1,
    email="newuser@example.com",
    total_gb=20,
    expiry_time=int((datetime.now() + timedelta(days=60)).timestamp() * 1000)
)

success = client_manager.add_client(client_request)
```

#### **2. به‌روزرسانی Client**

```python
# به‌روزرسانی حجم ترافیک
updates = {"totalGB": 30}
success = client_manager.update_client(inbound_id, client_id, updates)

# به‌روزرسانی زمان انقضا
updates = {"expiryTime": new_expiry_timestamp}
success = client_manager.update_client(inbound_id, client_id, updates)
```

#### **3. حذف Client**

```python
success = client_manager.delete_client(inbound_id, client_id)
```

---

## 🚀 **سرویس پیشرفته X-UI**

### **XUIEnhancedService**

این سرویس ترکیبی از مدیریت Inbound و Client است و امکانات پیشرفته‌تری ارائه می‌دهد.

#### **1. ایجاد Inbound همراه با Client**

```python
enhanced_service = XUIEnhancedService(base_url, session)

result = enhanced_service.create_inbound_with_client(
    port=12345,
    protocol="vless",
    remark="Test Inbound with Client",
    client_email="user@example.com",
    client_total_gb=15,
    client_expiry_time=int((datetime.now() + timedelta(days=30)).timestamp() * 1000)
)

if result:
    print(f"Inbound ID: {result['inbound_id']}")
    print(f"Client Added: {result['client_added']}")
    print(f"Client ID: {result['client_id']}")
```

#### **2. اضافه کردن Client به Inbound موجود**

```python
success = enhanced_service.add_client_to_inbound(
    inbound_id=1,
    email="newuser@example.com",
    total_gb=10,
    expiry_time=int((datetime.now() + timedelta(days=30)).timestamp() * 1000),
    limit_ip=1
)
```

#### **3. دریافت لیست Client های Inbound**

```python
clients = enhanced_service.get_inbound_clients(inbound_id)
for client in clients:
    print(f"Email: {client.get('email')}")
    print(f"ID: {client.get('id')}")
    print(f"Total GB: {client.get('totalGB')}")
```

#### **4. به‌روزرسانی Client**

```python
# به‌روزرسانی حجم ترافیک
success = enhanced_service.update_client_traffic(inbound_id, client_id, 25)

# به‌روزرسانی زمان انقضا
success = enhanced_service.update_client_expiry(inbound_id, client_id, new_expiry_timestamp)
```

#### **5. حذف Client**

```python
success = enhanced_service.delete_client_from_inbound(inbound_id, client_id)
```

---

## 📊 **مثال‌های کامل**

### **مثال 1: ایجاد سیستم کامل VPN**

```python
import requests
from xui_servers.enhanced_api_models import XUIEnhancedService

# تنظیم session
session = requests.Session()
session.headers.update({
    'Content-Type': 'application/json',
    'User-Agent': 'Django-XUI-Bot/2.0'
})

# لاگین
login_data = {"username": "admin", "password": "password"}
response = session.post("http://server:port/login", json=login_data)

# ایجاد سرویس پیشرفته
enhanced_service = XUIEnhancedService("http://server:port", session)

# ایجاد Inbound با Client
result = enhanced_service.create_inbound_with_client(
    port=12345,
    protocol="vless",
    remark="Premium User Inbound",
    client_email="premium@example.com",
    client_total_gb=50,
    client_expiry_time=int((datetime.now() + timedelta(days=90)).timestamp() * 1000)
)

print(f"سیستم VPN ایجاد شد:")
print(f"- Inbound ID: {result['inbound_id']}")
print(f"- Client ID: {result['client_id']}")
```

### **مثال 2: مدیریت چندین Client**

```python
# اضافه کردن Client های بیشتر
clients = [
    {"email": "user1@example.com", "total_gb": 10},
    {"email": "user2@example.com", "total_gb": 20},
    {"email": "user3@example.com", "total_gb": 15}
]

for client_data in clients:
    success = enhanced_service.add_client_to_inbound(
        inbound_id=result['inbound_id'],
        email=client_data['email'],
        total_gb=client_data['total_gb'],
        expiry_time=int((datetime.now() + timedelta(days=30)).timestamp() * 1000)
    )

    if success:
        print(f"Client {client_data['email']} اضافه شد")
    else:
        print(f"خطا در اضافه کردن Client {client_data['email']}")

# دریافت لیست تمام Client ها
all_clients = enhanced_service.get_inbound_clients(result['inbound_id'])
print(f"تعداد کل Client ها: {len(all_clients)}")
```

### **مثال 3: به‌روزرسانی دسته‌ای**

```python
# به‌روزرسانی حجم ترافیک تمام Client ها
for client in all_clients:
    client_id = client.get('id')
    current_traffic = client.get('totalGB', 0)
    new_traffic = current_traffic + 5  # اضافه کردن 5GB

    success = enhanced_service.update_client_traffic(
        result['inbound_id'],
        client_id,
        new_traffic
    )

    if success:
        print(f"ترافیک Client {client.get('email')} به‌روزرسانی شد")
```

---

## 🔍 **نکات مهم**

### **1. Content-Type**

تمام درخواست‌ها با `Content-Type: application/x-www-form-urlencoded` ارسال می‌شوند.

### **2. JSON Serialization**

فیلدهای `settings`, `streamSettings`, `sniffing`, و `allocate` به صورت JSON string ارسال می‌شوند.

### **3. Error Handling**

تمام متدها شامل مدیریت خطا هستند و پیام‌های مناسب نمایش می‌دهند.

### **4. Session Management**

Session باید قبل از استفاده لاگین شده باشد.

### **5. Timeout**

تمام درخواست‌ها با timeout 10 ثانیه ارسال می‌شوند.

---

## 🧪 **تست کردن**

برای تست مدل‌های پیشرفته:

```bash
python test_enhanced_api_models.py
```

این اسکریپت تمام قابلیت‌های جدید را تست می‌کند.

---

## 📈 **مزایای مدل‌های پیشرفته**

1. **ساختار یافته**: استفاده از dataclass برای type safety
2. **مدولار**: جداسازی مدیریت Inbound و Client
3. **قابل گسترش**: امکان اضافه کردن قابلیت‌های جدید
4. **مستندسازی**: کدهای کاملاً مستند
5. **خطایابی**: پیام‌های خطای دقیق
6. **یکپارچگی**: سازگار با سرویس‌های موجود

---

## 🎯 **نتیجه‌گیری**

مدل‌های پیشرفته API برای X-UI امکانات کاملی برای مدیریت Inbound و Client ارائه می‌دهند و می‌توانند به راحتی در پروژه‌های موجود ادغام شوند.
