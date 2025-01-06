import asyncio
import logging

from aiogram import Bot, Dispatcher
from aiogram.fsm.context import FSMContext
from aiogram.fsm.storage.base import StorageKey
from aiogram.utils.markdown import hlink

from bot.config import config, MessageSticker
from bot.database.models.common import Quota, Currency, Model, SendType
from bot.database.models.generation import GenerationStatus
from bot.database.models.request import RequestStatus
from bot.database.models.transaction import TransactionType
from bot.database.models.user import UserSettings
from bot.database.operations.generation.getters import get_generation, get_generations_by_request_id
from bot.database.operations.generation.updaters import update_generation
from bot.database.operations.product.getters import get_product_by_quota
from bot.database.operations.request.getters import get_request
from bot.database.operations.request.updaters import update_request
from bot.database.operations.transaction.writers import write_transaction
from bot.database.operations.user.getters import get_user
from bot.database.operations.user.updaters import update_user
from bot.handlers.ai.suno_handler import PRICE_SUNO
from bot.helpers.senders.send_audio import send_audio
from bot.helpers.senders.send_error_info import send_error_info
from bot.helpers.senders.send_video import send_video
from bot.helpers.updaters.update_user_usage_quota import get_user_with_updated_quota
from bot.keyboards.ai.suno import build_suno_keyboard
from bot.keyboards.common.common import build_reaction_keyboard, build_error_keyboard
from bot.locales.main import get_user_language, get_localization


async def handle_suno_webhook(bot: Bot, dp: Dispatcher, body: dict):
    first_generation = await get_generation(f'{body.get("task_id")}-1')
    second_generation = await get_generation(f'{body.get("task_id")}-2')
    if not first_generation and not second_generation:
        return False
    elif first_generation.status == GenerationStatus.FINISHED and second_generation.status == GenerationStatus.FINISHED:
        return True

    request = await get_request(first_generation.request_id)
    user = await get_user(request.user_id)
    user_language_code = await get_user_language(user.id, dp.storage)

    is_generations_success, generations_result = body.get('success', False), body.get('data', [])

    first_generation.status = GenerationStatus.FINISHED
    second_generation.status = GenerationStatus.FINISHED
    if not is_generations_success:
        first_generation.has_error = True
        second_generation.has_error = True
        await update_generation(first_generation.id, {
            'status': first_generation.status,
            'has_error': first_generation.has_error,
        })
        await update_generation(second_generation.id, {
            'status': second_generation.status,
            'has_error': second_generation.has_error,
        })

        error_message = body.get('error', {}).get('message', '')
        logging.exception(f'Error in suno_webhook', error_message)
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
            hashtags=['suno'],
        )
    else:
        for i, current_generation in enumerate([first_generation, second_generation]):
            generation_result = generations_result[i]
            current_generation.result = generation_result.get('audio_url', '')
            current_generation_new_details = {
                'id': generation_result.get('id'),
                'title': generation_result.get('title'),
                'audio_url': generation_result.get('audio_url'),
                'video_url': generation_result.get('video_url'),
                'image_url': generation_result.get('image_url'),
                'lyric': format_lyrics(generation_result.get('lyric')),
                'style': generation_result.get('style'),
                'duration': int(generation_result.get('duration')),
            }
            current_generation.details = {**current_generation.details, **current_generation_new_details}
            await update_generation(current_generation.id, {
                'status': current_generation.status,
                'result': current_generation.result,
                'details': current_generation.details,
            })

    if len(generations_result) > 0:
        for i, current_generation in enumerate([first_generation, second_generation]):
            generation_result = generations_result[i]
            (
                duration,
                video_url,
                audio_url,
                title,
                lyric,
            ) = (
                int(generation_result.get('duration', 0)),
                generation_result.get('video_url'),
                generation_result.get('audio_url'),
                generation_result.get('title', '🎸'),
                format_lyrics(generation_result.get('lyric', '')),
            )

            reply_markup = build_reaction_keyboard(current_generation.id)
            if user.settings[Model.SUNO][UserSettings.SEND_TYPE] == SendType.VIDEO and video_url:
                answered_message = await send_video(
                    bot=bot,
                    chat_id=user.telegram_chat_id,
                    result=video_url,
                    caption=hlink(get_localization(user_language_code).SETTINGS_SEND_TYPE_AUDIO, audio_url),
                    filename=title,
                    duration=duration,
                    reply_markup=reply_markup,
                )
            elif user.settings[Model.SUNO][UserSettings.SEND_TYPE] == SendType.AUDIO and video_url:
                answered_message = await send_audio(
                    bot=bot,
                    chat_id=user.telegram_chat_id,
                    result=audio_url,
                    caption=hlink(get_localization(user_language_code).SETTINGS_SEND_TYPE_VIDEO, video_url),
                    filename=title,
                    duration=duration,
                    reply_markup=reply_markup,
                )
            else:
                answered_message = await send_audio(
                    bot=bot,
                    chat_id=user.telegram_chat_id,
                    result=audio_url,
                    caption=hlink(get_localization(user_language_code).SETTINGS_SEND_TYPE_AUDIO, audio_url),
                    filename=title,
                    duration=duration,
                    reply_markup=reply_markup,
                )

            if answered_message:
                await bot.send_message(
                    chat_id=user.telegram_chat_id,
                    text=lyric,
                    reply_to_message_id=answered_message.message_id,
                )

    if request.status != RequestStatus.FINISHED:
        request.status = RequestStatus.FINISHED
        await update_request(request.id, {
            'status': request.status
        })

        request_generations = await get_generations_by_request_id(request.id)
        success_generations = []
        for request_generation in request_generations:
            if request_generation.result:
                success_generations.append(request_generation.result)

        total_result = len(success_generations)

        if total_result != len(request_generations):
            await bot.send_sticker(
                chat_id=user.telegram_chat_id,
                sticker=config.MESSAGE_STICKERS.get(MessageSticker.FEAR),
            )
            await bot.send_message(
                chat_id=user.telegram_chat_id,
                text=get_localization(user_language_code).ERROR_REQUEST_FORBIDDEN,
            )

        user = get_user_with_updated_quota(user, Quota.SUNO, total_result)

        product = await get_product_by_quota(Quota.SUNO)
        update_tasks = [
            write_transaction(
                user_id=user.id,
                type=TransactionType.EXPENSE,
                product_id=product.id,
                amount=PRICE_SUNO,
                clear_amount=PRICE_SUNO,
                currency=Currency.USD,
                quantity=total_result,
                details={
                    'mode': request.details.get('mode'),
                    'is_suggestion': request.details.get('is_suggestion', False),
                    'has_error': first_generation.has_error or second_generation.has_error,
                }
            ),
            update_user(user.id, {
                'daily_limits': user.daily_limits,
                'additional_usage_quota': user.additional_usage_quota
            }),
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
        user_language_code = await get_user_language(str(user.id), state.storage)

        if user.current_model == Model.SUNO:
            reply_markup = build_suno_keyboard(user_language_code)
            await bot.send_message(
                chat_id=user.telegram_chat_id,
                text=get_localization(user_language_code).SUNO_INFO,
                reply_markup=reply_markup,
            )
        for processing_message_id in request.processing_message_ids:
            try:
                await bot.delete_message(user.telegram_chat_id, processing_message_id)
            except Exception:
                continue

    return True


def format_lyrics(lyric: str):
    formatted_lines = []
    for line in lyric.splitlines():
        if line.startswith('[') and line.endswith(']'):
            formatted_lines.append(f'\n<b>{line}</b>')
        elif line.strip():
            formatted_lines.append(line)
        else:
            formatted_lines.append('')

    return '\n'.join(formatted_lines)
