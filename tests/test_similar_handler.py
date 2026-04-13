from src.music_search import MusicSearcher, SearchResult


class TestSearchResult:
    def test_dataclass_fields(self):
        result = SearchResult(
            video_id="abc123", title="Test Song", artist="Test Artist"
        )
        assert result.video_id == "abc123"
        assert result.title == "Test Song"
        assert result.artist == "Test Artist"


class TestMusicSearcherPlaylist:
    def test_can_instantiate(self):
        searcher = MusicSearcher()
        assert searcher is not None
        assert hasattr(searcher, "get_playlist_tracks")
