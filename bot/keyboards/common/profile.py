from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup

from bot.database.models.user import UserGender
from bot.locales.main import get_localization
from bot.locales.types import LanguageCode


def build_profile_keyboard(
    language_code: LanguageCode,
    is_photo_uploaded: bool,
    has_active_subscription: bool,
    has_canceled_subscription: bool,
) -> InlineKeyboardMarkup:
    buttons = [
        [
            InlineKeyboardButton(
                text=get_localization(language_code).OPEN_SETTINGS,
                callback_data="profile:open_settings",
            ),
        ],
        [
            InlineKeyboardButton(
                text=get_localization(language_code).PROFILE_SHOW_QUOTA,
                callback_data="profile:show_quota",
            ),
        ],
        [
            InlineKeyboardButton(
                text=get_localization(language_code).PROFILE_CHANGE_PHOTO
                if is_photo_uploaded
                else get_localization(language_code).PROFILE_UPLOAD_PHOTO,
                callback_data="profile:change_photo",
            ),
        ],
        [
            InlineKeyboardButton(
                text=get_localization(language_code).OPEN_BONUS_INFO,
                callback_data="profile:open_bonus_info",
            ),
        ],
        [
            InlineKeyboardButton(
                text=get_localization(language_code).OPEN_BUY_SUBSCRIPTIONS_INFO,
                callback_data="profile:open_buy_subscriptions_info",
            ),
        ],
        [
            InlineKeyboardButton(
                text=get_localization(language_code).OPEN_BUY_PACKAGES_INFO,
                callback_data="profile:open_buy_packages_info",
            ),
        ],
    ]

    if has_active_subscription:
        buttons.append(
            [
                InlineKeyboardButton(
                    text=get_localization(language_code).PROFILE_CANCEL_SUBSCRIPTION,
                    callback_data="profile:cancel_subscription",
                )
            ]
        )
    elif has_canceled_subscription:
        buttons.append(
            [
                InlineKeyboardButton(
                    text=get_localization(language_code).PROFILE_RENEW_SUBSCRIPTION,
                    callback_data="profile:renew_subscription",
                )
            ]
        )

    return InlineKeyboardMarkup(inline_keyboard=buttons)


def build_profile_quota_keyboard(language_code: LanguageCode):
    buttons = [
        [
            InlineKeyboardButton(
                text=get_localization(language_code).OPEN_BONUS_INFO,
                callback_data="profile:open_bonus_info",
            ),
        ],
        [
            InlineKeyboardButton(
                text=get_localization(language_code).OPEN_BUY_SUBSCRIPTIONS_INFO,
                callback_data="profile:open_buy_subscriptions_info",
            ),
        ],
        [
            InlineKeyboardButton(
                text=get_localization(language_code).OPEN_BUY_PACKAGES_INFO,
                callback_data="profile:open_buy_packages_info",
            ),
        ],
    ]

    return InlineKeyboardMarkup(inline_keyboard=buttons)


def build_profile_gender_keyboard(language_code: LanguageCode) -> InlineKeyboardMarkup:
    buttons = [
        [
            InlineKeyboardButton(
                text=get_localization(language_code).GENDER_MALE,
                callback_data=f"profile_gender:{UserGender.MALE}",
            )
        ],
        [
            InlineKeyboardButton(
                text=get_localization(language_code).GENDER_FEMALE,
                callback_data=f"profile_gender:{UserGender.FEMALE}",
            )
        ],
    ]

    return InlineKeyboardMarkup(inline_keyboard=buttons)
