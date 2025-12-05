# Bot Architecture Documentation

## Overview

This document describes the modular architecture of the Telegram bots in this project.

## Directory Structure

```
bot/
├── shared/              # Shared utilities for both bots
│   ├── __init__.py
│   ├── keyboards.py     # Shared keyboard definitions
│   ├── decorators.py    # Error handling and permission decorators
│   └── errors.py        # Error classes and handlers
├── user/                # User bot modules
│   ├── __init__.py
│   ├── handlers.py      # Command and message handlers
│   ├── services.py      # Business logic services
│   └── keyboards.py     # User-specific keyboards
├── admin/               # Admin bot modules
│   ├── __init__.py
│   ├── handlers.py      # Admin command handlers
│   ├── services.py      # Admin business logic
│   └── keyboards.py     # Admin-specific keyboards
├── user_bot.py          # Legacy user bot (being migrated)
├── admin_bot.py         # Legacy admin bot (being migrated)
└── README.md            # Bot documentation
```

## Shared Utilities

### `bot/shared/keyboards.py`

Contains shared keyboard definitions:
- `main_keyboard`: Main user keyboard
- `admin_keyboard`: Admin keyboard
- `admin_user_keyboard`: Combined keyboard for admin users
- Helper functions for creating inline keyboards

### `bot/shared/decorators.py`

Contains decorators for error handling and permissions:
- `@error_handler`: Wraps handlers with error handling
- `@admin_required`: Requires admin access
- `@user_required`: Ensures user exists in database
- `is_admin()`: Check if user is admin

### `bot/shared/errors.py`

Contains error classes and handlers:
- `BotError`: Base exception
- `UserNotFoundError`: User not found
- `PermissionDeniedError`: Permission denied
- `ConfigNotFoundError`: Config not found
- `PlanNotFoundError`: Plan not found
- `ServerError`: Server/X-UI error
- `handle_error()`: Error handler function

## User Bot Services

### `bot/user/services.py`

Contains business logic services:
- `UserBotService`: Main service class
  - `get_or_create_user()`: Get or create user
  - `get_user()`: Get user by telegram ID
  - `get_user_stats()`: Get user statistics
  - `get_user_plans()`: Get user's active plans
  - `get_user_configs()`: Get user's active configs
  - `can_get_trial()`: Check if user can get trial
  - `get_available_plans()`: Get all available plans
  - `get_plan()`: Get plan by ID
  - `create_trial_config()`: Create trial config
  - `create_order()`: Create order
  - `create_payment()`: Create payment record

## Migration Strategy

The bots are being gradually migrated from monolithic files to modular structure:

1. **Phase 1** (Current): Create shared utilities and service layers
2. **Phase 2**: Add error handling decorators to existing handlers
3. **Phase 3**: Migrate handlers to separate modules
4. **Phase 4**: Complete migration and remove legacy code

## Usage Examples

### Using Error Handling

```python
from bot.shared.decorators import error_handler, admin_required
from bot.shared.errors import handle_error

@error_handler
async def my_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        # Handler code
        pass
    except Exception as e:
        await handle_error(update, context, e)
```

### Using Services

```python
from bot.user.services import UserBotService

# Get or create user
user, created = await UserBotService.get_or_create_user(telegram_id, user_data)

# Get user stats
stats = await UserBotService.get_user_stats(user)

# Create trial config
config = await UserBotService.create_trial_config(user)
```

### Using Keyboards

```python
from bot.shared.keyboards import main_keyboard, create_inline_keyboard
from bot.user.keyboards import get_user_keyboard, create_plan_selection_keyboard

# Use shared keyboard
await update.message.reply_text("Message", reply_markup=main_keyboard)

# Create custom keyboard
buttons = [[{'text': 'Button', 'callback_data': 'action'}]]
keyboard = create_inline_keyboard(buttons)
```

## Best Practices

1. **Always use error handlers**: Wrap all handlers with `@error_handler`
2. **Use services for business logic**: Don't put business logic in handlers
3. **Use type hints**: Add type hints to all functions
4. **Log errors properly**: Use logger with appropriate levels
5. **Handle async properly**: Use `sync_to_async` for Django ORM calls
6. **Validate input**: Always validate user input before processing

## Future Improvements

1. Complete migration of handlers to separate modules
2. Add comprehensive unit tests
3. Add integration tests for bot flows
4. Implement rate limiting
5. Add monitoring and metrics
6. Implement caching for frequently accessed data

