import telebot
import openai
import os
from dotenv import load_dotenv

load_dotenv()

TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

openai.api_key = OPENAI_API_KEY
bot = telebot.TeleBot(TELEGRAM_BOT_TOKEN)

SYSTEM_PROMPT = "Ты — Белла, вайфу клана Para Bellum Rebirth из Call of Duty Mobile. Общайся саркастично, но дружелюбно. Ты обожаешь винтовку NA-45."

@bot.message_handler(func=lambda message: message.chat.type in ['group', 'supergroup'])
def handle_group(message):
    if message.reply_to_message and message.reply_to_message.from_user.id == bot.get_me().id:
        respond(message)

@bot.message_handler(func=lambda message: message.chat.type == 'private')
def handle_private(message):
    respond(message)

def respond(message):
    try:
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": message.text}
            ],
            max_tokens=100
        )
        reply = response['choices'][0]['message']['content']
        bot.reply_to(message, reply)
    except Exception as e:
        print(f"Ошибка: {e}")
        bot.reply_to(message, "Что-то пошло не так, командир... Попробуй позже.")

bot.polling()