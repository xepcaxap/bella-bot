import requests
import os
import random
from dotenv import load_dotenv
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, ContextTypes, filters
from bella_persona import bella_system_prompt
from admin_check import admin_only
from datetime import datetime, timedelta
from application_form import application_handler

load_dotenv()
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
HUGGINGFACE_API_URL = "https://api-inference.huggingface.co/models/tiiuae/falcon-rw-1b"
HUGGINGFACE_API_KEY = os.getenv("HUGGINGFACE_API_KEY")
HEADERS = {"Authorization": f"Bearer {HUGGINGFACE_API_KEY}"}

user_contexts = {}

def get_context(chat_id):
    return user_contexts.get(chat_id, [])

def update_context(chat_id, role, content):
    if chat_id not in user_contexts:
        user_contexts[chat_id] = []
    user_contexts[chat_id].append({"role": role, "content": content})
    user_contexts[chat_id] = user_contexts[chat_id][-6:]

def meta_text():
    return "На март 2025 мета: CBR4, M13, HVK-30 (с Large Caliber), KRM-262. Всё остальное — по вкусу, но эти — имба."

def совет_text():
    советы = [
        "Не раш на респе — живи дольше, набивай очки.",
        "Всегда ставь UAV первым — инфа решает.",
        "Smoke — лучший друг в Hardpoint.",
        "Если не идёт — смени пушку, а не настройку геймпада."
    ]
    return random.choice(советы)

def факт_text():
    факты = [
        "Клан Para Bellum выигрывал самые жёсткие катки даже в пати 3х.",
        "В Para Bellum не носят ботинки — мы ходим по головам.",
        "Если ты не в Para Bellum — ты всё ещё можешь мечтать."
    ]
    return random.choice(факты)

def оскорбление_text():
    оск = [
        "Ты играешь так, будто вышел из лобби Para Bellum и потерял скилл.",
        "Если бы ты был в Para Bellum — тебя бы уже выгнали. Шучу. Или нет.",
        "Ты не из Para Bellum, да? Объясняет многое..."
    ]
    return random.choice(оск)

async def command_meta(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(meta_text())

async def command_sovet(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(совет_text())

async def command_fact(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(факт_text())

async def command_insult(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(оскорбление_text())

async def command_help(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "/meta — Актуальная мета\n"
        "/sovet — Игровой совет\n"
        "/fact — Факт о CoDM\n"
        "/insult — Подколка от Бэллы\n"
        "/mute — Замутить игрока (админ)\n"
        "/kick — Кикнуть игрока (админ)\n"
        "/help — Все команды"
    )

@admin_only
async def mute_user(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.message.reply_to_message:
        await update.message.reply_text("Ответь на сообщение того, кого хочешь замутить.")
        return
    user_id = update.message.reply_to_message.from_user.id
    until_date = datetime.now() + timedelta(minutes=10)
    try:
        await context.bot.restrict_chat_member(
            chat_id=update.effective_chat.id,
            user_id=user_id,
            permissions={"can_send_messages": False},
            until_date=until_date
        )
        await update.message.reply_text("Выдан мут. Пусть остынет.")
    except Exception as e:
        await update.message.reply_text("Не смог замутить. Возможно, у меня нет прав.")
        print(e)

@admin_only
async def kick_user(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.message.reply_to_message:
        await update.message.reply_text("Ответь на сообщение того, кого хочешь кикнуть.")
        return
    user_id = update.message.reply_to_message.from_user.id
    try:
        await context.bot.ban_chat_member(chat_id=update.effective_chat.id, user_id=user_id)
        await update.message.reply_text("Игрок отправлен в аут.")
    except Exception as e:
        await update.message.reply_text("Не получилось кикнуть. Проверь права.")
        print(e)

async def welcome_new_member(update: Update, context: ContextTypes.DEFAULT_TYPE):
    for member in update.message.new_chat_members:
        name = member.full_name
        welcome_messages = [
            f"Опа, {name} залетел! Надеюсь, ты не бот — у нас конкуренция с настоящими.",
            f"{name}, добро пожаловать в логово Para Bellum. Надеюсь, ты умеешь стрелять, а не ныть.",
            f"{name} присоединился к Para Bellum. Осторожно, новичок в чате. Не трогать — пока не проверим на прочность.",
            f"Ну привет, {name}. В клане Para Bellum шутки кончаются там, где начинается рейтинговая игра."
        ]
        await update.message.reply_text(random.choice(welcome_messages))

async def bella_reply(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.message.chat_id
    user_input = update.message.text

    update_context(chat_id, "user", user_input)
    messages = [bella_system_prompt] + get_context(chat_id)

    
        prompt = f"{bella_system_prompt['content']}\n" + "\n".join(
    f"{m['role']}: {m['content']}" for m in get_context(chat_id)
) + "\nassistant:"

try:
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
app.add_handler(CommandHandler("meta", command_meta))
app.add_handler(CommandHandler("sovet", command_sovet))
app.add_handler(CommandHandler("fact", command_fact))
app.add_handler(CommandHandler("insult", command_insult))
app.add_handler(CommandHandler("help", command_help))
app.add_handler(CommandHandler("mute", mute_user))
app.add_handler(CommandHandler("kick", kick_user))
app.add_handler(MessageHandler(filters.StatusUpdate.NEW_CHAT_MEMBERS, welcome_new_member))
app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, bella_reply))

app.run_polling()
