import asyncio
import base64
from datetime import datetime, timezone

import httpx
from aiogram import Router
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, CallbackQuery, InlineKeyboardButton, InlineKeyboardMarkup
from aiogram.utils.chat_action import ChatActionSender
from filetype import filetype
from google.generativeai.types import StopCandidateException, BlockedPromptException

from bot.config import config, MessageEffect, MessageSticker
from bot.database.main import firebase
from bot.database.models.common import Model, GeminiGPTVersion, Quota, Currency
from bot.database.models.transaction import TransactionType
from bot.database.models.user import UserSettings, User
from bot.database.operations.chat.getters import get_chat
from bot.database.operations.message.getters import get_messages_by_chat_id
from bot.database.operations.message.writers import write_message
from bot.database.operations.product.getters import get_product_by_quota
from bot.database.operations.role.getters import get_role
from bot.database.operations.transaction.writers import write_transaction
from bot.database.operations.user.getters import get_user
from bot.database.operations.user.updaters import update_user
from bot.helpers.creaters.create_new_message_and_update_user import create_new_message_and_update_user
from bot.helpers.getters.get_quota_by_model import get_quota_by_model
from bot.helpers.getters.get_switched_to_ai_model import get_switched_to_ai_model
from bot.helpers.reply_with_voice import reply_with_voice
from bot.helpers.senders.send_ai_message import send_ai_message
from bot.helpers.senders.send_error_info import send_error_info
from bot.integrations.google import get_response_message
from bot.keyboards.ai.gemini import build_gemini_keyboard
from bot.keyboards.ai.model import build_switched_to_ai_keyboard
from bot.keyboards.common.common import (
    build_error_keyboard,
    build_continue_generating_keyboard,
    build_buy_motivation_keyboard,
)
from bot.locales.main import get_user_language, get_localization
from bot.locales.types import LanguageCode

gemini_router = Router()

PRICE_GEMINI_2_FLASH_INPUT = 0
PRICE_GEMINI_2_FLASH_OUTPUT = 0
PRICE_GEMINI_1_PRO_INPUT = 0.00000125
PRICE_GEMINI_1_PRO_OUTPUT = 0.000005
PRICE_GEMINI_1_ULTRA_INPUT = 0.00000125
PRICE_GEMINI_1_ULTRA_OUTPUT = 0.000005


@gemini_router.message(Command('gemini'))
async def gemini(message: Message, state: FSMContext):
    await state.clear()

    user_id = str(message.from_user.id)
    user = await get_user(user_id)
    user_language_code = await get_user_language(user_id, state.storage)

    reply_markup = build_gemini_keyboard(
        user_language_code,
        user.current_model,
        user.settings[Model.GEMINI][UserSettings.VERSION],
    )
    await message.answer(
        text=get_localization(user_language_code).MODEL_CHOOSE_GEMINI,
        reply_markup=reply_markup,
    )


@gemini_router.callback_query(lambda c: c.data.startswith('gemini:'))
async def handle_gemini_choose_selection(callback_query: CallbackQuery, state: FSMContext):
    await callback_query.answer()

    user_id = str(callback_query.from_user.id)
    user = await get_user(user_id)
    user_language_code = await get_user_language(user_id, state.storage)

    chosen_version = callback_query.data.split(':')[1]

    if user.current_model == Model.GEMINI and chosen_version == user.settings[Model.GEMINI][UserSettings.VERSION]:
        reply_markup = build_switched_to_ai_keyboard(user_language_code, Model.GEMINI)
        await callback_query.message.answer(
            text=get_localization(user_language_code).MODEL_ALREADY_SWITCHED_TO_THIS_MODEL,
            reply_markup=reply_markup,
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

        reply_markup = build_switched_to_ai_keyboard(user_language_code, Model.GEMINI)
        if keyboard_changed:
            user.current_model = Model.GEMINI
            user.settings[Model.GEMINI][UserSettings.VERSION] = chosen_version
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

            await callback_query.bot.unpin_all_chat_messages(user.telegram_chat_id)
            await callback_query.bot.pin_chat_message(user.telegram_chat_id, answered_message.message_id)
        else:
            text = get_localization(user_language_code).MODEL_ALREADY_SWITCHED_TO_THIS_MODEL
            await callback_query.message.answer(
                text=text,
                reply_markup=reply_markup,
            )

    await state.clear()


async def handle_gemini(
    message: Message,
    state: FSMContext,
    user: User,
    user_quota: Quota,
    filenames=None,
    single_mode=False,
):
    if user_quota != Quota.GEMINI_2_FLASH and user_quota != Quota.GEMINI_1_PRO and user_quota != Quota.GEMINI_1_ULTRA:
        raise NotImplementedError(f'User quota is not implemented: {user_quota}')

    await state.update_data(is_processing=True)

    user_language_code = await get_user_language(user.id, state.storage)
    user_data = await state.get_data()

    text = user_data.get('recognized_text', None)
    if text is None:
        if message.caption:
            text = message.caption
        elif message.text:
            text = message.text
        else:
            text = ''

    if filenames and len(filenames):
        await write_message(user.current_chat_id, 'user', user.id, text, True, filenames)
    else:
        await write_message(user.current_chat_id, 'user', user.id, text)

    chat = await get_chat(user.current_chat_id)
    if not user.subscription_id:
        limit = 6
    elif user_quota == Quota.GEMINI_1_ULTRA:
        limit = 20
    else:
        limit = 12
    messages = await get_messages_by_chat_id(
        chat_id=user.current_chat_id,
        limit=limit,
    )
    role = await get_role(chat.role_id)
    sorted_messages = sorted(messages, key=lambda m: m.created_at)
    if single_mode:
        sorted_messages = [sorted_messages[-1]]
    system_prompt = role.translated_instructions.get(user_language_code) or \
                    role.translated_instructions.get(LanguageCode.EN)
    history = []
    for sorted_message in sorted_messages:
        parts = []
        if sorted_message.content:
            parts.append(sorted_message.content)

        if sorted_message.photo_filenames:
            for photo_filename in sorted_message.photo_filenames:
                photo_path = f'users/vision/{user.id}/{photo_filename}'
                photo = await firebase.bucket.get_blob(photo_path)
                photo_link = firebase.get_public_url(photo.name)

                async with httpx.AsyncClient() as client:
                    response = await client.get(photo_link)
                    response_content = response.content

                kind = await asyncio.to_thread(lambda: filetype.guess(response_content))
                if kind:
                    media_type = kind.mime
                else:
                    media_type = 'image/jpeg'

                if not media_type.startswith('image') and not single_mode:
                    continue

                data = await asyncio.to_thread(lambda: base64.b64encode(response_content).decode('utf-8'))
                parts.append({
                    'mime_type': media_type,
                    'data': data,
                })

        if parts:
            history.append({
                'role': sorted_message.sender if sorted_message.sender == 'user' else 'model',
                'parts': parts,
            })

    processing_sticker = await message.answer_sticker(
        sticker=config.MESSAGE_STICKERS.get(MessageSticker.TEXT_GENERATION),
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
            response = await get_response_message(
                model_version=user.settings[user.current_model][UserSettings.VERSION],
                system_prompt=system_prompt,
                history=history,
            )
            response_message = response['message']
            if user_quota == Quota.GEMINI_2_FLASH:
                input_price = response['input_tokens'] * PRICE_GEMINI_2_FLASH_INPUT
                output_price = response['output_tokens'] * PRICE_GEMINI_2_FLASH_OUTPUT
            elif user_quota == Quota.GEMINI_1_PRO:
                input_price = response['input_tokens'] * PRICE_GEMINI_1_PRO_INPUT
                output_price = response['output_tokens'] * PRICE_GEMINI_1_PRO_OUTPUT
            elif user_quota == Quota.GEMINI_1_ULTRA:
                input_price = response['input_tokens'] * PRICE_GEMINI_1_ULTRA_INPUT
                output_price = response['output_tokens'] * PRICE_GEMINI_1_ULTRA_OUTPUT

            product = await get_product_by_quota(user_quota)

            total_price = round(input_price + output_price, 6)
            message_role, message_content = 'assistant', response_message
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
                    'request': text,
                    'answer': message_content,
                    'is_suggestion': False,
                    'has_error': False,
                },
            )

            transaction = firebase.db.transaction()
            await create_new_message_and_update_user(transaction, message_role, message_content, user, user_quota)

            if user.settings[user.current_model][UserSettings.TURN_ON_VOICE_MESSAGES]:
                reply_markup = build_continue_generating_keyboard(user_language_code)
                await reply_with_voice(
                    message=message,
                    text=message_content,
                    user_id=user.id,
                    reply_markup=reply_markup if response['finish_reason'] == 'MAX_TOKENS' else None,
                    voice=user.settings[user.current_model][UserSettings.VOICE],
                )
            else:
                chat_info = f'💬 {chat.title}\n' if (
                    user.settings[user.current_model][UserSettings.SHOW_THE_NAME_OF_THE_CHATS]
                ) else ''
                role_info = f'{role.translated_names.get(user_language_code) or role.translated_names.get(LanguageCode.EN)}\n' if (
                    user.settings[user.current_model][UserSettings.SHOW_THE_NAME_OF_THE_ROLES]
                ) else ''
                header_text = f'{chat_info}{role_info}\n' if chat_info or role_info else ''
                footer_text = f'\n\n✉️ {user.daily_limits[user_quota] + user.additional_usage_quota[user_quota] + 1}' \
                    if user.settings[user.current_model][UserSettings.SHOW_USAGE_QUOTA] and \
                       user.daily_limits[user_quota] != float('inf') else ''
                reply_markup = build_continue_generating_keyboard(user_language_code)
                full_text = f'{header_text}{message_content}{footer_text}'
                await send_ai_message(
                    message=message,
                    text=full_text,
                    reply_markup=reply_markup if response['finish_reason'] == 'MAX_TOKENS' else None,
                )
        except (StopCandidateException, BlockedPromptException):
            await message.answer_sticker(
                sticker=config.MESSAGE_STICKERS.get(MessageSticker.FEAR),
            )
            await message.reply(
                text=get_localization(user_language_code).ERROR_REQUEST_FORBIDDEN,
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
                hashtags=['gemini'],
            )
        finally:
            await processing_sticker.delete()
            await processing_message.delete()
            await state.update_data(is_processing=False)

    asyncio.create_task(
        handle_gemini_1_pro_example(
            user=user,
            user_language_code=user_language_code,
            prompt=text,
            system_prompt=system_prompt,
            history=history,
            message=message,
        )
    )


async def handle_gemini_1_pro_example(
    user: User,
    user_language_code: LanguageCode,
    prompt: str,
    system_prompt: str,
    history: list,
    message: Message,
):
    try:
        current_date = datetime.now(timezone.utc)
        if (
            not user.subscription_id and
            user.current_model == Model.GEMINI and
            user.settings[user.current_model][UserSettings.SHOW_EXAMPLES] and
            user.daily_limits[Quota.GEMINI_2_FLASH] + 1 in [3, 7] and
            (current_date - user.last_subscription_limit_update).days <= 3
        ):
            response = await get_response_message(
                model_version=GeminiGPTVersion.V1_Pro,
                system_prompt=system_prompt,
                history=history,
            )
            response_message = response['message']

            product = await get_product_by_quota(Quota.GEMINI_1_PRO)

            input_price = response['input_tokens'] * PRICE_GEMINI_1_PRO_INPUT
            output_price = response['output_tokens'] * PRICE_GEMINI_1_PRO_OUTPUT

            total_price = round(input_price + output_price, 6)
            message_role, message_content = 'assistant', response_message
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
                    'request': prompt,
                    'answer': message_content,
                    'is_suggestion': True,
                    'has_error': False,
                },
            )

            header_text = f'{get_localization(user_language_code).example_text_model(get_localization(user_language_code).GEMINI_1_PRO)}\n\n'
            footer_text = f'\n{get_localization(user_language_code).EXAMPLE_INFO}'
            full_text = f'{header_text}{message_content}{footer_text}'
            reply_markup = build_buy_motivation_keyboard(user_language_code)
            await send_ai_message(
                message=message,
                text=full_text,
                reply_markup=reply_markup,
            )
    except Exception as e:
        await send_error_info(
            bot=message.bot,
            user_id=user.id,
            info=str(e),
            hashtags=['gemini', 'example'],
        )
