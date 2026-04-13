"""Playlist queue management."""

import logging
import random
from dataclasses import dataclass, field

from src.music_search import SearchResult

logger = logging.getLogger(__name__)


@dataclass
class PlayQueue:
    tracks: list[SearchResult] = field(default_factory=list)
    index: int = 0
    shuffled: bool = True

    def set_playlist(self, tracks: list[SearchResult], shuffle: bool = True) -> None:
        self.tracks = list(tracks)
        if shuffle:
            random.shuffle(self.tracks)
        self.index = 0
        self.shuffled = shuffle
        logger.info("Queue set: %d tracks", len(self.tracks))

    def current(self) -> SearchResult | None:
        if not self.tracks or self.index >= len(self.tracks):
            return None
        return self.tracks[self.index]

    def next(self) -> SearchResult | None:
        if not self.tracks:
            return None
        self.index = (self.index + 1) % len(self.tracks)
        track = self.tracks[self.index]
        logger.info(
            "Queue next: [%d/%d] %s - %s",
            self.index + 1,
            len(self.tracks),
            track.artist,
            track.title,
        )
        return track

    def prev(self) -> SearchResult | None:
        if not self.tracks:
            return None
        self.index = (self.index - 1) % len(self.tracks)
        track = self.tracks[self.index]
        logger.info(
            "Queue prev: [%d/%d] %s - %s",
            self.index + 1,
            len(self.tracks),
            track.artist,
            track.title,
        )
        return track

    def is_active(self) -> bool:
        return len(self.tracks) > 0


queue = PlayQueue()
