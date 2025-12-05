"""
Admin bot specific keyboards
"""
from telegram import ReplyKeyboardMarkup, InlineKeyboardButton, InlineKeyboardMarkup
from bot.shared.keyboards import admin_keyboard, create_inline_keyboard


def create_server_keyboard(servers) -> InlineKeyboardMarkup:
    """
    Create keyboard for server selection
    
    Args:
        servers: List of server objects
    
    Returns:
        InlineKeyboardMarkup with server buttons
    """
    buttons = []
    for server in servers:
        status = "✅ فعال" if server.is_active else "❌ غیرفعال"
        buttons.append([{
            'text': f"{server.name} - {status}",
            'callback_data': f"server_{server.id}"
        }])
    
    buttons.append([{'text': "🔙 بازگشت", 'callback_data': 'back_to_main'}])
    
    return create_inline_keyboard(buttons)


def create_payment_keyboard(payments) -> InlineKeyboardMarkup:
    """
    Create keyboard for payment management
    
    Args:
        payments: List of payment objects
    
    Returns:
        InlineKeyboardMarkup with payment buttons
    """
    buttons = []
    for payment in payments:
        buttons.append([{
            'text': f"💰 {payment.code_pay} - {payment.amount} تومان",
            'callback_data': f"payment_{payment.id}"
        }])
    
    buttons.append([
        {'text': "✅ تایید همه", 'callback_data': 'approve_all_payments'},
        {'text': "❌ رد همه", 'callback_data': 'reject_all_payments'}
    ])
    buttons.append([{'text': "🔙 بازگشت", 'callback_data': 'back_to_main'}])
    
    return create_inline_keyboard(buttons)


def create_user_management_keyboard() -> InlineKeyboardMarkup:
    """
    Create keyboard for user management
    
    Returns:
        InlineKeyboardMarkup with user management options
    """
    buttons = [
        [{'text': "👥 لیست کاربران", 'callback_data': 'list_users'}],
        [{'text': "➕ افزودن کاربر", 'callback_data': 'add_user'}],
        [{'text': "🔍 جستجوی کاربر", 'callback_data': 'search_user'}],
        [{'text': "🔙 بازگشت", 'callback_data': 'back_to_main'}]
    ]
    
    return create_inline_keyboard(buttons)


def create_server_management_keyboard() -> InlineKeyboardMarkup:
    """
    Create keyboard for server management
    
    Returns:
        InlineKeyboardMarkup with server management options
    """
    buttons = [
        [{'text': "🖥️ لیست سرورها", 'callback_data': 'list_servers'}],
        [{'text': "➕ افزودن سرور", 'callback_data': 'add_server'}],
        [{'text': "🔄 همگام‌سازی", 'callback_data': 'sync_servers'}],
        [{'text': "🔙 بازگشت", 'callback_data': 'back_to_main'}]
    ]
    
    return create_inline_keyboard(buttons)

