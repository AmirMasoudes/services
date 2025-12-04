# Implementation Guide - Complete System Fix

## Overview

This guide provides step-by-step instructions for implementing all fixes identified in the audit.

---

## Phase 1: Database Migrations

### Step 1.1: Apply Model Improvements

1. **Update XUIServer Model:**
   - Copy fields from `xui_servers/models_improved.py` to `xui_servers/models.py`
   - Add: `use_ssl`, `server_type`, `api_token`, health check fields, sync fields
   - Add indexes

2. **Update XUIInbound Model:**
   - Add: `stream_settings`, `sniffing_settings`, `last_sync_at`
   - Add indexes and unique_together constraint

3. **Update XUIClient Model:**
   - Add: `last_usage_sync`, `sync_retry_count`, `last_sync_error`
   - Add indexes

4. **Update UserConfig Model:**
   - Add: `status`, `subscription_url`, `last_sync_at`, `sync_required`, retry fields
   - Add indexes

5. **Update OrderUserModel:**
   - Change `plans` from OneToOne to ForeignKey
   - Add: `status`, `order_number`, payment fields, dates
   - Add indexes

6. **Update PayMentModel:**
   - Add: `status`, `amount`, dates, approver fields
   - Add indexes

7. **Create AuditLog Model:**
   - New model for tracking changes
   - Add to `xui_servers/models.py`

### Step 1.2: Create Migrations

```bash
python manage.py makemigrations
python manage.py migrate
```

---

## Phase 2: S-UI Integration

### Step 2.1: Install S-UI Client

The S-UI client is already created in `xui_servers/sui_client.py`. 

**Features:**
- Retry logic with exponential backoff
- Idempotency support
- Health checks
- Proper error handling
- Token-based authentication

### Step 2.2: Use S-UI Managers

Import and use in your services:

```python
from xui_servers.sui_managers import SUIInboundManager, SUIProvisionService

# For inbound management
manager = SUIInboundManager(server)
inbounds = manager.get_available_inbounds()
best_inbound = manager.find_best_inbound('vless')

# For provisioning
provision_service = SUIProvisionService(server)
trial_config = provision_service.provision_trial_config(user)
paid_config = provision_service.provision_paid_config(user, plan)
```

### Step 2.3: Update Settings

Add S-UI settings to `config/settings.py`:

```python
SUI_HOST = os.environ.get('SUI_HOST', 'localhost')
SUI_PORT = int(os.environ.get('SUI_PORT', '2095'))
SUI_USE_SSL = os.environ.get('SUI_USE_SSL', 'False').lower() == 'true'
SUI_BASE_PATH = os.environ.get('SUI_BASE_PATH', '/app')
SUI_API_TOKEN = os.environ.get('SUI_API_TOKEN', '')
```

---

## Phase 3: X-UI API Improvements

### Step 3.1: Add Retry Logic

The retry decorator is available. Apply to X-UI API methods:

```python
from xui_servers.sui_client import retry_with_backoff

@retry_with_backoff(max_retries=3, backoff_factor=1.0)
def your_xui_method(self):
    # Your code
    pass
```

### Step 3.2: Add Idempotency

Use idempotency keys for all create operations:

```python
idempotency_key = f"user_{user_id}_{plan_id}_{int(time.time())}"
```

### Step 3.3: Implement Usage Sync

Create Celery task for periodic sync:

```python
# In xui_servers/tasks.py
@shared_task
def sync_client_usage():
    """Sync client usage from X-UI/S-UI"""
    for config in UserConfig.objects.filter(is_active=True, sync_required=True):
        # Sync usage
        pass
```

---

## Phase 4: Admin Bot Fixes

### Step 4.1: Create Utility Modules

Create `bot/utils.py`:

```python
# Permission decorator
def admin_required(func):
    @wraps(func)
    async def wrapper(update, context):
        if not await is_admin(update.effective_user.id):
            await update.message.reply_text("❌ دسترسی ادمین ندارید!")
            return
        return await func(update, context)
    return wrapper

# Error handler
async def error_handler(update, context):
    logger.error(f"Error: {context.error}")
    # Send error message
```

### Step 4.2: Fix Async Issues

Ensure all handlers are properly async:

```python
async def command_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        # Use sync_to_async for Django ORM
        result = await sync_to_async(Model.objects.get)(id=1)
    except Exception as e:
        logger.error(f"Error: {e}")
        await update.message.reply_text("❌ خطا رخ داد")
```

### Step 4.3: Add Input Validation

Create validation functions:

```python
def validate_server_data(data):
    """Validate server creation data"""
    errors = []
    if not data.get('host'):
        errors.append("Host is required")
    if not data.get('port') or not (1 <= data['port'] <= 65535):
        errors.append("Invalid port")
    return errors
```

### Step 4.4: Implement State Machine

For multi-step inputs:

```python
USER_STATES = {}

async def start_add_server(update, context):
    USER_STATES[update.effective_user.id] = 'waiting_server_name'
    await update.message.reply_text("نام سرور را وارد کنید:")

async def handle_server_name(update, context):
    if USER_STATES.get(update.effective_user.id) == 'waiting_server_name':
        context.user_data['server_name'] = update.message.text
        USER_STATES[update.effective_user.id] = 'waiting_server_host'
        await update.message.reply_text("آدرس سرور را وارد کنید:")
```

---

## Phase 5: User Bot Fixes

### Step 5.1: Fix Start Command

```python
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_data = update.effective_user
    telegram_id = user_data.id
    
    try:
        # Get or create user
        user, created = await sync_to_async(
            lambda: UsersModel.objects.get_or_create(
                telegram_id=telegram_id,
                defaults={
                    'id_tel': str(telegram_id),
                    'username_tel': user_data.username or '',
                    'full_name': user_data.full_name or 'کاربر',
                    'username': user_data.username or ''
                }
            )
        )()
        
        if created:
            message = "✅ ثبت‌نام با موفقیت انجام شد!"
        else:
            # Update existing user
            user.username_tel = user_data.username or ''
            user.full_name = user_data.full_name or 'کاربر'
            await sync_to_async(user.save)()
            message = "👋 خوش آمدید!"
        
        await update.message.reply_text(
            message,
            reply_markup=main_keyboard
        )
        
    except Exception as e:
        logger.error(f"Error in start: {e}")
        await update.message.reply_text("❌ خطا در ثبت‌نام. لطفا دوباره تلاش کنید.")
```

### Step 5.2: Implement Subscription Links

```python
async def get_subscription_link(user_config: UserConfig) -> str:
    """Generate subscription link"""
    if user_config.subscription_url:
        return user_config.subscription_url
    
    # Generate link
    from django.conf import settings
    base_url = getattr(settings, 'SERVER_DOMAIN', 'localhost')
    link = f"https://{base_url}/api/subscription/{user_config.xui_user_id}"
    
    # Save to database
    user_config.subscription_url = link
    await sync_to_async(user_config.save)()
    
    return link
```

### Step 5.3: Add Usage Display

```python
async def show_usage(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = await sync_to_async(UsersModel.objects.get)(
        telegram_id=update.effective_user.id
    )
    
    configs = await sync_to_async(list)(
        user.xui_configs.filter(is_active=True)
    )
    
    if not configs:
        await update.message.reply_text("❌ هیچ کانفیگ فعالی ندارید")
        return
    
    message = "📊 **استفاده شما:**\n\n"
    for config in configs:
        # Sync usage first
        await sync_usage(config)
        
        # Get usage stats
        # Display usage
        message += f"• {config.config_name}\n"
        # Add usage details
    
    await update.message.reply_text(message, parse_mode='Markdown')
```

### Step 5.4: Implement Renewal Flow

```python
async def renew_config(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Renew expired config"""
    user = await sync_to_async(UsersModel.objects.get)(
        telegram_id=update.effective_user.id
    )
    
    expired_configs = await sync_to_async(list)(
        user.xui_configs.filter(
            is_active=True,
            expires_at__lt=timezone.now()
        )
    )
    
    if not expired_configs:
        await update.message.reply_text("❌ هیچ کانفیگ منقضی شده‌ای ندارید")
        return
    
    # Show renewal options
    keyboard = []
    for config in expired_configs:
        keyboard.append([
            InlineKeyboardButton(
                f"🔄 تمدید {config.config_name}",
                callback_data=f"renew_{config.id}"
            )
        ])
    
    await update.message.reply_text(
        "🔄 کانفیگ‌های منقضی شده:",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )
```

---

## Phase 6: Security Fixes

### Step 6.1: Environment Variables

1. Create `.env` file from template
2. Move all secrets to environment variables
3. Never commit `.env` to git
4. Add `.env` to `.gitignore`

### Step 6.2: Input Validation

Add validation to all user inputs:

```python
from django.core.validators import validate_email, URLValidator

def validate_input(data, field_type):
    """Validate user input"""
    if field_type == 'email':
        validate_email(data)
    elif field_type == 'url':
        URLValidator()(data)
    # Add more validations
```

### Step 6.3: Sanitize Logs

```python
def sanitize_log_data(data):
    """Remove sensitive data from logs"""
    sensitive_keys = ['password', 'token', 'api_key', 'secret']
    sanitized = data.copy()
    for key in sensitive_keys:
        if key in sanitized:
            sanitized[key] = '***REDACTED***'
    return sanitized
```

---

## Phase 7: Testing

### Step 7.1: Unit Tests

Create tests for:
- S-UI client
- Provision service
- Bot handlers
- Models

### Step 7.2: Integration Tests

Test:
- Full provisioning flow
- Bot command flows
- API integrations

---

## Phase 8: Deployment

### Step 8.1: Update Requirements

Ensure all dependencies are in `requirements.txt`

### Step 8.2: Environment Setup

1. Set environment variables
2. Run migrations
3. Create superuser
4. Start services

### Step 8.3: Monitoring

Set up:
- Logging
- Error tracking
- Health checks
- Usage monitoring

---

## Quick Reference

### Key Files Created:
- `xui_servers/sui_client.py` - S-UI API client
- `xui_servers/sui_managers.py` - S-UI managers
- `xui_servers/models_improved.py` - Improved models
- `order/models_improved.py` - Improved order models
- `AUDIT_REPORT.md` - Full audit report
- `SECURITY_FIXES.md` - Security fixes
- `IMPLEMENTATION_GUIDE.md` - This file

### Next Steps:
1. Review audit report
2. Apply database migrations
3. Update bot handlers
4. Test thoroughly
5. Deploy

---

## Support

For issues or questions, refer to:
- `AUDIT_REPORT.md` for problem details
- `SECURITY_FIXES.md` for security improvements
- Code comments for implementation details

