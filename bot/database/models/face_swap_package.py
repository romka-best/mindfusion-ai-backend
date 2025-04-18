from datetime import datetime, timezone
from typing import TypedDict

from bot.database.models.user import UserGender


class FaceSwapPackageStatus:
    PUBLIC = "PUBLIC"
    PRIVATE = "PRIVATE"
    LEGACY = "LEGACY"


class FaceSwapFileData(TypedDict):
    name: str
    status: FaceSwapPackageStatus


class FaceSwapPackage:
    COLLECTION_NAME = "face_swap_packages"

    id: str
    name: str
    translated_names: dict
    gender: UserGender
    files: list[FaceSwapFileData]
    status: FaceSwapPackageStatus
    created_at: datetime
    edited_at: datetime

    def __init__(
        self,
        id: str,
        name: str,
        translated_names: dict,
        gender: UserGender,
        files: list[FaceSwapFileData],
        status: FaceSwapPackageStatus,
        created_at=None,
        edited_at=None,
    ):
        self.id = id
        self.name = name
        self.translated_names = translated_names
        self.gender = gender
        self.files = files
        self.status = status

        current_time = datetime.now(timezone.utc)
        self.created_at = created_at if created_at is not None else current_time
        self.edited_at = edited_at if edited_at is not None else current_time

    def to_dict(self):
        return vars(self)


class UsedFaceSwapPackage:
    COLLECTION_NAME = "used_face_swap_packages"

    id: str
    user_id: str
    package_id: str
    used_images: list[str]
    created_at: datetime
    edited_at: datetime

    def __init__(
        self,
        id: str,
        user_id: str,
        package_id: str,
        used_images: list[str],
        created_at=None,
        edited_at=None,
    ):
        self.id = id
        self.user_id = user_id
        self.package_id = package_id
        self.used_images = used_images

        current_time = datetime.now(timezone.utc)
        self.created_at = created_at if created_at is not None else current_time
        self.edited_at = edited_at if edited_at is not None else current_time

    def to_dict(self):
        return vars(self)
