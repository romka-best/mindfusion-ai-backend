import asyncio
import logging

from aiogram import Bot, Dispatcher
from aiogram.fsm.context import FSMContext
from aiogram.fsm.storage.base import StorageKey

from bot.config import config, MessageSticker
from bot.database.models.common import Model, Currency, Quota, PhotoshopAIAction, SendType
from bot.database.models.generation import Generation, GenerationStatus
from bot.database.models.request import Request, RequestStatus
from bot.database.models.transaction import TransactionType
from bot.database.models.user import User, UserSettings
from bot.database.operations.face_swap_package.getters import get_used_face_swap_package
from bot.database.operations.face_swap_package.updaters import update_used_face_swap_package
from bot.database.operations.generation.getters import get_generations_by_request_id, get_generation
from bot.database.operations.generation.updaters import update_generation
from bot.database.operations.product.getters import get_product
from bot.database.operations.request.getters import get_request
from bot.database.operations.request.updaters import update_request
from bot.database.operations.transaction.writers import write_transaction
from bot.database.operations.user.getters import get_user
from bot.handlers.ai.face_swap_handler import PRICE_FACE_SWAP, handle_face_swap
from bot.handlers.ai.flux_handler import PRICE_FLUX_1_DEV, PRICE_FLUX_1_PRO
from bot.handlers.ai.music_gen_handler import PRICE_MUSIC_GEN, handle_music_gen
from bot.handlers.ai.photoshop_ai_handler import (
    PRICE_PHOTOSHOP_AI_UPSCALE,
    PRICE_PHOTOSHOP_AI_RESTORATION,
    PRICE_PHOTOSHOP_AI_COLORIZATION,
    PRICE_PHOTOSHOP_AI_REMOVAL_BACKGROUND,
    handle_photoshop_ai,
)
from bot.handlers.ai.stable_diffusion_handler import PRICE_STABLE_DIFFUSION_XL, PRICE_STABLE_DIFFUSION_3
from bot.helpers.senders.send_audio import send_audio
from bot.helpers.senders.send_document import send_document
from bot.helpers.senders.send_error_info import send_error_info
from bot.helpers.senders.send_images import send_image
from bot.helpers.updaters.update_user_usage_quota import update_user_usage_quota
from bot.keyboards.common.common import build_reaction_keyboard, build_error_keyboard
from bot.locales.main import get_user_language, get_localization
from bot.locales.types import LanguageCode


async def handle_replicate_webhook(bot: Bot, dp: Dispatcher, prediction: dict):
    generation = await get_generation(prediction.get('id'))
    if not generation:
        return False
    elif generation.status == GenerationStatus.FINISHED:
        return True

    request = await get_request(generation.request_id)
    product = await get_product(request.product_id)
    user = await get_user(request.user_id)

    user_language_code = await get_user_language(user.id, dp.storage)

    generation_error, generation_result = prediction.get('error', ''), prediction.get('output', {})
    seconds = prediction.get('metrics', {}).get('predict_time', 0)

    generation.status = GenerationStatus.FINISHED
    generation.seconds = seconds
    if generation_error and 'NSFW content' in generation_error:
        await update_generation(generation.id, {
            'status': generation.status,
            'seconds': generation.seconds,
        })

        await bot.send_sticker(
            chat_id=user.telegram_chat_id,
            sticker=config.MESSAGE_STICKERS.get(MessageSticker.FEAR),
        )
        await bot.send_message(
            chat_id=user.telegram_chat_id,
            text=get_localization(user_language_code).ERROR_REQUEST_FORBIDDEN,
        )
    elif generation_error or not generation_result:
        generation.has_error = True
        await update_generation(generation.id, {
            'status': generation.status,
            'has_error': generation.has_error,
            'seconds': generation.seconds,
        })

        await send_error_info(
            bot=bot,
            user_id=user.id,
            info=generation_error,
            hashtags=['replicate'],
        )
        logging.exception(f'Error in replicate_webhook: {prediction.get("logs")}')
    else:
        generation.result = generation_result[0] if type(generation_result) == list else generation_result
        if (
            product.details.get('quota') == Quota.PHOTOSHOP_AI and
            request.details.get('type') == PhotoshopAIAction.COLORIZATION
        ):
            generation.result = generation.result.get('image')
        await update_generation(generation.id, {
            'status': generation.status,
            'result': generation.result,
            'seconds': generation.seconds,
        })

    if (
        product.details.get('quota') == Quota.STABLE_DIFFUSION_XL or
        product.details.get('quota') == Quota.STABLE_DIFFUSION_3
    ):
        asyncio.create_task(
            handle_replicate_stable_diffusion(
                bot,
                dp,
                user,
                user_language_code,
                product.details.get('quota'),
                request,
                generation,
            )
        )
    elif (
        product.details.get('quota') == Quota.FLUX_1_DEV or
        product.details.get('quota') == Quota.FLUX_1_PRO
    ):
        asyncio.create_task(
            handle_replicate_flux(
                bot,
                dp,
                user,
                user_language_code,
                product.details.get('quota'),
                request,
                generation,
            )
        )
    elif product.details.get('quota') == Quota.FACE_SWAP:
        asyncio.create_task(handle_replicate_face_swap(bot, dp, user, user_language_code, request, generation))
    elif product.details.get('quota') == Quota.PHOTOSHOP_AI:
        asyncio.create_task(handle_replicate_photoshop_ai(bot, dp, user, user_language_code, request, generation))
    elif product.details.get('quota') == Quota.MUSIC_GEN:
        asyncio.create_task(handle_replicate_music_gen(bot, dp, user, user_language_code, request, generation))

    return True


async def handle_replicate_photoshop_ai(
    bot: Bot,
    dp: Dispatcher,
    user: User,
    user_language_code: LanguageCode,
    request: Request,
    generation: Generation,
):
    if generation.result:
        footer_text = f'\n\n🖼 {user.daily_limits[Quota.PHOTOSHOP_AI] + user.additional_usage_quota[Quota.PHOTOSHOP_AI]}' \
            if user.settings[Model.PHOTOSHOP_AI][UserSettings.SHOW_USAGE_QUOTA] and \
               user.daily_limits[Quota.PHOTOSHOP_AI] != float('inf') else ''
        caption = f'{get_localization(user_language_code).GENERATION_IMAGE_SUCCESS}{footer_text}'

        reply_markup = build_reaction_keyboard(generation.id)
        if user.settings[Model.PHOTOSHOP_AI][UserSettings.SEND_TYPE] == SendType.DOCUMENT:
            await send_document(bot, user.telegram_chat_id, generation.result, reply_markup, caption)
        else:
            await send_image(bot, user.telegram_chat_id, generation.result, reply_markup, caption)
    elif generation.has_error:
        await bot.send_sticker(
            chat_id=user.telegram_chat_id,
            sticker=config.MESSAGE_STICKERS.get(MessageSticker.ERROR),
        )

        reply_markup = build_error_keyboard(user_language_code)
        await bot.send_message(
            chat_id=user.telegram_chat_id,
            text=get_localization(user_language_code).ERROR,
            reply_markup=reply_markup,
        )

    if request.status != RequestStatus.FINISHED:
        request.status = RequestStatus.FINISHED
        await update_request(request.id, {
            'status': request.status
        })

        action_name = request.details.get('type')
        if action_name == PhotoshopAIAction.UPSCALE:
            total_price = round(PRICE_PHOTOSHOP_AI_UPSCALE * generation.seconds, 6)
        elif action_name == PhotoshopAIAction.RESTORATION:
            total_price = round(PRICE_PHOTOSHOP_AI_RESTORATION * generation.seconds, 6)
        elif action_name == PhotoshopAIAction.COLORIZATION:
            total_price = round(PRICE_PHOTOSHOP_AI_COLORIZATION * generation.seconds, 6)
        elif action_name == PhotoshopAIAction.REMOVAL_BACKGROUND:
            total_price = round(PRICE_PHOTOSHOP_AI_REMOVAL_BACKGROUND * generation.seconds, 6)
        else:
            total_price = round(0.000575 * generation.seconds, 6)

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
                    'type': action_name,
                    'has_error': generation.has_error,
                },
            ),
            update_user_usage_quota(
                user,
                Quota.PHOTOSHOP_AI,
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

        if user.current_model == Model.PHOTOSHOP_AI:
            await handle_photoshop_ai(bot, user.telegram_chat_id, state, user.id)

        for processing_message_id in request.processing_message_ids:
            try:
                await bot.delete_message(user.telegram_chat_id, processing_message_id)
            except Exception:
                continue


async def handle_replicate_face_swap(
    bot: Bot,
    dp: Dispatcher,
    user: User,
    user_language_code: LanguageCode,
    request: Request,
    generation: Generation,
):
    if generation.result:
        reply_markup = build_reaction_keyboard(generation.id)
        if user.settings[Model.FACE_SWAP][UserSettings.SEND_TYPE] == SendType.DOCUMENT:
            await send_document(bot, user.telegram_chat_id, generation.result, reply_markup)
        else:
            await send_image(bot, user.telegram_chat_id, generation.result, reply_markup)

    current_count = await dp.storage.redis.incr(request.id)
    if current_count == request.requested and request.status != RequestStatus.FINISHED:
        request.status = RequestStatus.FINISHED
        await update_request(request.id, {
            'status': request.status
        })

        request_generations = await get_generations_by_request_id(request.id)
        success_generations = []
        used_face_swap_package_used_images = []
        total_seconds = 0
        for request_generation in request_generations:
            if request_generation.result:
                success_generations.append(request_generation.result)
            if request_generation.details.get('used_face_swap_package_used_image'):
                used_face_swap_package_used_images.append(
                    request_generation.details.get('used_face_swap_package_used_image')
                )
            total_seconds += request_generation.seconds

        total_result = len(success_generations)
        if total_result != len(request_generations):
            await bot.send_message(
                user.telegram_chat_id,
                get_localization(user_language_code).FACE_SWAP_NO_FACE_FOUND_ERROR,
            )

        used_face_swap_package = await get_used_face_swap_package(
            generation.details.get('used_face_swap_package_id')
        )
        if request.details.get('is_test'):
            total_price = round(PRICE_FACE_SWAP * total_seconds, 6)
            update_tasks = [
                write_transaction(
                    user_id=user.id,
                    type=TransactionType.EXPENSE,
                    product_id=generation.product_id,
                    amount=total_price,
                    clear_amount=total_price,
                    currency=Currency.USD,
                    quantity=total_result,
                    details={
                        'name': request.details.get('face_swap_package_name'),
                        'images': success_generations,
                        'seconds': total_seconds,
                        'has_error': generation.has_error,
                    }),
            ]
        else:
            total_price = round(PRICE_FACE_SWAP * total_seconds, 6)
            update_tasks = [
                write_transaction(
                    user_id=user.id,
                    type=TransactionType.EXPENSE,
                    product_id=generation.product_id,
                    amount=total_price,
                    clear_amount=total_price,
                    currency=Currency.USD,
                    quantity=total_result,
                    details={
                        'name': request.details.get('face_swap_package_name', 'CUSTOM'),
                        'images': success_generations,
                        'seconds': total_seconds,
                        'has_error': generation.has_error,
                    }
                ),
                update_user_usage_quota(
                    user,
                    Quota.FACE_SWAP,
                    total_result,
                ),
            ]

            if (
                total_result == len(request_generations) and
                used_face_swap_package and
                used_face_swap_package_used_images
            ):
                update_tasks.append(
                    update_used_face_swap_package(used_face_swap_package.id, {
                        'used_images': used_face_swap_package.used_images + used_face_swap_package_used_images,
                    })
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

        if total_result == len(request_generations) and user.current_model == Model.FACE_SWAP:
            await handle_face_swap(bot, user.telegram_chat_id, state, user.id)

        for processing_message_id in request.processing_message_ids:
            try:
                await bot.delete_message(user.telegram_chat_id, processing_message_id)
            except Exception:
                continue


async def handle_replicate_music_gen(
    bot: Bot,
    dp: Dispatcher,
    user: User,
    user_language_code: LanguageCode,
    request: Request,
    generation: Generation,
):
    prompt = generation.details.get('prompt')
    duration = int(generation.details.get('duration'))

    if generation.result:
        reply_markup = build_reaction_keyboard(generation.id)
        caption = f'🎵 {(user.daily_limits[Quota.MUSIC_GEN] + user.additional_usage_quota[Quota.MUSIC_GEN]) - duration // 10}' \
            if user.settings[Model.MUSIC_GEN][UserSettings.SHOW_USAGE_QUOTA] and \
               user.daily_limits[Quota.MUSIC_GEN] != float('inf') else '🎵'
        await send_audio(
            bot,
            user.telegram_chat_id,
            generation.result,
            caption,
            prompt,
            duration,
            reply_markup,
        )
    elif generation.has_error:
        await bot.send_sticker(
            chat_id=user.telegram_chat_id,
            sticker=config.MESSAGE_STICKERS.get(MessageSticker.ERROR),
        )

        reply_markup = build_error_keyboard(user_language_code)
        await bot.send_message(
            chat_id=user.telegram_chat_id,
            text=get_localization(user_language_code).ERROR,
            reply_markup=reply_markup,
        )

    if request.status != RequestStatus.FINISHED:
        request.status = RequestStatus.FINISHED
        await update_request(request.id, {
            'status': request.status
        })

        total_price = round(PRICE_MUSIC_GEN * generation.seconds, 6)
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
                    'duration': duration,
                    'has_error': generation.has_error,
                },
            ),
            update_user_usage_quota(
                user,
                Quota.MUSIC_GEN,
                duration // 10 if generation.result else 0,
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

        if user.current_model == Model.MUSIC_GEN:
            await handle_music_gen(bot, user.telegram_chat_id, state, user.id)

        for processing_message_id in request.processing_message_ids:
            try:
                await bot.delete_message(user.telegram_chat_id, processing_message_id)
            except Exception:
                continue


async def handle_replicate_stable_diffusion(
    bot: Bot,
    dp: Dispatcher,
    user: User,
    user_language_code: LanguageCode,
    user_quota: Quota,
    request: Request,
    generation: Generation,
):
    prompt = generation.details.get('prompt')

    if generation.result:
        footer_text = f'\n\n🖼 {user.daily_limits[user_quota] + user.additional_usage_quota[user_quota]}' \
            if user.settings[Model.STABLE_DIFFUSION][UserSettings.SHOW_USAGE_QUOTA] and \
               user.daily_limits[user_quota] != float('inf') else ''
        caption = f'{get_localization(user_language_code).GENERATION_IMAGE_SUCCESS}{footer_text}'

        reply_markup = build_reaction_keyboard(generation.id)
        if user.settings[Model.STABLE_DIFFUSION][UserSettings.SEND_TYPE] == SendType.DOCUMENT:
            await send_document(bot, user.telegram_chat_id, generation.result, reply_markup, caption)
        else:
            await send_image(bot, user.telegram_chat_id, generation.result, reply_markup, caption)
    elif generation.has_error:
        await bot.send_sticker(
            chat_id=user.telegram_chat_id,
            sticker=config.MESSAGE_STICKERS.get(MessageSticker.ERROR),
        )

        reply_markup = build_error_keyboard(user_language_code)
        await bot.send_message(
            chat_id=user.telegram_chat_id,
            text=get_localization(user_language_code).ERROR,
            reply_markup=reply_markup,
        )

    if request.status != RequestStatus.FINISHED:
        request.status = RequestStatus.FINISHED
        await update_request(request.id, {
            'status': request.status
        })

        total_price = PRICE_STABLE_DIFFUSION_XL if user_quota == Quota.STABLE_DIFFUSION_XL else PRICE_STABLE_DIFFUSION_3
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
                user_quota,
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


async def handle_replicate_flux(
    bot: Bot,
    dp: Dispatcher,
    user: User,
    user_language_code: LanguageCode,
    user_quota: Quota,
    request: Request,
    generation: Generation,
):
    prompt = generation.details.get('prompt')

    if generation.result:
        footer_text = f'\n\n🖼 {user.daily_limits[user_quota] + user.additional_usage_quota[user_quota]}' \
            if user.settings[Model.FLUX][UserSettings.SHOW_USAGE_QUOTA] and \
               user.daily_limits[user_quota] != float('inf') else ''
        caption = f'{get_localization(user_language_code).GENERATION_IMAGE_SUCCESS}{footer_text}'

        reply_markup = build_reaction_keyboard(generation.id)
        if user.settings[Model.FLUX][UserSettings.SEND_TYPE] == SendType.DOCUMENT:
            await send_document(bot, user.telegram_chat_id, generation.result, reply_markup, caption)
        else:
            await send_image(bot, user.telegram_chat_id, generation.result, reply_markup, caption)
    elif generation.has_error:
        await bot.send_sticker(
            chat_id=user.telegram_chat_id,
            sticker=config.MESSAGE_STICKERS.get(MessageSticker.ERROR),
        )

        reply_markup = build_error_keyboard(user_language_code)
        await bot.send_message(
            chat_id=user.telegram_chat_id,
            text=get_localization(user_language_code).ERROR,
            reply_markup=reply_markup,
        )

    if request.status != RequestStatus.FINISHED:
        request.status = RequestStatus.FINISHED
        await update_request(request.id, {
            'status': request.status
        })

        total_price = PRICE_FLUX_1_DEV if user_quota == Quota.FLUX_1_DEV else PRICE_FLUX_1_PRO
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
                user_quota,
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
