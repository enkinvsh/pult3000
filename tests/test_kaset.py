import json
from unittest.mock import AsyncMock, patch

import pytest

from src.kaset import KasetController


@pytest.fixture
def kaset():
    return KasetController()


class TestKasetCommands:
    @patch("src.kaset.run_osascript", new_callable=AsyncMock)
    async def test_play(self, mock_osa, kaset):
        await kaset.play()
        mock_osa.assert_called_once_with('tell application "Kaset" to play')

    @patch("src.kaset.run_osascript", new_callable=AsyncMock)
    async def test_pause(self, mock_osa, kaset):
        await kaset.pause()
        mock_osa.assert_called_once_with('tell application "Kaset" to pause')

    @patch("src.kaset.run_osascript", new_callable=AsyncMock)
    async def test_playpause(self, mock_osa, kaset):
        await kaset.playpause()
        mock_osa.assert_called_once_with('tell application "Kaset" to playpause')

    @patch("src.kaset.run_osascript", new_callable=AsyncMock)
    async def test_next_track(self, mock_osa, kaset):
        await kaset.next_track()
        mock_osa.assert_called_once_with('tell application "Kaset" to next track')

    @patch("src.kaset.run_osascript", new_callable=AsyncMock)
    async def test_previous_track(self, mock_osa, kaset):
        await kaset.previous_track()
        mock_osa.assert_called_once_with('tell application "Kaset" to previous track')

    @patch("src.kaset.run_osascript", new_callable=AsyncMock)
    async def test_set_volume(self, mock_osa, kaset):
        await kaset.set_volume(75)
        mock_osa.assert_called_once_with('tell application "Kaset" to set volume 75')

    @patch("src.kaset.run_osascript", new_callable=AsyncMock)
    async def test_set_volume_clamps_to_range(self, mock_osa, kaset):
        await kaset.set_volume(150)
        mock_osa.assert_called_once_with('tell application "Kaset" to set volume 100')

    @patch("src.kaset.run_osascript", new_callable=AsyncMock)
    async def test_toggle_shuffle(self, mock_osa, kaset):
        await kaset.toggle_shuffle()
        mock_osa.assert_called_once_with('tell application "Kaset" to toggle shuffle')

    @patch("src.kaset.run_osascript", new_callable=AsyncMock)
    async def test_like_track(self, mock_osa, kaset):
        await kaset.like_track()
        mock_osa.assert_called_once_with('tell application "Kaset" to like track')

    @patch("src.kaset.run_osascript", new_callable=AsyncMock)
    async def test_get_player_info(self, mock_osa, kaset):
        mock_osa.return_value = json.dumps(
            {
                "isPlaying": True,
                "currentTrack": {
                    "name": "Test Song",
                    "artist": "Test Artist",
                    "videoId": "abc123",
                },
            }
        )
        info = await kaset.get_player_info()
        assert info["isPlaying"] is True
        assert info["currentTrack"]["name"] == "Test Song"

    @patch("src.kaset.run_osascript", new_callable=AsyncMock)
    async def test_get_player_info_returns_none_on_error(self, mock_osa, kaset):
        mock_osa.side_effect = RuntimeError("Kaset not running")
        info = await kaset.get_player_info()
        assert info is None

    @patch("src.kaset.run_osascript", new_callable=AsyncMock)
    async def test_play_by_video_id(self, mock_osa, kaset):
        await kaset.play_video("dQw4w9WgXcQ")
        mock_osa.assert_called_once_with(
            'tell application "Kaset" to play video "dQw4w9WgXcQ"'
        )
