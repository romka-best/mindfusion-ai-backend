from typing import Optional
import re

import runwayml
from aiogram import Router
from aiogram.exceptions import TelegramBadRequest, TelegramRetryAfter
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.types import Message
from aiogram.utils.chat_action import ChatActionSender

from bot.config import config, MessageEffect, MessageSticker
from bot.database.models.common import Model, Quota, Currency, SendType
from bot.database.models.transaction import TransactionType
from bot.database.models.user import UserSettings, User
from bot.database.operations.product.getters import get_product_by_quota
from bot.database.operations.transaction.writers import write_transaction
from bot.database.operations.user.getters import get_user
from bot.database.operations.user.updaters import update_user
from bot.helpers.getters.get_quota_by_model import get_quota_by_model
from bot.helpers.getters.get_switched_to_ai_model import get_switched_to_ai_model
from bot.helpers.senders.send_error_info import send_error_info
from bot.helpers.updaters.update_user_usage_quota import update_user_usage_quota
from bot.integrations.runway import get_response_video, get_cost_for_video
from bot.keyboards.ai.model import build_switched_to_ai_keyboard
from bot.keyboards.common.common import build_error_keyboard
from bot.locales.main import get_user_language, get_localization
from bot.locales.translate_text import translate_text
from bot.locales.types import LanguageCode
from bot.helpers.senders.send_ai_model_internal_error import send_internal_ai_model_error

runway_router = Router()

PRICE_RUNWAY = 0.25


@runway_router.message(Command('runway'))
async def runway(message: Message, state: FSMContext):
    await state.clear()

    user_id = str(message.from_user.id)
    user = await get_user(user_id)
    user_language_code = await get_user_language(user_id, state.storage)

    if user.current_model == Model.RUNWAY:
        await message.answer(
            text=get_localization(user_language_code).MODEL_ALREADY_SWITCHED_TO_THIS_MODEL,
            reply_markup=build_switched_to_ai_keyboard(user_language_code, Model.RUNWAY),
        )
    else:
        user.current_model = Model.RUNWAY
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
            reply_markup=build_switched_to_ai_keyboard(user_language_code, Model.RUNWAY),
            message_effect_id=config.MESSAGE_EFFECTS.get(MessageEffect.FIRE),
        )

        try:
            await message.bot.unpin_all_chat_messages(user.telegram_chat_id)
            await message.bot.pin_chat_message(user.telegram_chat_id, answered_message.message_id)
        except (TelegramBadRequest, TelegramRetryAfter):
            pass


async def handle_runway(message: Message, state: FSMContext, user: User, video_frame_link: Optional[str] = None):
    await state.update_data(is_processing=True)

    user_language_code = await get_user_language(user.id, state.storage)
    user_data = await state.get_data()

    if not video_frame_link:
        await message.reply(
            text=get_localization(user_language_code).ERROR_PHOTO_REQUIRED,
            allow_sending_without_reply=True,
        )
        await state.update_data(is_processing=False)
        return

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
        try:
            model_version = user.settings[Model.RUNWAY][UserSettings.VERSION]
            resolution = user.settings[Model.RUNWAY][UserSettings.RESOLUTION]
            duration = user.settings[Model.RUNWAY][UserSettings.DURATION]

            cost = get_cost_for_video(duration)

            if prompt and user_language_code != LanguageCode.EN:
                prompt = await translate_text(prompt, user_language_code, LanguageCode.EN)

            if len(prompt) > 512:
                await message.reply(
                    text=get_localization(user_language_code).ERROR_PROMPT_TOO_LONG,
                    allow_sending_without_reply=True,
                )
                return

            response = await get_response_video(
                model_version,
                prompt,
                video_frame_link,
                resolution,
                duration,
            )

            product = await get_product_by_quota(Quota.RUNWAY)

            total_price = PRICE_RUNWAY * cost
            await write_transaction(
                user_id=user.id,
                type=TransactionType.EXPENSE,
                product_id=product.id,
                amount=total_price,
                clear_amount=total_price,
                currency=Currency.USD,
                quantity=1,
                details={
                    'prompt_text': prompt,
                    'prompt_image': video_frame_link,
                    'resolution': resolution,
                    'duration': duration,
                    'has_error': False,
                },
            )

            footer_text = f'\n\n📹 {user.daily_limits[Quota.RUNWAY] + user.additional_usage_quota[Quota.RUNWAY]}' \
                if user.settings[Model.RUNWAY][UserSettings.SHOW_USAGE_QUOTA] and \
                   user.daily_limits[Quota.RUNWAY] != float('inf') else ''

            if user.settings[Model.RUNWAY][UserSettings.SEND_TYPE] == SendType.DOCUMENT:
                await message.reply_document(
                    caption=f'{get_localization(user_language_code).GENERATION_VIDEO_SUCCESS}{footer_text}',
                    document=response.get('result', [])[0],
                    allow_sending_without_reply=True,
                )
            else:
                await message.reply_video(
                    caption=f'{get_localization(user_language_code).GENERATION_VIDEO_SUCCESS}{footer_text}',
                    video=response.get('result', [])[0],
                    allow_sending_without_reply=True,
                )

            await update_user_usage_quota(user, Quota.RUNWAY, cost)
        except runwayml.RateLimitError:
            await message.reply(
                text=get_localization(user_language_code).ERROR_SERVER_OVERLOADED,
                allow_sending_without_reply=True,
            )
        except runwayml.BadRequestError as e:
            error_message = e.body.get('error', '')

            if 'invalid asset aspect ratio' in error_message.lower():
                matches = re.search(
                    r'between (?P<min_ratio>\d+(\.\d+)?) '
                    r'and (?P<max_ratio>\d+(\.\d+)?)\. '
                    r'Got (?P<actual_ratio>\d+(\.\d+)?)',
                    error_message,
                )

                min_ratio, max_ratio, actual_ratio = matches.groupdict().values()

                await message.answer_sticker(
                    sticker=config.MESSAGE_STICKERS.get(MessageSticker.ERROR),
                )
                await message.answer(
                    text=get_localization(user_language_code).error_aspect_ratio_invalid(
                        min_ratio,
                        max_ratio,
                        actual_ratio,
                    ),
                )
            elif 'safety' in error_message.lower():
                await message.answer_sticker(
                    sticker=config.MESSAGE_STICKERS.get(MessageSticker.FEAR),
                )
                await message.answer(
                    text=get_localization(user_language_code).ERROR_REQUEST_FORBIDDEN,
                )
            else:
                raise e
        except runwayml.InternalServerError:
            await send_internal_ai_model_error(
                user_language_code, message, Model.RUNWAY
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
                hashtags=['runway'],
            )
        finally:
            await processing_sticker.delete()
            await processing_message.delete()
            await state.update_data(is_processing=False)
