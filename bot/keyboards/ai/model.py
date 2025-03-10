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


def build_model_keyboard(
    language_code: LanguageCode,
    model: Model,
    model_version: ChatGPTVersion | ClaudeGPTVersion | GeminiGPTVersion | DeepSeekVersion | StableDiffusionVersion | FluxVersion,
    page=0,
    chosen_model=None,
) -> InlineKeyboardMarkup:
    buttons = []
    if page == 0:
        if chosen_model == Model.CHAT_GPT:
            buttons.extend(
                [
                    [
                        InlineKeyboardButton(
                            text=get_localization(language_code).CHAT_GPT.upper(),
                            callback_data=f'model:{ModelType.TEXT}',
                        ),
                    ],
                    [
                        InlineKeyboardButton(
                            text=get_localization(language_code).CHAT_GPT_4_OMNI_MINI + (
                                ' ✅' if model == Model.CHAT_GPT and model_version == ChatGPTVersion.V4_Omni_Mini else ''
                            ),
                            callback_data=f'model:{Model.CHAT_GPT}:{ChatGPTVersion.V4_Omni_Mini}'
                        ),
                    ],
                    [
                        InlineKeyboardButton(
                            text=get_localization(language_code).CHAT_GPT_4_OMNI + (
                                ' ✅' if model == Model.CHAT_GPT and model_version == ChatGPTVersion.V4_Omni else ''
                            ),
                            callback_data=f'model:{Model.CHAT_GPT}:{ChatGPTVersion.V4_Omni}'
                        ),
                    ],
                    [
                        InlineKeyboardButton(
                            text=get_localization(language_code).CHAT_GPT_O_3_MINI + (
                                ' ✅' if model == Model.CHAT_GPT and model_version == ChatGPTVersion.V3_O_Mini else ''
                            ),
                            callback_data=f'model:{Model.CHAT_GPT}:{ChatGPTVersion.V3_O_Mini}'
                        ),
                    ],
                    [
                        InlineKeyboardButton(
                            text=get_localization(language_code).CHAT_GPT_O_1 + (
                                ' ✅' if model == Model.CHAT_GPT and model_version == ChatGPTVersion.V1_O else ''
                            ),
                            callback_data=f'model:{Model.CHAT_GPT}:{ChatGPTVersion.V1_O}'
                        ),
                    ],
                    [
                        InlineKeyboardButton(
                            text=get_localization(language_code).ACTION_BACK,
                            callback_data=f'model:{Model.CHAT_GPT}:back'
                        ),
                    ],
                ]
            )
        elif chosen_model == Model.CLAUDE:
            buttons.extend(
                [
                    [
                        InlineKeyboardButton(
                            text=get_localization(language_code).CLAUDE.upper(),
                            callback_data=f'model:{ModelType.TEXT}',
                        ),
                    ],
                    [
                        InlineKeyboardButton(
                            text=get_localization(language_code).CLAUDE_3_HAIKU + (
                                ' ✅' if model == Model.CLAUDE and model_version == ClaudeGPTVersion.V3_Haiku else ''
                            ),
                            callback_data=f'model:{Model.CLAUDE}:{ClaudeGPTVersion.V3_Haiku}'
                        ),
                    ],
                    [
                        InlineKeyboardButton(
                            text=get_localization(language_code).CLAUDE_3_SONNET + (
                                ' ✅' if model == Model.CLAUDE and model_version == ClaudeGPTVersion.V3_Sonnet else ''
                            ),
                            callback_data=f'model:{Model.CLAUDE}:{ClaudeGPTVersion.V3_Sonnet}'
                        ),
                    ],
                    [
                        InlineKeyboardButton(
                            text=get_localization(language_code).CLAUDE_3_OPUS + (
                                ' ✅' if model == Model.CLAUDE and model_version == ClaudeGPTVersion.V3_Opus else ''
                            ),
                            callback_data=f'model:{Model.CLAUDE}:{ClaudeGPTVersion.V3_Opus}'
                        ),
                    ],
                    [
                        InlineKeyboardButton(
                            text=get_localization(language_code).ACTION_BACK,
                            callback_data=f'model:{Model.CLAUDE}:back'
                        ),
                    ],
                ]
            )
        elif chosen_model == Model.GEMINI:
            buttons.extend(
                [
                    [
                        InlineKeyboardButton(
                            text=get_localization(language_code).GEMINI.upper(),
                            callback_data=f'model:{ModelType.TEXT}',
                        ),
                    ],
                    [
                        InlineKeyboardButton(
                            text=get_localization(language_code).GEMINI_2_FLASH + (
                                ' ✅' if model == Model.GEMINI and model_version == GeminiGPTVersion.V2_Flash else ''
                            ),
                            callback_data=f'model:{Model.GEMINI}:{GeminiGPTVersion.V2_Flash}'
                        ),
                    ],
                    [
                        InlineKeyboardButton(
                            text=get_localization(language_code).GEMINI_2_PRO + (
                                ' ✅' if model == Model.GEMINI and model_version == GeminiGPTVersion.V2_Pro else ''
                            ),
                            callback_data=f'model:{Model.GEMINI}:{GeminiGPTVersion.V2_Pro}'
                        ),
                    ],
                    [
                        InlineKeyboardButton(
                            text=get_localization(language_code).GEMINI_1_ULTRA + (
                                ' ✅' if model == Model.GEMINI and model_version == GeminiGPTVersion.V1_Ultra else ''
                            ),
                            callback_data=f'model:{Model.GEMINI}:{GeminiGPTVersion.V1_Ultra}'
                        ),
                    ],
                    [
                        InlineKeyboardButton(
                            text=get_localization(language_code).ACTION_BACK,
                            callback_data=f'model:{Model.GEMINI}:back'
                        ),
                    ],
                ]
            )
        elif chosen_model == Model.DEEP_SEEK:
            buttons.extend(
                [
                    [
                        InlineKeyboardButton(
                            text=get_localization(language_code).DEEP_SEEK.upper(),
                            callback_data=f'model:{ModelType.TEXT}',
                        ),
                    ],
                    [
                        InlineKeyboardButton(
                            text=get_localization(language_code).DEEP_SEEK_V3 + (
                                ' ✅' if model == Model.DEEP_SEEK and model_version == DeepSeekVersion.V3 else ''
                            ),
                            callback_data=f'model:{Model.DEEP_SEEK}:{DeepSeekVersion.V3}'
                        ),
                    ],
                    [
                        InlineKeyboardButton(
                            text=get_localization(language_code).DEEP_SEEK_R1 + (
                                ' ✅' if model == Model.DEEP_SEEK and model_version == DeepSeekVersion.R1 else ''
                            ),
                            callback_data=f'model:{Model.DEEP_SEEK}:{DeepSeekVersion.R1}'
                        ),
                    ],
                    [
                        InlineKeyboardButton(
                            text=get_localization(language_code).ACTION_BACK,
                            callback_data=f'model:{Model.DEEP_SEEK}:back'
                        ),
                    ],
                ]
            )
        else:
            buttons.extend(
                [
                    [
                        InlineKeyboardButton(
                            text=get_localization(language_code).MODELS_TEXT.upper(),
                            callback_data=f'model:{ModelType.TEXT}',
                        ),
                    ],
                    [
                        InlineKeyboardButton(
                            text=get_localization(language_code).CHAT_GPT,
                            callback_data=f'model:{Model.CHAT_GPT}',
                        ),
                        InlineKeyboardButton(
                            text=get_localization(language_code).CLAUDE,
                            callback_data=f'model:{Model.CLAUDE}',
                        ),
                    ],
                    [
                        InlineKeyboardButton(
                            text=get_localization(language_code).GEMINI,
                            callback_data=f'model:{Model.GEMINI}',
                        ),
                        InlineKeyboardButton(
                            text=get_localization(language_code).DEEP_SEEK,
                            callback_data=f'model:{Model.DEEP_SEEK}'
                        ),
                    ],
                    [
                        InlineKeyboardButton(
                            text=get_localization(language_code).GROK + (
                                ' ✅' if model == Model.GROK else ''
                            ),
                            callback_data=f'model:{Model.GROK}'
                        ),
                        InlineKeyboardButton(
                            text=get_localization(language_code).PERPLEXITY + (
                                ' ✅' if model == Model.PERPLEXITY else ''
                            ),
                            callback_data=f'model:{Model.PERPLEXITY}'
                        ),
                    ],
                    [
                        InlineKeyboardButton(
                            text='⬅️',
                            callback_data='model:back:4'
                        ),
                        InlineKeyboardButton(
                            text='1/5',
                            callback_data='model:page:0'
                        ),
                        InlineKeyboardButton(
                            text='➡️',
                            callback_data='model:next:1'
                        ),
                    ]
                ]
            )
    elif page == 1:
        buttons.extend([
            [
                InlineKeyboardButton(
                    text=get_localization(language_code).MODELS_SUMMARY.upper(),
                    callback_data=f'model:{ModelType.SUMMARY}',
                ),
            ],
            [
                InlineKeyboardButton(
                    text=get_localization(language_code).EIGHTIFY + (
                        ' ✅' if model == Model.EIGHTIFY else ''
                    ),
                    callback_data=f'model:{Model.EIGHTIFY}'
                ),
                InlineKeyboardButton(
                    text=get_localization(language_code).GEMINI_VIDEO + (
                        ' ✅' if model == Model.GEMINI_VIDEO else ''
                    ),
                    callback_data=f'model:{Model.GEMINI_VIDEO}'
                ),
            ],
            [
                InlineKeyboardButton(
                    text='⬅️',
                    callback_data='model:back:0'
                ),
                InlineKeyboardButton(
                    text='2/5',
                    callback_data='model:page:1'
                ),
                InlineKeyboardButton(
                    text='➡️',
                    callback_data='model:next:2'
                ),
            ]
        ])
    elif page == 2:
        if chosen_model == Model.STABLE_DIFFUSION:
            buttons.extend(
                [
                    [
                        InlineKeyboardButton(
                            text=get_localization(language_code).STABLE_DIFFUSION.upper(),
                            callback_data=f'model:{ModelType.IMAGE}',
                        ),
                    ],
                    [
                        InlineKeyboardButton(
                            text=get_localization(language_code).STABLE_DIFFUSION_XL + (
                                ' ✅' if model == Model.STABLE_DIFFUSION and model_version == StableDiffusionVersion.XL else ''
                            ),
                            callback_data=f'model:{Model.STABLE_DIFFUSION}:{StableDiffusionVersion.XL}'
                        ),
                    ],
                    [
                        InlineKeyboardButton(
                            text=get_localization(language_code).STABLE_DIFFUSION_3 + (
                                ' ✅' if model == Model.STABLE_DIFFUSION and model_version == StableDiffusionVersion.V3 else ''
                            ),
                            callback_data=f'model:{Model.STABLE_DIFFUSION}:{StableDiffusionVersion.V3}'
                        ),
                    ],
                    [
                        InlineKeyboardButton(
                            text=get_localization(language_code).ACTION_BACK,
                            callback_data=f'model:{Model.STABLE_DIFFUSION}:back'
                        ),
                    ],
                ]
            )
        elif chosen_model == Model.FLUX:
            buttons.extend(
                [
                    [
                        InlineKeyboardButton(
                            text=get_localization(language_code).FLUX.upper(),
                            callback_data=f'model:{ModelType.IMAGE}',
                        ),
                    ],
                    [
                        InlineKeyboardButton(
                            text=get_localization(language_code).FLUX_1_DEV + (
                                ' ✅' if model == Model.FLUX and model_version == FluxVersion.V1_Dev else ''
                            ),
                            callback_data=f'model:{Model.FLUX}:{FluxVersion.V1_Dev}'
                        ),
                    ],
                    [
                        InlineKeyboardButton(
                            text=get_localization(language_code).FLUX_1_PRO + (
                                ' ✅' if model == Model.FLUX and model_version == FluxVersion.V1_Pro else ''
                            ),
                            callback_data=f'model:{Model.FLUX}:{FluxVersion.V1_Pro}'
                        ),
                    ],
                    [
                        InlineKeyboardButton(
                            text=get_localization(language_code).ACTION_BACK,
                            callback_data=f'model:{Model.FLUX}:back'
                        ),
                    ],
                ]
            )
        else:
            buttons.extend([
                [
                    InlineKeyboardButton(
                        text=get_localization(language_code).MODELS_IMAGE.upper(),
                        callback_data=f'model:{ModelType.IMAGE}',
                    ),
                ],
                [
                    InlineKeyboardButton(
                        text=get_localization(language_code).DALL_E + (' ✅' if model == Model.DALL_E else ''),
                        callback_data=f'model:{Model.DALL_E}'
                    ),
                    InlineKeyboardButton(
                        text=get_localization(language_code).MIDJOURNEY + (' ✅' if model == Model.MIDJOURNEY else ''),
                        callback_data=f'model:{Model.MIDJOURNEY}'
                    ),
                ],
                [
                    InlineKeyboardButton(
                        text=get_localization(language_code).STABLE_DIFFUSION,
                        callback_data=f'model:{Model.STABLE_DIFFUSION}'
                    ),
                    InlineKeyboardButton(
                        text=get_localization(language_code).FLUX,
                        callback_data=f'model:{Model.FLUX}'
                    ),
                ],
                [
                    InlineKeyboardButton(
                        text=get_localization(language_code).LUMA_PHOTON + (
                            ' ✅' if model == Model.LUMA_PHOTON else ''
                        ),
                        callback_data=f'model:{Model.LUMA_PHOTON}'
                    ),
                    InlineKeyboardButton(
                        text=get_localization(language_code).RECRAFT + (
                            ' ✅' if model == Model.RECRAFT else ''
                        ),
                        callback_data=f'model:{Model.RECRAFT}'
                    ),
                ],
                [
                    InlineKeyboardButton(
                        text=get_localization(language_code).FACE_SWAP + (
                            ' ✅' if model == Model.FACE_SWAP else ''
                        ),
                        callback_data=f'model:{Model.FACE_SWAP}'
                    ),
                    InlineKeyboardButton(
                        text=get_localization(language_code).PHOTOSHOP_AI + (
                            ' ✅' if model == Model.PHOTOSHOP_AI else ''
                        ),
                        callback_data=f'model:{Model.PHOTOSHOP_AI}'
                    ),
                ],
                [
                    InlineKeyboardButton(
                        text='⬅️',
                        callback_data='model:back:1'
                    ),
                    InlineKeyboardButton(
                        text='3/5',
                        callback_data='model:page:2'
                    ),
                    InlineKeyboardButton(
                        text='➡️',
                        callback_data='model:next:3'
                    ),
                ]
            ])
    elif page == 3:
        buttons.extend([
            [
                InlineKeyboardButton(
                    text=get_localization(language_code).MODELS_MUSIC.upper(),
                    callback_data=f'model:{ModelType.MUSIC}',
                ),
            ],
            [
                InlineKeyboardButton(
                    text=get_localization(language_code).MUSIC_GEN + (' ✅' if model == Model.MUSIC_GEN else ''),
                    callback_data=f'model:{Model.MUSIC_GEN}'
                ),
                InlineKeyboardButton(
                    text=get_localization(language_code).SUNO + (' ✅' if model == Model.SUNO else ''),
                    callback_data=f'model:{Model.SUNO}'
                ),
            ],
            [
                InlineKeyboardButton(
                    text='⬅️',
                    callback_data='model:back:2'
                ),
                InlineKeyboardButton(
                    text='4/5',
                    callback_data='model:page:3'
                ),
                InlineKeyboardButton(
                    text='➡️',
                    callback_data='model:next:4'
                ),
            ]
        ])
    elif page == 4:
        buttons.extend([
            [
                InlineKeyboardButton(
                    text=get_localization(language_code).MODELS_VIDEO.upper(),
                    callback_data=f'model:{ModelType.VIDEO}',
                ),
            ],
            [
                InlineKeyboardButton(
                    text=get_localization(language_code).KLING + (
                        ' ✅' if model == Model.KLING else ''
                    ),
                    callback_data=f'model:{Model.KLING}'
                ),
                InlineKeyboardButton(
                    text=get_localization(language_code).RUNWAY + (
                        ' ✅' if model == Model.RUNWAY else ''
                    ),
                    callback_data=f'model:{Model.RUNWAY}'
                ),
            ],
            [
                InlineKeyboardButton(
                    text=get_localization(language_code).LUMA_RAY + (
                        ' ✅' if model == Model.LUMA_RAY else ''
                    ),
                    callback_data=f'model:{Model.LUMA_RAY}'
                ),
                InlineKeyboardButton(
                    text=get_localization(language_code).PIKA + (
                        ' ✅' if model == Model.PIKA else ''
                    ),
                    callback_data=f'model:{Model.PIKA}'
                ),
            ],
            [
                InlineKeyboardButton(
                    text='⬅️',
                    callback_data='model:back:3'
                ),
                InlineKeyboardButton(
                    text='5/5',
                    callback_data='model:page:4'
                ),
                InlineKeyboardButton(
                    text='➡️',
                    callback_data='model:next:0'
                ),
            ]
        ])

    return InlineKeyboardMarkup(inline_keyboard=buttons)


def build_switched_to_ai_keyboard(language_code: LanguageCode, model: Model) -> InlineKeyboardMarkup:
    buttons = [
        [
            InlineKeyboardButton(
                text=get_localization(language_code).MODEL_SWITCHED_TO_AI_MANAGE,
                callback_data=f'switched_to_ai:manage:{model}'
            ),
        ],
    ]

    return InlineKeyboardMarkup(inline_keyboard=buttons)


def build_switched_to_ai_selection_keyboard(language_code: LanguageCode, model: Model) -> InlineKeyboardMarkup:
    buttons = [
        [
            InlineKeyboardButton(
                text=get_localization(language_code).MODEL_SWITCHED_TO_AI_SETTINGS,
                callback_data=f'switched_to_ai:settings:{model}'
            ),
        ],
    ]

    if model not in [Model.EIGHTIFY, Model.GEMINI_VIDEO]:
        buttons.append(
            [
                InlineKeyboardButton(
                    text=get_localization(language_code).MODEL_SWITCHED_TO_AI_INFO,
                    callback_data=f'switched_to_ai:info:{model}'
                ),
            ],
        )

    if model not in [
        Model.EIGHTIFY,
        Model.GEMINI_VIDEO,
        Model.FACE_SWAP,
        Model.PHOTOSHOP_AI,
        Model.KLING,
        Model.RUNWAY,
        Model.LUMA_RAY,
        Model.PIKA,
    ]:
        buttons.append(
            [
                InlineKeyboardButton(
                    text=get_localization(language_code).MODEL_SWITCHED_TO_AI_EXAMPLES,
                    callback_data=f'switched_to_ai:examples:{model}'
                )
            ],
        )

    buttons.append(
        [
            InlineKeyboardButton(
                text=get_localization(language_code).ACTION_CLOSE,
                callback_data=f'switched_to_ai:close'
            )
        ],
    )

    return InlineKeyboardMarkup(inline_keyboard=buttons)


def build_model_limit_exceeded_keyboard(language_code: LanguageCode, had_subscription: bool) -> InlineKeyboardMarkup:
    buttons = [
        [
            InlineKeyboardButton(
                text=get_localization(language_code).MODEL_CHANGE_AI,
                callback_data='model_limit_exceeded:change_ai_model'
            )
        ],
        [
            InlineKeyboardButton(
                text=get_localization(language_code).OPEN_BUY_SUBSCRIPTIONS_INFO if had_subscription
                else get_localization(language_code).OPEN_BUY_SUBSCRIPTIONS_TRIAL_INFO,
                callback_data='model_limit_exceeded:open_buy_subscriptions_info'
            )
        ],
        [
            InlineKeyboardButton(
                text=get_localization(language_code).OPEN_BUY_PACKAGES_INFO,
                callback_data='model_limit_exceeded:open_buy_packages_info'
            )
        ],
        [
            InlineKeyboardButton(
                text=get_localization(language_code).OPEN_BONUS_FREE_INFO,
                callback_data='model_limit_exceeded:open_bonus_info'
            )
        ],
    ]

    return InlineKeyboardMarkup(inline_keyboard=buttons)


def build_model_restricted_keyboard(language_code: LanguageCode, had_subscription: bool) -> InlineKeyboardMarkup:
    buttons = [
        [
            InlineKeyboardButton(
                text=get_localization(language_code).MODEL_CHANGE_AI,
                callback_data='model_restricted:change_ai_model'
            )
        ],
        [
            InlineKeyboardButton(
                text=get_localization(language_code).MODEL_SHOW_QUOTA,
                callback_data='model_restricted:show_quota'
            )
        ],
        [
            InlineKeyboardButton(
                text=get_localization(language_code).OPEN_BUY_SUBSCRIPTIONS_INFO if had_subscription
                else get_localization(language_code).OPEN_BUY_SUBSCRIPTIONS_TRIAL_INFO,
                callback_data='model_restricted:open_buy_subscriptions_info'
            )
        ],
        [
            InlineKeyboardButton(
                text=get_localization(language_code).OPEN_BUY_PACKAGES_INFO,
                callback_data='model_restricted:open_buy_packages_info'
            )
        ],
        [
            InlineKeyboardButton(
                text=get_localization(language_code).OPEN_BONUS_FREE_INFO,
                callback_data='model_restricted:open_bonus_info'
            )
        ],
    ]

    return InlineKeyboardMarkup(inline_keyboard=buttons)
