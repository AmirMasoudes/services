# سیستم مدیریت ادمین X-UI

## 🎯 **هدف کلی**

این سیستم شامل دو بخش اصلی است:

1. **پنل ادمین Django** - برای مدیریت Inbound ها و تخصیص کاربران
2. **ربات ادمین تلگرام** - برای مدیریت از طریق تلگرام

---

## 🏗️ **مدل‌های جدید**

### **1. XUIInbound**
```python
class XUIInbound(BaseModel, TimeStampMixin, SoftDeleteModel):
    server = models.ForeignKey(XUIServer, ...)
    xui_inbound_id = models.IntegerField()  # ID در X-UI
    port = models.IntegerField()
    protocol = models.CharField()  # vless, vmess, trojan
    remark = models.CharField()  # نام inbound
    is_active = models.BooleanField()
    max_clients = models.IntegerField()  # حداکثر کلاینت
    current_clients = models.IntegerField()  # کلاینت‌های فعلی
```

### **2. XUIClient**
```python
class XUIClient(BaseModel, TimeStampMixin, SoftDeleteModel):
    inbound = models.ForeignKey(XUIInbound, ...)
    user = models.ForeignKey(UsersModel, ...)
    xui_client_id = models.CharField()  # ID کلاینت در X-UI
    email = models.CharField()
    total_gb = models.BigIntegerField()  # حجم کل
    used_gb = models.BigIntegerField()  # حجم استفاده شده
    expiry_time = models.BigIntegerField()  # زمان انقضا
    limit_ip = models.IntegerField()  # محدودیت IP
    is_active = models.BooleanField()
```

### **3. UserConfig (به‌روزرسانی شده)**
```python
class UserConfig(BaseModel, TimeStampMixin, SoftDeleteModel):
    # فیلدهای موجود...
    inbound = models.ForeignKey(XUIInbound, ...)  # فیلد جدید
```

---

## 🖥️ **پنل ادمین Django**

### **مدیریت سرورها (XUIServerAdmin)**
- نمایش تعداد Inbound ها و کلاینت‌ها
- فیلتر بر اساس وضعیت فعال/غیرفعال
- جستجو بر اساس نام و آدرس

### **مدیریت Inbound ها (XUIInboundAdmin)**
- نمایش اسلات‌های خالی
- Inline نمایش کلاینت‌ها
- اکشن‌های همگام‌سازی با X-UI
- به‌روزرسانی تعداد کلاینت‌ها

### **مدیریت کلاینت‌ها (XUIClientAdmin)**
- نمایش حجم باقی‌مانده
- وضعیت انقضا
- همگام‌سازی با X-UI
- به‌روزرسانی استفاده ترافیک

### **مدیریت کانفیگ‌ها (UserConfigAdmin)**
- تخصیص خودکار به Inbound
- تولید مجدد کانفیگ
- نمایش زمان باقی‌مانده

---

## 🤖 **ربات ادمین تلگرام**

### **دسترسی و امنیت**
- بررسی ID کاربران ادمین
- سیستم لاگین با رمز عبور
- اعتبارسنجی رمز عبور

### **دستورات اصلی**

#### **1. ورود و خروج**
```bash
/login [رمز عبور]  # ورود به سیستم
/logout             # خروج از سیستم
```

#### **2. داشبورد و آمار**
```bash
/dashboard          # داشبورد کلی
/servers            # لیست سرورها
/inbounds           # لیست Inbound ها
/clients            # لیست کلاینت‌ها
/users              # لیست کاربران
```

#### **3. مدیریت**
```bash
/create_inbound [سرور] [پورت] [پروتکل] [نام]
/assign_user [شناسه کاربر] [شناسه Inbound]
/sync_xui           # همگام‌سازی با X-UI
```

### **مثال استفاده**

#### **ایجاد Inbound جدید:**
```bash
/create_inbound سرور1 12345 vless Test Inbound
```

#### **تخصیص کاربر:**
```bash
/assign_user 123456789 1
```

---

## ⚙️ **تنظیمات**

### **1. تنظیمات Django (config/settings.py)**
```python
# تنظیمات ربات ادمین
ADMIN_BOT_TOKEN = os.environ.get('ADMIN_BOT_TOKEN', 'YOUR_ADMIN_BOT_TOKEN')
ADMIN_PASSWORD = os.environ.get('ADMIN_PASSWORD', 'admin123')
ADMIN_USER_IDS = [
    # ID های ادمین تلگرام
    123456789,
    987654321,
]
```

### **2. متغیرهای محیطی**
```bash
export ADMIN_BOT_TOKEN="YOUR_BOT_TOKEN"
export ADMIN_PASSWORD="your_admin_password"
```

---

## 🚀 **نصب و راه‌اندازی**

### **1. ایجاد Migration ها**
```bash
python manage.py makemigrations xui_servers
python manage.py migrate
```

### **2. تنظیم ادمین‌ها**
در فایل `config/settings.py`:
```python
ADMIN_USER_IDS = [
    # ID های واقعی ادمین‌ها
    123456789,  # مثال
]
```

### **3. راه‌اندازی ربات ادمین**
```bash
python start_admin_bot.py
```

### **4. راه‌اندازی به عنوان سرویس**
```bash
# ایجاد فایل سرویس
sudo nano /etc/systemd/system/admin-bot.service

[Unit]
Description=Admin Bot Service
After=network.target

[Service]
Type=simple
User=root
WorkingDirectory=/opt/vpn-service/services
Environment=PATH=/opt/vpn-service/services/venv/bin
ExecStart=/opt/vpn-service/services/venv/bin/python start_admin_bot.py
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target

# فعال‌سازی سرویس
sudo systemctl daemon-reload
sudo systemctl enable admin-bot
sudo systemctl start admin-bot
sudo systemctl status admin-bot
```

---

## 📋 **نحوه استفاده**

### **در پنل ادمین Django:**

1. **مدیریت سرورها:**
   - اضافه کردن سرورهای جدید
   - تنظیم اطلاعات اتصال
   - مشاهده آمار

2. **مدیریت Inbound ها:**
   - ایجاد Inbound جدید
   - تنظیم حداکثر کلاینت
   - همگام‌سازی با X-UI

3. **تخصیص کاربران:**
   - انتخاب کاربر
   - انتخاب Inbound
   - تخصیص خودکار

### **در ربات تلگرام:**

1. **ورود به سیستم:**
   ```
   /login admin123
   ```

2. **مشاهده آمار:**
   ```
   /dashboard
   ```

3. **ایجاد Inbound:**
   ```
   /create_inbound سرور1 12345 vless Test Inbound
   ```

4. **تخصیص کاربر:**
   ```
   /assign_user 123456789 1
   ```

---

## 🔧 **عیب‌یابی**

### **مشکلات رایج:**

1. **ربات پاسخ نمی‌دهد:**
   - بررسی TOKEN
   - بررسی ADMIN_USER_IDS
   - بررسی لاگ‌ها

2. **خطا در همگام‌سازی:**
   - بررسی اتصال به X-UI
   - بررسی اطلاعات سرور
   - بررسی لاگ‌ها

3. **خطا در تخصیص کاربر:**
   - بررسی وجود کاربر
   - بررسی ظرفیت Inbound
   - بررسی اتصال X-UI

### **لاگ‌ها:**
```bash
# لاگ ربات ادمین
sudo journalctl -u admin-bot -f

# لاگ Django
tail -f /var/log/django.log
```

---

## 📊 **ویژگی‌های پیشرفته**

### **1. همگام‌سازی خودکار**
- همگام‌سازی Inbound ها با X-UI
- به‌روزرسانی تعداد کلاینت‌ها
- همگام‌سازی اطلاعات کلاینت‌ها

### **2. مدیریت ظرفیت**
- کنترل حداکثر کلاینت‌ها
- نمایش اسلات‌های خالی
- هشدار ظرفیت پر

### **3. امنیت**
- بررسی دسترسی ادمین
- اعتبارسنجی رمز عبور
- لاگ تمام عملیات

### **4. گزارش‌گیری**
- آمار کلی سیستم
- گزارش استفاده ترافیک
- گزارش انقضاها

---

## 🎯 **نتیجه‌گیری**

این سیستم مدیریت ادمین کامل شامل:

✅ **پنل ادمین Django** برای مدیریت گرافیکی
✅ **ربات تلگرام** برای مدیریت از راه دور
✅ **سیستم امنیتی** با رمز عبور
✅ **همگام‌سازی خودکار** با X-UI
✅ **مدیریت ظرفیت** و تخصیص هوشمند
✅ **گزارش‌گیری** و آمار کامل

برای شروع، تنظیمات را انجام داده و سرویس‌ها را راه‌اندازی کنید. 