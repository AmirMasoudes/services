# راهنمای کامل API های X-UI سنایی

این راهنما شامل تمام اطلاعات مورد نیاز برای اتصال و استفاده از API های X-UI سنایی است.

## 📋 فهرست مطالب

1. [معرفی API های سنایی](#معرفی-api-های-سنایی)
2. [نصب و راه‌اندازی](#نصب-و-راه‌اندازی)
3. [متدهای اصلی](#متدهای-اصلی)
4. [نمونه کد](#نمونه-کد)
5. [خطاها و عیب‌یابی](#خطاها-و-عیب‌یابی)

## معرفی API های سنایی

X-UI سنایی یک نسخه بهبود یافته از X-UI است که API های جدید و بهتری ارائه می‌دهد. این API ها شامل:

### 🔐 احراز هویت

- `/login` - ورود به سیستم
- استفاده از توکن Bearer برای احراز هویت

### 📊 مدیریت Inbound ها

- `GET /panel/api/inbounds/list` - دریافت لیست inbound ها
- `GET /panel/api/inbounds/get/:id` - دریافت inbound با ID
- `POST /panel/api/inbounds/add` - ایجاد inbound جدید
- `POST /panel/api/inbounds/update/:id` - به‌روزرسانی inbound
- `POST /panel/api/inbounds/del/:id` - حذف inbound

### 👤 مدیریت کلاینت‌ها

- `POST /panel/api/inbounds/addClient` - اضافه کردن کلاینت
- `POST /panel/api/inbounds/:id/delClient/:clientId` - حذف کلاینت
- `POST /panel/api/inbounds/updateClient/:clientId` - به‌روزرسانی کلاینت
- `GET /panel/api/inbounds/getClientTraffics/:email` - دریافت ترافیک کلاینت
- `POST /panel/api/inbounds/:id/resetClientTraffic/:email` - ریست ترافیک کلاینت

### 📈 آمار و گزارش‌گیری

- `POST /panel/api/inbounds/onlines` - دریافت کلاینت‌های آنلاین
- `GET /panel/api/inbounds/createbackup` - ایجاد backup

## نصب و راه‌اندازی

### 1. نصب X-UI سنایی

```bash
# نصب X-UI سنایی
bash <(curl -Ls https://raw.githubusercontent.com/MHSanaei/3x-ui/master/install.sh)
```

### 2. تنظیمات اولیه

پس از نصب، X-UI را در آدرس `http://your-server-ip:2053` در دسترس خواهد بود.

### 3. تنظیم در Django

در پنل ادمین Django، یک سرور X-UI جدید اضافه کنید:

- **نام سرور**: نام دلخواه
- **آدرس سرور**: IP سرور شما
- **پورت**: 2053 (پیش‌فرض)
- **نام کاربری**: admin
- **رمز عبور**: رمز عبور تنظیم شده
- **مسیر وب**: `/MsxZ4xuIy5xLfQtsSC/` (پیش‌فرض)

## متدهای اصلی

### 🔐 ورود به سیستم

```python
from xui_servers.sanaei_api import SanaeiXUIAPI

# ایجاد اتصال
api = SanaeiXUIAPI(
    host="your-server-ip",
    port=2053,
    username="admin",
    password="your-password"
)

# ورود
if api.login():
    print("✅ ورود موفق")
else:
    print("❌ خطا در ورود")
```

### 📋 دریافت لیست Inbound ها

```python
# دریافت لیست inbound ها
inbounds = api.get_inbounds()
for inbound in inbounds:
    print(f"ID: {inbound['id']}, نام: {inbound['remark']}, پورت: {inbound['port']}")
```

### 🔧 ایجاد Inbound جدید

```python
# ایجاد inbound جدید
inbound_id = api.create_inbound(
    protocol="vless",
    port=443,
    remark="کانفیگ جدید"
)

if inbound_id:
    print(f"✅ Inbound ایجاد شد: {inbound_id}")
```

### 👤 اضافه کردن کلاینت

```python
# داده‌های کلاینت
client_data = {
    "id": "uuid-here",
    "email": "user@example.com",
    "flow": "",
    "limitIp": 0,
    "totalGB": 5120,  # 5 GB
    "expiryTime": 0,
    "enable": True,
    "tgId": "",
    "subId": ""
}

# اضافه کردن کلاینت
if api.add_client_to_inbound(inbound_id, client_data):
    print("✅ کلاینت اضافه شد")
```

### 🔧 تولید کانفیگ

```python
from xui_servers.sanaei_api import SanaeiConfigGenerator

# تولید کانفیگ VLess
config = SanaeiConfigGenerator.generate_vless_config(
    server_host="your-server-ip",
    port=443,
    uuid="user-uuid",
    user_name="نام کاربر"
)

print(f"کانفیگ: {config}")
```

## نمونه کد کامل

### ایجاد کانفیگ برای کاربر

```python
def create_user_config(user, server, plan):
    """ایجاد کانفیگ برای کاربر"""

    # ایجاد اتصال
    api = SanaeiXUIAPI(
        host=server.host,
        port=server.port,
        username=server.username,
        password=server.password,
        web_base_path=server.web_base_path
    )

    # ورود
    if not api.login():
        return None, "خطا در ورود به سرور"

    # ایجاد inbound
    inbound_id = api.create_inbound(
        protocol="vless",
        remark=f"کاربر {user.get_display_name()}"
    )

    if not inbound_id:
        return None, "خطا در ایجاد inbound"

    # ایجاد کلاینت
    client_data = {
        "id": str(uuid.uuid4()),
        "email": f"user_{user.id}@vpn.com",
        "flow": "",
        "limitIp": 0,
        "totalGB": plan.traffic_gb * 1024,  # تبدیل به MB
        "expiryTime": 0,
        "enable": True,
        "tgId": str(user.telegram_id) if user.telegram_id else "",
        "subId": ""
    }

    if not api.add_client_to_inbound(inbound_id, client_data):
        return None, "خطا در ایجاد کلاینت"

    # تولید کانفیگ
    config = SanaeiConfigGenerator.generate_vless_config(
        server.host,
        443,
        client_data['id'],
        user.get_display_name()
    )

    return config, "کانفیگ با موفقیت ایجاد شد"
```

### مدیریت ترافیک

```python
def update_user_traffic(user_email, new_traffic_gb):
    """به‌روزرسانی ترافیک کاربر"""

    api = SanaeiXUIAPI(host, port, username, password)

    if not api.login():
        return False

    # دریافت inbound کاربر
    inbounds = api.get_inbounds()
    user_inbound = None

    for inbound in inbounds:
        for client in inbound['settings']['clients']:
            if client['email'] == user_email:
                user_inbound = inbound
                break
        if user_inbound:
            break

    if not user_inbound:
        return False

    # به‌روزرسانی ترافیک
    return api.update_client_traffic(
        user_inbound['id'],
        user_email,
        new_traffic_gb * 1024
    )
```

### دریافت آمار

```python
def get_server_stats():
    """دریافت آمار سرور"""

    api = SanaeiXUIAPI(host, port, username, password)

    if not api.login():
        return None

    # دریافت inbound ها
    inbounds = api.get_inbounds()

    # دریافت کلاینت‌های آنلاین
    online_clients = api.get_online_clients()

    # محاسبه آمار
    stats = {
        "total_inbounds": len(inbounds),
        "total_clients": sum(len(inbound['settings']['clients']) for inbound in inbounds),
        "online_clients": len(online_clients),
        "total_traffic_up": sum(inbound.get('up', 0) for inbound in inbounds),
        "total_traffic_down": sum(inbound.get('down', 0) for inbound in inbounds)
    }

    return stats
```

## خطاها و عیب‌یابی

### خطاهای رایج

1. **خطا در ورود**

   - بررسی صحت نام کاربری و رمز عبور
   - بررسی دسترسی به سرور
   - بررسی فعال بودن X-UI

2. **خطا در ایجاد inbound**

   - بررسی دسترسی‌های سرور
   - بررسی عدم تداخل پورت
   - بررسی تنظیمات فایروال

3. **خطا در اضافه کردن کلاینت**
   - بررسی صحت داده‌های کلاینت
   - بررسی عدم تکراری بودن email
   - بررسی محدودیت‌های سرور

### تست اتصال

برای تست اتصال به X-UI سنایی:

```bash
python test_sanaei_connection.py
```

این اسکریپت تمام قابلیت‌های API را تست می‌کند.

### لاگ‌ها

برای بررسی لاگ‌های X-UI:

```bash
# لاگ‌های X-UI
tail -f /var/log/x-ui.log

# لاگ‌های xray
tail -f /var/log/xray.log
```

## 🔧 تنظیمات پیشرفته

### SSL Certificate

برای تنظیم SSL:

```bash
# ورود به X-UI
x-ui

# انتخاب SSL Certificate Management
# انتخاب Get SSL
```

### Fail2Ban

برای فعال کردن Fail2Ban:

```bash
# ورود به X-UI
x-ui

# انتخاب IP Limit Management
# نصب Fail2Ban
```

### Reverse Proxy

برای تنظیم Nginx:

```nginx
location / {
    proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
    proxy_set_header X-Forwarded-Proto $scheme;
    proxy_set_header Host $http_host;
    proxy_set_header X-Real-IP $remote_addr;
    proxy_redirect off;
    proxy_pass http://127.0.0.1:2053;
}
```

## 📞 پشتیبانی

برای سوالات و مشکلات:

1. **مستندات رسمی**: [GitHub Wiki](https://github.com/MHSanaei/3x-ui/wiki)
2. **Issues**: [GitHub Issues](https://github.com/MHSanaei/3x-ui/issues)
3. **Discussions**: [GitHub Discussions](https://github.com/MHSanaei/3x-ui/discussions)

---

**نکته**: این راهنما برای نسخه 3x-ui سنایی تهیه شده است. برای نسخه‌های دیگر ممکن است تفاوت‌هایی وجود داشته باشد.
