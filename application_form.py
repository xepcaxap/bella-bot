from telegram import Update
from telegram.ext import ConversationHandler, MessageHandler, CommandHandler, ContextTypes, filters

user_answers = {}
ADMIN_CHAT_ID = -4666012091

START, QUESTION = range(2)

questions = [
    "1. Как тебя зовут?",
    "2. Сколько тебе лет?",
    "3. Во сколько обычно играешь?",
    "4. Используешь ли ты микрофон? (Да / Нет)"
]

async def start_application(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.from_user.id
    user_answers[user_id] = []

    await update.message.reply_text(
        "Готов вступить в ряды Para Bellum Rebirth? Это достойный выбор.\n\n"
        "Прежде чем присоединиться, немного формальностей.\n"
        "Напиши ответы на вопросы, начиная с первого:"
    )
    await update.message.reply_text(questions[0])
    return QUESTION

async def handle_question(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.from_user.id
    answer = update.message.text
    user_answers[user_id].append(answer)

    if len(user_answers[user_id]) < len(questions):
        next_question = questions[len(user_answers[user_id])]
        await update.message.reply_text(next_question)
        return QUESTION
    else:
        text = "\n".join(f"{i+1}) {a}" for i, a in enumerate(user_answers[user_id]))
        await context.bot.send_message(chat_id=ADMIN_CHAT_ID, text=f"Новая анкета от @{update.message.from_user.username or 'юзер'}:\n{text}")
        await update.message.reply_text("Спасибо! Мы рассмотрим твою анкету и свяжемся с тобой.")
        return ConversationHandler.END

application_handler = ConversationHandler(
    entry_points=[CommandHandler("join", start_application)],
    states={QUESTION: [MessageHandler(filters.TEXT & ~filters.COMMAND, handle_question)]},
    fallbacks=[],
)