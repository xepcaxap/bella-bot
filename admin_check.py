from functools import wraps
from telegram import ChatMember

def admin_only(func):
    @wraps(func)
    async def wrapper(update, context, *args, **kwargs):
        user_id = update.effective_user.id
        chat_id = update.effective_chat.id
        member = await context.bot.get_chat_member(chat_id, user_id)

        if member.status not in [ChatMember.ADMINISTRATOR, ChatMember.OWNER]:
            await update.message.reply_text("Ты не админ, командир. Без доступа.")
            return
        return await func(update, context, *args, **kwargs)
    return wrapper
