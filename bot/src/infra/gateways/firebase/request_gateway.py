from bot.database.operations.request.updaters import update_request
from bot.database.operations.request.writers import write_request
from bot.database.operations.request.getters import (
    get_started_requests_by_user_id_and_product_id,
)
from bot.database.models.request import RequestStatus


class RequestGateway:
    async def save(
        self,
        user_id: str,
        processing_message_ids: list[int],
        product_id: str,
        requested: int,
        status=RequestStatus.STARTED,
        details=None,
    ):
        return await write_request(
            user_id=user_id,
            processing_message_ids=processing_message_ids,
            product_id=product_id,
            requested=requested,
            details=details,
        )

    async def update_status(self, request_id: str, status: str):
        return await update_request(request_id, {"status": status})

    async def get_started_by_user_id_and_product_id(
        self, user_id: str, product_id: str
    ):
        return await get_started_requests_by_user_id_and_product_id(user_id, product_id)
