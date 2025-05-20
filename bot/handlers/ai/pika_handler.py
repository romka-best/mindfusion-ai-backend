from contextlib import AsyncExitStack
from typing import Optional

import aiohttp
from aiogram import Router
from aiogram.exceptions import TelegramBadRequest, TelegramRetryAfter
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.types import Message
from aiogram.utils.chat_action import ChatActionSender

from bot.config import config, MessageEffect, MessageSticker
from bot.database.models.common import Model, Quota
from bot.database.models.generation import GenerationStatus
from bot.database.models.request import RequestStatus
from bot.database.models.user import User, UserSettings
from bot.database.operations.generation.getters import get_generations_by_request_id
from bot.database.operations.generation.updaters import update_generation
from bot.database.operations.generation.writers import write_generation
from bot.database.operations.product.getters import get_product_by_quota
from bot.database.operations.request.getters import get_started_requests_by_user_id_and_product_id
from bot.database.operations.request.updaters import update_request
from bot.database.operations.request.writers import write_request
from bot.database.operations.user.getters import get_user
from bot.database.operations.user.updaters import update_user
from bot.helpers.getters.get_quota_by_model import get_quota_by_model
from bot.helpers.getters.get_switched_to_ai_model import get_switched_to_ai_model
from bot.integrations.pika import generate_video
from bot.keyboards.ai.model import build_switched_to_ai_keyboard
from bot.keyboards.common.common import build_error_keyboard
from bot.locales.main import get_user_language, get_localization
from bot.locales.translate_text import translate_text
from bot.locales.types import LanguageCode
from bot.helpers.senders.send_ai_model_internal_error import send_internal_ai_model_error
from bot.helpers.notifiers.notify_error_channel import notify_error_channel
import traceback

from bot.utils.ctx_managers.generation_record_ctx import GenerationRecordCtx
from bot.utils.ctx_managers.processing_msgs_ctx import ProcessingMsgsCtx
from bot.utils.ctx_managers.request_record_ctx import RequestRecordCtx


pika_router = Router()

PRICE_PIKA = 0.06


@pika_router.message(Command('pika'))
async def pika(message: Message, state: FSMContext):
    await state.clear()

    user_id = str(message.from_user.id)
    user = await get_user(user_id)
    user_language_code = await get_user_language(user_id, state.storage)

    if user.current_model == Model.PIKA:
        await message.answer(
            text=get_localization(user_language_code).MODEL_ALREADY_SWITCHED_TO_THIS_MODEL,
            reply_markup=build_switched_to_ai_keyboard(user_language_code, Model.PIKA),
        )
    else:
        user.current_model = Model.PIKA
        await update_user(user_id, {
            'current_model': user.current_model,
        })

        text = await get_switched_to_ai_model(
            user,
            get_quota_by_model(user.current_model, user.settings[user.current_model][UserSettings.VERSION]),
            user_language_code,
        )
        answered_message = await message.answer(
            text=text,
            reply_markup=build_switched_to_ai_keyboard(user_language_code, Model.PIKA),
            message_effect_id=config.MESSAGE_EFFECTS.get(MessageEffect.FIRE),
        )

        try:
            await message.bot.unpin_all_chat_messages(user.telegram_chat_id)
            await message.bot.pin_chat_message(user.telegram_chat_id, answered_message.message_id)
        except (TelegramBadRequest, TelegramRetryAfter):
            pass

async def handle_pika(
    message: Message,
    state: FSMContext,
    user: User,
    video_frame_link: Optional[str] = None,
):
    # Params
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

    # Validation
    product = await get_product_by_quota(Quota.PIKA)
    user_not_finished_requests = await get_started_requests_by_user_id_and_product_id(user.id, product.id)
    if len(user_not_finished_requests):
        return await message.reply(
            text=get_localization(user_language_code).MODEL_ALREADY_MAKE_REQUEST,
            allow_sending_without_reply=True,
        )

    # Generation
    try:
        async with AsyncExitStack() as stack:
            # Prepare ctxs
            await stack.enter_async_context(ChatActionSender.upload_photo(bot=message.bot, chat_id=message.chat.id))
            processing_msgs_ctx = await stack.enter_async_context(
                ProcessingMsgsCtx(
                    message,
                    config.MESSAGE_STICKERS.get(MessageSticker.VIDEO_GENERATION),
                    get_localization(user_language_code).model_video_processing_request(),
                ),
            )
            request_record_ctx = await stack.enter_async_context(
                RequestRecordCtx(
                    user_id=user.id,
                    processing_message_ids=processing_msgs_ctx.ids,
                    product_id=product.id,
                    requested=1,
                ),
            )
            gen_ctx = await stack.enter_async_context(GenerationRecordCtx())

            # Translate
            if prompt and user_language_code != LanguageCode.EN:
                prompt = await translate_text(prompt, user_language_code, LanguageCode.EN)

            # Send generation
            result_id = await generate_video(
                prompt,
                user.settings[Model.PIKA][UserSettings.VERSION],
                user.settings[Model.PIKA][UserSettings.ASPECT_RATIO],
                video_frame_link,
            )

            gen_ctx.add(
                await write_generation(
                    id=result_id,
                    request_id=request_record_ctx.request.id,
                    product_id=product.id,
                    has_error=result_id is None,
                    details={
                        "prompt": prompt,
                        "version": user.settings[Model.PIKA][UserSettings.VERSION],
                        "aspect_ratio": user.settings[Model.PIKA][UserSettings.ASPECT_RATIO],
                        "video_first_frame_link": video_frame_link,
                    },
                ),
            )
    except aiohttp.ClientResponseError as e:
        if e.status == 500:
            await send_internal_ai_model_error(user_language_code, message, Model.PIKA)
        else:
            raise
    except Exception as e:
        await message.answer_sticker(
            sticker=config.MESSAGE_STICKERS.get(MessageSticker.ERROR),
        )

        await message.answer(
            text=get_localization(user_language_code).ERROR,
            reply_markup=build_error_keyboard(user_language_code),
        )

        await notify_error_channel(
            bot=message.bot,
            user_id=user.id,
            info=str(e),
            stack_trace=traceback.format_exc(),
            context={"prompt": prompt},
            hashtags=["pika"],
        )
