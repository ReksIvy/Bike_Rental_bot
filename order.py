from telegram import Update, InlineKeyboardMarkup
from telegram.ext import ContextTypes, ConversationHandler
from telegram.constants import ChatAction
from DB import get_available_bikes
from datetime import timedelta, datetime
from utils.globals import *
from utils.user_data import translations, user_languages
from utils.keyboards import create_keyboard
from order_complete import order_complete
from utils.logger import log
from utils.fallbacks import cancel
import logging

async def order(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    user_id = update.effective_chat.id
    lang = translations[user_languages[user_id]]
    state = context.user_data['state']

    if state == 'BIKE_LIST':
        try:
        # Formatted list of available bikes
            available_bikes = [
                f"{i+1}. {row[1]}" + f"{' (' + lang['available_until'] + str(row[6]) + ')' if row[6] and row[6] > datetime.now().date() + timedelta(days=1) else ''}" +
                f"{' (' + lang['available_from'] + str(row[7]) + ')' if row[7] and (not row[6] or row[6] <= datetime.now().date() + timedelta(days=1)) and row[7] > datetime.now().date() else ''}"
                + f"\n{lang['bike_production']} {row[2]}\n{lang['bike_color']}" +
                f" {row[3]}\n{lang['bike_price']}\n{lang['bike_price_week']} {row[4]}฿\n{lang['bike_price_month']} {row[5]}฿\n\n"
            for i, row in enumerate(get_available_bikes())
            ]
            if len(available_bikes) == 0:
                await update.callback_query.edit_message_text(lang['no_bikes'])
                return ConversationHandler.END
            if g_state['editing']:
                await update.callback_query.edit_message_text(lang['bike_list'] + "\n".join(available_bikes) + lang['choose_bike'])
            else:
                sent_message = await update.callback_query.edit_message_text(lang['bike_list'] + "\n".join(available_bikes) + lang['choose_bike'],
                                                            reply_markup=InlineKeyboardMarkup(create_keyboard(user_id, 'return')))
                g_state['message_id'] = sent_message.message_id
            context.user_data['state'] = 'BIKE_SELECTION'
        except Exception as e:
            log("log/bot.log", e, 40)
            await cancel(update, context)

    elif state == 'BIKE_SELECTION':
        user_input = update.message.text
        try:
            await context.bot.edit_message_reply_markup(chat_id=g_state['chat_id'], message_id=g_state['message_id'], reply_markup=None)
        except Exception as e:
            log("log/bot.log", e, logging.WARNING)
        
        try:
            try:
                bike_id = int(user_input)
            except Exception as e:
                print(e)
                await context.bot.send_chat_action(g_state['chat_id'], ChatAction.TYPING)
                await update.message.reply_text(lang['bike_error'])
                return BIKE_SELECTION
            context.user_data['bike_id'] = bike_id
            bike_data = list(enumerate(get_available_bikes())) # Get a list of available bikes from DB
            # Fill in all bike details
            selected_bike = next((row[1] for index, row in bike_data if index == bike_id - 1), None)
            context.user_data['available_from'] = next((row[6] or datetime.now().date() for index, row in bike_data if index == bike_id - 1), datetime.now().date())
            context.user_data['available_until'] = next((row[7] or datetime.max.date() for index, row in bike_data if index == bike_id - 1), datetime(2100, 1, 1).date())
            context.user_data['b_id'] = next((row[0] for index, row in bike_data if index == bike_id - 1), None)
            context.user_data['bike_price_week'] = next((row[4] for index, row in bike_data if index == bike_id - 1), None)
            context.user_data['bike_price_month'] = next((row[5] for index, row in bike_data if index == bike_id - 1), None)

            if selected_bike:
                context.user_data["selected_bike"] = selected_bike
                await context.bot.send_chat_action(g_state['chat_id'], ChatAction.TYPING)
                await update.message.reply_text(lang['delivery_date'])
                context.user_data['state'] = 'DATE_RENT_START'
            else:
                await context.bot.send_chat_action(g_state['chat_id'], ChatAction.TYPING)
                await update.message.reply_text(lang['bike_error'])
        except Exception as e:
            log("log/bot.log", e, logging.ERROR)
            await cancel(update, context)
            
    
    elif state == 'DATE_RENT_START':
        user_input = update.message.text

        # rent_start validation
        try:
            try:
                rent_start = datetime.strptime(user_input, "%d.%m.%y").date()
            except Exception as e:
                print(e)
                await context.bot.send_chat_action(g_state['chat_id'], ChatAction.TYPING)
                await update.message.reply_text(lang['delivery_date_error'])
                return BIKE_SELECTION
            if rent_start <= datetime.now().date():
                await context.bot.send_chat_action(g_state['chat_id'], ChatAction.TYPING)
                await update.message.reply_text(lang['delivery_date_error'])
                return BIKE_SELECTION
            if rent_start > context.user_data['available_until'] or rent_start < context.user_data['available_from']:
                await context.bot.send_chat_action(g_state['chat_id'], ChatAction.TYPING)
                await update.message.reply_text(lang['delivery_date_error'])
                return BIKE_SELECTION
            context.user_data['rent_start'] = rent_start
            await context.bot.send_chat_action(g_state['chat_id'], ChatAction.TYPING)
            await update.message.reply_text(lang['rent_end'])
            context.user_data['state'] = 'DATE_RENT_END'
        except Exception as e:
            log("log/bot.log", e, logging.ERROR)
            await cancel(update, context)
            
    
    elif state == 'DATE_RENT_END':
        user_input = update.message.text

        # rent_end can be a number of days or a date in DD.MM.YY format
        try:
            if len(user_input.split('.')) == 1:
                days_of_rent = int(user_input)
                # Min rent period
                if days_of_rent < 5:
                    await update.message.reply_text(lang['min_rent_error'])
                    return BIKE_SELECTION
                context.user_data['rent_end'] = context.user_data['rent_start'] + timedelta(days=days_of_rent)
            elif len(user_input.split('.')) == 3:
                # Min rent period
                if datetime.strptime(user_input, '%d.%m.%y').date() <= (context.user_data['rent_start'] + timedelta(days=4)):
                    await context.bot.send_chat_action(g_state['chat_id'], ChatAction.TYPING)
                    await update.message.reply_text(lang['min_rent_error'])
                    return BIKE_SELECTION
                context.user_data['rent_end'] = datetime.strptime(user_input, '%d.%m.%y').date()
            else:
                await context.bot.send_chat_action(g_state['chat_id'], ChatAction.TYPING)
                await update.message.reply_text(lang['rent_end_error'])
                return 
            # Checks to see if the chosen rent period conflicts with any upcoming or current order
            if context.user_data['rent_end'] > context.user_data['available_until'] or context.user_data['rent_end'] < context.user_data['available_from']:
                await context.bot.send_chat_action(g_state['chat_id'], ChatAction.TYPING)
                await update.message.reply_text(lang['rent_end_error'])
                return BIKE_SELECTION
            if g_state['editing']:
                context.user_data['state'] = 'ORDER_CONFIRM'
                await order_complete(update, context)
                return ORDER_COMPLETE
            await update.message.reply_text(lang['helmets'])
            context.user_data['state'] = 'HELMETS'
        except Exception as e:
            log("log/bot.log", e, logging.ERROR)
            await cancel(update, context)

    elif state == 'HELMETS':
        user_input = update.message.text

        try:
            if not user_input.isdigit() or int(user_input) > 2:
                await context.bot.send_chat_action(g_state['chat_id'], ChatAction.TYPING)
                await update.message.reply_text(lang['helmets'])
                return BIKE_SELECTION
            context.user_data['helmets'] = int(user_input)
            await context.bot.send_chat_action(g_state['chat_id'], ChatAction.TYPING)
            await update.message.reply_text(lang['helmets_kids'])
            context.user_data['state'] = 'HELMETS_KIDS'
        except Exception as e:
            log("log/bot.log", e, logging.ERROR)
            await cancel(update, context)
    
    elif state == 'HELMETS_KIDS':
        user_input = update.message.text

        try:
            if not user_input.isdigit() or int(user_input) > 2:
                await context.bot.send_chat_action(g_state['chat_id'], ChatAction.TYPING)
                await update.message.reply_text(lang['helmets_kids'])
                return BIKE_SELECTION
            context.user_data['helmets_kids'] = int(user_input)
            if g_state['editing']:
                context.user_data['state'] = 'ORDER_CONFIRM'
                await order_complete(update, context)
                return ORDER_COMPLETE
            if g_state['exists']:
                await context.bot.send_chat_action(g_state['chat_id'], ChatAction.TYPING)
                await update.message.reply_text(lang['address'] + '\n\n' +
                'La Habana 247\n\nBan Koo Kiang, Building A fl 3, 20/87\n\n1555/10, Tambon, Cha-Am, Chang Wat')
                context.user_data['state'] = 'ADDRESS_OPTIONAL'
                return PERSONAL_INFORMATION
            context.user_data['state'] = 'PASSPORT_SCAN'
            await context.bot.send_chat_action(g_state['chat_id'], ChatAction.TYPING)
            await update.message.reply_text(lang['passport'])
            return PERSONAL_INFORMATION
        except Exception as e:
            log("log/bot.log", e, logging.ERROR)
            await cancel(update, context)