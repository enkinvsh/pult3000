import json
import logging
from pathlib import Path

logger = logging.getLogger(__name__)

STATE_PATH = Path.home() / ".pult3000" / "state.json"


def load() -> dict:
    try:
        return json.loads(STATE_PATH.read_text())
    except FileNotFoundError:
        return {}
    except Exception as e:
        logger.warning("Could not load state: %s", e)
        return {}


def save(data: dict) -> None:
    try:
        STATE_PATH.parent.mkdir(parents=True, exist_ok=True)
        STATE_PATH.write_text(json.dumps(data))
    except Exception as e:
        logger.warning("Could not save state: %s", e)
