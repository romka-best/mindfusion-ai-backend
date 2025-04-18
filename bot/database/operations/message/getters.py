from typing import Optional

from google.cloud.firestore_v1 import FieldFilter, Query

from bot.database.main import firebase
from bot.database.models.message import Message


async def get_message(message_id: str) -> Optional[Message]:
    message_ref = firebase.db.collection(Message.COLLECTION_NAME).document(message_id)
    message = await message_ref.get()

    if message.exists:
        message_dict = message.to_dict()
        return Message(
            id=message_dict.get("id"),
            chat_id=message_dict.get("chat_id"),
            sender=message_dict.get("sender"),
            sender_id=message_dict.get("sender_id"),
            content=message_dict.get("content"),
            is_in_context=message_dict.get("is_in_context"),
            photo_filenames=message_dict.get("photo_filenames"),
            created_at=message_dict.get("created_at"),
            edited_at=message_dict.get("edited_at"),
        )


async def get_messages() -> list[Message]:
    messages = firebase.db.collection(Message.COLLECTION_NAME).stream()

    return [
        Message(
            id=message.to_dict().get("id"),
            chat_id=message.to_dict().get("chat_id"),
            sender=message.to_dict().get("sender"),
            sender_id=message.to_dict().get("sender_id"),
            content=message.to_dict().get("content"),
            is_in_context=message.to_dict().get("is_in_context"),
            photo_filenames=message.to_dict().get("photo_filenames"),
            created_at=message.to_dict().get("created_at"),
            edited_at=message.to_dict().get("edited_at"),
        )
        async for message in messages
    ]


async def get_messages_by_chat_id(
    chat_id: str, limit=10, is_in_context=True
) -> list[Message]:
    messages_query = firebase.db.collection(Message.COLLECTION_NAME).where(
        filter=FieldFilter("chat_id", "==", chat_id)
    )
    if is_in_context is not None:
        messages_query = messages_query.where(
            filter=FieldFilter("is_in_context", "==", is_in_context)
        )
    if limit > 0:
        messages_query = messages_query.limit(limit)
    messages_stream = messages_query.order_by(
        "created_at", direction=Query.DESCENDING
    ).stream()

    messages = [
        Message(
            id=message.to_dict().get("id"),
            chat_id=message.to_dict().get("chat_id"),
            sender=message.to_dict().get("sender"),
            sender_id=message.to_dict().get("sender_id"),
            content=message.to_dict().get("content"),
            is_in_context=message.to_dict().get("is_in_context"),
            photo_filenames=message.to_dict().get("photo_filenames"),
            created_at=message.to_dict().get("created_at"),
            edited_at=message.to_dict().get("edited_at"),
        )
        async for message in messages_stream
    ]

    return messages
