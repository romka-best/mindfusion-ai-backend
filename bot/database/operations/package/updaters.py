from datetime import datetime, timezone

from bot.database.main import firebase
from bot.database.models.package import Package


async def update_package(package_id: str, data: dict):
    package_ref = firebase.db.collection(Package.COLLECTION_NAME).document(package_id)
    data["edited_at"] = datetime.now(timezone.utc)

    await package_ref.update(data)


async def update_package_in_transaction(transaction, package_id: str, data: dict):
    data["edited_at"] = datetime.now(timezone.utc)

    transaction.update(
        firebase.db.collection(Package.COLLECTION_NAME).document(package_id), data
    )
