from datetime import timedelta

import aiohttp
from aiogram import Router
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, CallbackQuery, URLInputFile, User as TelegramUser

from bot.database.main import firebase
from bot.database.models.common import Model
from bot.database.models.subscription import SubscriptionStatus, SUBSCRIPTION_FREE_LIMITS
from bot.database.models.user import UserGender, UserSettings
from bot.database.operations.product.getters import get_product, get_product_by_quota
from bot.database.operations.subscription.getters import get_subscription
from bot.database.operations.user.getters import get_user
from bot.database.operations.user.updaters import update_user
from bot.handlers.ai.face_swap_handler import handle_face_swap
from bot.handlers.payment.bonus_handler import handle_bonus
from bot.handlers.payment.payment_handler import (
    handle_subscribe,
    handle_package,
    handle_cancel_subscription,
    handle_renew_subscription,
)
from bot.handlers.settings.settings_handler import handle_settings
from bot.helpers.getters.get_quota_by_model import get_quota_by_model
from bot.keyboards.common.common import build_cancel_keyboard
from bot.keyboards.common.profile import (
    build_profile_keyboard,
    build_profile_quota_keyboard,
)
from bot.locales.main import get_localization, get_user_language
from bot.states.common.profile import Profile

profile_router = Router()


@profile_router.message(Command('profile'))
async def profile(message: Message, state: FSMContext):
    await state.clear()

    await handle_profile(message, state, message.from_user)


async def handle_profile(message: Message, state: FSMContext, telegram_user: TelegramUser):
    user = await get_user(str(telegram_user.id))
    user_language_code = await get_user_language(str(telegram_user.id), state.storage)

    if (
        user.first_name != telegram_user.first_name or
        user.last_name != telegram_user.last_name or
        user.username != telegram_user.username or
        user.is_premium != telegram_user.is_premium or
        user.language_code != telegram_user.language_code
    ):
        await update_user(user.id, {
            'first_name': telegram_user.first_name,
            'last_name': telegram_user.last_name or '',
            'username': telegram_user.username,
            'is_premium': telegram_user.is_premium or False,
            'language_code': telegram_user.language_code,
        })

    subscription = await get_subscription(user.subscription_id)
    if subscription:
        product_subscription = await get_product(subscription.product_id)
        subscription_name = product_subscription.names.get(user_language_code)
        renewal_date = subscription.end_date.strftime('%d.%m.%Y')
    else:
        subscription_name = '🆓'
        renewal_date = (user.last_subscription_limit_update + timedelta(days=30)).strftime('%d.%m.%Y')

    user_current_quota = get_quota_by_model(user.current_model, user.settings[user.current_model][UserSettings.VERSION])
    user_current_model = await get_product_by_quota(user_current_quota)

    text = get_localization(user_language_code).profile(
        subscription_name,
        subscription.status if subscription else SubscriptionStatus.ACTIVE,
        user_current_model.names.get(user_language_code),
        renewal_date,
    )

    reply_markup = build_profile_keyboard(
        user_language_code,
        subscription.status == SubscriptionStatus.ACTIVE
        or subscription.status == SubscriptionStatus.TRIAL
        if subscription
        else False,
        subscription.status == SubscriptionStatus.CANCELED if subscription else False,
    )
    await message.answer(
        text=text,
        reply_markup=reply_markup
   )


@profile_router.callback_query(lambda c: c.data.startswith('profile:'))
async def handle_profile_selection(callback_query: CallbackQuery, state: FSMContext):
    await callback_query.answer()

    user_id = str(callback_query.from_user.id)

    action = callback_query.data.split(':')[1]

    if action == 'open_settings':
        await handle_settings(callback_query.message, user_id, state)
    elif action == 'show_quota':
        await handle_profile_show_quota(callback_query.message, user_id, state)
    elif action == 'open_bonus_info':
        await handle_bonus(callback_query.message, user_id, state)
    elif action == 'open_buy_subscriptions_info':
        await handle_subscribe(callback_query.message, user_id, state)
    elif action == 'open_buy_packages_info':
        await handle_package(callback_query.message, user_id, state)
    elif action == 'cancel_subscription':
        await handle_cancel_subscription(callback_query.message, user_id, state)
    elif action == 'renew_subscription':
        await handle_renew_subscription(callback_query.message, user_id, state)


async def handle_profile_show_quota(message: Message, user_id: str, state: FSMContext):
    user = await get_user(user_id)
    user_language_code = await get_user_language(user_id, state.storage)

    if user.subscription_id:
        user_subscription = await get_subscription(user.subscription_id)
        product_subscription = await get_product(user_subscription.product_id)
        limits = product_subscription.details.get('limits', SUBSCRIPTION_FREE_LIMITS)
    else:
        limits = SUBSCRIPTION_FREE_LIMITS

    await message.reply(
        text=get_localization(user_language_code).profile_quota(
            limits,
            user.daily_limits,
            user.additional_usage_quota,
        ),
        reply_markup=build_profile_quota_keyboard(user_language_code),
        allow_sending_without_reply=True,
    )


@profile_router.callback_query(lambda c: c.data.startswith('profile_gender:'))
async def handle_profile_gender_selection(callback_query: CallbackQuery, state: FSMContext):
    await callback_query.answer()

    user = await get_user(str(callback_query.from_user.id))
    user_language_code = await get_user_language(str(callback_query.from_user.id), state.storage)

    gender = callback_query.data.split(':')[1]

    if user.settings[Model.FACE_SWAP][UserSettings.GENDER] != gender:
        user.settings[Model.FACE_SWAP][UserSettings.GENDER] = gender
        await update_user(user.id, {
            'settings': user.settings,
        })

    text_your_gender = get_localization(user_language_code).PROFILE_YOUR_GENDER
    text_gender_male = get_localization(user_language_code).GENDER_MALE
    text_gender_female = get_localization(user_language_code).GENDER_FEMALE
    await callback_query.message.edit_text(
        f'{text_your_gender} {text_gender_male if user.settings[Model.FACE_SWAP][UserSettings.GENDER] == UserGender.MALE else text_gender_female}'
    )

    if user.current_model == Model.FACE_SWAP:
        await handle_face_swap(
            callback_query.bot,
            str(callback_query.message.chat.id),
            state,
            str(callback_query.from_user.id),
        )
