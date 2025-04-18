import json
import os
from dataclasses import field
from enum import StrEnum
from pathlib import Path
from typing import ClassVar

from pydantic import SecretStr, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class MessageEffect(StrEnum):
    FIRE = "FIRE"
    LIKE = "LIKE"
    DISLIKE = "DISLIKE"
    HEART = "HEART"
    CONGRATS = "CONGRATS"
    POOP = "POOP"


class MessageSticker(StrEnum):
    LOGO = "LOGO"
    HELLO = "HELLO"
    LOVE = "LOVE"
    FEAR = "FEAR"
    SAD = "SAD"
    THINKING = "THINKING"
    CONNECTION_ERROR = "CONNECTION_ERROR"
    ERROR = "ERROR"
    TEXT_GENERATION = "TEXT_GENERATION"
    SUMMARY_GENERATION = "SUMMARY_GENERATION"
    IMAGE_GENERATION = "IMAGE_GENERATION"
    MUSIC_GENERATION = "MUSIC_GENERATION"
    VIDEO_GENERATION = "VIDEO_GENERATION"


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

    SUPER_ADMIN_ID: str = "354543567"
    ADMIN_IDS: list[str] = field(default_factory=lambda: ["354543567", "6078317830"])
    DEVELOPER_IDS: list[str] = field(
        default_factory=lambda: ["354543567", "1384055865", "2048756506"]
    )
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

    MESSAGE_EFFECTS: dict[MessageEffect, str] = field(
        default_factory=lambda: {
            MessageEffect.FIRE: "5104841245755180586",  # 🔥
            MessageEffect.LIKE: "5107584321108051014",  # 👍
            MessageEffect.DISLIKE: "5104858069142078462",  # 👎
            MessageEffect.HEART: "5159385139981059251",  # ❤️
            MessageEffect.CONGRATS: "5046509860389126442",  # 🎉
            MessageEffect.POOP: "5046589136895476101",  # 💩
        }
    )
    MESSAGE_STICKERS: dict[MessageSticker, str] = field(
        default_factory=lambda: {
            MessageSticker.LOGO: "CAACAgIAAxkBAAENOatnRjb80J2N4a8yNcN7pKuIutcOwgACE2cAAuj3MUqczl2UrDJzHjYE",
            MessageSticker.HELLO: "CAACAgIAAxkBAAENOa1nRjnkK8oIvaOQ2K62WQ0vqQYAAX4AAnhiAALGvjFKvC6IwKVpJ_w2BA",
            MessageSticker.LOVE: "CAACAgIAAxkBAAENOa9nRjou7rQg922oE-Rt8ZqoiOzutgACN2EAAi8AATBKj8RV8S_82_Q2BA",
            MessageSticker.FEAR: "CAACAgIAAxkBAAENObFnRjo_HjllJHPZMetf2QYvBCI2YAAC5WgAAmqXMUo4nAe67a_KDjYE",
            MessageSticker.SAD: "CAACAgIAAxkBAAENObNnRjpKsHPA8_VrJmPEeqyi3dMMdAACXV0AAqRfOUq7PyeeSUYifzYE",
            MessageSticker.THINKING: "CAACAgIAAxkBAAENObVnRjpewc6JEr15zJi7USLxUJx77QACfFkAAlP9OEr7tPknrOV-bDYE",
            MessageSticker.CONNECTION_ERROR: "CAACAgIAAxkBAAENObdnRjqARgZxXn4x5744y3zg2NgETAACjWYAAm1JMUrazdOO3yTSEjYE",
            MessageSticker.ERROR: "CAACAgIAAxkBAAENOblnRjqTY41tWD9M1A60ad94sKX0-QACVmgAAmsaMUoJWMddREGp0TYE",
            MessageSticker.TEXT_GENERATION: "CAACAgIAAxkBAAENObtnRjqhyzadBFJzzpFFf_6lS19v4QACY2IAAiNkMErMXAktYqfoqjYE",
            MessageSticker.SUMMARY_GENERATION: "CAACAgIAAxkBAAENUJRnW2GomcZh9azUetyHqyIRe3MTQwACwFsAAi1s4EoTP-kuCqRfuzYE",
            MessageSticker.IMAGE_GENERATION: "CAACAgIAAxkBAAENOb1nRjquVRabNePw6b1NlsZPE1w9rgACaGgAApu2MUpD10AUcVst_TYE",
            MessageSticker.MUSIC_GENERATION: "CAACAgIAAxkBAAENOb9nRjq8WfEW4G1Zr8pLEsHzQTJm5gACYl0AAubSMUoVqNt3elKw6TYE",
            MessageSticker.VIDEO_GENERATION: "CAACAgIAAxkBAAENOcFnRjrVddqaOhU7ZOIooXpNIifTJAAC_WEAAqvsMUpvg5fGNgtAiTYE",
        }
    )

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
        env_file=str(BASE_DIR / f".env.{os.getenv('ENVIRONMENT', 'testing')}"),
        env_file_encoding="utf-8",
    )


config = Settings()
