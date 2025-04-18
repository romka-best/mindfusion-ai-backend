from bot.database.main import firebase
from bot.database.models.common import Currency
from bot.database.models.transaction import Transaction, TransactionType
from bot.database.operations.transaction.helpers import create_transaction_object


async def write_transaction(
    user_id: str,
    type: TransactionType,
    product_id: str,
    amount: float,
    clear_amount: float,
    currency: Currency,
    quantity=1,
    details=None,
    created_at=None,
) -> Transaction:
    transaction = await create_transaction_object(
        user_id,
        type,
        product_id,
        amount,
        clear_amount,
        currency,
        quantity,
        details,
        created_at,
    )
    await (
        firebase.db.collection(Transaction.COLLECTION_NAME)
        .document(transaction.id)
        .set(transaction.to_dict())
    )

    return transaction


async def write_transaction_in_transaction(
    transaction,
    user_id: str,
    type: TransactionType,
    product_id: str,
    amount: float,
    clear_amount: float,
    currency: Currency,
    quantity=1,
    details=None,
    created_at=None,
) -> Transaction:
    transaction_object = await create_transaction_object(
        user_id,
        type,
        product_id,
        amount,
        clear_amount,
        currency,
        quantity,
        details,
        created_at,
    )
    transaction.set(
        firebase.db.collection(Transaction.COLLECTION_NAME).document(
            transaction_object.id
        ),
        transaction_object.to_dict(),
    )

    return transaction_object
