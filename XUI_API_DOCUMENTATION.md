# X-UI API Documentation

## 📋 **بررسی API های X-UI**

### **1. API ایجاد Inbound:**

```
URL: /panel/inbound/add
Method: POST
Content-Type: application/x-www-form-urlencoded
```

**Payload:**

```json
{
  "up": 0,
  "down": 0,
  "total": 0,
  "remark": "User_123_vless",
  "enable": true,
  "expiryTime": 0,
  "listen": "",
  "port": 10334,
  "protocol": "vless",
  "settings": "{\"clients\":[],\"decryption\":\"none\",\"fallbacks\":[]}",
  "streamSettings": "{\"network\":\"tcp\",\"security\":\"none\",\"tcpSettings\":{\"header\":{\"type\":\"none\"}}}",
  "sniffing": "{\"enabled\":false,\"destOverride\":[\"http\",\"tls\",\"quic\",\"fakedns\"]}",
  "allocate": "{\"strategy\":\"always\",\"refresh\":5,\"concurrency\":3}"
}
```

### **2. API اضافه کردن Client:**

```
URL: /panel/inbound/addClient
Method: POST
Content-Type: application/x-www-form-urlencoded
```

**Payload:**

```json
{
  "id": 1,
  "settings": "{\"clients\":[{\"id\":\"16eb52bb-8820-4b61-b72e-22afa1b3edbf\",\"security\":\"auto\",\"email\":\"ut42taox\",\"limitIp\":0,\"totalGB\":0,\"expiryTime\":0,\"enable\":true,\"tgId\":\"\",\"subId\":\"3t2whfa85uzpfnus\",\"comment\":\"\",\"reset\":0}]}"
}
```

## 🏗️ **مدل‌های جدید API**

### **1. XUIClient:**

```python
@dataclass
class XUIClient:
    id: str                    # UUID کلاینت
    email: str                 # ایمیل کلاینت
    security: str = "auto"     # نوع امنیت
    limit_ip: int = 0         # محدودیت IP
    total_gb: int = 0         # حجم کل (GB)
    expiry_time: int = 0      # زمان انقضا (timestamp)
    enable: bool = True       # فعال/غیرفعال
    tg_id: str = ""          # ID تلگرام
    sub_id: str = ""         # ID اشتراک
    comment: str = ""         # توضیحات
    reset: int = 0           # تعداد ریست
    flow: str = ""           # نوع جریان
```

### **2. XUIInbound:**

```python
@dataclass
class XUIInbound:
    up: int = 0              # آپلود
    down: int = 0            # دانلود
    total: int = 0           # کل
    remark: str = ""         # نام
    enable: bool = True      # فعال/غیرفعال
    expiry_time: int = 0     # زمان انقضا
    listen: str = ""         # آدرس گوش دادن
    port: int = 0           # پورت
    protocol: str = "vless"  # پروتکل
    settings: XUIInboundSettings
    stream_settings: XUIStreamSettings
    sniffing: XUISniffing
    allocate: XUIAllocate
```

### **3. XUIAPIBuilder:**

```python
class XUIAPIBuilder:
    @staticmethod
    def create_inbound_payload(port, protocol, remark, client=None)
    @staticmethod
    def create_client_payload(inbound_id, client)
    @staticmethod
    def create_client(email, total_gb=0, expiry_time=0, limit_ip=0)
```

### **4. XUIAPIClient:**

```python
class XUIAPIClient:
    def create_inbound(inbound: XUIInbound) -> Optional[int]
    def add_client(inbound_id: int, client: XUIClient) -> bool
    def update_inbound(inbound_id: int, inbound: XUIInbound) -> bool
```

## 🔧 **نحوه استفاده**

### **1. ایجاد Inbound جدید:**

```python
from xui_servers.api_models import XUIAPIBuilder, XUIAPIClient

# ایجاد Inbound
inbound = XUIAPIBuilder.create_inbound_payload(
    port=12345,
    protocol="vless",
    remark="Test Inbound"
)

# ارسال به API
api_client = XUIAPIClient(base_url, session)
inbound_id = api_client.create_inbound(inbound)
```

### **2. اضافه کردن Client:**

```python
# ایجاد Client
client = XUIAPIBuilder.create_client(
    email="user@example.com",
    total_gb=10,
    expiry_time=int((datetime.now() + timedelta(days=30)).timestamp() * 1000)
)

# اضافه کردن به Inbound
success = api_client.add_client(inbound_id, client)
```

### **3. استفاده در XUIService:**

```python
from xui_servers.services import XUIService

# ایجاد سرویس
xui_service = XUIService(server)
xui_service.login()

# ایجاد Inbound برای کاربر
inbound_id = xui_service.create_user_specific_inbound(
    user_id=123,
    protocol="vless"
)

# ایجاد کاربر
user_data = {
    "id": str(uuid.uuid4()),
    "email": "user@example.com",
    "totalGB": 10,
    "expiryTime": int((datetime.now() + timedelta(days=30)).timestamp() * 1000)
}

success = xui_service.create_user(inbound_id, user_data)
```

## 📊 **ساختار داده‌ها**

### **Settings (تنظیمات Inbound):**

```json
{
  "clients": [
    {
      "id": "uuid-string",
      "security": "auto",
      "email": "user@example.com",
      "limitIp": 0,
      "totalGB": 10,
      "expiryTime": 1754234741,
      "enable": true,
      "tgId": "",
      "subId": "random-string",
      "comment": "",
      "reset": 0
    }
  ],
  "decryption": "none",
  "fallbacks": []
}
```

### **StreamSettings (تنظیمات Stream):**

```json
{
  "network": "tcp",
  "security": "none",
  "externalProxy": [],
  "tcpSettings": {
    "acceptProxyProtocol": false,
    "header": {
      "type": "none"
    }
  }
}
```

### **Sniffing (تنظیمات Sniffing):**

```json
{
  "enabled": false,
  "destOverride": ["http", "tls", "quic", "fakedns"],
  "metadataOnly": false,
  "routeOnly": false
}
```

### **Allocate (تنظیمات Allocate):**

```json
{
  "strategy": "always",
  "refresh": 5,
  "concurrency": 3
}
```

## 🚀 **مزایای مدل‌های جدید**

### **1. Type Safety:**

- استفاده از dataclass برای type checking
- جلوگیری از خطاهای runtime

### **2. Validation:**

- بررسی خودکار فیلدهای اجباری
- تنظیم مقادیر پیش‌فرض

### **3. Maintainability:**

- کد تمیزتر و قابل نگهداری
- جداسازی منطق API از business logic

### **4. Extensibility:**

- اضافه کردن آسان فیلدهای جدید
- پشتیبانی از پروتکل‌های مختلف

## 🔍 **تست و Debug**

### **1. تست API Builder:**

```bash
python test_new_api_models.py
```

### **2. تست کامل سیستم:**

```bash
python test_xui_simple.py
```

### **3. Debug API Calls:**

```python
# فعال کردن debug mode
import logging
logging.basicConfig(level=logging.DEBUG)
```

## 📝 **نکات مهم**

### **1. Content-Type:**

- تمام API ها از `application/x-www-form-urlencoded` استفاده می‌کنند
- نه `application/json`

### **2. JSON Fields:**

- فیلدهای `settings`, `streamSettings`, `sniffing`, `allocate` باید JSON string باشند
- نه object

### **3. Error Handling:**

- همیشه response status code را بررسی کنید
- JSON parsing errors را handle کنید

### **4. Session Management:**

- از session برای حفظ cookies استفاده کنید
- login قبل از هر API call

## 🎯 **نتیجه‌گیری**

مدل‌های جدید API X-UI مزایای زیر را فراهم می‌کنند:

1. **سازگاری کامل** با API های X-UI
2. **Type Safety** و validation
3. **کد تمیزتر** و قابل نگهداری
4. **قابلیت توسعه** آسان
5. **Debug آسان‌تر**

این مدل‌ها جایگزین مناسبی برای کدهای قدیمی هستند و مشکلات JSON parsing را حل می‌کنند.
