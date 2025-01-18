from dataclasses import field
from datetime import datetime, timezone
from enum import StrEnum
from typing import Optional, ClassVar, Union

from pydantic import BaseModel, Field

from bot.database.models.common import Currency, ModelType
from bot.database.models.subscription import SubscriptionType, SubscriptionPeriod
from bot.locales.types import LanguageCode


class ProductType(StrEnum):
    SUBSCRIPTION = 'SUBSCRIPTION'
    PACKAGE = 'PACKAGE'


class ProductCategory(StrEnum):
    MONTHLY = SubscriptionType.MONTHLY
    YEARLY = SubscriptionType.YEARLY
    TEXT = ModelType.TEXT
    SUMMARY = ModelType.SUMMARY
    IMAGE = ModelType.IMAGE
    MUSIC = ModelType.MUSIC
    VIDEO = ModelType.VIDEO
    OTHER = 'OTHER'


class ProductCategorySymbols(StrEnum):
    TEXT = '✉️'
    SUMMARY = '📝'
    IMAGE = '🖼'
    MUSIC = '🎵'
    VIDEO = '📹'
    OTHER = '🗓'


class Product(BaseModel):
    COLLECTION_NAME: ClassVar[str] = 'products'

    id: str
    stripe_id: str
    is_active: bool
    type: ProductType
    category: ProductCategory
    names: dict[LanguageCode, str]
    descriptions: dict[LanguageCode, str]
    prices: dict
    photos: Optional[dict] = None
    order: int = -1
    discount: int = 0
    details: Optional[dict] = field(default_factory=lambda: {})
    created_at: Optional[datetime] = Field(default_factory=lambda: datetime.now(timezone.utc))
    edited_at: Optional[datetime] = Field(default_factory=lambda: datetime.now(timezone.utc))

    def to_dict(self):
        return vars(self)

    @staticmethod
    def get_discount_price(
        type: ProductType,
        quantity: int,
        price: Union[int, float],
        currency: Currency,
        discount: int,
        subscription_period: Optional[SubscriptionPeriod] = None,
    ) -> str:
        if type == ProductType.SUBSCRIPTION:
            price_discount = {
                SubscriptionPeriod.MONTH1: discount if discount > 0 else 0,
                SubscriptionPeriod.MONTHS3: discount if discount > 5 else 5,
                SubscriptionPeriod.MONTHS6: discount if discount > 10 else 10,
                SubscriptionPeriod.MONTHS12: discount if discount > 20 else 20,
            }

            price_with_discount = round(
                price - (price * (price_discount[subscription_period] / 100.0)),
                2,
            )
            if currency == Currency.RUB or currency == Currency.XTR:
                price_with_discount = int(price_with_discount)
        else:
            price_with_discount = round(
                price * quantity - (price * quantity * (discount / 100.0)),
                2,
            )

        return ('%f' % price_with_discount).rstrip('0').rstrip('.')
