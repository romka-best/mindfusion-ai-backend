from datetime import datetime, timezone
from enum import StrEnum


class RequestStatus(StrEnum):
    STARTED = "STARTED"
    FINISHED = "FINISHED"


class Request:
    COLLECTION_NAME = "requests"

    id: str
    user_id: str
    product_id: str
    requested: int
    processing_message_ids: list[int]
    status: RequestStatus
    details: dict
    created_at: datetime
    edited_at: datetime

    def __init__(
        self,
        id: str,
        user_id: str,
        product_id: str,
        requested: int,
        processing_message_ids: list[int] = None,
        status=RequestStatus.STARTED,
        details=None,
        created_at=None,
        edited_at=None,
        **kwargs,
    ):
        self.id = id
        self.user_id = user_id
        self.product_id = product_id
        self.requested = requested
        self.processing_message_ids = processing_message_ids
        self.status = status
        self.details = details if details is not None else {}

        current_time = datetime.now(timezone.utc)
        self.created_at = created_at if created_at is not None else current_time
        self.edited_at = edited_at if edited_at is not None else current_time

    def to_dict(self):
        return vars(self)
