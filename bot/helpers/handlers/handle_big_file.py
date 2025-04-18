from aiogram import Bot
from aiogram.types import Update

from bot.config import MessageSticker, config
from bot.database.operations.user.getters import get_user
from bot.locales.main import get_localization


async def handle_big_file(bot: Bot, telegram_update: Update):
    user_id = None
    if telegram_update.callback_query and telegram_update.callback_query.from_user.id:
        user_id = str(telegram_update.callback_query.from_user.id)
    elif telegram_update.message and telegram_update.message.from_user.id:
        user_id = str(telegram_update.message.from_user.id)

    if user_id:
        user = await get_user(user_id)

        await bot.send_sticker(
            chat_id=user.telegram_chat_id,
            sticker=config.MESSAGE_STICKERS.get(MessageSticker.FEAR),
        )
        await bot.send_message(
            chat_id=user.telegram_chat_id,
            text=get_localization(user.interface_language_code).ERROR_FILE_TOO_BIG,
        )
