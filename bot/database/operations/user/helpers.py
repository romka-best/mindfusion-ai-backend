from datetime import datetime, timezone
from typing import Optional

from aiogram.types import User as TelegramUser

from bot.database.models.common import (
    Model,
    Quota,
    Currency,
    ChatGPTVersion,
    ClaudeGPTVersion,
    GeminiGPTVersion,
    DeepSeekVersion,
    StableDiffusionVersion,
    FluxVersion,
)
from bot.database.models.subscription import SUBSCRIPTION_FREE_LIMITS
from bot.database.models.user import User, UserSettings
from bot.locales.types import LanguageCode


def create_user_object(
    telegram_user: TelegramUser,
    user_data: dict,
    chat_id: str,
    telegram_chat_id: str,
    stripe_id: str,
    referred_by: Optional[str],
    is_referred_by_user=False,
    quota=Quota.CHAT_GPT4_OMNI_MINI,
    utm=None,
    discount=0,
) -> User:
    default_model = Model.CHAT_GPT
    default_settings = User.DEFAULT_SETTINGS
    default_additional_quota = User.DEFAULT_ADDITIONAL_USAGE_QUOTA
    if quota in [Quota.CHAT_GPT4_OMNI_MINI, Quota.CHAT_GPT4_OMNI, Quota.CHAT_GPT_O_1_MINI, Quota.CHAT_GPT_O_1]:
        default_model = Model.CHAT_GPT
        if quota == Quota.CHAT_GPT4_OMNI_MINI:
            default_settings[default_model][UserSettings.VERSION] = ChatGPTVersion.V4_Omni_Mini
            default_additional_quota[Quota.CHAT_GPT4_OMNI_MINI] = 10
        elif quota == Quota.CHAT_GPT4_OMNI:
            default_settings[default_model][UserSettings.VERSION] = ChatGPTVersion.V4_Omni
            default_additional_quota[Quota.CHAT_GPT4_OMNI] = 10
        elif quota == Quota.CHAT_GPT_O_1_MINI:
            default_settings[default_model][UserSettings.VERSION] = ChatGPTVersion.V1_O_Mini
            default_additional_quota[Quota.CHAT_GPT_O_1_MINI] = 10
        elif quota == Quota.CHAT_GPT_O_1:
            default_settings[default_model][UserSettings.VERSION] = ChatGPTVersion.V1_O
            default_additional_quota[Quota.CHAT_GPT_O_1] = 10
    elif quota in [Quota.CLAUDE_3_HAIKU, Quota.CLAUDE_3_SONNET, Quota.CLAUDE_3_OPUS]:
        default_model = Model.CLAUDE
        if quota == Quota.CLAUDE_3_HAIKU:
            default_settings[default_model][UserSettings.VERSION] = ClaudeGPTVersion.V3_Haiku
            default_additional_quota[Quota.CLAUDE_3_HAIKU] = 10
        elif quota == Quota.CLAUDE_3_SONNET:
            default_settings[default_model][UserSettings.VERSION] = ClaudeGPTVersion.V3_Sonnet
            default_additional_quota[Quota.CLAUDE_3_SONNET] = 10
        elif quota == Quota.CLAUDE_3_OPUS:
            default_settings[default_model][UserSettings.VERSION] = ClaudeGPTVersion.V3_Opus
            default_additional_quota[Quota.CLAUDE_3_OPUS] = 10
    elif quota in [Quota.GEMINI_2_FLASH, Quota.GEMINI_1_PRO, Quota.GEMINI_1_ULTRA]:
        default_model = Model.GEMINI
        if quota == Quota.GEMINI_2_FLASH:
            default_settings[default_model][UserSettings.VERSION] = GeminiGPTVersion.V2_Flash
            default_additional_quota[Quota.GEMINI_2_FLASH] = 10
        elif quota == Quota.GEMINI_1_PRO:
            default_settings[default_model][UserSettings.VERSION] = GeminiGPTVersion.V1_Pro
            default_additional_quota[Quota.GEMINI_1_PRO] = 10
        elif quota == Quota.GEMINI_1_ULTRA:
            default_settings[default_model][UserSettings.VERSION] = GeminiGPTVersion.V1_Ultra
            default_additional_quota[Quota.GEMINI_1_ULTRA] = 10
    elif quota == Quota.GROK_2:
        default_model = Model.GROK
        default_additional_quota[Quota.GROK_2] = 10
    elif quota in [Quota.DEEP_SEEK_V3, Quota.DEEP_SEEK_R1]:
        default_model = Model.DEEP_SEEK
        if quota == Quota.DEEP_SEEK_V3:
            default_settings[default_model][UserSettings.VERSION] = DeepSeekVersion.V3
            default_additional_quota[Quota.DEEP_SEEK_V3] = 10
        elif quota == Quota.DEEP_SEEK_R1:
            default_settings[default_model][UserSettings.VERSION] = DeepSeekVersion.R1
            default_additional_quota[Quota.DEEP_SEEK_R1] = 10
    elif quota == Quota.PERPLEXITY:
        default_model = Model.PERPLEXITY
        default_additional_quota[Quota.PERPLEXITY] = 10
    elif quota == Quota.EIGHTIFY:
        default_model = Model.EIGHTIFY
        default_additional_quota[Quota.EIGHTIFY] = 10
    elif quota == Quota.GEMINI_VIDEO:
        default_model = Model.GEMINI_VIDEO
        default_additional_quota[Quota.GEMINI_VIDEO] = 10
    elif quota == Quota.DALL_E:
        default_model = Model.DALL_E
        default_additional_quota[Quota.DALL_E] = 5
    elif quota == Quota.MIDJOURNEY:
        default_model = Model.MIDJOURNEY
        default_additional_quota[Quota.MIDJOURNEY] = 5
    elif quota in [Quota.STABLE_DIFFUSION_XL, Quota.STABLE_DIFFUSION_3]:
        default_model = Model.STABLE_DIFFUSION
        if quota == Quota.STABLE_DIFFUSION_XL:
            default_settings[default_model][UserSettings.VERSION] = StableDiffusionVersion.XL
            default_additional_quota[Quota.STABLE_DIFFUSION_XL] = 10
        elif quota == Quota.STABLE_DIFFUSION_3:
            default_settings[default_model][UserSettings.VERSION] = StableDiffusionVersion.V3
            default_additional_quota[Quota.STABLE_DIFFUSION_3] = 5
    elif quota in [Quota.FLUX_1_DEV, Quota.FLUX_1_PRO]:
        default_model = Model.FLUX
        if quota == Quota.FLUX_1_DEV:
            default_settings[default_model][UserSettings.VERSION] = FluxVersion.V1_Dev
            default_additional_quota[Quota.FLUX_1_DEV] = 10
        elif quota == Quota.FLUX_1_PRO:
            default_settings[default_model][UserSettings.VERSION] = FluxVersion.V1_Pro
            default_additional_quota[Quota.FLUX_1_PRO] = 5
    elif quota == Quota.LUMA_PHOTON:
        default_model = Model.LUMA_PHOTON
        default_additional_quota[Quota.LUMA_PHOTON] = 10
    elif quota == Quota.RECRAFT:
        default_model = Model.RECRAFT
        default_additional_quota[Quota.RECRAFT] = 5
    elif quota == Quota.FACE_SWAP:
        default_model = Model.FACE_SWAP
        default_additional_quota[Quota.FACE_SWAP] = 5
    elif quota == Quota.PHOTOSHOP_AI:
        default_model = Model.PHOTOSHOP_AI
        default_additional_quota[Quota.PHOTOSHOP_AI] = 5
    elif quota == Quota.MUSIC_GEN:
        default_model = Model.MUSIC_GEN
        default_additional_quota[Quota.MUSIC_GEN] = 6
    elif quota == Quota.SUNO:
        default_model = Model.SUNO
        default_additional_quota[Quota.SUNO] = 6
    elif quota == Quota.KLING:
        default_model = Model.KLING
        default_additional_quota[Quota.KLING] = 1
    elif quota == Quota.RUNWAY:
        default_model = Model.RUNWAY
        default_additional_quota[Quota.RUNWAY] = 1
    elif quota == Quota.LUMA_RAY:
        default_model = Model.LUMA_RAY
        default_additional_quota[Quota.LUMA_RAY] = 1
    elif quota == Quota.PIKA:
        default_model = Model.PIKA
        default_additional_quota[Quota.PIKA] = 1

    interface_language_code = LanguageCode.EN
    if telegram_user.language_code == LanguageCode.RU:
        interface_language_code = LanguageCode.RU
    elif telegram_user.language_code == LanguageCode.ES:
        interface_language_code = LanguageCode.ES
    elif telegram_user.language_code == LanguageCode.HI:
        interface_language_code = LanguageCode.HI

    return User(
        id=str(telegram_user.id),
        first_name=telegram_user.first_name,
        last_name=telegram_user.last_name or '',
        username=telegram_user.username,
        current_chat_id=chat_id,
        telegram_chat_id=telegram_chat_id,
        stripe_id=stripe_id,
        language_code=telegram_user.language_code,
        interface_language_code=user_data.get(
            'interface_language_code',
            interface_language_code,
        ),
        is_premium=telegram_user.is_premium or False,
        is_blocked=False,
        is_banned=False,
        current_model=user_data.get('current_model', default_model),
        currency=user_data.get(
            'currency',
            Currency.RUB if telegram_user.language_code == LanguageCode.RU else Currency.USD
        ),
        balance=user_data.get('balance', 25 if is_referred_by_user else 0),
        subscription_id=user_data.get('subscription_id', ''),
        last_subscription_limit_update=user_data.get('last_subscription_limit_update', datetime.now(timezone.utc)),
        daily_limits=user_data.get('daily_limits', SUBSCRIPTION_FREE_LIMITS),
        additional_usage_quota=user_data.get('additional_usage_quota', default_additional_quota),
        settings=user_data.get('settings', default_settings),
        referred_by=user_data.get('referred_by', referred_by),
        discount=user_data.get('discount', discount),
        utm=utm,
        created_at=user_data.get('created_at', None),
        edited_at=user_data.get('edited_at', None),
    )
