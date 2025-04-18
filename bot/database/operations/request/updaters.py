from datetime import datetime, timezone

from bot.database.main import firebase
from bot.database.models.request import Request


async def update_request(request_id: str, data: dict):
    request_ref = firebase.db.collection(Request.COLLECTION_NAME).document(request_id)
    data["edited_at"] = datetime.now(timezone.utc)

    await request_ref.update(data)
