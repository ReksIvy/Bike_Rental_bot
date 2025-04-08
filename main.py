from telegram import Update, BotCommand, InlineKeyboardMarkup
from telegram.ext import Application, MessageHandler, CommandHandler, filters, ContextTypes, ConversationHandler,  CallbackQueryHandler
from telegram.constants import ChatAction
from utils.user_data import user_languages
from bot_handlers import button_handler
from utils.globals import *
from greetings import greetings
from order import order
from personal_info import personal_info
from utils.keyboards import create_keyboard
from order_complete import order_complete
from DB import is_new_user

COMMANDS = [
    BotCommand("start", "Start the bot"),
    BotCommand("cancel", "Cancel order")
]

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    username = update.message.from_user.username
    g_state['chat_id'] = update.message.chat_id
    context.user_data['telegram'] = f'https://t.me/{username}'
    # Check if the user is already in the DB to shorten order process
    context.user_data['pass_num'], context.user_data['fullname'], context.user_data['pn'], context.user_data['whatsapp'] = await is_new_user(username)
    user_id = update.message.from_user.id
    # Check if the user has a preferred language
    if not user_languages.get(user_id):
        await context.bot.send_chat_action(g_state['chat_id'], ChatAction.TYPING)
        await update.message.reply_text(
        'Добро пожаловать в Bike Rental Group. С помощью данного бота вы сможете легко забронировать байк.' +
        'Перед началом, пожалуйста, выберите предпочитаемый язык\n\n' +
        'Welcome to Bike Rental Group. This bot will help you rent a bike. Before we start, please choose your preferred language',
        reply_markup=InlineKeyboardMarkup(create_keyboard(user_id, 'lang')))

        return LANGUAGE
    await greetings(update, context)
    return GREETINGS


async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    await update.message.reply_text('''Произошла ошибка во время оформления заказа. Пожалуйста попробуйте снова с помощью команды /start

An error occured during order processing. Please try again with /start command''')
    return ConversationHandler.END

if __name__ == "__main__":
    app = Application.builder().token(TOKEN).build()

    conversation_handler = ConversationHandler(
        entry_points=[CommandHandler('start', start)],
        states={
            GREETINGS: [MessageHandler(filters.TEXT & ~filters.COMMAND, greetings), CallbackQueryHandler(button_handler)],
            BIKE_SELECTION: [MessageHandler(filters.TEXT & ~filters.COMMAND, order), CallbackQueryHandler(button_handler)],
            LANGUAGE: [CallbackQueryHandler(button_handler)],
            PERSONAL_INFORMATION: [MessageHandler(filters.TEXT & ~filters.COMMAND, personal_info), 
            MessageHandler(filters.PHOTO, personal_info), CallbackQueryHandler(button_handler)],
            ORDER_COMPLETE: [MessageHandler(filters.TEXT & ~filters.COMMAND, order_complete), CallbackQueryHandler(button_handler)]
        },
        fallbacks=[CommandHandler('cancel', cancel)]
    )

    app.add_handler(conversation_handler)

    app.run_polling()