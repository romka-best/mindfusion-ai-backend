import asyncio
import logging

from aiogram import Bot, Dispatcher
from aiogram.fsm.context import FSMContext
from aiogram.fsm.storage.base import StorageKey

from bot.config import config, MessageSticker
from bot.database.models.common import Quota, Model, SendType, Currency
from bot.database.models.generation import GenerationStatus, Generation
from bot.database.models.request import Request, RequestStatus
from bot.database.models.transaction import TransactionType
from bot.database.models.user import User, UserSettings
from bot.database.operations.generation.getters import get_generation
from bot.database.operations.generation.updaters import update_generation
from bot.database.operations.product.getters import get_product
from bot.database.operations.request.getters import get_request
from bot.database.operations.request.updaters import update_request
from bot.database.operations.transaction.writers import write_transaction
from bot.database.operations.user.getters import get_user
from bot.handlers.ai.luma_handler import PRICE_LUMA_PHOTON, PRICE_LUMA_RAY
from bot.helpers.senders.send_document import send_document
from bot.helpers.senders.send_error_info import send_error_info
from bot.helpers.senders.send_images import send_image
from bot.helpers.senders.send_video import send_video
from bot.helpers.updaters.update_user_usage_quota import update_user_usage_quota
from bot.integrations.luma import get_cost_for_video
from bot.keyboards.common.common import build_reaction_keyboard, build_error_keyboard
from bot.locales.main import get_user_language, get_localization
from bot.locales.types import LanguageCode


async def handle_luma_webhook(bot: Bot, dp: Dispatcher, body: dict):
    if body.get('state') == 'dreaming':
        return

    generation = await get_generation(body.get('id'))
    if not generation:
        return
    elif generation.status == GenerationStatus.FINISHED:
        return

    request = await get_request(generation.request_id)

    current_count = await dp.storage.redis.incr(request.id)
    if current_count != request.requested:
        return

    product = await get_product(request.product_id)
    user = await get_user(request.user_id)

    user_language_code = await get_user_language(user.id, dp.storage)

    generation_error = body.get('failure_reason', '')
    generation_result = body.get('assets', {}).get('image') if body.get('generation_type') == 'image' \
        else body.get('assets', {}).get('video')

    generation.status = GenerationStatus.FINISHED
    if generation_error or not generation_result:
        generation.has_error = True
        await update_generation(generation.id, {
            'status': generation.status,
            'has_error': generation.has_error,
        })

        await send_error_info(
            bot=bot,
            user_id=user.id,
            info=generation_error,
            hashtags=['luma'],
        )
        logging.exception(f'Error in luma_webhook: {generation_error}')
    else:
        generation.result = generation_result
        await update_generation(generation.id, {
            'status': generation.status,
            'result': generation.result,
        })

    if product.details.get('quota') == Quota.LUMA_PHOTON:
        asyncio.create_task(handle_luma_photon(bot, dp, user, user_language_code, request, generation))
    elif product.details.get('quota') == Quota.LUMA_RAY:
        asyncio.create_task(handle_luma_ray(bot, dp, user, user_language_code, request, generation))


async def handle_luma_photon(
    bot: Bot,
    dp: Dispatcher,
    user: User,
    user_language_code: LanguageCode,
    request: Request,
    generation: Generation,
):
    prompt = generation.details.get('prompt')

    if generation.result:
        footer_text = f'\n\n🖼 {user.daily_limits[Quota.LUMA_PHOTON] + user.additional_usage_quota[Quota.LUMA_PHOTON]}' \
            if user.settings[Model.LUMA_PHOTON][UserSettings.SHOW_USAGE_QUOTA] and \
               user.daily_limits[Quota.LUMA_PHOTON] != float('inf') else ''
        caption = f'{get_localization(user_language_code).GENERATION_IMAGE_SUCCESS}{footer_text}'

        reply_markup = build_reaction_keyboard(generation.id)
        if user.settings[Model.LUMA_PHOTON][UserSettings.SEND_TYPE] == SendType.DOCUMENT:
            await send_document(bot, user.telegram_chat_id, generation.result, reply_markup, caption)
        else:
            await send_image(bot, user.telegram_chat_id, generation.result, reply_markup, caption)
    elif generation.has_error:
        await bot.send_sticker(
            chat_id=user.telegram_chat_id,
            sticker=config.MESSAGE_STICKERS.get(MessageSticker.ERROR),
        )

        await bot.send_message(
            chat_id=user.telegram_chat_id,
            text=get_localization(user_language_code).ERROR,
            reply_markup=build_error_keyboard(user_language_code),
        )

    if request.status != RequestStatus.FINISHED:
        request.status = RequestStatus.FINISHED
        await update_request(request.id, {
            'status': request.status
        })

        total_price = PRICE_LUMA_PHOTON
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
                Quota.LUMA_PHOTON,
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


async def handle_luma_ray(
    bot: Bot,
    dp: Dispatcher,
    user: User,
    user_language_code: LanguageCode,
    request: Request,
    generation: Generation,
):
    prompt = generation.details.get('prompt')

    if generation.result:
        footer_text = f'\n\n📹 {user.daily_limits[Quota.LUMA_RAY] + user.additional_usage_quota[Quota.LUMA_RAY]}' \
            if user.settings[Model.LUMA_RAY][UserSettings.SHOW_USAGE_QUOTA] and \
               user.daily_limits[Quota.LUMA_RAY] != float('inf') else ''
        caption = f'{get_localization(user_language_code).GENERATION_VIDEO_SUCCESS}{footer_text}'

        reply_markup = build_reaction_keyboard(generation.id)
        if user.settings[Model.LUMA_RAY][UserSettings.SEND_TYPE] == SendType.DOCUMENT:
            await send_document(
                bot,
                user.telegram_chat_id,
                generation.result,
                reply_markup,
                caption,
            )
        else:
            await send_video(
                bot,
                user.telegram_chat_id,
                generation.result,
                caption,
                get_localization(user_language_code).SETTINGS_SEND_TYPE_VIDEO,
                generation.details.get('duration', 5),
                reply_markup,
            )
    elif generation.has_error:
        await bot.send_sticker(
            chat_id=user.telegram_chat_id,
            sticker=config.MESSAGE_STICKERS.get(MessageSticker.ERROR),
        )

        await bot.send_message(
            chat_id=user.telegram_chat_id,
            text=get_localization(user_language_code).ERROR,
            reply_markup=build_error_keyboard(user_language_code),
        )

    if request.status != RequestStatus.FINISHED:
        request.status = RequestStatus.FINISHED
        await update_request(request.id, {
            'status': request.status
        })

        cost = get_cost_for_video(
            generation.details.get('quality'),
            generation.details.get('duration'),
        )

        total_price = PRICE_LUMA_RAY * cost
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
                Quota.LUMA_RAY,
                cost if generation.result else 0,
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
