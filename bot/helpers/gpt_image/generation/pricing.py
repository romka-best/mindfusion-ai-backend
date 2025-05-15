from decimal import Decimal
from types import MappingProxyType

from bot.helpers.gpt_image.version import Version


class Pricing:
    _PRICING = MappingProxyType({
        Version.V1: {
            "input": {
                "image": Decimal("10.00") / Decimal("1000000.00"),
                "text": Decimal("5.00") / Decimal("1000000.00"),
            },
            "output": {"image": Decimal("40.00") / Decimal("1000000.00")},
        },
    })

    @classmethod
    def get(cls, version, token_usage_data):
        pricing = cls._PRICING[version]

        return (
            pricing["input"]["text"] * token_usage_data.input_tokens_details.text_tokens
            + pricing["input"]["image"] * token_usage_data.input_tokens_details.image_tokens
            + pricing["output"]["image"] * token_usage_data.output_tokens
        )
