from datetime import datetime
from typing import Optional

from google.cloud.firestore_v1 import FieldFilter

from bot.database.main import firebase
from bot.database.models.chat import Chat
from bot.database.operations.user.getters import get_user


async def get_chat(chat_id: str) -> Optional[Chat]:
    chat_ref = firebase.db.collection(Chat.COLLECTION_NAME).document(str(chat_id))
    chat = await chat_ref.get()

    if chat.exists:
        return Chat(**chat.to_dict())
    return None


async def get_chat_by_user_id(user_id: str) -> Optional[Chat]:
    user = await get_user(user_id)

    if user:
        chat = await get_chat(user.current_chat_id)
        return chat


async def get_chats(
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None,
) -> list[Chat]:
    chats_query = firebase.db.collection(Chat.COLLECTION_NAME)

    if start_date:
        chats_query = chats_query.where(
            filter=FieldFilter("created_at", ">=", start_date)
        )
    if end_date:
        chats_query = chats_query.where(
            filter=FieldFilter("created_at", "<=", end_date)
        )

    chats = chats_query.stream()
    return [Chat(**chat.to_dict()) async for chat in chats]


async def get_chats_by_user_id(user_id: str) -> list[Chat]:
    chats_query = firebase.db.collection(Chat.COLLECTION_NAME).where(
        filter=FieldFilter("user_id", "==", user_id)
    )
    chats = [Chat(**chat.to_dict()) async for chat in chats_query.stream()]

    return chats
