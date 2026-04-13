# Similar Tracks (YouTube Music Radio) Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Add a "📻" button that fetches similar tracks via `ytmusicapi.get_watch_playlist(radio=True)` and shows them as selectable inline buttons — identical UX to existing search results.

**Architecture:** New `get_similar()` method on existing `MusicSearcher` wraps the ytmusicapi call. New `similar.py` handler responds to the "📻" button, gets current track from Kaset, fetches similar tracks, and renders them with the existing `search_results_keyboard`. Reuses `SearchResult` dataclass and "play:" callback from search handler. Separate "sp:" prefix for pagination to avoid conflicts with search pagination.

**Tech Stack:** ytmusicapi `get_watch_playlist(radio=True)` (already installed), aiogram (already installed). Zero new dependencies.

---

## Context for Implementer

### Key Files
- `src/music_search.py` — `MusicSearcher` class, `SearchResult` dataclass. All ytmusicapi calls live here.
- `src/bot/handlers/search.py` — Search handler. Has `_cached_results`, pagination with "page:" prefix, track selection with "play:" prefix.
- `src/bot/handlers/controls.py` — Control buttons handler. `CONTROL_BUTTONS` set determines which texts the search handler ignores.
- `src/bot/keyboards.py` — `reply_keyboard()` (main button layout), `search_results_keyboard()` (inline results).
- `src/kaset.py` — `KasetController.get_player_info()` returns `{"currentTrack": {"videoId": "...", "name": "...", "artist": "..."}, "isPlaying": bool, "volume": int}`.
- `src/main.py` — Bot initialization. Routers registered in order: commands → controls → search.
- `src/bot/status.py` — `format_now_playing()`, `sync_poller()`.

### ytmusicapi Response Format (`get_watch_playlist`)
```python
ytm.get_watch_playlist(videoId="abc123", radio=True, limit=25)
# Returns:
{
    "tracks": [
        {
            "videoId": "9mWr4c_ig54",      # NOT "video_id"
            "title": "Foolish Of Me",
            "length": "3:07",               # NOT "duration"
            "artists": [{"name": "Seven Lions", "id": "UC..."}],
            "album": {"name": "Foolish Of Me", "id": "MPREb_..."},
            "likeStatus": "INDIFFERENT",
            "thumbnails": [...]
        },
        ...
    ],
    "playlistId": "RDAMVM4y33h81phKU",
    "lyrics": "MPLYt_HNNclO0Ddoc-17"
}
```

**Critical mapping:** `track["length"]` → `SearchResult.duration` (NOT `track["duration"]`).

**Current track is included** as the first item — must be skipped by filtering on `videoId`.

### Existing Patterns to Follow
- Error handling: `try/except Exception as e` + `logger.error(...)` + return empty list.
- Module-level cache: `_cached_results: list[SearchResult] = []` (single-user bot, admin-only).
- Message lifecycle: Delete user message → show results → user picks → delete results → play + update status.
- Tests: `unittest.mock.patch("src.music_search.YTMusic")` to mock the ytmusicapi instance.

---

## Task 1: Add `get_similar` method to `MusicSearcher`

**Files:**
- Modify: `src/music_search.py`
- Test: `tests/test_music_search.py`

### Step 1: Write the failing tests

Add to `tests/test_music_search.py` in `TestMusicSearcher` class:

```python
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
```

### Step 2: Run tests to verify they fail

Run: `pytest tests/test_music_search.py -v -k "similar"`
Expected: FAIL with `AttributeError: 'MusicSearcher' object has no attribute 'get_similar'`

### Step 3: Write the implementation

Add to `MusicSearcher` in `src/music_search.py`, after `search_artist_tracks`:

```python
def get_similar(self, video_id: str, limit: int = 20) -> list[SearchResult]:
    """Get similar tracks via YouTube Music radio algorithm."""
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
```

### Step 4: Run tests to verify they pass

Run: `pytest tests/test_music_search.py -v -k "similar"`
Expected: All 5 tests PASS

### Step 5: Commit

```bash
git add src/music_search.py tests/test_music_search.py
git commit -m "feat: add get_similar method to MusicSearcher via ytmusicapi radio"
```

---

## Task 2: Add `page_prefix` to keyboard + "📻" button

**Files:**
- Modify: `src/bot/keyboards.py`
- Modify: `src/bot/handlers/controls.py` (add "📻" to CONTROL_BUTTONS)
- Test: `tests/test_keyboards.py`

### Step 1: Write the failing tests

Add to `tests/test_keyboards.py`:

```python
from src.bot.keyboards import reply_keyboard, search_results_keyboard


class TestReplyKeyboard:
    def test_similar_button_present(self):
        kb = reply_keyboard()
        all_texts = [btn.text for row in kb.keyboard for btn in row]
        assert "📻" in all_texts


class TestSearchResultsKeyboard:
    def test_default_page_prefix(self):
        results = [("v1", "Track 1"), ("v2", "Track 2")]
        kb = search_results_keyboard(results, page=0, per_page=2, total=5)
        nav_row = kb.inline_keyboard[-1]
        assert nav_row[0].callback_data == "page:1"

    def test_custom_page_prefix(self):
        results = [("v1", "Track 1"), ("v2", "Track 2")]
        kb = search_results_keyboard(results, page=0, per_page=2, total=5, page_prefix="sp")
        nav_row = kb.inline_keyboard[-1]
        assert nav_row[0].callback_data == "sp:1"

    def test_prev_button_custom_prefix(self):
        results = [("v1", "Track 1")]
        kb = search_results_keyboard(results, page=1, per_page=1, total=3, page_prefix="sp")
        nav_row = kb.inline_keyboard[-1]
        assert nav_row[0].callback_data == "sp:0"

    def test_play_prefix_unchanged(self):
        results = [("vid123", "Track 1")]
        kb = search_results_keyboard(results, page=0, per_page=5, total=1, page_prefix="sp")
        assert kb.inline_keyboard[0][0].callback_data == "play:vid123"
```

### Step 2: Run tests to verify they fail

Run: `pytest tests/test_keyboards.py -v`
Expected: FAIL — `test_similar_button_present` and `test_custom_page_prefix` fail

### Step 3: Implement keyboard changes

**`src/bot/keyboards.py`** — add `page_prefix` parameter and "📻" button:

```python
from aiogram.types import (
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    KeyboardButton,
    ReplyKeyboardMarkup,
)


def reply_keyboard() -> ReplyKeyboardMarkup:
    return ReplyKeyboardMarkup(
        keyboard=[
            [
                KeyboardButton(text="⏮"),
                KeyboardButton(text="⏯"),
                KeyboardButton(text="⏭"),
            ],
            [
                KeyboardButton(text="🔀"),
                KeyboardButton(text="❤️"),
                KeyboardButton(text="📻"),
                KeyboardButton(text="🔇"),
                KeyboardButton(text="ℹ️"),
            ],
            [
                KeyboardButton(text="15%"),
                KeyboardButton(text="25%"),
                KeyboardButton(text="50%"),
                KeyboardButton(text="75%"),
                KeyboardButton(text="100%"),
            ],
        ],
        resize_keyboard=True,
    )


def search_results_keyboard(
    results: list[tuple[str, str]],
    page: int = 0,
    per_page: int = 5,
    total: int = 0,
    page_prefix: str = "page",
) -> InlineKeyboardMarkup:
    buttons = [
        [InlineKeyboardButton(text=display, callback_data=f"play:{vid}")]
        for vid, display in results
    ]
    nav = []
    if page > 0:
        nav.append(InlineKeyboardButton(text="◀️", callback_data=f"{page_prefix}:{page - 1}"))
    if (page + 1) * per_page < total:
        nav.append(InlineKeyboardButton(text="▶️", callback_data=f"{page_prefix}:{page + 1}"))
    if nav:
        buttons.append(nav)
    return InlineKeyboardMarkup(inline_keyboard=buttons)
```

**`src/bot/handlers/controls.py`** — add "📻" to CONTROL_BUTTONS set:

```python
CONTROL_BUTTONS = {
    "⏮",
    "⏯",
    "⏭",
    "🔀",
    "❤️",
    "📻",
    "🔇",
    "ℹ️",
    "15%",
    "25%",
    "50%",
    "75%",
    "100%",
}
```

### Step 4: Run tests to verify they pass

Run: `pytest tests/test_keyboards.py -v`
Expected: All tests PASS

### Step 5: Commit

```bash
git add src/bot/keyboards.py src/bot/handlers/controls.py tests/test_keyboards.py
git commit -m "feat: add radio button to keyboard, page_prefix param for pagination"
```

---

## Task 3: Create similar tracks handler

**Files:**
- Create: `src/bot/handlers/similar.py`
- Test: `tests/test_similar_handler.py` (basic unit test for now)

### Step 1: Write the handler

Create `src/bot/handlers/similar.py`:

```python
"""Similar tracks handler — YouTube Music radio recommendations."""

import logging

from aiogram import F, Router
from aiogram.types import CallbackQuery, Message

from src.bot.keyboards import search_results_keyboard
from src.kaset import KasetController
from src.music_search import MusicSearcher, SearchResult

logger = logging.getLogger(__name__)

router = Router(name="similar")

_PER_PAGE = 5
_cached_similar: list[SearchResult] = []


def _page_items(page: int) -> list[tuple[str, str]]:
    start = page * _PER_PAGE
    end = start + _PER_PAGE
    return [(r.video_id, r.display) for r in _cached_similar[start:end]]


def setup(kaset: KasetController, searcher: MusicSearcher) -> Router:

    @router.message(F.text == "📻")
    async def on_similar(message: Message) -> None:
        try:
            await message.delete()
        except Exception:
            pass

        info = await kaset.get_player_info()
        if not info or not info.get("currentTrack"):
            await message.answer("📻 Сейчас ничего не играет")
            return

        video_id = info["currentTrack"].get("videoId")
        if not video_id:
            await message.answer("📻 Не могу определить трек")
            return

        results = searcher.get_similar(video_id, limit=20)
        if not results:
            await message.answer("📻 Не нашёл похожих треков")
            return

        _cached_similar.clear()
        _cached_similar.extend(results)
        page = 0
        items = _page_items(page)
        track = info["currentTrack"]
        title = f"📻 Похожее на: {track.get('artist', '?')} — {track.get('name', '?')}"
        await message.answer(
            title,
            reply_markup=search_results_keyboard(
                items,
                page=page,
                per_page=_PER_PAGE,
                total=len(_cached_similar),
                page_prefix="sp",
            ),
        )

    @router.callback_query(F.data.startswith("sp:"))
    async def on_sim_page(cb: CallbackQuery) -> None:
        page = int(cb.data.split(":", 1)[1])
        items = _page_items(page)
        if not items:
            await cb.answer("Нет результатов")
            return
        await cb.answer()
        try:
            await cb.message.edit_reply_markup(
                reply_markup=search_results_keyboard(
                    items,
                    page=page,
                    per_page=_PER_PAGE,
                    total=len(_cached_similar),
                    page_prefix="sp",
                ),
            )
        except Exception:
            pass

    return router
```

### Step 2: Write a basic test

Create `tests/test_similar_handler.py`:

```python
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
```

### Step 3: Run tests

Run: `pytest tests/test_similar_handler.py -v`
Expected: All tests PASS

### Step 4: Commit

```bash
git add src/bot/handlers/similar.py tests/test_similar_handler.py
git commit -m "feat: add similar tracks handler with pagination"
```

---

## Task 4: Wire up in main.py

**Files:**
- Modify: `src/main.py`

### Step 1: Add the import and register router

In `src/main.py`, add the import:
```python
from src.bot.handlers import commands, controls, search, similar
```

Register the similar router **before** search (important — "📻" must be caught before the catch-all text handler in search):
```python
dp.include_router(commands.setup(kaset))
dp.include_router(controls.setup(kaset))
dp.include_router(similar.setup(kaset, searcher))  # Must be before search
dp.include_router(search.setup(kaset, searcher))
```

### Step 2: Commit

```bash
git add src/main.py
git commit -m "feat: wire up similar tracks handler in bot startup"
```

---

## Task 5: Run full test suite and verify

### Step 1: Run all tests

Run: `pytest tests/ -v`
Expected: All tests PASS (existing + new)

### Step 2: Run linter/type checks if configured

Run: `python -m py_compile src/bot/handlers/similar.py && python -m py_compile src/music_search.py`
Expected: No errors

### Step 3: Manual smoke test (if bot is running)

1. Start bot: `python -m src.main`
2. In Telegram, play any track via search
3. Press "📻" button
4. Verify: inline keyboard with similar tracks appears
5. Select a track → it plays
6. Test pagination if >5 results

### Step 4: Final commit (if any fixes needed)

```bash
git add -A
git commit -m "fix: address issues found during smoke test"
```

---

## Design Decisions & Tradeoffs

| Decision | Rationale |
|----------|-----------|
| Add to `MusicSearcher` (not new class) | All ytmusicapi logic in one place. Follows existing pattern. |
| Reuse `SearchResult` dataclass | Same fields (videoId, title, artist, duration). No reason for a new type. |
| Reuse `search_results_keyboard` | Same UX — inline buttons with pagination. Added `page_prefix` param for clean separation. |
| "play:" callback shared with search | Both do the same thing: play a video. Search handler already handles it. |
| "sp:" prefix for similar pagination | Avoids conflict with search "page:" prefix and their separate caches. |
| `📻` button in row 2 | Grouped with other mode/action buttons (🔀, ❤️, 🔇). Natural placement. |
| No authentication changes | `get_watch_playlist` works without auth for public tracks. If auth needed later, change `YTMusic()` → `YTMusic("oauth.json")` in one place. |
| Skip current track by videoId | `get_watch_playlist(radio=True)` includes current track as first item. Filter it out. |
| `limit + 1` in API call | Account for skipping current track so we still return the requested `limit` count. |
| Module-level `_cached_similar` | Same pattern as `_cached_results` in search.py. Fine for single-user admin bot. |
| Similar router before search router | Ensures "📻" exact match is caught before search's catch-all `F.text` handler. |

## What's NOT in This Plan (Future Phases)

- Last.fm API fallback (Phase 2)
- Caching/Redis (Phase 3)
- Listening history tracking (Phase 3)
- Personalized recommendations via LightFM (Phase 4)
- Auto-play next similar track when current ends
