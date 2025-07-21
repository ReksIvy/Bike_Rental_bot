from telegram import Update, InlineKeyboardMarkup
from telegram.ext import ContextTypes
from telegram.constants import ChatAction
import readmrz
import os
import cv2
from src.utils.globals import *
from src.utils.user_data import user_languages, translations
from src.utils.keyboards import create_keyboard
from src.order_complete import order_complete
from pathlib import Path
from src.utils.logger import log
import logging
import random
import string

async def personal_info(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    user_id = update.effective_chat.id
    lang = translations[user_languages[user_id]]
    state = context.user_data['state']

    if state == 'PASSPORT_SCAN':
        try:
            # Get photo and establish a directory for it to be saved to
            passport_scan = update.message.photo[-1]
            file = await passport_scan.get_file()
            directory_path = PATH / Path('bot_scans')
            if not os.path.exists(directory_path):
                os.makedirs(directory_path)
            
            # Make sure the file name is unique
            chars = string.ascii_letters + string.digits
            download_path = directory_path / Path(''.join(random.choices(chars, k=10)))
            while os.path.exists(download_path):
                download_path = directory_path / Path(''.join(random.choices(chars, k=10)))
            file_path = await file.download_to_drive(download_path)
            context.user_data['path'] = download_path

            # Process photo
            image = cv2.imread(file_path)
            detector = readmrz.MrzDetector()
            reader = readmrz.MrzReader()
            cropped = detector.crop_area(image)
            result = reader.process(cropped)
            
            # Respond to user
            await context.bot.send_chat_action(g_state['chat_id'], ChatAction.TYPING)
            sent_message = await update.message.reply_text(f'{lang['passport_confirm']}\n{lang['passport_fullname']} {result['surname'] + ' ' + result['name']}\n' +
            f'{lang['passport_number']} {result['document_number']}', reply_markup=InlineKeyboardMarkup(create_keyboard(user_id, 'passport_confirm')))
            context.user_data['fullname'] = result['surname'] + ' ' + result['name']
            context.user_data['pass_num'] = result['document_number']

            # Save message id to remove buttons after the user has clicked one
            g_state['message_id'] = sent_message.message_id
        except Exception as e:
            log("log/bot.log", e, logging.ERROR)
            await context.bot.send_chat_action(g_state['chat_id'], ChatAction.TYPING)
            await update.message.reply_text(lang['passport_error'])
            try:
                if 'path' in context.user_data and os.path.exists(context.user_data['path']):
                    os.remove(context.user_data['path'])
            finally:
                pass
    
    elif state == 'ADDRESS_OPTIONAL':
        # Address can be any string
        try:
            if update.message.text == None:
                await context.bot.send_chat_action(g_state['chat_id'], ChatAction.TYPING)
                await update.message.reply_text(lang['address_error'])
                return PERSONAL_INFORMATION
            context.user_data['address'] = update.message.text
            if g_state['editing'] or g_state['exists']:
                context.user_data['state'] = 'ORDER_CONFIRM'
                await order_complete(update, context)
                return ORDER_COMPLETE
            await context.bot.send_chat_action(g_state['chat_id'], ChatAction.TYPING)
            sent_message = await update.message.reply_text(lang['thai_pn'], parse_mode="Markdown", reply_markup=InlineKeyboardMarkup(create_keyboard(user_id, 'pn_whatsapp')))
            context.user_data['state'] = 'PHONE_NUMBER'
            g_state['message_id'] = sent_message.message_id
        except Exception as e:
            return PERSONAL_INFORMATION
    
    elif state == 'PHONE_NUMBER':
        # Phone number can start with 0 or +66
        try:
            pn = str(update.message.text)
            if (len(list(pn)) == 12 and list(pn)[0] == '+') or (len(list(pn)) == 10 and list(pn)[0] == '0'):
                await context.bot.edit_message_reply_markup(chat_id=g_state['chat_id'], message_id=g_state['message_id'], reply_markup=None)
                context.user_data['pn'] = pn
                context.user_data['state'] = 'WHATSAPP'
                if g_state['editing']:
                    context.user_data['state'] = 'ORDER_CONFIRM'
                    await order_complete(update, context)
                    return ORDER_COMPLETE
                await context.bot.send_chat_action(g_state['chat_id'], ChatAction.TYPING)
                sent_message = await update.message.reply_text(lang['whatsapp'], parse_mode="Markdown", reply_markup=InlineKeyboardMarkup(create_keyboard(user_id, 'pn_whatsapp')))
                g_state['message_id'] = sent_message.message_id
            else:
                await context.bot.send_chat_action(g_state['chat_id'], ChatAction.TYPING)
                await update.message.reply_text(lang['thai_pn_error'])
        except Exception as e:
            return PERSONAL_INFORMATION
    
    elif state == 'WHATSAPP':
        try:
            if 'https://wa.me/' in update.message.text:
                await context.bot.edit_message_reply_markup(chat_id=g_state['chat_id'], message_id=g_state['message_id'], reply_markup=None)
                context.user_data['whatsapp'] = update.message.text
                context.user_data['state'] = 'ORDER_CONFIRM'
                await order_complete(update, context)
                return ORDER_COMPLETE
            else:
                await context.bot.send_chat_action(g_state['chat_id'], ChatAction.TYPING)
                await update.message.reply_text(lang['whatsapp_error'])
                return PERSONAL_INFORMATION
        except Exception as e:
            print(e)