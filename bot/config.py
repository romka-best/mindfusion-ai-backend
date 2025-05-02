import json
import os
import importlib
from dataclasses import field
from pathlib import Path
from typing import ClassVar

from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import SecretStr, field_validator

from .settings.message_sticker import MessageSticker
from .settings.message_effect import MessageEffect


env = os.getenv("ENV", "dev") # dev | dev_test | prod
_config = importlib.import_module(f"bot.settings.config_{env}")

class Settings(BaseSettings):
    BASE_DIR: ClassVar[Path] = Path(__file__).resolve().parent.parent

    WEBHOOK_URL: str
    WEBHOOK_REPLICATE_PATH: str
    WEBHOOK_MIDJOURNEY_PATH: str
    WEBHOOK_SUNO_PATH: str
    WEBHOOK_KLING_PATH: str
    WEBHOOK_LUMA_PATH: str
    WEBHOOK_PIKA_PATH: str

    REDIS_URL: str

    MAX_RETRIES: int = 2
    BATCH_SIZE: int = 500
    LIMIT_BETWEEN_REQUESTS_SECONDS: int = 20
    LIMIT_PROCESSING_SECONDS: int = 60

    SUPER_ADMIN_ID: str = _config.SUPER_ADMIN_ID
    ADMIN_IDS: list[str] = field(default_factory=lambda: ['354543567', '6078317830'])
    DEVELOPER_IDS: list[str] = field(default_factory=lambda: ['354543567', '1384055865', '2048756506'])
    MODERATOR_IDS: list[str] = field(default_factory=lambda: [])

    DEFAULT_ROLE_ID: SecretStr

    CERTIFICATE_NAME: SecretStr
    STORAGE_NAME: SecretStr
    BILLING_TABLE: SecretStr

    BOT_URL: str
    BOT_TOKEN: SecretStr
    ADDITIONAL_BOT_TOKENS: list[SecretStr]

    @field_validator("ADDITIONAL_BOT_TOKENS", mode="before")
    @classmethod
    def parse_json(cls, value):
        if isinstance(value, str):
            return [SecretStr(token) for token in json.loads(value)]
        return value

    MESSAGE_EFFECTS: dict[MessageEffect, str] = field(default_factory=lambda: _config.MESSAGE_EFFECTS)
    MESSAGE_STICKERS: dict[MessageSticker, str] = field(default_factory=lambda: _config.MESSAGE_STICKERS)
    BUNDLE_PHOTO_PLACEHOLDERS: dict[int, str] = field(default_factory=lambda : _config.BUNDLE_PHOTO_PLACEHOLDERS)

    YOOKASSA_ACCOUNT_ID: SecretStr
    YOOKASSA_SECRET_KEY: SecretStr

    STRIPE_PUBLISH_KEY: SecretStr
    STRIPE_SECRET_KEY: SecretStr

    OAUTH_YANDEX_TOKEN: SecretStr

    OPENAI_API_KEY: SecretStr
    ANTHROPIC_API_KEY: SecretStr
    GEMINI_API_KEY: SecretStr
    GROK_API_KEY: SecretStr
    DEEPSEEK_API_KEY: SecretStr
    PERPLEXITY_API_KEY: SecretStr

    EIGHTIFY_API_KEY: SecretStr

    REPLICATE_API_KEY: SecretStr

    MIDJOURNEY_API_KEY: SecretStr
    RECRAFT_API_KEY: SecretStr
    FACE_SWAP_API_KEY: SecretStr

    SUNO_API_KEY: SecretStr

    KLING_API_KEY: SecretStr
    RUNWAYML_API_KEY: SecretStr
    LUMA_API_KEY: SecretStr
    PIKA_API_KEY: SecretStr

    model_config = SettingsConfigDict(
        env_file=str(BASE_DIR / f'.env.{os.getenv("ENV", "dev")}'),
        env_file_encoding='utf-8',
    )


config = Settings()
