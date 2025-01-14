from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

from bot.database.models.face_swap_package import FaceSwapPackage
from bot.locales.main import get_localization
from bot.locales.types import LanguageCode


def build_face_swap_choose_keyboard(language_code: LanguageCode, packages: list[FaceSwapPackage]) -> InlineKeyboardMarkup:
    buttons = []
    for package in packages:
        buttons.append(
            [
                InlineKeyboardButton(
                    text=package.translated_names.get(language_code, package.name),
                    callback_data=f'face_swap_choose:{package.name}'
                )
            ],
        )

    return InlineKeyboardMarkup(inline_keyboard=buttons)


def build_face_swap_package_keyboard(language_code: LanguageCode, quantities: list[int]) -> InlineKeyboardMarkup:
    buttons = []
    for i in range(0, len(quantities), 2):
        pair = quantities[i:i + 2]
        buttons.append([
            InlineKeyboardButton(
                text=f'🔹 {quantity}',
                callback_data=f'face_swap_package:{quantity}'
            ) for quantity in pair
        ])

    buttons.extend([
        [
            InlineKeyboardButton(
                text=get_localization(language_code).ACTION_BACK,
                callback_data='face_swap_package:back'
            )
        ],
    ])

    return InlineKeyboardMarkup(inline_keyboard=buttons)
