from aiogram.fsm.context import FSMContext
from aiogram.types import Message

from bot.config import config
from bot.locales.main import get_localization, get_user_language


async def is_already_processing(
    message: Message, state: FSMContext, current_time: float
):
    user_data = await state.get_data()
    user_language_code = await get_user_language(str(message.chat.id), state.storage)
    is_processing = user_data.get("is_processing")

    if not is_processing:
        return False

    last_request_time = user_data.get("last_request_time")
    if last_request_time is None:
        await state.update_data(is_processing=False)
        return False

    time_elapsed = current_time - last_request_time
    if time_elapsed >= config.LIMIT_PROCESSING_SECONDS:
        await state.update_data(is_processing=False)
        return False

    await message.reply(
        text=get_localization(user_language_code).MODEL_ALREADY_MAKE_REQUEST,
        allow_sending_without_reply=True,
    )
    return True
