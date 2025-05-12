from .bg_transparent import BgTransparent
from .compression import Compression
from .quality import Quality
from .size import Size


class Manager:
    _registry = {"size": Size, "quality": Quality, "bg_transparent": BgTransparent, "compression": Compression}

    @classmethod
    def __get_item__(cls, key):
        return cls._registry[key]
