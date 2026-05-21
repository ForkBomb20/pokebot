import pytest
from unittest.mock import patch
import os

from config.config import load_config


class TestLoadConfig:
    @patch("config.config.load_dotenv")
    @patch.dict(os.environ, {"DISCORD_TOKEN": "test-token", "COMMAND_PREFIX": "?", "SESSION_CHANNEL_ID": "123456"})
    def test_loads_all_fields(self, mock_dotenv):
        config = load_config()
        assert config["token"] == "test-token"
        assert config["prefix"] == "?"
        assert config["session_channel_id"] == 123456

    @patch("config.config.load_dotenv")
    @patch.dict(os.environ, {"DISCORD_TOKEN": "test-token"}, clear=True)
    def test_default_prefix(self, mock_dotenv):
        config = load_config()
        assert config["prefix"] == "!"

    @patch("config.config.load_dotenv")
    @patch.dict(os.environ, {"DISCORD_TOKEN": "test-token"}, clear=True)
    def test_no_session_channel_is_none(self, mock_dotenv):
        config = load_config()
        assert config["session_channel_id"] is None

    @patch("config.config.load_dotenv")
    @patch.dict(os.environ, {"DISCORD_TOKEN": "test-token"}, clear=True)
    def test_default_session_persist_path(self, mock_dotenv):
        config = load_config()
        assert config["session_persist_path"] == "data/sessions.json"

    @patch("config.config.load_dotenv")
    @patch.dict(os.environ, {}, clear=True)
    def test_missing_token_returns_none(self, mock_dotenv):
        config = load_config()
        assert config["token"] is None

    @patch("config.config.load_dotenv")
    @patch.dict(os.environ, {"DISCORD_TOKEN": "t"}, clear=True)
    def test_assets_path_set(self, mock_dotenv):
        config = load_config()
        assert "assets" in config["assets_path"]
