from datetime import datetime, timezone

from bot.database.main import firebase
from bot.database.models.generation import Generation


async def update_generation(generation_id: str, data: dict):
    generation_ref = firebase.db.collection(Generation.COLLECTION_NAME).document(
        generation_id
    )
    data["edited_at"] = datetime.now(timezone.utc)

    await generation_ref.update(data)
