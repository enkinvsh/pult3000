from enum import Enum


class PlaybackMode(Enum):
    RADIO = "radio"
    ARTIST = "artist"


current: PlaybackMode = PlaybackMode.RADIO
