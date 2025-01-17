import openai
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
from bot.integrations.open_ai import get_response_image, get_cost_for_image
from bot.keyboards.ai.model import build_switched_to_ai_keyboard, build_model_limit_exceeded_keyboard
from bot.keyboards.common.common import build_error_keyboard
from bot.locales.main import get_localization, get_user_language

dall_e_router = Router()

PRICE_DALL_E = 0.04


@dall_e_router.message(Command('dalle'))
async def dall_e(message: Message, state: FSMContext):
    await state.clear()

    user_id = str(message.from_user.id)
    user = await get_user(user_id)
    user_language_code = await get_user_language(user_id, state.storage)

    if user.current_model == Model.DALL_E:
        reply_markup = build_switched_to_ai_keyboard(user_language_code, Model.DALL_E)
        await message.answer(
            text=get_localization(user_language_code).MODEL_ALREADY_SWITCHED_TO_THIS_MODEL,
            reply_markup=reply_markup,
        )
    else:
        user.current_model = Model.DALL_E
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
            reply_markup=build_switched_to_ai_keyboard(user_language_code, Model.DALL_E),
            message_effect_id=config.MESSAGE_EFFECTS.get(MessageEffect.FIRE),
        )

        try:
            await message.bot.unpin_chat_message(user.telegram_chat_id)
            await message.bot.pin_chat_message(user.telegram_chat_id, answered_message.message_id)
        except (TelegramBadRequest, TelegramRetryAfter):
            pass


async def handle_dall_e(message: Message, state: FSMContext, user: User):
    await state.update_data(is_processing=True)

    user_language_code = await get_user_language(user.id, state.storage)
    user_data = await state.get_data()

    text = user_data.get('recognized_text', None)
    if text is None:
        text = message.text

    processing_sticker = await message.answer_sticker(
        sticker=config.MESSAGE_STICKERS.get(MessageSticker.IMAGE_GENERATION),
    )
    processing_message = await message.reply(
        text=get_localization(user_language_code).model_image_processing_request(),
        allow_sending_without_reply=True,
    )

    async with ChatActionSender.upload_photo(bot=message.bot, chat_id=message.chat.id):
        try:
            maximum_generations = user.daily_limits[Quota.DALL_E] + user.additional_usage_quota[Quota.DALL_E]
            resolution = user.settings[Model.DALL_E][UserSettings.RESOLUTION]
            quality = user.settings[Model.DALL_E][UserSettings.QUALITY]
            cost = get_cost_for_image(quality, resolution)
            if maximum_generations < cost:
                await message.answer_sticker(
                    sticker=config.MESSAGE_STICKERS.get(MessageSticker.SAD),
                )

                reply_markup = build_model_limit_exceeded_keyboard(user_language_code)
                await message.reply(
                    text=get_localization(user_language_code).model_reached_usage_limit(),
                    reply_markup=reply_markup,
                    allow_sending_without_reply=True,
                )
                return

            response_url = await get_response_image(
                user.settings[Model.DALL_E][UserSettings.VERSION],
                text,
                resolution,
                quality,
            )

            product = await get_product_by_quota(Quota.DALL_E)

            total_price = PRICE_DALL_E * cost
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

            footer_text = f'\n\n🖼 {user.daily_limits[Quota.DALL_E] + user.additional_usage_quota[Quota.DALL_E]}' \
                if user.settings[Model.DALL_E][UserSettings.SHOW_USAGE_QUOTA] and \
                   user.daily_limits[Quota.DALL_E] != float('inf') else ''
            if user.settings[Model.DALL_E][UserSettings.SEND_TYPE] == SendType.DOCUMENT:
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

            await update_user_usage_quota(user, Quota.DALL_E, cost)
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

                reply_markup = build_error_keyboard(user_language_code)
                await message.answer(
                    text=get_localization(user_language_code).ERROR,
                    reply_markup=reply_markup,
                )
                await send_error_info(
                    bot=message.bot,
                    user_id=user.id,
                    info=str(e),
                    hashtags=['dalle'],
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
                hashtags=['dalle'],
            )
        finally:
            await processing_sticker.delete()
            await processing_message.delete()
            await state.update_data(is_processing=False)
