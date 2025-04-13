import asyncio
from typing import Optional

from aiogram import Router
from aiogram.exceptions import TelegramBadRequest, TelegramRetryAfter
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.types import Message
from aiogram.utils.chat_action import ChatActionSender

from bot.config import config, MessageEffect, MessageSticker
from bot.database.main import firebase
from bot.database.models.common import Model, Quota
from bot.database.models.generation import GenerationStatus
from bot.database.models.request import RequestStatus
from bot.database.models.user import UserSettings, User
from bot.database.operations.generation.getters import get_generations_by_request_id
from bot.database.operations.generation.updaters import update_generation
from bot.database.operations.generation.writers import write_generation
from bot.database.operations.product.getters import get_product_by_quota
from bot.database.operations.request.getters import get_started_requests_by_user_id_and_product_id
from bot.database.operations.request.updaters import update_request
from bot.database.operations.request.writers import write_request
from bot.database.operations.user.getters import get_user
from bot.database.operations.user.updaters import update_user
from bot.handlers.ai.midjourney_handler import handle_midjourney_example
from bot.helpers.getters.get_quota_by_model import get_quota_by_model
from bot.helpers.getters.get_switched_to_ai_model import get_switched_to_ai_model
from bot.helpers.senders.send_error_info import send_error_info
from bot.integrations.luma import get_response_image, get_response_video
from bot.keyboards.ai.model import build_switched_to_ai_keyboard
from bot.keyboards.common.common import build_error_keyboard
from bot.locales.main import get_user_language, get_localization
from bot.locales.translate_text import translate_text
from bot.locales.types import LanguageCode

luma_router = Router()

PRICE_LUMA_PHOTON = 0.016
PRICE_LUMA_RAY = 0.4


@luma_router.message(Command('luma_photon'))
async def luma_photon(message: Message, state: FSMContext):
    await state.clear()

    user_id = str(message.from_user.id)
    user = await get_user(user_id)
    user_language_code = await get_user_language(user_id, state.storage)

    if user.current_model == Model.LUMA_PHOTON:
        await message.answer(
            text=get_localization(user_language_code).MODEL_ALREADY_SWITCHED_TO_THIS_MODEL,
            reply_markup=build_switched_to_ai_keyboard(user_language_code, Model.LUMA_PHOTON),
        )
    else:
        user.current_model = Model.LUMA_PHOTON
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
            reply_markup=build_switched_to_ai_keyboard(user_language_code, Model.LUMA_PHOTON),
            message_effect_id=config.MESSAGE_EFFECTS.get(MessageEffect.FIRE),
        )

        try:
            await message.bot.unpin_all_chat_messages(user.telegram_chat_id)
            await message.bot.pin_chat_message(user.telegram_chat_id, answered_message.message_id)
        except (TelegramBadRequest, TelegramRetryAfter):
            pass


async def handle_luma_photon(
    message: Message,
    state: FSMContext,
    user: User,
    image_filename: Optional[str] = None,
):
    user_language_code = await get_user_language(user.id, state.storage)
    user_data = await state.get_data()

    prompt = user_data.get('recognized_text', None)
    if prompt is None:
        if message.caption:
            prompt = message.caption
        elif message.text:
            prompt = message.text
        else:
            prompt = ''

    if not prompt or len(prompt) <= 3:
        await message.reply(
            text=get_localization(user_language_code).ERROR_PROMPT_REQUIRED,
            allow_sending_without_reply=True,
        )
        return

    image_link = None
    if image_filename:
        image_path = f'users/vision/{user.id}/{image_filename}'
        image = await firebase.bucket.get_blob(image_path)
        image_link = firebase.get_public_url(image.name)

    processing_sticker = await message.answer_sticker(
        sticker=config.MESSAGE_STICKERS.get(MessageSticker.IMAGE_GENERATION),
    )
    processing_message = await message.reply(
        text=get_localization(user_language_code).model_image_processing_request(),
        allow_sending_without_reply=True,
    )

    async with ChatActionSender.upload_photo(bot=message.bot, chat_id=message.chat.id):
        product = await get_product_by_quota(Quota.LUMA_PHOTON)

        user_not_finished_requests = await get_started_requests_by_user_id_and_product_id(user.id, product.id)

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
            processing_message_ids=[processing_sticker.message_id, processing_message.message_id],
            product_id=product.id,
            requested=1,
        )

        try:
            if prompt and user_language_code != LanguageCode.EN:
                prompt = await translate_text(prompt, user_language_code, LanguageCode.EN)
            result_id = await get_response_image(
                prompt,
                user.settings[Model.LUMA_PHOTON][UserSettings.ASPECT_RATIO],
                image_link,
            )

            await write_generation(
                id=result_id,
                request_id=request.id,
                product_id=product.id,
                has_error=result_id is None,
                details={
                    'prompt': prompt,
                }
            )
        except Exception as e:
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
                hashtags=['luma_photon'],
            )

            request.status = RequestStatus.FINISHED
            await update_request(request.id, {
                'status': request.status
            })

            generations = await get_generations_by_request_id(request.id)
            for generation in generations:
                generation.status = GenerationStatus.FINISHED
                generation.has_error = True
                await update_generation(
                    generation.id,
                    {
                        'status': generation.status,
                        'has_error': generation.has_error,
                    },
                )

            await processing_sticker.delete()
            await processing_message.delete()

        asyncio.create_task(
            handle_midjourney_example(
                user=user,
                user_language_code=user_language_code,
                prompt=prompt,
                message=message,
            )
        )


@luma_router.message(Command('luma_ray'))
async def luma_ray(message: Message, state: FSMContext):
    await state.clear()

    user_id = str(message.from_user.id)
    user = await get_user(user_id)
    user_language_code = await get_user_language(user_id, state.storage)

    if user.current_model == Model.LUMA_RAY:
        await message.answer(
            text=get_localization(user_language_code).MODEL_ALREADY_SWITCHED_TO_THIS_MODEL,
            reply_markup=build_switched_to_ai_keyboard(user_language_code, Model.LUMA_RAY),
        )
    else:
        user.current_model = Model.LUMA_RAY
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
            reply_markup=build_switched_to_ai_keyboard(user_language_code, Model.LUMA_RAY),
            message_effect_id=config.MESSAGE_EFFECTS.get(MessageEffect.FIRE),
        )

        try:
            await message.bot.unpin_all_chat_messages(user.telegram_chat_id)
            await message.bot.pin_chat_message(user.telegram_chat_id, answered_message.message_id)
        except (TelegramBadRequest, TelegramRetryAfter):
            pass


async def handle_luma_ray(
    message: Message,
    state: FSMContext,
    user: User,
    video_frame_link: Optional[str] = None
):
    user_language_code = await get_user_language(user.id, state.storage)
    user_data = await state.get_data()

    prompt = user_data.get('recognized_text', '')
    if not prompt:
        if message.caption:
            prompt = message.caption
        elif message.text:
            prompt = message.text
        else:
            prompt = ''

    processing_sticker = await message.answer_sticker(
        sticker=config.MESSAGE_STICKERS.get(MessageSticker.VIDEO_GENERATION),
    )
    processing_message = await message.reply(
        text=get_localization(user_language_code).model_video_processing_request(),
        allow_sending_without_reply=True,
    )

    async with ChatActionSender.upload_video(bot=message.bot, chat_id=message.chat.id):
        product = await get_product_by_quota(Quota.LUMA_RAY)

        user_not_finished_requests = await get_started_requests_by_user_id_and_product_id(user.id, product.id)

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
            processing_message_ids=[processing_sticker.message_id, processing_message.message_id],
            product_id=product.id,
            requested=1,
        )

        try:
            if prompt and user_language_code != LanguageCode.EN:
                prompt = await translate_text(prompt, user_language_code, LanguageCode.EN)
            result_id = await get_response_video(
                prompt,
                user.settings[Model.LUMA_RAY][UserSettings.VERSION],
                user.settings[Model.LUMA_RAY][UserSettings.ASPECT_RATIO],
                user.settings[Model.LUMA_RAY][UserSettings.DURATION],
                user.settings[Model.LUMA_RAY][UserSettings.QUALITY],
                video_frame_link,
            )

            await write_generation(
                id=result_id,
                request_id=request.id,
                product_id=product.id,
                has_error=result_id is None,
                details={
                    'prompt': prompt,
                    'aspect_ratio': user.settings[Model.LUMA_RAY][UserSettings.ASPECT_RATIO],
                    'duration': user.settings[Model.LUMA_RAY][UserSettings.DURATION],
                    'quality': user.settings[Model.LUMA_RAY][UserSettings.QUALITY],
                }
            )
        except Exception as e:
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
                hashtags=['luma_ray'],
            )

            request.status = RequestStatus.FINISHED
            await update_request(request.id, {
                'status': request.status
            })

            generations = await get_generations_by_request_id(request.id)
            for generation in generations:
                generation.status = GenerationStatus.FINISHED
                generation.has_error = True
                await update_generation(
                    generation.id,
                    {
                        'status': generation.status,
                        'has_error': generation.has_error,
                    },
                )

            await processing_sticker.delete()
            await processing_message.delete()
