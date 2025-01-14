from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

from bot.database.models.generation import GenerationReaction
from bot.locales.main import get_localization
from bot.locales.types import LanguageCode


def build_start_keyboard(language_code: LanguageCode) -> InlineKeyboardMarkup:
    buttons = [
        [
            InlineKeyboardButton(
                text=get_localization(language_code).START_QUICK_GUIDE,
                callback_data='start:quick_guide'
            )
        ],
    ]

    return InlineKeyboardMarkup(inline_keyboard=buttons)


def build_start_chosen_keyboard(language_code: LanguageCode) -> InlineKeyboardMarkup:
    buttons = [
        [
            InlineKeyboardButton(
                text=get_localization(language_code).ACTION_BACK,
                callback_data='start:back'
            )
        ],
    ]

    return InlineKeyboardMarkup(inline_keyboard=buttons)


def build_continue_generating_keyboard(language_code: LanguageCode) -> InlineKeyboardMarkup:
    buttons = [
        [
            InlineKeyboardButton(
                text=get_localization(language_code).MODEL_CONTINUE_GENERATING,
                callback_data='continue_generation:continue'
            )
        ]
    ]

    return InlineKeyboardMarkup(inline_keyboard=buttons)


def build_reaction_keyboard(generation_id: str) -> InlineKeyboardMarkup:
    buttons = [
        [
            InlineKeyboardButton(
                text='👍',
                callback_data=f'reaction:{GenerationReaction.LIKED}:{generation_id}'
            ),
            InlineKeyboardButton(
                text='👎',
                callback_data=f'reaction:{GenerationReaction.DISLIKED}:{generation_id}'
            ),
        ],
    ]

    return InlineKeyboardMarkup(inline_keyboard=buttons)


def build_buy_motivation_keyboard(language_code: LanguageCode) -> InlineKeyboardMarkup:
    buttons = [
        [
            InlineKeyboardButton(
                text=get_localization(language_code).OPEN_BONUS_INFO,
                callback_data='buy_motivation:open_bonus_info'
            )
        ],
        [
            InlineKeyboardButton(
                text=get_localization(language_code).OPEN_BUY_SUBSCRIPTIONS_INFO,
                callback_data='buy_motivation:open_buy_subscriptions_info'
            )
        ],
        [
            InlineKeyboardButton(
                text=get_localization(language_code).OPEN_BUY_PACKAGES_INFO,
                callback_data='buy_motivation:open_buy_packages_info'
            )
        ],
    ]

    return InlineKeyboardMarkup(inline_keyboard=buttons)


def build_time_limit_exceeded_keyboard(language_code: LanguageCode) -> InlineKeyboardMarkup:
    buttons = [
        [
            InlineKeyboardButton(
                text=get_localization(language_code).REMOVE_RESTRICTION,
                callback_data='time_limit_exceeded:remove_restriction'
            )
        ],
    ]

    return InlineKeyboardMarkup(inline_keyboard=buttons)


def build_time_limit_exceeded_chosen_keyboard(language_code: LanguageCode) -> InlineKeyboardMarkup:
    buttons = [
        [
            InlineKeyboardButton(
                text=get_localization(language_code).OPEN_BONUS_INFO,
                callback_data='limit_exceeded:open_bonus_info'
            )
        ],
        [
            InlineKeyboardButton(
                text=get_localization(language_code).OPEN_BUY_SUBSCRIPTIONS_INFO,
                callback_data='limit_exceeded:open_buy_subscriptions_info'
            )
        ],
        [
            InlineKeyboardButton(
                text=get_localization(language_code).OPEN_BUY_PACKAGES_INFO,
                callback_data='limit_exceeded:open_buy_packages_info'
            )
        ],
    ]

    return InlineKeyboardMarkup(inline_keyboard=buttons)


def build_notify_about_quota_keyboard(language_code: LanguageCode) -> InlineKeyboardMarkup:
    buttons = [
        [
            InlineKeyboardButton(
                text=get_localization(language_code).MODEL_SWITCHED_TO_AI_EXAMPLES,
                callback_data=f'notify_about_quota:examples'
            )
        ],
        [
            InlineKeyboardButton(
                text=get_localization(language_code).NOTIFY_ABOUT_QUOTA_TURN_OFF,
                callback_data=f'notify_about_quota:turn_off'
            )
        ],
    ]

    return InlineKeyboardMarkup(inline_keyboard=buttons)


def build_suggestions_keyboard(language_code: LanguageCode) -> InlineKeyboardMarkup:
    buttons = [
        [
            InlineKeyboardButton(
                text=get_localization(language_code).MODEL_CHANGE_AI,
                callback_data='suggestions:change_ai_model'
            )
        ],
    ]

    return InlineKeyboardMarkup(inline_keyboard=buttons)


def build_cancel_keyboard(language_code: LanguageCode) -> InlineKeyboardMarkup:
    buttons = [
        [
            InlineKeyboardButton(
                text=get_localization(language_code).ACTION_CANCEL,
                callback_data='common:cancel'
            )
        ],
    ]

    return InlineKeyboardMarkup(inline_keyboard=buttons)


def build_error_keyboard(language_code: LanguageCode) -> InlineKeyboardMarkup:
    buttons = [
        [
            InlineKeyboardButton(
                text=get_localization(language_code).TECH_SUPPORT,
                url='https://t.me/roman_danilov',
                callback_data='error:tech_support'
            )
        ],
    ]

    return InlineKeyboardMarkup(inline_keyboard=buttons)
