from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import CallbackContext, ConversationHandler, CommandHandler, MessageHandler, CallbackQueryHandler, filters

# Вопросы по анкете
QUESTIONS = [
    "🔠🔠 Откуда вы о нас узнали?\nПример: Реклама в канале",
    "🔠🔠 Внутриигровой UID\nПример: 1234567890123456789",
    "🔠🔠 Внутриигровой ник\nПример: Ghost",
    "🔠🔠 Сколько времени вы играете в CoD: Mobile?\nПример: 2 года",
    "🔠🔠 Прикрепите скриншоты вашего профиля",
    "🔠🔠 Хотели бы вы попробовать себя в составе команды для участия в турнирах? (Да / Нет)",
    "🔠🔠 Укажите ваше игровое прайм-время и часовой пояс.\nПример: 18:00-20:00 мск",
    "🔠🔠 Готовы ли вы участвовать в командных тренировках? (Да / Нет)",
    "🔠🔠 Какие режимы игры предпочитаете?\nПример: Найти и уничтожить, Опорный пункт, Королевская битва",
    "🔠🔠 Используете ли вы микрофон? (Да / Нет)"
]

user_answers = {}
ADMIN_CHAT_ID = -4666012091

START, QUESTION = range(2)

def start_application(update: Update, context: CallbackContext):
    keyboard = [[InlineKeyboardButton("Заполнить анкету", callback_data="start_form")]]
    reply_markup = InlineKeyboardMarkup(keyboard)
    update.message.reply_text(
        "🖇Готов вступить в ряды Para Bellum Rebirth? Это достойный выбор."


        "🖇Прежде чем присоединиться, немного формальностей."

        "Нажми кнопку ниже, чтобы начать анкету.",
        reply_markup=reply_markup
    )
    return START

def button_handler(update: Update, context: CallbackContext):
    query = update.callback_query
    query.answer()
    user_id = query.from_user.id
    user_answers[user_id] = []
    query.message.reply_text(QUESTIONS[0])
    context.user_data["step"] = 0
    return QUESTION

def handle_answer(update: Update, context: CallbackContext):
    user_id = update.message.from_user.id
    step = context.user_data.get("step", 0)
    user_answers[user_id].append(update.message.text)

    if step + 1 < len(QUESTIONS):
        context.user_data["step"] = step + 1
        update.message.reply_text(QUESTIONS[step + 1])
        return QUESTION
    else:
        # Анкета завершена
        summary = "\n".join(
            [f"{i+1}. {q}\n{a}" for i, (q, a) in enumerate(zip(QUESTIONS, user_answers[user_id]))]
        )
        context.bot.send_message(chat_id=ADMIN_CHAT_ID, text=f"📥 Новая заявка от @{update.message.from_user.username or 'пользователя'}:\n\n{summary}")
        update.message.reply_text("Спасибо! Твоя заявка отправлена офицерам Para Bellum.")
        del user_answers[user_id]
        return ConversationHandler.END

def cancel(update: Update, context: CallbackContext):
    update.message.reply_text("Анкета отменена.")
    return ConversationHandler.END

application_handler = ConversationHandler(
    entry_points=[CommandHandler("вступить", start_application)],
    states={
        START: [CallbackQueryHandler(button_handler, pattern="^start_form$")],
        QUESTION: [MessageHandler(filters.TEXT & ~filters.COMMAND, handle_answer)],
    },
    fallbacks=[CommandHandler("отмена", cancel)],
)
