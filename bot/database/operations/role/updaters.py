from datetime import datetime, timezone

from bot.database.main import firebase
from bot.database.models.role import Role


async def update_role(role_id: str, data: dict):
    role_ref = firebase.db.collection(Role.COLLECTION_NAME).document(role_id)
    data["edited_at"] = datetime.now(timezone.utc)

    await role_ref.update(data)
