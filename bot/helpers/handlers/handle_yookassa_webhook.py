import logging
from datetime import datetime, timezone

from aiogram import Bot, Dispatcher
from yookassa.domain.notification import WebhookNotification

from bot.config import config, MessageEffect, MessageSticker
from bot.database.main import firebase
from bot.database.models.common import PaymentMethod, Currency
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
    get_subscription_by_provider_payment_charge_id,
    get_subscription_by_provider_auto_payment_charge_id,
    get_activated_subscriptions_by_user_id,
)
from bot.database.operations.subscription.updaters import update_subscription
from bot.database.operations.subscription.writers import write_subscription
from bot.database.operations.transaction.writers import write_transaction
from bot.database.operations.user.getters import get_user
from bot.database.operations.user.updaters import update_user
from bot.helpers.creaters.create_package import create_package
from bot.helpers.creaters.create_subscription import create_subscription
from bot.helpers.getters.get_quota_by_model import get_quota_by_model
from bot.helpers.getters.get_switched_to_ai_model import get_switched_to_ai_model
from bot.helpers.senders.send_message_to_admins import send_message_to_admins
from bot.keyboards.ai.mode import build_switched_to_ai_keyboard
from bot.keyboards.common.common import build_buy_motivation_keyboard
from bot.locales.main import get_localization, get_user_language
from bot.locales.types import LanguageCode


async def handle_yookassa_webhook(request: dict, bot: Bot, dp: Dispatcher):
    notification_object = WebhookNotification(request)
    payment = notification_object.object

    try:
        subscription = await get_subscription_by_provider_payment_charge_id(payment.id)
        if subscription is not None:
            user = await get_user(subscription.user_id)
            product = await get_product(subscription.product_id)
            if payment.status == 'succeeded':
                transaction = firebase.db.transaction()
                await create_subscription(
                    transaction,
                    bot,
                    subscription.id,
                    subscription.user_id,
                    float(payment.income_amount.value),
                    payment.id,
                    payment.payment_method.id if payment.payment_method.saved else '',
                )
                await write_transaction(
                    user_id=subscription.user_id,
                    type=TransactionType.INCOME,
                    product_id=subscription.product_id,
                    amount=subscription.amount,
                    clear_amount=float(payment.income_amount.value),
                    currency=subscription.currency,
                    quantity=1,
                    details={
                        'payment_method': PaymentMethod.YOOKASSA,
                        'subscription_id': subscription.id,
                        'provider_payment_charge_id': payment.id,
                        'provider_auto_payment_charge_id': payment.payment_method.id if payment.payment_method.saved else '',
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
                await bot.send_message(
                    chat_id=subscription.user_id,
                    text=text,
                    reply_markup=reply_markup,
                    message_effect_id=config.MESSAGE_EFFECTS.get(MessageEffect.FIRE),
                )

                await send_message_to_admins(
                    bot=bot,
                    message=f'#payment #subscription #success\n\n'
                            f'🤑 <b>Успешно оформлена подписка у пользователя: {subscription.user_id}</b>\n\n'
                            f'ℹ️ ID: {subscription.id}\n'
                            f'💱 Метод оплаты: {subscription.payment_method}\n'
                            f'💳 Тип: {product.names.get(LanguageCode.RU)}\n'
                            f'💰 Сумма: {subscription.amount}{Currency.SYMBOLS[subscription.currency]}\n'
                            f'💸 Чистая сумма: {float(payment.income_amount.value)}{Currency.SYMBOLS[subscription.currency]}\n\n'
                            f'Продолжаем в том же духе 💪',
                )
            elif payment.status == 'canceled':
                subscription.status = SubscriptionStatus.DECLINED
                await update_subscription(
                    subscription.id,
                    {
                        'status': subscription.status,
                    }
                )

                await send_message_to_admins(
                    bot=bot,
                    message=f'#payment #subscription #declined\n\n'
                            f'❌ <b>Отмена оплаты подписки у пользователя: {subscription.user_id}</b>\n\n'
                            f'ℹ️ ID: {subscription.id}\n'
                            f'💱 Метод оплаты: {subscription.payment_method}\n'
                            f'💳 Тип: {product.names.get(LanguageCode.RU)}\n'
                            f'💰 Сумма: {subscription.amount}{Currency.SYMBOLS[subscription.currency]}\n\n'
                            f'Грустно, но что поделать 🤷',
                )
            else:
                await send_message_to_admins(
                    bot=bot,
                    message=f'#payment #subscription #error\n\n'
                            f'🚫 <b>Неизвестный статус при оплате подписки у пользователя: {subscription.user_id}</b>\n\n'
                            f'ℹ️ ID: {subscription.id}\n'
                            f'🛠 Статус: {payment.status}\n'
                            f'💱 Метод оплаты: {subscription.payment_method}\n'
                            f'💳 Тип: {product.names.get(LanguageCode.RU)}\n'
                            f'💰 Сумма: {subscription.amount}{Currency.SYMBOLS[subscription.currency]}\n\n'
                            f'@roman_danilov, посмотришь? 🤨',
                )
        elif payment.payment_method and payment.payment_method.id:
            old_subscription = await get_subscription_by_provider_auto_payment_charge_id(payment.payment_method.id)
            if old_subscription is not None:
                user = await get_user(old_subscription.user_id)
                product = await get_product(old_subscription.product_id)
                if payment.status == 'succeeded':
                    transaction = firebase.db.transaction()
                    await update_subscription(old_subscription.id, {'status': SubscriptionStatus.FINISHED})
                    new_subscription = await write_subscription(
                        None,
                        user.id,
                        old_subscription.product_id,
                        old_subscription.period,
                        SubscriptionStatus.ACTIVE,
                        Currency.RUB,
                        float(payment.amount.value),
                        float(payment.income_amount.value),
                        PaymentMethod.YOOKASSA,
                        payment.id,
                    )
                    await create_subscription(
                        transaction,
                        bot,
                        new_subscription.id,
                        new_subscription.user_id,
                        float(payment.income_amount.value),
                        payment.id,
                        payment.payment_method.id if payment.payment_method.saved else '',
                    )
                    await write_transaction(
                        user_id=new_subscription.user_id,
                        type=TransactionType.INCOME,
                        product_id=new_subscription.product_id,
                        amount=new_subscription.amount,
                        clear_amount=float(payment.income_amount.value),
                        currency=new_subscription.currency,
                        quantity=1,
                        details={
                            'payment_method': PaymentMethod.YOOKASSA,
                            'subscription_id': new_subscription.id,
                            'provider_payment_charge_id': payment.id,
                            'provider_auto_payment_charge_id': payment.payment_method.id if payment.payment_method.saved else '',
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
                        message=f'#payment #renew #subscription #success\n\n'
                                f'🤑 <b>Успешно продлена подписка у пользователя: {new_subscription.user_id}</b>\n\n'
                                f'ℹ️ ID: {new_subscription.id}\n'
                                f'💱 Метод оплаты: {new_subscription.payment_method}\n'
                                f'💳 Тип: {product.names.get(LanguageCode.RU)}\n'
                                f'💰 Сумма: {new_subscription.amount}{Currency.SYMBOLS[new_subscription.currency]}\n'
                                f'💸 Чистая сумма: {float(payment.income_amount.value)}{Currency.SYMBOLS[new_subscription.currency]}\n\n'
                                f'Продолжаем в том же духе 💪',
                    )
                elif payment.status == 'canceled':
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
                        message=f'#payment #renew #subscription #declined\n\n'
                                f'❌ <b>Не смогли продлить подписку у пользователя: {old_subscription.user_id}</b>\n\n'
                                f'ℹ️ ID: {old_subscription.id}\n'
                                f'💱 Метод оплаты: {old_subscription.payment_method}\n'
                                f'💳 Тип: {product.names.get(LanguageCode.RU)}\n'
                                f'💰 Сумма: {old_subscription.amount}{Currency.SYMBOLS[old_subscription.currency]}\n\n'
                                f'Грустно, но что поделать 🤷',
                    )
                else:
                    await send_message_to_admins(
                        bot=bot,
                        message=f'#payment #renew #subscription #error\n\n'
                                f'🚫 <b>Неизвестный статус при продлении подписки у пользователя: {old_subscription.user_id}</b>\n\n'
                                f'ℹ️ ID: {old_subscription.id}\n'
                                f'🛠 Статус: {payment.status}\n'
                                f'💱 Метод оплаты: {old_subscription.payment_method}\n'
                                f'💳 Тип: {product.names.get(LanguageCode.RU)}\n'
                                f'💰 Сумма: {old_subscription.amount}{Currency.SYMBOLS[old_subscription.currency]}\n\n'
                                f'@roman_danilov, посмотришь? 🤨',
                    )
    except Exception as e:
        logging.exception(f'Error in yookassa_webhook in subscription section: {e}')
        await send_message_to_admins(
            bot=bot,
            message=f'#payment #subscription #error\n\n'
                    f'🚫 Неизвестная ошибка в блоке оплаты у подписки:\n\n'
                    f'💱 Метод оплаты: {PaymentMethod.YOOKASSA}\n'
                    f'ℹ️ Информация:\n {e}\n\n'
                    f'@roman_danilov, посмотришь? 🤨',
            parse_mode=None,
        )

    try:
        packages = await get_packages_by_provider_payment_charge_id(payment.id)
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
            if payment.status == 'succeeded':
                transaction = firebase.db.transaction()
                await create_package(
                    transaction,
                    package.id,
                    package.user_id,
                    float(payment.income_amount.value),
                    payment.id,
                )

                await write_transaction(
                    user_id=package.user_id,
                    type=TransactionType.INCOME,
                    product_id=package.product_id,
                    amount=package.amount,
                    clear_amount=float(payment.income_amount.value),
                    currency=package.currency,
                    quantity=package.quantity,
                    details={
                        'payment_method': PaymentMethod.YOOKASSA,
                        'package_id': package.id,
                        'provider_payment_charge_id': payment.id,
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
                await bot.send_message(
                    chat_id=package.user_id,
                    text=text,
                    reply_markup=reply_markup,
                    message_effect_id=config.MESSAGE_EFFECTS.get(MessageEffect.FIRE),
                )

                await send_message_to_admins(
                    bot=bot,
                    message=f'#payment #package #success\n\n'
                            f'🤑 <b>Успешно прошла оплата пакета у пользователя: {package.user_id}</b>\n\n'
                            f'ℹ️ ID: {package.id}\n'
                            f'💱 Метод оплаты: {package.payment_method}\n'
                            f'💳 Тип: {product.names.get(LanguageCode.RU)}\n'
                            f'🔢 Количество: {package.quantity}\n'
                            f'💰 Сумма: {package.amount}{Currency.SYMBOLS[package.currency]}\n'
                            f'💸 Чистая сумма: {float(payment.income_amount.value)}{Currency.SYMBOLS[package.currency]}\n\n'
                            f'Продолжаем в том же духе 💪',
                )
            elif payment.status == 'canceled':
                package.status = PackageStatus.DECLINED
                await update_package(
                    package.id,
                    {
                        'status': package.status,
                    }
                )

                await send_message_to_admins(
                    bot=bot,
                    message=f'#payment #package #declined\n\n'
                            f'❌ <b>Отмена оплаты пакета у пользователя: {package.user_id}</b>\n\n'
                            f'ℹ️ ID: {package.id}\n'
                            f'💱 Метод оплаты: {package.payment_method}\n'
                            f'💳 Тип: {product.names.get(LanguageCode.RU)}\n'
                            f'🔢 Количество: {package.quantity}\n'
                            f'💰 Сумма: {package.amount}{Currency.SYMBOLS[package.currency]}\n\n'
                            f'Грустно, но что поделать 🤷',
                )
            else:
                await send_message_to_admins(
                    bot=bot,
                    message=f'#payment #package #error\n\n'
                            f'🚫 <b>Неизвестный статус при оплате пакета у пользователя: {package.user_id}</b>\n\n'
                            f'ℹ️ ID: {package.id}\n'
                            f'🛠 Статус: {payment.status}\n'
                            f'💱 Метод оплаты: {package.payment_method}\n'
                            f'💳 Тип: {product.names.get(LanguageCode.RU)}\n'
                            f'🔢 Количество: {package.quantity}\n'
                            f'💰 Сумма: {package.amount}{Currency.SYMBOLS[package.currency]}\n\n'
                            f'@roman_danilov, посмотришь? 🤨',
                )
        elif len(packages) > 1:
            user = await get_user(packages[0].user_id)
            user_subscription = await get_subscription(user.subscription_id)
            if user_subscription:
                product_subscription = await get_product(user_subscription.product_id)
                subscription_discount = product_subscription.details.get('discount', 0)
            else:
                subscription_discount = 0

            if payment.status == 'succeeded':
                transaction = firebase.db.transaction()
                for package in packages:
                    await create_package(
                        transaction,
                        package.id,
                        package.user_id,
                        float(payment.income_amount.value),
                        payment.id,
                    )

                    await write_transaction(
                        user_id=user.id,
                        type=TransactionType.INCOME,
                        product_id=package.product_id,
                        amount=package.amount,
                        clear_amount=float(payment.income_amount.value),
                        currency=package.currency,
                        quantity=package.quantity,
                        details={
                            'payment_method': PaymentMethod.YOOKASSA,
                            'package_id': package.id,
                            'provider_payment_charge_id': payment.id,
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
                await bot.send_message(
                    chat_id=user.id,
                    text=text,
                    reply_markup=reply_markup,
                    message_effect_id=config.MESSAGE_EFFECTS.get(MessageEffect.FIRE),
                )

                await send_message_to_admins(
                    bot=bot,
                    message=f'#payment #packages #success\n\n'
                            f'🤑 <b>Успешно прошла оплата пакетов у пользователя: {user.id}</b>\n\n'
                            f'💱 Метод оплаты: {PaymentMethod.YOOKASSA}\n'
                            f'💰 Сумма: {float(payment.amount.value)}{Currency.SYMBOLS[packages[0].currency]}\n'
                            f'💸 Чистая сумма: {float(payment.income_amount.value)}{Currency.SYMBOLS[packages[0].currency]}\n\n'
                            f'Продолжаем в том же духе 💪',
                )
            elif payment.status == 'canceled':
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
                    message=f'#payment #packages #declined\n\n'
                            f'❌ <b>Отмена оплаты пакетов у пользователя: {user.id}</b>\n\n'
                            f'💱 Метод оплаты: {PaymentMethod.YOOKASSA}\n'
                            f'💰 Сумма: {float(payment.amount.value)}{Currency.SYMBOLS[packages[0].currency]}\n\n'
                            f'Грустно, но что поделать 🤷',
                )
            else:
                await send_message_to_admins(
                    bot=bot,
                    message=f'#payment #packages #error\n\n'
                            f'🚫 <b>Неизвестный статус при оплате пакетов у пользователя: {user.id}</b>\n\n'
                            f'🛠 Статус: {payment.status}\n'
                            f'💱 Метод оплаты: {PaymentMethod.YOOKASSA}\n'
                            f'💰 Сумма: {float(payment.amount.value)}{Currency.SYMBOLS[packages[0].currency]}\n\n'
                            f'@roman_danilov, посмотришь? 🤨',
                )
    except Exception as e:
        logging.exception(f'Error in yookassa_webhook in package section: {e}')
        await send_message_to_admins(
            bot=bot,
            message=f'#payment #package #packages #error\n\n'
                    f'🚫 Неизвестная ошибка в блоке оплаты у пакета(-ов):\n\n'
                    f'💱 Метод оплаты: {PaymentMethod.YOOKASSA}\n'
                    f'ℹ️ Информация:\n {e}\n\n'
                    f'@roman_danilov, посмотришь? 🤨',
            parse_mode=None,
        )
