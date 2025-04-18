from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup

from bot.database.models.common import Currency
from bot.database.models.product import Product, ProductCategory, ProductType
from bot.database.models.transaction import TransactionType
from bot.locales.main import get_localization
from bot.locales.types import LanguageCode


def build_statistics_keyboard(
    language_code: LanguageCode, is_admin: bool
) -> InlineKeyboardMarkup:
    buttons = [
        [InlineKeyboardButton(text="За день 📅", callback_data="statistics:day")],
        [InlineKeyboardButton(text="За неделю 📆", callback_data="statistics:week")],
        [InlineKeyboardButton(text="За месяц 🗓️", callback_data="statistics:month")],
        [InlineKeyboardButton(text="За всё время ⏳", callback_data="statistics:all")],
    ]

    if is_admin:
        buttons.append(
            [
                InlineKeyboardButton(
                    text="Записать транзакцию ➕➖",
                    callback_data="statistics:write_transaction",
                )
            ]
        )

    buttons.append(
        [
            InlineKeyboardButton(
                text=get_localization(language_code).ACTION_BACK,
                callback_data="statistics:back",
            )
        ]
    )

    return InlineKeyboardMarkup(inline_keyboard=buttons)


def build_statistics_write_transaction_keyboard(
    language_code: LanguageCode,
) -> InlineKeyboardMarkup:
    buttons = [
        [
            InlineKeyboardButton(
                text="Записать доход 📈",
                callback_data=f"statistics_write_transaction:{TransactionType.INCOME}",
            )
        ],
        [
            InlineKeyboardButton(
                text="Записать расход 📉",
                callback_data=f"statistics_write_transaction:{TransactionType.EXPENSE}",
            )
        ],
        [
            InlineKeyboardButton(
                text=get_localization(language_code).ACTION_BACK,
                callback_data="statistics_write_transaction:back",
            )
        ],
    ]

    return InlineKeyboardMarkup(inline_keyboard=buttons)


def build_statistics_choose_service_keyboard(
    language_code: LanguageCode,
    products: list[Product],
    transaction_type: TransactionType,
) -> InlineKeyboardMarkup:
    buttons = []
    if transaction_type == TransactionType.INCOME:
        for product in products:
            if product.category == ProductCategory.MONTHLY:
                buttons.append(
                    [
                        InlineKeyboardButton(
                            text=f"{product.names.get(language_code)} {get_localization(language_code).SUBSCRIPTION_MONTHLY}",
                            callback_data=f"statistics_choose_service:{product.id}",
                        )
                    ]
                )
            elif product.category == ProductCategory.YEARLY:
                buttons.append(
                    [
                        InlineKeyboardButton(
                            text=f"{product.names.get(language_code)} {get_localization(language_code).SUBSCRIPTION_YEARLY}",
                            callback_data=f"statistics_choose_service:{product.id}",
                        )
                    ]
                )
            else:
                buttons.append(
                    [
                        InlineKeyboardButton(
                            text=product.names.get(language_code),
                            callback_data=f"statistics_choose_service:{product.id}",
                        )
                    ]
                )
        buttons.append(
            [
                InlineKeyboardButton(
                    text="Other 🤷", callback_data="statistics_choose_service:OTHER"
                )
            ]
        )
    elif transaction_type == TransactionType.EXPENSE:
        for product in products:
            if product.type == ProductType.PACKAGE:
                buttons.append(
                    [
                        InlineKeyboardButton(
                            text=product.names.get(language_code),
                            callback_data="statistics_choose_service:{product.id}",
                        )
                    ]
                )
        buttons.append(
            [
                InlineKeyboardButton(
                    text="Server 💻", callback_data="statistics_choose_service:SERVER"
                )
            ]
        )
        buttons.append(
            [
                InlineKeyboardButton(
                    text="Database 🗄",
                    callback_data="statistics_choose_service:DATABASE",
                )
            ]
        )
        buttons.append(
            [
                InlineKeyboardButton(
                    text="Other 🤷", callback_data="statistics_choose_service:OTHER"
                )
            ]
        )
    buttons.append(
        [
            InlineKeyboardButton(
                text=get_localization(language_code).ACTION_CANCEL,
                callback_data="statistics_choose_service:cancel",
            )
        ],
    )

    return InlineKeyboardMarkup(inline_keyboard=buttons)


def build_statistics_choose_currency_keyboard(
    language_code: LanguageCode,
) -> InlineKeyboardMarkup:
    buttons = [
        [
            InlineKeyboardButton(
                text="RUB ₽", callback_data=f"statistics_choose_currency:{Currency.RUB}"
            )
        ],
        [
            InlineKeyboardButton(
                text="USD $", callback_data=f"statistics_choose_currency:{Currency.USD}"
            )
        ],
        [
            InlineKeyboardButton(
                text="Telegram Stars ⭐",
                callback_data=f"statistics_choose_currency:{Currency.XTR}",
            )
        ],
        [
            InlineKeyboardButton(
                text=get_localization(language_code).ACTION_CANCEL,
                callback_data="statistics_choose_currency:cancel",
            )
        ],
    ]

    return InlineKeyboardMarkup(inline_keyboard=buttons)
