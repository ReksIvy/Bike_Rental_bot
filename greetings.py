from telegram import Update, InlineKeyboardMarkup
from telegram.ext import ContextTypes
from telegram.constants import ChatAction
from utils.user_data import translations, user_languages
from utils.globals import *
from utils.keyboards import create_keyboard

async def greetings(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_chat.id
    lang = translations[user_languages[user_id]]
    
    # If the user is new, the first message they see is language selection, which is edited to greetings
    if update.callback_query:
        await update.callback_query.edit_message_text(lang["welcome_message"],
                                                  reply_markup=InlineKeyboardMarkup(create_keyboard(user_id, 'greetings')))
    # If user's preferred language is already set (old user) this is the first message
    else:
        await context.bot.send_chat_action(g_state['chat_id'], ChatAction.TYPING)
        await update.effective_chat.send_message(lang["welcome_message"],
                                                  reply_markup=InlineKeyboardMarkup(create_keyboard(user_id, 'greetings')))