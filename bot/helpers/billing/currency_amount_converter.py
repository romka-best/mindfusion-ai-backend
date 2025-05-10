from decimal import ROUND_HALF_UP, Decimal


class CurrencyAmountConverter:
    CURRENCY_MULTIPLIERS = {
        "USD": 100,
        "RUB": 100,
        "EUR": 100,
        "INR": 100,
        "GBP": 100,
    }

    def __init__(self, currency: str):
        self.currency = currency.upper()
        self.multiplier = self.CURRENCY_MULTIPLIERS.get(self.currency)
        if not self.multiplier:
            raise ValueError(f"Unsupported currency: {self.currency}")

    def to_smallest_unit(self, amount: Decimal) -> int:
        return int((amount * Decimal(self.multiplier)).to_integral_value(rounding=ROUND_HALF_UP))

    def from_smallest_unit(self, amount: int) -> Decimal:
        return Decimal(amount) / Decimal(self.multiplier)

