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
from bot.database.operations.request.getters import get_request
from bot.database.operations.request.updaters import update_request
from bot.database.operations.transaction.writers import write_transaction
from bot.database.operations.user.getters import get_user
from bot.helpers.senders.send_document import send_document
from bot.helpers.senders.send_error_info import send_error_info
from bot.helpers.senders.send_video import send_video
from bot.helpers.updaters.update_user_usage_quota import update_user_usage_quota
from bot.integrations.kling import Kling
from bot.keyboards.common.common import build_reaction_keyboard, build_error_keyboard
from bot.locales.main import get_user_language, get_localization
from bot.locales.types import LanguageCode


async def handle_kling_webhook(bot: Bot, dp: Dispatcher, body: dict):
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
    try:
        generation_result = body.get('output', {}) \
            .get('works', [{}])[0] \
            .get('video', {}) \
            .get('resource_without_watermark')
    except TypeError:
        generation_result = None

    generation.status = GenerationStatus.FINISHED
    if generation_error or not generation_result:
        generation.has_error = True
        await update_generation(generation.id, {
            'status': generation.status,
            'has_error': generation.has_error,
        })

        if 'inappropriate image detected' in generation_error:
            await bot.send_sticker(
                chat_id=user.telegram_chat_id,
                sticker=config.MESSAGE_STICKERS.get(MessageSticker.FEAR),
            )
            await bot.send_message(
                chat_id=user.telegram_chat_id,
                text=get_localization(user_language_code).ERROR_REQUEST_FORBIDDEN,
            )

            generation.has_error = False
        else:
            await send_error_info(
                bot=bot,
                user_id=user.id,
                info=generation_error,
                hashtags=['kling'],
            )
            logging.exception(f'Error in kling_webhook: {generation_error}')
    else:
        generation.result = generation_result
        await update_generation(generation.id, {
            'status': generation.status,
            'result': generation.result,
            'seconds': generation.seconds,
        })

    asyncio.create_task(handle_kling(bot, dp, user, user_language_code, request, generation))


async def handle_kling(
    bot: Bot,
    dp: Dispatcher,
    user: User,
    user_language_code: LanguageCode,
    request: Request,
    generation: Generation,
):
    prompt = generation.details.get('prompt')

    if generation.result:
        footer_text = f'\n\n📹 {user.daily_limits[Quota.KLING] + user.additional_usage_quota[Quota.KLING]}' \
            if user.settings[Model.KLING][UserSettings.SHOW_USAGE_QUOTA] and \
               user.daily_limits[Quota.KLING] != float('inf') else ''
        caption = f'{get_localization(user_language_code).GENERATION_VIDEO_SUCCESS}{footer_text}'

        reply_markup = build_reaction_keyboard(generation.id)
        if user.settings[Model.KLING][UserSettings.SEND_TYPE] == SendType.DOCUMENT:
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

        total_price = Kling.get_price_for_video(generation.details.get('mode'), generation.details.get('duration'))
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
                Quota.KLING,
                Kling.get_cost_for_video(
                    generation.details.get('mode'),
                    generation.details.get('duration'),
                ) if generation.result else 0,
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
