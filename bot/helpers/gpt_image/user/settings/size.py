from enum import Enum


class Size(str, Enum):
    SQUARE = "1024x1024"
    LANDSCAPE = "1536x1024"
    PORTRAIT = "1024x1536"
    AUTO = "auto"
