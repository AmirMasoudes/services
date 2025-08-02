# 🎉 راهنمای نهایی سیستم Django VPN

## ✅ وضعیت فعلی سیستم

سیستم شما با موفقیت راه‌اندازی شده و تمام اجزاء فعال هستند:

### 🌐 دسترسی‌ها
- **Django Admin**: http://38.54.105.124/admin/
- **X-UI Panel**: http://38.54.105.124:54321/MsxZ4xuIy5xLfQtsSC/
- **Username**: admin
- **Password**: YourSecurePassword123

### 📦 پلن‌های VPN
1. **پلن تستی** - 0 تومان - 1 روز - 1 GB
2. **پلن برنزی** - 50,000 تومان - 30 روز - 10 GB
3. **پلن نقره‌ای** - 80,000 تومان - 30 روز - 25 GB
4. **پلن طلایی** - 120,000 تومان - 30 روز - 50 GB
5. **پلن الماس** - 200,000 تومان - 30 روز - 100 GB

### 🚀 سرویس‌های فعال
- ✅ Django VPN
- ✅ Nginx
- ✅ Redis Server
- ✅ PostgreSQL
- ✅ Admin Bot
- ✅ User Bot

## 🤖 بات‌های تلگرام

### وضعیت فعلی
- ✅ توکن‌های Admin Bot تنظیم شده است
- ✅ توکن‌های User Bot تنظیم شده است
- ✅ سرویس‌های بات restart شده‌اند

### تست بات‌ها
```bash
# بررسی وضعیت بات‌ها
python check_bots_simple.py

# راه‌اندازی دستی بات‌ها (در صورت نیاز)
python start_bots_manual.py

# تست جامع سیستم
python test_complete_system.py
```

## 🔧 مدیریت سیستم

### سرویس‌ها
```bash
# بررسی وضعیت سرویس‌ها
systemctl status django-vpn
systemctl status nginx
systemctl status redis-server
systemctl status postgresql
systemctl status admin-bot
systemctl status user-bot

# Restart سرویس‌ها
systemctl restart django-vpn
systemctl restart admin-bot
systemctl restart user-bot
```

### لاگ‌ها
```bash
# مشاهده لاگ‌های Django
journalctl -u django-vpn -f

# مشاهده لاگ‌های Admin Bot
journalctl -u admin-bot -f

# مشاهده لاگ‌های User Bot
journalctl -u user-bot -f
```

## 📊 تست سیستم

### تست کامل
```bash
python final_test_complete.py
```

### تست جامع
```bash
python test_complete_system.py
```

### تست بات‌ها
```bash
python check_bots_simple.py
```

## 🛠️ عیب‌یابی

### مشکل بات‌ها
1. **بررسی توکن‌ها**:
   ```bash
   python setup_bot_tokens.py
   ```

2. **راه‌اندازی دستی**:
   ```bash
   python start_bots_manual.py
   ```

3. **بررسی لاگ‌ها**:
   ```bash
   journalctl -u admin-bot --no-pager -n 20
   journalctl -u user-bot --no-pager -n 20
   ```

### مشکل X-UI
1. **تست اتصال**:
   ```bash
   python test_xui_connection.py
   ```

2. **تنظیم سرور**:
   ```bash
   python setup_xui_server.py
   ```

### مشکل Django
1. **بررسی مایگریشن‌ها**:
   ```bash
   python manage.py migrate
   ```

2. **بررسی سوپر یوزر**:
   ```bash
   python manage.py createsuperuser
   ```

## 📁 فایل‌های مهم

### اسکریپت‌های تست
- `final_test_complete.py` - تست نهایی کامل
- `test_complete_system.py` - تست جامع سیستم
- `check_bots_simple.py` - بررسی ساده بات‌ها
- `start_bots_manual.py` - راه‌اندازی دستی بات‌ها

### فایل‌های تنظیمات
- `.env` - متغیرهای محیطی
- `config/settings.py` - تنظیمات Django
- `xui_servers/settings.py` - تنظیمات X-UI

### فایل‌های بات
- `bot/admin_boy.py` - Admin Bot
- `bot/user_bot.py` - User Bot

## 🎯 دستورات مفید

### بررسی وضعیت
```bash
# وضعیت تمام سرویس‌ها
systemctl list-units --type=service --state=active | grep -E "(django|nginx|redis|postgresql|admin|user)"

# وضعیت پورت‌ها
ss -tlnp | grep -E "(80|8000|54321|6379|5432)"

# پروسه‌های Python
ps aux | grep python
```

### مدیریت بات‌ها
```bash
# توقف بات‌ها
pkill -f admin_boy.py
pkill -f user_bot.py

# راه‌اندازی مجدد
systemctl restart admin-bot
systemctl restart user-bot
```

### پشتیبان‌گیری
```bash
# پشتیبان‌گیری از دیتابیس
pg_dump configvpn_db > backup_$(date +%Y%m%d_%H%M%S).sql

# پشتیبان‌گیری از فایل‌ها
tar -czf backup_$(date +%Y%m%d_%H%M%S).tar.gz /opt/vpn-service/services/
```

## 🚀 راه‌اندازی مجدد سیستم

در صورت نیاز به راه‌اندازی مجدد کامل:

```bash
# 1. توقف سرویس‌ها
systemctl stop django-vpn admin-bot user-bot

# 2. راه‌اندازی مجدد
systemctl start django-vpn admin-bot user-bot

# 3. بررسی وضعیت
python test_complete_system.py
```

## 📞 پشتیبانی

### لاگ‌های مهم
- Django: `/var/log/django-vpn.log`
- Nginx: `/var/log/nginx/error.log`
- System: `/var/log/syslog`

### اطلاعات سیستم
- سرور: 38.54.105.124
- پورت X-UI: 54321
- مسیر X-UI: /MsxZ4xuIy5xLfQtsSC/

---

## 🎉 سیستم آماده استفاده است!

تمام اجزاء سیستم با موفقیت راه‌اندازی شده‌اند و آماده استفاده هستند.

**ویژگی‌های فعال:**
- ✅ مدیریت کاربران
- ✅ مدیریت پلن‌ها
- ✅ ایجاد خودکار inbound
- ✅ بات‌های تلگرام
- ✅ پنل مدیریت
- ✅ وب سرویس‌ها

**🎯 سیستم شما آماده است!**
