from typing import Optional

from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

from bot.database.models.common import (
    Model,
    SendType,
    AspectRatio,
    VideoSummaryFocus,
    VideoSummaryFormat,
    VideoSummaryAmount,
    DALLEResolution,
    DALLEQuality,
    MidjourneyVersion,
    FluxSafetyTolerance,
    SunoVersion,
    KlingVersion,
    KlingDuration,
    KlingMode,
    RunwayResolution,
    RunwayDuration,
    LumaRayQuality,
    LumaRayDuration,
)
from bot.database.models.user import UserSettings, UserGender
from bot.locales.main import get_localization
from bot.locales.types import LanguageCode


def build_settings_choose_model_type_keyboard(language_code: LanguageCode) -> InlineKeyboardMarkup:
    buttons = [
        [
            InlineKeyboardButton(
                text=get_localization(language_code).MODELS_TEXT,
                callback_data=f'settings_choose_model_type:text_models'
            ),
        ],
        [
            InlineKeyboardButton(
                text=get_localization(language_code).MODELS_IMAGE,
                callback_data=f'settings_choose_model_type:image_models'
            ),
        ],
        [
            InlineKeyboardButton(
                text=get_localization(language_code).MODELS_MUSIC,
                callback_data=f'settings_choose_model_type:music_models'
            ),
        ],
        [
            InlineKeyboardButton(
                text=get_localization(language_code).MODELS_VIDEO,
                callback_data=f'settings_choose_model_type:video_models'
            ),
        ],
        [
            InlineKeyboardButton(
                text=get_localization(language_code).ACTION_CLOSE,
                callback_data='settings_choose_model:close'
            ),
        ],
    ]

    return InlineKeyboardMarkup(inline_keyboard=buttons)


def build_settings_choose_text_model_keyboard(language_code: LanguageCode) -> InlineKeyboardMarkup:
    buttons = [
        [
            InlineKeyboardButton(
                text=get_localization(language_code).CHAT_GPT,
                callback_data=f'settings_choose_text_model:{Model.CHAT_GPT}'
            ),
            InlineKeyboardButton(
                text=get_localization(language_code).CLAUDE,
                callback_data=f'settings_choose_text_model:{Model.CLAUDE}'
            ),
        ],
        [
            InlineKeyboardButton(
                text=get_localization(language_code).GEMINI,
                callback_data=f'settings_choose_text_model:{Model.GEMINI}'
            ),
            InlineKeyboardButton(
                text=get_localization(language_code).DEEP_SEEK,
                callback_data=f'settings_choose_text_model:{Model.DEEP_SEEK}'
            ),
        ],
        [
            InlineKeyboardButton(
                text=get_localization(language_code).GROK,
                callback_data=f'settings_choose_text_model:{Model.GROK}'
            ),
            InlineKeyboardButton(
                text=get_localization(language_code).PERPLEXITY,
                callback_data=f'settings_choose_text_model:{Model.PERPLEXITY}'
            ),
        ],
        [
            InlineKeyboardButton(
                text=get_localization(language_code).ACTION_TO_OTHER_TYPE_MODELS,
                callback_data='settings_choose_text_model:back'
            ),
        ],
    ]

    return InlineKeyboardMarkup(inline_keyboard=buttons)


def build_settings_choose_summary_model_keyboard(language_code: LanguageCode) -> InlineKeyboardMarkup:
    buttons = [
        [
            InlineKeyboardButton(
                text=get_localization(language_code).EIGHTIFY,
                callback_data=f'settings_choose_summary_model:{Model.EIGHTIFY}'
            ),
            InlineKeyboardButton(
                text=get_localization(language_code).GEMINI_VIDEO,
                callback_data=f'settings_choose_summary_model:{Model.GEMINI_VIDEO}'
            ),
        ],
        [
            InlineKeyboardButton(
                text=get_localization(language_code).ACTION_TO_OTHER_TYPE_MODELS,
                callback_data='settings_choose_summary_model:back'
            ),
        ],
    ]

    return InlineKeyboardMarkup(inline_keyboard=buttons)


def build_settings_choose_image_model_keyboard(language_code: LanguageCode) -> InlineKeyboardMarkup:
    buttons = [
        [
            InlineKeyboardButton(
                text=get_localization(language_code).DALL_E,
                callback_data=f'settings_choose_image_model:{Model.DALL_E}'
            ),
            InlineKeyboardButton(
                text=get_localization(language_code).MIDJOURNEY,
                callback_data=f'settings_choose_image_model:{Model.MIDJOURNEY}'
            ),
        ],
        [
            InlineKeyboardButton(
                text=get_localization(language_code).STABLE_DIFFUSION,
                callback_data=f'settings_choose_image_model:{Model.STABLE_DIFFUSION}'
            ),
            InlineKeyboardButton(
                text=get_localization(language_code).FLUX,
                callback_data=f'settings_choose_image_model:{Model.FLUX}'
            ),
        ],
        [
            InlineKeyboardButton(
                text=get_localization(language_code).LUMA_PHOTON,
                callback_data=f'settings_choose_image_model:{Model.LUMA_PHOTON}'
            ),
            InlineKeyboardButton(
                text=get_localization(language_code).RECRAFT,
                callback_data=f'settings_choose_image_model:{Model.RECRAFT}'
            ),
        ],
        [
            InlineKeyboardButton(
                text=get_localization(language_code).FACE_SWAP,
                callback_data=f'settings_choose_image_model:{Model.FACE_SWAP}'
            ),
            InlineKeyboardButton(
                text=get_localization(language_code).PHOTOSHOP_AI,
                callback_data=f'settings_choose_image_model:{Model.PHOTOSHOP_AI}'
            ),
        ],
        [
            InlineKeyboardButton(
                text=get_localization(language_code).ACTION_TO_OTHER_TYPE_MODELS,
                callback_data='settings_choose_image_model:back'
            ),
        ],
    ]

    return InlineKeyboardMarkup(inline_keyboard=buttons)


def build_settings_choose_music_model_keyboard(language_code: LanguageCode) -> InlineKeyboardMarkup:
    buttons = [
        [
            InlineKeyboardButton(
                text=get_localization(language_code).MUSIC_GEN,
                callback_data=f'settings_choose_music_model:{Model.MUSIC_GEN}'
            ),
            InlineKeyboardButton(
                text=get_localization(language_code).SUNO,
                callback_data=f'settings_choose_music_model:{Model.SUNO}'
            ),
        ],
        [
            InlineKeyboardButton(
                text=get_localization(language_code).ACTION_TO_OTHER_TYPE_MODELS,
                callback_data='settings_choose_music_model:back'
            ),
        ],
    ]

    return InlineKeyboardMarkup(inline_keyboard=buttons)


def build_settings_choose_video_model_keyboard(language_code: LanguageCode) -> InlineKeyboardMarkup:
    buttons = [
        [
            InlineKeyboardButton(
                text=get_localization(language_code).KLING,
                callback_data=f'settings_choose_video_model:{Model.KLING}'
            ),
            InlineKeyboardButton(
                text=get_localization(language_code).RUNWAY,
                callback_data=f'settings_choose_video_model:{Model.RUNWAY}'
            ),
        ],
        [
            InlineKeyboardButton(
                text=get_localization(language_code).LUMA_RAY,
                callback_data=f'settings_choose_video_model:{Model.LUMA_RAY}'
            ),
            InlineKeyboardButton(
                text=get_localization(language_code).PIKA,
                callback_data=f'settings_choose_video_model:{Model.PIKA}'
            ),
        ],
        [
            InlineKeyboardButton(
                text=get_localization(language_code).ACTION_TO_OTHER_TYPE_MODELS,
                callback_data='settings_choose_video_model:back'
            ),
        ],
    ]

    return InlineKeyboardMarkup(inline_keyboard=buttons)


def build_settings_keyboard(
    language_code: LanguageCode,
    model: Model,
    model_type: str,
    settings: dict,
) -> InlineKeyboardMarkup:
    buttons = []
    if (
        model == Model.CHAT_GPT or
        model == Model.CLAUDE or
        model == Model.GEMINI or
        model == Model.GROK or
        model == Model.DEEP_SEEK or
        model == Model.PERPLEXITY
    ):
        buttons = [
            [
                InlineKeyboardButton(
                    text=get_localization(language_code).SETTINGS_SHOW_USAGE_QUOTA_IN_MESSAGES + (
                        ' ✅' if settings[model][UserSettings.SHOW_USAGE_QUOTA] else ' ❌'
                    ),
                    callback_data=f'setting:{UserSettings.SHOW_USAGE_QUOTA}:{model}'
                ),
            ],
            [
                InlineKeyboardButton(
                    text=get_localization(language_code).SETTINGS_SHOW_THE_NAME_OF_THE_CHATS + (
                        ' ✅' if settings[model][UserSettings.SHOW_THE_NAME_OF_THE_CHATS] else ' ❌'
                    ),
                    callback_data=f'setting:{UserSettings.SHOW_THE_NAME_OF_THE_CHATS}:{model}'
                ),
            ],
            [
                InlineKeyboardButton(
                    text=get_localization(language_code).SETTINGS_SHOW_THE_NAME_OF_THE_ROLES + (
                        ' ✅' if settings[model][UserSettings.SHOW_THE_NAME_OF_THE_ROLES] else ' ❌'
                    ),
                    callback_data=f'setting:{UserSettings.SHOW_THE_NAME_OF_THE_ROLES}:{model}'
                ),
            ],
            [
                InlineKeyboardButton(
                    text=get_localization(language_code).VOICE_MESSAGES,
                    callback_data=f'setting:voice_messages:{model}'
                ),
            ],
            [
                InlineKeyboardButton(
                    text=get_localization(language_code).CHAT_MANAGE,
                    callback_data=f'setting:manage_chats:{model}'
                ),
            ],
            [
                InlineKeyboardButton(
                    text=get_localization(language_code).CATALOG_MANAGE,
                    callback_data=f'setting:manage_catalog:{model}'
                ),
            ],
        ]
    elif model == Model.EIGHTIFY or model == Model.GEMINI_VIDEO:
        buttons = [
            [
                InlineKeyboardButton(
                    text=get_localization(language_code).SETTINGS_SHOW_USAGE_QUOTA_IN_MESSAGES + (
                        ' ✅' if settings[model][UserSettings.SHOW_USAGE_QUOTA] else ' ❌'
                    ),
                    callback_data=f'setting:{UserSettings.SHOW_USAGE_QUOTA}:{model}'
                ),
            ],
            [
                InlineKeyboardButton(
                    text=get_localization(language_code).SETTINGS_FOCUS.upper(),
                    callback_data=f'setting:nothing:{model}'
                ),
            ],
            [
                InlineKeyboardButton(
                    text=get_localization(language_code).VIDEO_SUMMARY_FOCUS_INSIGHTFUL + (
                        ' ✅' if settings[model][UserSettings.FOCUS] == VideoSummaryFocus.INSIGHTFUL else ''
                    ),
                    callback_data=f'setting:{VideoSummaryFocus.INSIGHTFUL}:{model}'
                ),
                InlineKeyboardButton(
                    text=get_localization(language_code).VIDEO_SUMMARY_FOCUS_FUNNY + (
                        ' ✅' if settings[model][UserSettings.FOCUS] == VideoSummaryFocus.FUNNY else ''
                    ),
                    callback_data=f'setting:{VideoSummaryFocus.FUNNY}:{model}'
                ),
            ],
            [
                InlineKeyboardButton(
                    text=get_localization(language_code).VIDEO_SUMMARY_FOCUS_ACTIONABLE + (
                        ' ✅' if settings[model][UserSettings.FOCUS] == VideoSummaryFocus.ACTIONABLE else ''
                    ),
                    callback_data=f'setting:{VideoSummaryFocus.ACTIONABLE}:{model}'
                ),
                InlineKeyboardButton(
                    text=get_localization(language_code).VIDEO_SUMMARY_FOCUS_CONTROVERSIAL + (
                        ' ✅' if settings[model][UserSettings.FOCUS] == VideoSummaryFocus.CONTROVERSIAL else ''
                    ),
                    callback_data=f'setting:{VideoSummaryFocus.CONTROVERSIAL}:{model}'
                ),
            ],
            [
                InlineKeyboardButton(
                    text=get_localization(language_code).SETTINGS_FORMAT.upper(),
                    callback_data=f'setting:nothing:{model}'
                ),
            ],
            [
                InlineKeyboardButton(
                    text=get_localization(language_code).VIDEO_SUMMARY_FORMAT_LIST + (
                        ' ✅' if settings[model][UserSettings.FORMAT] == VideoSummaryFormat.LIST else ''
                    ),
                    callback_data=f'setting:{VideoSummaryFormat.LIST}:{model}'
                ),
                InlineKeyboardButton(
                    text=get_localization(language_code).VIDEO_SUMMARY_FORMAT_FAQ + (
                        ' ✅' if settings[model][UserSettings.FORMAT] == VideoSummaryFormat.FAQ else ''
                    ),
                    callback_data=f'setting:{VideoSummaryFormat.FAQ}:{model}'
                ),
            ],
            [
                InlineKeyboardButton(
                    text=get_localization(language_code).SETTINGS_AMOUNT.upper(),
                    callback_data=f'setting:nothing:{model}'
                ),
            ],
            [
                InlineKeyboardButton(
                    text=get_localization(language_code).VIDEO_SUMMARY_AMOUNT_SHORT + (
                        ' ✅' if settings[model][UserSettings.AMOUNT] == VideoSummaryAmount.SHORT else ''
                    ),
                    callback_data=f'setting:{VideoSummaryAmount.SHORT}:{model}'
                ),
                InlineKeyboardButton(
                    text=get_localization(language_code).VIDEO_SUMMARY_AMOUNT_AUTO + (
                        ' ✅' if settings[model][UserSettings.AMOUNT] == VideoSummaryAmount.AUTO else ''
                    ),
                    callback_data=f'setting:{VideoSummaryAmount.AUTO}:{model}'
                ),
                InlineKeyboardButton(
                    text=get_localization(language_code).VIDEO_SUMMARY_AMOUNT_DETAILED + (
                        ' ✅' if settings[model][UserSettings.AMOUNT] == VideoSummaryAmount.DETAILED else ''
                    ),
                    callback_data=f'setting:{VideoSummaryAmount.DETAILED}:{model}'
                ),
            ],
            [
                InlineKeyboardButton(
                    text=get_localization(language_code).VOICE_MESSAGES,
                    callback_data=f'setting:voice_messages:{model}'
                ),
            ],
        ]
    elif model == Model.DALL_E:
        buttons = [
            [
                InlineKeyboardButton(
                    text=get_localization(language_code).SETTINGS_SHOW_USAGE_QUOTA_IN_MESSAGES + (
                        ' ✅' if settings[model][UserSettings.SHOW_USAGE_QUOTA] else ' ❌'
                    ),
                    callback_data=f'setting:{UserSettings.SHOW_USAGE_QUOTA}:{model}'
                ),
            ],
            [
                InlineKeyboardButton(
                    text=get_localization(language_code).SETTINGS_SEND_TYPE.upper(),
                    callback_data=f'setting:nothing:{model}'
                ),
            ],
            [
                InlineKeyboardButton(
                    text=get_localization(language_code).SETTINGS_SEND_TYPE_IMAGE + (
                        ' ✅' if settings[model][UserSettings.SEND_TYPE] == SendType.IMAGE else ''
                    ),
                    callback_data=f'setting:{SendType.IMAGE}:{model}'
                ),
                InlineKeyboardButton(
                    text=get_localization(language_code).SETTINGS_SEND_TYPE_DOCUMENT + (
                        ' ✅' if settings[model][UserSettings.SEND_TYPE] == SendType.DOCUMENT else ''
                    ),
                    callback_data=f'setting:{SendType.DOCUMENT}:{model}'
                ),
            ],
            [
                InlineKeyboardButton(
                    text=get_localization(language_code).SETTINGS_ASPECT_RATIO.upper(),
                    callback_data=f'setting:nothing:{model}'
                ),
            ],
            [
                InlineKeyboardButton(
                    text=AspectRatio.SQUARE + (
                        ' ✅' if settings[model][UserSettings.RESOLUTION] == DALLEResolution.LOW else ''
                    ),
                    callback_data=f'setting:{DALLEResolution.LOW}:{model}'
                ),
                InlineKeyboardButton(
                    text=AspectRatio.PORTRAIT + (
                        ' ✅' if settings[model][UserSettings.RESOLUTION] == DALLEResolution.MEDIUM else ''
                    ),
                    callback_data=f'setting:{DALLEResolution.MEDIUM}:{model}'
                ),
                InlineKeyboardButton(
                    text=AspectRatio.LANDSCAPE + (
                        ' ✅' if settings[model][UserSettings.RESOLUTION] == DALLEResolution.HIGH else ''
                    ),
                    callback_data=f'setting:{DALLEResolution.HIGH}:{model}'
                ),
            ],
            [
                InlineKeyboardButton(
                    text=get_localization(language_code).SETTINGS_QUALITY.upper(),
                    callback_data=f'setting:nothing:{model}'
                ),
            ],
            [
                InlineKeyboardButton(
                    text=DALLEQuality.STANDARD + (
                        ' ✅' if settings[model][UserSettings.QUALITY] == DALLEQuality.STANDARD else ''
                    ),
                    callback_data=f'setting:{DALLEQuality.STANDARD}:{model}'
                ),
                InlineKeyboardButton(
                    text=DALLEQuality.HD + (
                        ' ✅' if settings[model][UserSettings.QUALITY] == DALLEQuality.HD else ''
                    ),
                    callback_data=f'setting:{DALLEQuality.HD}:{model}'
                ),
            ],
        ]
    elif model == Model.MIDJOURNEY:
        buttons = [
            [
                InlineKeyboardButton(
                    text=get_localization(language_code).SETTINGS_SHOW_USAGE_QUOTA_IN_MESSAGES + (
                        ' ✅' if settings[model][UserSettings.SHOW_USAGE_QUOTA] else ' ❌'
                    ),
                    callback_data=f'setting:{UserSettings.SHOW_USAGE_QUOTA}:{model}'
                ),
            ],
            [
                InlineKeyboardButton(
                    text=get_localization(language_code).SETTINGS_SEND_TYPE.upper(),
                    callback_data=f'setting:nothing:{model}'
                ),
            ],
            [
                InlineKeyboardButton(
                    text=get_localization(language_code).SETTINGS_SEND_TYPE_IMAGE + (
                        ' ✅' if settings[model][UserSettings.SEND_TYPE] == SendType.IMAGE else ''
                    ),
                    callback_data=f'setting:{SendType.IMAGE}:{model}'
                ),
                InlineKeyboardButton(
                    text=get_localization(language_code).SETTINGS_SEND_TYPE_DOCUMENT + (
                        ' ✅' if settings[model][UserSettings.SEND_TYPE] == SendType.DOCUMENT else ''
                    ),
                    callback_data=f'setting:{SendType.DOCUMENT}:{model}'
                ),
            ],
            [
                InlineKeyboardButton(
                    text=get_localization(language_code).SETTINGS_ASPECT_RATIO.upper(),
                    callback_data=f'setting:nothing:{model}'
                ),
            ],
            [
                InlineKeyboardButton(
                    text=AspectRatio.SQUARE + (
                        ' ✅' if settings[model][UserSettings.ASPECT_RATIO] == AspectRatio.SQUARE else ''
                    ),
                    callback_data=f'setting:SQUARE:{model}'
                ),
                InlineKeyboardButton(
                    text=AspectRatio.LANDSCAPE + (
                        ' ✅' if settings[model][UserSettings.ASPECT_RATIO] == AspectRatio.LANDSCAPE else ''
                    ),
                    callback_data=f'setting:LANDSCAPE:{model}'
                ),
                InlineKeyboardButton(
                    text=AspectRatio.PORTRAIT + (
                        ' ✅' if settings[model][UserSettings.ASPECT_RATIO] == AspectRatio.PORTRAIT else ''
                    ),
                    callback_data=f'setting:PORTRAIT:{model}'
                ),
            ],
            [
                InlineKeyboardButton(
                    text=AspectRatio.CINEMASCOPE_HORIZONTAL + (
                        ' ✅' if settings[model][UserSettings.ASPECT_RATIO] == AspectRatio.CINEMASCOPE_HORIZONTAL else ''
                    ),
                    callback_data=f'setting:CINEMASCOPE_HORIZONTAL:{model}'
                ),
                InlineKeyboardButton(
                    text=AspectRatio.CINEMASCOPE_VERTICAL + (
                        ' ✅' if settings[model][UserSettings.ASPECT_RATIO] == AspectRatio.CINEMASCOPE_VERTICAL else ''
                    ),
                    callback_data=f'setting:CINEMASCOPE_VERTICAL:{model}'
                ),
                InlineKeyboardButton(
                    text=AspectRatio.STANDARD_HORIZONTAL + (
                        ' ✅' if settings[model][UserSettings.ASPECT_RATIO] == AspectRatio.STANDARD_HORIZONTAL else ''
                    ),
                    callback_data=f'setting:STANDARD_HORIZONTAL:{model}'
                ),
                InlineKeyboardButton(
                    text=AspectRatio.STANDARD_VERTICAL + (
                        ' ✅' if settings[model][UserSettings.ASPECT_RATIO] == AspectRatio.STANDARD_VERTICAL else ''
                    ),
                    callback_data=f'setting:STANDARD_VERTICAL:{model}'
                ),
            ],
            [
                InlineKeyboardButton(
                    text=AspectRatio.BANNER_HORIZONTAL + (
                        ' ✅' if settings[model][UserSettings.ASPECT_RATIO] == AspectRatio.BANNER_HORIZONTAL else ''
                    ),
                    callback_data=f'setting:BANNER_HORIZONTAL:{model}'
                ),
                InlineKeyboardButton(
                    text=AspectRatio.BANNER_VERTICAL + (
                        ' ✅' if settings[model][UserSettings.ASPECT_RATIO] == AspectRatio.BANNER_VERTICAL else ''
                    ),
                    callback_data=f'setting:BANNER_VERTICAL:{model}'
                ),
                InlineKeyboardButton(
                    text=AspectRatio.CLASSIC_HORIZONTAL + (
                        ' ✅' if settings[model][UserSettings.ASPECT_RATIO] == AspectRatio.CLASSIC_HORIZONTAL else ''
                    ),
                    callback_data=f'setting:CLASSIC_HORIZONTAL:{model}'
                ),
                InlineKeyboardButton(
                    text=AspectRatio.CLASSIC_VERTICAL + (
                        ' ✅' if settings[model][UserSettings.ASPECT_RATIO] == AspectRatio.CLASSIC_VERTICAL else ''
                    ),
                    callback_data=f'setting:CLASSIC_VERTICAL:{model}'
                ),
            ],
            [
                InlineKeyboardButton(
                    text=get_localization(language_code).SETTINGS_VERSION.upper(),
                    callback_data=f'setting:nothing:{model}'
                ),
            ],
            [
                InlineKeyboardButton(
                    text=MidjourneyVersion.V5 + (
                        ' ✅' if settings[model][UserSettings.VERSION] == MidjourneyVersion.V5 else ''
                    ),
                    callback_data=f'setting:{MidjourneyVersion.V5}:{model}'
                ),
                InlineKeyboardButton(
                    text=MidjourneyVersion.V6 + (
                        ' ✅' if settings[model][UserSettings.VERSION] == MidjourneyVersion.V6 else ''
                    ),
                    callback_data=f'setting:{MidjourneyVersion.V6}:{model}'
                ),
                InlineKeyboardButton(
                    text=MidjourneyVersion.V7 + (
                        ' ✅' if settings[model][UserSettings.VERSION] == MidjourneyVersion.V7 else ''
                    ),
                    callback_data=f'setting:{MidjourneyVersion.V7}:{model}'
                ),
            ],
        ]
    elif model == Model.STABLE_DIFFUSION:
        buttons = [
            [
                InlineKeyboardButton(
                    text=get_localization(language_code).SETTINGS_SHOW_USAGE_QUOTA_IN_MESSAGES + (
                        ' ✅' if settings[model][UserSettings.SHOW_USAGE_QUOTA] else ' ❌'),
                    callback_data=f'setting:{UserSettings.SHOW_USAGE_QUOTA}:{model}'
                ),
            ],
            [
                InlineKeyboardButton(
                    text=get_localization(language_code).SETTINGS_SEND_TYPE.upper(),
                    callback_data=f'setting:nothing:{model}'
                ),
            ],
            [
                InlineKeyboardButton(
                    text=get_localization(language_code).SETTINGS_SEND_TYPE_IMAGE + (
                        ' ✅' if settings[model][UserSettings.SEND_TYPE] == SendType.IMAGE else ''
                    ),
                    callback_data=f'setting:{SendType.IMAGE}:{model}'
                ),
                InlineKeyboardButton(
                    text=get_localization(language_code).SETTINGS_SEND_TYPE_DOCUMENT + (
                        ' ✅' if settings[model][UserSettings.SEND_TYPE] == SendType.DOCUMENT else ''
                    ),
                    callback_data=f'setting:{SendType.DOCUMENT}:{model}'
                ),
            ],
            [
                InlineKeyboardButton(
                    text=get_localization(language_code).SETTINGS_ASPECT_RATIO.upper(),
                    callback_data=f'setting:nothing:{model}'
                ),
            ],
            [
                InlineKeyboardButton(
                    text=AspectRatio.SQUARE + (
                        ' ✅' if settings[model][UserSettings.ASPECT_RATIO] == AspectRatio.SQUARE else ''
                    ),
                    callback_data=f'setting:SQUARE:{model}'
                ),
                InlineKeyboardButton(
                    text=AspectRatio.LANDSCAPE + (
                        ' ✅' if settings[model][UserSettings.ASPECT_RATIO] == AspectRatio.LANDSCAPE else ''
                    ),
                    callback_data=f'setting:LANDSCAPE:{model}'
                ),
                InlineKeyboardButton(
                    text=AspectRatio.PORTRAIT + (
                        ' ✅' if settings[model][UserSettings.ASPECT_RATIO] == AspectRatio.PORTRAIT else ''
                    ),
                    callback_data=f'setting:PORTRAIT:{model}'
                ),
            ],
            [
                InlineKeyboardButton(
                    text=AspectRatio.CINEMASCOPE_HORIZONTAL + (
                        ' ✅' if settings[model][UserSettings.ASPECT_RATIO] == AspectRatio.CINEMASCOPE_HORIZONTAL else ''
                    ),
                    callback_data=f'setting:CINEMASCOPE_HORIZONTAL:{model}'
                ),
                InlineKeyboardButton(
                    text=AspectRatio.CINEMASCOPE_VERTICAL + (
                        ' ✅' if settings[model][UserSettings.ASPECT_RATIO] == AspectRatio.CINEMASCOPE_VERTICAL else ''
                    ),
                    callback_data=f'setting:CINEMASCOPE_VERTICAL:{model}'
                ),
                InlineKeyboardButton(
                    text=AspectRatio.STANDARD_HORIZONTAL + (
                        ' ✅' if settings[model][UserSettings.ASPECT_RATIO] == AspectRatio.STANDARD_HORIZONTAL else ''
                    ),
                    callback_data=f'setting:STANDARD_HORIZONTAL:{model}'
                ),
                InlineKeyboardButton(
                    text=AspectRatio.STANDARD_VERTICAL + (
                        ' ✅' if settings[model][UserSettings.ASPECT_RATIO] == AspectRatio.STANDARD_VERTICAL else ''
                    ),
                    callback_data=f'setting:STANDARD_VERTICAL:{model}'
                ),
            ],
            [
                InlineKeyboardButton(
                    text=AspectRatio.BANNER_HORIZONTAL + (
                        ' ✅' if settings[model][UserSettings.ASPECT_RATIO] == AspectRatio.BANNER_HORIZONTAL else ''
                    ),
                    callback_data=f'setting:BANNER_HORIZONTAL:{model}'
                ),
                InlineKeyboardButton(
                    text=AspectRatio.BANNER_VERTICAL + (
                        ' ✅' if settings[model][UserSettings.ASPECT_RATIO] == AspectRatio.BANNER_VERTICAL else ''
                    ),
                    callback_data=f'setting:BANNER_VERTICAL:{model}'
                ),
                InlineKeyboardButton(
                    text=AspectRatio.CLASSIC_HORIZONTAL + (
                        ' ✅' if settings[model][UserSettings.ASPECT_RATIO] == AspectRatio.CLASSIC_HORIZONTAL else ''
                    ),
                    callback_data=f'setting:CLASSIC_HORIZONTAL:{model}'
                ),
                InlineKeyboardButton(
                    text=AspectRatio.CLASSIC_VERTICAL + (
                        ' ✅' if settings[model][UserSettings.ASPECT_RATIO] == AspectRatio.CLASSIC_VERTICAL else ''
                    ),
                    callback_data=f'setting:CLASSIC_VERTICAL:{model}'
                ),
            ],
        ]
    elif model == Model.FLUX:
        buttons = [
            [
                InlineKeyboardButton(
                    text=get_localization(language_code).SETTINGS_SHOW_USAGE_QUOTA_IN_MESSAGES + (
                        ' ✅' if settings[model][UserSettings.SHOW_USAGE_QUOTA] else ' ❌'
                    ),
                    callback_data=f'setting:{UserSettings.SHOW_USAGE_QUOTA}:{model}'
                ),
            ],
            [
                InlineKeyboardButton(
                    text=get_localization(language_code).SETTINGS_SEND_TYPE.upper(),
                    callback_data=f'setting:nothing:{model}'
                ),
            ],
            [
                InlineKeyboardButton(
                    text=get_localization(language_code).SETTINGS_SEND_TYPE_IMAGE + (
                        ' ✅' if settings[model][UserSettings.SEND_TYPE] == SendType.IMAGE else ''
                    ),
                    callback_data=f'setting:{SendType.IMAGE}:{model}'
                ),
                InlineKeyboardButton(
                    text=get_localization(language_code).SETTINGS_SEND_TYPE_DOCUMENT + (
                        ' ✅' if settings[model][UserSettings.SEND_TYPE] == SendType.DOCUMENT else ''
                    ),
                    callback_data=f'setting:{SendType.DOCUMENT}:{model}'
                ),
            ],
            [
                InlineKeyboardButton(
                    text=get_localization(language_code).SETTINGS_ASPECT_RATIO.upper(),
                    callback_data=f'setting:nothing:{model}'
                ),
            ],
            [
                InlineKeyboardButton(
                    text=AspectRatio.SQUARE + (
                        ' ✅' if settings[model][UserSettings.ASPECT_RATIO] == AspectRatio.SQUARE else ''
                    ),
                    callback_data=f'setting:SQUARE:{model}'
                ),
                InlineKeyboardButton(
                    text=AspectRatio.LANDSCAPE + (
                        ' ✅' if settings[model][UserSettings.ASPECT_RATIO] == AspectRatio.LANDSCAPE else ''
                    ),
                    callback_data=f'setting:LANDSCAPE:{model}'
                ),
                InlineKeyboardButton(
                    text=AspectRatio.PORTRAIT + (
                        ' ✅' if settings[model][UserSettings.ASPECT_RATIO] == AspectRatio.PORTRAIT else ''
                    ),
                    callback_data=f'setting:PORTRAIT:{model}'
                ),
            ],
            [
                InlineKeyboardButton(
                    text=AspectRatio.STANDARD_HORIZONTAL + (
                        ' ✅' if settings[model][UserSettings.ASPECT_RATIO] == AspectRatio.STANDARD_HORIZONTAL else ''
                    ),
                    callback_data=f'setting:STANDARD_HORIZONTAL:{model}'
                ),
                InlineKeyboardButton(
                    text=AspectRatio.STANDARD_VERTICAL + (
                        ' ✅' if settings[model][UserSettings.ASPECT_RATIO] == AspectRatio.STANDARD_VERTICAL else ''
                    ),
                    callback_data=f'setting:STANDARD_VERTICAL:{model}'
                ),
            ],
            [
                InlineKeyboardButton(
                    text=AspectRatio.BANNER_HORIZONTAL + (
                        ' ✅' if settings[model][UserSettings.ASPECT_RATIO] == AspectRatio.BANNER_HORIZONTAL else ''
                    ),
                    callback_data=f'setting:BANNER_HORIZONTAL:{model}'
                ),
                InlineKeyboardButton(
                    text=AspectRatio.BANNER_VERTICAL + (
                        ' ✅' if settings[model][UserSettings.ASPECT_RATIO] == AspectRatio.BANNER_VERTICAL else ''
                    ),
                    callback_data=f'setting:BANNER_VERTICAL:{model}'
                ),
                InlineKeyboardButton(
                    text=AspectRatio.CLASSIC_HORIZONTAL + (
                        ' ✅' if settings[model][UserSettings.ASPECT_RATIO] == AspectRatio.CLASSIC_HORIZONTAL else ''
                    ),
                    callback_data=f'setting:CLASSIC_HORIZONTAL:{model}'
                ),
                InlineKeyboardButton(
                    text=AspectRatio.CLASSIC_VERTICAL + (
                        ' ✅' if settings[model][UserSettings.ASPECT_RATIO] == AspectRatio.CLASSIC_VERTICAL else ''
                    ),
                    callback_data=f'setting:CLASSIC_VERTICAL:{model}'
                ),
            ],
            [
                InlineKeyboardButton(
                    text=get_localization(language_code).SETTINGS_PROMPT_SAFETY.upper(),
                    callback_data=f'setting:nothing:{model}'
                ),
            ],
            [
                InlineKeyboardButton(
                    text=get_localization(language_code).FLUX_STRICT_SAFETY_TOLERANCE + (
                        ' ✅' if settings[model][UserSettings.SAFETY_TOLERANCE] == FluxSafetyTolerance.STRICT else ''
                    ),
                    callback_data=f'setting:{FluxSafetyTolerance.STRICT}:{model}'
                ),
            ],
            [
                InlineKeyboardButton(
                    text=get_localization(language_code).FLUX_MIDDLE_SAFETY_TOLERANCE + (
                        ' ✅' if settings[model][UserSettings.SAFETY_TOLERANCE] == FluxSafetyTolerance.MIDDLE else ''
                    ),
                    callback_data=f'setting:{FluxSafetyTolerance.MIDDLE}:{model}'
                ),
            ],
            [
                InlineKeyboardButton(
                    text=get_localization(language_code).FLUX_PERMISSIVE_SAFETY_TOLERANCE + (
                        ' ✅' if settings[model][UserSettings.SAFETY_TOLERANCE] == FluxSafetyTolerance.PERMISSIVE else ''
                    ),
                    callback_data=f'setting:{FluxSafetyTolerance.PERMISSIVE}:{model}'
                ),
            ],
        ]
    elif model == Model.FACE_SWAP:
        buttons = [
            [
                InlineKeyboardButton(
                    text=get_localization(language_code).SETTINGS_SHOW_USAGE_QUOTA_IN_MESSAGES + (
                        ' ✅' if settings[model][UserSettings.SHOW_USAGE_QUOTA] else ' ❌'),
                    callback_data=f'setting:{UserSettings.SHOW_USAGE_QUOTA}:{model}'
                ),
            ],
            [
                InlineKeyboardButton(
                    text=get_localization(language_code).SETTINGS_SEND_TYPE.upper(),
                    callback_data=f'setting:nothing:{model}'
                ),
            ],
            [
                InlineKeyboardButton(
                    text=get_localization(language_code).SETTINGS_SEND_TYPE_IMAGE + (
                        ' ✅' if settings[model][UserSettings.SEND_TYPE] == SendType.IMAGE else ''
                    ),
                    callback_data=f'setting:{SendType.IMAGE}:{model}'
                ),
                InlineKeyboardButton(
                    text=get_localization(language_code).SETTINGS_SEND_TYPE_DOCUMENT + (
                        ' ✅' if settings[model][UserSettings.SEND_TYPE] == SendType.DOCUMENT else ''
                    ),
                    callback_data=f'setting:{SendType.DOCUMENT}:{model}'
                ),
            ],
            [
                InlineKeyboardButton(
                    text=get_localization(language_code).SETTINGS_GENDER.upper(),
                    callback_data=f'setting:nothing:{model}'
                ),
            ],
            [
                InlineKeyboardButton(
                    text=get_localization(language_code).GENDER_MALE + (
                        ' ✅' if settings[model][UserSettings.GENDER] == UserGender.MALE else ''
                    ),
                    callback_data=f'setting:{UserGender.MALE}:{model}'
                ),
                InlineKeyboardButton(
                    text=get_localization(language_code).GENDER_FEMALE + (
                        ' ✅' if settings[model][UserSettings.GENDER] == UserGender.FEMALE else ''
                    ),
                    callback_data=f'setting:{UserGender.FEMALE}:{model}'
                ),
            ],
        ]
    elif model == Model.LUMA_PHOTON:
        buttons = [
            [
                InlineKeyboardButton(
                    text=get_localization(language_code).SETTINGS_SHOW_USAGE_QUOTA_IN_MESSAGES + (
                        ' ✅' if settings[model][UserSettings.SHOW_USAGE_QUOTA] else ' ❌'),
                    callback_data=f'setting:{UserSettings.SHOW_USAGE_QUOTA}:{model}'
                ),
            ],
            [
                InlineKeyboardButton(
                    text=get_localization(language_code).SETTINGS_SEND_TYPE.upper(),
                    callback_data=f'setting:nothing:{model}'
                ),
            ],
            [
                InlineKeyboardButton(
                    text=get_localization(language_code).SETTINGS_SEND_TYPE_IMAGE + (
                        ' ✅' if settings[model][UserSettings.SEND_TYPE] == SendType.IMAGE else ''
                    ),
                    callback_data=f'setting:{SendType.IMAGE}:{model}'
                ),
                InlineKeyboardButton(
                    text=get_localization(language_code).SETTINGS_SEND_TYPE_DOCUMENT + (
                        ' ✅' if settings[model][UserSettings.SEND_TYPE] == SendType.DOCUMENT else ''
                    ),
                    callback_data=f'setting:{SendType.DOCUMENT}:{model}'
                ),
            ],
            [
                InlineKeyboardButton(
                    text=get_localization(language_code).SETTINGS_ASPECT_RATIO.upper(),
                    callback_data=f'setting:nothing:{model}'
                ),
            ],
            [
                InlineKeyboardButton(
                    text=AspectRatio.SQUARE + (
                        ' ✅' if settings[model][UserSettings.ASPECT_RATIO] == AspectRatio.SQUARE else ''
                    ),
                    callback_data=f'setting:SQUARE:{model}'
                ),
                InlineKeyboardButton(
                    text=AspectRatio.LANDSCAPE + (
                        ' ✅' if settings[model][UserSettings.ASPECT_RATIO] == AspectRatio.LANDSCAPE else ''
                    ),
                    callback_data=f'setting:LANDSCAPE:{model}'
                ),
                InlineKeyboardButton(
                    text=AspectRatio.PORTRAIT + (
                        ' ✅' if settings[model][UserSettings.ASPECT_RATIO] == AspectRatio.PORTRAIT else ''
                    ),
                    callback_data=f'setting:PORTRAIT:{model}'
                ),
            ],
            [
                InlineKeyboardButton(
                    text=AspectRatio.CINEMASCOPE_HORIZONTAL + (
                        ' ✅' if settings[model][UserSettings.ASPECT_RATIO] == AspectRatio.CINEMASCOPE_HORIZONTAL else ''
                    ),
                    callback_data=f'setting:CINEMASCOPE_HORIZONTAL:{model}'
                ),
                InlineKeyboardButton(
                    text=AspectRatio.CINEMASCOPE_VERTICAL + (
                        ' ✅' if settings[model][UserSettings.ASPECT_RATIO] == AspectRatio.CINEMASCOPE_VERTICAL else ''
                    ),
                    callback_data=f'setting:CINEMASCOPE_VERTICAL:{model}'
                ),
            ],
            [
                InlineKeyboardButton(
                    text=AspectRatio.CLASSIC_HORIZONTAL + (
                        ' ✅' if settings[model][UserSettings.ASPECT_RATIO] == AspectRatio.CLASSIC_HORIZONTAL else ''
                    ),
                    callback_data=f'setting:CLASSIC_HORIZONTAL:{model}'
                ),
                InlineKeyboardButton(
                    text=AspectRatio.CLASSIC_VERTICAL + (
                        ' ✅' if settings[model][UserSettings.ASPECT_RATIO] == AspectRatio.CLASSIC_VERTICAL else ''
                    ),
                    callback_data=f'setting:CLASSIC_VERTICAL:{model}'
                ),
            ],
        ]
    elif model == Model.RECRAFT:
        buttons = [
            [
                InlineKeyboardButton(
                    text=get_localization(language_code).SETTINGS_SHOW_USAGE_QUOTA_IN_MESSAGES + (
                        ' ✅' if settings[model][UserSettings.SHOW_USAGE_QUOTA] else ' ❌'
                    ),
                    callback_data=f'setting:{UserSettings.SHOW_USAGE_QUOTA}:{model}'
                ),
            ],
            [
                InlineKeyboardButton(
                    text=get_localization(language_code).SETTINGS_SEND_TYPE.upper(),
                    callback_data=f'setting:nothing:{model}'
                ),
            ],
            [
                InlineKeyboardButton(
                    text=get_localization(language_code).SETTINGS_SEND_TYPE_IMAGE + (
                        ' ✅' if settings[model][UserSettings.SEND_TYPE] == SendType.IMAGE else ''
                    ),
                    callback_data=f'setting:{SendType.IMAGE}:{model}'
                ),
                InlineKeyboardButton(
                    text=get_localization(language_code).SETTINGS_SEND_TYPE_DOCUMENT + (
                        ' ✅' if settings[model][UserSettings.SEND_TYPE] == SendType.DOCUMENT else ''
                    ),
                    callback_data=f'setting:{SendType.DOCUMENT}:{model}'
                ),
            ],
            [
                InlineKeyboardButton(
                    text=get_localization(language_code).SETTINGS_ASPECT_RATIO.upper(),
                    callback_data=f'setting:nothing:{model}'
                ),
            ],
            [
                InlineKeyboardButton(
                    text=AspectRatio.SQUARE + (
                        ' ✅' if settings[model][UserSettings.ASPECT_RATIO] == AspectRatio.SQUARE else ''
                    ),
                    callback_data=f'setting:SQUARE:{model}'
                ),
                InlineKeyboardButton(
                    text=AspectRatio.LANDSCAPE + (
                        ' ✅' if settings[model][UserSettings.ASPECT_RATIO] == AspectRatio.LANDSCAPE else ''
                    ),
                    callback_data=f'setting:LANDSCAPE:{model}'
                ),
                InlineKeyboardButton(
                    text=AspectRatio.PORTRAIT + (
                        ' ✅' if settings[model][UserSettings.ASPECT_RATIO] == AspectRatio.PORTRAIT else ''
                    ),
                    callback_data=f'setting:PORTRAIT:{model}'
                ),
            ],
            [
                InlineKeyboardButton(
                    text=AspectRatio.STANDARD_HORIZONTAL + (
                        ' ✅' if settings[model][UserSettings.ASPECT_RATIO] == AspectRatio.STANDARD_HORIZONTAL else ''
                    ),
                    callback_data=f'setting:STANDARD_HORIZONTAL:{model}'
                ),
                InlineKeyboardButton(
                    text=AspectRatio.STANDARD_VERTICAL + (
                        ' ✅' if settings[model][UserSettings.ASPECT_RATIO] == AspectRatio.STANDARD_VERTICAL else ''
                    ),
                    callback_data=f'setting:STANDARD_VERTICAL:{model}'
                ),
            ],
            [
                InlineKeyboardButton(
                    text=AspectRatio.BANNER_HORIZONTAL + (
                        ' ✅' if settings[model][UserSettings.ASPECT_RATIO] == AspectRatio.BANNER_HORIZONTAL else ''
                    ),
                    callback_data=f'setting:BANNER_HORIZONTAL:{model}'
                ),
                InlineKeyboardButton(
                    text=AspectRatio.BANNER_VERTICAL + (
                        ' ✅' if settings[model][UserSettings.ASPECT_RATIO] == AspectRatio.BANNER_VERTICAL else ''
                    ),
                    callback_data=f'setting:BANNER_VERTICAL:{model}'
                ),
                InlineKeyboardButton(
                    text=AspectRatio.CLASSIC_HORIZONTAL + (
                        ' ✅' if settings[model][UserSettings.ASPECT_RATIO] == AspectRatio.CLASSIC_HORIZONTAL else ''
                    ),
                    callback_data=f'setting:CLASSIC_HORIZONTAL:{model}'
                ),
                InlineKeyboardButton(
                    text=AspectRatio.CLASSIC_VERTICAL + (
                        ' ✅' if settings[model][UserSettings.ASPECT_RATIO] == AspectRatio.CLASSIC_VERTICAL else ''
                    ),
                    callback_data=f'setting:CLASSIC_VERTICAL:{model}'
                ),
            ],
        ]
    elif model == Model.PHOTOSHOP_AI:
        buttons = [
            [
                InlineKeyboardButton(
                    text=get_localization(language_code).SETTINGS_SHOW_USAGE_QUOTA_IN_MESSAGES + (
                        ' ✅' if settings[model][UserSettings.SHOW_USAGE_QUOTA] else ' ❌'),
                    callback_data=f'setting:{UserSettings.SHOW_USAGE_QUOTA}:{model}'
                ),
            ],
            [
                InlineKeyboardButton(
                    text=get_localization(language_code).SETTINGS_SEND_TYPE.upper(),
                    callback_data=f'setting:nothing:{model}'
                ),
            ],
            [
                InlineKeyboardButton(
                    text=get_localization(language_code).SETTINGS_SEND_TYPE_IMAGE + (
                        ' ✅' if settings[model][UserSettings.SEND_TYPE] == SendType.IMAGE else ''
                    ),
                    callback_data=f'setting:{SendType.IMAGE}:{model}'
                ),
                InlineKeyboardButton(
                    text=get_localization(language_code).SETTINGS_SEND_TYPE_DOCUMENT + (
                        ' ✅' if settings[model][UserSettings.SEND_TYPE] == SendType.DOCUMENT else ''
                    ),
                    callback_data=f'setting:{SendType.DOCUMENT}:{model}'
                ),
            ],
        ]
    elif model == Model.MUSIC_GEN:
        buttons = [
            [
                InlineKeyboardButton(
                    text=get_localization(language_code).SETTINGS_SHOW_USAGE_QUOTA_IN_MESSAGES + (
                        ' ✅' if settings[model][UserSettings.SHOW_USAGE_QUOTA] else ' ❌'),
                    callback_data=f'setting:{UserSettings.SHOW_USAGE_QUOTA}:{model}'
                ),
            ],
        ]
    elif model == Model.SUNO:
        buttons = [
            [
                InlineKeyboardButton(
                    text=get_localization(language_code).SETTINGS_SHOW_USAGE_QUOTA_IN_MESSAGES + (
                        ' ✅' if settings[model][UserSettings.SHOW_USAGE_QUOTA] else ' ❌'),
                    callback_data=f'setting:{UserSettings.SHOW_USAGE_QUOTA}:{model}'
                ),
            ],
            [
                InlineKeyboardButton(
                    text=get_localization(language_code).SETTINGS_SEND_TYPE.upper(),
                    callback_data=f'setting:nothing:{model}'
                ),
            ],
            [
                InlineKeyboardButton(
                    text=get_localization(language_code).SETTINGS_SEND_TYPE_AUDIO + (
                        ' ✅' if settings[model][UserSettings.SEND_TYPE] == SendType.AUDIO else ''
                    ),
                    callback_data=f'setting:{SendType.AUDIO}:{model}'
                ),
                InlineKeyboardButton(
                    text=get_localization(language_code).SETTINGS_SEND_TYPE_VIDEO + (
                        ' ✅' if settings[model][UserSettings.SEND_TYPE] == SendType.VIDEO else ''
                    ),
                    callback_data=f'setting:{SendType.VIDEO}:{model}'
                ),
            ],
            [
                InlineKeyboardButton(
                    text=get_localization(language_code).SETTINGS_VERSION.upper(),
                    callback_data=f'setting:nothing:{model}'
                ),
            ],
            [
                InlineKeyboardButton(
                    text=SunoVersion.V3 + (
                        ' ✅' if settings[model][UserSettings.VERSION] == SunoVersion.V3 else ''
                    ),
                    callback_data=f'setting:{SunoVersion.V3}:{model}'
                ),
                InlineKeyboardButton(
                    text=SunoVersion.V4 + (
                        ' ✅' if settings[model][UserSettings.VERSION] == SunoVersion.V4 else ''
                    ),
                    callback_data=f'setting:{SunoVersion.V4}:{model}'
                ),
            ],
        ]
    elif model == Model.KLING:
        buttons = [
            [
                InlineKeyboardButton(
                    text=get_localization(language_code).SETTINGS_SHOW_USAGE_QUOTA_IN_MESSAGES + (
                        ' ✅' if settings[model][UserSettings.SHOW_USAGE_QUOTA] else ' ❌'),
                    callback_data=f'setting:{UserSettings.SHOW_USAGE_QUOTA}:{model}'
                ),
            ],
            [
                InlineKeyboardButton(
                    text=get_localization(language_code).SETTINGS_SEND_TYPE.upper(),
                    callback_data=f'setting:nothing:{model}'
                ),
            ],
            [
                InlineKeyboardButton(
                    text=get_localization(language_code).SETTINGS_SEND_TYPE_VIDEO + (
                        ' ✅' if settings[model][UserSettings.SEND_TYPE] == SendType.VIDEO else ''
                    ),
                    callback_data=f'setting:{SendType.VIDEO}:{model}'
                ),
                InlineKeyboardButton(
                    text=get_localization(language_code).SETTINGS_SEND_TYPE_DOCUMENT + (
                        ' ✅' if settings[model][UserSettings.SEND_TYPE] == SendType.DOCUMENT else ''
                    ),
                    callback_data=f'setting:{SendType.DOCUMENT}:{model}'
                ),
            ],
            [
                InlineKeyboardButton(
                    text=get_localization(language_code).SETTINGS_VERSION.upper(),
                    callback_data=f'setting:nothing:{model}'
                ),
            ],
            [
                InlineKeyboardButton(
                    text=KlingVersion.V1 + (
                        ' ✅' if settings[model][UserSettings.VERSION] == KlingVersion.V1 else ''
                    ),
                    callback_data=f'setting:{KlingVersion.V1}:{model}'
                ),
                InlineKeyboardButton(
                    text=KlingVersion.V2 + (
                        ' ✅' if settings[model][UserSettings.VERSION] == KlingVersion.V2 else ''
                    ),
                    callback_data=f'setting:{KlingVersion.V2}:{model}'
                ),
            ],
            [
                InlineKeyboardButton(
                    text=get_localization(language_code).SETTINGS_ASPECT_RATIO.upper(),
                    callback_data=f'setting:nothing:{model}'
                ),
            ],
            [
                InlineKeyboardButton(
                    text=AspectRatio.SQUARE + (
                        ' ✅' if settings[model][UserSettings.ASPECT_RATIO] == AspectRatio.SQUARE else ''
                    ),
                    callback_data=f'setting:SQUARE:{model}'
                ),
                InlineKeyboardButton(
                    text=AspectRatio.LANDSCAPE + (
                        ' ✅' if settings[model][UserSettings.ASPECT_RATIO] == AspectRatio.LANDSCAPE else ''
                    ),
                    callback_data=f'setting:LANDSCAPE:{model}'
                ),
                InlineKeyboardButton(
                    text=AspectRatio.PORTRAIT + (
                        ' ✅' if settings[model][UserSettings.ASPECT_RATIO] == AspectRatio.PORTRAIT else ''
                    ),
                    callback_data=f'setting:PORTRAIT:{model}'
                ),
            ],
            [
                InlineKeyboardButton(
                    text=get_localization(language_code).SETTINGS_DURATION.upper(),
                    callback_data=f'setting:nothing:{model}'
                ),
            ],
            [
                InlineKeyboardButton(
                    text='5' + (
                        ' ✅' if settings[model][UserSettings.DURATION] == KlingDuration.SECONDS_5 else ''
                    ),
                    callback_data=f'setting:{KlingDuration.SECONDS_5}:{model}'
                ),
                InlineKeyboardButton(
                    text='10' + (
                        ' ✅' if settings[model][UserSettings.DURATION] == KlingDuration.SECONDS_10 else ''
                    ),
                    callback_data=f'setting:{KlingDuration.SECONDS_10}:{model}'
                ),
            ],
            [
                InlineKeyboardButton(
                    text=get_localization(language_code).SETTINGS_MODE.upper(),
                    callback_data=f'setting:nothing:{model}'
                ),
            ],
            [
                InlineKeyboardButton(
                    text=get_localization(language_code).KLING_MODE_STANDARD + (
                        ' ✅' if settings[model][UserSettings.MODE] == KlingMode.STANDARD else ''
                    ),
                    callback_data=f'setting:{KlingMode.STANDARD}:{model}'
                ),
                InlineKeyboardButton(
                    text=get_localization(language_code).KLING_MODE_PRO + (
                        ' ✅' if settings[model][UserSettings.MODE] == KlingMode.PRO else ''
                    ),
                    callback_data=f'setting:{KlingMode.PRO}:{model}'
                ),
            ],
        ]
    elif model == Model.RUNWAY:
        buttons = [
            [
                InlineKeyboardButton(
                    text=get_localization(language_code).SETTINGS_SHOW_USAGE_QUOTA_IN_MESSAGES + (
                        ' ✅' if settings[model][UserSettings.SHOW_USAGE_QUOTA] else ' ❌'
                    ),
                    callback_data=f'setting:{UserSettings.SHOW_USAGE_QUOTA}:{model}'
                ),
            ],
            [
                InlineKeyboardButton(
                    text=get_localization(language_code).SETTINGS_SEND_TYPE.upper(),
                    callback_data=f'setting:nothing:{model}'
                ),
            ],
            [
                InlineKeyboardButton(
                    text=get_localization(language_code).SETTINGS_SEND_TYPE_VIDEO + (
                        ' ✅' if settings[model][UserSettings.SEND_TYPE] == SendType.VIDEO else ''
                    ),
                    callback_data=f'setting:{SendType.VIDEO}:{model}'
                ),
                InlineKeyboardButton(
                    text=get_localization(language_code).SETTINGS_SEND_TYPE_DOCUMENT + (
                        ' ✅' if settings[model][UserSettings.SEND_TYPE] == SendType.DOCUMENT else ''
                    ),
                    callback_data=f'setting:{SendType.DOCUMENT}:{model}'
                ),
            ],
            [
                InlineKeyboardButton(
                    text=get_localization(language_code).SETTINGS_ASPECT_RATIO.upper(),
                    callback_data=f'setting:nothing:{model}'
                ),
            ],
            [
                InlineKeyboardButton(
                    text=AspectRatio.LANDSCAPE + (
                        ' ✅' if settings[model][UserSettings.RESOLUTION] == RunwayResolution.LANDSCAPE else ''
                    ),
                    callback_data=f'setting:LANDSCAPE:{model}'
                ),
                InlineKeyboardButton(
                    text=AspectRatio.PORTRAIT + (
                        ' ✅' if settings[model][UserSettings.RESOLUTION] == RunwayResolution.PORTRAIT else ''
                    ),
                    callback_data=f'setting:PORTRAIT:{model}'
                ),
            ],
            [
                InlineKeyboardButton(
                    text=AspectRatio.SQUARE + (
                        ' ✅' if settings[model][UserSettings.RESOLUTION] == RunwayResolution.SQUARE else ''
                    ),
                    callback_data=f'setting:SQUARE:{model}'
                ),
                InlineKeyboardButton(
                    text=AspectRatio.CINEMASCOPE_HORIZONTAL + (
                        ' ✅' if settings[model][UserSettings.RESOLUTION] == RunwayResolution.CINEMASCOPE else ''
                    ),
                    callback_data=f'setting:CINEMASCOPE_HORIZONTAL:{model}'
                ),
            ],
            [
                InlineKeyboardButton(
                    text=AspectRatio.STANDARD_VERTICAL + (
                        ' ✅' if settings[model][UserSettings.RESOLUTION] == RunwayResolution.STANDARD_VERTICAL else ''
                    ),
                    callback_data=f'setting:STANDARD_VERTICAL:{model}'
                ),
                InlineKeyboardButton(
                    text=AspectRatio.STANDARD_HORIZONTAL + (
                        ' ✅' if settings[model][UserSettings.RESOLUTION] == RunwayResolution.STANDARD_HORIZONTAL else ''
                    ),
                    callback_data=f'setting:STANDARD_HORIZONTAL:{model}'
                ),
            ],
            [
                InlineKeyboardButton(
                    text=get_localization(language_code).SETTINGS_DURATION.upper(),
                    callback_data=f'setting:nothing:{model}'
                ),
            ],
            [
                InlineKeyboardButton(
                    text='5' + (
                        ' ✅' if settings[model][UserSettings.DURATION] == RunwayDuration.SECONDS_5 else ''
                    ),
                    callback_data=f'setting:{RunwayDuration.SECONDS_5}:{model}'
                ),
                InlineKeyboardButton(
                    text='10' + (
                        ' ✅' if settings[model][UserSettings.DURATION] == RunwayDuration.SECONDS_10 else ''
                    ),
                    callback_data=f'setting:{RunwayDuration.SECONDS_10}:{model}'
                ),
            ],
        ]
    elif model == Model.LUMA_RAY:
        buttons = [
            [
                InlineKeyboardButton(
                    text=get_localization(language_code).SETTINGS_SHOW_USAGE_QUOTA_IN_MESSAGES + (
                        ' ✅' if settings[model][UserSettings.SHOW_USAGE_QUOTA] else ' ❌'
                    ),
                    callback_data=f'setting:{UserSettings.SHOW_USAGE_QUOTA}:{model}'
                ),
            ],
            [
                InlineKeyboardButton(
                    text=get_localization(language_code).SETTINGS_SEND_TYPE.upper(),
                    callback_data=f'setting:nothing:{model}'
                ),
            ],
            [
                InlineKeyboardButton(
                    text=get_localization(language_code).SETTINGS_SEND_TYPE_VIDEO + (
                        ' ✅' if settings[model][UserSettings.SEND_TYPE] == SendType.VIDEO else ''
                    ),
                    callback_data=f'setting:{SendType.VIDEO}:{model}'
                ),
                InlineKeyboardButton(
                    text=get_localization(language_code).SETTINGS_SEND_TYPE_DOCUMENT + (
                        ' ✅' if settings[model][UserSettings.SEND_TYPE] == SendType.DOCUMENT else ''
                    ),
                    callback_data=f'setting:{SendType.DOCUMENT}:{model}'
                ),
            ],
            [
                InlineKeyboardButton(
                    text=get_localization(language_code).SETTINGS_QUALITY.upper(),
                    callback_data=f'setting:nothing:{model}'
                ),
            ],
            [
                InlineKeyboardButton(
                    text=LumaRayQuality.SD + (
                        ' ✅' if settings[model][UserSettings.QUALITY] == LumaRayQuality.SD else ''
                    ),
                    callback_data=f'setting:{LumaRayQuality.SD}:{model}'
                ),
                InlineKeyboardButton(
                    text=LumaRayQuality.HD + (
                        ' ✅' if settings[model][UserSettings.QUALITY] == LumaRayQuality.HD else ''
                    ),
                    callback_data=f'setting:{LumaRayQuality.HD}:{model}'
                ),
            ],
            [
                InlineKeyboardButton(
                    text=get_localization(language_code).SETTINGS_ASPECT_RATIO.upper(),
                    callback_data=f'setting:nothing:{model}'
                ),
            ],
            [
                InlineKeyboardButton(
                    text=AspectRatio.SQUARE + (
                        ' ✅' if settings[model][UserSettings.ASPECT_RATIO] == AspectRatio.SQUARE else ''
                    ),
                    callback_data=f'setting:SQUARE:{model}'
                ),
                InlineKeyboardButton(
                    text=AspectRatio.LANDSCAPE + (
                        ' ✅' if settings[model][UserSettings.ASPECT_RATIO] == AspectRatio.LANDSCAPE else ''
                    ),
                    callback_data=f'setting:LANDSCAPE:{model}'
                ),
                InlineKeyboardButton(
                    text=AspectRatio.PORTRAIT + (
                        ' ✅' if settings[model][UserSettings.ASPECT_RATIO] == AspectRatio.PORTRAIT else ''
                    ),
                    callback_data=f'setting:PORTRAIT:{model}'
                ),
            ],
            [
                InlineKeyboardButton(
                    text=AspectRatio.CINEMASCOPE_HORIZONTAL + (
                        ' ✅' if settings[model][UserSettings.ASPECT_RATIO] == AspectRatio.CINEMASCOPE_HORIZONTAL else ''
                    ),
                    callback_data=f'setting:CINEMASCOPE_HORIZONTAL:{model}'
                ),
                InlineKeyboardButton(
                    text=AspectRatio.CINEMASCOPE_VERTICAL + (
                        ' ✅' if settings[model][UserSettings.ASPECT_RATIO] == AspectRatio.CINEMASCOPE_VERTICAL else ''
                    ),
                    callback_data=f'setting:CINEMASCOPE_VERTICAL:{model}'
                ),
            ],
            [
                InlineKeyboardButton(
                    text=AspectRatio.CLASSIC_HORIZONTAL + (
                        ' ✅' if settings[model][UserSettings.ASPECT_RATIO] == AspectRatio.CLASSIC_HORIZONTAL else ''
                    ),
                    callback_data=f'setting:CLASSIC_HORIZONTAL:{model}'
                ),
                InlineKeyboardButton(
                    text=AspectRatio.CLASSIC_VERTICAL + (
                        ' ✅' if settings[model][UserSettings.ASPECT_RATIO] == AspectRatio.CLASSIC_VERTICAL else ''
                    ),
                    callback_data=f'setting:CLASSIC_VERTICAL:{model}'
                ),
            ],
            [
                InlineKeyboardButton(
                    text=get_localization(language_code).SETTINGS_DURATION.upper(),
                    callback_data=f'setting:nothing:{model}'
                ),
            ],
            [
                InlineKeyboardButton(
                    text='5' + (
                        ' ✅' if settings[model][UserSettings.DURATION] == LumaRayDuration.SECONDS_5 else ''
                    ),
                    callback_data=f'setting:{LumaRayDuration.SECONDS_5}:{model}'
                ),
                InlineKeyboardButton(
                    text='9' + (
                        ' ✅' if settings[model][UserSettings.DURATION] == LumaRayDuration.SECONDS_9 else ''
                    ),
                    callback_data=f'setting:{LumaRayDuration.SECONDS_9}:{model}'
                ),
            ],
        ]
    elif model == Model.PIKA:
        buttons = [
            [
                InlineKeyboardButton(
                    text=get_localization(language_code).SETTINGS_SHOW_USAGE_QUOTA_IN_MESSAGES + (
                        ' ✅' if settings[model][UserSettings.SHOW_USAGE_QUOTA] else ' ❌'),
                    callback_data=f'setting:{UserSettings.SHOW_USAGE_QUOTA}:{model}'
                ),
            ],
            [
                InlineKeyboardButton(
                    text=get_localization(language_code).SETTINGS_SEND_TYPE.upper(),
                    callback_data=f'setting:nothing:{model}'
                ),
            ],
            [
                InlineKeyboardButton(
                    text=get_localization(language_code).SETTINGS_SEND_TYPE_VIDEO + (
                        ' ✅' if settings[model][UserSettings.SEND_TYPE] == SendType.VIDEO else ''
                    ),
                    callback_data=f'setting:{SendType.VIDEO}:{model}'
                ),
                InlineKeyboardButton(
                    text=get_localization(language_code).SETTINGS_SEND_TYPE_DOCUMENT + (
                        ' ✅' if settings[model][UserSettings.SEND_TYPE] == SendType.DOCUMENT else ''
                    ),
                    callback_data=f'setting:{SendType.DOCUMENT}:{model}'
                ),
            ],
            [
                InlineKeyboardButton(
                    text=get_localization(language_code).SETTINGS_ASPECT_RATIO.upper(),
                    callback_data=f'setting:nothing:{model}'
                ),
            ],
            [
                InlineKeyboardButton(
                    text=AspectRatio.SQUARE + (
                        ' ✅' if settings[model][UserSettings.ASPECT_RATIO] == AspectRatio.SQUARE else ''
                    ),
                    callback_data=f'setting:SQUARE:{model}'
                ),
                InlineKeyboardButton(
                    text=AspectRatio.LANDSCAPE + (
                        ' ✅' if settings[model][UserSettings.ASPECT_RATIO] == AspectRatio.LANDSCAPE else ''
                    ),
                    callback_data=f'setting:LANDSCAPE:{model}'
                ),
                InlineKeyboardButton(
                    text=AspectRatio.PORTRAIT + (
                        ' ✅' if settings[model][UserSettings.ASPECT_RATIO] == AspectRatio.PORTRAIT else ''
                    ),
                    callback_data=f'setting:PORTRAIT:{model}'
                ),
            ],
            [
                InlineKeyboardButton(
                    text=AspectRatio.BANNER_VERTICAL + (
                        ' ✅' if settings[model][UserSettings.ASPECT_RATIO] == AspectRatio.BANNER_VERTICAL else ''
                    ),
                    callback_data=f'setting:BANNER_VERTICAL:{model}'
                ),
                InlineKeyboardButton(
                    text=AspectRatio.CLASSIC_HORIZONTAL + (
                        ' ✅' if settings[model][UserSettings.ASPECT_RATIO] == AspectRatio.CLASSIC_HORIZONTAL else ''
                    ),
                    callback_data=f'setting:CLASSIC_HORIZONTAL:{model}'
                ),
            ],
        ]

    buttons.append(
        [
            InlineKeyboardButton(
                text=get_localization(language_code).ACTION_TO_OTHER_MODELS,
                callback_data=f'setting:back:{model_type}'
            )
        ],
    )

    return InlineKeyboardMarkup(inline_keyboard=buttons)


def build_voice_messages_settings_keyboard(
    language_code: LanguageCode,
    settings: dict,
    model: Optional[Model] = None,
) -> InlineKeyboardMarkup:
    buttons = [
        [
            InlineKeyboardButton(
                text=get_localization(language_code).SETTINGS_TURN_ON_VOICE_MESSAGES + (
                    ' ✅' if settings[Model.CHAT_GPT][UserSettings.TURN_ON_VOICE_MESSAGES] else ' ❌'),
                callback_data=f'voice_messages_setting:{UserSettings.TURN_ON_VOICE_MESSAGES}'
            ),
        ],
        [
            InlineKeyboardButton(
                text='👕 alloy' + (' ✅' if settings[Model.CHAT_GPT][UserSettings.VOICE] == 'alloy' else ''),
                callback_data=f'voice_messages_setting:alloy'
            ),
            InlineKeyboardButton(
                text='👕 echo' + (' ✅' if settings[Model.CHAT_GPT][UserSettings.VOICE] == 'echo' else ''),
                callback_data=f'voice_messages_setting:echo'
            ),
        ],
        [
            InlineKeyboardButton(
                text='👚 nova' + (' ✅' if settings[Model.CHAT_GPT][UserSettings.VOICE] == 'nova' else ''),
                callback_data=f'voice_messages_setting:nova'
            ),
            InlineKeyboardButton(
                text='👚 shimmer' + (' ✅' if settings[Model.CHAT_GPT][UserSettings.VOICE] == 'shimmer' else ''),
                callback_data=f'voice_messages_setting:shimmer'
            ),
        ],
        [
            InlineKeyboardButton(
                text='👕 fable' + (' ✅' if settings[Model.CHAT_GPT][UserSettings.VOICE] == 'fable' else ''),
                callback_data=f'voice_messages_setting:fable'
            ),
            InlineKeyboardButton(
                text='👕 onyx' + (' ✅' if settings[Model.CHAT_GPT][UserSettings.VOICE] == 'onyx' else ''),
                callback_data=f'voice_messages_setting:onyx'
            ),
        ],
        [
            InlineKeyboardButton(
                text=get_localization(language_code).SETTINGS_LISTEN_VOICES,
                callback_data=f'voice_messages_setting:listen'
            ),
        ],
        [
            InlineKeyboardButton(
                text=get_localization(language_code).ACTION_BACK,
                callback_data=f'voice_messages_setting:back:{model}' if model else 'voice_messages_setting:back'
            )
        ],
    ]

    return InlineKeyboardMarkup(inline_keyboard=buttons)
