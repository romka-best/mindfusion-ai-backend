from bot.database.models.common import PaymentMethod
from bot.helpers.billing.refund.refund_result import RefundResult


class TelegramStarsRefund:
    def __init__(self, bot, user_id):
        self.bot = bot
        self.user_id = user_id

    async def execute(self, charge_id: str, **kwargs):  # noqa: ARG002
        is_success = await self.bot.refund_star_payment(user_id=self.user_id, telegram_payment_charge_id=charge_id)

        return RefundResult(provider=PaymentMethod.TELEGRAM_STARS, success=is_success)
