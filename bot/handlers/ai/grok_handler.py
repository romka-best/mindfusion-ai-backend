import openai
from aiogram import Router
from aiogram.exceptions import TelegramBadRequest, TelegramRetryAfter
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.types import Message
from aiogram.utils.chat_action import ChatActionSender

from bot.config import config, MessageEffect, MessageSticker
from bot.database.main import firebase
from bot.database.models.common import Model, Quota, Currency
from bot.database.models.transaction import TransactionType
from bot.database.models.user import User, UserSettings
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
from bot.integrations.grok import get_response_message
from bot.keyboards.ai.model import build_switched_to_ai_keyboard
from bot.keyboards.common.common import build_continue_generating_keyboard, build_error_keyboard
from bot.locales.main import get_user_language, get_localization
from bot.locales.types import LanguageCode

grok_router = Router()

PRICE_GROK_2_INPUT = 0.000002
PRICE_GROK_2_OUTPUT = 0.00001


@grok_router.message(Command('grok'))
async def grok(message: Message, state: FSMContext):
    await state.clear()

    user_id = str(message.from_user.id)
    user = await get_user(user_id)
    user_language_code = await get_user_language(user_id, state.storage)

    if user.current_model == Model.GROK:
        await message.answer(
            text=get_localization(user_language_code).MODEL_ALREADY_SWITCHED_TO_THIS_MODEL,
            reply_markup=build_switched_to_ai_keyboard(user_language_code, Model.GROK),
        )
    else:
        user.current_model = Model.GROK
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
            reply_markup=build_switched_to_ai_keyboard(user_language_code, Model.GROK),
            message_effect_id=config.MESSAGE_EFFECTS.get(MessageEffect.FIRE),
        )

        try:
            await message.bot.unpin_all_chat_messages(user.telegram_chat_id)
            await message.bot.pin_chat_message(user.telegram_chat_id, answered_message.message_id)
        except (TelegramBadRequest, TelegramRetryAfter):
            pass


async def handle_grok(message: Message, state: FSMContext, user: User, photo_filenames=None):
    await state.update_data(is_processing=True)

    user_language_code = await get_user_language(user.id, state.storage)
    user_data = await state.get_data()

    text = user_data.get('recognized_text', None)
    if not text:
        if message.caption:
            text = message.caption
        elif message.text:
            text = message.text
        else:
            text = ''

    if photo_filenames and len(photo_filenames):
        await write_message(user.current_chat_id, 'user', user.id, text, True, photo_filenames)
    else:
        await write_message(user.current_chat_id, 'user', user.id, text)

    chat = await get_chat(user.current_chat_id)
    if user.subscription_id:
        limit = 12
    else:
        limit = 6
    messages = await get_messages_by_chat_id(
        chat_id=user.current_chat_id,
        limit=limit,
    )
    role = await get_role(chat.role_id)
    sorted_messages = sorted(messages, key=lambda m: m.created_at)
    history = [
        {
            'role': 'system',
            'content': role.translated_instructions.get(user_language_code) or
                       role.translated_instructions.get(LanguageCode.EN),
        },
    ]

    for sorted_message in sorted_messages:
        content = []
        if sorted_message.content:
            content.append({
                'type': 'text',
                'text': sorted_message.content,
            })

        if sorted_message.photo_filenames:
            for photo_filename in sorted_message.photo_filenames:
                photo_path = f'users/vision/{user.id}/{photo_filename}'
                photo = await firebase.bucket.get_blob(photo_path)
                photo_link = firebase.get_public_url(photo.name)
                content.append({
                    'type': 'image_url',
                    'image_url': {
                        'url': photo_link,
                    },
                })

        history.append({
            'role': sorted_message.sender,
            'content': content,
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
            response = await get_response_message(user.settings[user.current_model][UserSettings.VERSION], history)
            response_message = response['message']
            input_price = response['input_tokens'] * PRICE_GROK_2_INPUT
            output_price = response['output_tokens'] * PRICE_GROK_2_OUTPUT

            product = await get_product_by_quota(Quota.GROK_2)

            total_price = round(input_price + output_price, 6)
            message_role, message_content = response_message.role, response_message.content
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
            await create_new_message_and_update_user(transaction, message_role, message_content, user, Quota.GROK_2)

            if user.settings[user.current_model][UserSettings.TURN_ON_VOICE_MESSAGES]:
                reply_markup = build_continue_generating_keyboard(user_language_code)
                await reply_with_voice(
                    message=message,
                    text=message_content,
                    user_id=user.id,
                    reply_markup=reply_markup if response['finish_reason'] == 'length' else None,
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
                footer_text = f'\n\n✉️ {user.daily_limits[Quota.GROK_2] + user.additional_usage_quota[Quota.GROK_2] + 1}' \
                    if user.settings[user.current_model][UserSettings.SHOW_USAGE_QUOTA] and \
                       user.daily_limits[Quota.GROK_2] != float('inf') else ''
                reply_markup = build_continue_generating_keyboard(user_language_code)
                full_text = f"{header_text}{message_content}{footer_text}"
                await send_ai_message(
                    message=message,
                    text=full_text,
                    reply_markup=reply_markup if response['finish_reason'] == 'length' else None,
                )
        except openai.BadRequestError as e:
            if e.code == 'content_policy_violation':
                await message.answer_sticker(
                    sticker=config.MESSAGE_STICKERS.get(MessageSticker.FEAR),
                )
                await message.reply(
                    text=get_localization(user_language_code).ERROR_REQUEST_FORBIDDEN,
                    allow_sending_without_reply=True,
                )
            else:
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
                    hashtags=['grok'],
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
                hashtags=['grok'],
            )
        finally:
            await processing_sticker.delete()
            await processing_message.delete()
            await state.update_data(is_processing=False)
