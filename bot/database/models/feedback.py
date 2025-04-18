from datetime import datetime, timezone
from enum import StrEnum


class FeedbackStatus(StrEnum):
    WAITING = "WAITING"
    APPROVED = "APPROVED"
    DENIED = "DENIED"


class Feedback:
    COLLECTION_NAME = "feedbacks"

    id: str
    user_id: str
    content: str
    status: FeedbackStatus
    created_at: datetime
    edited_at: datetime

    def __init__(
        self,
        id: str,
        user_id: str,
        content: str,
        status=FeedbackStatus.WAITING,
        created_at=None,
        edited_at=None,
    ):
        self.id = id
        self.user_id = user_id
        self.content = content
        self.status = status

        current_time = datetime.now(timezone.utc)
        self.created_at = created_at if created_at is not None else current_time
        self.edited_at = edited_at if edited_at is not None else current_time

    def to_dict(self):
        return vars(self)
