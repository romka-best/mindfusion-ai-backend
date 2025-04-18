from typing import Optional

from aiogram import Router
from aiogram.exceptions import TelegramBadRequest, TelegramRetryAfter
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.types import Message
from aiogram.utils.chat_action import ChatActionSender

from bot.config import MessageEffect, MessageSticker, config
from bot.database.models.common import Model, Quota
from bot.database.models.generation import GenerationStatus
from bot.database.models.request import RequestStatus
from bot.database.models.user import User, UserSettings
from bot.database.operations.generation.getters import get_generations_by_request_id
from bot.database.operations.generation.updaters import update_generation
from bot.database.operations.generation.writers import write_generation
from bot.database.operations.product.getters import get_product_by_quota
from bot.database.operations.request.getters import (
    get_started_requests_by_user_id_and_product_id,
)
from bot.database.operations.request.updaters import update_request
from bot.database.operations.request.writers import write_request
from bot.database.operations.user.getters import get_user
from bot.database.operations.user.updaters import update_user
from bot.helpers.getters.get_quota_by_model import get_quota_by_model
from bot.helpers.getters.get_switched_to_ai_model import get_switched_to_ai_model
from bot.helpers.senders.send_error_info import send_error_info
from bot.integrations.kling import generate_video
from bot.keyboards.ai.model import build_switched_to_ai_keyboard
from bot.keyboards.common.common import build_error_keyboard
from bot.locales.main import get_localization, get_user_language
from bot.locales.translate_text import translate_text
from bot.locales.types import LanguageCode

kling_router = Router()


@kling_router.message(Command("kling"))
async def kling(message: Message, state: FSMContext):
    await state.clear()

    user_id = str(message.from_user.id)
    user = await get_user(user_id)
    user_language_code = await get_user_language(user_id, state.storage)

    if user.current_model == Model.KLING:
        await message.answer(
            text=get_localization(
                user_language_code
            ).MODEL_ALREADY_SWITCHED_TO_THIS_MODEL,
            reply_markup=build_switched_to_ai_keyboard(user_language_code, Model.KLING),
        )
    else:
        user.current_model = Model.KLING
        await update_user(
            user_id,
            {
                "current_model": user.current_model,
            },
        )

        text = await get_switched_to_ai_model(
            user,
            get_quota_by_model(
                user.current_model,
                user.settings[user.current_model][UserSettings.VERSION],
            ),
            user_language_code,
        )
        answered_message = await message.answer(
            text=text,
            reply_markup=build_switched_to_ai_keyboard(user_language_code, Model.KLING),
            message_effect_id=config.MESSAGE_EFFECTS.get(MessageEffect.FIRE),
        )

        try:
            await message.bot.unpin_all_chat_messages(user.telegram_chat_id)
            await message.bot.pin_chat_message(
                user.telegram_chat_id, answered_message.message_id
            )
        except (TelegramBadRequest, TelegramRetryAfter):
            pass


async def handle_kling(
    message: Message,
    state: FSMContext,
    user: User,
    video_frame_link: Optional[str] = None,
):
    user_language_code = await get_user_language(user.id, state.storage)
    user_data = await state.get_data()

    prompt = user_data.get("recognized_text", "")
    if not prompt:
        if message.caption:
            prompt = message.caption
        elif message.text:
            prompt = message.text
        else:
            prompt = ""

    processing_sticker = await message.answer_sticker(
        sticker=config.MESSAGE_STICKERS.get(MessageSticker.VIDEO_GENERATION),
    )
    processing_message = await message.reply(
        text=get_localization(user_language_code).model_video_processing_request(),
        allow_sending_without_reply=True,
    )

    async with ChatActionSender.upload_video(bot=message.bot, chat_id=message.chat.id):
        product = await get_product_by_quota(Quota.KLING)

        user_not_finished_requests = (
            await get_started_requests_by_user_id_and_product_id(user.id, product.id)
        )

        if len(user_not_finished_requests):
            await message.reply(
                text=get_localization(user_language_code).MODEL_ALREADY_MAKE_REQUEST,
                allow_sending_without_reply=True,
            )

            await processing_sticker.delete()
            await processing_message.delete()
            return

        request = await write_request(
            user_id=user.id,
            processing_message_ids=[
                processing_sticker.message_id,
                processing_message.message_id,
            ],
            product_id=product.id,
            requested=1,
        )

        try:
            if prompt and user_language_code != LanguageCode.EN:
                prompt = await translate_text(
                    prompt, user_language_code, LanguageCode.EN
                )
            result_id = await generate_video(
                prompt,
                user.settings[Model.KLING][UserSettings.VERSION],
                user.settings[Model.KLING][UserSettings.MODE],
                user.settings[Model.KLING][UserSettings.DURATION],
                user.settings[Model.KLING][UserSettings.ASPECT_RATIO],
                video_frame_link,
            )

            await write_generation(
                id=result_id,
                request_id=request.id,
                product_id=product.id,
                has_error=result_id is None,
                details={
                    "prompt": prompt,
                    "version": user.settings[Model.KLING][UserSettings.VERSION],
                    "mode": user.settings[Model.KLING][UserSettings.MODE],
                    "duration": user.settings[Model.KLING][UserSettings.DURATION],
                    "aspect_ratio": user.settings[Model.KLING][
                        UserSettings.ASPECT_RATIO
                    ],
                    "video_first_frame_link": video_frame_link,
                },
            )
        except Exception as e:
            if "the prompt contains sensitive words" in str(e).lower():
                await message.answer_sticker(
                    sticker=config.MESSAGE_STICKERS.get(MessageSticker.FEAR),
                )
                await message.reply(
                    text=get_localization(user_language_code).ERROR_REQUEST_FORBIDDEN,
                    allow_sending_without_reply=True,
                )
            elif "too many requests" in str(e).lower():
                await message.answer(
                    text=get_localization(user_language_code).ERROR_SERVER_OVERLOADED,
                    allow_sending_without_reply=True,
                )
            else:
                await message.answer_sticker(
                    sticker=config.MESSAGE_STICKERS.get(MessageSticker.ERROR),
                )

                await message.answer(
                    text=get_localization(user_language_code).ERROR,
                    reply_markup=build_error_keyboard(user_language_code),
                )
                await send_error_info(
                    bot=message.bot,
                    user_id=user.id,
                    info=str(e),
                    hashtags=["kling"],
                )

            request.status = RequestStatus.FINISHED
            await update_request(request.id, {"status": request.status})

            generations = await get_generations_by_request_id(request.id)
            for generation in generations:
                generation.status = GenerationStatus.FINISHED
                generation.has_error = True
                await update_generation(
                    generation.id,
                    {
                        "status": generation.status,
                        "has_error": generation.has_error,
                    },
                )

            await processing_sticker.delete()
            await processing_message.delete()
