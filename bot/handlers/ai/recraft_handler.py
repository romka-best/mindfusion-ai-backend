from aiogram import Router
from aiogram.exceptions import TelegramBadRequest, TelegramRetryAfter
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.types import Message
from aiogram.utils.chat_action import ChatActionSender

from bot.config import config, MessageEffect, MessageSticker
from bot.database.models.common import Quota, Currency, Model, SendType
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
from bot.integrations.recraft import get_response_image
from bot.keyboards.ai.model import build_switched_to_ai_keyboard
from bot.keyboards.common.common import build_error_keyboard
from bot.locales.main import get_localization, get_user_language

recraft_router = Router()

PRICE_RECRAFT = 0.04


@recraft_router.message(Command('recraft'))
async def recraft(message: Message, state: FSMContext):
    await state.clear()

    user_id = str(message.from_user.id)
    user = await get_user(user_id)
    user_language_code = await get_user_language(user_id, state.storage)

    if user.current_model == Model.RECRAFT:
        await message.answer(
            text=get_localization(user_language_code).MODEL_ALREADY_SWITCHED_TO_THIS_MODEL,
            reply_markup=build_switched_to_ai_keyboard(user_language_code, Model.RECRAFT),
        )
    else:
        user.current_model = Model.RECRAFT
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
            reply_markup=build_switched_to_ai_keyboard(user_language_code, Model.RECRAFT),
            message_effect_id=config.MESSAGE_EFFECTS.get(MessageEffect.FIRE),
        )

        try:
            await message.bot.unpin_all_chat_messages(user.telegram_chat_id)
            await message.bot.pin_chat_message(user.telegram_chat_id, answered_message.message_id)
        except (TelegramBadRequest, TelegramRetryAfter):
            pass


async def handle_recraft(message: Message, state: FSMContext, user: User):
    await state.update_data(is_processing=True)

    user_language_code = await get_user_language(user.id, state.storage)
    user_data = await state.get_data()

    text = user_data.get('recognized_text', None)
    if text is None:
        text = message.text

    if not text:
        await message.answer(
            text=get_localization(user_language_code).ERROR_PROMPT_REQUIRED,
            reply_markup=build_error_keyboard(user_language_code),
        )
        await state.update_data(is_processing=False)
        return

    if len(text) > 1000:
        await message.answer(
            text=get_localization(user_language_code).ERROR_PROMPT_TOO_LONG,
            reply_markup=build_error_keyboard(user_language_code),
        )
        await state.update_data(is_processing=False)
        return

    processing_sticker = await message.answer_sticker(
        sticker=config.MESSAGE_STICKERS.get(MessageSticker.IMAGE_GENERATION),
    )
    processing_message = await message.reply(
        text=get_localization(user_language_code).model_image_processing_request(),
        allow_sending_without_reply=True,
    )

    async with ChatActionSender.upload_photo(bot=message.bot, chat_id=message.chat.id):
        try:
            response_url = await get_response_image(
                text,
                user.settings[Model.RECRAFT][UserSettings.VERSION],
                user.settings[Model.RECRAFT][UserSettings.ASPECT_RATIO],
            )

            product = await get_product_by_quota(Quota.RECRAFT)

            total_price = PRICE_RECRAFT
            await write_transaction(
                user_id=user.id,
                type=TransactionType.EXPENSE,
                product_id=product.id,
                amount=total_price,
                clear_amount=total_price,
                currency=Currency.USD,
                quantity=1,
                details={
                    'text': text,
                    'has_error': False,
                },
            )

            footer_text = f'\n\n🖼 {user.daily_limits[Quota.RECRAFT] + user.additional_usage_quota[Quota.RECRAFT]}' \
                if user.settings[Model.RECRAFT][UserSettings.SHOW_USAGE_QUOTA] and \
                   user.daily_limits[Quota.RECRAFT] != float('inf') else ''
            if user.settings[Model.RECRAFT][UserSettings.SEND_TYPE] == SendType.DOCUMENT:
                await message.reply_document(
                    caption=f'{get_localization(user_language_code).GENERATION_IMAGE_SUCCESS}{footer_text}',
                    document=response_url,
                    allow_sending_without_reply=True,
                )
            else:
                await message.reply_photo(
                    caption=f'{get_localization(user_language_code).GENERATION_IMAGE_SUCCESS}{footer_text}',
                    photo=response_url,
                    allow_sending_without_reply=True,
                )

            await update_user_usage_quota(user, Quota.RECRAFT, 1)
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
                hashtags=['recraft'],
            )
        finally:
            await processing_sticker.delete()
            await processing_message.delete()
            await state.update_data(is_processing=False)
