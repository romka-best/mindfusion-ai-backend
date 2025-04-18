from datetime import datetime
from typing import Optional

from bot.database.main import firebase
from bot.database.models.common import Currency, PaymentMethod
from bot.database.models.package import Package, PackageStatus
from bot.database.operations.package.helpers import create_package_object


async def write_package(
    package_id: Optional[str],
    user_id: str,
    product_id: str,
    status: PackageStatus,
    currency: Currency,
    amount: float,
    income_amount: float,
    quantity: int,
    payment_method: PaymentMethod,
    provider_payment_charge_id: Optional[str],
    until_at: datetime = None,
) -> Package:
    package = await create_package_object(
        package_id,
        user_id,
        product_id,
        status,
        currency,
        amount,
        income_amount,
        quantity,
        payment_method,
        provider_payment_charge_id,
        until_at,
    )
    await (
        firebase.db.collection(Package.COLLECTION_NAME)
        .document(package.id)
        .set(package.to_dict())
    )

    return package
