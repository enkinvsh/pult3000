import pytest
from src.config import Config


@pytest.fixture
def config():
    return Config(
        bot_token="test-token",
        admin_id=123456,
        whisper_model="tiny",
        project_root="/tmp/test",
    )
