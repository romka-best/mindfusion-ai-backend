from typing import Optional

from bot.database.main import firebase
from bot.database.models.generation import (
    Generation,
    GenerationReaction,
    GenerationStatus,
)
from bot.database.operations.generation.helpers import create_generation_object


async def write_generation(
    id: Optional[str],
    request_id: str,
    product_id: str,
    result="",
    has_error=False,
    status=GenerationStatus.STARTED,
    reaction=GenerationReaction.NONE,
    seconds=0,
    details=None,
) -> Generation:
    if not id:
        id = firebase.db.collection(Generation.COLLECTION_NAME).document().id

    generation = await create_generation_object(
        id,
        request_id,
        product_id,
        result,
        has_error,
        status,
        reaction,
        seconds,
        details,
    )
    await (
        firebase.db.collection(Generation.COLLECTION_NAME)
        .document(id)
        .set(generation.to_dict())
    )

    return generation
