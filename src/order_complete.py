from telegram import Update, InlineKeyboardMarkup
from telegram.ext import ContextTypes, ConversationHandler
from telegram.constants import ChatAction
from src.utils.user_data import translations, user_languages
from src.utils.globals import *
from src.utils.keyboards import create_keyboard
from src.utils.logger import log
import logging
from src.utils.DB import get_available_bikes, send_order

async def order_complete(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_chat.id
    lang = translations[user_languages[user_id]]
    state = context.user_data['state']

    if state == 'ORDER_CONFIRM':
        # Send a message with all order details for user to confirm or edit
        try:
            pn_text = ''
            whatsapp_text = ''
            days_of_rent = (context.user_data['rent_end'] - context.user_data['rent_start']).days
            if days_of_rent < 17:
                context.user_data['price'] = str(round(days_of_rent * (context.user_data['bike_price_week'] / 7)))
            elif days_of_rent >= 17:
                context.user_data['price'] = str(round(days_of_rent * (context.user_data['bike_price_month'] / 30)))
            if context.user_data['pn']:
                pn_text = f'{lang['o_pn']} {context.user_data['pn']}\n'
            if context.user_data['whatsapp']:
                whatsapp_text = f'{lang['o_whatsapp']} {context.user_data['whatsapp']}\n'
            
            await context.bot.send_chat_action(g_state['chat_id'], ChatAction.TYPING)
            sent_message = await update.effective_chat.send_message(
            lang['order_check'] + '\n\n' +
            f'{lang['o_chosen_bike']} {context.user_data['selected_bike']}\n' +
            f'{lang['o_delivery_date']} {context.user_data['rent_start'].strftime("%d.%m.%y")}\n' +
            f'{lang['o_rent_end']} {context.user_data['rent_end'].strftime("%d.%m.%y")}\n' +
            f'{lang['o_helmets']} {context.user_data['helmets']}/{context.user_data['helmets_kids']}\n' +
            f'{lang['o_address']} {context.user_data['address']}\n' +
            f'{lang['o_price']} {context.user_data['price']}฿ + 1500฿\n' +
            pn_text + whatsapp_text, reply_markup=InlineKeyboardMarkup(create_keyboard(user_id, 'order_info')), disable_web_page_preview=True)
            if g_state['editing']:
                g_state['editing'] = False
            g_state['message_id'] = sent_message.message_id
        except Exception as e:
            print(e)
    
    elif state == 'ORDER_CHECK':
        # Check to see if their chosen bike is available as of the moment they press 'confirm'
        b_id = next((row[0] for row in get_available_bikes() if row[0] == context.user_data['b_id']), None) 
        if not context.user_data['b_id'] == b_id:
            await context.bot.send_chat_action(g_state['chat_id'], ChatAction.TYPING)
            await update.effective_chat.send_message(lang['bike_unavailable'])
            return ConversationHandler.END
        context.user_data['state'] = 'ORDER_COMPLETE'
        await order_complete(update, context)
    
    elif state == 'ORDER_COMPLETE':
        # Send final order details to user and to admin, as well as to the DB
        try:
            order_id = await send_order(context.user_data)
            await context.bot.send_chat_action(g_state['chat_id'], ChatAction.TYPING)
            await context.bot.edit_message_text(chat_id=g_state['chat_id'], message_id=g_state['message_id'], text=lang['order_info_head'] + '\n\n' +
            f'{lang['order_id']} {order_id}\n' +
            f'{lang['o_chosen_bike']} {context.user_data['selected_bike']}\n' +
            f'{lang['o_delivery_date']} {context.user_data['rent_start']}\n' +
            f'{lang['o_rent_end']} {context.user_data['rent_end']}\n' +
            f'{lang['o_helmets']} {context.user_data['helmets']}/{context.user_data['helmets_kids']}\n' +
            f'{lang['o_address']} {context.user_data['address']}' +
            f'{lang['o_price']} {context.user_data['price']}฿ + 1500฿\n\n' +
            f'{lang['contacts']}', reply_markup=None)

            await context.bot.send_message(ADMIN_CHAT,
            f'{translations['ru']['order_id']} {order_id}\n' +
            f'{translations['ru']['o_chosen_bike']} {context.user_data['selected_bike']}/{context.user_data['b_id']}\n' +
            f'{translations['ru']['o_delivery_date']} {context.user_data['rent_start']}\n' +
            f'{translations['ru']['o_rent_end']} {context.user_data['rent_end']}\n' +
            f'{translations['ru']['o_helmets']} {context.user_data['helmets']}/{context.user_data['helmets_kids']}\n' +
            f'{translations['ru']['o_address']} {context.user_data['address']}\n' +
            f'{translations['ru']['o_price']} {context.user_data['price']}฿\n' +
            f'{translations['ru']['o_fullname']} {context.user_data['fullname']}\n' +
            f'{f'{translations['ru']['o_pn']} {context.user_data['pn']}\n' if context.user_data['pn'] else ''}' +
            f'{translations['ru']['o_telegram']} {context.user_data['telegram']}\n' +
            f'{f'{translations['ru']['o_whatsapp']} {context.user_data['whatsapp']}\n' if context.user_data['whatsapp'] else ''}')
            return ConversationHandler.END
        except Exception as e:
            log("log/bot.log", e, logging.ERROR)
