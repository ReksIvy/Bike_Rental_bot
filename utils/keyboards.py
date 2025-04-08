from telegram import InlineKeyboardButton
from utils.user_data import user_languages, translations


def create_keyboard(id: int, type: str):
    """
    Custom function that creates localized buttons for messages

    :params id: User's id to determine their preferred language
    :params type: Custom button preset
    """
    if type == 'lang':
        keyboard = [
            [InlineKeyboardButton("Русский/RU", callback_data='ru')],
            [InlineKeyboardButton("English/EN", callback_data='en')]
        ]
        return keyboard

    lang = translations[user_languages[id]]

    if type == 'greetings':
        keyboard = [
        [InlineKeyboardButton(lang['change_lang_btn'], callback_data='lang')],
        [InlineKeyboardButton(lang['make_order_btn'], callback_data='make_order')],
        [InlineKeyboardButton(lang['faq_btn'], callback_data='faq')],
        ]
    
    elif type == 'return':
        keyboard = [
            [InlineKeyboardButton(lang['return'], callback_data='return')]
        ]
    
    elif type == 'passport_confirm':
        keyboard = [
            [InlineKeyboardButton(lang['passport_confirm_btn'], callback_data='p_confirm')],
            [InlineKeyboardButton(lang['passport_deny_btn'], callback_data='p_deny')]
        ]
    
    elif type == 'pn_whatsapp':
        keyboard = [
            [InlineKeyboardButton(lang['optional_deny'], callback_data='optional_deny')]
        ]
    
    elif type == 'order_info':
        keyboard = [
            [InlineKeyboardButton(lang['o_confirm_btn'], callback_data='confirm_order')],
            [InlineKeyboardButton(lang['o_bike_btn'], callback_data='change_bike')],
            [InlineKeyboardButton(lang['o_rent_period_btn'], callback_data='change_rent_period')],
            [InlineKeyboardButton(lang['o_helmets_btn'], callback_data='change_helmets')],
            [InlineKeyboardButton(lang['o_address_btn'], callback_data='change_address')],
            [InlineKeyboardButton(lang['o_pn_btn'], callback_data='change_pn')],
            [InlineKeyboardButton(lang['o_whatsapp_btn'], callback_data='change_whatsapp')]
        ]

    return keyboard