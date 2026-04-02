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
