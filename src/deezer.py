import logging
from dataclasses import dataclass

import aiohttp

logger = logging.getLogger(__name__)

_API_BASE = "https://api.deezer.com"


@dataclass
class SimilarTrack:
    name: str
    artist: str


class DeezerRecommender:
    async def get_similar(
        self, artist: str, title: str, limit: int = 10
    ) -> list[SimilarTrack]:
        async with aiohttp.ClientSession() as session:
            async with session.get(
                f"{_API_BASE}/search/artist", params={"q": artist, "limit": 1}
            ) as resp:
                if resp.status != 200:
                    logger.warning("Deezer artist search error: %s", resp.status)
                    return []
                data = await resp.json()

            artists = data.get("data", [])
            if not artists:
                logger.warning("Deezer: artist not found: %s", artist)
                return []

            artist_id = artists[0].get("id")
            if not artist_id:
                return []

            async with session.get(f"{_API_BASE}/artist/{artist_id}/radio") as resp:
                if resp.status != 200:
                    logger.warning("Deezer radio error: %s", resp.status)
                    return []
                radio_data = await resp.json()

            radio_tracks = radio_data.get("data", [])
            if not radio_tracks:
                logger.warning("Deezer: no radio tracks for artist %s", artist)
                return []

            results = []
            seen = set()
            original_artist_lower = artist.lower()

            for track in radio_tracks:
                track_artist = track.get("artist", {}).get("name", "")
                track_title = track.get("title", "")

                if track_artist.lower() == original_artist_lower:
                    continue
                key = f"{track_artist.lower()}|{track_title.lower()}"
                if key in seen:
                    continue
                seen.add(key)

                results.append(SimilarTrack(name=track_title, artist=track_artist))
                if len(results) >= limit:
                    break

            logger.info(
                "Deezer radio for '%s': got %d similar tracks", artist, len(results)
            )
            return results
