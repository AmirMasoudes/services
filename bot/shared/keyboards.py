"""
Shared keyboard definitions for Telegram bots
"""
from telegram import ReplyKeyboardMarkup, InlineKeyboardButton, InlineKeyboardMarkup
from typing import List, Optional


# Main user keyboard
main_keyboard = ReplyKeyboardMarkup([
    ["🎁 پلن تستی", "🛒 خرید پلن"],
    ["📦 پلن‌های من", "ℹ️ اطلاعات من"],
    ["💬 ارتباط با ما", "🆘 پشتیبانی"]
], resize_keyboard=True)


# Admin keyboard
admin_keyboard = ReplyKeyboardMarkup([
    ["📊 داشبورد", "🖥️ سرورها"],
    ["📦 پلن‌ها", "🔗 Inbound ها"],
    ["👤 کلاینت‌ها", "👥 کاربران"],
    ["🧹 پاکسازی", "⏰ منقضی شده"]
], resize_keyboard=True)


# Admin + User keyboard (for admin users)
admin_user_keyboard = ReplyKeyboardMarkup([
    ["🛒 خرید پلن", "📊 پروفایل من"],
    ["📦 پلن‌های من", "⚙️ تنظیمات من"],
    ["🎁 پلن تستی", "📚 راهنما"],
    ["📊 داشبورد", "🖥️ سرورها"],
    ["👥 کاربران", "📦 پلن‌ها"]
], resize_keyboard=True)


def create_inline_keyboard(buttons: List[List[dict]], row_width: int = 2) -> InlineKeyboardMarkup:
    """
    Create inline keyboard from button definitions
    
    Args:
        buttons: List of button rows, each row is a list of dicts with 'text' and 'callback_data'
        row_width: Number of buttons per row
    
    Returns:
        InlineKeyboardMarkup object
    """
    keyboard = []
    for row in buttons:
        keyboard_row = []
        for btn in row:
            if 'url' in btn:
                keyboard_row.append(InlineKeyboardButton(btn['text'], url=btn['url']))
            elif 'callback_data' in btn:
                keyboard_row.append(InlineKeyboardButton(btn['text'], callback_data=btn['callback_data']))
            elif 'switch_inline_query' in btn:
                keyboard_row.append(InlineKeyboardButton(btn['text'], switch_inline_query=btn['switch_inline_query']))
        if keyboard_row:
            keyboard.append(keyboard_row)
    
    return InlineKeyboardMarkup(keyboard)


def create_plan_keyboard(plans: List, prefix: str = "plan") -> InlineKeyboardMarkup:
    """
    Create inline keyboard for plan selection
    
    Args:
        plans: List of plan objects
        prefix: Callback data prefix
    
    Returns:
        InlineKeyboardMarkup with plan buttons
    """
    buttons = []
    for plan in plans:
        buttons.append([{
            'text': f"{plan.name} - {plan.price} {getattr(plan, 'currency', 'تومان')}",
            'callback_data': f"{prefix}_{plan.id}"
        }])
    
    # Add back button
    buttons.append([{'text': "🔙 بازگشت", 'callback_data': 'back_to_main'}])
    
    return create_inline_keyboard(buttons)


def create_pagination_keyboard(
    current_page: int,
    total_pages: int,
    prefix: str = "page",
    back_callback: str = "back_to_main"
) -> InlineKeyboardMarkup:
    """
    Create pagination keyboard
    
    Args:
        current_page: Current page number (1-indexed)
        total_pages: Total number of pages
        prefix: Callback data prefix
        back_callback: Back button callback data
    
    Returns:
        InlineKeyboardMarkup with pagination buttons
    """
    buttons = []
    
    # Navigation buttons
    nav_row = []
    if current_page > 1:
        nav_row.append({'text': "◀️ قبلی", 'callback_data': f"{prefix}_{current_page - 1}"})
    
    nav_row.append({'text': f"صفحه {current_page}/{total_pages}", 'callback_data': 'noop'})
    
    if current_page < total_pages:
        nav_row.append({'text': "▶️ بعدی", 'callback_data': f"{prefix}_{current_page + 1}"})
    
    if nav_row:
        buttons.append(nav_row)
    
    # Back button
    buttons.append([{'text': "🔙 بازگشت", 'callback_data': back_callback}])
    
    return create_inline_keyboard(buttons)

