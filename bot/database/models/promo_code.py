from datetime import datetime, timezone
from enum import StrEnum


class PromoCodeType(StrEnum):
    SUBSCRIPTION = "SUBSCRIPTION"
    PACKAGE = "PACKAGE"
    DISCOUNT = "DISCOUNT"


class PromoCode:
    COLLECTION_NAME = "promo_codes"

    id: str
    created_by_user_id: str
    name: str
    type: PromoCodeType
    details: dict
    until: datetime
    created_at: datetime
    edited_at: datetime

    def __init__(
        self,
        id: str,
        created_by_user_id: str,
        name: str,
        type: PromoCodeType,
        details: dict,
        until=None,
        created_at=None,
        edited_at=None,
        **kwargs,
    ):
        self.id = id
        self.created_by_user_id = created_by_user_id
        self.name = name
        self.type = type
        self.details = details
        self.until = until

        current_time = datetime.now(timezone.utc)
        self.created_at = created_at if created_at is not None else current_time
        self.edited_at = edited_at if edited_at is not None else current_time

    def to_dict(self):
        return vars(self)


class UsedPromoCode:
    COLLECTION_NAME = "used_promo_codes"

    id: str
    user_id: str
    promo_code_id: str
    date: datetime

    def __init__(
        self,
        id: str,
        user_id: str,
        promo_code_id: str,
        date=None,
    ):
        self.id = id
        self.user_id = user_id
        self.promo_code_id = promo_code_id

        current_time = datetime.now(timezone.utc)
        self.date = date if date is not None else current_time

    def to_dict(self):
        return vars(self)
