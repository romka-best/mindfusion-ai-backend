from datetime import datetime, timezone
from enum import StrEnum
from typing import Optional

from bot.database.models.common import (
    Currency,
    Model,
    Quota,
    ChatGPTVersion,
    ClaudeGPTVersion,
    GeminiGPTVersion,
    EightifyVersion,
    EightifyFocus,
    EightifyFormat,
    EightifyAmount,
    DALLEVersion,
    DALLEResolution,
    DALLEQuality,
    MidjourneyVersion,
    StableDiffusionVersion,
    FluxVersion,
    FluxSafetyTolerance,
    FaceSwapVersion,
    PhotoshopAIVersion,
    MusicGenVersion,
    SunoVersion,
    AspectRatio,
    SendType,
    RunwayVersion,
    RunwayResolution,
    RunwayDuration,
)
from bot.database.models.subscription import SUBSCRIPTION_FREE_LIMITS
from bot.locales.types import LanguageCode


class UserSettings:
    SHOW_THE_NAME_OF_THE_CHATS = 'show_the_name_of_the_chats'
    SHOW_THE_NAME_OF_THE_ROLES = 'show_the_name_of_the_roles'
    SHOW_USAGE_QUOTA = 'show_usage_quota'
    SHOW_EXAMPLES = 'show_examples'
    TURN_ON_VOICE_MESSAGES = 'turn_on_voice_messages'
    VOICE = 'voice'
    GENDER = 'gender'
    RESOLUTION = 'resolution'
    ASPECT_RATIO = 'aspect_ratio'
    QUALITY = 'quality'
    VERSION = 'version'
    SEND_TYPE = 'send_type'
    SAFETY_TOLERANCE = 'safety_tolerance'
    FOCUS = 'focus'
    FORMAT = 'format'
    AMOUNT = 'amount'
    DURATION = 'duration'


class UserGender(StrEnum):
    MALE = 'MALE'
    FEMALE = 'FEMALE'
    UNSPECIFIED = 'UNSPECIFIED'


class User:
    COLLECTION_NAME = 'users'

    id: str
    first_name: str
    last_name: str
    username: str
    current_chat_id: str
    telegram_chat_id: str
    stripe_id: str
    language_code: str
    interface_language_code: LanguageCode
    is_premium: bool
    is_blocked: bool
    is_banned: bool
    current_model: Model
    currency: Currency
    balance: float
    subscription_id: Optional[str]
    last_subscription_limit_update: datetime
    daily_limits: dict
    additional_usage_quota: dict
    settings: dict
    referred_by: str
    discount: int
    utm: dict
    created_at: datetime
    edited_at: datetime

    DEFAULT_ADDITIONAL_USAGE_QUOTA = {
        Quota.CHAT_GPT4_OMNI_MINI: 0,
        Quota.CHAT_GPT4_OMNI: 0,
        Quota.CHAT_GPT_O_1_MINI: 0,
        Quota.CHAT_GPT_O_1: 0,
        Quota.CLAUDE_3_HAIKU: 0,
        Quota.CLAUDE_3_SONNET: 0,
        Quota.CLAUDE_3_OPUS: 0,
        Quota.GEMINI_1_FLASH: 0,
        Quota.GEMINI_1_PRO: 0,
        Quota.GEMINI_1_ULTRA: 0,
        Quota.EIGHTIFY: 0,
        Quota.ADDITIONAL_CHATS: 0,
        Quota.DALL_E: 0,
        Quota.MIDJOURNEY: 0,
        Quota.STABLE_DIFFUSION: 0,
        Quota.FLUX: 0,
        Quota.FACE_SWAP: 0,
        Quota.PHOTOSHOP_AI: 0,
        Quota.MUSIC_GEN: 0,
        Quota.SUNO: 0,
        Quota.FAST_MESSAGES: False,
        Quota.VOICE_MESSAGES: False,
        Quota.ACCESS_TO_CATALOG: False,
    }

    DEFAULT_SETTINGS = {
        Model.CHAT_GPT: {
            UserSettings.SHOW_THE_NAME_OF_THE_CHATS: False,
            UserSettings.SHOW_THE_NAME_OF_THE_ROLES: False,
            UserSettings.SHOW_USAGE_QUOTA: False,
            UserSettings.TURN_ON_VOICE_MESSAGES: False,
            UserSettings.VOICE: 'alloy',
            UserSettings.VERSION: ChatGPTVersion.V4_Omni_Mini,
            UserSettings.SHOW_EXAMPLES: True,
        },
        Model.CLAUDE: {
            UserSettings.SHOW_THE_NAME_OF_THE_CHATS: False,
            UserSettings.SHOW_THE_NAME_OF_THE_ROLES: False,
            UserSettings.SHOW_USAGE_QUOTA: False,
            UserSettings.TURN_ON_VOICE_MESSAGES: False,
            UserSettings.VOICE: 'alloy',
            UserSettings.VERSION: ClaudeGPTVersion.V3_Sonnet,
            UserSettings.SHOW_EXAMPLES: True,
        },
        Model.GEMINI: {
            UserSettings.SHOW_THE_NAME_OF_THE_CHATS: False,
            UserSettings.SHOW_THE_NAME_OF_THE_ROLES: False,
            UserSettings.SHOW_USAGE_QUOTA: False,
            UserSettings.TURN_ON_VOICE_MESSAGES: False,
            UserSettings.VOICE: 'alloy',
            UserSettings.VERSION: GeminiGPTVersion.V1_Flash,
            UserSettings.SHOW_EXAMPLES: True,
        },
        Model.EIGHTIFY: {
            UserSettings.SHOW_USAGE_QUOTA: False,
            UserSettings.TURN_ON_VOICE_MESSAGES: False,
            UserSettings.VOICE: 'alloy',
            UserSettings.VERSION: EightifyVersion.LATEST,
            UserSettings.FOCUS: EightifyFocus.INSIGHTFUL,
            UserSettings.FORMAT: EightifyFormat.LIST,
            UserSettings.AMOUNT: EightifyAmount.AUTO,
            UserSettings.SHOW_EXAMPLES: False,
        },
        Model.DALL_E: {
            UserSettings.SHOW_USAGE_QUOTA: True,
            UserSettings.VERSION: DALLEVersion.V3,
            UserSettings.RESOLUTION: DALLEResolution.LOW,
            UserSettings.ASPECT_RATIO: AspectRatio.SQUARE,
            UserSettings.QUALITY: DALLEQuality.STANDARD,
            UserSettings.SEND_TYPE: SendType.IMAGE,
            UserSettings.SHOW_EXAMPLES: True,
        },
        Model.MIDJOURNEY: {
            UserSettings.SHOW_USAGE_QUOTA: True,
            UserSettings.VERSION: MidjourneyVersion.V6,
            UserSettings.ASPECT_RATIO: AspectRatio.SQUARE,
            UserSettings.SEND_TYPE: SendType.IMAGE,
            UserSettings.SHOW_EXAMPLES: False,
        },
        Model.STABLE_DIFFUSION: {
            UserSettings.SHOW_USAGE_QUOTA: True,
            UserSettings.VERSION: StableDiffusionVersion.LATEST,
            UserSettings.ASPECT_RATIO: AspectRatio.SQUARE,
            UserSettings.SEND_TYPE: SendType.IMAGE,
            UserSettings.SHOW_EXAMPLES: False,
        },
        Model.FLUX: {
            UserSettings.SHOW_USAGE_QUOTA: True,
            UserSettings.VERSION: FluxVersion.LATEST,
            UserSettings.SAFETY_TOLERANCE: FluxSafetyTolerance.MIDDLE,
            UserSettings.ASPECT_RATIO: AspectRatio.SQUARE,
            UserSettings.SEND_TYPE: SendType.IMAGE,
            UserSettings.SHOW_EXAMPLES: False,
        },
        Model.FACE_SWAP: {
            UserSettings.SHOW_USAGE_QUOTA: True,
            UserSettings.VERSION: FaceSwapVersion.LATEST,
            UserSettings.ASPECT_RATIO: AspectRatio.CUSTOM,
            UserSettings.SEND_TYPE: SendType.IMAGE,
            UserSettings.GENDER: UserGender.UNSPECIFIED,
            UserSettings.SHOW_EXAMPLES: False,
        },
        Model.PHOTOSHOP_AI: {
            UserSettings.SHOW_USAGE_QUOTA: False,
            UserSettings.VERSION: PhotoshopAIVersion.LATEST,
            UserSettings.ASPECT_RATIO: AspectRatio.CUSTOM,
            UserSettings.SEND_TYPE: SendType.DOCUMENT,
            UserSettings.SHOW_EXAMPLES: False,
        },
        Model.MUSIC_GEN: {
            UserSettings.SHOW_USAGE_QUOTA: True,
            UserSettings.VERSION: MusicGenVersion.LATEST,
            UserSettings.SHOW_EXAMPLES: True,
        },
        Model.SUNO: {
            UserSettings.SHOW_USAGE_QUOTA: True,
            UserSettings.SEND_TYPE: SendType.VIDEO,
            UserSettings.VERSION: SunoVersion.V4,
            UserSettings.SHOW_EXAMPLES: False,
        },
        Model.RUNWAY: {
            UserSettings.SHOW_USAGE_QUOTA: True,
            UserSettings.SEND_TYPE: SendType.VIDEO,
            UserSettings.VERSION: RunwayVersion.V3_Alpha_Turbo,
            UserSettings.RESOLUTION: RunwayResolution.LANDSCAPE,
            UserSettings.ASPECT_RATIO: AspectRatio.LANDSCAPE,
            UserSettings.DURATION: RunwayDuration.SECONDS_5,
            UserSettings.SHOW_EXAMPLES: False,
        },
    }

    def __init__(
        self,
        id: str,
        first_name: str,
        last_name: str,
        username: str,
        current_chat_id: str,
        telegram_chat_id: str,
        stripe_id: str,
        language_code='en',
        interface_language_code=LanguageCode.EN,
        is_premium=False,
        is_blocked=False,
        is_banned=False,
        current_model=Model.CHAT_GPT,
        currency=Currency.RUB,
        balance=0,
        subscription_id='',
        last_subscription_limit_update=None,
        daily_limits=None,
        additional_usage_quota=None,
        settings=None,
        referred_by=None,
        discount=0,
        utm=None,
        created_at=None,
        edited_at=None,
        **kwargs,
    ):
        self.id = str(id)
        self.first_name = first_name
        self.last_name = last_name
        self.username = username
        self.language_code = language_code
        self.interface_language_code = interface_language_code
        self.is_premium = is_premium
        self.is_blocked = is_blocked
        self.is_banned = is_banned
        self.current_model = current_model
        self.currency = currency
        self.balance = balance
        self.subscription_id = subscription_id
        self.current_chat_id = str(current_chat_id)
        self.telegram_chat_id = str(telegram_chat_id)
        self.stripe_id = stripe_id
        self.daily_limits = daily_limits if daily_limits is not None else SUBSCRIPTION_FREE_LIMITS
        self.additional_usage_quota = additional_usage_quota if additional_usage_quota is not None \
            else self.DEFAULT_ADDITIONAL_USAGE_QUOTA
        self.settings = settings if settings is not None else self.DEFAULT_SETTINGS
        self.referred_by = referred_by
        self.discount = discount
        self.utm = utm if utm is not None else {}

        current_time = datetime.now(timezone.utc)
        self.last_subscription_limit_update = last_subscription_limit_update \
            if last_subscription_limit_update is not None else current_time
        self.created_at = created_at if created_at is not None else current_time
        self.edited_at = edited_at if edited_at is not None else current_time

    def to_dict(self):
        return vars(self)
