from bot.database.main import firebase
from bot.database.models.request import Request, RequestStatus
from bot.database.operations.request.helpers import create_request_object


async def write_request(
    user_id: str,
    processing_message_ids: list[int],
    product_id: str,
    requested: int,
    status=RequestStatus.STARTED,
    details=None,
) -> Request:
    request = await create_request_object(
        user_id,
        processing_message_ids,
        product_id,
        requested,
        status,
        details,
    )
    await (
        firebase.db.collection(Request.COLLECTION_NAME)
        .document(request.id)
        .set(request.to_dict())
    )

    return request
