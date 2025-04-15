from aiogram.types import Message
from bot.config import config, MessageSticker
from .types import LanguageCode, get_localization


async def send_internal_ai_model_error(
    lang_code: LanguageCode, message: Message, ai_model_name: str
):
    await message.answer_sticker(
        sticker=config.MESSAGE_STICKERS.get(MessageSticker.ERROR),
    )

    await message.answer(
        text=get_localization(
            lang_code).error_internal_ai_model(ai_model_name),
    )
