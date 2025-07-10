from telegram.ext import ConversationHandler, ContextTypes
from telegram import Update

async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    await update.message.reply_text('''Произошла ошибка во время оформления заказа. Пожалуйста попробуйте снова с помощью команды /start

An error occured during order processing. Please try again with /start command''')
    return ConversationHandler.END