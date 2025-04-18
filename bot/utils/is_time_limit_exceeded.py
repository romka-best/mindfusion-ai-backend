import asyncio

from aiogram import Bot
from aiogram.fsm.context import FSMContext
from aiogram.types import Message

from bot.config import config
from bot.database.models.common import Model, Quota
from bot.database.models.user import User
from bot.keyboards.common.common import build_time_limit_exceeded_keyboard
from bot.locales.main import get_localization, get_user_language
from bot.locales.types import LanguageCode


async def notify_user_after_timeout(
    bot: Bot,
    chat_id: int,
    delay: int,
    language_code: LanguageCode,
    reply_to_message_id: int,
):
    await asyncio.sleep(delay)

    await bot.send_message(
        chat_id=chat_id,
        text=get_localization(language_code).MODEL_READY_FOR_NEW_REQUEST,
        reply_to_message_id=reply_to_message_id,
        allow_sending_without_reply=True,
    )


async def is_time_limit_exceeded(
    message: Message, state: FSMContext, user: User, current_time: float
) -> bool:
    if (
        user.daily_limits[Quota.FAST_MESSAGES]
        or user.additional_usage_quota[Quota.FAST_MESSAGES]
        or user.current_model == Model.FACE_SWAP
        or user.current_model == Model.PHOTOSHOP_AI
        or user.current_model == Model.MUSIC_GEN
        or user.current_model == Model.SUNO
    ):
        return False

    user_data = await state.get_data()
    user_language_code = await get_user_language(str(message.chat.id), state.storage)
    last_request_time = user_data.get("last_request_time", 0.0)

    if not last_request_time:
        return False

    time_elapsed = current_time - last_request_time
    if time_elapsed >= config.LIMIT_BETWEEN_REQUESTS_SECONDS:
        await state.clear()
        return False

    remaining_time = int(config.LIMIT_BETWEEN_REQUESTS_SECONDS - time_elapsed)
    if user_data.get("additional_request_made"):
        text = get_localization(user_language_code).MODEL_ALREADY_MAKE_REQUEST
        await message.reply(
            text=text,
            allow_sending_without_reply=True,
        )
    else:
        await state.update_data(additional_request_made=True)

        await message.reply(
            text=get_localization(user_language_code).model_wait_for_another_request(
                remaining_time
            ),
            reply_markup=build_time_limit_exceeded_keyboard(user_language_code),
            allow_sending_without_reply=True,
        )
        asyncio.create_task(
            notify_user_after_timeout(
                bot=message.bot,
                chat_id=message.chat.id,
                delay=remaining_time,
                language_code=user_language_code,
                reply_to_message_id=message.message_id,
            )
        )
    return True
