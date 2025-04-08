from telegram import Update, InlineKeyboardMarkup
from telegram.ext import CallbackContext
from telegram.constants import ChatAction
from utils.user_data import user_languages, translations
from utils.globals import *
from greetings import greetings
from order import order
from utils.keyboards import create_keyboard
from order_complete import order_complete
import os

async def button_handler(update: Update, context: CallbackContext):
    """
    Custom bot button handler
    """
    query = update.callback_query
    user_id = query.from_user.id
    await query.answer()

    data = query.data

    if data == 'en':
        user_languages[query.from_user.id] = 'en'
        await greetings(update, context)
        return GREETINGS
    elif data == 'ru':
        user_languages[query.from_user.id] = 'ru'
        await greetings(update, context)
        return GREETINGS
    elif data == 'lang':
        await query.edit_message_text('Добро пожаловать в Bike Rental Group. С помощью данного бота вы сможете легко забронировать байк.' +
        'Перед началом, пожалуйста, выберите предпочитаемый язык\n\n' +
        'Welcome to Bike Rental Group. This bot will help you rent a bike. Before we start, please choose your preferred language',
        reply_markup=InlineKeyboardMarkup(create_keyboard(user_id, 'lang')))
        return LANGUAGE
    elif data == 'make_order':
        context.user_data['state'] = 'BIKE_LIST'
        await order(update, context)
        return BIKE_SELECTION
    elif data == 'faq':
        lang = translations[user_languages[user_id]]
        await query.edit_message_text(lang['faq'], reply_markup=InlineKeyboardMarkup(create_keyboard(user_id, 'return')), parse_mode="HTML") 
    elif data == 'return':
        return await greetings(update, context)
    elif data == 'p_confirm':
        lang = translations[user_languages[user_id]]
        await query.edit_message_reply_markup(reply_markup=None)
        await context.bot.send_chat_action(g_state['chat_id'], ChatAction.TYPING)
        await update.effective_chat.send_message(lang['address'] + '\n\n' +
        'La Habana 247\n\nBan Koo Kiang, Building A fl 3, 20/87\n\n1555/10, Tambon, Cha-Am, Chang Wat')
        context.user_data['state'] = 'ADDRESS_OPTIONAL'
        return PERSONAL_INFORMATION
    elif data == 'p_deny':
        lang = translations[user_languages[user_id]]
        await context.bot.send_chat_action(g_state['chat_id'], ChatAction.TYPING)
        await update.effective_chat.send_message(lang['passport'])
        # if os.path.exists('C:\\Users\\kisel\\Desktop\\Telegram_bot\\' + context.user_data['path']):
        #     os.remove('C:\\Users\\kisel\\Desktop\\Telegram_bot\\' + context.user_data['path'])
        context.user_data['state'] = 'PASSPORT_SCAN'
        return PERSONAL_INFORMATION
    elif data == 'optional_deny':
        lang = translations[user_languages[user_id]]
        if context.user_data['state'] == 'PHONE_NUMBER':
            await query.edit_message_reply_markup(reply_markup=None)
            context.user_data['pn'] = None
            if g_state['editing']:
                context.user_data['state'] = 'ORDER_CONFIRM'
                await order_complete(update, context)
                return ORDER_COMPLETE
            context.user_data['state'] = 'WHATSAPP'
            await context.bot.send_chat_action(g_state['chat_id'], ChatAction.TYPING)
            sent_message = await update.effective_chat.send_message(lang['whatsapp'], reply_markup=InlineKeyboardMarkup(create_keyboard(user_id, 'pn_whatsapp')))
            g_state['message_id'] = sent_message.message_id
            return PERSONAL_INFORMATION
        if context.user_data['state'] == 'WHATSAPP':
            await query.edit_message_reply_markup(reply_markup=None)
            context.user_data['whatsapp'] = None
            context.user_data['state'] = 'ORDER_CONFIRM'
            await order_complete(update, context)
            return ORDER_COMPLETE
    elif data == 'confirm_order':
        context.user_data['state'] = 'ORDER_CHECK'
        await order_complete(update, context)
        return ORDER_COMPLETE
    elif data == 'change_bike':
        g_state['editing'] = True
        context.user_data['state'] = 'BIKE_LIST'
        await order(update, context)
        return BIKE_SELECTION
    elif data == 'change_rent_period':
        lang = translations[user_languages[user_id]]
        g_state['editing'] = True
        context.user_data['state'] = 'DATE_RENT_START'
        await update.callback_query.edit_message_text(lang['delivery_date'])
        return BIKE_SELECTION
    elif data == 'change_helmets':
        lang = translations[user_languages[user_id]]
        g_state['editing'] = True
        context.user_data['state'] = 'HELMETS'
        await update.callback_query.edit_message_text(lang['helmets'])
        return BIKE_SELECTION
    elif data == 'change_address':
        lang = translations[user_languages[user_id]]
        g_state['editing'] = True
        context.user_data['state'] = 'ADDRESS_OPTIONAL'
        await update.callback_query.edit_message_text(lang['address'] + '\n\n' +
        'La Habana 247\n\nBan Koo Kiang, Building A fl 3, 20/87\n\n1555/10, Tambon, Cha-Am, Chang Wat')
        return PERSONAL_INFORMATION
    elif data == 'change_pn':
        lang = translations[user_languages[user_id]]
        g_state['editing'] = True
        context.user_data['state'] = 'PHONE_NUMBER'
        await update.callback_query.edit_message_text(lang['thai_pn'], parse_mode="Markdown", reply_markup=InlineKeyboardMarkup(create_keyboard(user_id, 'pn_whatsapp')))
        return PERSONAL_INFORMATION