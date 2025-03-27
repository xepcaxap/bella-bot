from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ConversationHandler, CallbackQueryHandler, MessageHandler, filters, ContextTypes
from admin_check import admin_only

user_answers = {}
ADMIN_CHAT_ID = -4666012091
QUESTIONS = [
    "Укажи свой UID.",
    "Какой у тебя ник в игре?",
    "Откуда вы о нас узнали?",
    "Ты готов участвовать в командных играх и турнирах?",
    "Ты адекватен и не токсичен?",
    "Есть ли у тебя микрофон? (Да / Нет)"
]

START, *STEPS = range(len(QUESTIONS) + 1)

async def start_application(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "Готов вступить в ряды Para Bellum Rebirth? Это достойный выбор.

"
        "Прежде чем присоединиться, немного формальностей.
"
        "Напиши ответы на вопросы, начиная с первого:

"
        f"1. {QUESTIONS[0]}"
    )
    user_answers[update.message.chat_id] = []
    return START

async def handle_response(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.message.chat_id
    text = update.message.text
    step = len(user_answers[chat_id])
    user_answers[chat_id].append(text)

    if step + 1 < len(QUESTIONS):
        await update.message.reply_text(f"{step + 2}. {QUESTIONS[step + 1]}")
        return START
    else:
        result = "
".join([f"{i + 1}. {q}
Ответ: {a}" for i, (q, a) in enumerate(zip(QUESTIONS, user_answers[chat_id]))])
        await context.bot.send_message(chat_id=ADMIN_CHAT_ID, text=f"Новая заявка:

{result}")
        await update.message.reply_text("Спасибо! Твоя анкета отправлена командирам клана.")
        del user_answers[chat_id]
        return ConversationHandler.END

application_handler = ConversationHandler(
    entry_points=[CommandHandler("join", start_application)],
    states={START: [MessageHandler(filters.TEXT & ~filters.COMMAND, handle_response)]},
    fallbacks=[]
)