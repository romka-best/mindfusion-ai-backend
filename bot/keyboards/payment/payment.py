from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from stripe import Subscription

from bot.database.models.common import PaymentType, PaymentMethod, Currency
from bot.database.models.product import Product, ProductType, ProductCategory, ProductCategorySymbols
from bot.database.models.subscription import SubscriptionPeriod
from bot.helpers.getters.get_user_discount import get_user_discount
from bot.locales.main import get_localization
from bot.locales.types import LanguageCode


def build_buy_keyboard(language_code: LanguageCode) -> InlineKeyboardMarkup:
    buttons = [
        [
            InlineKeyboardButton(
                text=get_localization(language_code).SUBSCRIPTIONS,
                callback_data=f'buy:{PaymentType.SUBSCRIPTION}'
            ),
            InlineKeyboardButton(
                text=get_localization(language_code).PACKAGES,
                callback_data=f'buy:{PaymentType.PACKAGE}'
            ),
        ],
        [
            InlineKeyboardButton(
                text=get_localization(language_code).PROMO_CODE_ACTIVATE,
                callback_data=f'buy:promo_code'
            ),
        ],
    ]

    return InlineKeyboardMarkup(inline_keyboard=buttons)


def build_subscriptions_keyboard(
    subscriptions: list[Product],
    category: ProductCategory,
    currency: Currency,
    user_discount: int,
    language_code: LanguageCode,
) -> InlineKeyboardMarkup:
    buttons = []

    if currency != Currency.XTR:
        buttons.append([
            InlineKeyboardButton(
                text=get_localization(language_code).SUBSCRIPTION_MONTHLY + (
                    ' 🟢' if category == ProductCategory.MONTHLY else ''
                ),
                callback_data=f'subscription:{ProductCategory.MONTHLY}'
            ),
            InlineKeyboardButton(
                text=get_localization(language_code).SUBSCRIPTION_YEARLY + (
                    ' 🟢' if category == ProductCategory.YEARLY else ''
                ),
                callback_data=f'subscription:{ProductCategory.YEARLY}'
            ),
        ])

    for subscription in subscriptions:
        discount = get_user_discount(user_discount, 0, subscription.discount)
        subscription_price = Product.get_discount_price(
            ProductType.SUBSCRIPTION,
            1,
            subscription.prices.get(currency),
            currency,
            discount,
        )
        buttons.append([
            InlineKeyboardButton(
                text=f'{subscription.names.get(language_code)} – {subscription_price}{Currency.SYMBOLS[currency]}',
                callback_data=f'subscription:{subscription.id}'
            ),
        ])

    buttons.extend([
        [
            InlineKeyboardButton(
                text=get_localization(language_code).PAYMENT_CHANGE_CURRENCY,
                callback_data=f'subscription:change_currency'
            ),
        ],
        [
            InlineKeyboardButton(
                text=get_localization(language_code).ACTION_BACK,
                callback_data='subscription:back'
            )
        ],
    ])

    return InlineKeyboardMarkup(inline_keyboard=buttons)


def build_payment_method_for_subscription_keyboard(
    language_code: LanguageCode,
    subscription_id: str,
) -> InlineKeyboardMarkup:
    buttons = [
        [
            InlineKeyboardButton(
                text=f'{get_localization(language_code).PAYMENT_YOOKASSA_PAYMENT_METHOD}',
                callback_data=f'pms:{PaymentMethod.YOOKASSA}:{subscription_id}'
            ),
        ],
        [
            InlineKeyboardButton(
                text=f'{get_localization(language_code).PAYMENT_STRIPE_PAYMENT_METHOD}',
                callback_data=f'pms:{PaymentMethod.STRIPE}:{subscription_id}'
            ),
        ],
        [
            InlineKeyboardButton(
                text=f'{get_localization(language_code).PAYMENT_TELEGRAM_STARS_PAYMENT_METHOD}',
                callback_data=f'pms:{PaymentMethod.TELEGRAM_STARS}:{subscription_id}'
            ),
        ],
        [
            InlineKeyboardButton(
                text=get_localization(language_code).ACTION_BACK,
                callback_data='pms:back'
            )
        ],
    ]

    return InlineKeyboardMarkup(inline_keyboard=buttons)


def build_payment_keyboard(language_code: LanguageCode, payment_link: str) -> InlineKeyboardMarkup:
    buttons = [
        [
            InlineKeyboardButton(
                text=get_localization(language_code).PAYMENT_PROCEED_TO_PAY,
                url=payment_link,
                callback_data=f'payment:pay'
            ),
        ],
    ]

    return InlineKeyboardMarkup(inline_keyboard=buttons)


def build_cancel_subscription_keyboard(language_code: LanguageCode) -> InlineKeyboardMarkup:
    buttons = [
        [
            InlineKeyboardButton(
                text=get_localization(language_code).ACTION_APPROVE,
                callback_data=f'cancel_subscription:approve'
            )
        ],
        [
            InlineKeyboardButton(
                text=get_localization(language_code).ACTION_CANCEL,
                callback_data=f'cancel_subscription:cancel'
            )
        ],
    ]

    return InlineKeyboardMarkup(inline_keyboard=buttons)


def build_packages_keyboard(
    language_code: LanguageCode,
    products: list[Product],
    currency: Currency,
    discount: int,
    page=0,
) -> InlineKeyboardMarkup:
    buttons = [
        [
            InlineKeyboardButton(
                text=get_localization(language_code).SHOPPING_CART,
                callback_data='package:cart'
            )
        ],
    ]

    if page == 0:
        buttons.append([
            InlineKeyboardButton(
                text=get_localization(language_code).MODELS_TEXT.upper(),
                callback_data=f'package:{ProductCategory.TEXT}',
            ),
        ])
    elif page == 1:
        buttons.append([
            InlineKeyboardButton(
                text=get_localization(language_code).MODELS_SUMMARY.upper(),
                callback_data=f'package:{ProductCategory.SUMMARY}',
            ),
        ])
    elif page == 2:
        buttons.append([
            InlineKeyboardButton(
                text=get_localization(language_code).MODELS_IMAGE.upper(),
                callback_data=f'package:{ProductCategory.IMAGE}',
            ),
        ])
    elif page == 3:
        buttons.append([
            InlineKeyboardButton(
                text=get_localization(language_code).MODELS_MUSIC.upper(),
                callback_data=f'package:{ProductCategory.MUSIC}',
            ),
        ])
    elif page == 4:
        buttons.append(
            [
                InlineKeyboardButton(
                    text=get_localization(language_code).MODELS_VIDEO.upper(),
                    callback_data=f'package:{ProductCategory.VIDEO}',
                ),
            ],
        )

    for product in products:
        product_price = Product.get_discount_price(
            ProductType.PACKAGE,
            1,
            product.prices.get(currency),
            currency,
            discount,
        )
        buttons.append(
            [
                InlineKeyboardButton(
                    text=f'{product.names.get(language_code)} – {product_price}{Currency.SYMBOLS[currency]}',
                    callback_data=f'package:{product.id}'
                ),
            ],
        )

    buttons.append([
        InlineKeyboardButton(
            text='⬅️',
            callback_data=f'package:prev:{page - 1 if page != 0 else 5}'
        ),
        InlineKeyboardButton(
            text=f'{page + 1}/6',
            callback_data=f'package:page:{page}'
        ),
        InlineKeyboardButton(
            text='➡️',
            callback_data=f'package:next:{page + 1 if page != 5 else 0}'
        ),
    ])
    buttons.extend(
        [
            [
                InlineKeyboardButton(
                    text=get_localization(language_code).PAYMENT_CHANGE_CURRENCY,
                    callback_data=f'package:change_currency:{page}'
                ),
            ],
            [
                InlineKeyboardButton(
                    text=get_localization(language_code).ACTION_BACK,
                    callback_data='package:back'
                )
            ],
        ],
    )

    return InlineKeyboardMarkup(inline_keyboard=buttons)


def build_package_selection_keyboard(
    language_code: LanguageCode,
    product: Product,
    currency: Currency,
    discount: int,
) -> InlineKeyboardMarkup:
    buttons = []
    quantities = []
    if (
        product.category == ProductCategory.TEXT or
        product.category == ProductCategory.SUMMARY or
        product.category == ProductCategory.IMAGE
    ):
        quantities = [50, 100, 250, 500, 1000]
    elif (
        product.category == ProductCategory.MUSIC or
        product.category == ProductCategory.VIDEO
    ):
        quantities = [5, 10, 25, 50, 100]
    elif product.category == ProductCategory.OTHER:
        quantities = [1, 3, 6, 9, 12]

    for quantity in quantities:
        product_price = Product.get_discount_price(
            ProductType.PACKAGE,
            quantity,
            product.prices.get(currency),
            currency,
            discount,
        )
        buttons.append([
            InlineKeyboardButton(
                text=f'{ProductCategorySymbols[product.category]} {quantity} – {product_price}{Currency.SYMBOLS[currency]}',
                callback_data=f'package_selection:{quantity}'
            )
        ])

    buttons.append([
        InlineKeyboardButton(
            text=get_localization(language_code).ACTION_BACK,
            callback_data=f'package_selection:back:{product.category}'
        )
    ])

    return InlineKeyboardMarkup(inline_keyboard=buttons)


def build_package_quantity_sent_keyboard(language_code: LanguageCode) -> InlineKeyboardMarkup:
    buttons = [
        [
            InlineKeyboardButton(
                text=get_localization(language_code).SHOPPING_CART_ADD,
                callback_data='package_quantity_sent:add_to_cart'
            ),
            InlineKeyboardButton(
                text=get_localization(language_code).SHOPPING_CART_BUY_NOW,
                callback_data='package_quantity_sent:buy_now'
            ),
        ],
        [
            InlineKeyboardButton(
                text=get_localization(language_code).ACTION_BACK,
                callback_data='package_quantity_sent:back'
            ),
        ],
    ]

    return InlineKeyboardMarkup(inline_keyboard=buttons)


def build_package_add_to_cart_selection_keyboard(language_code: LanguageCode) -> InlineKeyboardMarkup:
    buttons = [
        [
            InlineKeyboardButton(
                text=get_localization(language_code).SHOPPING_CART_GO_TO,
                callback_data='package_add_to_cart_selection:go_to_cart'
            )
        ],
        [
            InlineKeyboardButton(
                text=get_localization(language_code).SHOPPING_CART_CONTINUE_SHOPPING,
                callback_data='package_add_to_cart_selection:continue_shopping'
            )
        ],
    ]

    return InlineKeyboardMarkup(inline_keyboard=buttons)


def build_package_cart_keyboard(
    language_code: LanguageCode,
    is_empty: bool,
) -> InlineKeyboardMarkup:
    buttons = []
    if not is_empty:
        buttons.extend([
            [
                InlineKeyboardButton(
                    text=get_localization(language_code).PAYMENT_PROCEED_TO_CHECKOUT,
                    callback_data='package_cart:proceed_to_checkout'
                )
            ],
            [
                InlineKeyboardButton(
                    text=get_localization(language_code).SHOPPING_CART_CLEAR,
                    callback_data='package_cart:clear'
                )
            ],
        ])
    buttons.extend([
        [
            InlineKeyboardButton(
                text=get_localization(language_code).PAYMENT_CHANGE_CURRENCY,
                callback_data=f'package_cart:change_currency'
            ),
        ],
        [
            InlineKeyboardButton(
                text=get_localization(language_code).ACTION_BACK,
                callback_data='package_cart:back'
            )
        ],
    ])

    return InlineKeyboardMarkup(inline_keyboard=buttons)


def build_payment_method_for_package_keyboard(
    language_code: LanguageCode,
    package_product_id: str,
    package_quantity: int,
) -> InlineKeyboardMarkup:
    buttons = [
        [
            InlineKeyboardButton(
                text=f'{get_localization(language_code).PAYMENT_YOOKASSA_PAYMENT_METHOD}',
                callback_data=f'pmp:{PaymentMethod.YOOKASSA}:{package_product_id}:{package_quantity}'
            ),
        ],
        [
            InlineKeyboardButton(
                text=f'{get_localization(language_code).PAYMENT_STRIPE_PAYMENT_METHOD}',
                callback_data=f'pmp:{PaymentMethod.STRIPE}:{package_product_id}:{package_quantity}'
            ),
        ],
        [
            InlineKeyboardButton(
                text=f'{get_localization(language_code).PAYMENT_TELEGRAM_STARS_PAYMENT_METHOD}',
                callback_data=f'pmp:{PaymentMethod.TELEGRAM_STARS}:{package_product_id}:{package_quantity}'
            ),
        ],
        [
            InlineKeyboardButton(
                text=get_localization(language_code).ACTION_BACK,
                callback_data='pmp:back'
            )
        ],
    ]

    return InlineKeyboardMarkup(inline_keyboard=buttons)


def build_payment_method_for_cart_keyboard(language_code: LanguageCode) -> InlineKeyboardMarkup:
    buttons = [
        [
            InlineKeyboardButton(
                text=f'{get_localization(language_code).PAYMENT_YOOKASSA_PAYMENT_METHOD}',
                callback_data=f'pmc:{PaymentMethod.YOOKASSA}'
            ),
        ],
        [
            InlineKeyboardButton(
                text=f'{get_localization(language_code).PAYMENT_STRIPE_PAYMENT_METHOD}',
                callback_data=f'pmc:{PaymentMethod.STRIPE}'
            ),
        ],
        [
            InlineKeyboardButton(
                text=f'{get_localization(language_code).PAYMENT_TELEGRAM_STARS_PAYMENT_METHOD}',
                callback_data=f'pmc:{PaymentMethod.TELEGRAM_STARS}'
            ),
        ],
        [
            InlineKeyboardButton(
                text=get_localization(language_code).ACTION_BACK,
                callback_data='pmc:back'
            )
        ],
    ]

    return InlineKeyboardMarkup(inline_keyboard=buttons)


def build_return_to_packages_keyboard(language_code: LanguageCode) -> InlineKeyboardMarkup:
    buttons = [
        [
            InlineKeyboardButton(
                text=get_localization(language_code).ACTION_BACK,
                callback_data=f'pmp:back'
            ),
        ],
    ]

    return InlineKeyboardMarkup(inline_keyboard=buttons)


def build_return_to_cart_keyboard(language_code: LanguageCode) -> InlineKeyboardMarkup:
    buttons = [
        [
            InlineKeyboardButton(
                text=get_localization(language_code).ACTION_BACK,
                callback_data=f'pmc:back'
            ),
        ],
    ]

    return InlineKeyboardMarkup(inline_keyboard=buttons)
