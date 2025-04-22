from dataclasses import dataclass
from .photo import Photo


@dataclass
class PhotoBundle:
    photos: list[Photo]
