from typing import Optional

from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup

from bot.database.models.common import (
    Model,
    ModelType,
    ChatGPTVersion,
    ClaudeGPTVersion,
    GeminiGPTVersion,
    DeepSeekVersion,
    StableDiffusionVersion,
    FluxVersion,
)
from bot.locales.main import get_localization
from bot.locales.types import LanguageCode


def build_info_keyboard(
    language_code: LanguageCode,
    model: Optional[Model] = None,
) -> InlineKeyboardMarkup:
    if model:
        return build_info_chosen_model_type_keyboard(language_code, model)
    else:
        buttons = [
            [
                InlineKeyboardButton(
                    text=get_localization(language_code).MODELS_TEXT,
                    callback_data=f'info:{ModelType.TEXT}'
                ),
            ],
            [
                InlineKeyboardButton(
                    text=get_localization(language_code).MODELS_IMAGE,
                    callback_data=f'info:{ModelType.IMAGE}'
                ),
            ],
            [
                InlineKeyboardButton(
                    text=get_localization(language_code).MODELS_MUSIC,
                    callback_data=f'info:{ModelType.MUSIC}'
                ),
            ],
            [
                InlineKeyboardButton(
                    text=get_localization(language_code).MODELS_VIDEO,
                    callback_data=f'info:{ModelType.VIDEO}'
                ),
            ],
            [
                InlineKeyboardButton(
                    text=get_localization(language_code).ACTION_CLOSE,
                    callback_data='info:close'
                ),
            ],
        ]

    return InlineKeyboardMarkup(inline_keyboard=buttons)


def build_info_text_models_keyboard(language_code: LanguageCode) -> InlineKeyboardMarkup:
    buttons = [
        [
            InlineKeyboardButton(
                text=get_localization(language_code).CHAT_GPT,
                callback_data=f'info_text_models:{Model.CHAT_GPT}'
            ),
            InlineKeyboardButton(
                text=get_localization(language_code).CLAUDE,
                callback_data=f'info_text_models:{Model.CLAUDE}'
            ),
        ],
        [
            InlineKeyboardButton(
                text=get_localization(language_code).GEMINI,
                callback_data=f'info_text_models:{Model.GEMINI}'
            ),
            InlineKeyboardButton(
                text=get_localization(language_code).DEEP_SEEK,
                callback_data=f'info_text_models:{Model.DEEP_SEEK}'
            ),
        ],
        [
            InlineKeyboardButton(
                text=get_localization(language_code).GROK,
                callback_data=f'info_text_models:{Model.GROK}'
            ),
            InlineKeyboardButton(
                text=get_localization(language_code).PERPLEXITY,
                callback_data=f'info_text_models:{Model.PERPLEXITY}'
            ),
        ],
        [
            InlineKeyboardButton(
                text=get_localization(language_code).ACTION_TO_OTHER_TYPE_MODELS,
                callback_data='info_text_models:back'
            ),
        ],
    ]

    return InlineKeyboardMarkup(inline_keyboard=buttons)


def build_info_chat_gpt_models_keyboard(language_code: LanguageCode) -> InlineKeyboardMarkup:
    buttons = [
        [
            InlineKeyboardButton(
                text=get_localization(language_code).CHAT_GPT_4_OMNI_MINI,
                callback_data=f'info_text_model:{Model.CHAT_GPT}:{ChatGPTVersion.V4_Omni_Mini}'
            ),
        ],
        [
            InlineKeyboardButton(
                text=get_localization(language_code).CHAT_GPT_4_OMNI,
                callback_data=f'info_text_model:{Model.CHAT_GPT}:{ChatGPTVersion.V4_Omni}'
            ),
        ],
        [
            InlineKeyboardButton(
                text=get_localization(language_code).CHAT_GPT_O_4_MINI,
                callback_data=f'info_text_model:{Model.CHAT_GPT}:{ChatGPTVersion.V4_O_Mini}'
            ),
        ],
        [
            InlineKeyboardButton(
                text=get_localization(language_code).CHAT_GPT_O_3,
                callback_data=f'info_text_model:{Model.CHAT_GPT}:{ChatGPTVersion.V3_O}'
            ),
        ],
        [
            InlineKeyboardButton(
                text=get_localization(language_code).CHAT_GPT_4_1_MINI,
                callback_data=f'info_text_model:{Model.CHAT_GPT}:{ChatGPTVersion.V4_1_Mini}'
            ),
        ],
        [
            InlineKeyboardButton(
                text=get_localization(language_code).CHAT_GPT_4_1,
                callback_data=f'info_text_model:{Model.CHAT_GPT}:{ChatGPTVersion.V4_1}'
            ),
        ],
        [
            InlineKeyboardButton(
                text=get_localization(language_code).ACTION_TO_OTHER_MODELS,
                callback_data=f'info_text_model:{Model.CHAT_GPT}:back'
            ),
        ],
    ]

    return InlineKeyboardMarkup(inline_keyboard=buttons)


def build_info_claude_models_keyboard(language_code: LanguageCode) -> InlineKeyboardMarkup:
    buttons = [
        [
            InlineKeyboardButton(
                text=get_localization(language_code).CLAUDE_3_HAIKU,
                callback_data=f'info_text_model:{Model.CLAUDE}:{ClaudeGPTVersion.V3_Haiku}'
            ),
        ],
        [
            InlineKeyboardButton(
                text=get_localization(language_code).CLAUDE_3_SONNET,
                callback_data=f'info_text_model:{Model.CLAUDE}:{ClaudeGPTVersion.V3_Sonnet}'
            ),
        ],
        [
            InlineKeyboardButton(
                text=get_localization(language_code).CLAUDE_3_OPUS,
                callback_data=f'info_text_model:{Model.CLAUDE}:{ClaudeGPTVersion.V3_Opus}'
            ),
        ],
        [
            InlineKeyboardButton(
                text=get_localization(language_code).ACTION_TO_OTHER_MODELS,
                callback_data=f'info_text_model:{Model.CLAUDE}:back'
            ),
        ],
    ]

    return InlineKeyboardMarkup(inline_keyboard=buttons)


def build_info_gemini_models_keyboard(language_code: LanguageCode) -> InlineKeyboardMarkup:
    buttons = [
        [
            InlineKeyboardButton(
                text=get_localization(language_code).GEMINI_2_FLASH,
                callback_data=f'info_text_model:{Model.GEMINI}:{GeminiGPTVersion.V2_Flash}'
            ),
        ],
        [
            InlineKeyboardButton(
                text=get_localization(language_code).GEMINI_2_PRO,
                callback_data=f'info_text_model:{Model.GEMINI}:{GeminiGPTVersion.V2_Pro}'
            ),
        ],
        [
            InlineKeyboardButton(
                text=get_localization(language_code).GEMINI_1_ULTRA,
                callback_data=f'info_text_model:{Model.GEMINI}:{GeminiGPTVersion.V1_Ultra}'
            ),
        ],
        [
            InlineKeyboardButton(
                text=get_localization(language_code).ACTION_TO_OTHER_MODELS,
                callback_data=f'info_text_model:{Model.GEMINI}:back'
            ),
        ],
    ]

    return InlineKeyboardMarkup(inline_keyboard=buttons)


def build_info_deep_seek_models_keyboard(language_code: LanguageCode) -> InlineKeyboardMarkup:
    buttons = [
        [
            InlineKeyboardButton(
                text=get_localization(language_code).DEEP_SEEK_V3,
                callback_data=f'info_text_model:{Model.DEEP_SEEK}:{DeepSeekVersion.V3}'
            ),
        ],
        [
            InlineKeyboardButton(
                text=get_localization(language_code).DEEP_SEEK_R1,
                callback_data=f'info_text_model:{Model.DEEP_SEEK}:{DeepSeekVersion.R1}'
            ),
        ],
        [
            InlineKeyboardButton(
                text=get_localization(language_code).ACTION_TO_OTHER_MODELS,
                callback_data=f'info_text_model:{Model.DEEP_SEEK}:back'
            ),
        ],
    ]

    return InlineKeyboardMarkup(inline_keyboard=buttons)


def build_info_image_models_keyboard(language_code: LanguageCode) -> InlineKeyboardMarkup:
    buttons = [
        [
            InlineKeyboardButton(
                text=get_localization(language_code).DALL_E,
                callback_data=f'info_image_models:{Model.DALL_E}'
            ),
            InlineKeyboardButton(
                text=get_localization(language_code).MIDJOURNEY,
                callback_data=f'info_image_models:{Model.MIDJOURNEY}'
            ),
        ],
        [
            InlineKeyboardButton(
                text=get_localization(language_code).STABLE_DIFFUSION,
                callback_data=f'info_image_models:{Model.STABLE_DIFFUSION}'
            ),
            InlineKeyboardButton(
                text=get_localization(language_code).FLUX,
                callback_data=f'info_image_models:{Model.FLUX}'
            ),
        ],
        [
            InlineKeyboardButton(
                text=get_localization(language_code).LUMA_PHOTON,
                callback_data=f'info_image_models:{Model.LUMA_PHOTON}'
            ),
            InlineKeyboardButton(
                text=get_localization(language_code).RECRAFT,
                callback_data=f'info_image_models:{Model.RECRAFT}'
            ),
        ],
        [
            InlineKeyboardButton(
                text=get_localization(language_code).FACE_SWAP,
                callback_data=f'info_image_models:{Model.FACE_SWAP}'
            ),
            InlineKeyboardButton(
                text=get_localization(language_code).PHOTOSHOP_AI,
                callback_data=f'info_image_models:{Model.PHOTOSHOP_AI}'
            ),
        ],
        [
            InlineKeyboardButton(
                text=get_localization(language_code).ACTION_TO_OTHER_TYPE_MODELS,
                callback_data='info_image_models:back'
            ),
        ],
    ]

    return InlineKeyboardMarkup(inline_keyboard=buttons)


def build_info_stable_diffusion_models_keyboard(language_code: LanguageCode) -> InlineKeyboardMarkup:
    buttons = [
        [
            InlineKeyboardButton(
                text=get_localization(language_code).STABLE_DIFFUSION_XL,
                callback_data=f'info_image_model:{Model.STABLE_DIFFUSION}:{StableDiffusionVersion.XL}'
            ),
        ],
        [
            InlineKeyboardButton(
                text=get_localization(language_code).STABLE_DIFFUSION_3,
                callback_data=f'info_image_model:{Model.STABLE_DIFFUSION}:{StableDiffusionVersion.V3}'
            ),
        ],
        [
            InlineKeyboardButton(
                text=get_localization(language_code).ACTION_TO_OTHER_MODELS,
                callback_data=f'info_image_model:{Model.STABLE_DIFFUSION}:back'
            ),
        ],
    ]

    return InlineKeyboardMarkup(inline_keyboard=buttons)


def build_info_flux_models_keyboard(language_code: LanguageCode) -> InlineKeyboardMarkup:
    buttons = [
        [
            InlineKeyboardButton(
                text=get_localization(language_code).FLUX_1_DEV,
                callback_data=f'info_image_model:{Model.FLUX}:{FluxVersion.V1_Dev}'
            ),
        ],
        [
            InlineKeyboardButton(
                text=get_localization(language_code).FLUX_1_PRO,
                callback_data=f'info_image_model:{Model.FLUX}:{FluxVersion.V1_Pro}'
            ),
        ],
        [
            InlineKeyboardButton(
                text=get_localization(language_code).ACTION_TO_OTHER_MODELS,
                callback_data=f'info_image_model:{Model.FLUX}:back'
            ),
        ],
    ]

    return InlineKeyboardMarkup(inline_keyboard=buttons)


def build_info_music_models_keyboard(language_code: LanguageCode) -> InlineKeyboardMarkup:
    buttons = [
        [
            InlineKeyboardButton(
                text=get_localization(language_code).MUSIC_GEN,
                callback_data=f'info_music_models:{Model.MUSIC_GEN}'
            ),
            InlineKeyboardButton(
                text=get_localization(language_code).SUNO,
                callback_data=f'info_music_models:{Model.SUNO}'
            ),
        ],
        [
            InlineKeyboardButton(
                text=get_localization(language_code).ACTION_TO_OTHER_TYPE_MODELS,
                callback_data='info_music_models:back'
            ),
        ],
    ]

    return InlineKeyboardMarkup(inline_keyboard=buttons)


def build_info_video_models_keyboard(language_code: LanguageCode) -> InlineKeyboardMarkup:
    buttons = [
        [
            InlineKeyboardButton(
                text=get_localization(language_code).KLING,
                callback_data=f'info_video_models:{Model.KLING}'
            ),
            InlineKeyboardButton(
                text=get_localization(language_code).RUNWAY,
                callback_data=f'info_video_models:{Model.RUNWAY}'
            ),
        ],
        [
            InlineKeyboardButton(
                text=get_localization(language_code).LUMA_RAY,
                callback_data=f'info_video_models:{Model.LUMA_RAY}'
            ),
            InlineKeyboardButton(
                text=get_localization(language_code).PIKA,
                callback_data=f'info_video_models:{Model.PIKA}'
            ),
        ],
        [
            InlineKeyboardButton(
                text=get_localization(language_code).ACTION_TO_OTHER_TYPE_MODELS,
                callback_data='info_video_models:back'
            ),
        ]
    ]

    return InlineKeyboardMarkup(inline_keyboard=buttons)


def build_info_chosen_model_type_keyboard(language_code: LanguageCode, model_type: str) -> InlineKeyboardMarkup:
    buttons = [
        [
            InlineKeyboardButton(
                text=get_localization(language_code).ACTION_TO_OTHER_MODELS,
                callback_data=f'info_chosen_model_type:back:{model_type}'
            ),
        ],
    ]

    return InlineKeyboardMarkup(inline_keyboard=buttons)
