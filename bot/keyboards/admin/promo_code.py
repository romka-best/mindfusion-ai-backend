from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup

from bot.database.models.product import Product
from bot.database.models.promo_code import PromoCodeType
from bot.locales.main import get_localization
from bot.locales.types import LanguageCode


def build_create_promo_code_keyboard(
    language_code: LanguageCode,
) -> InlineKeyboardMarkup:
    buttons = [
        [
            InlineKeyboardButton(
                text=get_localization(language_code).SUBSCRIPTION,
                callback_data=f"create_promo_code:{PromoCodeType.SUBSCRIPTION}",
            )
        ],
        [
            InlineKeyboardButton(
                text=get_localization(language_code).PACKAGE,
                callback_data=f"create_promo_code:{PromoCodeType.PACKAGE}",
            )
        ],
        [
            InlineKeyboardButton(
                text=get_localization(language_code).PAYMENT_DISCOUNT,
                callback_data=f"create_promo_code:{PromoCodeType.DISCOUNT}",
            )
        ],
        [
            InlineKeyboardButton(
                text=get_localization(language_code).ACTION_BACK,
                callback_data="create_promo_code:back",
            )
        ],
    ]

    return InlineKeyboardMarkup(inline_keyboard=buttons)


def build_create_promo_code_subscription_keyboard(
    language_code: LanguageCode,
    products: list[Product],
) -> InlineKeyboardMarkup:
    buttons = []
    for product in products:
        buttons.append(
            [
                InlineKeyboardButton(
                    text=product.names.get(language_code),
                    callback_data=f"create_promo_code_subscription:{product.id}",
                ),
            ]
        )
    buttons.append(
        [
            InlineKeyboardButton(
                text=get_localization(language_code).ACTION_CANCEL,
                callback_data="create_promo_code_subscription:cancel",
            )
        ]
    )

    return InlineKeyboardMarkup(inline_keyboard=buttons)


def build_create_promo_code_package_keyboard(
    language_code: LanguageCode, products: list[Product]
):
    buttons = []
    for product in products:
        buttons.append(
            [
                InlineKeyboardButton(
                    text=product.names.get(language_code),
                    callback_data=f"create_promo_code_package:{product.id}",
                ),
            ],
        )
    buttons.append(
        [
            InlineKeyboardButton(
                text=get_localization(language_code).ACTION_CANCEL,
                callback_data="create_promo_code_package:cancel",
            )
        ],
    )

    return InlineKeyboardMarkup(inline_keyboard=buttons)


def build_create_promo_code_discount_keyboard(language_code: LanguageCode):
    buttons = [
        [
            InlineKeyboardButton(
                text="5%", callback_data="create_promo_code_discount:5"
            ),
            InlineKeyboardButton(
                text="10%", callback_data="create_promo_code_discount:10"
            ),
        ],
        [
            InlineKeyboardButton(
                text="15%", callback_data="create_promo_code_discount:15"
            ),
            InlineKeyboardButton(
                text="20%", callback_data="create_promo_code_discount:20"
            ),
        ],
        [
            InlineKeyboardButton(
                text="25%", callback_data="create_promo_code_discount:25"
            ),
            InlineKeyboardButton(
                text="30%", callback_data="create_promo_code_discount:30"
            ),
        ],
        [
            InlineKeyboardButton(
                text=get_localization(language_code).ACTION_CANCEL,
                callback_data="create_promo_code_discount:cancel",
            )
        ],
    ]

    return InlineKeyboardMarkup(inline_keyboard=buttons)
