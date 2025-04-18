from datetime import datetime, timezone

from bot.database.main import firebase
from bot.database.models.transaction import Transaction


async def update_transaction(transaction_id: str, data: dict):
    transaction_ref = firebase.db.collection(Transaction.COLLECTION_NAME).document(
        transaction_id
    )
    data["edited_at"] = datetime.now(timezone.utc)

    await transaction_ref.update(data)
