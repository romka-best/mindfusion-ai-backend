from typing import Optional

from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup

from bot.database.models.chat import Chat
from bot.database.models.common import Model
from bot.locales.main import get_localization
from bot.locales.types import LanguageCode


def build_chats_keyboard(
    language_code: LanguageCode,
    model: Optional[Model] = None,
) -> InlineKeyboardMarkup:
    buttons = [
        [
            InlineKeyboardButton(
                text=get_localization(language_code).CHAT_CREATE,
                callback_data="chat:create",
            ),
            InlineKeyboardButton(
                text=get_localization(language_code).CHAT_SWITCH,
                callback_data="chat:switch",
            ),
        ],
        [
            InlineKeyboardButton(
                text=get_localization(language_code).CHAT_RESET,
                callback_data="chat:reset",
            ),
            InlineKeyboardButton(
                text=get_localization(language_code).CHAT_DELETE,
                callback_data="chat:delete",
            ),
        ],
        [
            InlineKeyboardButton(
                text=get_localization(language_code).ACTION_BACK,
                callback_data=f"chat:back:{model}" if model else "chat:back",
            )
        ],
    ]

    return InlineKeyboardMarkup(inline_keyboard=buttons)


def build_create_chat_keyboard(language_code: LanguageCode) -> InlineKeyboardMarkup:
    buttons = [
        [
            InlineKeyboardButton(
                text=get_localization(language_code).ACTION_CANCEL,
                callback_data="create_chat:cancel",
            )
        ]
    ]

    return InlineKeyboardMarkup(inline_keyboard=buttons)


def build_switch_chat_keyboard(
    language_code: LanguageCode, current_chat_id: str, chats: list[Chat]
) -> InlineKeyboardMarkup:
    buttons = []
    for chat in chats:
        buttons.append(
            [
                InlineKeyboardButton(
                    text=f"{chat.title}"
                    + (" ✅" if current_chat_id == chat.id else " ❌"),
                    callback_data=f"switch_chat:{chat.id}",
                )
            ]
        )
    buttons.append(
        [
            InlineKeyboardButton(
                text=get_localization(language_code).ACTION_CANCEL,
                callback_data="switch_chat:cancel",
            )
        ]
    )

    return InlineKeyboardMarkup(inline_keyboard=buttons)


def build_delete_chat_keyboard(
    language_code: LanguageCode, current_chat_id: str, chats: list[Chat]
) -> InlineKeyboardMarkup:
    buttons = []
    for chat in chats:
        if current_chat_id != chat.id:
            buttons.append(
                [
                    InlineKeyboardButton(
                        text=chat.title, callback_data=f"delete_chat:{chat.id}"
                    )
                ]
            )
    buttons.append(
        [
            InlineKeyboardButton(
                text=get_localization(language_code).ACTION_CANCEL,
                callback_data="delete_chat:cancel",
            )
        ]
    )

    return InlineKeyboardMarkup(inline_keyboard=buttons)


def build_reset_chat_keyboard(language_code: LanguageCode) -> InlineKeyboardMarkup:
    buttons = [
        [
            InlineKeyboardButton(
                text=get_localization(language_code).ACTION_APPROVE,
                callback_data="reset_chat:approve",
            )
        ],
        [
            InlineKeyboardButton(
                text=get_localization(language_code).ACTION_CANCEL,
                callback_data="reset_chat:cancel",
            )
        ],
    ]

    return InlineKeyboardMarkup(inline_keyboard=buttons)
