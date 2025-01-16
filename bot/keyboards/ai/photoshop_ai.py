from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

from bot.database.models.common import PhotoshopAIAction
from bot.locales.main import get_localization
from bot.locales.types import LanguageCode


def build_photoshop_ai_keyboard(language_code: LanguageCode) -> InlineKeyboardMarkup:
    buttons = [
        [
            InlineKeyboardButton(
                text=get_localization(language_code).PHOTOSHOP_AI_UPSCALE,
                callback_data=f'photoshop_ai:{PhotoshopAIAction.UPSCALE}',
            ),
        ],
        [
            InlineKeyboardButton(
                text=get_localization(language_code).PHOTOSHOP_AI_RESTORATION,
                callback_data=f'photoshop_ai:{PhotoshopAIAction.RESTORATION}',
            ),
        ],
        [
            InlineKeyboardButton(
                text=get_localization(language_code).PHOTOSHOP_AI_COLORIZATION,
                callback_data=f'photoshop_ai:{PhotoshopAIAction.COLORIZATION}',
            ),
        ],
        [
            InlineKeyboardButton(
                text=get_localization(language_code).PHOTOSHOP_AI_REMOVE_BACKGROUND,
                callback_data=f'photoshop_ai:{PhotoshopAIAction.REMOVAL_BACKGROUND}',
            ),
        ],
    ]

    return InlineKeyboardMarkup(inline_keyboard=buttons)


def build_photoshop_ai_chosen_keyboard(language_code: LanguageCode) -> InlineKeyboardMarkup:
    buttons = [
        [
            InlineKeyboardButton(
                text=get_localization(language_code).ACTION_BACK,
                callback_data=f'photoshop_ai_chosen:back',
            ),
        ],
    ]

    return InlineKeyboardMarkup(inline_keyboard=buttons)
