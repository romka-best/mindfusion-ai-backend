from bot.database.models.generation import (
    Generation,
    GenerationReaction,
    GenerationStatus,
)


async def create_generation_object(
    id: str,
    request_id: str,
    product_id: str,
    result="",
    has_error=False,
    status=GenerationStatus.STARTED,
    reaction=GenerationReaction.NONE,
    seconds=0,
    details=None,
) -> Generation:
    return Generation(
        id=id,
        request_id=request_id,
        product_id=product_id,
        result=result,
        has_error=has_error,
        status=status,
        reaction=reaction,
        seconds=seconds,
        details=details,
    )
