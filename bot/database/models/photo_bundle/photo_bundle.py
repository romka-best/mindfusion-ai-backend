from dataclasses import dataclass
from .photo import Photo


@dataclass
class PhotoBundle:
    photos: list[Photo]

    def is_empty(self):
        return not bool(len(self.photos))
