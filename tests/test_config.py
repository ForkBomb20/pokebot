import pytest
from unittest.mock import patch
import os

from config.config import load_config


class TestLoadConfig:
    @patch.dict(os.environ, {"DISCORD_TOKEN": "test-token-123", "COMMAND_PREFIX": "?"})
    def test_loads_token_from_env(self):
        config = load_config()
        assert config["token"] == "test-token-123"

    @patch.dict(os.environ, {"DISCORD_TOKEN": "test-token-123", "COMMAND_PREFIX": "?"})
    def test_loads_prefix_from_env(self):
        config = load_config()
        assert config["prefix"] == "?"

    @patch.dict(os.environ, {"DISCORD_TOKEN": "test-token-123"}, clear=False)
    def test_default_prefix(self):
        os.environ.pop("COMMAND_PREFIX", None)
        config = load_config()
        assert config["prefix"] == "!"

    @patch.dict(os.environ, {"DISCORD_TOKEN": "test-token-123"})
    def test_assets_path_exists(self):
        config = load_config()
        assert "assets_path" in config
        assert "assets" in config["assets_path"]

    @patch.dict(os.environ, {"DISCORD_TOKEN": "test-token-123"})
    def test_returns_dict(self):
        config = load_config()
        assert isinstance(config, dict)

    @patch("config.config.load_dotenv")
    @patch.dict(os.environ, {}, clear=True)
    def test_missing_token_returns_none(self, mock_dotenv):
        config = load_config()
        assert config["token"] is None
