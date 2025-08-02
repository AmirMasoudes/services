# تنظیمات پروتکل‌های VPN
# این فایل شامل تنظیمات پیش‌فرض برای پروتکل‌های مختلف است

# پروتکل پیش‌فرض برای سیستم
DEFAULT_PROTOCOL = "vless"

# دامنه‌های فیک ایرانی برای Reality (تصادفی انتخاب می‌شوند)
FAKE_DOMAINS = [
    # سایت‌های خبری و رسانه‌ای
    "www.aparat.com",
    "www.filimo.com", 
    "www.digikala.com",
    "www.namava.ir",
    "www.varzesh3.com",
    "www.khabaronline.ir",
    "www.tabnak.ir",
    "www.mehrnews.com",
    "www.isna.ir",
    "www.irna.ir",
    "www.farsnews.ir",
    "www.tasnimnews.com",
    "www.yjc.ir",
    "www.entekhab.ir",
    "www.aftabnews.ir",
    "www.parsine.com",
    "www.irinn.ir",
    "www.telewebion.com",
    "www.iribnews.ir",
    "www.irib.ir",
    
    # سایت‌های خرید و فروش
    "www.divar.ir",
    "www.bama.ir",
    "www.sheypoor.com",
    "www.snapp.ir",
    
    # سایت‌های دولتی و رسمی
    "www.iran.ir",
    "www.shaparak.ir",
    "www.mci.ir",
    
    # اپراتورهای موبایل و اینترنت
    "www.irancell.ir",
    "www.rightel.ir",
    "www.shatel.ir",
    "www.parsonline.ir",
    "www.asiatech.ir",
    
    # موتورهای جستجو و پورتال‌ها
    "www.parsijoo.ir",
    "www.parsijoo.com",
    
    # شبکه‌های اجتماعی (که در ایران استفاده می‌شوند)
    "www.telegram.org",
    "www.instagram.com",
    
    # سایت‌های آموزشی و دانشگاهی
    "www.ut.ac.ir",
    "www.sharif.ir",
    "www.aut.ac.ir",
    "www.iust.ac.ir",
    
    # بانک‌ها و موسسات مالی
    "www.mellat.ir",
    "www.parsijoo.ir",
    "www.samanbank.ir",
    "www.ansarbank.ir",
    
    # سایت‌های ورزشی
    "www.varzesh3.com",
    "www.footballitar.ir",
    "www.iranleague.ir",
    
    # سایت‌های مسافرتی و هتل
    "www.iranhotel.com",
    "www.irantravel.com",
    "www.iranair.com",
    
    # سایت‌های پزشکی و سلامت
    "www.tehranhospital.com",
    "www.iranhealth.com",
    "www.medicaliran.com"
]

# کلیدهای عمومی Reality (تصادفی انتخاب می‌شوند)
REALITY_PUBLIC_KEYS = [
    "LqlFK+R6fsSExaVJfrvcnwvJGQu8BQ0e/0RnG+OV7G0=",
    "K8mFJ+Q5erRDwZUIfqubmvuIFPq9APzd/1QmF+NU6Fz=",
    "J7lEI+P4dqQCvYTHeptalutHEOp8zOQc0PhW+MT5Ey=",
    "I6kDH+O3cpPBvXSGdosaKtTGDNo7yNPb0OgV+LS4Dx=",
    "H5jCG+N2boOAvWRFcntZJsSFCMn6xMOa1NfU+KR3Cw=",
    "G4iBF+M1anNAuVQEbmsYIrREBLm5wLNZ0MeT+JQ2Bv=",
    "F3hAE+L0ZmMztUPDalrXHqQDzKl4vKMYzLdS+IP1Au=",
    "E2gAD+KzYlLysTCZkqWGpPCyJk3uJLxYyKcR+HO0zt=",
    "D1fAC+JyXkKxrSBYjpVFoOBxIj2tIKwXxJbQ+GNzys=",
    "C0eAB+JxWjJwqRAXioUEoNAwHi1sHJvWwIaP+FMzxt="
]

# تنظیمات پروتکل‌های مختلف
PROTOCOL_SETTINGS = {
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
        },
        "settings": {
            "clients": [],
            "decryption": "none",
            "fallbacks": []
        }
    },
    "vless": {
        "name": "VLess Reality",
        "description": "پروتکل VLess با Reality",
        "default_port": 443,
        "stream_settings": {
            "network": "tcp",
            "security": "reality",
            "realitySettings": {
                "show": False,
                "dest": "www.aparat.com:443",
                "xver": 0,
                "serverNames": ["www.aparat.com"],
                "privateKey": "YFgo8YQUJmqhu2yXL8rd8D9gDgJ1H1XgfbYqMB6LmoM",
                "shortIds": [""]
            },
            "tcpSettings": {
                "header": {
                    "type": "none"
                }
            }
        },
        "settings": {
            "clients": [],
            "decryption": "none",
            "fallbacks": []
        }
    },
    "trojan": {
        "name": "Trojan",
        "description": "پروتکل Trojan با TLS",
        "default_port": 443,
        "stream_settings": {
            "network": "tcp",
            "security": "tls",
            "tlsSettings": {
                "serverName": "",
                "certificates": [
                    {
                        "certificateFile": "/root/cert.crt",
                        "keyFile": "/root/private.key"
                    }
                ]
            },
            "tcpSettings": {
                "header": {
                    "type": "none"
                }
            }
        },
        "settings": {
            "clients": [],
            "fallbacks": []
        }
    }
}

# تنظیمات پیش‌فرض برای inbound ها
INBOUND_SETTINGS = {
    "sniffing": {
        "enabled": True,
        "destOverride": [
            "http",
            "tls"
        ]
    },
    "enable": True,
    "expiryTime": 0,
    "listen": "",
    "up": [],
    "down": [],
    "total": 0
}

# تنظیمات پیش‌فرض برای کاربران
USER_DEFAULT_SETTINGS = {
    "limitIp": 1,
    "totalGB": 0,  # برای تست نامحدود
    "expiryTime": 0  # زمان انقضا بر حسب میلی‌ثانیه
}

# تنظیمات کانفیگ‌های تولید شده
CONFIG_SETTINGS = {
    "vmess": {
        "version": "2",
        "aid": "0",
        "net": "ws",
        "type": "none",
        "host": "",
        "path": "/",
        "tls": "tls"
    },
    "vless": {
        "type": "tcp",
        "security": "reality",
        "serverName": "",
        "publicKey": "",
        "shortId": "",
        "spiderX": "/"
    },
    "trojan": {
        "security": "tls"
    }
}

# تنظیمات نام‌گذاری inbound ها
INBOUND_NAMING = {
    "prefix": "AutoBot",
    "separator": "-",
    "format": "{prefix}{separator}{protocol}{separator}{port}"
}

# تنظیمات ایمیل کاربران
EMAIL_SETTINGS = {
    "trial_format": "trial_{telegram_id}@vpn.com",
    "paid_format": "paid_{telegram_id}_{plan_id}@vpn.com"
}

# تنظیمات زمان انقضا (30 روز برای پلن‌های پولی)
EXPIRY_SETTINGS = {
    "trial_hours": 24,
    "paid_days": 30
}

# تنظیمات حجم داده (تبدیل MB به GB)
TRAFFIC_SETTINGS = {
    "mb_to_gb_conversion": 1024
}

# تنظیمات پورت‌ها (پورت‌های مختلف برای هر کاربر)
PORT_SETTINGS = {
    "min_port": 10000,
    "max_port": 65000,
    "default_ports": {
        "vmess": 443,
        "vless": 443,
        "trojan": 443
    }
}

# تنظیمات امنیت
SECURITY_SETTINGS = {
    "enable_sniffing": True,
    "dest_override": ["http", "tls"],
    "tls_enabled": True
}

# تنظیمات لاگ
LOGGING_SETTINGS = {
    "enable_logging": True,
    "log_level": "INFO",
    "log_format": "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
}

# تنظیمات اتصال به X-UI
XUI_CONNECTION_SETTINGS = {
    "timeout": 10,
    "retry_attempts": 3,
    "retry_delay": 1
}

# تنظیمات نام‌های کانفیگ (با نام کاربر)
CONFIG_NAMING = {
    "trial_format": "پلن تستی {user_name} ({protocol})",
    "paid_format": "{plan_name} {user_name} ({protocol})"
}

# تنظیمات پیام‌های موفقیت
SUCCESS_MESSAGES = {
    "trial_created": "کانفیگ تستی {protocol} با موفقیت ایجاد شد",
    "paid_created": "کانفیگ پولی {protocol} با موفقیت ایجاد شد",
    "config_deleted": "کانفیگ با موفقیت حذف شد"
}

# تنظیمات پیام‌های خطا
ERROR_MESSAGES = {
    "xui_login_failed": "خطا در ورود به X-UI",
    "inbound_creation_failed": "خطا در ایجاد inbound خودکار",
    "user_creation_failed": "خطا در ایجاد کاربر در X-UI",
    "invalid_protocol": "پروتکل نامعتبر",
    "xui_deletion_failed": "خطا در حذف از X-UI"
} 