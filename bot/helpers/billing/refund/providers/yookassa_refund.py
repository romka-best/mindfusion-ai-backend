import asyncio
from decimal import ROUND_HALF_UP, Decimal

from yookassa import Configuration, Refund

from bot.config import config
from bot.database.models.common import Currency, PaymentMethod
from bot.helpers.billing.refund.providers.statuses.yookassa_refund_status import YookassaRefundStatus
from bot.helpers.billing.refund.refund_result import RefundResult

Configuration.configure(config.YOOKASSA_ACCOUNT_ID.get_secret_value(), config.YOOKASSA_SECRET_KEY.get_secret_value())


class YookassaRefund:
    async def execute(self, charge_id: str, amount: Decimal, currency: Currency, **kwargs):  # noqa: ARG002
        response = await asyncio.to_thread(
            lambda: Refund.create({
                "payment_id": charge_id,
                "amount": {
                    "value": str(amount.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)),
                    "currency": currency,
                },
            }),
        )
        is_success = response.status == YookassaRefundStatus.SUCCEEDED

        return RefundResult(
            provider=PaymentMethod.YOOKASSA,
            success=is_success,
            refund_id=response.id,
            response=response,
        )
