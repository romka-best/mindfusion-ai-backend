from datetime import datetime, timezone
from typing import Optional, ClassVar

from pydantic import BaseModel, Field


class Campaign(BaseModel):
    COLLECTION_NAME: ClassVar[str] = 'campaigns'

    id: str
    utm: dict
    discount: int
    created_at: Optional[datetime] = Field(default_factory=lambda: datetime.now(timezone.utc))
    edited_at: Optional[datetime] = Field(default_factory=lambda: datetime.now(timezone.utc))

    def to_dict(self):
        return vars(self)
