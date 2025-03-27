from telegram import Update
from telegram.ext import ContextTypes

ADMIN_CHAT_ID = -4666012091

async def admin_only(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.message.chat_id != ADMIN_CHAT_ID:
        await update.message.reply_text("Извините, эта команда только для админов.")
        return False
    return True