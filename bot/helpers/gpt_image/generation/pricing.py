from decimal import Decimal
from types import MappingProxyType

from bot.helpers.gpt_image.user.settings.quality import Quality
from bot.helpers.gpt_image.user.settings.size import Size


class Pricing:
    _PRICING = MappingProxyType({
        (Size.SQUARE, Quality.LOW): Decimal("0.011"),
        (Size.SQUARE, Quality.MEDIUM): Decimal("0.042"),
        (Size.SQUARE, Quality.HIGH): Decimal("0.167"),
        (Size.PORTRAIT, Quality.LOW): Decimal("0.016"),
        (Size.PORTRAIT, Quality.MEDIUM): Decimal("0.063"),
        (Size.PORTRAIT, Quality.HIGH): Decimal("0.25"),
        (Size.LANDSCAPE, Quality.LOW): Decimal("0.016"),
        (Size.LANDSCAPE, Quality.MEDIUM): Decimal("0.063"),
        (Size.LANDSCAPE, Quality.HIGH): Decimal("0.25"),
    })

    def __getitem__(self, key: tuple[Size, Quality]) -> float:
        return self._PRICING[key]
