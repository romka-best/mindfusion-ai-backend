from aiogram import F, Router
from aiogram.fsm.context import FSMContext
from aiogram.types import Message

from bot.locales.main import get_localization, get_user_language

sticker_router = Router()


@sticker_router.message(F.sticker)
async def sticker(message: Message, state: FSMContext):
    user_id = str(message.from_user.id)
    user_language_code = await get_user_language(user_id, state.storage)

    await message.reply(
        text=get_localization(user_language_code).ERROR_STICKER_FORBIDDEN,
        allow_sending_without_reply=True,
    )
