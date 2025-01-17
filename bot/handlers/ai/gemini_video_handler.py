import re

from aiogram import Router, Bot, F
from aiogram.exceptions import TelegramBadRequest, TelegramRetryAfter
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.types import Message
from aiogram.utils.chat_action import ChatActionSender
from google.generativeai.types import StopCandidateException, BlockedPromptException

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
from bot.integrations.google import get_response_video_summary
from bot.keyboards.ai.model import build_switched_to_ai_keyboard
from bot.keyboards.common.common import build_error_keyboard
from bot.locales.main import get_user_language, get_localization

gemini_video_router = Router()

PRICE_GEMINI_VIDEO_INPUT = 0
PRICE_GEMINI_VIDEO_OUTPUT = 0


@gemini_video_router.message(Command('video_summary'))
async def gemini_video(message: Message, state: FSMContext):
    await state.clear()

    user_id = str(message.from_user.id)
    user = await get_user(user_id)
    user_language_code = await get_user_language(user_id, state.storage)

    if user.current_model == Model.GEMINI_VIDEO:
        reply_markup = build_switched_to_ai_keyboard(user_language_code, Model.GEMINI_VIDEO)
        await message.answer(
            text=get_localization(user_language_code).MODEL_ALREADY_SWITCHED_TO_THIS_MODEL,
            reply_markup=reply_markup,
        )
    else:
        user.current_model = Model.GEMINI_VIDEO
        await update_user(user_id, {
            'current_model': user.current_model,
        })

        text = await get_switched_to_ai_model(
            user,
            get_quota_by_model(user.current_model, user.settings[user.current_model][UserSettings.VERSION]),
            user_language_code,
        )
        reply_markup = build_switched_to_ai_keyboard(user_language_code, Model.GEMINI_VIDEO)
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

    await message.answer(
        text=get_localization(user_language_code).GEMINI_VIDEO_INFO,
    )


async def handle_gemini_video(message: Message, state: FSMContext, user: User, video_link: str):
    await state.update_data(is_processing=True)

    user_language_code = await get_user_language(user.id, state.storage)

    video_regex = (
        r'^https://.+'
    )
    match = re.search(video_regex, video_link)
    if not match:
        await message.reply(
            text=get_localization(user_language_code).GEMINI_VIDEO_VALUE_ERROR,
            allow_sending_without_reply=True,
        )
        await state.update_data(is_processing=False)
        return

    system_prompt = get_localization(user_language_code).gemini_video_prompt(
        focus=user.settings[Model.GEMINI_VIDEO][UserSettings.FOCUS],
        format=user.settings[Model.GEMINI_VIDEO][UserSettings.FORMAT],
        amount=user.settings[Model.GEMINI_VIDEO][UserSettings.AMOUNT],
    )

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
            response = await get_response_video_summary(
                prompt=system_prompt,
                video_file_link=video_link,
            )
            response_summary = response['message']
            input_price = response['input_tokens'] * PRICE_GEMINI_VIDEO_INPUT
            output_price = response['output_tokens'] * PRICE_GEMINI_VIDEO_OUTPUT

            product = await get_product_by_quota(Quota.GEMINI_VIDEO)

            total_price = round(input_price + output_price, 6)
            await write_transaction(
                user_id=user.id,
                type=TransactionType.EXPENSE,
                product_id=product.id,
                amount=total_price,
                clear_amount=total_price,
                currency=Currency.USD,
                quantity=1,
                details={
                    'input_tokens': response['input_tokens'],
                    'output_tokens': response['output_tokens'],
                    'request': system_prompt,
                    'answer': response_summary,
                    'is_suggestion': False,
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
                footer_text = f'\n\n✉️ {user.daily_limits[Quota.GEMINI_VIDEO] + user.additional_usage_quota[Quota.GEMINI_VIDEO]}' \
                    if user.settings[user.current_model][UserSettings.SHOW_USAGE_QUOTA] and \
                       user.daily_limits[Quota.GEMINI_VIDEO] != float('inf') else ''
                full_text = f"{response_summary}{footer_text}"
                await send_ai_message(
                    message=message,
                    text=full_text,
                    reply_markup=None,
                )

            await update_user_usage_quota(user, Quota.GEMINI_VIDEO, 1)
        except (StopCandidateException, BlockedPromptException):
            await message.answer_sticker(
                sticker=config.MESSAGE_STICKERS.get(MessageSticker.FEAR),
            )
            await message.reply(
                text=get_localization(user_language_code).ERROR_REQUEST_FORBIDDEN,
                allow_sending_without_reply=True,
            )
        except ValueError:
            await message.reply(
                text=get_localization(user_language_code).GEMINI_VIDEO_VALUE_ERROR,
                allow_sending_without_reply=True,
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
                hashtags=['gemini_video'],
            )
        finally:
            await processing_sticker.delete()
            await processing_message.delete()
            await state.update_data(is_processing=False)
