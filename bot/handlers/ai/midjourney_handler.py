from datetime import datetime, timezone
from typing import Optional

from aiogram import Router
from aiogram.exceptions import TelegramBadRequest, TelegramRetryAfter
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, CallbackQuery
from aiogram.utils.chat_action import ChatActionSender

from bot.config import config, MessageEffect, MessageSticker
from bot.database.main import firebase
from bot.database.models.common import Model, Quota, MidjourneyAction, MidjourneyVersion
from bot.database.models.generation import GenerationStatus
from bot.database.models.request import RequestStatus
from bot.database.models.user import User, UserSettings
from bot.database.operations.generation.getters import get_generation, get_generations_by_request_id
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
from bot.helpers.senders.send_error_info import send_error_info
from bot.keyboards.ai.model import build_switched_to_ai_keyboard, build_model_limit_exceeded_keyboard
from bot.locales.translate_text import translate_text
from bot.integrations.midjourney import (
    create_midjourney_images,
    create_midjourney_image,
    create_different_midjourney_image,
    create_different_midjourney_images,
)
from bot.keyboards.common.common import build_error_keyboard
from bot.locales.main import get_localization, get_user_language
from bot.locales.types import LanguageCode

midjourney_router = Router()

PRICE_MIDJOURNEY_REQUEST = 0.04


@midjourney_router.message(Command('midjourney'))
async def midjourney(message: Message, state: FSMContext):
    await state.clear()

    user_id = str(message.from_user.id)
    user = await get_user(user_id)
    user_language_code = await get_user_language(user_id, state.storage)

    if user.current_model == Model.MIDJOURNEY:
        reply_markup = build_switched_to_ai_keyboard(user_language_code, Model.MIDJOURNEY)
        await message.answer(
            text=get_localization(user_language_code).MODEL_ALREADY_SWITCHED_TO_THIS_MODEL,
            reply_markup=reply_markup,
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
        reply_markup = build_switched_to_ai_keyboard(user_language_code, Model.MIDJOURNEY)
        answered_message = await message.answer(
            text=text,
            reply_markup=reply_markup,
            message_effect_id=config.MESSAGE_EFFECTS.get(MessageEffect.FIRE),
        )

        try:
            await message.bot.unpin_chat_message(user.telegram_chat_id)
            await message.bot.pin_chat_message(user.telegram_chat_id, answered_message.message_id)
        except (TelegramBadRequest, TelegramRetryAfter):
            pass


async def handle_midjourney(
    message: Message,
    state: FSMContext,
    user: User,
    prompt: str,
    action: MidjourneyAction,
    hash_id='',
    choice=0,
    image_filename: Optional[str] = None,
):
    user_language_code = await get_user_language(user.id, state.storage)

    version = user.settings[Model.MIDJOURNEY][UserSettings.VERSION]

    processing_sticker = await message.answer_sticker(
        sticker=config.MESSAGE_STICKERS.get(MessageSticker.IMAGE_GENERATION),
    )
    processing_message = await message.reply(
        text=get_localization(user_language_code).model_image_processing_request(),
        allow_sending_without_reply=True,
    )

    async with ChatActionSender.upload_photo(bot=message.bot, chat_id=message.chat.id):
        quota = user.daily_limits[Quota.MIDJOURNEY] + user.additional_usage_quota[Quota.MIDJOURNEY]
        if quota < 1:
            await message.answer_sticker(
                sticker=config.MESSAGE_STICKERS.get(MessageSticker.SAD),
            )

            reply_markup = build_model_limit_exceeded_keyboard(user_language_code)
            await message.reply(
                text=get_localization(user_language_code).model_reached_usage_limit(),
                reply_markup=reply_markup,
                allow_sending_without_reply=True,
            )
        else:
            product = await get_product_by_quota(Quota.MIDJOURNEY)

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
                details={
                    'prompt': prompt,
                    'action': action,
                    'version': version,
                    'is_suggestion': False,
                }
            )

            try:
                if user_language_code != LanguageCode.EN:
                    prompt = await translate_text(prompt, user_language_code, LanguageCode.EN)
                prompt = prompt.replace('-', '- ')
                if image_filename:
                    image_path = f'users/vision/{user.id}/{image_filename}'
                    image = await firebase.bucket.get_blob(image_path)
                    image_link = firebase.get_public_url(image.name)
                    prompt = f'{image_link} {prompt}'
                prompt += f' --v {version} --ar {user.settings[Model.MIDJOURNEY][UserSettings.ASPECT_RATIO]}'

                if action == MidjourneyAction.UPSCALE:
                    result_id = await create_midjourney_image(hash_id, choice)
                elif action == MidjourneyAction.VARIATION:
                    result_id = await create_different_midjourney_image(hash_id, choice)
                elif action == MidjourneyAction.REROLL:
                    result_id = await create_different_midjourney_images(hash_id)
                else:
                    result_id = await create_midjourney_images(prompt)
                await write_generation(
                    id=result_id,
                    request_id=request.id,
                    product_id=product.id,
                    has_error=result_id is None,
                    details={
                        'prompt': prompt,
                        'action': action,
                        'version': version,
                        'is_suggestion': False,
                    }
                )
            except Exception as e:
                await message.answer_sticker(
                    sticker=config.MESSAGE_STICKERS.get(MessageSticker.ERROR),
                )

                reply_markup = build_error_keyboard(user_language_code)
                await message.answer(
                    text=get_localization(user_language_code).ERROR,
                    reply_markup=reply_markup,
                )

                await send_error_info(
                    bot=message.bot,
                    user_id=user.id,
                    info=str(e),
                    hashtags=['midjourney'],
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
    current_date = datetime.now(timezone.utc)
    if (
        not user.subscription_id and
        user.current_model == Model.LUMA_PHOTON and
        user.settings[user.current_model][UserSettings.SHOW_EXAMPLES] and
        user.daily_limits[Quota.LUMA_PHOTON] in [1] and
        (current_date - user.last_subscription_limit_update).days <= 3
    ):
        product = await get_product_by_quota(Quota.MIDJOURNEY)

        request = await write_request(
            user_id=user.id,
            processing_message_ids=[message.message_id],
            product_id=product.id,
            requested=1,
            details={
                'prompt': prompt,
                'action': MidjourneyAction.IMAGINE,
                'version': MidjourneyVersion.V6,
                'is_suggestion': True,
            }
        )

        try:
            if user_language_code != LanguageCode.EN:
                prompt = await translate_text(prompt, user_language_code, LanguageCode.EN)
            prompt += f' --v {MidjourneyVersion.V6} --ar {user.settings[user.current_model][UserSettings.ASPECT_RATIO]}'

            result_id = await create_midjourney_images(prompt)
            await write_generation(
                id=result_id,
                request_id=request.id,
                product_id=product.id,
                has_error=result_id is None,
                details={
                    'prompt': prompt,
                    'action': MidjourneyAction.IMAGINE,
                    'version': MidjourneyVersion.V6,
                    'is_suggestion': True,
                }
            )
        except Exception as e:
            await send_error_info(
                bot=message.bot,
                user_id=user.id,
                info=str(e),
                hashtags=['midjourney', 'example'],
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
