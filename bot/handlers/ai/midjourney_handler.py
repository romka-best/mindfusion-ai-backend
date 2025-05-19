import logging
from contextlib import AsyncExitStack
from datetime import datetime, timezone
from typing import Optional

from aiogram import Router
from aiogram.exceptions import TelegramBadRequest, TelegramRetryAfter
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message
from aiogram.utils.chat_action import ChatActionSender
from aiohttp import ClientResponseError

from bot.config import MessageEffect, MessageSticker, config
from bot.database.main import firebase
from bot.database.models.common import MidjourneyAction, MidjourneyVersion, Model, Quota
from bot.database.models.user import User, UserSettings
from bot.database.operations.generation.getters import get_generation
from bot.database.operations.generation.writers import write_generation
from bot.database.operations.product.getters import get_product_by_quota
from bot.database.operations.request.getters import get_started_requests_by_user_id_and_product_id
from bot.database.operations.user.getters import get_user
from bot.database.operations.user.updaters import update_user
from bot.helpers import midjourney as midjourney_helper
from bot.helpers.getters.get_quota_by_model import get_quota_by_model
from bot.helpers.getters.get_switched_to_ai_model import get_switched_to_ai_model
from bot.helpers.senders.send_ai_model_internal_error import send_internal_ai_model_error
from bot.helpers.senders.send_error_info import send_error_info
from bot.integrations.midjourney import (
    create_different_midjourney_image,
    create_different_midjourney_images,
    create_midjourney_image,
    create_midjourney_images,
)
from bot.keyboards.ai.model import build_model_limit_exceeded_keyboard, build_switched_to_ai_keyboard
from bot.keyboards.common.common import build_error_keyboard
from bot.locales.main import get_localization, get_user_language
from bot.locales.translate_text import translate_text
from bot.locales.types import LanguageCode
from bot.utils.ctx_managers.generation_record_ctx import GenerationRecordCtx
from bot.utils.ctx_managers.processing_msgs_ctx import ProcessingMsgsCtx
from bot.utils.ctx_managers.request_record_ctx import RequestRecordCtx

midjourney_router = Router()


@midjourney_router.message(Command('midjourney'))
async def midjourney(message: Message, state: FSMContext):
    await state.clear()

    user_id = str(message.from_user.id)
    user = await get_user(user_id)
    user_language_code = await get_user_language(user_id, state.storage)

    if user.current_model == Model.MIDJOURNEY:
        await message.answer(
            text=get_localization(user_language_code).MODEL_ALREADY_SWITCHED_TO_THIS_MODEL,
            reply_markup=build_switched_to_ai_keyboard(user_language_code, Model.MIDJOURNEY),
        )
    else:
        user.current_model = Model.MIDJOURNEY
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
            reply_markup=build_switched_to_ai_keyboard(user_language_code, Model.MIDJOURNEY),
            message_effect_id=config.MESSAGE_EFFECTS.get(MessageEffect.FIRE),
        )

        try:
            await message.bot.unpin_all_chat_messages(user.telegram_chat_id)
            await message.bot.pin_chat_message(user.telegram_chat_id, answered_message.message_id)
        except (TelegramBadRequest, TelegramRetryAfter):
            pass


async def handle_midjourney(
    message: Message,
    state: FSMContext,
    user: User,
    prompt: str,
    action: MidjourneyAction,
    hash_id="",
    choice=0,
    image_filename: Optional[str] = None,
):
    # Params
    user_language_code = await get_user_language(user.id, state.storage)

    # Prepare prompt
    prompt = midjourney_helper.prompt.Parser().parse(prompt)

    if image_filename:
        image_path = f"users/vision/{user.id}/{image_filename}"
        image = await firebase.bucket.get_blob(image_path)
        image_link = firebase.get_public_url(image.name)
        prompt.reference_images += image_link

    if prompt.params.version == midjourney_helper.prompt.NullParameter:
        prompt.params["version"] = user.settings[Model.MIDJOURNEY][UserSettings.VERSION]
    if prompt.params.aspect == midjourney_helper.prompt.NullParameter:
        prompt.params["aspect"] = user.settings[Model.MIDJOURNEY][UserSettings.ASPECT_RATIO]

    midjourney_helper.prompt.RemoveUnsupportedParams.execute(prompt)

    # Validation
    quota = user.daily_limits[Quota.MIDJOURNEY] + user.additional_usage_quota[Quota.MIDJOURNEY]
    if quota < 1 and action != MidjourneyAction.UPSCALE:
        await message.answer_sticker(
            sticker=config.MESSAGE_STICKERS.get(MessageSticker.SAD),
        )
        return await message.reply(
            text=get_localization(user_language_code).model_reached_usage_limit(),
            reply_markup=build_model_limit_exceeded_keyboard(user_language_code, user.had_subscription),
            allow_sending_without_reply=True,
        )

    product = await get_product_by_quota(Quota.MIDJOURNEY)
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
                    config.MESSAGE_STICKERS.get(MessageSticker.IMAGE_GENERATION),
                    get_localization(user_language_code).model_image_processing_request(),
                ),
            )
            request_record_ctx = await stack.enter_async_context(
                RequestRecordCtx(
                    user_id=user.id,
                    processing_message_ids=processing_msgs_ctx.ids,
                    product_id=product.id,
                    requested=1,
                    details={
                        "prompt": str(prompt),
                        "action": action,
                        "version": prompt.params.version,
                        "is_suggestion": False,
                    },
                ),
            )
            gen_ctx = await stack.enter_async_context(GenerationRecordCtx())

            # Translate
            if user_language_code != LanguageCode.EN:
                prompt.text = await translate_text(prompt.text, user_language_code, LanguageCode.EN)

            # Generation
            match action:
                case MidjourneyAction.UPSCALE:
                    result_id = await create_midjourney_image(hash_id, choice)
                case MidjourneyAction.VARIATION:
                    result_id = await create_different_midjourney_image(hash_id, choice)
                case MidjourneyAction.REROLL:
                    result_id = await create_different_midjourney_images(hash_id)
                case _:
                    result_id = await create_midjourney_images(
                        str(prompt), "turbo" if prompt.params.version == MidjourneyVersion.V7 else "fast",
                    )

            gen_ctx.add(
                await write_generation(
                    id=result_id,
                    request_id=request_record_ctx.request.id,
                    product_id=product.id,
                    has_error=result_id is None,
                    details={
                        "prompt": str(prompt),
                        "action": action,
                        "version": prompt.params.version,
                        "is_suggestion": False,
                    },
                ),
            )
    except ClientResponseError as e:
        if e.status == 500:
            if "Invalid Param Value" in e.payload.get("data", {}).get("error", {}).get("raw_message", ""):
                await message.answer(
                    text=get_localization(user_language_code).midjourney_params_error(
                        str(prompt),
                        e.payload["data"]["error"]["raw_message"].split(":", 1)[-1],
                    ),
                )
            else:
                await send_internal_ai_model_error(user_language_code, message, Model.MIDJOURNEY)
        else:
            raise
    except Exception as e:
        logging.exception("")

        if action == MidjourneyAction.IMAGINE:
            await message.answer_sticker(
                sticker=config.MESSAGE_STICKERS.get(MessageSticker.FEAR),
            )
            await message.answer(
                text=get_localization(user_language_code).ERROR_REQUEST_FORBIDDEN,
            )
        elif action == MidjourneyAction.UPSCALE:
            await message.answer(
                text=get_localization(user_language_code).MIDJOURNEY_ALREADY_CHOSE_UPSCALE,
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
                hashtags=["midjourney"],
            )


@midjourney_router.callback_query(lambda c: c.data.startswith('midjourney:'))
async def handle_midjourney_selection(callback_query: CallbackQuery, state: FSMContext):
    await callback_query.answer()

    user_id = str(callback_query.from_user.id)
    user = await get_user(user_id)

    action = callback_query.data.split(':')[1]
    hash_id = callback_query.data.split(':')[2]

    generation = await get_generation(hash_id)

    if action.startswith('u'):
        choice = int(action[1:])
        await handle_midjourney(
            callback_query.message,
            state,
            user,
            generation.details.get('prompt'),
            MidjourneyAction.UPSCALE,
            hash_id,
            choice,
        )
    elif action.startswith('v'):
        choice = int(action[1:])
        await handle_midjourney(
            callback_query.message,
            state,
            user,
            generation.details.get('prompt'),
            MidjourneyAction.VARIATION,
            hash_id,
            choice,
        )
    elif action == 'again':
        await handle_midjourney(
            callback_query.message,
            state,
            user,
            generation.details.get('prompt'),
            MidjourneyAction.REROLL,
            hash_id,
        )

    await state.clear()


async def handle_midjourney_example(user: User, user_language_code: LanguageCode, prompt: str, message: Message):
    # Validation
    current_date = datetime.now(timezone.utc)
    if not (
        not user.subscription_id
        and user.current_model == Model.LUMA_PHOTON
        and user.settings[user.current_model][UserSettings.SHOW_EXAMPLES]
        and user.daily_limits[Quota.LUMA_PHOTON] in [1]
        and (current_date - user.last_subscription_limit_update).days <= 3
    ):
        return

    # Prepare prompt
    prompt = midjourney_helper.prompt.Parser().parse(prompt)

    if prompt.params.version == midjourney_helper.prompt.NullParameter:
        prompt.params["version"] = user.settings[Model.MIDJOURNEY][UserSettings.VERSION]
    if prompt.params.aspect == midjourney_helper.prompt.NullParameter:
        prompt.params["aspect"] = user.settings[Model.MIDJOURNEY][UserSettings.ASPECT_RATIO]

    midjourney_helper.prompt.RemoveUnsupportedParams.execute(prompt)

    # Generation
    product = await get_product_by_quota(Quota.MIDJOURNEY)
    try:
        async with AsyncExitStack() as stack:
            # Prepare ctxs
            request_record_ctx = await stack.enter_async_context(
                RequestRecordCtx(
                    user_id=user.id,
                    processing_message_ids=[message.message_id],
                    product_id=product.id,
                    requested=1,
                    details={
                        "prompt": str(prompt),
                        "action": MidjourneyAction.IMAGINE,
                        "version": prompt.params.version,
                        "is_suggestion": True,
                    },
                ),
            )
            gen_ctx = await stack.enter_async_context(GenerationRecordCtx())

        # Translate
        if user_language_code != LanguageCode.EN:
            prompt.text = await translate_text(prompt.text, user_language_code, LanguageCode.EN)

        # Send generation
        result_id = await create_midjourney_images(str(prompt), "fast")

        gen_ctx.add(
            await write_generation(
                id=result_id,
                request_id=request_record_ctx.request.id,
                product_id=product.id,
                has_error=result_id is None,
                details={
                    "prompt": str(prompt),
                    "action": MidjourneyAction.IMAGINE,
                    "version": prompt.params.version,
                    "is_suggestion": True,
                },
            ),
        )
    except Exception as e:
        logging.exception("")

        await send_error_info(
            bot=message.bot,
            user_id=user.id,
            info=str(e),
            hashtags=["midjourney", "example"],
        )
