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
    def __init__(self, proxy_url: str | None = None) -> None:
        proxies = {"https": proxy_url, "http": proxy_url} if proxy_url else None
        self._ytm = YTMusic(proxies=proxies)

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

    def get_similar(self, video_id: str, limit: int = 20) -> list[SearchResult]:
        try:
            watch = self._ytm.get_watch_playlist(
                videoId=video_id, radio=True, limit=limit + 1
            )
        except Exception as e:
            logger.error("get similar tracks failed: %s", e)
            return []

        results: list[SearchResult] = []
        for item in watch.get("tracks", []):
            vid = item.get("videoId")
            if not vid or vid == video_id:
                continue
            artists = item.get("artists", [])
            artist_name = artists[0]["name"] if artists else "Unknown"
            results.append(
                SearchResult(
                    video_id=vid,
                    title=item.get("title", "Unknown"),
                    artist=artist_name,
                    duration=item.get("length"),
                )
            )
        return results[:limit]

    def get_playlist_tracks(self, artist: str, limit: int = 50) -> list[SearchResult]:
        try:
            playlists = self._ytm.search(artist, filter="playlists", limit=5)
            if not playlists:
                logger.warning("No playlists found for: %s", artist)
                return []

            for pl in playlists:
                playlist_id = pl.get("browseId")
                if not playlist_id:
                    continue

                playlist_data = self._ytm.get_playlist(playlist_id, limit=limit)
                tracks = playlist_data.get("tracks", [])

                results = []
                for item in tracks:
                    vid = item.get("videoId")
                    if not vid:
                        continue
                    artists = item.get("artists", [])
                    artist_name = artists[0]["name"] if artists else "Unknown"
                    results.append(
                        SearchResult(
                            video_id=vid,
                            title=item.get("title", "Unknown"),
                            artist=artist_name,
                            duration=item.get("duration"),
                        )
                    )

                if results:
                    logger.info(
                        "Found %d tracks in playlist '%s' for artist %s",
                        len(results),
                        pl.get("title"),
                        artist,
                    )
                    return results

            return []
        except Exception as e:
            logger.error("get playlist tracks failed: %s", e)
            return []
