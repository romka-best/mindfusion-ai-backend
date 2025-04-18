from datetime import datetime
from typing import Optional

from google.cloud.firestore_v1 import FieldFilter

from bot.database.main import firebase
from bot.database.models.request import Request, RequestStatus


async def get_request(request_id: str) -> Optional[Request]:
    request_ref = firebase.db.collection(Request.COLLECTION_NAME).document(
        str(request_id)
    )
    request = await request_ref.get()

    if request.exists:
        return Request(**request.to_dict())


async def get_requests() -> list[Request]:
    requests = firebase.db.collection(Request.COLLECTION_NAME).stream()

    return [Request(**request.to_dict()) async for request in requests]


async def get_started_requests(
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None,
) -> list[Request]:
    requests_query = firebase.db.collection(Request.COLLECTION_NAME)

    if start_date:
        requests_query = requests_query.where(
            filter=FieldFilter("created_at", ">=", start_date)
        )
    if end_date:
        requests_query = requests_query.where(
            filter=FieldFilter("created_at", "<=", end_date)
        )
    requests_query = requests_query.where(
        filter=FieldFilter("status", "==", RequestStatus.STARTED)
    )

    requests = [
        Request(**request.to_dict()) async for request in requests_query.stream()
    ]

    return requests


async def get_started_requests_by_user_id_and_product_id(
    user_id: str, product_id: str
) -> list[Request]:
    requests_stream = (
        firebase.db.collection(Request.COLLECTION_NAME)
        .where(filter=FieldFilter("user_id", "==", user_id))
        .where(filter=FieldFilter("status", "==", RequestStatus.STARTED))
        .where(filter=FieldFilter("product_id", "==", product_id))
        .stream()
    )

    requests = [Request(**request.to_dict()) async for request in requests_stream]

    return requests
