from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup

from bot.database.models.role import Role
from bot.locales.main import get_localization
from bot.locales.types import LanguageCode


def build_manage_catalog_keyboard(
    language_code: LanguageCode, roles: list[Role]
) -> InlineKeyboardMarkup:
    buttons = []
    for role in roles:
        buttons.append(
            [
                InlineKeyboardButton(
                    text=role.translated_names.get(language_code),
                    callback_data=f"catalog_manage:{role.id}",
                )
            ],
        )
    buttons.extend(
        [
            [
                InlineKeyboardButton(
                    text=get_localization(language_code).ADMIN_CATALOG_CREATE_ROLE,
                    callback_data="catalog_manage:create",
                )
            ],
            [
                InlineKeyboardButton(
                    text=get_localization(language_code).ACTION_BACK,
                    callback_data="catalog_manage:back",
                )
            ],
        ]
    )

    return InlineKeyboardMarkup(inline_keyboard=buttons)


def build_manage_catalog_create_keyboard(
    language_code: LanguageCode,
) -> InlineKeyboardMarkup:
    buttons = [
        [
            InlineKeyboardButton(
                text=get_localization(language_code).ACTION_BACK,
                callback_data="catalog_manage_create:back",
            )
        ],
        [
            InlineKeyboardButton(
                text=get_localization(language_code).ACTION_CANCEL,
                callback_data="catalog_manage_create:cancel",
            )
        ],
    ]

    return InlineKeyboardMarkup(inline_keyboard=buttons)


def build_manage_catalog_create_role_confirmation_keyboard(
    language_code: LanguageCode,
) -> InlineKeyboardMarkup:
    buttons = [
        [
            InlineKeyboardButton(
                text=get_localization(language_code).ACTION_APPROVE,
                callback_data="catalog_manage_create_role_confirmation:approve",
            )
        ],
        [
            InlineKeyboardButton(
                text=get_localization(language_code).ACTION_CANCEL,
                callback_data="catalog_manage_create_role_confirmation:cancel",
            )
        ],
    ]

    return InlineKeyboardMarkup(inline_keyboard=buttons)


def build_manage_catalog_edit_keyboard(
    language_code: LanguageCode, role_id: str
) -> InlineKeyboardMarkup:
    buttons = [
        [
            InlineKeyboardButton(
                text=get_localization(language_code).ADMIN_CATALOG_EDIT_ROLE_NAME,
                callback_data=f"catalog_manage_edit:name:{role_id}",
            )
        ],
        [
            InlineKeyboardButton(
                text=get_localization(
                    language_code
                ).ADMIN_CATALOG_EDIT_ROLE_DESCRIPTION,
                callback_data=f"catalog_manage_edit:description:{role_id}",
            )
        ],
        [
            InlineKeyboardButton(
                text=get_localization(
                    language_code
                ).ADMIN_CATALOG_EDIT_ROLE_INSTRUCTION,
                callback_data=f"catalog_manage_edit:instruction:{role_id}",
            )
        ],
        [
            InlineKeyboardButton(
                text=get_localization(language_code).ADMIN_CATALOG_EDIT_ROLE_PHOTO,
                callback_data=f"catalog_manage_edit:photo:{role_id}",
            )
        ],
        [
            InlineKeyboardButton(
                text=get_localization(language_code).ACTION_BACK,
                callback_data="catalog_manage_edit:back",
            )
        ],
    ]

    return InlineKeyboardMarkup(inline_keyboard=buttons)
