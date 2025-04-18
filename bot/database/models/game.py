from datetime import datetime, timezone
from enum import StrEnum


class GameType(StrEnum):
    BOWLING = "BOWLING"
    SOCCER = "SOCCER"
    BASKETBALL = "BASKETBALL"
    DARTS = "DARTS"
    DICE = "DICE"
    CASINO = "CASINO"


class GameStatus(StrEnum):
    LOST = "LOST"
    WON = "WON"


class Game:
    COLLECTION_NAME = "games"

    id: str
    user_id: str
    type: GameType
    status: GameStatus
    reward: int
    created_at: datetime
    edited_at: datetime

    def __init__(
        self,
        id: str,
        user_id: str,
        type: GameType,
        status: GameStatus,
        reward=0,
        created_at=None,
        edited_at=None,
    ):
        self.id = id
        self.user_id = user_id
        self.type = type
        self.status = status
        self.reward = reward

        current_time = datetime.now(timezone.utc)
        self.created_at = created_at if created_at is not None else current_time
        self.edited_at = edited_at if edited_at is not None else current_time

    def to_dict(self):
        return vars(self)
