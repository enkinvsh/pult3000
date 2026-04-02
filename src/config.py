from dataclasses import dataclass
from os import environ
from pathlib import Path

from dotenv import load_dotenv

load_dotenv()


@dataclass(frozen=True)
class Config:
    bot_token: str
    admin_id: int
    whisper_model: str
    project_root: Path

    @classmethod
    def from_env(cls) -> "Config":
        token = environ.get("BOT_TOKEN")
        if not token:
            raise ValueError("BOT_TOKEN not set")

        admin_id = environ.get("ADMIN_ID")
        if not admin_id:
            raise ValueError("ADMIN_ID not set")

        return cls(
            bot_token=token,
            admin_id=int(admin_id),
            whisper_model=environ.get("WHISPER_MODEL", "base"),
            project_root=Path(__file__).parent.parent,
        )
