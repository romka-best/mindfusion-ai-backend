import asyncio
import logging

from aiogram import Bot, Dispatcher
from aiogram.fsm.context import FSMContext
from aiogram.fsm.storage.base import StorageKey

from bot.config import config, MessageSticker
from bot.database.models.common import Model, SendType, Quota, Currency
from bot.database.models.generation import GenerationStatus
from bot.database.models.request import RequestStatus
from bot.database.models.transaction import TransactionType
from bot.database.models.user import UserSettings
from bot.database.operations.generation.getters import get_generation
from bot.database.operations.generation.updaters import update_generation
from bot.database.operations.request.getters import get_request
from bot.database.operations.request.updaters import update_request
from bot.database.operations.transaction.writers import write_transaction
from bot.database.operations.user.getters import get_user
from bot.handlers.ai.pika_handler import PRICE_PIKA
from bot.helpers.senders.send_document import send_document
from bot.helpers.senders.send_error_info import send_error_info
from bot.helpers.senders.send_video import send_video
from bot.helpers.updaters.update_user_usage_quota import update_user_usage_quota
from bot.keyboards.common.common import build_error_keyboard, build_reaction_keyboard
from bot.locales.main import get_user_language, get_localization


async def handle_pika_webhook(bot: Bot, dp: Dispatcher, body: dict):
    generation = await get_generation(body.get('task_id'))
    if not generation:
        return False
    elif generation.status == GenerationStatus.FINISHED:
        return True

    request = await get_request(generation.request_id)
    user = await get_user(request.user_id)
    user_language_code = await get_user_language(user.id, dp.storage)

    is_generations_success, generations_result = body.get('success', False), body.get('data', [])

    generation.status = GenerationStatus.FINISHED
    if not is_generations_success:
        generation.has_error = True
        await update_generation(generation.id, {
            'status': generation.status,
            'has_error': generation.has_error,
        })

        error_message = body.get('error', {}).get('message', {}).get('message', '')
        if 'content violation' in error_message:
            await bot.send_sticker(
                chat_id=user.telegram_chat_id,
                sticker=config.MESSAGE_STICKERS.get(MessageSticker.FEAR),
            )
            await bot.send_message(
                chat_id=user.telegram_chat_id,
                text=get_localization(user_language_code).ERROR_REQUEST_FORBIDDEN,
            )
        else:
            logging.exception(f'Error in pika_webhook', error_message)
            await bot.send_sticker(
                chat_id=user.telegram_chat_id,
                sticker=config.MESSAGE_STICKERS.get(MessageSticker.ERROR),
            )

            await bot.send_message(
                chat_id=user.telegram_chat_id,
                text=get_localization(user_language_code).ERROR,
                reply_markup=build_error_keyboard(user_language_code),
            )
            await send_error_info(
                bot=bot,
                user_id=user.id,
                info=str(error_message),
                hashtags=['pika'],
            )
    else:
        generation_result = generations_result[0]
        generation.result = generation_result.get('video_url', '')
        generation_new_details = {
            'id': generation_result.get('id'),
            'video_url': generation_result.get('video_url'),
            'image_url': generation_result.get('image_url'),
            'duration': int(generation_result.get('duration')),
        }
        generation.details = {**generation.details, **generation_new_details}
        await update_generation(generation.id, {
            'status': generation.status,
            'result': generation.result,
            'details': generation.details,
        })

    if len(generations_result) > 0:
        generation_result = generations_result[0]
        (
            duration,
            video_url,
            audio_url,
        ) = (
            int(generation_result.get('duration', 0)),
            generation_result.get('video_url'),
            generation_result.get('audio_url'),
        )

        footer_text = f'\n\n📹 {user.daily_limits[Quota.PIKA] + user.additional_usage_quota[Quota.PIKA]}' \
            if user.settings[Model.PIKA][UserSettings.SHOW_USAGE_QUOTA] and \
               user.daily_limits[Quota.PIKA] != float('inf') else ''
        caption = f'{get_localization(user_language_code).GENERATION_VIDEO_SUCCESS}{footer_text}'

        reply_markup = build_reaction_keyboard(generation.id)
        if user.settings[Model.PIKA][UserSettings.SEND_TYPE] == SendType.DOCUMENT:
            await send_document(
                bot=bot,
                chat_id=user.telegram_chat_id,
                document=generation.result,
                reply_markup=reply_markup,
                caption=caption,
            )
        else:
            await send_video(
                bot=bot,
                chat_id=user.telegram_chat_id,
                result=video_url,
                caption=caption,
                filename=get_localization(user_language_code).SETTINGS_SEND_TYPE_VIDEO,
                duration=duration,
                reply_markup=reply_markup,
            )
    if request.status != RequestStatus.FINISHED:
        request.status = RequestStatus.FINISHED
        await update_request(request.id, {
            'status': request.status
        })

        prompt = generation.details.get('prompt')

        total_price = PRICE_PIKA
        update_tasks = [
            write_transaction(
                user_id=user.id,
                type=TransactionType.EXPENSE,
                product_id=generation.product_id,
                amount=total_price,
                clear_amount=total_price,
                currency=Currency.USD,
                quantity=1 if generation.result else 0,
                details={
                    'result': generation.result,
                    'prompt': prompt,
                    'has_error': generation.has_error,
                },
            ),
            update_user_usage_quota(
                user,
                Quota.PIKA,
                1 if generation.result else 0,
            ),
        ]

        await asyncio.gather(*update_tasks)

        state = FSMContext(
            storage=dp.storage,
            key=StorageKey(
                chat_id=int(user.telegram_chat_id),
                user_id=int(user.id),
                bot_id=bot.id,
            )
        )
        await state.clear()

        for processing_message_id in request.processing_message_ids:
            try:
                await bot.delete_message(user.telegram_chat_id, processing_message_id)
            except Exception:
                continue

    return True
