from unittest.mock import MagicMock, patch

import pytest

from src.music_search import MusicSearcher, SearchResult


class TestMusicSearcher:
    @patch("src.music_search.YTMusic")
    def test_search_returns_results(self, mock_ytm_cls):
        mock_ytm = MagicMock()
        mock_ytm_cls.return_value = mock_ytm
        mock_ytm.search.return_value = [
            {
                "category": "Songs",
                "resultType": "song",
                "videoId": "abc123",
                "title": "Nothing Else Matters",
                "artists": [{"name": "Metallica"}],
                "duration": "6:28",
            },
            {
                "category": "Songs",
                "resultType": "song",
                "videoId": "def456",
                "title": "Enter Sandman",
                "artists": [{"name": "Metallica"}],
                "duration": "5:31",
            },
        ]

        searcher = MusicSearcher()
        results = searcher.search("Metallica Nothing Else Matters", limit=5)

        assert len(results) >= 1
        assert results[0].video_id == "abc123"
        assert results[0].title == "Nothing Else Matters"
        assert results[0].artist == "Metallica"

    @patch("src.music_search.YTMusic")
    def test_search_returns_empty_on_no_results(self, mock_ytm_cls):
        mock_ytm = MagicMock()
        mock_ytm_cls.return_value = mock_ytm
        mock_ytm.search.return_value = []

        searcher = MusicSearcher()
        results = searcher.search("asjkdhaksjdhaksjdh")
        assert results == []

    @patch("src.music_search.YTMusic")
    def test_search_filters_songs_only(self, mock_ytm_cls):
        mock_ytm = MagicMock()
        mock_ytm_cls.return_value = mock_ytm
        mock_ytm.search.return_value = [
            {
                "category": "Songs",
                "resultType": "song",
                "videoId": "abc123",
                "title": "Song",
                "artists": [{"name": "Artist"}],
                "duration": "3:00",
            },
        ]

        searcher = MusicSearcher()
        results = searcher.search("test", limit=5)
        mock_ytm.search.assert_called_once_with("test", filter="songs", limit=5)

    def test_search_result_display(self):
        r = SearchResult(
            video_id="abc",
            title="Nothing Else Matters",
            artist="Metallica",
            duration="6:28",
        )
        assert "Nothing Else Matters" in r.display
        assert "Metallica" in r.display
        assert "6:28" in r.display

    @patch("src.music_search.YTMusic")
    def test_get_similar_returns_results(self, mock_ytm_cls):
        mock_ytm = MagicMock()
        mock_ytm_cls.return_value = mock_ytm
        mock_ytm.get_watch_playlist.return_value = {
            "tracks": [
                {
                    "videoId": "current123",
                    "title": "Current Song",
                    "artists": [{"name": "Artist A"}],
                    "length": "3:30",
                },
                {
                    "videoId": "similar1",
                    "title": "Similar Song 1",
                    "artists": [{"name": "Artist B"}],
                    "length": "4:00",
                },
                {
                    "videoId": "similar2",
                    "title": "Similar Song 2",
                    "artists": [{"name": "Artist C"}],
                    "length": "3:15",
                },
            ],
            "playlistId": "RDAMVM...",
        }

        searcher = MusicSearcher()
        results = searcher.get_similar("current123", limit=10)

        assert len(results) == 2
        assert results[0].video_id == "similar1"
        assert results[0].title == "Similar Song 1"
        assert results[0].artist == "Artist B"
        assert results[0].duration == "4:00"
        mock_ytm.get_watch_playlist.assert_called_once_with(
            videoId="current123", radio=True, limit=11
        )

    @patch("src.music_search.YTMusic")
    def test_get_similar_skips_current_track(self, mock_ytm_cls):
        mock_ytm = MagicMock()
        mock_ytm_cls.return_value = mock_ytm
        mock_ytm.get_watch_playlist.return_value = {
            "tracks": [
                {
                    "videoId": "current123",
                    "title": "Current Song",
                    "artists": [{"name": "Artist A"}],
                    "length": "3:30",
                },
            ],
            "playlistId": "RDAMVM...",
        }

        searcher = MusicSearcher()
        results = searcher.get_similar("current123")

        assert results == []

    @patch("src.music_search.YTMusic")
    def test_get_similar_returns_empty_on_error(self, mock_ytm_cls):
        mock_ytm = MagicMock()
        mock_ytm_cls.return_value = mock_ytm
        mock_ytm.get_watch_playlist.side_effect = Exception("API error")

        searcher = MusicSearcher()
        results = searcher.get_similar("abc123")

        assert results == []

    @patch("src.music_search.YTMusic")
    def test_get_similar_returns_empty_when_no_tracks(self, mock_ytm_cls):
        mock_ytm = MagicMock()
        mock_ytm_cls.return_value = mock_ytm
        mock_ytm.get_watch_playlist.return_value = {
            "tracks": [],
            "playlistId": "RDAMVM...",
        }

        searcher = MusicSearcher()
        results = searcher.get_similar("abc123")

        assert results == []

    @patch("src.music_search.YTMusic")
    def test_get_similar_handles_missing_artists(self, mock_ytm_cls):
        mock_ytm = MagicMock()
        mock_ytm_cls.return_value = mock_ytm
        mock_ytm.get_watch_playlist.return_value = {
            "tracks": [
                {
                    "videoId": "no_artist",
                    "title": "Mystery Track",
                    "artists": [],
                    "length": "2:00",
                },
            ],
            "playlistId": "RDAMVM...",
        }

        searcher = MusicSearcher()
        results = searcher.get_similar("other_id")

        assert len(results) == 1
        assert results[0].artist == "Unknown"
