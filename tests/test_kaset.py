import json
import plistlib
from unittest.mock import AsyncMock, patch

import pytest

from src.kaset import KasetController


@pytest.fixture
def kaset():
    return KasetController()


def _make_plist(video_id="abc123", title="Test Song", artist="Test Artist", volume=0.5):
    session = {
        "currentVideoId": video_id,
        "duration": 200,
        "progress": 42,
        "currentIndex": 0,
        "queue": [
            {
                "title": title,
                "artists": [{"name": artist}],
                "videoId": video_id,
                "duration": 200,
                "id": video_id,
            }
        ],
    }
    data = {
        "kaset.saved.playbackSession": json.dumps(session).encode(),
        "playerVolume": volume,
    }
    return plistlib.dumps(data).decode()


class TestKasetControls:
    @patch("src.kaset._key_code", new_callable=AsyncMock)
    async def test_playpause(self, mock_kc, kaset):
        await kaset.playpause()
        mock_kc.assert_called_once_with(49)

    @patch("src.kaset._key_code", new_callable=AsyncMock)
    async def test_next_track(self, mock_kc, kaset):
        await kaset.next_track()
        mock_kc.assert_called_once_with(124, "command down")

    @patch("src.kaset._key_code", new_callable=AsyncMock)
    async def test_previous_track(self, mock_kc, kaset):
        await kaset.previous_track()
        mock_kc.assert_called_once_with(123, "command down")

    @patch("src.kaset._keystroke", new_callable=AsyncMock)
    async def test_toggle_shuffle(self, mock_ks, kaset):
        await kaset.toggle_shuffle()
        mock_ks.assert_called_once_with("s", "command down")

    @patch("src.kaset._keystroke", new_callable=AsyncMock)
    async def test_like_track(self, mock_ks, kaset):
        await kaset.like_track()
        mock_ks.assert_called_once_with("l", "command down")

    @patch("src.kaset._run", new_callable=AsyncMock)
    async def test_play_video(self, mock_run, kaset):
        await kaset.play_video("dQw4w9WgXcQ")
        mock_run.assert_called_once_with(["open", "kaset://play?v=dQw4w9WgXcQ"])


class TestGetPlayerInfo:
    @patch("src.kaset._run", new_callable=AsyncMock)
    async def test_returns_track_info(self, mock_run, kaset):
        mock_run.return_value = _make_plist("abc123", "Test Song", "Test Artist", 0.75)

        info = await kaset.get_player_info()

        assert info["currentTrack"]["name"] == "Test Song"
        assert info["currentTrack"]["artist"] == "Test Artist"
        assert info["currentTrack"]["videoId"] == "abc123"
        assert info["volume"] == 75
        assert info["duration"] == 200
        assert info["position"] == 42

    @patch("src.kaset._run", new_callable=AsyncMock)
    async def test_returns_none_on_error(self, mock_run, kaset):
        mock_run.side_effect = RuntimeError("no defaults")

        info = await kaset.get_player_info()

        assert info is None

    @patch("src.kaset._run", new_callable=AsyncMock)
    async def test_returns_none_on_empty_session(self, mock_run, kaset):
        data = {"playerVolume": 0.5}
        mock_run.return_value = plistlib.dumps(data).decode()

        info = await kaset.get_player_info()

        assert info is None

    @patch("src.kaset._run", new_callable=AsyncMock)
    async def test_unknown_artist_when_no_artists(self, mock_run, kaset):
        session = {
            "currentVideoId": "x",
            "duration": 100,
            "progress": 0,
            "currentIndex": 0,
            "queue": [
                {
                    "title": "T",
                    "artists": [],
                    "videoId": "x",
                    "duration": 100,
                    "id": "x",
                }
            ],
        }
        data = {
            "kaset.saved.playbackSession": json.dumps(session).encode(),
            "playerVolume": 0.25,
        }
        mock_run.return_value = plistlib.dumps(data).decode()

        info = await kaset.get_player_info()

        assert info["currentTrack"]["artist"] == "Unknown"
        assert info["volume"] == 25
