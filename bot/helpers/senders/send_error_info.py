from aiogram import Bot

from bot.helpers.senders.send_message_to_admins_and_developers import (
    send_message_to_admins_and_developers,
)


async def send_error_info(
    bot: Bot, user_id: str, info: str, hashtags: list[str] = None
):
    if hashtags is None:
        hashtags = []

    message = f"""
#error {"#" if len(hashtags) > 0 else ""}{" #".join(hashtags)}

ALARM! Ошибка у пользователя: {user_id}
Информация:
{info}
"""
    await send_message_to_admins_and_developers(
        bot=bot,
        message=message,
        parse_mode=None,
    )
