import logging
from datetime import datetime, timezone

import stripe
from aiogram import Bot, Dispatcher
from aiogram.fsm.context import FSMContext
from aiogram.fsm.storage.base import StorageKey

from bot.config import MessageEffect, config, MessageSticker
from bot.database.main import firebase
from bot.database.models.common import Model, Currency, PaymentMethod
from bot.database.models.package import PackageStatus
from bot.database.models.subscription import (
    SubscriptionStatus,
    SUBSCRIPTION_FREE_LIMITS,
)
from bot.database.models.transaction import TransactionType
from bot.database.models.user import UserSettings
from bot.database.operations.cart.getters import get_cart_by_user_id
from bot.database.operations.cart.updaters import update_cart
from bot.database.operations.package.getters import get_packages_by_provider_payment_charge_id
from bot.database.operations.package.updaters import update_package
from bot.database.operations.product.getters import get_product
from bot.database.operations.subscription.getters import (
    get_subscription,
    get_subscription_by_provider_auto_payment_charge_id,
    get_activated_subscriptions_by_user_id,
)
from bot.database.operations.subscription.updaters import update_subscription
from bot.database.operations.subscription.writers import write_subscription
from bot.database.operations.transaction.writers import write_transaction
from bot.database.operations.user.getters import get_user
from bot.database.operations.user.updaters import update_user
from bot.handlers.ai.face_swap_handler import handle_face_swap
from bot.handlers.ai.music_gen_handler import handle_music_gen
from bot.handlers.ai.photoshop_ai_handler import handle_photoshop_ai
from bot.handlers.ai.suno_handler import handle_suno
from bot.helpers.creaters.create_package import create_package
from bot.helpers.creaters.create_subscription import create_subscription
from bot.helpers.getters.get_quota_by_model import get_quota_by_model
from bot.helpers.getters.get_switched_to_ai_model import get_switched_to_ai_model
from bot.helpers.senders.send_message_to_admins import send_message_to_admins
from bot.keyboards.ai.model import build_switched_to_ai_keyboard
from bot.keyboards.common.common import build_buy_motivation_keyboard
from bot.locales.main import get_user_language, get_localization
from bot.locales.types import LanguageCode


def get_net(amount: int):
    fee_percentage = 0.029  # 2.9%
    fixed_fee = 30

    fee = round(amount * fee_percentage) + fixed_fee
    net = amount - fee

    return net


async def handle_stripe_webhook(request: dict, bot: Bot, dp: Dispatcher):
    request_type = request.get('type', '')
    request_object = request.get('data', {}).get('object', {})
    request_id = request_object.get('id', '')

    if request_type.startswith('invoice'):
        amount = round(request_object.get('amount_paid') / 100, 2)
        order_id = request_object.get('lines', {}).get('data', [{}])[0].get('metadata', {}).get('order_id')
        charge_id = request_object.get('charge')
    elif request_type.startswith('payment_intent'):
        amount = round(request_object.get('amount_received') / 100, 2)
        order_id = request_object.get('metadata', {}).get('order_id')
        charge_id = request_object.get('latest_charge')
    else:
        return

    if not order_id:
        return

    if charge_id:
        payment_charge = await stripe.Charge.retrieve_async(
            charge_id,
            expand=['balance_transaction'],
        )
        balance_transaction = payment_charge.balance_transaction
    else:
        balance_transaction = 0

    if balance_transaction:
        clear_amount = balance_transaction.net / 100
    else:
        clear_amount = round(get_net(amount * 100) / 100, 2)

    if clear_amount < 0:
        clear_amount = 0

    try:
        subscription = await get_subscription(order_id)
        if (
            subscription is not None and (
            subscription.status == SubscriptionStatus.WAITING or subscription.status == SubscriptionStatus.DECLINED
        )):
            user = await get_user(subscription.user_id)
            product = await get_product(subscription.product_id)
            if request_type == 'invoice.payment_succeeded':
                is_trial = float(clear_amount) <= 0.01
                transaction = firebase.db.transaction()
                subscription.income_amount = float(clear_amount)
                await create_subscription(
                    transaction,
                    bot,
                    subscription.id,
                    subscription.user_id,
                    subscription.income_amount,
                    request_id,
                    subscription.id,
                    request_object.get('subscription', ''),
                    is_trial,
                )
                await write_transaction(
                    user_id=subscription.user_id,
                    type=TransactionType.INCOME,
                    product_id=subscription.product_id,
                    amount=subscription.amount,
                    clear_amount=subscription.income_amount,
                    currency=subscription.currency,
                    quantity=1,
                    details={
                        'payment_method': PaymentMethod.STRIPE,
                        'subscription_id': subscription.id,
                        'provider_payment_charge_id': request_id,
                        'provider_auto_payment_charge_id': subscription.id,
                        'is_trial': is_trial,
                    },
                )

                if user.discount > product.discount:
                    await update_user(subscription.user_id, {
                        'discount': 0,
                    })

                await bot.send_sticker(
                    chat_id=user.telegram_chat_id,
                    sticker=config.MESSAGE_STICKERS.get(MessageSticker.LOVE),
                )

                user_language_code = await get_user_language(subscription.user_id, dp.storage)
                await bot.send_message(
                    chat_id=subscription.user_id,
                    text=get_localization(user_language_code).SUBSCRIPTION_SUCCESS,
                    message_effect_id=config.MESSAGE_EFFECTS.get(MessageEffect.HEART),
                )

                text = await get_switched_to_ai_model(
                    user,
                    get_quota_by_model(user.current_model, user.settings[user.current_model][UserSettings.VERSION]),
                    user_language_code,
                )
                reply_markup = build_switched_to_ai_keyboard(user_language_code, user.current_model)
                answered_message = await bot.send_message(
                    chat_id=subscription.user_id,
                    text=text,
                    reply_markup=reply_markup,
                    message_effect_id=config.MESSAGE_EFFECTS.get(MessageEffect.FIRE),
                )

                await bot.unpin_all_chat_messages(user.telegram_chat_id)
                await bot.pin_chat_message(user.telegram_chat_id, answered_message.message_id)

                state = FSMContext(
                    storage=dp.storage,
                    key=StorageKey(
                        chat_id=int(user.telegram_chat_id),
                        user_id=int(user.id),
                        bot_id=bot.id,
                    )
                )
                if user.current_model == Model.EIGHTIFY:
                    await bot.send_message(
                        chat_id=user.telegram_chat_id,
                        text=get_localization(user_language_code).EIGHTIFY_INFO,
                    )
                elif user.current_model == Model.GEMINI_VIDEO:
                    await bot.send_message(
                        chat_id=user.telegram_chat_id,
                        text=get_localization(user_language_code).GEMINI_VIDEO_INFO,
                    )
                elif user.current_model == Model.FACE_SWAP:
                    await handle_face_swap(
                        bot=bot,
                        chat_id=user.telegram_chat_id,
                        state=state,
                        user_id=user.id,
                    )
                elif user.current_model == Model.PHOTOSHOP_AI:
                    await handle_photoshop_ai(
                        bot=bot,
                        chat_id=user.telegram_chat_id,
                        state=state,
                        user_id=user.id,
                    )
                elif user.current_model == Model.MUSIC_GEN:
                    await handle_music_gen(
                        bot=bot,
                        chat_id=user.telegram_chat_id,
                        state=state,
                        user_id=user.id,
                    )
                elif user.current_model == Model.SUNO:
                    await handle_suno(
                        bot=bot,
                        chat_id=user.telegram_chat_id,
                        state=state,
                        user_id=user.id,
                    )

                await send_message_to_admins(
                    bot=bot,
                    message=get_localization(LanguageCode.RU).admin_payment_subscription_changed_status(
                        status=SubscriptionStatus.ACTIVE,
                        subscription=subscription,
                        product=product,
                        is_trial=is_trial,
                    )
                )
            elif request_type == 'invoice.payment_failed':
                subscription.status = SubscriptionStatus.DECLINED
                await update_subscription(
                    subscription.id,
                    {
                        'status': subscription.status,
                    }
                )

                await send_message_to_admins(
                    bot=bot,
                    message=get_localization(LanguageCode.RU).admin_payment_subscription_changed_status(
                        status=SubscriptionStatus.DECLINED,
                        subscription=subscription,
                        product=product,
                    ),
                )
            else:
                logging.exception(f'Error in handle_stripe_webhook: {request_type}')
                await send_message_to_admins(
                    bot=bot,
                    message=get_localization(LanguageCode.RU).admin_payment_subscription_changed_status(
                        status=SubscriptionStatus.ERROR,
                        subscription=subscription,
                        product=product,
                    ),
                )
        else:
            old_subscription = await get_subscription_by_provider_auto_payment_charge_id(order_id)
            if (
                old_subscription is not None and (
                old_subscription.status == SubscriptionStatus.ACTIVE or old_subscription.status == SubscriptionStatus.TRIAL or old_subscription.status == SubscriptionStatus.FINISHED
            )):
                user = await get_user(old_subscription.user_id)
                product = await get_product(old_subscription.product_id)
                if request_type == 'invoice.payment_succeeded':
                    if old_subscription.status == SubscriptionStatus.TRIAL:
                        new_income_amount = old_subscription.income_amount + float(clear_amount)
                        old_subscription.income_amount = new_income_amount
                        await update_subscription(old_subscription.id, {
                            'status': SubscriptionStatus.ACTIVE,
                            'income_amount': new_income_amount,
                        })
                        await write_transaction(
                            user_id=old_subscription.user_id,
                            type=TransactionType.INCOME,
                            product_id=old_subscription.product_id,
                            amount=old_subscription.amount,
                            clear_amount=float(clear_amount),
                            currency=old_subscription.currency,
                            quantity=1,
                            details={
                                'payment_method': PaymentMethod.STRIPE,
                                'subscription_id': old_subscription.id,
                                'provider_payment_charge_id': request_id,
                                'provider_auto_payment_charge_id': order_id,
                            },
                        )

                        await send_message_to_admins(
                            bot=bot,
                            message=get_localization(LanguageCode.RU).admin_payment_subscription_changed_status(
                                status=SubscriptionStatus.ACTIVE,
                                subscription=old_subscription,
                                product=product,
                                is_trial=True,
                                is_renew=True,
                            )
                        )
                    else:
                        transaction = firebase.db.transaction()
                        await update_subscription(old_subscription.id, {'status': SubscriptionStatus.FINISHED})
                        new_subscription = await write_subscription(
                            None,
                            user.id,
                            old_subscription.product_id,
                            old_subscription.period,
                            SubscriptionStatus.ACTIVE,
                            Currency.USD,
                            float(amount),
                            float(clear_amount),
                            PaymentMethod.STRIPE,
                            request_id,
                        )
                        await create_subscription(
                            transaction,
                            bot,
                            new_subscription.id,
                            new_subscription.user_id,
                            new_subscription.income_amount,
                            request_id,
                            order_id,
                            old_subscription.stripe_id,
                        )
                        await write_transaction(
                            user_id=new_subscription.user_id,
                            type=TransactionType.INCOME,
                            product_id=new_subscription.product_id,
                            amount=new_subscription.amount,
                            clear_amount=new_subscription.income_amount,
                            currency=new_subscription.currency,
                            quantity=1,
                            details={
                                'payment_method': PaymentMethod.STRIPE,
                                'subscription_id': new_subscription.id,
                                'provider_payment_charge_id': request_id,
                                'provider_auto_payment_charge_id': order_id,
                            },
                        )

                        await bot.send_sticker(
                            chat_id=user.telegram_chat_id,
                            sticker=config.MESSAGE_STICKERS.get(MessageSticker.LOVE),
                            disable_notification=True,
                        )

                        user_language_code = await get_user_language(new_subscription.user_id, dp.storage)
                        await bot.send_message(
                            chat_id=new_subscription.user_id,
                            text=get_localization(user_language_code).SUBSCRIPTION_RESET,
                            message_effect_id=config.MESSAGE_EFFECTS.get(MessageEffect.HEART),
                            disable_notification=True,
                        )

                        await send_message_to_admins(
                            bot=bot,
                            message=get_localization(LanguageCode.RU).admin_payment_subscription_changed_status(
                                status=SubscriptionStatus.ACTIVE,
                                subscription=new_subscription,
                                product=product,
                                is_trial=False,
                                is_renew=True,
                            )
                        )
                elif request_type == 'invoice.payment_failed':
                    current_date = datetime.now(timezone.utc)

                    old_subscription.status = SubscriptionStatus.FINISHED
                    activated_subscriptions = await get_activated_subscriptions_by_user_id(user.id, current_date)
                    for activated_subscription in activated_subscriptions:
                        if activated_subscription.id != old_subscription.id:
                            activated_subscription_product = await get_product(activated_subscription.product_id)
                            user.subscription_id = activated_subscription.id
                            user.daily_limits = activated_subscription_product.details.get('limits')
                            break
                    else:
                        user.subscription_id = ''
                        user.daily_limits = SUBSCRIPTION_FREE_LIMITS

                    await update_subscription(old_subscription.id, {'status': old_subscription.status})
                    await update_user(old_subscription.user_id, {
                        'subscription_id': user.subscription_id,
                        'daily_limits': user.daily_limits,
                        'last_subscription_limit_update': current_date,
                    })

                    await bot.send_sticker(
                        chat_id=user.telegram_chat_id,
                        sticker=config.MESSAGE_STICKERS.get(MessageSticker.SAD),
                        disable_notification=True,
                    )

                    await bot.send_message(
                        chat_id=user.telegram_chat_id,
                        text=get_localization(user.interface_language_code).SUBSCRIPTION_END,
                        reply_markup=build_buy_motivation_keyboard(user.interface_language_code),
                        disable_notification=True,
                    )

                    await send_message_to_admins(
                        bot=bot,
                        message=get_localization(LanguageCode.RU).admin_payment_subscription_changed_status(
                            status=SubscriptionStatus.DECLINED,
                            subscription=old_subscription,
                            product=product,
                            is_trial=old_subscription.status == SubscriptionStatus.TRIAL,
                            is_renew=True,
                        )
                    )
                else:
                    logging.exception(f'Error in handle_stripe_webhook: {request_type}')
                    await send_message_to_admins(
                        bot=bot,
                        message=get_localization(LanguageCode.RU).admin_payment_subscription_changed_status(
                            status=SubscriptionStatus.ERROR,
                            subscription=old_subscription,
                            product=product,
                            is_renew=True,
                        )
                    )
    except Exception as e:
        logging.exception(f'Error in stripe_webhook in subscription section: {e}')

    try:
        packages = await get_packages_by_provider_payment_charge_id(order_id)
        if len(packages) == 1:
            package = packages[0]
            product = await get_product(package.product_id)
            user = await get_user(package.user_id)
            user_subscription = await get_subscription(user.subscription_id)
            if user_subscription:
                product_subscription = await get_product(user_subscription.product_id)
                subscription_discount = product_subscription.details.get('discount', 0)
            else:
                subscription_discount = 0

            if request_type == 'payment_intent.succeeded':
                transaction = firebase.db.transaction()
                package.income_amount = float(clear_amount)
                await create_package(
                    transaction,
                    package.id,
                    package.user_id,
                    package.income_amount,
                    order_id,
                )

                await write_transaction(
                    user_id=package.user_id,
                    type=TransactionType.INCOME,
                    product_id=package.product_id,
                    amount=package.amount,
                    clear_amount=package.income_amount,
                    currency=package.currency,
                    quantity=package.quantity,
                    details={
                        'payment_method': PaymentMethod.STRIPE,
                        'package_id': package.id,
                        'provider_payment_charge_id': order_id,
                    },
                )

                if (
                    user.discount > product.discount and user.discount > subscription_discount
                ):
                    await update_user(package.user_id, {
                        'discount': 0,
                    })

                await bot.send_sticker(
                    chat_id=user.telegram_chat_id,
                    sticker=config.MESSAGE_STICKERS.get(MessageSticker.LOVE),
                )

                user_language_code = await get_user_language(package.user_id, dp.storage)
                await bot.send_message(
                    chat_id=package.user_id,
                    text=get_localization(user_language_code).PACKAGE_SUCCESS,
                    message_effect_id=config.MESSAGE_EFFECTS.get(MessageEffect.HEART),
                )

                text = await get_switched_to_ai_model(
                    user,
                    get_quota_by_model(user.current_model, user.settings[user.current_model][UserSettings.VERSION]),
                    user_language_code,
                )
                reply_markup = build_switched_to_ai_keyboard(user_language_code, user.current_model)
                answered_message = await bot.send_message(
                    chat_id=package.user_id,
                    text=text,
                    reply_markup=reply_markup,
                    message_effect_id=config.MESSAGE_EFFECTS.get(MessageEffect.FIRE),
                )

                await bot.unpin_all_chat_messages(user.telegram_chat_id)
                await bot.pin_chat_message(user.telegram_chat_id, answered_message.message_id)

                state = FSMContext(
                    storage=dp.storage,
                    key=StorageKey(
                        chat_id=int(user.telegram_chat_id),
                        user_id=int(user.id),
                        bot_id=bot.id,
                    )
                )
                if user.current_model == Model.EIGHTIFY:
                    await bot.send_message(
                        chat_id=user.telegram_chat_id,
                        text=get_localization(user_language_code).EIGHTIFY_INFO,
                    )
                elif user.current_model == Model.GEMINI_VIDEO:
                    await bot.send_message(
                        chat_id=user.telegram_chat_id,
                        text=get_localization(user_language_code).GEMINI_VIDEO_INFO,
                    )
                elif user.current_model == Model.FACE_SWAP:
                    await handle_face_swap(
                        bot=bot,
                        chat_id=user.telegram_chat_id,
                        state=state,
                        user_id=user.id,
                    )
                elif user.current_model == Model.PHOTOSHOP_AI:
                    await handle_photoshop_ai(
                        bot=bot,
                        chat_id=user.telegram_chat_id,
                        state=state,
                        user_id=user.id,
                    )
                elif user.current_model == Model.MUSIC_GEN:
                    await handle_music_gen(
                        bot=bot,
                        chat_id=user.telegram_chat_id,
                        state=state,
                        user_id=user.id,
                    )
                elif user.current_model == Model.SUNO:
                    await handle_suno(
                        bot=bot,
                        chat_id=user.telegram_chat_id,
                        state=state,
                        user_id=user.id,
                    )

                await send_message_to_admins(
                    bot=bot,
                    message=get_localization(LanguageCode.RU).admin_payment_package_changed_status(
                        status=PackageStatus.SUCCESS,
                        package=package,
                        product=product,
                    )
                )
            elif request_type == 'payment_intent.payment_failed' or request_type == 'payment_intent.canceled':
                package.status = PackageStatus.DECLINED
                await update_package(
                    package.id,
                    {
                        'status': package.status,
                    }
                )

                await send_message_to_admins(
                    bot=bot,
                    message=get_localization(LanguageCode.RU).admin_payment_package_changed_status(
                        status=PackageStatus.DECLINED,
                        package=package,
                        product=product,
                    )
                )
            else:
                logging.exception(f'Error in handle_stripe_webhook: {request_type}')
                await send_message_to_admins(
                    bot=bot,
                    message=get_localization(LanguageCode.RU).admin_payment_package_changed_status(
                        status=PackageStatus.ERROR,
                        package=package,
                        product=product,
                    )
                )
        elif len(packages) > 1:
            user = await get_user(packages[0].user_id)
            user_subscription = await get_subscription(user.subscription_id)
            if user_subscription:
                product_subscription = await get_product(user_subscription.product_id)
                subscription_discount = product_subscription.details.get('discount', 0)
            else:
                subscription_discount = 0

            if request_type == 'payment_intent.succeeded':
                transaction = firebase.db.transaction()
                total_amount = sum(float(package.amount) for package in packages)
                for package in packages:
                    package_clear_amount = round(
                        (float(package.amount) / total_amount) * float(clear_amount),
                        3,
                    )
                    await create_package(
                        transaction,
                        package.id,
                        package.user_id,
                        package_clear_amount,
                        order_id,
                    )

                    await write_transaction(
                        user_id=user.id,
                        type=TransactionType.INCOME,
                        product_id=package.product_id,
                        amount=package.amount,
                        clear_amount=package_clear_amount,
                        currency=package.currency,
                        quantity=package.quantity,
                        details={
                            'payment_method': PaymentMethod.STRIPE,
                            'package_id': package.id,
                            'provider_payment_charge_id': order_id,
                        },
                    )

                cart = await get_cart_by_user_id(user.id)
                cart.items = []
                await update_cart(cart.id, {
                    'items': cart.items,
                })

                if (
                    user.discount > subscription_discount
                ):
                    await update_user(user.id, {
                        'discount': 0,
                    })

                await bot.send_sticker(
                    chat_id=user.telegram_chat_id,
                    sticker=config.MESSAGE_STICKERS.get(MessageSticker.LOVE),
                )

                user_language_code = await get_user_language(user.id, dp.storage)
                await bot.send_message(
                    chat_id=user.id,
                    text=get_localization(user_language_code).PACKAGES_SUCCESS,
                    message_effect_id=config.MESSAGE_EFFECTS.get(MessageEffect.HEART),
                )

                text = await get_switched_to_ai_model(
                    user,
                    get_quota_by_model(user.current_model, user.settings[user.current_model][UserSettings.VERSION]),
                    user_language_code,
                )
                reply_markup = build_switched_to_ai_keyboard(user_language_code, user.current_model)
                answered_message = await bot.send_message(
                    chat_id=user.id,
                    text=text,
                    reply_markup=reply_markup,
                    message_effect_id=config.MESSAGE_EFFECTS.get(MessageEffect.FIRE),
                )

                await bot.unpin_all_chat_messages(user.telegram_chat_id)
                await bot.pin_chat_message(user.telegram_chat_id, answered_message.message_id)

                state = FSMContext(
                    storage=dp.storage,
                    key=StorageKey(
                        chat_id=int(user.telegram_chat_id),
                        user_id=int(user.id),
                        bot_id=bot.id,
                    )
                )
                if user.current_model == Model.EIGHTIFY:
                    await bot.send_message(
                        chat_id=user.telegram_chat_id,
                        text=get_localization(user_language_code).EIGHTIFY_INFO,
                    )
                elif user.current_model == Model.GEMINI_VIDEO:
                    await bot.send_message(
                        chat_id=user.telegram_chat_id,
                        text=get_localization(user_language_code).GEMINI_VIDEO_INFO,
                    )
                elif user.current_model == Model.FACE_SWAP:
                    await handle_face_swap(
                        bot=bot,
                        chat_id=user.telegram_chat_id,
                        state=state,
                        user_id=user.id,
                    )
                elif user.current_model == Model.PHOTOSHOP_AI:
                    await handle_photoshop_ai(
                        bot=bot,
                        chat_id=user.telegram_chat_id,
                        state=state,
                        user_id=user.id,
                    )
                elif user.current_model == Model.MUSIC_GEN:
                    await handle_music_gen(
                        bot=bot,
                        chat_id=user.telegram_chat_id,
                        state=state,
                        user_id=user.id,
                    )
                elif user.current_model == Model.SUNO:
                    await handle_suno(
                        bot=bot,
                        chat_id=user.telegram_chat_id,
                        state=state,
                        user_id=user.id,
                    )

                await send_message_to_admins(
                    bot=bot,
                    message=get_localization(LanguageCode.RU).admin_payment_packages_changed_status(
                        status=PackageStatus.SUCCESS,
                        user_id=user.id,
                        payment_method=PaymentMethod.STRIPE,
                        amount=float(amount),
                        income_amount=float(clear_amount),
                        currency=packages[0].currency,
                    )
                )
            elif request_type == 'payment_intent.payment_failed' or request_type == 'payment_intent.canceled':
                for package in packages:
                    package.status = PackageStatus.DECLINED
                    await update_package(
                        package.id,
                        {
                            'status': package.status,
                        }
                    )

                await send_message_to_admins(
                    bot=bot,
                    message=get_localization(LanguageCode.RU).admin_payment_packages_changed_status(
                        status=PackageStatus.DECLINED,
                        user_id=user.id,
                        payment_method=PaymentMethod.STRIPE,
                        amount=float(amount),
                        income_amount=0,
                        currency=packages[0].currency,
                    )
                )
            else:
                logging.exception(f'Error in handle_stripe_webhook: {request_type}')

                await send_message_to_admins(
                    bot=bot,
                    message=get_localization(LanguageCode.RU).admin_payment_packages_changed_status(
                        status=PackageStatus.ERROR,
                        user_id=user.id,
                        payment_method=PaymentMethod.STRIPE,
                        amount=float(amount),
                        income_amount=0,
                        currency=packages[0].currency,
                    )
                )
    except Exception as e:
        logging.exception(f'Error in stripe_webhook in package section: {e}')
