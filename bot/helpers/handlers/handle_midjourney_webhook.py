import asyncio
import logging

from aiogram import Bot, Dispatcher
from aiogram.fsm.context import FSMContext
from aiogram.fsm.storage.base import StorageKey

from bot.config import config, MessageSticker
from bot.database.models.common import Quota, Currency, Model, MidjourneyAction, SendType
from bot.database.models.generation import GenerationStatus, Generation
from bot.database.models.request import Request, RequestStatus
from bot.database.models.transaction import TransactionType
from bot.database.models.user import User, UserSettings
from bot.database.operations.generation.getters import get_generation
from bot.database.operations.generation.updaters import update_generation
from bot.database.operations.request.getters import get_request
from bot.database.operations.request.updaters import update_request
from bot.database.operations.transaction.writers import write_transaction
from bot.database.operations.user.getters import get_user
from bot.helpers.senders.send_document import send_document
from bot.helpers.senders.send_error_info import send_error_info
from bot.helpers.senders.send_images import send_image
from bot.helpers.updaters.update_user_usage_quota import update_user_usage_quota
from bot.integrations.midjourney import Midjourney
from bot.keyboards.ai.midjourney import build_midjourney_keyboard
from bot.keyboards.common.common import build_reaction_keyboard, build_error_keyboard, build_buy_motivation_keyboard
from bot.locales.main import get_localization, get_user_language
from bot.locales.types import LanguageCode


async def handle_midjourney_webhook(bot: Bot, dp: Dispatcher, body: dict):
    body = body.get('data')
    if body.get('status') == 'processing':
        return

    generation = await get_generation(body.get('task_id'))
    if not generation:
        return
    elif generation.status == GenerationStatus.FINISHED:
        return

    request = await get_request(generation.request_id)
    user = await get_user(request.user_id)

    user_language_code = await get_user_language(user.id, dp.storage)

    generation_error = body.get('error', {}).get('raw_message', '')
    generation_result = body.get('output', {}).get('image_url', '')

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
            hashtags=['midjourney'],
        )
        logging.exception(f'Error in midjourney_webhook: {generation_error}')
    else:
        generation.result = generation_result
        await update_generation(generation.id, {
            'status': generation.status,
            'result': generation.result,
            'seconds': generation.seconds,
        })

    asyncio.create_task(handle_midjourney_result(bot, dp, user, user_language_code, request, generation))


async def handle_midjourney_result(
    bot: Bot,
    dp: Dispatcher,
    user: User,
    user_language_code: LanguageCode,
    request: Request,
    generation: Generation,
):
    is_suggestion = generation.details.get('is_suggestion', False)
    action_type = generation.details.get('action')
    if not generation.has_error and not is_suggestion:
        reply_markup = build_midjourney_keyboard(generation.id) if action_type != MidjourneyAction.UPSCALE \
            else build_reaction_keyboard(generation.id)
        footer_text = f'\n\n🖼 {user.daily_limits[Quota.MIDJOURNEY] + user.additional_usage_quota[Quota.MIDJOURNEY]}' \
            if user.settings[Model.MIDJOURNEY][UserSettings.SHOW_USAGE_QUOTA] and \
               user.daily_limits[Quota.MIDJOURNEY] != float('inf') else ''
        caption = f'{get_localization(user_language_code).GENERATION_IMAGE_SUCCESS}{footer_text}'
        if user.settings[Model.MIDJOURNEY][UserSettings.SEND_TYPE] == SendType.DOCUMENT:
            await send_document(bot, user.telegram_chat_id, generation.result, reply_markup, caption)
        else:
            await send_image(bot, user.telegram_chat_id, generation.result, reply_markup, caption)
    elif not generation.has_error and is_suggestion:
        header_text = f'{get_localization(user_language_code).example_image_model(get_localization(user_language_code).MIDJOURNEY)}\n'
        footer_text = f'\n{get_localization(user_language_code).EXAMPLE_INFO}'
        full_text = f'{header_text}{footer_text}'
        await send_image(
            bot,
            user.telegram_chat_id,
            generation.result,
            build_buy_motivation_keyboard(user_language_code),
            full_text,
        )
    else:
        generation_error = generation.details.get('error', '').lower()
        if not is_suggestion:
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
            info=str(generation_error),
            hashtags=['midjourney'],
        )

    request.status = RequestStatus.FINISHED
    await update_request(request.id, {
        'status': request.status
    })

    price = Midjourney.get_price_for_image(generation.details.get('version'), generation.details.get('action'))
    update_tasks = [
        write_transaction(
            user_id=user.id,
            type=TransactionType.EXPENSE,
            product_id=generation.product_id,
            amount=price,
            clear_amount=price,
            currency=Currency.USD,
            quantity=1,
            details={
                'prompt': generation.details.get('prompt'),
                'type': generation.details.get('action'),
                'is_suggestion': generation.details.get('is_suggestion', False),
                'has_error': generation.details.get('has_error', False),
            }
        ),
    ]

    if not generation.has_error and not is_suggestion and action_type != MidjourneyAction.UPSCALE:
        update_tasks.append(
            update_user_usage_quota(
                user,
                Quota.MIDJOURNEY,
                1,
            )
        )

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

    if not is_suggestion:
        for processing_message_id in request.processing_message_ids:
            try:
                await bot.delete_message(user.telegram_chat_id, processing_message_id)
            except Exception:
                continue
