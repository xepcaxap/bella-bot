from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import CallbackContext, ConversationHandler, CommandHandler, MessageHandler, CallbackQueryHandler, filters

# Вопросы по анкете
QUESTIONS = [
    "🆔 Откуда вы о нас узнали?\nПример: Реклама в канале",
    "🔠🔠 Внутриигровой UID\nПример: 1234567890123456789",
    "🔠🔠 Внутриигровой ник\nПример: Ghost",
    "🎮 Сколько времени вы играете в CoD: Mobile?\nПример: 2 года",
    "📸 Прикрепите скриншоты вашего профиля",
    "🏆 Хотели бы вы попробовать себя в составе команды для участия в турнирах? (Да / Нет)",
    "🕒 Укажите ваше игровое прайм-время и часовой пояс.\nПример: 18:00-20:00 мск",
    "🤝 Готовы ли вы участвовать в командных тренировках? (Да / Нет)",
    "🎯 Какие режимы игры предпочитаете?\nПример: Найти и уничтожить, Опорный пункт, Королевская битва",
    "🎙 Используете ли вы микрофон? (Да / Нет)"
]

user_answers = {}
ADMIN_CHAT_ID = -4666012091

START, QUESTION = range(2)

async def start_application(update: Update, context: CallbackContext):
    keyboard = [[InlineKeyboardButton("Заполнить анкету", callback_data="start_form")]]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text(
        "📎Готов вступить в ряды Para Bellum Rebirth? Это достойный выбор.\n\n"
        "📎Прежде чем присоединиться, немного формальностей.\n"
        "Нажми кнопку ниже, чтобы начать анкету.",
        reply_markup=reply_markup
    )
    return START

async def button_handler(update: Update, context: CallbackContext):
    query = update.callback_query
    await query.answer()
    user_id = query.from_user.id
    user_answers[user_id] = []
    await query.message.reply_text(QUESTIONS[0])
    return QUESTION

async def handle_question(update: Update, context: CallbackContext):
    user_id = update.message.from_user.id
    answer = update.message.text
    user_answers[user_id].append(answer)
    if len(user_answers[user_id]) < len(QUESTIONS):
        await update.message.reply_text(QUESTIONS[len(user_answers[user_id])])
        return QUESTION
    else:
        summary = ""
        for i, q in enumerate(QUESTIONS):
            summary += f"{q}\n{user_answers[user_id][i]}\n\n"
        await context.bot.send_message(
            chat_id=ADMIN_CHAT_ID,
            text=f"📥 Новая заявка от @{update.message.from_user.username or 'пользователя'}:\n\n{summary}"
        )
        await update.message.reply_text("Спасибо! Твоя заявка отправлена офицерам Para Bellum.")
        return ConversationHandler.END

application_handler = ConversationHandler(
    entry_points=[CommandHandler("join", start_application)],
    states={
        START: [CallbackQueryHandler(button_handler, pattern="^start_form$")],
        QUESTION: [MessageHandler(filters.TEXT & ~filters.COMMAND, handle_question)],
    },
    fallbacks=[]
)