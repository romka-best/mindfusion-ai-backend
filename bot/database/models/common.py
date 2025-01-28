from enum import StrEnum


class Currency:
    RUB = 'RUB'
    USD = 'USD'
    XTR = 'XTR'

    SYMBOLS = {
        RUB: '₽',
        USD: '$',
        XTR: '⭐️',
    }


class Model:
    CHAT_GPT = 'chat-gpt'
    CLAUDE = 'claude'
    GEMINI = 'gemini'
    GROK = 'grok'
    DEEP_SEEK = 'deep-seek'
    PERPLEXITY = 'perplexity'
    EIGHTIFY = 'eightify'
    GEMINI_VIDEO = 'gemini-video'
    DALL_E = 'dall-e'
    MIDJOURNEY = 'midjourney'
    STABLE_DIFFUSION = 'stable-diffusion'
    FLUX = 'flux'
    LUMA_PHOTON = 'luma-photon'
    RECRAFT = 'recraft'
    FACE_SWAP = 'face-swap'
    PHOTOSHOP_AI = 'photoshop-ai'
    MUSIC_GEN = 'music-gen'
    SUNO = 'suno'
    KLING = 'kling'
    RUNWAY = 'runway'
    LUMA_RAY = 'luma-ray'
    PIKA = 'pika'


class ModelType(StrEnum):
    TEXT = 'TEXT'
    SUMMARY = 'SUMMARY'
    IMAGE = 'IMAGE'
    MUSIC = 'MUSIC'
    VIDEO = 'VIDEO'


class Quota:
    CHAT_GPT4_OMNI = 'gpt4_omni'
    CHAT_GPT4_OMNI_MINI = 'gpt4_omni_mini'
    CHAT_GPT_O_1_MINI = 'o1_mini'
    CHAT_GPT_O_1 = 'o1'
    CLAUDE_3_HAIKU = 'claude_3_haiku'
    CLAUDE_3_SONNET = 'claude_3_sonnet'
    CLAUDE_3_OPUS = 'claude_3_opus'
    GEMINI_2_FLASH = 'gemini_2_flash'
    GEMINI_1_PRO = 'gemini_1_pro'
    GEMINI_1_ULTRA = 'gemini_1_ultra'
    GROK_2 = 'grok_2'
    DEEP_SEEK_V3 = 'deep_seek_v3'
    DEEP_SEEK_R1 = 'deep_seek_r1'
    PERPLEXITY = 'perplexity'
    EIGHTIFY = 'eightify'
    GEMINI_VIDEO = 'gemini_video'
    DALL_E = 'dall_e'
    MIDJOURNEY = 'midjourney'
    STABLE_DIFFUSION_XL = 'stable_diffusion_xl'
    STABLE_DIFFUSION_3 = 'stable_diffusion_3'
    FLUX_1_DEV = 'flux_1_dev'
    FLUX_1_PRO = 'flux_1_pro'
    LUMA_PHOTON = 'luma_photon'
    RECRAFT = 'recraft'
    FACE_SWAP = 'face_swap'
    PHOTOSHOP_AI = 'photoshop_ai'
    MUSIC_GEN = 'music_gen'
    SUNO = 'suno'
    KLING = 'kling'
    RUNWAY = 'runway'
    LUMA_RAY = 'luma_ray'
    PIKA = 'pika'
    WORK_WITH_FILES = 'work_with_files'
    FAST_MESSAGES = 'fast_messages'
    VOICE_MESSAGES = 'voice_messages'
    ACCESS_TO_CATALOG = 'access_to_catalog'


class ChatGPTVersion:
    V4_Omni = 'gpt-4o'
    V4_Omni_Mini = 'gpt-4o-mini'
    V1_O_Mini = 'o1-mini'
    V1_O = 'o1'


class ClaudeGPTVersion:
    V3_Haiku = 'claude-3-5-haiku-latest'
    V3_Sonnet = 'claude-3-5-sonnet-latest'
    V3_Opus = 'claude-3-opus-latest'


class GeminiGPTVersion:
    V2_Flash = 'gemini-2.0-flash-exp'
    V1_Pro = 'gemini-1.5-pro'
    V1_Ultra = 'gemini-1.0-ultra'


class GrokGPTVersion:
    V2 = 'grok-2-vision-1212'


class DeepSeekVersion:
    V3 = 'deepseek-chat'
    R1 = 'deepseek-reasoner'


class PerplexityGPTVersion:
    Sonar = 'sonar'
    Sonar_Pro = 'sonar-pro'


class EightifyVersion:
    LATEST = 'LATEST'


class GeminiVideoVersion:
    LATEST = 'LATEST'


class VideoSummaryFocus:
    INSIGHTFUL = 'insightful'
    FUNNY = 'funny'
    ACTIONABLE = 'actionable'
    CONTROVERSIAL = 'controversial'


class VideoSummaryFormat:
    LIST = 'list'
    FAQ = 'faq'


class VideoSummaryAmount:
    AUTO = 'auto'
    SHORT = 'short'
    DETAILED = 'detailed'


class DALLEVersion:
    V3 = 'dall-e-3'


class DALLEResolution:
    LOW = '1024x1024'
    MEDIUM = '1024x1792'
    HIGH = '1792x1024'


class DALLEQuality:
    STANDARD = 'standard'
    HD = 'hd'


class MidjourneyVersion:
    V5 = '5.2'
    V6 = '6.1'


class MidjourneyAction:
    PAYMENT = 'payment'
    IMAGINE = 'imagine'
    UPSCALE = 'upscale'
    # UPSCALE_TWO = 'upscale_2x'
    # UPSCALE_FOUR = 'upscale_4x'
    # UPSCALE_SUBTLE = 'upscale_subtle'
    # UPSCALE_CREATIVE = 'upscale_creative'
    VARIATION = 'variation'
    # VARY_SUBTLE = 'vary_subtle'
    # VARY_STRONG = 'vary_strong'
    # ZOOM_OUT_ONE_AND_HALF = 'zoom_out_1.5x'
    # ZOOM_OUT_TWO = 'zoom_out_2x'
    REROLL = 'reroll'


class StableDiffusionVersion:
    XL = 'xl'
    V3 = '3.5'


class FluxVersion:
    V1_Dev = 'flux-1-dev'
    V1_Pro = 'flux-1-pro'


class FluxSafetyTolerance:
    STRICT = 1
    MIDDLE = 3
    PERMISSIVE = 6


class LumaPhotonVersion:
    V1 = 'photon-1'


class RecraftVersion:
    V3 = 'recraftv3'


class FaceSwapVersion:
    LATEST = 'LATEST'


class PhotoshopAIVersion:
    LATEST = 'LATEST'


class PhotoshopAIAction:
    UPSCALE = 'upscale'
    RESTORATION = 'restoration'
    COLORIZATION = 'colorization'
    REMOVAL_BACKGROUND = 'removal_background'


class MusicGenVersion:
    LATEST = 'LATEST'


class SunoVersion:
    V3 = 'chirp-v3-5'
    V4 = 'chirp-v4'


class SunoMode:
    SIMPLE = 'SIMPLE'
    CUSTOM = 'CUSTOM'


class KlingVersion:
    V1 = '1.6'


class KlingMode:
    STANDARD = 'std'
    PRO = 'pro'


class KlingDuration:
    SECONDS_5 = 5
    SECONDS_10 = 10


class RunwayVersion:
    V3_Alpha_Turbo = 'gen3a_turbo'


class RunwayDuration:
    SECONDS_5 = 5
    SECONDS_10 = 10


class RunwayResolution:
    LANDSCAPE = '1280:768'
    PORTRAIT = '768:1280'


class LumaRayVersion:
    V2 = 'ray-2'


class LumaRayDuration:
    SECONDS_5 = 5
    SECONDS_9 = 9


class LumaRayQuality:
    SD = '540p'
    HD = '720p'


class PikaVersion:
    V2 = '2.0'


class AspectRatio:
    SQUARE = '1:1'
    LANDSCAPE = '16:9'
    PORTRAIT = '9:16'
    CINEMASCOPE_HORIZONTAL = '21:9'
    CINEMASCOPE_VERTICAL = '9:21'
    STANDARD_HORIZONTAL = '3:2'
    STANDARD_VERTICAL = '2:3'
    BANNER_HORIZONTAL = '5:4'
    BANNER_VERTICAL = '4:5'
    CLASSIC_HORIZONTAL = '4:3'
    CLASSIC_VERTICAL = '3:4'
    CUSTOM = 'CUSTOM'


class SendType:
    TEXT = 'TEXT'
    IMAGE = 'IMAGE'
    DOCUMENT = 'DOCUMENT'
    AUDIO = 'AUDIO'
    VIDEO = 'VIDEO'


class PaymentType:
    SUBSCRIPTION = 'SUBSCRIPTION'
    PACKAGE = 'PACKAGE'
    CART = 'CART'


class PaymentMethod:
    YOOKASSA = 'YOOKASSA'
    PAY_SELECTION = 'PAY_SELECTION'
    STRIPE = 'STRIPE'
    TELEGRAM_STARS = 'TELEGRAM_STARS'
    CRYPTO = 'CRYPTO'
    GIFT = 'GIFT'

    _CURRENCY_MAP = {
        YOOKASSA: Currency.RUB,
        PAY_SELECTION: Currency.USD,
        STRIPE: Currency.USD,
        TELEGRAM_STARS: Currency.XTR,
        CRYPTO: None,
        GIFT: None,
    }

    @staticmethod
    def get_currency(payment_method: str):
        return PaymentMethod._CURRENCY_MAP.get(payment_method, Currency.USD)


class UTM:
    SOURCE = 'source'
    MEDIUM = 'medium'
    CAMPAIGN = 'campaign'
    TERM = 'term'
    CONTENT = 'content'
