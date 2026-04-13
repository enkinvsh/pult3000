from unittest.mock import AsyncMock, MagicMock

import pytest

from src.browser_player import BrowserPlayer, TrackInfo


class TestTrackInfo:
    def test_to_dict(self):
        info = TrackInfo(
            video_id="abc123",
            title="Test Song",
            artist="Test Artist",
            is_playing=True,
        )
        d = info.to_dict()
        assert d["currentTrack"]["id"] == "abc123"
        assert d["currentTrack"]["title"] == "Test Song"
        assert d["currentTrack"]["artist"] == "Test Artist"
        assert d["isPlaying"] is True


class TestBrowserPlayer:
    def test_init_with_proxy(self):
        player = BrowserPlayer(proxy_url="socks5://127.0.0.1:7890")
        assert player._proxy_url == "socks5://127.0.0.1:7890"

    def test_init_without_proxy(self):
        player = BrowserPlayer()
        assert player._proxy_url is None


class TestBrowserPlayerControls:
    @pytest.fixture
    def player_with_page(self):
        player = BrowserPlayer()
        player._page = MagicMock()
        player._context = MagicMock()
        return player

    async def test_get_player_info_returns_dict(self, player_with_page):
        player_with_page._page.evaluate = AsyncMock(
            return_value={
                "currentTrack": {
                    "id": "vid123",
                    "videoId": "vid123",
                    "title": "Song",
                    "artist": "Artist",
                },
                "isPlaying": True,
            }
        )

        info = await player_with_page.get_player_info()

        assert info["currentTrack"]["videoId"] == "vid123"
        assert info["isPlaying"] is True

    async def test_get_player_info_returns_none_on_error(self, player_with_page):
        player_with_page._page.evaluate = AsyncMock(side_effect=Exception("JS error"))

        info = await player_with_page.get_player_info()

        assert info is None

    async def test_play_video_navigates_to_url(self, player_with_page):
        player_with_page._page.goto = AsyncMock()
        mock_locator = MagicMock()
        mock_locator.count = AsyncMock(return_value=0)
        player_with_page._page.locator.return_value = mock_locator

        await player_with_page.play_video("dQw4w9WgXcQ")

        player_with_page._page.goto.assert_called_once()
        call_args = player_with_page._page.goto.call_args[0][0]
        assert "dQw4w9WgXcQ" in call_args
