from bot.database.main import firebase
from bot.database.models.message import Message
from bot.database.operations.message.helpers import create_message_object


async def write_message(
    chat_id: str,
    sender: str,
    sender_id: str,
    content: str,
    is_in_context=True,
    photo_filenames=None,
) -> Message:
    message = await create_message_object(
        chat_id, sender, sender_id, content, is_in_context, photo_filenames
    )
    await (
        firebase.db.collection(Message.COLLECTION_NAME)
        .document(message.id)
        .set(message.to_dict())
    )

    return message


async def write_message_in_transaction(
    transaction,
    chat_id: str,
    sender: str,
    sender_id: str,
    content: str,
    is_in_context=True,
    photo_filenames=None,
) -> Message:
    message = await create_message_object(
        chat_id, sender, sender_id, content, is_in_context, photo_filenames
    )
    transaction.set(
        firebase.db.collection(Message.COLLECTION_NAME).document(message.id),
        message.to_dict(),
    )

    return message
