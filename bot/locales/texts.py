from typing import Protocol, Union

from bot.database.models.common import (
    Model,
    ModelType,
    Currency,
    PaymentMethod,
    VideoSummaryFocus,
    VideoSummaryFormat,
    VideoSummaryAmount,
)
from bot.database.models.package import Package, PackageStatus
from bot.database.models.product import Product, ProductCategory
from bot.database.models.prompt import Prompt
from bot.database.models.subscription import Subscription, SubscriptionStatus
from bot.locales.types import LanguageCode


class Texts(Protocol):
    # Action
    ACTION_BACK: str
    ACTION_CLOSE: str
    ACTION_CANCEL: str
    ACTION_APPROVE: str
    ACTION_DENY: str
    ACTION_TO_OTHER_MODELS: str
    ACTION_TO_OTHER_TYPE_MODELS: str

    # Additional Bot
    @staticmethod
    def additional_bot_info(link: str) -> str:
        raise NotImplementedError

    # Bonus
    @staticmethod
    def bonus_info(balance: int) -> str:
        raise NotImplementedError

    @staticmethod
    def bonus_info_earn(user_id: str, referred_count: int, feedback_count: int, play_count: int):
        raise NotImplementedError

    @staticmethod
    def bonus_info_spend(balance: int):
        raise NotImplementedError

    BONUS_EARN: str
    BONUS_SPEND: str
    BONUS_ACTIVATED_SUCCESSFUL: str
    BONUS_INVITE_FRIEND: str
    BONUS_REFERRAL_SUCCESS: str
    BONUS_REFERRAL_LIMIT_ERROR: str

    @staticmethod
    def bonus_referral_link(user_id: str, is_share: bool) -> str:
        if is_share:
            return f'https://t.me/share/url?url=https://t.me/GPTsTurboBot?start=r-{user_id}'
        return f'https://t.me/GPTsTurboBot?start=r-{user_id}'

    BONUS_LEAVE_FEEDBACK: str
    BONUS_CASH_OUT: str
    BONUS_PLAY: str
    BONUS_PLAY_GAME: str
    BONUS_PLAY_GAME_CHOOSE: str
    BONUS_PLAY_BOWLING_GAME: str
    BONUS_PLAY_BOWLING_GAME_INFO: str
    BONUS_PLAY_SOCCER_GAME: str
    BONUS_PLAY_SOCCER_GAME_INFO: str
    BONUS_PLAY_BASKETBALL_GAME: str
    BONUS_PLAY_BASKETBALL_GAME_INFO: str
    BONUS_PLAY_DARTS_GAME: str
    BONUS_PLAY_DARTS_GAME_INFO: str
    BONUS_PLAY_DICE_GAME: str
    BONUS_PLAY_DICE_GAME_INFO: str
    BONUS_PLAY_DICE_GAME_CHOOSE_1 = '🎲 1️⃣'
    BONUS_PLAY_DICE_GAME_CHOOSE_2 = '🎲 2️⃣'
    BONUS_PLAY_DICE_GAME_CHOOSE_3 = '🎲 3️⃣'
    BONUS_PLAY_DICE_GAME_CHOOSE_4 = '🎲 4️⃣'
    BONUS_PLAY_DICE_GAME_CHOOSE_5 = '🎲 5️⃣'
    BONUS_PLAY_DICE_GAME_CHOOSE_6 = '🎲 6️⃣'
    BONUS_PLAY_CASINO_GAME: str
    BONUS_PLAY_CASINO_GAME_INFO: str
    BONUS_PLAY_GAME_WON: str
    BONUS_PLAY_GAME_LOST: str

    @staticmethod
    def bonus_play_game_reached_limit():
        raise NotImplementedError

    # Catalog
    CATALOG_INFO: str
    CATALOG_MANAGE: str
    CATALOG_DIGITAL_EMPLOYEES: str
    CATALOG_DIGITAL_EMPLOYEES_INFO: str
    CATALOG_DIGITAL_EMPLOYEES_FORBIDDEN_ERROR: str
    CATALOG_PROMPTS: str
    CATALOG_PROMPTS_CHOOSE_MODEL_TYPE: str
    CATALOG_PROMPTS_CHOOSE_CATEGORY: str
    CATALOG_PROMPTS_CHOOSE_SUBCATEGORY: str

    @staticmethod
    def catalog_prompts_choose_prompt(prompts: list[Prompt]):
        raise NotImplementedError

    @staticmethod
    def catalog_prompts_info_prompt(prompt: Prompt, products: list[Product]):
        raise NotImplementedError

    @staticmethod
    def catalog_prompts_examples(products: list[Product]):
        raise NotImplementedError

    CATALOG_PROMPTS_GET_SHORT_PROMPT: str
    CATALOG_PROMPTS_GET_LONG_PROMPT: str
    CATALOG_PROMPTS_GET_EXAMPLES: str
    CATALOG_PROMPTS_COPY: str

    # Chats
    @staticmethod
    def chat_info(current_chat_name: str, total_chats: int) -> str:
        raise NotImplementedError

    CHAT_DEFAULT_TITLE: str
    CHAT_MANAGE: str
    CHAT_CREATE: str
    CHAT_CREATE_SUCCESS: str
    CHAT_TYPE_TITLE: str
    CHAT_SWITCH: str
    CHAT_SWITCH_FORBIDDEN_ERROR: str
    CHAT_SWITCH_SUCCESS: str
    CHAT_RESET: str
    CHAT_RESET_WARNING: str
    CHAT_RESET_SUCCESS: str
    CHAT_DELETE: str
    CHAT_DELETE_FORBIDDEN_ERROR: str
    CHAT_DELETE_SUCCESS: str

    # ChatGPT
    CHAT_GPT = '💭 ChatGPT'
    CHAT_GPT_3_TURBO = '✉️ ChatGPT 3.5 Turbo'
    CHAT_GPT_4_OMNI_MINI = '✉️ ChatGPT 4.0 Omni Mini'
    CHAT_GPT_4_TURBO = '🧠 ChatGPT 4.0 Turbo'
    CHAT_GPT_4_OMNI = '💥 ChatGPT 4.0 Omni'
    CHAT_GPT_O_1_MINI = '🧩 ChatGPT o1-mini'
    CHAT_GPT_O_1 = '🧪 ChatGPT o1'

    # Claude
    CLAUDE = '📄 Claude'
    CLAUDE_3_HAIKU = '📜 Claude 3.5 Haiku'
    CLAUDE_3_SONNET = '💫 Claude 3.5 Sonnet'
    CLAUDE_3_OPUS = '🚀 Claude 3.0 Opus'

    # DALL-E
    DALL_E = '👨‍🎨 DALL-E'

    # Eightify
    EIGHTIFY = '👀 YouTube Summary'
    EIGHTIFY_INFO: str
    EIGHTIFY_VALUE_ERROR: str
    EIGHTIFY_VIDEO_ERROR: str

    # Errors
    ERROR: str
    ERROR_NETWORK: str
    ERROR_PROMPT_REQUIRED: str
    ERROR_PROMPT_TOO_LONG: str
    ERROR_REQUEST_FORBIDDEN: str
    ERROR_PHOTO_FORBIDDEN: str
    ERROR_PHOTO_REQUIRED: str
    ERROR_ALBUM_FORBIDDEN: str
    ERROR_VIDEO_FORBIDDEN: str
    ERROR_DOCUMENT_FORBIDDEN: str
    ERROR_STICKER_FORBIDDEN: str
    ERROR_SERVER_OVERLOADED: str
    ERROR_FILE_TOO_BIG: str
    ERROR_IS_NOT_NUMBER: str

    # Examples
    EXAMPLE_INFO: str

    @staticmethod
    def example_text_model(model: str):
        raise NotImplementedError

    @staticmethod
    def example_image_model(model: str):
        raise NotImplementedError

    # FaceSwap
    FACE_SWAP = '📷️ FaceSwap'
    FACE_SWAP_INFO: str
    FACE_SWAP_CHOOSE_PHOTO: str
    FACE_SWAP_CHOOSE_PHOTO_INFO: str
    FACE_SWAP_CHOOSE_PROMPT: str
    FACE_SWAP_CHOOSE_PROMPT_INFO: str
    FACE_SWAP_CHOOSE_PACKAGE: str
    FACE_SWAP_CHOOSE_PACKAGE_INFO: str
    FACE_SWAP_GENERATIONS_IN_PACKAGES_ENDED: str
    FACE_SWAP_MIN_ERROR: str
    FACE_SWAP_MAX_ERROR: str
    FACE_SWAP_NO_FACE_FOUND_ERROR: str

    @staticmethod
    def face_swap_choose_package(name: str, available_images: int, total_images: int, used_images: int) -> str:
        raise NotImplementedError

    @staticmethod
    def face_swap_package_forbidden_error(available_images: int) -> str:
        raise NotImplementedError

    # Feedback
    FEEDBACK_INFO: str
    FEEDBACK_SUCCESS: str
    FEEDBACK_APPROVED: str
    FEEDBACK_APPROVED_WITH_LIMIT_ERROR: str
    FEEDBACK_DENIED: str

    # Flux
    FLUX = '🫐 Flux'
    FLUX_1_DEV = '🌲 Flux 1.0 Dev'
    FLUX_1_PRO = '🏔 Flux 1.1 Pro'
    FLUX_STRICT_SAFETY_TOLERANCE: str
    FLUX_MIDDLE_SAFETY_TOLERANCE: str
    FLUX_PERMISSIVE_SAFETY_TOLERANCE: str

    # Gemini
    GEMINI = '✨ Gemini'
    GEMINI_2_FLASH = '🏎 Gemini 2.0 Flash'
    GEMINI_1_PRO = '💼 Gemini 1.5 Pro'
    GEMINI_1_ULTRA = '🛡️ Gemini 1.0 Ultra'

    # Gemini Video
    GEMINI_VIDEO = '📼 Video Summary'
    GEMINI_VIDEO_INFO: str
    GEMINI_VIDEO_TOO_LONG_ERROR: str
    GEMINI_VIDEO_VALUE_ERROR: str

    @staticmethod
    def gemini_video_prompt(
        focus: VideoSummaryFocus,
        format: VideoSummaryFormat,
        amount: VideoSummaryAmount,
    ) -> str:
        raise NotImplementedError

    # Gender
    GENDER_CHOOSE: str
    GENDER_CHANGE: str
    GENDER_UNSPECIFIED: str
    GENDER_MALE: str
    GENDER_FEMALE: str

    # Generation
    GENERATION_IMAGE_SUCCESS: str
    GENERATION_VIDEO_SUCCESS: str

    # Grok
    GROK = '🐦 Grok 2.0'

    # Help
    HELP_INFO: str

    # Info
    INFO: str
    INFO_TEXT_MODELS: str
    INFO_IMAGE_MODELS: str
    INFO_MUSIC_MODELS: str
    INFO_VIDEO_MODELS: str
    INFO_CHAT_GPT: str
    INFO_CHAT_GPT_4_OMNI_MINI: str
    INFO_CHAT_GPT_4_OMNI: str
    INFO_CHAT_GPT_O_1_MINI: str
    INFO_CHAT_GPT_O_1: str
    INFO_CLAUDE: str
    INFO_CLAUDE_3_HAIKU: str
    INFO_CLAUDE_3_SONNET: str
    INFO_CLAUDE_3_OPUS: str
    INFO_GEMINI: str
    INFO_GEMINI_2_FLASH: str
    INFO_GEMINI_1_PRO: str
    INFO_GEMINI_1_ULTRA: str
    INFO_GROK: str
    INFO_PERPLEXITY: str
    INFO_DALL_E: str
    INFO_MIDJOURNEY: str
    INFO_STABLE_DIFFUSION: str
    INFO_STABLE_DIFFUSION_XL: str
    INFO_STABLE_DIFFUSION_3: str
    INFO_FLUX: str
    INFO_FLUX_1_DEV: str
    INFO_FLUX_1_PRO: str
    INFO_LUMA_PHOTON: str
    INFO_RECRAFT: str
    INFO_FACE_SWAP: str
    INFO_PHOTOSHOP_AI: str
    INFO_MUSIC_GEN: str
    INFO_SUNO: str
    INFO_KLING: str
    INFO_RUNWAY: str
    INFO_LUMA_RAY: str
    INFO_PIKA: str

    # Kling
    KLING = '🎬 Kling'
    KLING_MODE_STANDARD: str
    KLING_MODE_PRO: str

    # Language
    LANGUAGE: str
    LANGUAGE_CHOSEN: str

    # Luma Photon
    LUMA_PHOTON = '🌌 Luma Photon'

    # Luma Ray
    LUMA_RAY = '🔆 Luma Ray'

    # Maintenance Mode
    MAINTENANCE_MODE: str

    # Midjourney
    MIDJOURNEY = '🎨 Midjourney'
    MIDJOURNEY_ALREADY_CHOSE_UPSCALE: str

    # Model
    MODEL: str
    MODEL_CHANGE_AI: str
    MODEL_CHOOSE_CHAT_GPT: str
    MODEL_CHOOSE_CLAUDE: str
    MODEL_CHOOSE_GEMINI: str
    MODEL_CHOOSE_STABLE_DIFFUSION: str
    MODEL_CHOOSE_FLUX: str
    MODEL_CONTINUE_GENERATING: str
    MODEL_ALREADY_MAKE_REQUEST: str
    MODEL_READY_FOR_NEW_REQUEST: str
    MODEL_SHOW_QUOTA: str
    MODEL_SWITCHED_TO_AI_MANAGE: str
    MODEL_SWITCHED_TO_AI_MANAGE_INFO: str
    MODEL_SWITCHED_TO_AI_SETTINGS: str
    MODEL_SWITCHED_TO_AI_INFO: str
    MODEL_SWITCHED_TO_AI_EXAMPLES: str
    MODEL_ALREADY_SWITCHED_TO_THIS_MODEL: str

    @staticmethod
    def model_switched(model_name: str, model_type: ModelType, model_info: dict):
        raise NotImplementedError

    @staticmethod
    def model_text_processing_request() -> str:
        raise NotImplementedError

    @staticmethod
    def model_image_processing_request() -> str:
        raise NotImplementedError

    @staticmethod
    def model_face_swap_processing_request() -> str:
        raise NotImplementedError

    @staticmethod
    def model_music_processing_request() -> str:
        raise NotImplementedError

    @staticmethod
    def model_video_processing_request() -> str:
        raise NotImplementedError

    @staticmethod
    def model_wait_for_another_request(seconds: int) -> str:
        raise NotImplementedError

    @staticmethod
    def model_reached_usage_limit():
        raise NotImplementedError

    @staticmethod
    def model_restricted(model: str):
        raise NotImplementedError

    MODELS_TEXT: str
    MODELS_SUMMARY: str
    MODELS_IMAGE: str
    MODELS_MUSIC: str
    MODELS_VIDEO: str

    # MusicGen
    MUSIC_GEN = '🎺 MusicGen'
    MUSIC_GEN_INFO: str
    MUSIC_GEN_TYPE_SECONDS: str
    MUSIC_GEN_MIN_ERROR: str
    MUSIC_GEN_MAX_ERROR: str
    MUSIC_GEN_SECONDS_10: str
    MUSIC_GEN_SECONDS_30: str
    MUSIC_GEN_SECONDS_60: str
    MUSIC_GEN_SECONDS_180: str
    MUSIC_GEN_SECONDS_300: str
    MUSIC_GEN_SECONDS_600: str

    @staticmethod
    def music_gen_forbidden_error(available_seconds: int) -> str:
        raise NotImplementedError

    # Notify about quota
    @staticmethod
    def notify_about_quota(
        subscription_limits: dict,
    ) -> str:
        raise NotImplementedError

    NOTIFY_ABOUT_QUOTA_TURN_OFF: str
    NOTIFY_ABOUT_QUOTA_TURN_OFF_SUCCESS: str

    # Open
    OPEN_SETTINGS: str
    OPEN_BONUS_INFO: str
    OPEN_BUY_SUBSCRIPTIONS_INFO: str
    OPEN_BUY_PACKAGES_INFO: str

    # Package
    PACKAGE: str
    PACKAGE_SUCCESS: str
    PACKAGE_QUANTITY_MIN_ERROR: str
    PACKAGE_QUANTITY_MAX_ERROR: str

    @staticmethod
    def package_info(currency: Currency, cost: str, gift_products: list[Product]) -> str:
        raise NotImplementedError

    @staticmethod
    def package_choose_min(name: str) -> str:
        raise NotImplementedError

    @staticmethod
    def package_confirmation(package_name: str, package_quantity: int, currency: Currency, price: str) -> str:
        raise NotImplementedError

    @staticmethod
    def payment_package_description(user_id: str, package_name: str, package_quantity: int):
        raise NotImplementedError

    PACKAGES: str
    PACKAGES_SUCCESS: str
    PACKAGES_END: str

    @staticmethod
    def packages_description(user_id: str):
        raise NotImplementedError

    # Payment
    PAYMENT_BUY: str
    PAYMENT_CHANGE_CURRENCY: str
    PAYMENT_YOOKASSA_PAYMENT_METHOD: str
    PAYMENT_STRIPE_PAYMENT_METHOD: str
    PAYMENT_TELEGRAM_STARS_PAYMENT_METHOD: str
    PAYMENT_CHOOSE_PAYMENT_METHOD: str
    PAYMENT_PROCEED_TO_PAY: str
    PAYMENT_PROCEED_TO_CHECKOUT: str
    PAYMENT_DISCOUNT: str
    PAYMENT_NO_DISCOUNT: str

    @staticmethod
    def payment_purchase_minimal_price(currency: Currency, current_price: str):
        raise NotImplementedError

    # Perplexity
    PERPLEXITY = '🌐 Perplexity'

    # Photoshop AI
    PHOTOSHOP_AI = '🪄 Photoshop AI'
    PHOTOSHOP_AI_INFO: str
    PHOTOSHOP_AI_UPSCALE: str
    PHOTOSHOP_AI_UPSCALE_INFO: str
    PHOTOSHOP_AI_RESTORATION: str
    PHOTOSHOP_AI_RESTORATION_INFO: str
    PHOTOSHOP_AI_COLORIZATION: str
    PHOTOSHOP_AI_COLORIZATION_INFO: str
    PHOTOSHOP_AI_REMOVE_BACKGROUND: str
    PHOTOSHOP_AI_REMOVE_BACKGROUND_INFO: str

    # Pika
    PIKA = '🐇 Pika'

    # Profile
    @staticmethod
    def profile(
        subscription_name: str,
        subscription_status: SubscriptionStatus,
        current_model: str,
        renewal_date,
    ) -> str:
        raise NotImplementedError

    @staticmethod
    def profile_quota(
        subscription_limits: dict,
        daily_limits: dict,
        additional_usage_quota: dict,
    ) -> str:
        raise NotImplementedError

    PROFILE_SHOW_QUOTA: str
    PROFILE_TELL_ME_YOUR_GENDER: str
    PROFILE_YOUR_GENDER: str
    PROFILE_SEND_ME_YOUR_PICTURE: str
    PROFILE_UPLOAD_PHOTO: str
    PROFILE_UPLOADING_PHOTO: str
    PROFILE_CHANGE_PHOTO: str
    PROFILE_CHANGE_PHOTO_SUCCESS: str
    PROFILE_RENEW_SUBSCRIPTION: str
    PROFILE_RENEW_SUBSCRIPTION_SUCCESS: str
    PROFILE_CANCEL_SUBSCRIPTION: str
    PROFILE_CANCEL_SUBSCRIPTION_CONFIRMATION: str
    PROFILE_CANCEL_SUBSCRIPTION_SUCCESS: str
    PROFILE_NO_ACTIVE_SUBSCRIPTION: str

    # Promo code
    PROMO_CODE_ACTIVATE: str
    PROMO_CODE_INFO: str
    PROMO_CODE_SUCCESS: str
    PROMO_CODE_ALREADY_HAVE_SUBSCRIPTION: str
    PROMO_CODE_EXPIRED_ERROR: str
    PROMO_CODE_NOT_FOUND_ERROR: str
    PROMO_CODE_ALREADY_USED_ERROR: str

    # Runway
    RUNWAY = '🎥 Runway'

    # Recraft
    RECRAFT = '🐼 Recraft'

    # Remove Restriction
    REMOVE_RESTRICTION: str
    REMOVE_RESTRICTION_INFO: str

    # Settings
    @staticmethod
    def settings_info(human_model: str, current_model: Model, generation_cost=1) -> str:
        raise NotImplementedError

    SETTINGS_CHOOSE_MODEL_TYPE: str
    SETTINGS_CHOOSE_MODEL: str
    SETTINGS_VOICE_MESSAGES: str
    SETTINGS_VERSION: str
    SETTINGS_FOCUS: str
    SETTINGS_FORMAT: str
    SETTINGS_AMOUNT: str
    SETTINGS_SEND_TYPE: str
    SETTINGS_SEND_TYPE_IMAGE: str
    SETTINGS_SEND_TYPE_DOCUMENT: str
    SETTINGS_SEND_TYPE_AUDIO: str
    SETTINGS_SEND_TYPE_VIDEO: str
    SETTINGS_ASPECT_RATIO: str
    SETTINGS_QUALITY: str
    SETTINGS_PROMPT_SAFETY: str
    SETTINGS_GENDER: str
    SETTINGS_DURATION: str
    SETTINGS_MODE: str
    SETTINGS_SHOW_THE_NAME_OF_THE_CHATS: str
    SETTINGS_SHOW_THE_NAME_OF_THE_ROLES: str
    SETTINGS_SHOW_USAGE_QUOTA_IN_MESSAGES: str
    SETTINGS_TURN_ON_VOICE_MESSAGES: str
    SETTINGS_LISTEN_VOICES: str

    # Shopping cart
    SHOPPING_CART: str
    SHOPPING_CART_ADD: str

    @staticmethod
    def shopping_cart_add_or_buy_now(
        product: Product,
        product_quantity: int,
        product_price: float,
        currency: Currency,
    ):
        raise NotImplementedError

    SHOPPING_CART_BUY_NOW: str
    SHOPPING_CART_REMOVE: str
    SHOPPING_CART_GO_TO: str
    SHOPPING_CART_GO_TO_OR_CONTINUE_SHOPPING: str
    SHOPPING_CART_CONTINUE_SHOPPING: str
    SHOPPING_CART_CLEAR: str

    @staticmethod
    async def shopping_cart_info(currency: Currency, cart_items: list[dict], discount: int):
        raise NotImplementedError

    @staticmethod
    async def shopping_cart_confirmation(cart_items: list[dict], currency: Currency, price: float) -> str:
        raise NotImplementedError

    # Stable Diffusion
    STABLE_DIFFUSION = '🎆 Stable Diffusion'
    STABLE_DIFFUSION_XL = '🦄 Stable Diffusion XL'
    STABLE_DIFFUSION_3 = '🧑‍🚀 Stable Diffusion 3.5'

    # Start
    START_INFO: str
    START_QUICK_GUIDE: str
    START_QUICK_GUIDE_INFO: str

    # Subscription
    SUBSCRIPTION: str
    SUBSCRIPTIONS: str
    SUBSCRIPTION_MONTH_1: str
    SUBSCRIPTION_MONTHS_3: str
    SUBSCRIPTION_MONTHS_6: str
    SUBSCRIPTION_MONTHS_12: str
    SUBSCRIPTION_SUCCESS: str
    SUBSCRIPTION_RESET: str
    SUBSCRIPTION_RETRY: str
    SUBSCRIPTION_END: str
    SUBSCRIPTION_MONTHLY: str
    SUBSCRIPTION_YEARLY: str

    @staticmethod
    def subscription_description(user_id: str, name: str):
        raise NotImplementedError

    @staticmethod
    def subscription_renew_description(user_id: str, name: str):
        raise NotImplementedError

    @staticmethod
    def subscribe(
        subscriptions: list[Product],
        currency: Currency,
        user_discount: int,
        is_trial=False,
    ) -> str:
        raise NotImplementedError

    @staticmethod
    def subscribe_confirmation(
        name: str,
        category: ProductCategory,
        currency: Currency,
        price: Union[str, int, float],
        is_trial: bool,
    ) -> str:
        raise NotImplementedError

    # Suno
    SUNO = '🎸 Suno'
    SUNO_INFO: str
    SUNO_SIMPLE_MODE: str
    SUNO_CUSTOM_MODE: str
    SUNO_SIMPLE_MODE_PROMPT: str
    SUNO_CUSTOM_MODE_LYRICS: str
    SUNO_CUSTOM_MODE_GENRES: str
    SUNO_START_AGAIN: str
    SUNO_TOO_MANY_WORDS_ERROR: str
    SUNO_VALUE_ERROR: str
    SUNO_SKIP: str

    # Tech Support
    TECH_SUPPORT: str

    # Terms Link
    TERMS_LINK: str

    # Video Summary
    VIDEO_SUMMARY_FOCUS_INSIGHTFUL: str
    VIDEO_SUMMARY_FOCUS_FUNNY: str
    VIDEO_SUMMARY_FOCUS_ACTIONABLE: str
    VIDEO_SUMMARY_FOCUS_CONTROVERSIAL: str
    VIDEO_SUMMARY_FORMAT_LIST: str
    VIDEO_SUMMARY_FORMAT_FAQ: str
    VIDEO_SUMMARY_AMOUNT_AUTO: str
    VIDEO_SUMMARY_AMOUNT_SHORT: str
    VIDEO_SUMMARY_AMOUNT_DETAILED: str

    # Voice
    VOICE_MESSAGES: str
    VOICE_MESSAGES_FORBIDDEN_ERROR: str

    # Work with files
    WORK_WITH_FILES: str
    WORK_WITH_FILES_FORBIDDEN_ERROR: str

    # Admin
    ADMIN_INFO: str

    ADMIN_ADS_INFO: str
    ADMIN_ADS_CREATE: str
    ADMIN_ADS_GET: str
    ADMIN_ADS_SEND_LINK: str
    ADMIN_ADS_CHOOSE_SOURCE: str
    ADMIN_ADS_CHOOSE_MEDIUM: str
    ADMIN_ADS_SEND_DISCOUNT: str
    ADMIN_ADS_SEND_NAME: str
    ADMIN_ADS_VALUE_ERROR: str

    ADMIN_BAN_INFO: str
    ADMIN_BAN_SUCCESS: str
    ADMIN_UNBAN_SUCCESS: str

    ADMIN_BLAST_CHOOSE_USER_TYPE: str
    ADMIN_BLAST_CHOOSE_LANGUAGE: str
    ADMIN_BLAST_WRITE_IN_CHOSEN_LANGUAGE: str
    ADMIN_BLAST_WRITE_IN_DEFAULT_LANGUAGE: str
    ADMIN_BLAST_SUCCESS: str

    @staticmethod
    def admin_blast_confirmation(
        blast_letters: dict,
    ):
        raise NotImplementedError

    ADMIN_CATALOG: str
    ADMIN_CATALOG_CREATE: str
    ADMIN_CATALOG_CREATE_ROLE: str
    ADMIN_CATALOG_CREATE_ROLE_ALREADY_EXISTS_ERROR: str
    ADMIN_CATALOG_CREATE_ROLE_NAME: str
    ADMIN_CATALOG_CREATE_ROLE_DESCRIPTION: str
    ADMIN_CATALOG_CREATE_ROLE_INSTRUCTION: str
    ADMIN_CATALOG_CREATE_ROLE_PHOTO: str
    ADMIN_CATALOG_CREATE_ROLE_SUCCESS: str

    @staticmethod
    def admin_catalog_create_role_confirmation(
        role_names: dict,
        role_descriptions: dict,
        role_instructions: dict,
    ):
        raise NotImplementedError

    @staticmethod
    def admin_catalog_edit_role_info(
        role_names: dict[LanguageCode, str],
        role_descriptions: dict[LanguageCode, str],
        role_instructions: dict[LanguageCode, str],
    ):
        raise NotImplementedError

    ADMIN_CATALOG_EDIT_ROLE_NAME: str
    ADMIN_CATALOG_EDIT_ROLE_NAME_INFO: str
    ADMIN_CATALOG_EDIT_ROLE_DESCRIPTION: str
    ADMIN_CATALOG_EDIT_ROLE_DESCRIPTION_INFO: str
    ADMIN_CATALOG_EDIT_ROLE_INSTRUCTION: str
    ADMIN_CATALOG_EDIT_ROLE_INSTRUCTION_INFO: str
    ADMIN_CATALOG_EDIT_ROLE_PHOTO: str
    ADMIN_CATALOG_EDIT_ROLE_PHOTO_INFO: str
    ADMIN_CATALOG_EDIT_SUCCESS: str

    ADMIN_DATABASE: str

    ADMIN_FACE_SWAP_INFO: str
    ADMIN_FACE_SWAP_CREATE: str
    ADMIN_FACE_SWAP_CREATE_PACKAGE: str
    ADMIN_FACE_SWAP_CREATE_PACKAGE_ALREADY_EXISTS_ERROR: str
    ADMIN_FACE_SWAP_CREATE_PACKAGE_NAME: str
    ADMIN_FACE_SWAP_CREATE_PACKAGE_SUCCESS: str

    @staticmethod
    def admin_face_swap_create_package_confirmation(
        package_system_name: str,
        package_names: dict,
    ):
        raise NotImplementedError

    ADMIN_FACE_SWAP_EDIT: str
    ADMIN_FACE_SWAP_EDIT_PACKAGE: str
    ADMIN_FACE_SWAP_EDIT_CHOOSE_GENDER: str
    ADMIN_FACE_SWAP_EDIT_CHOOSE_PACKAGE: str
    ADMIN_FACE_SWAP_EDIT_SUCCESS: str
    ADMIN_FACE_SWAP_CHANGE_STATUS: str
    ADMIN_FACE_SWAP_SHOW_PICTURES: str
    ADMIN_FACE_SWAP_ADD_NEW_PICTURE: str
    ADMIN_FACE_SWAP_ADD_NEW_PICTURE_NAME: str
    ADMIN_FACE_SWAP_ADD_NEW_PICTURE_IMAGE: str
    ADMIN_FACE_SWAP_EXAMPLE_PICTURE: str
    ADMIN_FACE_SWAP_PUBLIC: str
    ADMIN_FACE_SWAP_PRIVATE: str

    ADMIN_PROMO_CODE_INFO: str
    ADMIN_PROMO_CODE_SUCCESS: str
    ADMIN_PROMO_CODE_CHOOSE_SUBSCRIPTION: str
    ADMIN_PROMO_CODE_CHOOSE_PACKAGE: str
    ADMIN_PROMO_CODE_CHOOSE_DISCOUNT: str
    ADMIN_PROMO_CODE_CHOOSE_NAME: str
    ADMIN_PROMO_CODE_CHOOSE_DATE: str
    ADMIN_PROMO_CODE_NAME_EXISTS_ERROR: str
    ADMIN_PROMO_CODE_DATE_VALUE_ERROR: str

    ADMIN_SERVER: str

    ADMIN_STATISTICS_INFO: str
    ADMIN_STATISTICS_WRITE_TRANSACTION: str
    ADMIN_STATISTICS_CHOOSE_SERVICE: str
    ADMIN_STATISTICS_CHOOSE_CURRENCY: str
    ADMIN_STATISTICS_SERVICE_QUANTITY: str
    ADMIN_STATISTICS_SERVICE_AMOUNT: str
    ADMIN_STATISTICS_SERVICE_DATE: str
    ADMIN_STATISTICS_SERVICE_DATE_VALUE_ERROR: str
    ADMIN_STATISTICS_WRITE_TRANSACTION_SUCCESSFUL: str

    @staticmethod
    def admin_statistics_processing_request() -> str:
        raise NotImplementedError

    @staticmethod
    def admin_statistics_users(
        period: str,
        subscription_products: dict[str, list[str]],
        count_all_users: int,
        count_all_users_before: int,
        count_activated_users: int,
        count_activated_users_before: int,
        count_referral_users: int,
        count_referral_users_before: int,
        count_campaign_users: int,
        count_campaign_users_before: int,
        count_english_users: int,
        count_english_users_before: int,
        count_russian_users: int,
        count_russian_users_before: int,
        count_spanish_users: int,
        count_spanish_users_before: int,
        count_hindi_users: int,
        count_hindi_users_before: int,
        count_other_users: int,
        count_other_users_before: int,
        count_paid_users: int,
        count_paid_users_before: int,
        count_blocked_users: int,
        count_blocked_users_before: int,
        count_subscription_users: dict,
        count_subscription_users_before: dict,
    ):
        raise NotImplementedError

    @staticmethod
    def admin_statistics_text_models(
        period: str,
        text_products: dict[str, str],
        count_all_transactions: dict,
        count_all_transactions_before: dict,
    ):
        raise NotImplementedError

    @staticmethod
    def admin_statistics_summary_models(
        period: str,
        summary_products: dict[str, str],
        count_all_transactions: dict,
        count_all_transactions_before: dict,
    ):
        raise NotImplementedError

    @staticmethod
    def admin_statistics_image_models(
        period: str,
        image_products: dict[str, str],
        count_all_transactions: dict,
        count_all_transactions_before: dict,
    ):
        raise NotImplementedError

    @staticmethod
    def admin_statistics_music_models(
        period: str,
        music_products: dict[str, str],
        count_all_transactions: dict,
        count_all_transactions_before: dict,
    ):
        raise NotImplementedError

    @staticmethod
    def admin_statistics_video_models(
        period: str,
        video_products: dict[str, str],
        count_all_transactions: dict,
        count_all_transactions_before: dict,
    ):
        raise NotImplementedError

    @staticmethod
    def admin_statistics_reactions(
        period: str,
        products_with_reactions: dict[str, str],
        count_reactions: dict,
        count_reactions_before: dict,
        count_feedbacks: dict,
        count_feedbacks_before: dict,
        count_games: dict,
        count_games_before: dict,
    ):
        raise NotImplementedError

    @staticmethod
    def admin_statistics_bonuses(
        period: str,
        package_products: dict[str, str],
        count_credits: dict,
        count_credits_before: dict,
        count_all_transactions: dict,
        count_all_transactions_before: dict,
        count_activated_promo_codes: int,
        count_activated_promo_codes_before: int,
    ):
        raise NotImplementedError

    @staticmethod
    def admin_statistics_ai_expenses(
        period: str,
        ai_products: dict[str, str],
        count_expense_money: dict,
        count_expense_money_before: dict,
    ):
        raise NotImplementedError

    @staticmethod
    def admin_statistics_tech_expenses(
        period: str,
        tech_products: dict[str, str],
        count_expense_money: dict,
        count_expense_money_before: dict,
    ):
        raise NotImplementedError

    @staticmethod
    def admin_statistics_user_expenses(
        period: str,
        subscription_products: dict[str, list[str]],
        count_expense_money: dict,
        count_expense_money_before: dict,
    ):
        raise NotImplementedError

    @staticmethod
    def admin_statistics_expenses(
        period: str,
        count_expense_money: dict,
        count_expense_money_before: dict,
    ):
        raise NotImplementedError

    @staticmethod
    def admin_statistics_incomes(
        period: str,
        subscription_products: dict[str, list[str]],
        package_products: dict[str, str],
        count_income_money: dict,
        count_income_money_before: dict,
    ):
        raise NotImplementedError

    @staticmethod
    def admin_payment_subscription_changed_status(
        status: SubscriptionStatus,
        subscription: Subscription,
        product: Product,
        is_trial=False,
        is_renew=False,
    ):
        raise NotImplementedError

    @staticmethod
    def admin_payment_package_changed_status(
        status: PackageStatus,
        package: Package,
        product: Product,
    ):
        raise NotImplementedError

    @staticmethod
    def admin_payment_packages_changed_status(
        status: PackageStatus,
        user_id: str,
        payment_method: PaymentMethod,
        amount: float,
        income_amount: float,
        currency: Currency,
    ):
        raise NotImplementedError
