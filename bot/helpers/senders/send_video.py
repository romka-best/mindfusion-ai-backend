import logging

from aiogram import Bot
from aiogram.exceptions import TelegramForbiddenError
from aiogram.types import URLInputFile

from bot.database.operations.user.updaters import update_user
from bot.helpers.senders.send_message_to_admins import send_message_to_admins


async def send_video(
    bot: Bot,
    chat_id: str,
    result: str,
    caption: str,
    filename: str,
    duration: int,
    reply_markup=None,
    reply_to_message_id=None,
):
    try:
        await bot.send_video(
            chat_id=chat_id,
            video=URLInputFile(result, filename=filename, timeout=60),
            caption=caption,
            duration=duration,
            reply_markup=reply_markup,
            reply_to_message_id=reply_to_message_id,
        )
    except TelegramForbiddenError:
        await update_user(chat_id, {
            "is_blocked": True,
        })
    except Exception as e:
        logging.error(f'Error in send_video: {e}')
        await send_message_to_admins(
            bot=bot,
            message=f"#error\n\nALARM! Ошибка при отправке видео у пользователя: {chat_id}\n"
                    f"Информация:\n{e}",
            parse_mode=None,
        )
