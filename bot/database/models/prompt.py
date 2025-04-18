from datetime import datetime, timezone
from typing import ClassVar, Optional

from pydantic import BaseModel, Field

from bot.database.models.common import ModelType
from bot.locales.types import LanguageCode


class PromptCategory(BaseModel):
    COLLECTION_NAME: ClassVar[str] = "prompt_categories"

    id: str
    type: ModelType
    names: dict[LanguageCode, str]
    created_at: Optional[datetime] = Field(
        default_factory=lambda: datetime.now(timezone.utc)
    )
    edited_at: Optional[datetime] = Field(
        default_factory=lambda: datetime.now(timezone.utc)
    )

    def to_dict(self):
        return vars(self)


class PromptSubCategory(BaseModel):
    COLLECTION_NAME: ClassVar[str] = "prompt_subcategories"

    id: str
    category_ids: list[str]
    names: dict[LanguageCode, str]
    created_at: Optional[datetime] = Field(
        default_factory=lambda: datetime.now(timezone.utc)
    )
    edited_at: Optional[datetime] = Field(
        default_factory=lambda: datetime.now(timezone.utc)
    )

    def to_dict(self):
        return vars(self)


class Prompt(BaseModel):
    COLLECTION_NAME: ClassVar[str] = "prompts"

    id: str
    product_ids: list[str]
    subcategory_ids: list[str]
    names: dict[LanguageCode, str]
    short_prompts: dict[LanguageCode, str]
    long_prompts: dict[LanguageCode, str]
    has_examples: bool = False
    created_at: Optional[datetime] = Field(
        default_factory=lambda: datetime.now(timezone.utc)
    )
    edited_at: Optional[datetime] = Field(
        default_factory=lambda: datetime.now(timezone.utc)
    )

    def to_dict(self):
        return vars(self)
