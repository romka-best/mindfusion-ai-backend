from dataclasses import dataclass
from typing import Any, Optional

from bot.database.models.common import PaymentMethod


@dataclass
class RefundResult:
    provider: PaymentMethod
    success: bool
    refund_id: Optional[str] = None
    response: Optional[Any] = None
