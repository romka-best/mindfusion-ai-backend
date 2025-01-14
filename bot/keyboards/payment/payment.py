from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

from bot.database.models.common import PaymentType, PaymentMethod, Currency
from bot.database.models.product import Product, ProductCategory
from bot.locales.main import get_localization
from bot.locales.types import LanguageCode


def build_buy_keyboard(language_code: LanguageCode) -> InlineKeyboardMarkup:
    buttons = [
        [
            InlineKeyboardButton(
                text=get_localization(language_code).SUBSCRIPTION,
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
        subscription_id = subscription.id
        subscription_name = subscription.names.get(language_code)
        buttons.append([
            InlineKeyboardButton(
                text=subscription_name,
                callback_data=f'subscription:{subscription_id}'
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


def build_packages_keyboard(language_code: LanguageCode, products: list[Product], page=0) -> InlineKeyboardMarkup:
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
        for product in products:
            buttons.append(
                [
                    InlineKeyboardButton(
                        text=product.names.get(language_code),
                        callback_data=f'package:{product.id}'
                    ),
                ],
            )
        buttons.append(
            [
                InlineKeyboardButton(
                    text='⬅️',
                    callback_data='package:prev:5'
                ),
                InlineKeyboardButton(
                    text='1/6',
                    callback_data='package:page:0'
                ),
                InlineKeyboardButton(
                    text='➡️',
                    callback_data='package:next:1'
                ),
            ]
        )
    elif page == 1:
        buttons.append([
            InlineKeyboardButton(
                text=get_localization(language_code).MODELS_SUMMARY.upper(),
                callback_data=f'package:{ProductCategory.SUMMARY}',
            ),
        ])
        for product in products:
            buttons.append(
                [
                    InlineKeyboardButton(
                        text=product.names.get(language_code),
                        callback_data=f'package:{product.id}'
                    ),
                ],
            )
        buttons.append(
            [
                InlineKeyboardButton(
                    text='⬅️',
                    callback_data='package:prev:0'
                ),
                InlineKeyboardButton(
                    text='2/6',
                    callback_data='package:page:1'
                ),
                InlineKeyboardButton(
                    text='➡️',
                    callback_data='package:next:2'
                ),
            ]
        )
    elif page == 2:
        buttons.append([
            InlineKeyboardButton(
                text=get_localization(language_code).MODELS_IMAGE.upper(),
                callback_data=f'package:{ProductCategory.IMAGE}',
            ),
        ])
        for product in products:
            buttons.append(
                [
                    InlineKeyboardButton(
                        text=product.names.get(language_code),
                        callback_data=f'package:{product.id}'
                    ),
                ],
            )
        buttons.append(
            [
                InlineKeyboardButton(
                    text='⬅️',
                    callback_data='package:prev:1'
                ),
                InlineKeyboardButton(
                    text='3/6',
                    callback_data='package:page:2'
                ),
                InlineKeyboardButton(
                    text='➡️',
                    callback_data='package:next:3'
                ),
            ]
        )
    elif page == 3:
        buttons.append(
            [
                InlineKeyboardButton(
                    text=get_localization(language_code).MODELS_MUSIC.upper(),
                    callback_data=f'package:{ProductCategory.MUSIC}',
                ),
            ],
        )
        for product in products:
            buttons.append(
                [
                    InlineKeyboardButton(
                        text=product.names.get(language_code),
                        callback_data=f'package:{product.id}'
                    ),
                ],
            )
        buttons.append(
            [
                InlineKeyboardButton(
                    text='⬅️',
                    callback_data='package:prev:2'
                ),
                InlineKeyboardButton(
                    text='4/6',
                    callback_data='package:page:3'
                ),
                InlineKeyboardButton(
                    text='➡️',
                    callback_data='package:next:4'
                ),
            ]
        )
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
            buttons.append(
                [
                    InlineKeyboardButton(
                        text=product.names.get(language_code),
                        callback_data=f'package:{product.id}'
                    ),
                ],
            )
        buttons.append(
            [
                InlineKeyboardButton(
                    text='⬅️',
                    callback_data='package:prev:3'
                ),
                InlineKeyboardButton(
                    text='5/6',
                    callback_data='package:page:4'
                ),
                InlineKeyboardButton(
                    text='➡️',
                    callback_data='package:next:5'
                ),
            ]
        )
    elif page == 5:
        for product in products:
            buttons.append(
                [
                    InlineKeyboardButton(
                        text=product.names.get(language_code),
                        callback_data=f'package:{product.id}'
                    ),
                ],
            )
        buttons.append(
            [
                InlineKeyboardButton(
                    text='⬅️',
                    callback_data='package:prev:4'
                ),
                InlineKeyboardButton(
                    text='6/6',
                    callback_data='package:page:5'
                ),
                InlineKeyboardButton(
                    text='➡️',
                    callback_data='package:next:0'
                ),
            ]
        )

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


def build_package_selection_keyboard(language_code: LanguageCode) -> InlineKeyboardMarkup:
    buttons = [
        [
            InlineKeyboardButton(
                text=get_localization(language_code).ACTION_BACK,
                callback_data='package_selection:back'
            )
        ],
    ]

    return InlineKeyboardMarkup(inline_keyboard=buttons)


def build_package_quantity_sent_keyboard(language_code: LanguageCode) -> InlineKeyboardMarkup:
    buttons = [
        [
            InlineKeyboardButton(
                text=get_localization(language_code).SHOPPING_CART_ADD,
                callback_data='package_quantity_sent:add_to_cart'
            )
        ],
        [
            InlineKeyboardButton(
                text=get_localization(language_code).SHOPPING_CART_BUY_NOW,
                callback_data='package_quantity_sent:buy_now'
            )
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


def build_package_cart_keyboard(language_code: LanguageCode) -> InlineKeyboardMarkup:
    buttons = [
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
    ]

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
