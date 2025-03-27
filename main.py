
import os
import random
import requests
from dotenv import load_dotenv
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, CallbackQueryHandler, ContextTypes
from bella_persona import bella_system_prompt
from application_form import start_application, application_handler
from admin_check import admin_only
from datetime import datetime, timedelta

load_dotenv()
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
HUGGINGFACE_API_KEY = os.getenv("HUGGINGFACE_API_KEY")
HUGGINGFACE_API_URL = "https://api-inference.huggingface.co/models/mistralai/Mixtral-8x7B-Instruct-v0.1"
HEADERS = {"Authorization": f"Bearer {HUGGINGFACE_API_KEY}"}

user_contexts = {}
ADMIN_CHAT_ID = -4666012091

def get_context(chat_id):
    return user_contexts.get(chat_id, [])

def update_context(chat_id, role, content):
    if chat_id not in user_contexts:
        user_contexts[chat_id] = []
    user_contexts[chat_id].append({"role": role, "content": content})
    user_contexts[chat_id] = user_contexts[chat_id][-6:]

def meta_text():
    return "На март 2025 мета: CBR4, M13, HVK-30 (с Large Caliber), KRM-262. Всё остальное — по вкусу, но эти — имба."

def sovet_text():
    советы = [
        "Не раш на респе — живи дольше, набивай очки.",
        "Всегда ставь UAV первым — инфа решает.",
        "Smoke — лучший друг в Hardpoint.",
        "Если не идёт — смени пушку, а не настройку геймпада."
    ]
    return random.choice(советы)

async def welcome_new_member(update: Update, context: ContextTypes.DEFAULT_TYPE):
    name = update.message.new_chat_members[0].first_name
    welcome_messages = [
        f"Она, {name}, залетела! Надеюсь, ты не бот — у нас конкуренция с настоящими.",
        f"{name}, добро пожаловать в логово Para Bellum. Надеюсь, ты умеешь стрелять, а не ныть.",
        f"{name} присоединился к Para Bellum. Осторожно, новичок в чате.",
        f"Ну привет, {name}. В клане Para Bellum шутки кончаются там, где начинается рейтинговая игра."
    ]
    await update.message.reply_text(random.choice(welcome_messages))

async def bella_reply(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.message is None:
        return

    chat_id = update.message.chat_id
    user_input = update.message.text

    if update.message.chat.type in ["group", "supergroup"]:
        if not (update.message.reply_to_message and update.message.reply_to_message.from_user.id == context.bot.id) and f"@{context.bot.username}" not in user_input:
            return

    update_context(chat_id, "user", user_input)
    messages = [bella_system_prompt] + get_context(chat_id)

    try:
        prompt = f"{bella_system_prompt['content']}\n" + "\n".join(
            f"{m['role']}: {m['content']}" for m in get_context(chat_id)
        ) + "\nassistant:"

        response = requests.post(
            HUGGINGFACE_API_URL,
            headers=HEADERS,
            json={"inputs": prompt, "max_new_tokens": 100}
        )

        if response.status_code == 200:
            generated = response.json()[0]["generated_text"]
            reply = generated.split("assistant:")[-1].strip()
        else:
            reply = "Сервер HuggingFace занят. Попробуй чуть позже."

        update_context(chat_id, "assistant", reply)
        await update.message.reply_text(reply)

    except Exception as e:
        await update.message.reply_text("Что-то пошло не так, командир... Попробуй позже.")
        print(e)

app = ApplicationBuilder().token(TELEGRAM_BOT_TOKEN).build()
app.add_handler(CommandHandler("meta", lambda u, c: u.message.reply_text(meta_text())))
app.add_handler(CommandHandler("sovet", lambda u, c: u.message.reply_text(sovet_text())))
app.add_handler(CommandHandler("join", start_application))
app.add_handler(application_handler)
app.add_handler(MessageHandler(filters.StatusUpdate.NEW_CHAT_MEMBERS, welcome_new_member))
app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, bella_reply))
app.run_polling()
