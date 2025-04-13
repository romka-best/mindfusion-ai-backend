import asyncio
import logging
import traceback
from datetime import datetime, timezone

from aiogram import Bot
from aiogram.exceptions import TelegramForbiddenError
from aiogram.fsm.storage.base import BaseStorage
from google.cloud.firestore_v1 import AsyncWriteBatch, FieldFilter

from bot.config import config, MessageSticker
from bot.database.main import firebase
from bot.database.models.common import Quota, PaymentMethod
from bot.database.models.subscription import (
    SubscriptionStatus,
    SUBSCRIPTION_FREE_LIMITS,
)
from bot.database.models.user import User, UserSettings
from bot.database.operations.chat.getters import get_chats_by_user_id
from bot.database.operations.chat.updaters import update_chat
from bot.database.operations.package.getters import get_packages_by_user_id
from bot.database.operations.product.getters import get_product
from bot.database.operations.subscription.getters import get_subscription, get_activated_subscriptions_by_user_id
from bot.database.operations.subscription.updaters import update_subscription
from bot.database.operations.user.updaters import update_user
from bot.helpers.billing.create_auto_payment import create_auto_payment
from bot.helpers.billing.create_payment import OrderItem
from bot.helpers.notifiers.notify_user_about_quota import notify_user_about_quota
from bot.helpers.senders.send_message_to_admins_and_developers import send_message_to_admins_and_developers
from bot.helpers.senders.send_message_to_users import send_message_to_user
from bot.helpers.senders.send_sticker import send_sticker
from bot.keyboards.common.common import build_buy_motivation_keyboard
from bot.locales.main import get_localization, get_user_language


async def update_daily_limits(bot: Bot, storage: BaseStorage):
    users_query = firebase.db.collection(User.COLLECTION_NAME).limit(config.BATCH_SIZE)
    is_running = True
    last_doc = None

    while is_running:
        if last_doc:
            users_query = users_query.start_after(last_doc)

        docs = users_query.stream()

        tasks = []
        batch = firebase.db.batch()

        count = 0
        async for doc in docs:
            count += 1

            user = User(**doc.to_dict())

            await update_user_daily_limits(bot, user, batch, storage)

            if not user.subscription_id:
                tasks.append(
                    notify_user_about_quota(
                        bot=bot,
                        user=user,
                        storage=storage,
                    )
                )

        await batch.commit()
        await asyncio.gather(*tasks, return_exceptions=True)

        if count < config.BATCH_SIZE:
            is_running = False
            break

        last_doc = doc

    await send_message_to_admins_and_developers(bot, f'<b>Updated Daily Limits Successfully</b> 🎉')


async def update_user_daily_limits(bot: Bot, user: User, batch: AsyncWriteBatch, storage: BaseStorage):
    try:
        user = await update_user_subscription(bot, user, batch, storage)
        await update_user_additional_usage_quota(bot, user, bool(user.subscription_id), batch, storage)
    except TelegramForbiddenError:
        await update_user(user.id, {
            'is_blocked': True,
        })
    except Exception:
        error_trace = traceback.format_exc()
        logging.exception(f'Error updating user {user.id}: {error_trace}')


async def update_user_subscription(bot: Bot, user: User, batch: AsyncWriteBatch, storage: BaseStorage):
    user_ref = firebase.db.collection(User.COLLECTION_NAME).document(user.id)
    current_date = datetime.now(timezone.utc)
    current_subscription = await get_subscription(user.subscription_id)

    if (
        current_subscription and
        current_subscription.status == SubscriptionStatus.TRIAL and
        (current_date - current_subscription.start_date).days >= 3
    ):
        user_language_code = await get_user_language(user.id, storage)

        product = await get_product(current_subscription.product_id)
        if current_subscription.payment_method == PaymentMethod.YOOKASSA:
            payment = await create_auto_payment(
                payment_method=current_subscription.payment_method,
                provider_auto_payment_charge_id=current_subscription.provider_auto_payment_charge_id,
                user_id=current_subscription.user_id,
                description=get_localization(user_language_code).subscription_renew_description(
                    current_subscription.user_id,
                    product.names.get(user_language_code),
                ),
                amount=current_subscription.amount,
                language_code=user_language_code,
                order_items=[
                    OrderItem(
                        product=product,
                        price=current_subscription.amount,
                    ),
                ],
            )
            if not payment:
                current_subscription.status = SubscriptionStatus.FINISHED

                activated_subscriptions = await get_activated_subscriptions_by_user_id(user.id, current_date)
                for activated_subscription in activated_subscriptions:
                    if activated_subscription.id != current_subscription.id:
                        activated_subscription_product = await get_product(activated_subscription.product_id)
                        user.subscription_id = activated_subscription.id
                        user.daily_limits = activated_subscription_product.details.get('limits')
                        break
                else:
                    user.subscription_id = ''
                    user.daily_limits = SUBSCRIPTION_FREE_LIMITS

                await update_subscription(current_subscription.id, {
                    'status': current_subscription.status,
                    'end_date': current_date,
                })
                batch.update(user_ref, {
                    'subscription_id': user.subscription_id,
                    'daily_limits': user.daily_limits,
                    'last_subscription_limit_update': current_date,
                    'edited_at': current_date,
                })

                if not user.subscription_id:
                    await send_sticker(
                        bot,
                        user.telegram_chat_id,
                        config.MESSAGE_STICKERS.get(MessageSticker.SAD),
                    )
                    await send_message_to_user(
                        bot,
                        user,
                        get_localization(user_language_code).SUBSCRIPTION_END,
                        build_buy_motivation_keyboard(user_language_code),
                    )
            return user

    if (
        current_subscription and
        current_subscription.status != SubscriptionStatus.FINISHED and
        current_subscription.end_date <= current_date
    ):
        user_language_code = await get_user_language(user.id, storage)
        if current_subscription.provider_auto_payment_charge_id and current_subscription.status != SubscriptionStatus.CANCELED:
            product = await get_product(current_subscription.product_id)
            if current_subscription.payment_method == PaymentMethod.YOOKASSA:
                payment = await create_auto_payment(
                    payment_method=current_subscription.payment_method,
                    provider_auto_payment_charge_id=current_subscription.provider_auto_payment_charge_id,
                    user_id=current_subscription.user_id,
                    description=get_localization(user_language_code).subscription_renew_description(
                        current_subscription.user_id,
                        product.names.get(user_language_code),
                    ),
                    amount=current_subscription.amount,
                    language_code=user_language_code,
                    order_items=[
                        OrderItem(
                            product=product,
                            price=current_subscription.amount,
                        ),
                    ],
                )
                if not payment:
                    current_subscription.status = SubscriptionStatus.FINISHED

                    activated_subscriptions = await get_activated_subscriptions_by_user_id(user.id, current_date)
                    for activated_subscription in activated_subscriptions:
                        if activated_subscription.id != current_subscription.id:
                            activated_subscription_product = await get_product(activated_subscription.product_id)
                            user.subscription_id = activated_subscription.id
                            user.daily_limits = activated_subscription_product.details.get('limits')
                            break
                    else:
                        user.subscription_id = ''
                        user.daily_limits = SUBSCRIPTION_FREE_LIMITS

                    await update_subscription(current_subscription.id, {'status': current_subscription.status})
                    batch.update(user_ref, {
                        'subscription_id': user.subscription_id,
                        'daily_limits': user.daily_limits,
                        'last_subscription_limit_update': current_date,
                        'edited_at': current_date,
                    })

                    if not user.subscription_id:
                        await send_sticker(
                            bot,
                            user.telegram_chat_id,
                            config.MESSAGE_STICKERS.get(MessageSticker.SAD),
                        )
                        await send_message_to_user(
                            bot,
                            user,
                            get_localization(user_language_code).SUBSCRIPTION_END,
                            build_buy_motivation_keyboard(user_language_code),
                        )
                return user
            elif current_subscription.payment_method == PaymentMethod.STRIPE or current_subscription.payment_method == PaymentMethod.TELEGRAM_STARS:
                days_difference = (current_date - current_subscription.end_date).days
                if days_difference > 1:
                    current_subscription.status = SubscriptionStatus.FINISHED if current_subscription.status != SubscriptionStatus.CANCELED else current_subscription.status

                    activated_subscriptions = await get_activated_subscriptions_by_user_id(user.id, current_date)
                    for activated_subscription in activated_subscriptions:
                        if activated_subscription.id != current_subscription.id:
                            activated_subscription_product = await get_product(activated_subscription.product_id)
                            user.subscription_id = activated_subscription.id
                            user.daily_limits = activated_subscription_product.details.get('limits')
                            break
                    else:
                        user.subscription_id = ''
                        user.daily_limits = SUBSCRIPTION_FREE_LIMITS

                    await update_subscription(current_subscription.id, {'status': current_subscription.status})
                    batch.update(user_ref, {
                        'subscription_id': user.subscription_id,
                        'daily_limits': user.daily_limits,
                        'last_subscription_limit_update': current_date,
                        'edited_at': current_date,
                    })

                    if not user.subscription_id:
                        await send_sticker(
                            bot,
                            user.telegram_chat_id,
                            config.MESSAGE_STICKERS.get(MessageSticker.SAD),
                        )
                        await send_message_to_user(
                            bot,
                            user,
                            get_localization(user_language_code).SUBSCRIPTION_END,
                            build_buy_motivation_keyboard(user_language_code),
                        )

            return user
        else:
            current_subscription.status = SubscriptionStatus.FINISHED if current_subscription.status != SubscriptionStatus.CANCELED else current_subscription.status

            activated_subscriptions = await get_activated_subscriptions_by_user_id(user.id, current_date)
            for activated_subscription in activated_subscriptions:
                if activated_subscription.id != current_subscription.id:
                    activated_subscription_product = await get_product(activated_subscription.product_id)
                    user.subscription_id = activated_subscription.id
                    user.daily_limits = activated_subscription_product.details.get('limits')
                    break
            else:
                user.subscription_id = ''
                user.daily_limits = SUBSCRIPTION_FREE_LIMITS

            await update_subscription(current_subscription.id, {'status': current_subscription.status})
            batch.update(user_ref, {
                'subscription_id': user.subscription_id,
                'daily_limits': user.daily_limits,
                'last_subscription_limit_update': current_date,
                'edited_at': current_date,
            })

            if not user.subscription_id:
                await send_sticker(
                    bot,
                    user.telegram_chat_id,
                    config.MESSAGE_STICKERS.get(MessageSticker.SAD),
                )
                await send_message_to_user(
                    bot,
                    user,
                    get_localization(user_language_code).SUBSCRIPTION_END,
                    build_buy_motivation_keyboard(user_language_code),
                )

            return user
    elif (
        current_subscription and
        current_subscription.end_date >= current_date and
        current_subscription.status != SubscriptionStatus.FINISHED
    ):
        product = await get_product(current_subscription.product_id)
        daily_limits = product.details.get('limits')
    else:
        daily_limits = SUBSCRIPTION_FREE_LIMITS

    batch.update(user_ref, {
        'daily_limits': daily_limits,
        'edited_at': current_date,
    })

    return user


async def update_user_additional_usage_quota(
    bot: Bot,
    user: User,
    had_subscription: bool,
    batch: AsyncWriteBatch,
    storage: BaseStorage,
):
    need_update = False

    count_active_packages_before = 0
    for quota in [Quota.VOICE_MESSAGES, Quota.FAST_MESSAGES, Quota.ACCESS_TO_CATALOG]:
        if user.additional_usage_quota.get(quota) and not user.subscription_id:
            user.additional_usage_quota[quota] = False
            count_active_packages_before += 1
            need_update = True

    if need_update:
        user_ref = firebase.db.collection(User.COLLECTION_NAME).document(user.id)
        current_date = datetime.now(timezone.utc)

        packages = await get_packages_by_user_id(user.id)
        count_active_packages_after = 0
        for package in packages:
            product = await get_product(package.product_id)
            if product.details.get('is_recurring', False) and package.until_at > current_date:
                user.additional_usage_quota[Quota.VOICE_MESSAGES] = True
                count_active_packages_after += 1

        if not user.additional_usage_quota[Quota.VOICE_MESSAGES]:
            user.settings[user.current_model][UserSettings.TURN_ON_VOICE_MESSAGES] = False

        if not user.additional_usage_quota[Quota.ACCESS_TO_CATALOG]:
            await reset_user_chats(user)

        batch.update(user_ref, {
            'additional_usage_quota': user.additional_usage_quota,
            'settings': user.settings,
            'edited_at': current_date,
        })

        if not had_subscription and count_active_packages_before > count_active_packages_after:
            user_language_code = await get_user_language(user.id, storage)
            await send_sticker(
                bot,
                user.telegram_chat_id,
                config.MESSAGE_STICKERS.get(MessageSticker.SAD),
            )
            await send_message_to_user(
                bot,
                user,
                get_localization(user_language_code).PACKAGES_END,
                build_buy_motivation_keyboard(user_language_code),
            )


async def reset_user_chats(user: User):
    chats = await get_chats_by_user_id(user.id)

    for chat in chats:
        if chat.role_id != config.DEFAULT_ROLE_ID.get_secret_value():
            await update_chat(chat.id, {
                'role_id': config.DEFAULT_ROLE_ID.get_secret_value(),
            })
