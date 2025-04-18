from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup

from bot.locales.main import get_localization
from bot.locales.types import LanguageCode


def build_admin_keyboard(language_code: LanguageCode) -> InlineKeyboardMarkup:
    buttons = [
        [
            InlineKeyboardButton(
                text="😇 Создать промокод",
                callback_data="admin:create_promo_code",
            ),
        ],
        [
            InlineKeyboardButton(
                text="📸 Управление контентом в FaceSwap",
                callback_data="admin:manage_face_swap",
            ),
        ],
        [
            InlineKeyboardButton(
                text="🎩 Управление ролями в чатах",
                callback_data="admin:manage_catalog",
            ),
        ],
        [
            InlineKeyboardButton(
                text="📊 Статистика",
                callback_data="admin:statistics",
            ),
        ],
        [
            InlineKeyboardButton(
                text="🏷 Реклама",
                callback_data="admin:ads",
            ),
        ],
        [
            InlineKeyboardButton(
                text="📣 Сделать рассылку",
                callback_data="admin:blast",
            ),
        ],
        [
            InlineKeyboardButton(
                text="⛔️ Бан/Разбан пользователя",
                callback_data="admin:ban",
            ),
        ],
        [
            InlineKeyboardButton(
                text=get_localization(language_code).ACTION_CLOSE,
                callback_data="admin:close",
            ),
        ],
    ]

    return InlineKeyboardMarkup(inline_keyboard=buttons)
