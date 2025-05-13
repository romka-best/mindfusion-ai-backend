from enum import Enum

from .bg_transparent import BgTransparent
from .compression import Compression
from .quality import Quality
from .size import Size


class Settings(Enum):
    SIZE = Size
    QUALITY = Quality
    BG_TRANSPARENT = BgTransparent
    COMPRESSION = Compression
