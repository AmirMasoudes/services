# Quick Fix Reference - Critical Issues

## 🚨 Critical Issues That Need Immediate Attention

### 1. Security - Move Secrets to Environment (URGENT)

**Current Problem:**
- Bot tokens in `config.env`
- Passwords hardcoded
- File may be committed to git

**Quick Fix:**
```bash
# 1. Create .env file (copy from template)
cp .env.example .env

# 2. Add to .gitignore
echo ".env" >> .gitignore
echo "config.env" >> .gitignore

# 3. Update settings.py to use environment
# Already done in settings.py, just need to set env vars
```

---

### 2. Database - Fix Order Model Relationship (HIGH PRIORITY)

**Problem:** `OrderUserModel.plans` is OneToOne, should be ForeignKey

**Quick Fix:**
```python
# In order/models.py, change:
plans = models.OneToOneField(...)  # WRONG
# To:
plan = models.ForeignKey(ConfingPlansModel, ...)  # CORRECT
```

Then run:
```bash
python manage.py makemigrations
python manage.py migrate
```

---

### 3. S-UI Integration - Use New Client (MEDIUM PRIORITY)

**Problem:** S-UI integration missing

**Quick Fix:**
```python
# Import the new client
from xui_servers.sui_client import SUIClient
from xui_servers.sui_managers import SUIProvisionService

# Use it
client = SUIClient(
    host='your-host',
    port=2095,
    api_token='your-token'
)

# Provision configs
service = SUIProvisionService(server)
config = service.provision_trial_config(user)
```

---

### 4. Admin Bot - Add Error Handling (MEDIUM PRIORITY)

**Problem:** No error handling in bot handlers

**Quick Fix Pattern:**
```python
async def your_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        # Your code here
        pass
    except Exception as e:
        logger.error(f"Error in handler: {e}", exc_info=True)
        await update.message.reply_text("❌ خطا رخ داد. لطفا دوباره تلاش کنید.")
```

---

### 5. User Bot - Fix Start Command (MEDIUM PRIORITY)

**Problem:** Start command may fail silently

**Quick Fix:**
```python
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        user_data = update.effective_user
        user, created = await sync_to_async(
            lambda: UsersModel.objects.get_or_create(
                telegram_id=user_data.id,
                defaults={
                    'id_tel': str(user_data.id),
                    'username_tel': user_data.username or '',
                    'full_name': user_data.full_name or 'کاربر',
                }
            )
        )()
        
        if created:
            message = "✅ ثبت‌نام موفق!"
        else:
            message = "👋 خوش آمدید!"
        
        await update.message.reply_text(message, reply_markup=main_keyboard)
        
    except Exception as e:
        logger.error(f"Start error: {e}", exc_info=True)
        await update.message.reply_text("❌ خطا در ثبت‌نام")
```

---

## Priority Order

1. **URGENT:** Security - Move secrets to environment
2. **HIGH:** Database - Fix Order relationship
3. **MEDIUM:** Add error handling to bots
4. **MEDIUM:** Use S-UI integration
5. **LOW:** Apply all other improvements

---

## Testing Checklist

After applying fixes:

- [ ] Environment variables set correctly
- [ ] Database migrations applied
- [ ] Admin bot commands work
- [ ] User bot start command works
- [ ] S-UI integration tested
- [ ] No secrets in code/config files
- [ ] Error handling works
- [ ] Logs don't contain sensitive data

---

## Need Help?

- See `IMPLEMENTATION_GUIDE.md` for detailed steps
- See `AUDIT_REPORT.md` for problem details
- See `FIXES_SUMMARY.md` for complete overview

