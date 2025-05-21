from bot.database.models.common import PaymentMethod


class RefundService:
    def __init__(self, providers: dict):
        self.providers = providers

    async def execute(self, payment_provider: PaymentMethod, charge_id: str, **kwargs):
        provider = self.providers.get(payment_provider)
        if not provider:
            raise ValueError("Unknown payment provider")  # noqa: EM101
        return await provider.execute(charge_id, **kwargs)
