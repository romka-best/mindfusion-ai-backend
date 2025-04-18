from datetime import datetime, timezone

from bot.locales.types import LanguageCode


class Role:
    COLLECTION_NAME = "roles"

    id: str
    translated_names: dict[LanguageCode, str]
    translated_descriptions: dict[LanguageCode, str]
    translated_instructions: dict[LanguageCode, str]
    photo: str
    created_at: datetime
    edited_at: datetime

    def __init__(
        self,
        id: str,
        translated_names: dict[LanguageCode, str],
        translated_descriptions: dict[LanguageCode, str],
        translated_instructions: dict[LanguageCode, str],
        photo: str,
        created_at=None,
        edited_at=None,
        **kwargs,
    ):
        self.id = id
        self.translated_names = translated_names
        self.translated_descriptions = translated_descriptions
        self.translated_instructions = translated_instructions
        self.photo = photo

        current_time = datetime.now(timezone.utc)
        self.created_at = created_at if created_at is not None else current_time
        self.edited_at = edited_at if edited_at is not None else current_time

    def to_dict(self):
        return vars(self)
