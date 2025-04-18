from datetime import datetime
from typing import Optional

from google.cloud.firestore_v1 import FieldFilter, Query

from bot.database.main import firebase
from bot.database.models.role import Role


async def get_role(role_id: str) -> Optional[Role]:
    role_ref = firebase.db.collection(Role.COLLECTION_NAME).document(role_id)
    role = await role_ref.get()

    if role.exists:
        return Role(**role.to_dict())


async def get_roles(
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None,
) -> list[Role]:
    roles_query = firebase.db.collection(Role.COLLECTION_NAME)

    if start_date:
        roles_query = roles_query.where(
            filter=FieldFilter("created_at", ">=", start_date)
        )
    if end_date:
        roles_query = roles_query.where(
            filter=FieldFilter("created_at", "<=", end_date)
        )

    roles = roles_query.order_by("created_at", direction=Query.ASCENDING).stream()
    return [Role(**role.to_dict()) async for role in roles]
