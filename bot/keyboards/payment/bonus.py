from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup

from bot.database.models.common import Currency
from bot.database.models.game import GameType
from bot.database.models.product import (
    Product,
    ProductCategory,
    ProductCategorySymbols,
    ProductType,
)
from bot.locales.main import get_localization
from bot.locales.types import LanguageCode


def build_bonus_keyboard(language_code: LanguageCode) -> InlineKeyboardMarkup:
    buttons = [
        [
            InlineKeyboardButton(
                text=get_localization(language_code).BONUS_EARN,
                callback_data="bonus:earn",
            ),
            InlineKeyboardButton(
                text=get_localization(language_code).BONUS_SPEND,
                callback_data="bonus:spend",
            ),
        ],
    ]

    return InlineKeyboardMarkup(inline_keyboard=buttons)


def build_bonus_earn_keyboard(
    language_code: LanguageCode, user_id: str
) -> InlineKeyboardMarkup:
    buttons = [
        [
            InlineKeyboardButton(
                text=get_localization(language_code).BONUS_INVITE_FRIEND,
                url=get_localization(language_code).bonus_referral_link(user_id, True),
                callback_data="bonus_earn:invite_friend",
            ),
        ],
        [
            InlineKeyboardButton(
                text=get_localization(language_code).BONUS_LEAVE_FEEDBACK,
                callback_data="bonus_earn:leave_feedback",
            ),
        ],
        [
            InlineKeyboardButton(
                text=get_localization(language_code).BONUS_PLAY_GAME,
                callback_data="bonus_earn:play_game",
            ),
        ],
        [
            InlineKeyboardButton(
                text=get_localization(language_code).ACTION_BACK,
                callback_data="bonus_earn:back",
            ),
        ],
    ]

    return InlineKeyboardMarkup(inline_keyboard=buttons)


def build_bonus_play_game_keyboard(language_code: LanguageCode) -> InlineKeyboardMarkup:
    buttons = [
        [
            InlineKeyboardButton(
                text=get_localization(language_code).BONUS_PLAY_BOWLING_GAME,
                callback_data=f"bonus_play_game:{GameType.BOWLING}",
            ),
            InlineKeyboardButton(
                text=get_localization(language_code).BONUS_PLAY_SOCCER_GAME,
                callback_data=f"bonus_play_game:{GameType.SOCCER}",
            ),
        ],
        [
            InlineKeyboardButton(
                text=get_localization(language_code).BONUS_PLAY_BASKETBALL_GAME,
                callback_data=f"bonus_play_game:{GameType.BASKETBALL}",
            ),
            InlineKeyboardButton(
                text=get_localization(language_code).BONUS_PLAY_DARTS_GAME,
                callback_data=f"bonus_play_game:{GameType.DARTS}",
            ),
        ],
        [
            InlineKeyboardButton(
                text=get_localization(language_code).BONUS_PLAY_DICE_GAME,
                callback_data=f"bonus_play_game:{GameType.DICE}",
            ),
            InlineKeyboardButton(
                text=get_localization(language_code).BONUS_PLAY_CASINO_GAME,
                callback_data=f"bonus_play_game:{GameType.CASINO}",
            ),
        ],
        [
            InlineKeyboardButton(
                text=get_localization(language_code).ACTION_BACK,
                callback_data="bonus_play_game:back",
            ),
        ],
    ]

    return InlineKeyboardMarkup(inline_keyboard=buttons)


def build_bonus_play_game_chosen_keyboard(
    language_code: LanguageCode, game_type: GameType
) -> InlineKeyboardMarkup:
    buttons = []
    if (
        game_type == GameType.BOWLING
        or game_type == GameType.SOCCER
        or game_type == GameType.BASKETBALL
        or game_type == GameType.DARTS
        or game_type == GameType.CASINO
    ):
        buttons.append(
            [
                InlineKeyboardButton(
                    text=get_localization(language_code).BONUS_PLAY,
                    callback_data=f"bonus_play_game_chosen:{game_type}",
                ),
            ]
        )
    elif game_type == GameType.DICE:
        buttons.extend(
            [
                [
                    InlineKeyboardButton(
                        text=get_localization(
                            language_code
                        ).BONUS_PLAY_DICE_GAME_CHOOSE_1,
                        callback_data=f"bonus_play_game_chosen:{game_type}:1",
                    ),
                    InlineKeyboardButton(
                        text=get_localization(
                            language_code
                        ).BONUS_PLAY_DICE_GAME_CHOOSE_2,
                        callback_data=f"bonus_play_game_chosen:{game_type}:2",
                    ),
                ],
                [
                    InlineKeyboardButton(
                        text=get_localization(
                            language_code
                        ).BONUS_PLAY_DICE_GAME_CHOOSE_3,
                        callback_data=f"bonus_play_game_chosen:{game_type}:3",
                    ),
                    InlineKeyboardButton(
                        text=get_localization(
                            language_code
                        ).BONUS_PLAY_DICE_GAME_CHOOSE_4,
                        callback_data=f"bonus_play_game_chosen:{game_type}:4",
                    ),
                ],
                [
                    InlineKeyboardButton(
                        text=get_localization(
                            language_code
                        ).BONUS_PLAY_DICE_GAME_CHOOSE_5,
                        callback_data=f"bonus_play_game_chosen:{game_type}:5",
                    ),
                    InlineKeyboardButton(
                        text=get_localization(
                            language_code
                        ).BONUS_PLAY_DICE_GAME_CHOOSE_6,
                        callback_data=f"bonus_play_game_chosen:{game_type}:6",
                    ),
                ],
            ]
        )
    buttons.append(
        [
            InlineKeyboardButton(
                text=get_localization(language_code).ACTION_BACK,
                callback_data="bonus_play_game_chosen:back",
            ),
        ]
    )

    return InlineKeyboardMarkup(inline_keyboard=buttons)


def build_bonus_spend_keyboard(
    language_code: LanguageCode, products: list[Product], page=0
) -> InlineKeyboardMarkup:
    buttons = []

    if page == 0:
        buttons.append(
            [
                InlineKeyboardButton(
                    text=get_localization(language_code).MODELS_TEXT.upper(),
                    callback_data=f"bonus_spend:{ProductCategory.TEXT}",
                ),
            ]
        )
    elif page == 1:
        buttons.append(
            [
                InlineKeyboardButton(
                    text=get_localization(language_code).MODELS_SUMMARY.upper(),
                    callback_data=f"bonus_spend:{ProductCategory.SUMMARY}",
                ),
            ]
        )
    elif page == 2:
        buttons.append(
            [
                InlineKeyboardButton(
                    text=get_localization(language_code).MODELS_IMAGE.upper(),
                    callback_data=f"bonus_spend:{ProductCategory.IMAGE}",
                ),
            ]
        )
    elif page == 3:
        buttons.append(
            [
                InlineKeyboardButton(
                    text=get_localization(language_code).MODELS_MUSIC.upper(),
                    callback_data=f"bonus_spend:{ProductCategory.MUSIC}",
                ),
            ],
        )
    elif page == 4:
        buttons.append(
            [
                InlineKeyboardButton(
                    text=get_localization(language_code).MODELS_VIDEO.upper(),
                    callback_data=f"bonus_spend:{ProductCategory.VIDEO}",
                ),
            ],
        )

    for product in products:
        product_price = Product.get_discount_price(
            ProductType.PACKAGE,
            1,
            product.prices.get(Currency.XTR),
            Currency.XTR,
            0,
        )
        buttons.append(
            [
                InlineKeyboardButton(
                    text=f"{product.names.get(language_code)} – {product_price} 🪙",
                    callback_data=f"bonus_spend:{product.id}",
                ),
            ],
        )

    buttons.append(
        [
            InlineKeyboardButton(
                text="⬅️",
                callback_data=f"bonus_spend:prev:{page - 1 if page != 0 else 5}",
            ),
            InlineKeyboardButton(
                text=f"{page + 1}/6", callback_data=f"bonus_spend:page:{page}"
            ),
            InlineKeyboardButton(
                text="➡️",
                callback_data=f"bonus_spend:next:{page + 1 if page != 5 else 0}",
            ),
        ]
    )

    buttons.append(
        [
            InlineKeyboardButton(
                text=get_localization(language_code).ACTION_BACK,
                callback_data="bonus_spend:back",
            )
        ],
    )

    return InlineKeyboardMarkup(inline_keyboard=buttons)


def build_bonus_spend_selection_keyboard(
    language_code: LanguageCode, product: Product
) -> InlineKeyboardMarkup:
    buttons = []
    quantities = []
    if (
        product.category == ProductCategory.TEXT
        or product.category == ProductCategory.SUMMARY
        or product.category == ProductCategory.IMAGE
    ):
        quantities = [50, 100, 250, 500, 1000]
    elif (
        product.category == ProductCategory.MUSIC
        or product.category == ProductCategory.VIDEO
    ):
        quantities = [5, 10, 25, 50, 100]
    elif product.category == ProductCategory.OTHER:
        quantities = [1, 3, 6, 9, 12]

    for quantity in quantities:
        product_price = Product.get_discount_price(
            ProductType.PACKAGE,
            quantity,
            product.prices.get(Currency.XTR),
            Currency.XTR,
            0,
        )
        buttons.append(
            [
                InlineKeyboardButton(
                    text=f"{ProductCategorySymbols[product.category]} {quantity} – {product_price} 🪙",
                    callback_data=f"bonus_spend_selection:{quantity}",
                )
            ]
        )

    buttons.append(
        [
            InlineKeyboardButton(
                text=get_localization(language_code).ACTION_BACK,
                callback_data=f"bonus_spend_selection:back:{product.category}",
            )
        ]
    )

    return InlineKeyboardMarkup(inline_keyboard=buttons)


def build_bonus_suggestion_keyboard(
    language_code: LanguageCode,
) -> InlineKeyboardMarkup:
    buttons = [
        [
            InlineKeyboardButton(
                text=get_localization(language_code).OPEN_BONUS_INFO,
                callback_data="bonus_suggestion:open",
            )
        ],
    ]

    return InlineKeyboardMarkup(inline_keyboard=buttons)
