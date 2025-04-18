import asyncio

from bot.database.main import firebase
from bot.database.models.chat import Chat
from bot.database.operations.message.getters import get_messages_by_chat_id
from bot.database.operations.message.updaters import update_message


async def delete_chat(chat_id: str) -> None:
    chat_ref = firebase.db.collection(Chat.COLLECTION_NAME).document(chat_id)
    await chat_ref.delete()


async def reset_chat(chat_id: str) -> None:
    chat_messages_ref = await get_messages_by_chat_id(chat_id, 0)
    tasks = []
    for chat_message_ref in chat_messages_ref:
        tasks.append(
            update_message(
                chat_message_ref.id,
                {
                    "is_in_context": False,
                },
            )
        )
    await asyncio.gather(*tasks)
