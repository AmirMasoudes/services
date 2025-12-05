"""
User bot specific keyboards
"""
from telegram import ReplyKeyboardMarkup, InlineKeyboardButton, InlineKeyboardMarkup
from bot.shared.keyboards import main_keyboard, create_inline_keyboard


def get_user_keyboard(is_admin: bool = False) -> ReplyKeyboardMarkup:
    """
    Get appropriate keyboard for user
    
    Args:
        is_admin: Whether user is admin
    
    Returns:
        ReplyKeyboardMarkup instance
    """
    if is_admin:
        return ReplyKeyboardMarkup([
            ["🛒 خرید پلن", "📊 پروفایل من"],
            ["📦 پلن‌های من", "⚙️ تنظیمات من"],
            ["🎁 پلن تستی", "📚 راهنما"],
            ["📊 داشبورد", "🖥️ سرورها"],
            ["👥 کاربران", "📦 پلن‌ها"]
        ], resize_keyboard=True)
    else:
        return main_keyboard


def create_plan_selection_keyboard(plans) -> InlineKeyboardMarkup:
    """
    Create keyboard for plan selection
    
    Args:
        plans: List of plan objects
    
    Returns:
        InlineKeyboardMarkup with plan buttons
    """
    buttons = []
    for plan in plans:
        buttons.append([{
            'text': f"{plan.name} - {plan.price} تومان",
            'callback_data': f"select_plan_{plan.id}"
        }])
    
    buttons.append([{'text': "🔙 بازگشت", 'callback_data': 'back_to_main'}])
    
    return create_inline_keyboard(buttons)


def create_config_keyboard(configs) -> InlineKeyboardMarkup:
    """
    Create keyboard for config selection
    
    Args:
        configs: List of config objects
    
    Returns:
        InlineKeyboardMarkup with config buttons
    """
    buttons = []
    for config in configs:
        status = "✅ فعال" if not config.is_expired() else "❌ منقضی"
        buttons.append([{
            'text': f"{config.name or f'Config {config.id}'} - {status}",
            'callback_data': f"view_config_{config.id}"
        }])
    
    buttons.append([{'text': "🔙 بازگشت", 'callback_data': 'back_to_main'}])
    
    return create_inline_keyboard(buttons)


def create_help_keyboard() -> InlineKeyboardMarkup:
    """
    Create help menu keyboard
    
    Returns:
        InlineKeyboardMarkup with help options
    """
    buttons = [
        [{'text': "📱 راهنمای اپلیکیشن", 'callback_data': 'help_app'}],
        [{'text': "⚙️ راهنمای کانفیگ", 'callback_data': 'help_config'}],
        [{'text': "❓ سوالات متداول", 'callback_data': 'help_faq'}],
        [{'text': "💬 تماس با ما", 'callback_data': 'help_contact'}],
        [{'text': "🔙 بازگشت", 'callback_data': 'back_to_main'}]
    ]
    
    return create_inline_keyboard(buttons)

