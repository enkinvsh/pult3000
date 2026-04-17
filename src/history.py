import json
import logging
from pathlib import Path

logger = logging.getLogger(__name__)

HISTORY_PATH = Path.home() / ".pult3000" / "history.json"
MAX_ITEMS = 30


def load() -> list[dict]:
    try:
        data = json.loads(HISTORY_PATH.read_text())
        return data if isinstance(data, list) else []
    except FileNotFoundError:
        return []
    except Exception as e:
        logger.warning("Could not load history: %s", e)
        return []


def add(video_id: str, title: str, artist: str) -> None:
    if not video_id:
        return
    items = load()
    items = [i for i in items if i.get("videoId") != video_id]
    items.insert(0, {"videoId": video_id, "title": title, "artist": artist})
    items = items[:MAX_ITEMS]
    try:
        HISTORY_PATH.parent.mkdir(parents=True, exist_ok=True)
        HISTORY_PATH.write_text(json.dumps(items, ensure_ascii=False))
    except Exception as e:
        logger.warning("Could not save history: %s", e)


def recent(limit: int = 20) -> list[dict]:
    return load()[:limit]
