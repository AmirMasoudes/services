# راهنمای استارت بات تلگرام - Python 3.14

## ⚠️ مشکل Python 3.14

در Python 3.14، `nest_asyncio` با `httpx` و `httpcore` مشکل دارد. باید از روش دیگری استفاده کنیم.

## ✅ راه‌حل نهایی

### روش 1: استفاده از `run_bot.py` (توصیه می‌شود)

```powershell
.\venv\Scripts\Activate.ps1
python run_bot.py --user
```

### روش 2: استارت مستقیم

```powershell
.\venv\Scripts\Activate.ps1
python bot/user_bot.py
```

## 🔧 تغییرات انجام شده

1. ✅ حذف `nest_asyncio` از `user_bot.py`
2. ✅ استفاده از `asyncio.run()` به جای مدیریت دستی event loop
3. ✅ استفاده از `close_loop=False` در `run_polling()`

## 📝 نکات مهم

- **همیشه venv را فعال کنید** قبل از استارت
- **از `asyncio.run()` استفاده کنید** نه `loop.run_until_complete()`
- **`close_loop=False`** را در `run_polling()` تنظیم کنید

## 🚀 دستورات

```powershell
# فعال‌سازی venv
.\venv\Scripts\Activate.ps1

# استارت ربات کاربر
python run_bot.py --user

# استارت ربات ادمین
python run_bot.py --admin

# یا استارت مستقیم
python bot/user_bot.py
python bot/admin_bot.py
```

## ❌ اگر هنوز مشکل دارید

1. بررسی کنید که Python 3.14 نصب است
2. بررسی کنید که `python-telegram-bot` به‌روز است
3. بررسی کنید که `nest-asyncio` نصب نیست یا استفاده نمی‌شود

