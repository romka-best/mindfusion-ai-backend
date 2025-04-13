import asyncio
from datetime import datetime, timezone
from typing import Optional

from aiogram import Router
from aiogram.exceptions import TelegramBadRequest, TelegramRetryAfter
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, CallbackQuery, InlineKeyboardButton, InlineKeyboardMarkup
from aiogram.utils.chat_action import ChatActionSender

from bot.config import config, MessageEffect, MessageSticker
from bot.database.main import firebase
from bot.database.models.common import Model, Quota, FluxVersion
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
from bot.helpers.senders.send_error_info import send_error_info
from bot.integrations.replicate_ai import create_flux_image
from bot.keyboards.ai.flux import build_flux_keyboard
from bot.keyboards.ai.model import build_switched_to_ai_keyboard
from bot.keyboards.common.common import build_error_keyboard
from bot.locales.main import get_user_language, get_localization
from bot.locales.translate_text import translate_text
from bot.locales.types import LanguageCode

flux_router = Router()

PRICE_FLUX_1_DEV = 0.025
PRICE_FLUX_1_PRO = 0.04


@flux_router.message(Command('flux'))
async def flux(message: Message, state: FSMContext):
    await state.clear()

    user_id = str(message.from_user.id)
    user = await get_user(user_id)
    user_language_code = await get_user_language(user_id, state.storage)

    await message.answer(
        text=get_localization(user_language_code).MODEL_CHOOSE_FLUX,
        reply_markup=build_flux_keyboard(
            user_language_code,
            user.current_model,
            user.settings[Model.FLUX][UserSettings.VERSION],
        ),
    )


@flux_router.callback_query(lambda c: c.data.startswith('flux:'))
async def flux_choose_selection(callback_query: CallbackQuery, state: FSMContext):
    await callback_query.answer()

    user_id = str(callback_query.from_user.id)
    user = await get_user(user_id)
    user_language_code = await get_user_language(user_id, state.storage)

    chosen_version = callback_query.data.split(':')[1]

    if (
        user.current_model == Model.FLUX and
        chosen_version == user.settings[Model.FLUX][UserSettings.VERSION]
    ):
        await callback_query.message.answer(
            text=get_localization(user_language_code).MODEL_ALREADY_SWITCHED_TO_THIS_MODEL,
            reply_markup=build_switched_to_ai_keyboard(user_language_code, Model.FLUX),
        )
    else:
        keyboard = callback_query.message.reply_markup.inline_keyboard
        keyboard_changed = False

        new_keyboard = []
        for row in keyboard:
            new_row = []
            for button in row:
                text = button.text
                callback_data = button.callback_data.split(':', 1)[1]

                if callback_data == chosen_version:
                    if '✅' not in text:
                        text += ' ✅'
                        keyboard_changed = True
                else:
                    text = text.replace(' ✅', '')
                new_row.append(InlineKeyboardButton(text=text, callback_data=button.callback_data))
            new_keyboard.append(new_row)
        await callback_query.message.edit_reply_markup(reply_markup=InlineKeyboardMarkup(inline_keyboard=new_keyboard))

        reply_markup = build_switched_to_ai_keyboard(user_language_code, Model.FLUX)
        if keyboard_changed:
            user.current_model = Model.FLUX
            user.settings[Model.FLUX][UserSettings.VERSION] = chosen_version
            await update_user(user_id, {
                'current_model': user.current_model,
                'settings': user.settings,
            })

            text = await get_switched_to_ai_model(
                user,
                get_quota_by_model(user.current_model, user.settings[user.current_model][UserSettings.VERSION]),
                user_language_code,
            )
            if not text:
                raise NotImplementedError(
                    f'Model version is not found: {user.settings[user.current_model][UserSettings.VERSION]}'
                )

            answered_message = await callback_query.message.answer(
                text=text,
                reply_markup=reply_markup,
                message_effect_id=config.MESSAGE_EFFECTS.get(MessageEffect.FIRE),
            )

            try:
                await callback_query.bot.unpin_all_chat_messages(user.telegram_chat_id)
                await callback_query.bot.pin_chat_message(user.telegram_chat_id, answered_message.message_id)
            except (TelegramBadRequest, TelegramRetryAfter):
                pass
        else:
            await callback_query.message.answer(
                text=get_localization(user_language_code).MODEL_ALREADY_SWITCHED_TO_THIS_MODEL,
                reply_markup=reply_markup,
            )

    await state.clear()


async def handle_flux(
    message: Message,
    state: FSMContext,
    user: User,
    user_quota: Quota,
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
        product = await get_product_by_quota(user_quota)

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
            if user_language_code != LanguageCode.EN:
                prompt = await translate_text(prompt, user_language_code, LanguageCode.EN)
            result_id = await create_flux_image(
                prompt,
                user.settings[Model.FLUX][UserSettings.VERSION],
                user.settings[Model.FLUX][UserSettings.ASPECT_RATIO],
                user.settings[Model.FLUX][UserSettings.SAFETY_TOLERANCE],
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
                hashtags=['flux'],
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
        handle_flux_example(
            user=user,
            user_language_code=user_language_code,
            prompt=prompt,
            message=message,
        )
    )


async def handle_flux_example(
    user: User,
    user_language_code: LanguageCode,
    prompt: str,
    message: Message,
):
    current_date = datetime.now(timezone.utc)
    if (
        not user.subscription_id and
        user.current_model == Model.FLUX and
        user.settings[user.current_model][UserSettings.VERSION] == FluxVersion.V1_Dev and
        user.settings[user.current_model][UserSettings.SHOW_EXAMPLES] and
        user.daily_limits[Quota.FLUX_1_DEV] in [1] and
        (current_date - user.last_subscription_limit_update).days <= 3
    ):
        product = await get_product_by_quota(Quota.FLUX_1_PRO)

        request = await write_request(
            user_id=user.id,
            processing_message_ids=[message.message_id],
            product_id=product.id,
            requested=1,
            details={
                'prompt': prompt,
                'is_suggestion': True,
            }
        )

        try:
            if user_language_code != LanguageCode.EN:
                prompt = await translate_text(prompt, user_language_code, LanguageCode.EN)
            result_id = await create_flux_image(
                prompt,
                FluxVersion.V1_Pro,
                user.settings[Model.FLUX][UserSettings.ASPECT_RATIO],
                user.settings[Model.FLUX][UserSettings.SAFETY_TOLERANCE],
            )

            await write_generation(
                id=result_id,
                request_id=request.id,
                product_id=product.id,
                has_error=result_id is None,
                details={
                    'prompt': prompt,
                    'is_suggestion': True,
                }
            )
        except Exception as e:
            await send_error_info(
                bot=message.bot,
                user_id=user.id,
                info=str(e),
                hashtags=['flux', 'example'],
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
