"""Browser-based YouTube Music player using Playwright."""

import asyncio
import logging
from dataclasses import dataclass
from pathlib import Path
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from playwright.async_api import BrowserContext, Page

logger = logging.getLogger(__name__)

# User data directory for persistent login
USER_DATA_DIR = Path.home() / ".pult3000" / "browser-data"


@dataclass
class TrackInfo:
    """Current track information."""

    video_id: str
    title: str
    artist: str
    is_playing: bool
    duration: str | None = None
    progress: str | None = None

    def to_dict(self) -> dict:
        return {
            "currentTrack": {
                "id": self.video_id,
                "videoId": self.video_id,
                "title": self.title,
                "artist": self.artist,
            },
            "isPlaying": self.is_playing,
        }


class BrowserPlayer:
    """Controls YouTube Music in a browser via Playwright."""

    def __init__(self, proxy_url: str | None = None) -> None:
        self._proxy_url = proxy_url
        self._context: "BrowserContext | None" = None
        self._page: "Page | None" = None
        self._playwright = None
        self._lock = asyncio.Lock()

    async def open(self) -> None:
        """Open browser and navigate to YouTube Music."""
        if self._page is not None:
            logger.debug("Browser already open")
            return

        from playwright.async_api import async_playwright

        self._playwright = await async_playwright().start()

        # Prepare launch options
        USER_DATA_DIR.mkdir(parents=True, exist_ok=True)

        launch_opts: dict = {
            "headless": False,
            "args": [
                "--autoplay-policy=no-user-gesture-required",
                "--disable-blink-features=AutomationControlled",
            ],
        }

        # Add proxy if configured
        if self._proxy_url:
            launch_opts["proxy"] = {"server": self._proxy_url}

        self._context = await self._playwright.chromium.launch_persistent_context(
            user_data_dir=str(USER_DATA_DIR),
            channel="chrome",
            **launch_opts,
        )

        pages = self._context.pages
        self._page = pages[0] if pages else await self._context.new_page()

        await self._context.add_init_script("""
            setInterval(() => {
                const video = document.querySelector('video');
                if (video) {
                    const vol = localStorage.getItem('pult_volume');
                    if (vol !== null) video.volume = parseFloat(vol);
                }
            }, 100);
        """)

        await self._page.goto(
            "https://music.youtube.com", wait_until="domcontentloaded"
        )
        logger.info("Browser opened, navigated to YouTube Music")

        await asyncio.sleep(2)

    async def close(self) -> None:
        """Close the browser."""
        if self._context:
            await self._context.close()
            self._context = None
            self._page = None
        if self._playwright:
            await self._playwright.stop()
            self._playwright = None
        logger.info("Browser closed")

    async def _ensure_open(self) -> "Page":
        """Ensure browser is open and return the page."""
        async with self._lock:
            if self._page is None:
                await self.open()
            return self._page  # type: ignore

    async def search_and_play_playlist(self, artist: str) -> bool:
        """Search for artist playlist and start playing."""
        page = await self._ensure_open()

        try:
            # Click search button
            search_btn = page.locator('tp-yt-paper-icon-button[aria-label="Search"]')
            if await search_btn.count() > 0:
                await search_btn.click()
                await asyncio.sleep(0.5)

            # Type in search box
            search_input = page.locator('input[aria-label="Search"]')
            await search_input.fill(f"{artist} playlist")
            await search_input.press("Enter")
            await asyncio.sleep(2)

            # Click on "Playlists" filter chip if available
            playlists_chip = page.locator(
                'yt-chip-cloud-chip-renderer:has-text("Playlists")'
            )
            if await playlists_chip.count() > 0:
                await playlists_chip.first.click()
                await asyncio.sleep(1)

            # Click first playlist result
            playlist_card = page.locator(
                'ytmusic-card-shelf-renderer a[href*="playlist"]'
            ).first
            if await playlist_card.count() > 0:
                await playlist_card.click()
                await asyncio.sleep(2)

                # Click shuffle play button
                shuffle_btn = page.locator('tp-yt-paper-button:has-text("Shuffle")')
                if await shuffle_btn.count() > 0:
                    await shuffle_btn.first.click()
                    logger.info("Started playlist for: %s", artist)
                    return True

            # Fallback: click any play button
            play_btn = page.locator("ytmusic-play-button-renderer").first
            if await play_btn.count() > 0:
                await play_btn.click()
                logger.info("Started playback for: %s (fallback)", artist)
                return True

            logger.warning("Could not find playlist to play for: %s", artist)
            return False

        except Exception as e:
            logger.error("Failed to search and play playlist: %s", e)
            return False

    async def play_video(self, video_id: str) -> None:
        """Navigate to and play a specific video."""
        page = await self._ensure_open()

        url = f"https://music.youtube.com/watch?v={video_id}"
        await page.goto(url, wait_until="domcontentloaded")
        await asyncio.sleep(2)

        await self._click_play_if_paused(page)
        logger.info("Playing video: %s", video_id)

    async def _click_play_if_paused(self, page: "Page") -> None:
        """Click play button if video is paused."""
        play_btn = page.locator(
            'tp-yt-paper-icon-button.play-pause-button[aria-label="Play"]'
        )
        if await play_btn.count() > 0:
            await play_btn.click()

    async def play(self) -> None:
        """Resume playback."""
        page = await self._ensure_open()
        await self._click_play_if_paused(page)

    async def pause(self) -> None:
        """Pause playback."""
        page = await self._ensure_open()
        pause_btn = page.locator(
            'tp-yt-paper-icon-button.play-pause-button[aria-label="Pause"]'
        )
        if await pause_btn.count() > 0:
            await pause_btn.click()

    async def playpause(self) -> None:
        """Toggle play/pause."""
        page = await self._ensure_open()
        await page.keyboard.press(" ")
        logger.info("Toggled play/pause")

    async def next_track(self) -> None:
        """Skip to next track."""
        page = await self._ensure_open()
        await page.keyboard.press("Shift+N")
        logger.info("Skipped to next track")

    async def previous_track(self) -> None:
        """Go to previous track."""
        page = await self._ensure_open()
        await page.keyboard.press("Shift+P")
        logger.info("Went to previous track")

    async def toggle_shuffle(self) -> None:
        """Toggle shuffle mode."""
        page = await self._ensure_open()
        shuffle_btn = page.locator('tp-yt-paper-icon-button[aria-label*="shuffle" i]')
        if await shuffle_btn.count() > 0:
            await shuffle_btn.first.click()

    async def like_track(self) -> None:
        """Like current track."""
        page = await self._ensure_open()
        like_btn = page.locator(
            "ytmusic-like-button-renderer #button-shape-like button"
        )
        if await like_btn.count() > 0:
            await like_btn.click()

    async def set_volume(self, level: int) -> None:
        page = await self._ensure_open()
        vol = level / 100
        await page.evaluate(f"""
            localStorage.setItem('pult_volume', '{vol}');
            const video = document.querySelector('video');
            if (video) video.volume = {vol};
        """)
        logger.info("Volume set to %d%%", level)

    async def get_player_info(self) -> dict | None:
        """Get current player state."""
        page = await self._ensure_open()

        try:
            info = await page.evaluate(
                """
                () => {
                    const video = document.querySelector('video');
                    if (!video) return null;

                    // Try multiple selectors for title
                    const titleSelectors = [
                        'ytmusic-player-bar .title',
                        '.content-info-wrapper .title',
                        'yt-formatted-string.title',
                        '.title.ytmusic-player-bar',
                    ];
                    let title = '';
                    for (const sel of titleSelectors) {
                        const el = document.querySelector(sel);
                        if (el && el.textContent.trim()) {
                            title = el.textContent.trim();
                            break;
                        }
                    }

                    // Try multiple selectors for artist
                    const artistSelectors = [
                        'ytmusic-player-bar .subtitle a',
                        '.content-info-wrapper .subtitle a',
                        'span.subtitle yt-formatted-string a',
                        '.byline.ytmusic-player-bar a',
                        'ytmusic-player-bar .byline a',
                    ];
                    let artist = '';
                    for (const sel of artistSelectors) {
                        const el = document.querySelector(sel);
                        if (el && el.textContent.trim()) {
                            artist = el.textContent.trim();
                            break;
                        }
                    }

                    // Get video ID from URL
                    const url = new URL(window.location.href);
                    const videoId = url.searchParams.get('v') || '';

                    // Get play state
                    const isPlaying = !video.paused;

                    return {
                        currentTrack: {
                            id: videoId,
                            videoId: videoId,
                            title: title,
                            artist: artist,
                        },
                        isPlaying: isPlaying,
                        volume: Math.round(video.volume * 100),
                    };
                }
                """
            )
            return info
        except Exception as e:
            logger.warning("Failed to get player info: %s", e)
            return None
