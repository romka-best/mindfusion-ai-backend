from datetime import datetime, timezone

from bot.config import config


class Chat:
    COLLECTION_NAME = "chats"

    id: str
    user_id: str
    telegram_chat_id: str
    role_id: str
    title: str
    created_at: datetime
    edited_at: datetime

    def __init__(
        self,
        id: str,
        user_id: str,
        telegram_chat_id: str,
        title: str,
        role_id=None,
        created_at=None,
        edited_at=None,
        **kwargs,
    ):
        self.id = str(id)
        self.user_id = user_id
        self.telegram_chat_id = str(telegram_chat_id)
        self.title = title
        self.role_id = role_id if role_id else config.DEFAULT_ROLE_ID.get_secret_value()

        current_time = datetime.now(timezone.utc)
        self.created_at = created_at if created_at is not None else current_time
        self.edited_at = edited_at if edited_at is not None else current_time

    def to_dict(self):
        return vars(self)
