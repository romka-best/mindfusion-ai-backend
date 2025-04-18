from datetime import datetime, timezone
from enum import StrEnum

from bot.database.models.common import Currency


class TransactionType(StrEnum):
    INCOME = "INCOME"
    EXPENSE = "EXPENSE"


class ServiceType(StrEnum):
    FREE = "FREE"
    SERVER = "SERVER"
    DATABASE = "DATABASE"
    OTHER = "OTHER"


class Transaction:
    COLLECTION_NAME = "transactions"

    id: str
    user_id: str
    type: TransactionType
    product_id: str
    amount: float
    clear_amount: float
    currency: Currency
    quantity: int
    details: dict
    created_at: datetime
    edited_at: datetime

    def __init__(
        self,
        id: str,
        user_id: str,
        type: TransactionType,
        product_id: str,
        amount: float,
        clear_amount: float,
        currency: Currency,
        quantity=1,
        details=None,
        created_at=None,
        edited_at=None,
        **kwargs,
    ):
        self.id = str(id)
        self.user_id = str(user_id)
        self.type = type
        self.product_id = product_id
        self.amount = amount
        self.clear_amount = clear_amount
        self.currency = currency
        self.quantity = quantity
        self.details = {} if details is None else details

        current_time = datetime.now(timezone.utc)
        self.created_at = created_at if created_at is not None else current_time
        self.edited_at = edited_at if edited_at is not None else current_time

    def to_dict(self):
        return vars(self)
