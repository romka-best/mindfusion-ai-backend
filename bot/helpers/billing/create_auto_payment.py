import json
import logging
import uuid

import aiohttp
from aiohttp import BasicAuth
from yookassa import Configuration

from bot.config import config
from bot.database.models.common import Currency, PaymentMethod
from bot.helpers.billing.create_payment import OrderItem
from bot.locales.types import LanguageCode

Configuration.account_id = config.YOOKASSA_ACCOUNT_ID.get_secret_value()
Configuration.secret_key = config.YOOKASSA_SECRET_KEY.get_secret_value()


async def create_auto_payment(
    payment_method: PaymentMethod,
    provider_auto_payment_charge_id: str,
    user_id: str,
    description: str,
    amount: float,
    language_code: LanguageCode,
    order_items: list[OrderItem],
) -> dict:
    if payment_method == PaymentMethod.YOOKASSA:
        url = "https://api.yookassa.ru/v3/payments"
        headers = {
            "Content-Type": "application/json",
            "Idempotence-Key": str(uuid.uuid4()),
        }
        items = []
        for order_item in order_items:
            product, price, quantity = (
                order_item.product,
                order_item.price,
                order_item.quantity,
            )
            items.append(
                {
                    "amount": {
                        "value": price,
                        "currency": Currency.RUB,
                    },
                    "description": product.names.get(language_code),
                    "vat_code": 1,
                    "quantity": quantity,
                }
            )
        payload = {
            "amount": {
                "value": amount,
                "currency": Currency.RUB,
            },
            "capture": True,
            "payment_method_id": provider_auto_payment_charge_id,
            "description": description,
            "merchant_customer_id": user_id,
            "receipt": {
                "customer": {
                    "full_name": user_id,
                    "email": "me@romandanilov.com",
                },
                "items": items,
            },
        }

        async with aiohttp.ClientSession(
            auth=BasicAuth(Configuration.account_id, Configuration.secret_key)
        ) as session:
            async with session.post(
                url, headers=headers, data=json.dumps(payload)
            ) as response:
                body = await response.json()
                logging.info(body)
                if response.ok:
                    return body
    else:
        raise NotImplementedError(f"Payment method is not defined: {payment_method}")
