from typing import Optional

from bot.database.models.common import (
    Model,
    ChatGPTVersion,
    ClaudeGPTVersion,
    GeminiGPTVersion,
    DeepSeekVersion,
    StableDiffusionVersion,
    FluxVersion,
)
from bot.locales.main import get_localization
from bot.locales.types import LanguageCode


def get_info_by_model(
    model: Model,
    model_version: Optional[
        ChatGPTVersion | ClaudeGPTVersion | GeminiGPTVersion | DeepSeekVersion | StableDiffusionVersion | FluxVersion
    ],
    language_code: LanguageCode,
):
    info = None

    if model == Model.CHAT_GPT:
        if model_version == ChatGPTVersion.V4_Omni_Mini:
            info = get_localization(language_code).INFO_CHAT_GPT_4_OMNI_MINI
        elif model_version == ChatGPTVersion.V4_Omni:
            info = get_localization(language_code).INFO_CHAT_GPT_4_OMNI
        elif model_version == ChatGPTVersion.V3_O_Mini:
            info = get_localization(language_code).INFO_CHAT_GPT_O_3_MINI
        elif model_version == ChatGPTVersion.V1_O:
            info = get_localization(language_code).INFO_CHAT_GPT_O_1
    elif model == Model.CLAUDE:
        if model_version == ClaudeGPTVersion.V3_Haiku:
            info = get_localization(language_code).INFO_CLAUDE_3_HAIKU
        elif model_version == ClaudeGPTVersion.V3_Sonnet:
            info = get_localization(language_code).INFO_CLAUDE_3_SONNET
        elif model_version == ClaudeGPTVersion.V3_Opus:
            info = get_localization(language_code).INFO_CLAUDE_3_OPUS
    elif model == Model.GEMINI:
        if model_version == GeminiGPTVersion.V2_Flash:
            info = get_localization(language_code).INFO_GEMINI_2_FLASH
        elif model_version == GeminiGPTVersion.V1_Pro:
            info = get_localization(language_code).INFO_GEMINI_1_PRO
        elif model_version == GeminiGPTVersion.V1_Ultra:
            info = get_localization(language_code).INFO_GEMINI_1_ULTRA
    elif model == Model.DEEP_SEEK:
        if model_version == DeepSeekVersion.V3:
            info = get_localization(language_code).INFO_DEEP_SEEK_V3
        elif model_version == DeepSeekVersion.R1:
            info = get_localization(language_code).INFO_DEEP_SEEK_R1
    elif model == Model.GROK:
        info = get_localization(language_code).INFO_GROK
    elif model == Model.PERPLEXITY:
        info = get_localization(language_code).INFO_PERPLEXITY
    elif model == Model.DALL_E:
        info = get_localization(language_code).INFO_DALL_E
    elif model == Model.MIDJOURNEY:
        info = get_localization(language_code).INFO_MIDJOURNEY
    elif model == Model.STABLE_DIFFUSION:
        if model_version == StableDiffusionVersion.XL:
            info = get_localization(language_code).INFO_STABLE_DIFFUSION_XL
        elif model_version == StableDiffusionVersion.V3:
            info = get_localization(language_code).INFO_STABLE_DIFFUSION_3
    elif model == Model.FLUX:
        if model_version == FluxVersion.V1_Dev:
            info = get_localization(language_code).INFO_FLUX_1_DEV
        elif model_version == FluxVersion.V1_Pro:
            info = get_localization(language_code).INFO_FLUX_1_PRO
    elif model == Model.LUMA_PHOTON:
        info = get_localization(language_code).INFO_LUMA_PHOTON
    elif model == Model.RECRAFT:
        info = get_localization(language_code).INFO_RECRAFT
    elif model == Model.FACE_SWAP:
        info = get_localization(language_code).INFO_FACE_SWAP
    elif model == Model.PHOTOSHOP_AI:
        info = get_localization(language_code).INFO_PHOTOSHOP_AI
    elif model == Model.MUSIC_GEN:
        info = get_localization(language_code).INFO_MUSIC_GEN
    elif model == Model.SUNO:
        info = get_localization(language_code).INFO_SUNO
    elif model == Model.KLING:
        info = get_localization(language_code).INFO_KLING
    elif model == Model.RUNWAY:
        info = get_localization(language_code).INFO_RUNWAY
    elif model == Model.LUMA_RAY:
        info = get_localization(language_code).INFO_LUMA_RAY
    elif model == Model.PIKA:
        info = get_localization(language_code).INFO_PIKA

    return info
