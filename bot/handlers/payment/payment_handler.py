import logging
import traceback
from datetime import datetime, timezone, timedelta
from typing import cast

from aiogram import Router, F
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, CallbackQuery, URLInputFile, LabeledPrice, PreCheckoutQuery

from bot.config import config, MessageEffect
from bot.database.main import firebase
from bot.database.models.cart import CartItem
from bot.database.models.common import Model, Currency, PaymentType, PaymentMethod
from bot.database.models.package import Package, PackageStatus
from bot.database.models.product import Product, ProductType, ProductCategory
from bot.database.models.subscription import (
    Subscription,
    SubscriptionStatus,
    SubscriptionPeriod,
)
from bot.database.models.transaction import TransactionType
from bot.database.models.user import UserSettings
from bot.database.operations.cart.getters import get_cart_by_user_id
from bot.database.operations.cart.updaters import update_cart
from bot.database.operations.package.getters import (
    get_packages_by_user_id_and_status,
    get_package,
)
from bot.database.operations.package.updaters import update_package
from bot.database.operations.package.writers import write_package
from bot.database.operations.product.getters import get_active_products_by_product_type_and_category, get_product
from bot.database.operations.subscription.getters import get_subscription, get_activated_subscriptions_by_user_id
from bot.database.operations.subscription.writers import write_subscription
from bot.database.operations.transaction.writers import write_transaction
from bot.database.operations.user.getters import get_user
from bot.database.operations.user.updaters import update_user
from bot.handlers.ai.face_swap_handler import handle_face_swap
from bot.handlers.ai.music_gen_handler import handle_music_gen
from bot.handlers.ai.photoshop_ai_handler import handle_photoshop_ai
from bot.handlers.ai.suno_handler import handle_suno
from bot.handlers.common.info_handler import handle_info_selection
from bot.handlers.payment.promo_code_handler import handle_promo_code
from bot.helpers.billing.create_payment import OrderItem, create_payment
from bot.helpers.billing.resubscribe import resubscribe_wrapper
from bot.helpers.billing.unsubscribe import unsubscribe_wrapper
from bot.helpers.creaters.create_package import create_package
from bot.helpers.creaters.create_subscription import create_subscription
from bot.helpers.getters.get_quota_by_model import get_quota_by_model
from bot.helpers.getters.get_switched_to_ai_model import get_switched_to_ai_model
from bot.helpers.getters.get_user_discount import get_user_discount
from bot.helpers.senders.send_message_to_admins import send_message_to_admins
from bot.keyboards.ai.model import build_switched_to_ai_keyboard
from bot.keyboards.payment.payment import (
    build_buy_keyboard,
    build_subscriptions_keyboard,
    build_payment_method_for_subscription_keyboard,
    build_packages_keyboard,
    build_package_selection_keyboard,
    build_package_quantity_sent_keyboard,
    build_package_cart_keyboard,
    build_package_add_to_cart_selection_keyboard,
    build_cancel_subscription_keyboard,
    build_payment_keyboard,
    build_payment_method_for_package_keyboard,
    build_payment_method_for_cart_keyboard,
    build_return_to_packages_keyboard,
)
from bot.locales.main import get_localization, get_user_language
from bot.locales.types import LanguageCode
from bot.states.payment.payment import Payment

payment_router = Router()


async def handle_buy(message: Message, user_id: str, state: FSMContext):
    user_language_code = await get_user_language(user_id, state.storage)

    reply_keyboard = build_buy_keyboard(user_language_code)
    text = get_localization(user_language_code).PAYMENT_BUY
    await message.answer(
        text=text,
        reply_markup=reply_keyboard,
    )


@payment_router.message(Command('buy'))
async def buy(message: Message, state: FSMContext):
    await state.clear()

    await handle_buy(message, str(message.from_user.id), state)


@payment_router.callback_query(lambda c: c.data.startswith('buy:'))
async def handle_buy_selection(callback_query: CallbackQuery, state: FSMContext):
    await callback_query.answer()

    user_id = str(callback_query.from_user.id)

    payment_type = callback_query.data.split(':')[1]
    if payment_type == PaymentType.PACKAGE:
        await handle_package(callback_query.message, user_id, state)
    elif payment_type == PaymentType.SUBSCRIPTION:
        await handle_subscribe(callback_query.message, user_id, state)
    elif payment_type == 'promo_code':
        await handle_promo_code(callback_query.message, str(callback_query.from_user.id), state)

    await callback_query.message.delete()


async def handle_subscribe(message: Message, user_id: str, state: FSMContext):
    user = await get_user(str(user_id))
    user_language_code = await get_user_language(str(user_id), state.storage)

    photo_path = f'payments/subscriptions_{user_language_code}.png'
    photo = await firebase.bucket.get_blob(photo_path)
    photo_link = firebase.get_public_url(photo.name)

    subscriptions = await get_active_products_by_product_type_and_category(
        ProductType.SUBSCRIPTION,
        ProductCategory.MONTHLY,
    )
    await state.update_data(product_category=ProductCategory.MONTHLY)

    last_user_subscriptions = await get_activated_subscriptions_by_user_id(
        user.id,
        datetime(2024, 1, 1),
    )

    text = get_localization(user_language_code).subscribe(
        subscriptions,
        user.currency,
        user.discount,
        len(last_user_subscriptions) == 0 and user.currency != Currency.XTR,
    )
    reply_markup = build_subscriptions_keyboard(
        subscriptions,
        ProductCategory.MONTHLY,
        user.currency,
        user_language_code,
    )
    await message.answer_photo(
        photo=URLInputFile(photo_link, filename=photo_path, timeout=300),
        caption=text,
        reply_markup=reply_markup,
    )


@payment_router.callback_query(lambda c: c.data.startswith('subscription:'))
async def handle_subscription_selection(callback_query: CallbackQuery, state: FSMContext):
    await callback_query.answer()

    user_id = str(callback_query.from_user.id)

    subscription_type = callback_query.data.split(':')[1]
    if subscription_type == 'back':
        await handle_buy(callback_query.message, user_id, state)
        await callback_query.message.delete()
    elif subscription_type == ProductCategory.MONTHLY or subscription_type == ProductCategory.YEARLY:
        product_category = cast(ProductCategory, subscription_type)
        user_data = await state.get_data()
        if user_data.get('product_category') == product_category:
            return
        else:
            await state.update_data(product_category=product_category)

        user = await get_user(user_id)
        user_language_code = await get_user_language(user_id, state.storage)

        subscriptions = await get_active_products_by_product_type_and_category(
            ProductType.SUBSCRIPTION,
            product_category,
        )

        last_user_subscriptions = await get_activated_subscriptions_by_user_id(
            user.id,
            datetime(2024, 1, 1),
        )

        text = get_localization(user_language_code).subscribe(
            subscriptions,
            user.currency,
            user.discount,
            len(last_user_subscriptions) == 0 and user.currency != Currency.XTR,
        )
        reply_markup = build_subscriptions_keyboard(
            subscriptions,
            product_category,
            user.currency,
            user_language_code,
        )
        await callback_query.message.edit_caption(
            caption=text,
            reply_markup=reply_markup,
        )
    elif subscription_type == 'change_currency':
        user = await get_user(user_id)
        user_language_code = await get_user_language(user_id, state.storage)
        user_data = await state.get_data()

        if user.currency == Currency.RUB:
            user.currency = Currency.USD
        elif user.currency == Currency.USD:
            user.currency = Currency.XTR
        else:
            user.currency = Currency.RUB
        await update_user(
            user_id,
            {
                'currency': user.currency,
            }
        )

        product_category = user_data.get('product_category')
        if product_category is None:
            product_category = ProductCategory.MONTHLY

        subscriptions = await get_active_products_by_product_type_and_category(
            ProductType.SUBSCRIPTION,
            product_category,
        )

        last_user_subscriptions = await get_activated_subscriptions_by_user_id(
            user.id,
            datetime(2024, 1, 1),
        )

        text = get_localization(user_language_code).subscribe(
            subscriptions,
            user.currency,
            user.discount,
            len(last_user_subscriptions) == 0 and user.currency != Currency.XTR,
        )
        reply_markup = build_subscriptions_keyboard(
            subscriptions,
            product_category,
            user.currency,
            user_language_code,
        )
        await callback_query.message.edit_caption(
            caption=text,
            reply_markup=reply_markup,
        )
    else:
        user_language_code = await get_user_language(user_id, state.storage)

        subscription = await get_product(subscription_type)

        caption = get_localization(user_language_code).PAYMENT_CHOOSE_PAYMENT_METHOD
        reply_markup = build_payment_method_for_subscription_keyboard(user_language_code, subscription.id)
        photo_path = subscription.photos.get(user_language_code)
        photo = await firebase.bucket.get_blob(photo_path)
        photo_link = firebase.get_public_url(photo.name)

        await callback_query.message.answer_photo(
            photo=URLInputFile(photo_link, filename=photo_path, timeout=300),
            caption=caption,
            reply_markup=reply_markup,
        )
        await callback_query.message.delete()


@payment_router.callback_query(lambda c: c.data.startswith('pms:'))
async def handle_payment_method_subscription_selection(callback_query: CallbackQuery, state: FSMContext):
    await callback_query.answer()

    user_id = str(callback_query.from_user.id)

    payment_method = cast(PaymentMethod, callback_query.data.split(':')[1])
    if payment_method == 'back':
        await handle_subscribe(callback_query.message, user_id, state)
        await callback_query.message.delete()
    else:
        user = await get_user(user_id)
        user_language_code = await get_user_language(user_id, state.storage)

        currency = PaymentMethod.get_currency(payment_method)

        subscription_id = callback_query.data.split(':')[2]
        subscription = await get_product(subscription_id)
        subscription_name = subscription.names.get(user_language_code)
        subscription_period = SubscriptionPeriod.MONTH1 if subscription.category == ProductCategory.MONTHLY else SubscriptionPeriod.MONTHS12
        subscription_price = subscription.prices.get(currency)
        discount = get_user_discount(user.discount, 0, subscription.discount)
        amount = Product.get_discount_price(
            ProductType.SUBSCRIPTION,
            1,
            subscription_price,
            currency,
            discount,
            subscription_period,
        )

        last_user_subscriptions = await get_activated_subscriptions_by_user_id(
            user.id,
            datetime(2024, 1, 1),
        )
        is_trial = len(last_user_subscriptions) == 0 and payment_method != PaymentMethod.TELEGRAM_STARS

        if payment_method == PaymentMethod.TELEGRAM_STARS:
            subscription_ref = await write_subscription(
                None,
                user_id,
                subscription_id,
                subscription_period,
                SubscriptionStatus.WAITING,
                currency,
                int(float(amount)),
                0,
                payment_method,
                None,
            )
            payment = await callback_query.bot.create_invoice_link(
                title=subscription_name,
                description=get_localization(user_language_code).subscription_description(
                    user_id,
                    subscription_name,
                ),
                provider_token='',
                payload=f'{PaymentType.SUBSCRIPTION}:{subscription_ref.id}',
                currency=Currency.XTR,
                prices=[
                    LabeledPrice(
                        label=subscription_name,
                        amount=int(float(amount)),
                    ),
                ],
                subscription_period=2592000,
            )
        else:
            subscription_ref = firebase.db.collection(Subscription.COLLECTION_NAME).document()
            payment = await create_payment(
                payment_method=payment_method,
                user=user,
                description=get_localization(user_language_code).subscription_description(
                    user_id,
                    subscription_name,
                ),
                amount=float(amount),
                language_code=user_language_code,
                is_recurring=True,
                order_items=[
                    OrderItem(
                        product=subscription,
                        price=float(amount),
                    ),
                ],
                order_id=subscription_ref.id if payment_method == PaymentMethod.STRIPE else None,
                order_interval='month' if subscription_period == SubscriptionPeriod.MONTH1 else 'year',
                is_trial=is_trial,
            )

        if payment_method == PaymentMethod.YOOKASSA:
            payment_url = payment.get('confirmation').get('confirmation_url')
            provider_payment_charge_id = payment.get('id')
        elif payment_method == PaymentMethod.STRIPE:
            payment_url = payment.get('url')
            provider_payment_charge_id = None
        elif payment_method == PaymentMethod.TELEGRAM_STARS:
            payment_url = payment
            provider_payment_charge_id = None
        else:
            raise NotImplementedError(f'Payment method is not recognized: {payment_method}')

        caption = get_localization(user_language_code).subscribe_confirmation(
            subscription_name,
            subscription.category,
            currency,
            amount,
            is_trial,
        )
        reply_markup = build_payment_keyboard(
            user_language_code,
            payment_url,
        )
        await callback_query.message.edit_caption(
            caption=caption,
            reply_markup=reply_markup,
        )

        if payment_method != PaymentMethod.TELEGRAM_STARS:
            await write_subscription(
                subscription_ref.id if payment_method == PaymentMethod.STRIPE else None,
                user_id,
                subscription_id,
                subscription_period,
                SubscriptionStatus.WAITING,
                currency,
                float(amount),
                0,
                payment_method,
                provider_payment_charge_id,
            )


async def handle_package(message: Message, user_id: str, state: FSMContext, is_edit=False, page=0):
    user = await get_user(user_id)
    user_language_code = await get_user_language(user_id, state.storage)

    photo_path = f'payments/packages_{user_language_code}.png'
    photo = await firebase.bucket.get_blob(photo_path)
    photo_link = firebase.get_public_url(photo.name)

    if page == 0:
        product_category = ProductCategory.TEXT
    elif page == 1:
        product_category = ProductCategory.SUMMARY
    elif page == 2:
        product_category = ProductCategory.IMAGE
    elif page == 3:
        product_category = ProductCategory.MUSIC
    elif page == 4:
        product_category = ProductCategory.VIDEO
    elif page == 5:
        product_category = ProductCategory.OTHER
    else:
        product_category = None

    user_subscription = await get_subscription(user.subscription_id)
    if user_subscription:
        product_subscription = await get_product(user_subscription.product_id)
        subscription_discount = product_subscription.details.get('discount', 0)
    else:
        subscription_discount = 0
    discount = get_user_discount(user.discount, subscription_discount, 0)

    products = await get_active_products_by_product_type_and_category(
        ProductType.PACKAGE,
        product_category,
    )

    cost = Product.get_discount_price(
        ProductType.PACKAGE,
        1,
        1,
        user.currency,
        discount,
    )
    text = get_localization(user_language_code).package_info(user.currency, cost)
    reply_markup = build_packages_keyboard(user_language_code, products, page)

    if is_edit:
        await message.edit_caption(
            caption=text,
            reply_markup=reply_markup,
        )
    else:
        await message.answer_photo(
            photo=URLInputFile(photo_link, filename=photo_path, timeout=300),
            caption=text,
            reply_markup=reply_markup,
        )


@payment_router.callback_query(lambda c: c.data.startswith('package:'))
async def handle_package_selection(callback_query: CallbackQuery, state: FSMContext):
    await callback_query.answer()

    user_id = str(callback_query.from_user.id)
    user = await get_user(user_id)
    user_language_code = await get_user_language(user_id, state.storage)

    package_type = callback_query.data.split(':')[1]
    if package_type == 'page':
        return
    elif (
        package_type == ProductCategory.TEXT or
        package_type == ProductCategory.SUMMARY or
        package_type == ProductCategory.IMAGE or
        package_type == ProductCategory.MUSIC or
        package_type == ProductCategory.VIDEO
    ):
        await handle_info_selection(callback_query, state, package_type)
    elif package_type == 'next' or package_type == 'prev':
        page = int(callback_query.data.split(':')[2])
        await handle_package(callback_query.message, str(callback_query.from_user.id), state, True, page)
    elif package_type == 'change_currency':
        if user.currency == Currency.RUB:
            user.currency = Currency.USD
        elif user.currency == Currency.USD:
            user.currency = Currency.XTR
        else:
            user.currency = Currency.RUB
        await update_user(
            user_id,
            {
                'currency': user.currency,
            }
        )

        page = int(callback_query.data.split(':')[2])
        await handle_package(callback_query.message, str(callback_query.from_user.id), state, True, page)
    elif package_type == 'back':
        await handle_buy(callback_query.message, user_id, state)
        await callback_query.message.delete()
    elif package_type == 'cart':
        cart = await get_cart_by_user_id(user_id)

        user_subscription = await get_subscription(user.subscription_id)
        if user_subscription:
            product_subscription = await get_product(user_subscription.product_id)
            subscription_discount = product_subscription.details.get('discount', 0)
        else:
            subscription_discount = 0
        discount = get_user_discount(user.discount, subscription_discount, 0)
        caption = await get_localization(user_language_code).shopping_cart_info(
            user.currency,
            cart.items,
            discount,
        )
        reply_markup = build_package_cart_keyboard(user_language_code)
        await callback_query.message.edit_caption(caption=caption, reply_markup=reply_markup)
    else:
        product = await get_product(package_type)
        caption = get_localization(user_language_code).package_choose_min(product.names.get(user_language_code))
        reply_markup = build_package_selection_keyboard(user_language_code)
        await callback_query.message.edit_caption(caption=caption, reply_markup=reply_markup)

        await state.update_data(package_product_id=package_type)
        await state.set_state(Payment.waiting_for_package_quantity)


@payment_router.callback_query(lambda c: c.data.startswith('package_selection:'))
async def handle_package_selection_selection(callback_query: CallbackQuery, state: FSMContext):
    await callback_query.answer()

    user_id = str(callback_query.from_user.id)

    await handle_package(callback_query.message, user_id, state)
    await callback_query.message.delete()


@payment_router.message(Payment.waiting_for_package_quantity, ~F.text.startswith('/'))
async def quantity_of_package_sent(message: Message, state: FSMContext):
    user_id = str(message.from_user.id)
    user_language_code = await get_user_language(user_id, state.storage)

    try:
        quantity = int(message.text)

        photo_path = f'payments/packages_{user_language_code}.png'
        photo = await firebase.bucket.get_blob(photo_path)
        photo_link = firebase.get_public_url(photo.name)

        reply_markup = build_package_quantity_sent_keyboard(user_language_code)
        await message.reply_photo(
            photo=URLInputFile(photo_link, filename=photo_path, timeout=300),
            caption=get_localization(user_language_code).SHOPPING_CART_ADD_OR_BUY_NOW,
            reply_markup=reply_markup,
            allow_sending_without_reply=True,
        )

        await state.update_data(package_quantity=quantity)
    except (TypeError, ValueError):
        reply_markup = build_package_selection_keyboard(user_language_code)
        await message.reply(
            text=get_localization(user_language_code).ERROR_IS_NOT_NUMBER,
            reply_markup=reply_markup,
            allow_sending_without_reply=True,
        )


@payment_router.callback_query(lambda c: c.data.startswith('package_quantity_sent:'))
async def handle_package_quantity_sent_selection(callback_query: CallbackQuery, state: FSMContext):
    await callback_query.answer()

    user_id = str(callback_query.from_user.id)
    user_language_code = await get_user_language(user_id, state.storage)
    user_data = await state.get_data()

    package_product_id = user_data['package_product_id']
    package_quantity = user_data['package_quantity']

    action = callback_query.data.split(':')[1]
    if action == 'add_to_cart':
        cart = await get_cart_by_user_id(user_id)
        is_already_in_cart = False
        for index, cart_item in enumerate(cart.items):
            if cart_item.get('product_id') == package_product_id:
                is_already_in_cart = True
                cart.items[index]['quantity'] = cart_item.get('quantity', 0) + package_quantity
                break
        if not is_already_in_cart:
            cart.items.append(CartItem(package_product_id, package_quantity).to_dict())

        await update_cart(cart.id, {
            'items': cart.items,
        })

        reply_markup = build_package_add_to_cart_selection_keyboard(user_language_code)
        await callback_query.message.edit_caption(
            caption=get_localization(user_language_code).SHOPPING_CART_GO_TO_OR_CONTINUE_SHOPPING,
            reply_markup=reply_markup,
        )
    elif action == 'buy_now':
        reply_markup = build_payment_method_for_package_keyboard(
            user_language_code,
            package_product_id,
            package_quantity,
        )
        await callback_query.message.edit_caption(
            caption=get_localization(user_language_code).PAYMENT_CHOOSE_PAYMENT_METHOD,
            reply_markup=reply_markup,
        )


@payment_router.callback_query(lambda c: c.data.startswith('package_add_to_cart_selection:'))
async def handle_package_add_to_cart_selection(callback_query: CallbackQuery, state: FSMContext):
    await callback_query.answer()

    user_id = str(callback_query.from_user.id)
    user = await get_user(user_id)
    user_language_code = await get_user_language(user_id, state.storage)

    action = callback_query.data.split(':')[1]
    if action == 'go_to_cart':
        cart = await get_cart_by_user_id(user_id)

        photo_path = f'payments/packages_{user_language_code}.png'
        photo = await firebase.bucket.get_blob(photo_path)
        photo_link = firebase.get_public_url(photo.name)

        user_subscription = await get_subscription(user.subscription_id)
        if user_subscription:
            product_subscription = await get_product(user_subscription.product_id)
            subscription_discount = product_subscription.details.get('discount', 0)
        else:
            subscription_discount = 0
        discount = get_user_discount(user.discount, subscription_discount, 0)
        caption = await get_localization(user_language_code).shopping_cart_info(
            user.currency,
            cart.items,
            discount,
        )
        reply_markup = build_package_cart_keyboard(user_language_code)
        await callback_query.message.answer_photo(
            photo=URLInputFile(photo_link, filename=photo_path, timeout=300),
            caption=caption,
            reply_markup=reply_markup,
        )
        await callback_query.message.delete()
    elif action == 'continue_shopping':
        await handle_package(callback_query.message, user_id, state)
        await callback_query.message.delete()


@payment_router.callback_query(lambda c: c.data.startswith('package_cart:'))
async def handle_package_cart_selection(callback_query: CallbackQuery, state: FSMContext):
    await callback_query.answer()

    user_id = str(callback_query.from_user.id)
    user = await get_user(user_id)
    user_language_code = await get_user_language(user_id, state.storage)

    action = callback_query.data.split(':')[1]
    if action == 'proceed_to_checkout':
        reply_markup = build_payment_method_for_cart_keyboard(user_language_code)
        await callback_query.message.edit_caption(
            caption=get_localization(user_language_code).PAYMENT_CHOOSE_PAYMENT_METHOD,
            reply_markup=reply_markup,
        )
    elif action == 'clear':
        cart = await get_cart_by_user_id(user_id)
        if cart.items:
            cart.items = []
            await update_cart(cart.id, {
                'items': cart.items,
            })

            user_subscription = await get_subscription(user.subscription_id)
            if user_subscription:
                product_subscription = await get_product(user_subscription.product_id)
                subscription_discount = product_subscription.details.get('discount', 0)
            else:
                subscription_discount = 0
            discount = get_user_discount(user.discount, subscription_discount, 0)
            caption = await get_localization(user_language_code).shopping_cart_info(
                user.currency,
                cart.items,
                discount,
            )
            reply_markup = build_package_cart_keyboard(user_language_code)
            await callback_query.message.edit_caption(caption=caption, reply_markup=reply_markup)
    elif action == 'change_currency':
        if user.currency == Currency.RUB:
            user.currency = Currency.USD
        elif user.currency == Currency.USD:
            user.currency = Currency.XTR
        else:
            user.currency = Currency.RUB
        await update_user(
            user_id,
            {
                'currency': user.currency,
            }
        )

        cart = await get_cart_by_user_id(user_id)

        user_subscription = await get_subscription(user.subscription_id)
        if user_subscription:
            product_subscription = await get_product(user_subscription.product_id)
            subscription_discount = product_subscription.details.get('discount', 0)
        else:
            subscription_discount = 0
        discount = get_user_discount(user.discount, subscription_discount, 0)
        caption = await get_localization(user_language_code).shopping_cart_info(
            user.currency,
            cart.items,
            discount,
        )
        reply_markup = build_package_cart_keyboard(user_language_code)
        await callback_query.message.edit_caption(caption=caption, reply_markup=reply_markup)
    elif action == 'back':
        await handle_package(callback_query.message, user_id, state)
        await callback_query.message.delete()


@payment_router.callback_query(lambda c: c.data.startswith('package_proceed_to_checkout:'))
async def handle_package_proceed_to_checkout_selection(callback_query: CallbackQuery, state: FSMContext):
    await callback_query.answer()

    user_id = str(callback_query.from_user.id)
    user = await get_user(user_id)
    user_language_code = await get_user_language(user_id, state.storage)

    cart = await get_cart_by_user_id(user_id)

    user_subscription = await get_subscription(user.subscription_id)
    if user_subscription:
        product_subscription = await get_product(user_subscription.product_id)
        subscription_discount = product_subscription.details.get('discount', 0)
    else:
        subscription_discount = 0
    discount = get_user_discount(user.discount, subscription_discount, 0)
    caption = await get_localization(user_language_code).shopping_cart_info(
        user.currency,
        cart.items,
        discount,
    )
    reply_markup = build_package_cart_keyboard(user_language_code)
    await callback_query.message.edit_caption(caption=caption, reply_markup=reply_markup)


@payment_router.callback_query(lambda c: c.data.startswith('pmp:'))
async def handle_payment_method_package_selection(callback_query: CallbackQuery, state: FSMContext):
    await callback_query.answer()

    await state.clear()

    user_id = str(callback_query.from_user.id)

    payment_method = cast(PaymentMethod, callback_query.data.split(':')[1])
    if payment_method == 'back':
        await handle_package(callback_query.message, user_id, state, True)
    else:
        user = await get_user(user_id)
        user_language_code = await get_user_language(user_id, state.storage)

        user_subscription = await get_subscription(user.subscription_id)
        if user_subscription:
            product_subscription = await get_product(user_subscription.product_id)
            subscription_discount = product_subscription.details.get('discount', 0)
        else:
            subscription_discount = 0

        currency = PaymentMethod.get_currency(payment_method)

        package_product_id, package_quantity = callback_query.data.split(':')[2], int(callback_query.data.split(':')[3])
        package = await get_product(package_product_id)
        package_price = package.prices.get(currency)
        discount = get_user_discount(user.discount, subscription_discount, package.discount)
        package_amount = Product.get_discount_price(
            ProductType.PACKAGE,
            package_quantity,
            package_price,
            currency,
            discount,
        )
        package_name = package.names.get(user_language_code)
        package_description = package.descriptions.get(user_language_code)

        until_at = None
        if package.details.get('is_recurring', False):
            current_date = datetime.now(timezone.utc)
            until_at = current_date + timedelta(days=30 * int(package_quantity))

        if (
            (currency == Currency.USD and float(package_amount) < 1) or
            (currency == Currency.RUB and float(package_amount) < 50) or
            (currency == Currency.XTR and float(package_amount) < 50)
        ):
            reply_markup = build_return_to_packages_keyboard(user_language_code)
            await callback_query.message.edit_caption(
                caption=get_localization(user_language_code).payment_purchase_minimal_price(currency, package_amount),
                reply_markup=reply_markup,
            )
            return

        if payment_method == PaymentMethod.TELEGRAM_STARS:
            package_ref = await write_package(
                None,
                user_id,
                package_product_id,
                PackageStatus.WAITING,
                currency,
                int(float(package_amount)),
                0,
                int(package_quantity),
                payment_method,
                None,
                until_at,
            )
            payment = await callback_query.bot.create_invoice_link(
                title=f'{package_name} ({package_quantity})',
                description=package_description,
                provider_token='',
                payload=f'{PaymentType.PACKAGE}:{package_ref.id}',
                currency=currency,
                prices=[
                    LabeledPrice(
                        label=package_name,
                        amount=int(float(package_amount)),
                    ),
                ],
            )
        else:
            package_ref = firebase.db.collection(Package.COLLECTION_NAME).document()
            payment = await create_payment(
                payment_method=payment_method,
                user=user,
                description=get_localization(user_language_code).payment_package_description(
                    user_id,
                    package_name,
                    package_quantity,
                ),
                amount=float(package_amount),
                language_code=user_language_code,
                is_recurring=False,
                order_items=[
                    OrderItem(
                        product=package,
                        price=round(float(package_amount) / package_quantity, 2),
                        quantity=package_quantity,
                    ),
                ],
                order_id=package_ref.id if payment_method == PaymentMethod.STRIPE else None,
            )

        if payment_method == PaymentMethod.YOOKASSA:
            payment_url = payment.get('confirmation').get('confirmation_url')
            provider_payment_charge_id = payment.get('id')
        elif payment_method == PaymentMethod.STRIPE:
            payment_url = payment.get('url')
            provider_payment_charge_id = package_ref.id
        elif payment_method == PaymentMethod.TELEGRAM_STARS:
            payment_url = payment
            provider_payment_charge_id = None
        else:
            raise NotImplementedError(f'Payment method is not recognized: {payment_method}')

        caption = get_localization(user_language_code).package_confirmation(
            package_name,
            package_quantity,
            currency,
            package_amount,
        )
        reply_markup = build_payment_keyboard(
            user_language_code,
            payment_url,
        )
        await callback_query.message.edit_caption(
            caption=caption,
            reply_markup=reply_markup,
        )

        await write_package(
            None,
            user_id,
            package_product_id,
            PackageStatus.WAITING,
            currency,
            float(package_amount),
            0,
            int(package_quantity),
            payment_method,
            provider_payment_charge_id,
            until_at,
        )


@payment_router.callback_query(lambda c: c.data.startswith('pmc:'))
async def handle_payment_method_cart_selection(callback_query: CallbackQuery, state: FSMContext):
    await callback_query.answer()

    user_id = str(callback_query.from_user.id)
    user = await get_user(user_id)
    user_language_code = await get_user_language(user_id, state.storage)

    cart = await get_cart_by_user_id(user_id)

    payment_method = cast(PaymentMethod, callback_query.data.split(':')[1])
    if payment_method == 'back':
        user_subscription = await get_subscription(user.subscription_id)
        if user_subscription:
            product_subscription = await get_product(user_subscription.product_id)
            subscription_discount = product_subscription.details.get('discount', 0)
        else:
            subscription_discount = 0
        discount = get_user_discount(user.discount, subscription_discount, 0)
        caption = await get_localization(user_language_code).shopping_cart_info(
            user.currency,
            cart.items,
            discount,
        )
        reply_markup = build_package_cart_keyboard(user_language_code)
        await callback_query.message.edit_caption(caption=caption, reply_markup=reply_markup)
    else:
        packages_with_waiting_status = await get_packages_by_user_id_and_status(user_id, PackageStatus.WAITING)
        for package_with_waiting_status in packages_with_waiting_status:
            await update_package(package_with_waiting_status.id, {
                'status': PackageStatus.DECLINED,
            })

        user_subscription = await get_subscription(user.subscription_id)
        if user_subscription:
            product_subscription = await get_product(user_subscription.product_id)
            subscription_discount = product_subscription.details.get('discount', 0)
        else:
            subscription_discount = 0
        discount = get_user_discount(user.discount, subscription_discount, 0)

        currency = PaymentMethod.get_currency(payment_method)

        amount = 0
        order_items = []
        payload = f'{PaymentType.CART}:{user.id}'
        for cart_item in cart.items:
            product_id, product_quantity = cart_item.get('product_id'), cart_item.get('quantity', 0)

            product = await get_product(product_id)

            until_at = None
            if product.details.get('is_recurring', False):
                current_date = datetime.now(timezone.utc)
                until_at = current_date + timedelta(days=30 * product_quantity)

            product_price = float(Product.get_discount_price(
                ProductType.PACKAGE,
                product_quantity,
                product.prices.get(currency),
                currency,
                discount,
            ))
            amount += product_price
            order_items.append(
                OrderItem(
                    product=product,
                    price=round(product_price / product_quantity, 2),
                    quantity=product_quantity,
                )
            )
            payload += f':{product_id}:{product_quantity}'

            await write_package(
                None,
                user_id,
                product_id,
                PackageStatus.WAITING,
                currency,
                float(product_price),
                0,
                int(product_quantity),
                payment_method,
                None,
                until_at,
            )

        amount = round(amount, 2)
        if (
            (currency == Currency.USD and amount < 1) or
            (currency == Currency.RUB and amount < 50) or
            (currency == Currency.XTR and amount < 50)
        ):
            reply_markup = build_return_to_packages_keyboard(user_language_code)
            await callback_query.message.edit_caption(
                caption=get_localization(user_language_code).payment_purchase_minimal_price(currency, amount),
                reply_markup=reply_markup,
            )
            return

        package_ref = firebase.db.collection(Package.COLLECTION_NAME).document()
        if payment_method == PaymentMethod.TELEGRAM_STARS:
            payment = await callback_query.bot.create_invoice_link(
                title=get_localization(user_language_code).PACKAGES,
                description=get_localization(user_language_code).SHOPPING_CART,
                provider_token='',
                payload=payload,
                currency=currency,
                prices=[
                    LabeledPrice(
                        label=get_localization(user_language_code).SHOPPING_CART,
                        amount=int(float(amount)),
                    ),
                ],
            )
        else:
            payment = await create_payment(
                payment_method=payment_method,
                user=user,
                description=get_localization(user_language_code).packages_description(user_id),
                amount=amount,
                language_code=user_language_code,
                is_recurring=False,
                order_items=order_items,
                order_id=package_ref.id if payment_method == PaymentMethod.STRIPE else None,
            )

        if payment_method == PaymentMethod.YOOKASSA:
            payment_url = payment.get('confirmation').get('confirmation_url')
            provider_payment_charge_id = payment.get('id')
        elif payment_method == PaymentMethod.STRIPE:
            payment_url = payment.get('url')
            provider_payment_charge_id = package_ref.id
        elif payment_method == PaymentMethod.TELEGRAM_STARS:
            payment_url = payment
            provider_payment_charge_id = None
        else:
            raise NotImplementedError(f'Payment method is not recognized: {payment_method}')

        caption = await get_localization(user_language_code).shopping_cart_confirmation(
            cart.items,
            currency,
            amount,
        )
        reply_markup = build_payment_keyboard(
            user_language_code,
            payment_url,
        )

        await callback_query.message.edit_caption(
            caption=caption,
            reply_markup=reply_markup,
        )

        packages_with_waiting_status = await get_packages_by_user_id_and_status(user_id, PackageStatus.WAITING)
        for package_with_waiting_status in packages_with_waiting_status:
            await update_package(package_with_waiting_status.id, {
                'provider_payment_charge_id': provider_payment_charge_id,
            })


@payment_router.pre_checkout_query()
async def handle_pre_checkout(pre_checkout_query: PreCheckoutQuery):
    payment_type = pre_checkout_query.invoice_payload.split(':')[0]
    if payment_type == PaymentType.SUBSCRIPTION:
        try:
            await pre_checkout_query.answer(ok=True)
        except Exception:
            error_trace = traceback.format_exc()
            logging.exception(f'Error in pre_checkout: {error_trace}')

            await pre_checkout_query.answer(ok=False)
    elif payment_type == PaymentType.PACKAGE:
        try:
            await pre_checkout_query.answer(ok=True)
        except Exception:
            error_trace = traceback.format_exc()
            logging.exception(f'Error in pre_checkout: {error_trace}')

            await pre_checkout_query.answer(ok=False)
    elif payment_type == PaymentType.CART:
        try:
            await pre_checkout_query.answer(ok=True)
        except Exception:
            error_trace = traceback.format_exc()
            logging.error(f'Error in pre_checkout: {error_trace}')

            await pre_checkout_query.answer(ok=False)
    else:
        await pre_checkout_query.answer(ok=False)


@payment_router.message(F.successful_payment)
async def handle_successful_payment(message: Message, state: FSMContext):
    user_id = str(message.from_user.id)
    user = await get_user(user_id)
    user_language_code = await get_user_language(user_id, state.storage)

    payment = message.successful_payment
    payment_type = payment.invoice_payload.split(':')[0]
    if payment_type == PaymentType.SUBSCRIPTION:
        _, subscription_id = payment.invoice_payload.split(':')
        subscription = await get_subscription(subscription_id)
        product = await get_product(subscription.product_id)

        if not payment.is_first_recurring:
            subscription = await write_subscription(
                None,
                user_id,
                product.id,
                SubscriptionPeriod.MONTH1,
                SubscriptionStatus.WAITING,
                Currency.XTR,
                payment.total_amount,
                0,
                PaymentMethod.TELEGRAM_STARS,
                None,
            )

        transaction = firebase.db.transaction()
        await create_subscription(
            transaction,
            message.bot,
            subscription.id,
            subscription.user_id,
            subscription.amount,
            payment.telegram_payment_charge_id,
            subscription_id,
        )
        await write_transaction(
            user_id=user_id,
            type=TransactionType.INCOME,
            product_id=subscription.product_id,
            amount=subscription.amount,
            clear_amount=subscription.amount,
            currency=subscription.currency,
            quantity=1,
            details={
                'payment_method': PaymentMethod.TELEGRAM_STARS,
                'subscription_id': subscription.id,
                'provider_payment_charge_id': payment.provider_payment_charge_id,
                'provider_auto_payment_charge_id': subscription_id,
            },
        )
        if user.discount > product.discount:
            await update_user(user_id, {
                'discount': 0,
            })

        await message.answer(
            text=get_localization(user_language_code).SUBSCRIPTION_SUCCESS,
        )

        await send_message_to_admins(
            bot=message.bot,
            message=get_localization(LanguageCode.RU).admin_payment_subscription_changed_status(
                status=SubscriptionStatus.ACTIVE,
                subscription=subscription,
                product=product,
                is_trial=False,
                is_renew=payment.is_first_recurring,
            )
        )
    elif payment_type == PaymentType.PACKAGE:
        _, package_id = payment.invoice_payload.split(':')
        package = await get_package(package_id)
        product = await get_product(package.product_id)

        transaction = firebase.db.transaction()
        await create_package(
            transaction,
            package.id,
            package.user_id,
            package.amount,
            payment.provider_payment_charge_id,
        )

        user_subscription = await get_subscription(user.subscription_id)
        if user_subscription:
            product_subscription = await get_product(user_subscription.product_id)
            subscription_discount = product_subscription.details.get('discount')
        else:
            subscription_discount = 0
        if user.discount > product.discount and user.discount > subscription_discount:
            await update_user(user_id, {
                'discount': 0,
            })

        await write_transaction(
            user_id=user_id,
            type=TransactionType.INCOME,
            product_id=package.product_id,
            amount=package.amount,
            clear_amount=package.amount,
            currency=package.currency,
            quantity=package.quantity,
            details={
                'payment_method': PaymentMethod.TELEGRAM_STARS,
                'package_id': package.id,
                'provider_payment_charge_id': payment.provider_payment_charge_id
            },
        )

        await message.answer(
            text=get_localization(user_language_code).PACKAGE_SUCCESS,
        )
        await send_message_to_admins(
            bot=message.bot,
            message=get_localization(LanguageCode.RU).admin_payment_package_changed_status(
                status=PackageStatus.SUCCESS,
                package=package,
                product=product,
            )
        )
    elif payment_type == PaymentType.CART:
        user_id = payment.invoice_payload.split(':')[1]
        packages = await get_packages_by_user_id_and_status(user_id, PackageStatus.WAITING)

        transaction = firebase.db.transaction()
        for package in packages:
            await create_package(
                transaction,
                package.id,
                package.user_id,
                package.amount,
                payment.provider_payment_charge_id,
            )

            await write_transaction(
                user_id=user_id,
                type=TransactionType.INCOME,
                product_id=package.product_id,
                amount=package.amount,
                clear_amount=package.amount,
                currency=package.currency,
                quantity=package.quantity,
                details={
                    'payment_method': PaymentMethod.TELEGRAM_STARS,
                    'package_id': package.id,
                    'provider_payment_charge_id': payment.provider_payment_charge_id
                },
            )

        cart = await get_cart_by_user_id(user_id)
        cart.items = []
        await update_cart(cart.id, {
            'items': cart.items,
        })

        user_subscription = await get_subscription(user.subscription_id)
        if user_subscription:
            product_subscription = await get_product(user_subscription.product_id)
            subscription_discount = product_subscription.details.get('discount', 0)
        else:
            subscription_discount = 0
        if user.discount > subscription_discount:
            await update_user(user_id, {
                'discount': 0,
            })

        await message.answer(
            text=get_localization(user_language_code).PACKAGES_SUCCESS,
        )
        await send_message_to_admins(
            bot=message.bot,
            message=get_localization(LanguageCode.RU).admin_payment_packages_changed_status(
                status=PackageStatus.SUCCESS,
                user_id=user.id,
                payment_method=PaymentMethod.TELEGRAM_STARS,
                amount=float(payment.total_amount),
                income_amount=float(payment.total_amount),
                currency=packages[0].currency,
            )
        )

    text = await get_switched_to_ai_model(
        user,
        get_quota_by_model(user.current_model, user.settings[user.current_model][UserSettings.VERSION]),
        user_language_code,
    )
    reply_markup = build_switched_to_ai_keyboard(user_language_code, user.current_model)
    answered_message = await message.answer(
        text=text,
        reply_markup=reply_markup,
    )

    await message.bot.unpin_all_chat_messages(user.telegram_chat_id)
    await message.bot.pin_chat_message(user.telegram_chat_id, answered_message.message_id)

    if user.current_model == Model.EIGHTIFY:
        await message.answer(
            text=get_localization(user_language_code).EIGHTIFY_INFO,
        )
    elif user.current_model == Model.GEMINI_VIDEO:
        await message.answer(
            text=get_localization(user_language_code).GEMINI_VIDEO_INFO,
        )
    elif user.current_model == Model.FACE_SWAP:
        await handle_face_swap(
            bot=message.bot,
            chat_id=user.telegram_chat_id,
            state=state,
            user_id=user.id,
        )
    elif user.current_model == Model.PHOTOSHOP_AI:
        await handle_photoshop_ai(
            bot=message.bot,
            chat_id=user.telegram_chat_id,
            state=state,
            user_id=user.id,
        )
    elif user.current_model == Model.MUSIC_GEN:
        await handle_music_gen(
            bot=message.bot,
            chat_id=user.telegram_chat_id,
            state=state,
            user_id=user.id,
        )
    elif user.current_model == Model.SUNO:
        await handle_suno(
            bot=message.bot,
            chat_id=user.telegram_chat_id,
            state=state,
            user_id=user.id,
        )


async def handle_cancel_subscription(message: Message, user_id: str, state: FSMContext):
    user_language_code = await get_user_language(user_id, state.storage)
    user = await get_user(user_id)

    subscription = await get_subscription(user.subscription_id)
    if subscription and (
        subscription.status == SubscriptionStatus.ACTIVE or subscription.status == SubscriptionStatus.TRIAL
    ):
        text = get_localization(user_language_code).PROFILE_CANCEL_SUBSCRIPTION_CONFIRMATION
        reply_markup = build_cancel_subscription_keyboard(user_language_code)
    else:
        text = get_localization(user_language_code).PROFILE_NO_ACTIVE_SUBSCRIPTION
        reply_markup = None

    await message.answer(
        text=text,
        reply_markup=reply_markup,
    )


async def handle_renew_subscription(message: Message, user_id: str, state: FSMContext):
    user_language_code = await get_user_language(user_id, state.storage)
    user = await get_user(user_id)

    old_subscription = await get_subscription(user.subscription_id)

    transaction = firebase.db.transaction()
    await resubscribe_wrapper(transaction, old_subscription, message.bot)

    await message.answer(
        text=get_localization(user_language_code).PROFILE_RENEW_SUBSCRIPTION_SUCCESS,
        message_effect_id=config.MESSAGE_EFFECTS.get(MessageEffect.HEART),
    )


@payment_router.callback_query(lambda c: c.data.startswith('cancel_subscription:'))
async def handle_cancel_subscription_selection(callback_query: CallbackQuery, state: FSMContext):
    await callback_query.answer()

    user_id = str(callback_query.from_user.id)

    action = callback_query.data.split(':')[1]
    if action == 'approve':
        user = await get_user(user_id)
        old_subscription = await get_subscription(user.subscription_id)

        transaction = firebase.db.transaction()
        await unsubscribe_wrapper(transaction, old_subscription, callback_query.bot)

        user_language_code = await get_user_language(user_id, state.storage)
        await callback_query.message.edit_text(
            text=get_localization(user_language_code).PROFILE_CANCEL_SUBSCRIPTION_SUCCESS,
        )
    else:
        await callback_query.message.delete()
