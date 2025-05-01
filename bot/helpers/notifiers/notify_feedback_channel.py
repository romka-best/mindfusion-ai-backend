import asyncio
from aiogram.exceptions import TelegramRetryAfter
from bot.config import config

async def notify_feedback_channel(bot, user_id, feedback_text, retry_after=0):
    if retry_after:
        await asyncio.sleep(retry_after)

    try:
        await bot.send_message(
            chat_id=config.ALERT_CHANELS["FEEDBACK"],
            text=f"""
#feedback
🚀 <b>Новая обратная связь от пользователя</b>: {user_id} 🚀
<code>{feedback_text}</code>
""")
    except TelegramRetryAfter as e:
        asyncio.create_task(
                notify_feedback_channel(
                    bot,
                    user_id,
                    feedback_text,
                    e.retry_after + 30
                )
        )


