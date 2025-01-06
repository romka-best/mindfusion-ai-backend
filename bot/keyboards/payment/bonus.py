from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

from bot.database.models.game import GameType
from bot.database.models.product import Product, ProductCategory
from bot.locales.main import get_localization
from bot.locales.types import LanguageCode


def build_bonus_keyboard(language_code: LanguageCode, user_id: str) -> InlineKeyboardMarkup:
    buttons = [
        [
            InlineKeyboardButton(
                text=get_localization(language_code).BONUS_INVITE_FRIEND,
                url=get_localization(language_code).bonus_referral_link(user_id, True),
                callback_data=f'bonus:invite_friend'
            ),
        ],
        [
            InlineKeyboardButton(
                text=get_localization(language_code).BONUS_LEAVE_FEEDBACK,
                callback_data=f'bonus:leave_feedback'
            ),
        ],
        [
            InlineKeyboardButton(
                text=get_localization(language_code).BONUS_PLAY_GAME,
                callback_data=f'bonus:play_game'
            ),
        ],
        [
            InlineKeyboardButton(
                text=get_localization(language_code).BONUS_CASH_OUT,
                callback_data=f'bonus:cash_out'
            ),
        ],
        [
            InlineKeyboardButton(
                text=get_localization(language_code).ACTION_CLOSE,
                callback_data=f'bonus:close'
            ),
        ],
    ]

    return InlineKeyboardMarkup(inline_keyboard=buttons)


def build_bonus_play_game_keyboard(language_code: LanguageCode) -> InlineKeyboardMarkup:
    buttons = [
        [
            InlineKeyboardButton(
                text=get_localization(language_code).BONUS_PLAY_BOWLING_GAME,
                callback_data=f'bonus_play_game:{GameType.BOWLING}'
            ),
        ],
        [
            InlineKeyboardButton(
                text=get_localization(language_code).BONUS_PLAY_SOCCER_GAME,
                callback_data=f'bonus_play_game:{GameType.SOCCER}'
            ),
        ],
        [
            InlineKeyboardButton(
                text=get_localization(language_code).BONUS_PLAY_BASKETBALL_GAME,
                callback_data=f'bonus_play_game:{GameType.BASKETBALL}'
            ),
        ],
        [
            InlineKeyboardButton(
                text=get_localization(language_code).BONUS_PLAY_DARTS_GAME,
                callback_data=f'bonus_play_game:{GameType.DARTS}'
            ),
        ],
        [
            InlineKeyboardButton(
                text=get_localization(language_code).BONUS_PLAY_DICE_GAME,
                callback_data=f'bonus_play_game:{GameType.DICE}'
            ),
        ],
        [
            InlineKeyboardButton(
                text=get_localization(language_code).BONUS_PLAY_CASINO_GAME,
                callback_data=f'bonus_play_game:{GameType.CASINO}'
            ),
        ],
        [
            InlineKeyboardButton(
                text=get_localization(language_code).ACTION_BACK,
                callback_data=f'bonus_play_game:back'
            ),
        ],
    ]

    return InlineKeyboardMarkup(inline_keyboard=buttons)


def build_bonus_play_game_chosen_keyboard(language_code: LanguageCode, game_type: GameType) -> InlineKeyboardMarkup:
    buttons = []
    if (
        game_type == GameType.BOWLING or
        game_type == GameType.SOCCER or
        game_type == GameType.BASKETBALL or
        game_type == GameType.DARTS or
        game_type == GameType.CASINO
    ):
        buttons.append([
            InlineKeyboardButton(
                text=get_localization(language_code).BONUS_PLAY,
                callback_data=f'bonus_play_game_chosen:{game_type}'
            ),
        ])
    elif game_type == GameType.DICE:
        buttons.extend([
            [
                InlineKeyboardButton(
                    text=get_localization(language_code).BONUS_PLAY_DICE_GAME_CHOOSE_1,
                    callback_data=f'bonus_play_game_chosen:{game_type}:1'
                ),
                InlineKeyboardButton(
                    text=get_localization(language_code).BONUS_PLAY_DICE_GAME_CHOOSE_2,
                    callback_data=f'bonus_play_game_chosen:{game_type}:2'
                ),
            ],
            [
                InlineKeyboardButton(
                    text=get_localization(language_code).BONUS_PLAY_DICE_GAME_CHOOSE_3,
                    callback_data=f'bonus_play_game_chosen:{game_type}:3'
                ),
                InlineKeyboardButton(
                    text=get_localization(language_code).BONUS_PLAY_DICE_GAME_CHOOSE_4,
                    callback_data=f'bonus_play_game_chosen:{game_type}:4'
                ),
            ],
            [
                InlineKeyboardButton(
                    text=get_localization(language_code).BONUS_PLAY_DICE_GAME_CHOOSE_5,
                    callback_data=f'bonus_play_game_chosen:{game_type}:5'
                ),
                InlineKeyboardButton(
                    text=get_localization(language_code).BONUS_PLAY_DICE_GAME_CHOOSE_6,
                    callback_data=f'bonus_play_game_chosen:{game_type}:6'
                ),
            ],
        ])
    buttons.append([
        InlineKeyboardButton(
            text=get_localization(language_code).ACTION_BACK,
            callback_data=f'bonus_play_game_chosen:back'
        ),
    ])

    return InlineKeyboardMarkup(inline_keyboard=buttons)


def build_bonus_cash_out_keyboard(language_code: LanguageCode, products: list[Product], page=0) -> InlineKeyboardMarkup:
    buttons = []

    if page == 0:
        buttons.append([
            InlineKeyboardButton(
                text=get_localization(language_code).MODELS_TEXT,
                callback_data=f'bonus_cash_out:{ProductCategory.TEXT}',
            ),
        ])
        for product in products:
            buttons.append(
                [
                    InlineKeyboardButton(
                        text=product.names.get(language_code),
                        callback_data=f'bonus_cash_out:{product.id}'
                    ),
                ],
            )
        buttons.append(
            [
                InlineKeyboardButton(
                    text='⬅️',
                    callback_data='bonus_cash_out:prev:5'
                ),
                InlineKeyboardButton(
                    text='1/6',
                    callback_data='bonus_cash_out:page:0'
                ),
                InlineKeyboardButton(
                    text='➡️',
                    callback_data='bonus_cash_out:next:1'
                ),
            ]
        )
    elif page == 1:
        buttons.append([
            InlineKeyboardButton(
                text=get_localization(language_code).MODELS_SUMMARY,
                callback_data=f'bonus_cash_out:{ProductCategory.SUMMARY}',
            ),
        ])
        for product in products:
            buttons.append(
                [
                    InlineKeyboardButton(
                        text=product.names.get(language_code),
                        callback_data=f'bonus_cash_out:{product.id}'
                    ),
                ],
            )
        buttons.append(
            [
                InlineKeyboardButton(
                    text='⬅️',
                    callback_data='bonus_cash_out:prev:0'
                ),
                InlineKeyboardButton(
                    text='2/6',
                    callback_data='bonus_cash_out:page:1'
                ),
                InlineKeyboardButton(
                    text='➡️',
                    callback_data='bonus_cash_out:next:2'
                ),
            ]
        )
    elif page == 2:
        buttons.append([
            InlineKeyboardButton(
                text=get_localization(language_code).MODELS_IMAGE,
                callback_data=f'bonus_cash_out:{ProductCategory.IMAGE}',
            ),
        ])
        for product in products:
            buttons.append(
                [
                    InlineKeyboardButton(
                        text=product.names.get(language_code),
                        callback_data=f'bonus_cash_out:{product.id}'
                    ),
                ],
            )
        buttons.append(
            [
                InlineKeyboardButton(
                    text='⬅️',
                    callback_data='bonus_cash_out:prev:1'
                ),
                InlineKeyboardButton(
                    text='3/6',
                    callback_data='bonus_cash_out:page:2'
                ),
                InlineKeyboardButton(
                    text='➡️',
                    callback_data='bonus_cash_out:next:3'
                ),
            ]
        )
    elif page == 3:
        buttons.append(
            [
                InlineKeyboardButton(
                    text=get_localization(language_code).MODELS_MUSIC,
                    callback_data=f'bonus_cash_out:{ProductCategory.MUSIC}',
                ),
            ],
        )
        for product in products:
            buttons.append(
                [
                    InlineKeyboardButton(
                        text=product.names.get(language_code),
                        callback_data=f'bonus_cash_out:{product.id}'
                    ),
                ],
            )
        buttons.append(
            [
                InlineKeyboardButton(
                    text='⬅️',
                    callback_data='bonus_cash_out:prev:2'
                ),
                InlineKeyboardButton(
                    text='4/6',
                    callback_data='bonus_cash_out:page:3'
                ),
                InlineKeyboardButton(
                    text='➡️',
                    callback_data='bonus_cash_out:next:4'
                ),
            ]
        )
    elif page == 4:
        buttons.append(
            [
                InlineKeyboardButton(
                    text=get_localization(language_code).MODELS_VIDEO,
                    callback_data=f'bonus_cash_out:{ProductCategory.VIDEO}',
                ),
            ],
        )
        for product in products:
            buttons.append(
                [
                    InlineKeyboardButton(
                        text=product.names.get(language_code),
                        callback_data=f'bonus_cash_out:{product.id}'
                    ),
                ],
            )
        buttons.append(
            [
                InlineKeyboardButton(
                    text='⬅️',
                    callback_data='bonus_cash_out:prev:3'
                ),
                InlineKeyboardButton(
                    text='5/6',
                    callback_data='bonus_cash_out:page:4'
                ),
                InlineKeyboardButton(
                    text='➡️',
                    callback_data='bonus_cash_out:next:5'
                ),
            ]
        )
    elif page == 5:
        for product in products:
            buttons.append(
                [
                    InlineKeyboardButton(
                        text=product.names.get(language_code),
                        callback_data=f'bonus_cash_out:{product.id}'
                    ),
                ],
            )
        buttons.append(
            [
                InlineKeyboardButton(
                    text='⬅️',
                    callback_data='bonus_cash_out:prev:4'
                ),
                InlineKeyboardButton(
                    text='6/6',
                    callback_data='bonus_cash_out:page:5'
                ),
                InlineKeyboardButton(
                    text='➡️',
                    callback_data='bonus_cash_out:next:0'
                ),
            ]
        )

    buttons.append(
        [
            InlineKeyboardButton(
                text=get_localization(language_code).ACTION_BACK,
                callback_data='bonus_cash_out:back'
            )
        ],
    )

    return InlineKeyboardMarkup(inline_keyboard=buttons)
