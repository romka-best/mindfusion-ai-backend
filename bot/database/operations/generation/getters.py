from datetime import datetime
from typing import Optional

from google.cloud.firestore_v1 import FieldFilter, Query

from bot.database.main import firebase
from bot.database.models.generation import Generation, GenerationReaction


async def get_generation(generation_id: str) -> Optional[Generation]:
    generation_ref = firebase.db.collection(Generation.COLLECTION_NAME).document(
        str(generation_id)
    )
    generation = await generation_ref.get()

    if generation.exists:
        return Generation(**generation.to_dict())


async def get_generations_by_request_id(request_id: str) -> list[Generation]:
    generations_stream = (
        firebase.db.collection(Generation.COLLECTION_NAME)
        .where(filter=FieldFilter("request_id", "==", request_id))
        .order_by("created_at", direction=Query.DESCENDING)
        .stream()
    )
    generations = [
        Generation(**generation.to_dict()) async for generation in generations_stream
    ]

    return generations


async def get_count_of_generations(
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None,
    reaction: Optional[GenerationReaction] = None,
    product_id: Optional[str] = None,
    action: Optional[str] = None,
) -> int:
    generations_query = firebase.db.collection(Generation.COLLECTION_NAME)

    if start_date:
        generations_query = generations_query.where(
            filter=FieldFilter("created_at", ">=", start_date)
        )
    if end_date:
        generations_query = generations_query.where(
            filter=FieldFilter("created_at", "<=", end_date)
        )
    if reaction:
        generations_query = generations_query.where(
            filter=FieldFilter("reaction", "==", reaction)
        )
    if product_id:
        generations_query = generations_query.where(
            filter=FieldFilter("product_id", "==", product_id)
        )
    if action:
        generations_query = generations_query.where(
            filter=FieldFilter("details.action", "==", action)
        )

    generations_query = await generations_query.count().get()

    return int(generations_query[0][0].value)
