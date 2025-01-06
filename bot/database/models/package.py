from datetime import datetime, timezone
from enum import StrEnum

from bot.database.models.common import Currency, PaymentMethod


class PackageStatus(StrEnum):
    SUCCESS = 'SUCCESS'
    WAITING = 'WAITING'
    DECLINED = 'DECLINED'
    ERROR = 'ERROR'


class Package:
    COLLECTION_NAME = 'packages'

    id: str
    user_id: str
    product_id: str
    status: PackageStatus
    currency: Currency
    amount: float
    income_amount: float
    quantity: int
    payment_method: PaymentMethod
    provider_payment_charge_id: str
    until_at: datetime
    created_at: datetime
    edited_at: datetime

    def __init__(
        self,
        id: str,
        user_id: str,
        product_id: str,
        status: PackageStatus,
        currency: Currency,
        amount: float,
        income_amount=0.00,
        quantity=1,
        payment_method=PaymentMethod.YOOKASSA,
        provider_payment_charge_id='',
        until_at=None,
        created_at=None,
        edited_at=None,
        **kwargs,
    ):
        self.id = id
        self.user_id = user_id
        self.product_id = product_id
        self.status = status
        self.currency = currency
        self.amount = amount
        self.income_amount = income_amount
        self.quantity = quantity
        self.payment_method = payment_method
        self.provider_payment_charge_id = provider_payment_charge_id
        self.product_id = product_id
        self.until_at = until_at

        current_time = datetime.now(timezone.utc)
        self.created_at = created_at if created_at is not None else current_time
        self.edited_at = edited_at if edited_at is not None else current_time

    def to_dict(self):
        return vars(self)
