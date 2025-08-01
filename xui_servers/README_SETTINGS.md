# راهنمای تنظیمات X-UI Bot

## مقدمه
فایل `settings.py` شامل تمام تنظیمات قابل تغییر برای سیستم VPN Bot است. این فایل به شما امکان می‌دهد تا بدون تغییر کد، تنظیمات سیستم را تغییر دهید.

## بخش‌های مختلف تنظیمات

### 1. پروتکل پیش‌فرض
```python
DEFAULT_PROTOCOL = "vmess"
```
پروتکل پیش‌فرض که سیستم از آن استفاده می‌کند. گزینه‌های موجود:
- `"vmess"` - پروتکل VMess
- `"vless"` - پروتکل VLess  
- `"trojan"` - پروتکل Trojan

### 2. تنظیمات پروتکل‌ها (`PROTOCOL_SETTINGS`)
هر پروتکل دارای تنظیمات مخصوص خود است:

#### VMess
```python
"vmess": {
    "name": "VMess",
    "description": "پروتکل VMess با WebSocket",
    "default_port": 443,
    "stream_settings": {
        "network": "ws",
        "security": "none",
        "wsSettings": {
            "acceptProxyProtocol": False,
            "path": "/",
            "headers": {}
        }
    }
}
```

#### VLess
```python
"vless": {
    "name": "VLess", 
    "description": "پروتکل VLess با WebSocket",
    "default_port": 443,
    "stream_settings": {
        "network": "ws",
        "security": "none",
        "wsSettings": {
            "acceptProxyProtocol": False,
            "path": "/",
            "headers": {}
        }
    }
}
```

#### Trojan
```python
"trojan": {
    "name": "Trojan",
    "description": "پروتکل Trojan با TLS",
    "default_port": 443,
    "stream_settings": {
        "network": "tcp",
        "security": "tls",
        "tlsSettings": {
            "serverName": "",  # از سرور X-UI گرفته می‌شود
            "certificates": [
                {
                    "certificateFile": "/root/cert.crt",
                    "keyFile": "/root/private.key"
                }
            ]
        }
    }
}
```

### 3. تنظیمات پورت‌ها (`PORT_SETTINGS`)
```python
PORT_SETTINGS = {
    "min_port": 10000,      # حداقل پورت
    "max_port": 65000,      # حداکثر پورت
    "default_ports": {
        "vmess": 443,
        "vless": 443, 
        "trojan": 443
    }
}
```

### 4. تنظیمات زمان انقضا (`EXPIRY_SETTINGS`)
```python
EXPIRY_SETTINGS = {
    "trial_hours": 24,    # مدت زمان پلن تستی (ساعت)
    "paid_days": 30       # مدت زمان پلن پولی (روز)
}
```

### 5. تنظیمات حجم داده (`TRAFFIC_SETTINGS`)
```python
TRAFFIC_SETTINGS = {
    "mb_to_gb_conversion": 1024  # تبدیل MB به GB
}
```

### 6. تنظیمات نام‌گذاری (`INBOUND_NAMING`)
```python
INBOUND_NAMING = {
    "prefix": "AutoBot",
    "separator": "-", 
    "format": "{prefix}{separator}{protocol}{separator}{port}"
}
```
مثال: `AutoBot-VMESS-443`

### 7. تنظیمات ایمیل (`EMAIL_SETTINGS`)
```python
EMAIL_SETTINGS = {
    "trial_format": "trial_{telegram_id}@vpn.com",
    "paid_format": "paid_{telegram_id}_{plan_id}@vpn.com"
}
```

### 8. تنظیمات نام کانفیگ (`CONFIG_NAMING`)
```python
CONFIG_NAMING = {
    "trial_format": "پلن تستی ({protocol})",
    "paid_format": "{plan_name} ({protocol})"
}
```

### 9. تنظیمات امنیت (`SECURITY_SETTINGS`)
```python
SECURITY_SETTINGS = {
    "enable_sniffing": True,
    "dest_override": ["http", "tls"],
    "tls_enabled": True
}
```

## نحوه تغییر تنظیمات

### تغییر پروتکل پیش‌فرض
```python
DEFAULT_PROTOCOL = "vless"  # تغییر به VLess
```

### تغییر مدت زمان پلن تستی
```python
EXPIRY_SETTINGS = {
    "trial_hours": 48,  # تغییر به 48 ساعت
    "paid_days": 30
}
```

### تغییر پورت‌های پیش‌فرض
```python
PORT_SETTINGS = {
    "min_port": 10000,
    "max_port": 65000,
    "default_ports": {
        "vmess": 8080,    # تغییر پورت VMess
        "vless": 443,
        "trojan": 443
    }
}
```

### تغییر تنظیمات WebSocket
```python
PROTOCOL_SETTINGS["vmess"]["stream_settings"]["wsSettings"]["path"] = "/ws"
```

### تغییر تنظیمات TLS برای Trojan
```python
PROTOCOL_SETTINGS["trojan"]["stream_settings"]["tlsSettings"]["certificates"] = [
    {
        "certificateFile": "/etc/ssl/certs/cert.pem",
        "keyFile": "/etc/ssl/private/key.pem"
    }
]
```

## نکات مهم

1. **پس از تغییر تنظیمات، سرور را restart کنید**
2. **تنظیمات TLS برای Trojan باید با سرور شما مطابقت داشته باشد**
3. **پورت‌های انتخاب شده نباید در سرور استفاده شده باشند**
4. **تنظیمات WebSocket path باید با CDN شما مطابقت داشته باشد**

## مثال‌های کاربردی

### تنظیم برای Cloudflare
```python
PROTOCOL_SETTINGS["vmess"]["stream_settings"]["wsSettings"]["path"] = "/cdn"
PROTOCOL_SETTINGS["vless"]["stream_settings"]["wsSettings"]["path"] = "/cdn"
```

### تنظیم برای Arvan
```python
PROTOCOL_SETTINGS["vmess"]["stream_settings"]["wsSettings"]["path"] = "/arvan"
PROTOCOL_SETTINGS["vless"]["stream_settings"]["wsSettings"]["path"] = "/arvan"
```

### تنظیم پورت‌های مختلف
```python
PORT_SETTINGS["default_ports"]["vmess"] = 8080
PORT_SETTINGS["default_ports"]["vless"] = 8443
PORT_SETTINGS["default_ports"]["trojan"] = 443
```

## عیب‌یابی

### مشکل اتصال
1. پورت‌ها را بررسی کنید
2. تنظیمات TLS را بررسی کنید
3. مسیر WebSocket را بررسی کنید

### مشکل کانفیگ
1. تنظیمات پروتکل را بررسی کنید
2. UUID ها را بررسی کنید
3. آدرس سرور را بررسی کنید

## پشتیبانی
برای سوالات بیشتر، لطفاً با تیم پشتیبانی تماس بگیرید. 