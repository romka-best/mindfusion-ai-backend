from typing import BinaryIO
from bot.database.models.photo_bundle.photo import Photo
from dataclasses import dataclass


@dataclass
class PhotoBinaryUpload:
    __photo: Photo
    file: BinaryIO

    @property
    def id(self) -> int:
        return self.__photo.id

    @property
    def tg_id(self) -> str:
        return self.__photo.tg_id

    @property
    def file_format(self) -> str:
        return self.__photo.file_format

    @property
    def file_name(self) -> str:
        return self.__photo.file_name
