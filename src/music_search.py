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

    def search_artist_tracks(self, query: str, limit: int = 20) -> list[SearchResult]:
        """Search for an artist and return their top tracks."""
        try:
            artists = self._ytm.search(query, filter="artists", limit=1)
            if not artists:
                return []
            artist_id = artists[0].get("browseId")
            if not artist_id:
                return []
            artist_data = self._ytm.get_artist(artist_id)
            songs = artist_data.get("songs", {}).get("results", [])
        except Exception as e:
            logger.error("artist track search failed: %s", e)
            return []

        results = []
        for item in songs[:limit]:
            if item.get("videoId"):
                artists_list = item.get("artists", [])
                artist_name = artists_list[0]["name"] if artists_list else "Unknown"
                results.append(
                    SearchResult(
                        video_id=item["videoId"],
                        title=item.get("title", "Unknown"),
                        artist=artist_name,
                        duration=item.get("duration"),
                    )
                )
        return results
