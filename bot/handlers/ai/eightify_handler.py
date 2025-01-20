import re

import aiohttp
from aiogram import Router
from aiogram.exceptions import TelegramBadRequest, TelegramRetryAfter
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.types import Message
from aiogram.utils.chat_action import ChatActionSender

from bot.config import config, MessageEffect, MessageSticker
from bot.database.models.common import Model, Quota, Currency
from bot.database.models.transaction import TransactionType
from bot.database.models.user import UserSettings, User
from bot.database.operations.product.getters import get_product_by_quota
from bot.database.operations.transaction.writers import write_transaction
from bot.database.operations.user.getters import get_user
from bot.database.operations.user.updaters import update_user
from bot.helpers.getters.get_quota_by_model import get_quota_by_model
from bot.helpers.getters.get_switched_to_ai_model import get_switched_to_ai_model
from bot.helpers.reply_with_voice import reply_with_voice
from bot.helpers.senders.send_ai_message import send_ai_message
from bot.helpers.senders.send_error_info import send_error_info
from bot.helpers.updaters.update_user_usage_quota import update_user_usage_quota
from bot.integrations.eightify import generate_summary
from bot.keyboards.ai.model import build_switched_to_ai_keyboard, build_model_limit_exceeded_keyboard
from bot.keyboards.common.common import build_error_keyboard
from bot.locales.main import get_user_language, get_localization

eightify_router = Router()


@eightify_router.message(Command('youtube_summary'))
async def eightify(message: Message, state: FSMContext):
    await state.clear()

    user_id = str(message.from_user.id)
    user = await get_user(user_id)
    user_language_code = await get_user_language(user_id, state.storage)

    if user.current_model == Model.EIGHTIFY:
        await message.answer(
            text=get_localization(user_language_code).MODEL_ALREADY_SWITCHED_TO_THIS_MODEL,
            reply_markup=build_switched_to_ai_keyboard(user_language_code, Model.EIGHTIFY),
        )
    else:
        user.current_model = Model.EIGHTIFY
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
            reply_markup=build_switched_to_ai_keyboard(user_language_code, Model.EIGHTIFY),
            message_effect_id=config.MESSAGE_EFFECTS.get(MessageEffect.FIRE),
        )

        try:
            await message.bot.unpin_chat_message(user.telegram_chat_id)
            await message.bot.pin_chat_message(user.telegram_chat_id, answered_message.message_id)
        except (TelegramBadRequest, TelegramRetryAfter):
            pass

    await message.answer(
        text=get_localization(user_language_code).EIGHTIFY_INFO,
    )


async def handle_eightify(message: Message, state: FSMContext, user: User):
    await state.update_data(is_processing=True)

    user_language_code = await get_user_language(str(user.id), state.storage)

    link = message.text
    if link is None:
        await message.reply(
            text=get_localization(user_language_code).EIGHTIFY_VALUE_ERROR,
            allow_sending_without_reply=True,
        )
        return

    youtube_regex = (
        r'(?:https?://)?(?:www\.)?(?:youtube\.com/watch\?v=|youtu\.be/)([\w-]{11})'
    )
    match = re.search(youtube_regex, link)
    if match:
        video_id = match.group(1)
    else:
        await message.reply(
            text=get_localization(user_language_code).EIGHTIFY_VALUE_ERROR,
            allow_sending_without_reply=True,
        )
        return

    processing_sticker = await message.answer_sticker(
        sticker=config.MESSAGE_STICKERS.get(MessageSticker.SUMMARY_GENERATION),
    )
    processing_message = await message.reply(
        text=get_localization(user_language_code).model_text_processing_request(),
        allow_sending_without_reply=True,
    )

    if user.settings[user.current_model][UserSettings.TURN_ON_VOICE_MESSAGES]:
        chat_action_sender = ChatActionSender.record_voice
    else:
        chat_action_sender = ChatActionSender.typing

    async with chat_action_sender(bot=message.bot, chat_id=message.chat.id):
        try:
            quota = user.daily_limits[Quota.EIGHTIFY] + user.additional_usage_quota[Quota.EIGHTIFY]
            if quota < 1:
                await message.answer_sticker(
                    sticker=config.MESSAGE_STICKERS.get(MessageSticker.SAD),
                )

                await message.answer(
                    text=get_localization(user_language_code).model_reached_usage_limit(),
                    reply_markup=build_model_limit_exceeded_keyboard(user_language_code),
                )

                await processing_sticker.delete()
                await processing_message.delete()
            else:
                product = await get_product_by_quota(Quota.EIGHTIFY)

                response_summary = await generate_summary(
                    language_code=user_language_code,
                    video_id=video_id,
                    focus=user.settings[Model.EIGHTIFY][UserSettings.FOCUS],
                    format=user.settings[Model.EIGHTIFY][UserSettings.FORMAT],
                    amount=user.settings[Model.EIGHTIFY][UserSettings.AMOUNT],
                )

                await write_transaction(
                    user_id=user.id,
                    type=TransactionType.EXPENSE,
                    product_id=product.id,
                    amount=0,
                    clear_amount=0,
                    currency=Currency.USD,
                    quantity=1,
                    details={
                        'request': link,
                        'answer': response_summary,
                        'has_error': False,
                    },
                )

                if user.settings[user.current_model][UserSettings.TURN_ON_VOICE_MESSAGES]:
                    await reply_with_voice(
                        message=message,
                        text=response_summary,
                        user_id=user.id,
                        reply_markup=None,
                        voice=user.settings[user.current_model][UserSettings.VOICE],
                    )
                else:
                    footer_text = f'\n\n✉️ {user.daily_limits[Quota.EIGHTIFY] + user.additional_usage_quota[Quota.EIGHTIFY]}' \
                        if user.settings[user.current_model][UserSettings.SHOW_USAGE_QUOTA] and \
                           user.daily_limits[Quota.EIGHTIFY] != float('inf') else ''
                    full_text = f"{response_summary}{footer_text}"
                    await send_ai_message(
                        message=message,
                        text=full_text,
                        reply_markup=None,
                    )

                await update_user_usage_quota(user, Quota.EIGHTIFY, 1)
        except aiohttp.ClientResponseError:
            await message.answer_sticker(
                sticker=config.MESSAGE_STICKERS.get(MessageSticker.SAD),
            )

            await message.answer(
                text=get_localization(user_language_code).EIGHTIFY_VIDEO_ERROR,
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
                hashtags=['eightify'],
            )
        finally:
            await processing_sticker.delete()
            await processing_message.delete()
            await state.update_data(is_processing=False)

            await state.clear()
