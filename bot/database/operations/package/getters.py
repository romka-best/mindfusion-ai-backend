from datetime import datetime
from typing import Optional

from google.cloud.firestore_v1 import FieldFilter

from bot.database.main import firebase
from bot.database.models.package import Package, PackageStatus


async def get_package(package_id: str) -> Optional[Package]:
    package_ref = firebase.db.collection(Package.COLLECTION_NAME).document(
        str(package_id)
    )
    package = await package_ref.get()

    if package.exists:
        return Package(**package.to_dict())


async def get_packages_by_provider_payment_charge_id(
    provider_payment_charge_id: str,
) -> list[Package]:
    packages = (
        firebase.db.collection(Package.COLLECTION_NAME)
        .where(
            filter=FieldFilter(
                "provider_payment_charge_id", "==", provider_payment_charge_id
            )
        )
        .stream()
    )

    return [Package(**package.to_dict()) async for package in packages]


async def get_packages(
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None,
) -> list[Package]:
    packages_query = firebase.db.collection(Package.COLLECTION_NAME)

    if start_date:
        packages_query = packages_query.where(
            filter=FieldFilter("created_at", ">=", start_date)
        )
    if end_date:
        packages_query = packages_query.where(
            filter=FieldFilter("created_at", "<=", end_date)
        )

    packages = packages_query.stream()

    return [Package(**package.to_dict()) async for package in packages]


async def get_packages_by_user_id_and_status(
    user_id: str, status: PackageStatus
) -> list[Package]:
    packages_query = (
        firebase.db.collection(Package.COLLECTION_NAME)
        .where(filter=FieldFilter("user_id", "==", user_id))
        .where(filter=FieldFilter("status", "==", status))
    )

    packages = packages_query.stream()

    return [Package(**package.to_dict()) async for package in packages]


async def get_packages_by_user_id(user_id: str) -> list[Package]:
    packages_query = firebase.db.collection(Package.COLLECTION_NAME).where(
        filter=FieldFilter("user_id", "==", user_id)
    )

    packages = packages_query.stream()

    return [Package(**package.to_dict()) async for package in packages]
