import stripe

from bot.config import config
from bot.database.models.common import PaymentMethod
from bot.helpers.billing.refund.providers.statuses.stripe_refund_status import StripeRefundStatus
from bot.helpers.billing.refund.refund_result import RefundResult

stripe.api_key = config.STRIPE_SECRET_KEY.get_secret_value()


class StripeRefund:
    async def execute(self, charge_id: str, **kwargs):  # noqa: ARG002
        refund = await stripe.Refund.create_async(charge=charge_id)
        is_success = refund.status == StripeRefundStatus.SUCCEEDED

        return RefundResult(provider=PaymentMethod.STRIPE, success=is_success, refund_id=refund.id, response=refund)
