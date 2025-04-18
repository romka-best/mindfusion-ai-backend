from datetime import datetime
from typing import Optional

from google.cloud.firestore_v1 import FieldFilter, Query

from bot.database.main import firebase
from bot.database.models.transaction import Transaction


async def get_transaction(transaction_id: str) -> Optional[Transaction]:
    transaction_ref = firebase.db.collection(Transaction.COLLECTION_NAME).document(
        str(transaction_id)
    )
    transaction = await transaction_ref.get()

    if transaction.exists:
        return Transaction(**transaction.to_dict())


async def get_last_transaction_by_user(user_id: str) -> Optional[Transaction]:
    transaction_stream = (
        firebase.db.collection(Transaction.COLLECTION_NAME)
        .where(filter=FieldFilter("user_id", "==", user_id))
        .order_by("created_at", direction=Query.DESCENDING)
        .limit(1)
        .stream()
    )

    async for transaction_doc in transaction_stream:
        return Transaction(**transaction_doc.to_dict())


async def get_transactions_by_product_id_and_created_time(
    product_id: str,
    created_time: datetime,
    is_payment=False,
) -> list[Transaction]:
    start_date = created_time.replace(
        hour=0,
        minute=0,
        second=0,
        microsecond=0,
    )
    end_date = created_time.replace(
        hour=23,
        minute=59,
        second=59,
        microsecond=999999,
    )

    transaction_query = (
        firebase.db.collection(Transaction.COLLECTION_NAME)
        .where(filter=FieldFilter("product_id", "==", product_id))
        .where(filter=FieldFilter("created_at", ">=", start_date))
        .where(filter=FieldFilter("created_at", "<=", end_date))
    )

    if is_payment:
        transaction_query = transaction_query.where(
            filter=FieldFilter("details.type", "==", "payment")
        )

    transaction_stream = transaction_query.stream()

    return [
        Transaction(**transaction.to_dict()) async for transaction in transaction_stream
    ]
