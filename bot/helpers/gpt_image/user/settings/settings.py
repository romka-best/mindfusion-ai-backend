from enum import Enum

from .background import Background
from .compression import Compression
from .quality import Quality
from .size import Size


class Settings(Enum):
    SIZE = Size
    QUALITY = Quality
    BACKGROUND = Background
    COMPRESSION = Compression
