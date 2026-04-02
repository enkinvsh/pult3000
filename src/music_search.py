"""YouTube Music search via ytmusicapi."""

import logging
from dataclasses import dataclass

from ytmusicapi import YTMusic

logger = logging.getLogger(__name__)


@dataclass
class SearchResult:
    video_id: str
    title: str
    artist: str
    duration: str | None = None

    @property
    def display(self) -> str:
        dur = f" ({self.duration})" if self.duration else ""
        return f"{self.artist} — {self.title}{dur}"


class MusicSearcher:
    def __init__(self) -> None:
        self._ytm = YTMusic()

    def search(self, query: str, limit: int = 5) -> list[SearchResult]:
        try:
            raw = self._ytm.search(query, filter="songs", limit=limit)
        except Exception as e:
            logger.error("ytmusicapi search failed: %s", e)
            return []

        results = []
        for item in raw:
            if item.get("videoId"):
                artists = item.get("artists", [])
                artist_name = artists[0]["name"] if artists else "Unknown"
                results.append(
                    SearchResult(
                        video_id=item["videoId"],
                        title=item.get("title", "Unknown"),
                        artist=artist_name,
                        duration=item.get("duration"),
                    )
                )
        return results
