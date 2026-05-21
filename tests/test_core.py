import pytest
from unittest.mock import patch, MagicMock, AsyncMock

from bot.core import create_bot, PokeBot


class TestCreateBot:
    def test_returns_pokebot_instance(self):
        config = {"prefix": "!", "token": "fake"}
        bot = create_bot(config)
        assert isinstance(bot, PokeBot)

    def test_custom_prefix(self):
        config = {"prefix": "?", "token": "fake"}
        bot = create_bot(config)
        assert bot.command_prefix == "?"

    def test_default_prefix(self):
        config = {"token": "fake"}
        bot = create_bot(config)
        assert bot.command_prefix == "!"

    def test_intents_include_message_content(self):
        config = {"prefix": "!", "token": "fake"}
        bot = create_bot(config)
        assert bot.intents.message_content is True

    def test_config_stored(self):
        config = {"prefix": "!", "token": "fake", "session_channel_id": 12345}
        bot = create_bot(config)
        assert bot.config["session_channel_id"] == 12345


class TestPokeBotState:
    def test_initial_maps_empty(self):
        config = {"prefix": "!", "token": "fake"}
        bot = create_bot(config)
        assert bot.version_map == {}
        assert bot.session_map == {}

    def test_initial_service_none(self):
        config = {"prefix": "!", "token": "fake"}
        bot = create_bot(config)
        assert bot.poke_service is None
        assert bot.http_session is None
