from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup

from bot.database.models.face_swap_package import FaceSwapPackage, FaceSwapPackageStatus
from bot.database.models.user import UserGender
from bot.locales.main import get_localization
from bot.locales.types import LanguageCode


def build_manage_face_swap_keyboard(
    language_code: LanguageCode,
) -> InlineKeyboardMarkup:
    buttons = [
        [
            InlineKeyboardButton(
                text=get_localization(language_code).ADMIN_FACE_SWAP_CREATE_PACKAGE,
                callback_data="fsm:create",
            )
        ],
        [
            InlineKeyboardButton(
                text=get_localization(language_code).ADMIN_FACE_SWAP_EDIT_PACKAGE,
                callback_data="fsm:edit",
            )
        ],
        [
            InlineKeyboardButton(
                text=get_localization(language_code).ACTION_BACK,
                callback_data="fsm:back",
            )
        ],
    ]

    return InlineKeyboardMarkup(inline_keyboard=buttons)


def build_manage_face_swap_create_keyboard(
    language_code: LanguageCode,
) -> InlineKeyboardMarkup:
    buttons = [
        [
            InlineKeyboardButton(
                text=get_localization(language_code).ACTION_BACK,
                callback_data="fsm_create:back",
            )
        ],
        [
            InlineKeyboardButton(
                text=get_localization(language_code).ACTION_CANCEL,
                callback_data="fsm_create:cancel",
            )
        ],
    ]

    return InlineKeyboardMarkup(inline_keyboard=buttons)


def build_manage_face_swap_create_confirmation_keyboard(
    language_code: LanguageCode,
) -> InlineKeyboardMarkup:
    buttons = [
        [
            InlineKeyboardButton(
                text=get_localization(language_code).ACTION_APPROVE,
                callback_data="fsm_create_confirmation:approve",
            )
        ],
        [
            InlineKeyboardButton(
                text=get_localization(language_code).ACTION_CANCEL,
                callback_data="fsm_create_confirmation:cancel",
            )
        ],
    ]

    return InlineKeyboardMarkup(inline_keyboard=buttons)


def build_manage_face_swap_edit_choose_gender_keyboard(
    language_code: LanguageCode,
) -> InlineKeyboardMarkup:
    buttons = [
        [
            InlineKeyboardButton(
                text=get_localization(language_code).GENDER_MALE,
                callback_data=f"fsm_edit_choose_gender:{UserGender.MALE}",
            )
        ],
        [
            InlineKeyboardButton(
                text=get_localization(language_code).GENDER_FEMALE,
                callback_data=f"fsm_edit_choose_gender:{UserGender.FEMALE}",
            )
        ],
    ]

    return InlineKeyboardMarkup(inline_keyboard=buttons)


def build_manage_face_swap_edit_choose_package_keyboard(
    language_code: LanguageCode,
    packages: list[FaceSwapPackage],
) -> InlineKeyboardMarkup:
    buttons = []
    for package in packages:
        buttons.append(
            [
                InlineKeyboardButton(
                    text=f"{package.name} ({package.translated_names.get(language_code, package.name)})",
                    callback_data=f"fsm_edit_choose_package:{package.name}",
                )
            ]
        )

    return InlineKeyboardMarkup(inline_keyboard=buttons)


def build_manage_face_swap_edit_keyboard(
    language_code: LanguageCode,
) -> InlineKeyboardMarkup:
    buttons = [
        [
            InlineKeyboardButton(
                text=get_localization(language_code).ADMIN_FACE_SWAP_CHANGE_STATUS,
                callback_data="fsm_edit:change_status",
            )
        ],
        [
            InlineKeyboardButton(
                text=get_localization(language_code).ADMIN_FACE_SWAP_SHOW_PICTURES,
                callback_data="fsm_edit:show_pictures",
            )
        ],
        [
            InlineKeyboardButton(
                text=get_localization(language_code).ADMIN_FACE_SWAP_ADD_NEW_PICTURE,
                callback_data="fsm_edit:add_new_picture",
            )
        ],
        [
            InlineKeyboardButton(
                text=get_localization(language_code).ACTION_BACK,
                callback_data="fsm_edit:back",
            )
        ],
        [
            InlineKeyboardButton(
                text=get_localization(language_code).ACTION_CANCEL,
                callback_data="fsm_edit:cancel",
            )
        ],
    ]

    return InlineKeyboardMarkup(inline_keyboard=buttons)


def build_manage_face_swap_edit_package_change_status_keyboard(
    language_code: LanguageCode,
    current_status: FaceSwapPackageStatus,
) -> InlineKeyboardMarkup:
    buttons = [
        [
            InlineKeyboardButton(
                text=get_localization(language_code).ADMIN_FACE_SWAP_PUBLIC
                + (" ✅" if current_status == FaceSwapPackageStatus.PUBLIC else ""),
                callback_data=f"fsm_edit_package_change_status:{FaceSwapPackageStatus.PUBLIC}",
            )
        ],
        [
            InlineKeyboardButton(
                text=get_localization(language_code).ADMIN_FACE_SWAP_PRIVATE
                + (" ✅" if current_status == FaceSwapPackageStatus.PRIVATE else ""),
                callback_data=f"fsm_edit_package_change_status:{FaceSwapPackageStatus.PRIVATE}",
            )
        ],
        [
            InlineKeyboardButton(
                text=get_localization(language_code).ACTION_BACK,
                callback_data="fsm_edit_package_change_status:back",
            )
        ],
    ]

    return InlineKeyboardMarkup(inline_keyboard=buttons)


def build_manage_face_swap_edit_picture_keyboard(
    language_code: LanguageCode, file_name: str
) -> InlineKeyboardMarkup:
    buttons = [
        [
            InlineKeyboardButton(
                text=get_localization(language_code).ADMIN_FACE_SWAP_CHANGE_STATUS,
                callback_data=f"fsm_edit_picture:change_status:{file_name}",
            )
        ],
        [
            InlineKeyboardButton(
                text=get_localization(language_code).ADMIN_FACE_SWAP_EXAMPLE_PICTURE,
                callback_data=f"fsm_edit_picture:example_picture:{file_name}",
            )
        ],
    ]

    return InlineKeyboardMarkup(inline_keyboard=buttons)


def build_manage_face_swap_edit_picture_change_status_keyboard(
    language_code: LanguageCode,
    current_status: FaceSwapPackageStatus,
) -> InlineKeyboardMarkup:
    buttons = [
        [
            InlineKeyboardButton(
                text=get_localization(language_code).ADMIN_FACE_SWAP_PUBLIC
                + (" ✅" if current_status == FaceSwapPackageStatus.PUBLIC else ""),
                callback_data=f"fsm_edit_picture_change_status:{FaceSwapPackageStatus.PUBLIC}",
            )
        ],
        [
            InlineKeyboardButton(
                text=get_localization(language_code).ADMIN_FACE_SWAP_PRIVATE
                + (" ✅" if current_status == FaceSwapPackageStatus.PRIVATE else ""),
                callback_data=f"fsm_edit_picture_change_status:{FaceSwapPackageStatus.PRIVATE}",
            )
        ],
        [
            InlineKeyboardButton(
                text=get_localization(language_code).ACTION_BACK,
                callback_data="fsm_edit_picture_change_status:back",
            )
        ],
    ]

    return InlineKeyboardMarkup(inline_keyboard=buttons)
