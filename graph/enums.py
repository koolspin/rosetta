from enum import Enum


class PadDirection(Enum):
    """
    Defines the direction of a pad
    """
    UNKNOWN = 0
    SOURCE = 1
    SRC = 1
    SINK = 2


class PadPresence(Enum):
    """
    Defines the presence or availability of a pad
    """
    ALWAYS = 0
    SOMETIMES = 1
    REQUEST = 2


class CapabilitiesType(Enum):
    """
    Defines the caps type - match normal, match any, match none
    """
    MATCH_NONE = -1
    MATCH_NORMAL = 0
    MATCH_ANY = 1

