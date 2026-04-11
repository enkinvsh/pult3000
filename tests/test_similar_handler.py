from src.bot.handlers.similar import _page_items, _cached_similar
from src.music_search import SearchResult


class TestSimilarPageItems:
    def setup_method(self):
        _cached_similar.clear()

    def test_page_items_returns_correct_slice(self):
        for i in range(12):
            _cached_similar.append(
                SearchResult(
                    video_id=f"vid{i}",
                    title=f"Track {i}",
                    artist=f"Artist {i}",
                    duration="3:00",
                )
            )

        items = _page_items(0)
        assert len(items) == 5
        assert items[0][0] == "vid0"
        assert items[4][0] == "vid4"

        items = _page_items(1)
        assert len(items) == 5
        assert items[0][0] == "vid5"

        items = _page_items(2)
        assert len(items) == 2
        assert items[0][0] == "vid10"

    def test_page_items_empty_cache(self):
        items = _page_items(0)
        assert items == []

    def test_page_items_out_of_range(self):
        _cached_similar.append(
            SearchResult(video_id="v1", title="T", artist="A", duration="1:00")
        )
        items = _page_items(5)
        assert items == []
