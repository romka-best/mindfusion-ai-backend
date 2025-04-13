from typing import Optional

from bot.database.models.generation import GenerationStatus, GenerationReaction
from bot.database.operations.generation.getters import get_generations_by_request_id
from bot.database.operations.generation.updaters import update_generation
from bot.database.operations.generation.writers import write_generation


class GenerationGateway:
    async def get_all_by_request_id(self, request_id: str):
        return await get_generations_by_request_id(request_id)

    async def update(self, id: str, data: dict):
        return await update_generation(id, data)

    async def save(
        self,
        id: Optional[str],
        request_id: str,
        product_id: str,
        result="",
        has_error=False,
        status=GenerationStatus.STARTED,
        reaction=GenerationReaction.NONE,
        seconds=0,
        details=None,
    ):
        return await write_generation(
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
