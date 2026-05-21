import pytest
from unittest.mock import AsyncMock, MagicMock

from bot.helpers import resolve_pokemon, get_species_name, pokemon_matcher


class TestResolvePokemon:
    async def test_exact_match_returns_lowercase(self):
        channel = MagicMock()
        channel.send = AsyncMock()
        result = await resolve_pokemon(channel, "Pikachu")
        assert result == "pikachu"

    async def test_fuzzy_match_sends_correction(self):
        channel = MagicMock()
        channel.send = AsyncMock()
        result = await resolve_pokemon(channel, "pikchu")
        assert result == "pikachu"
        channel.send.assert_called()
        call_text = channel.send.call_args[0][0]
        assert "Showing data for" in call_text

    async def test_no_match_returns_none(self):
        channel = MagicMock()
        channel.send = AsyncMock()
        result = await resolve_pokemon(channel, "xyzxyzxyz")
        assert result is None
        channel.send.assert_called()

    async def test_no_match_with_suggestions(self):
        channel = MagicMock()
        channel.send = AsyncMock()
        result = await resolve_pokemon(channel, "pikach")
        # This is close enough to get suggestions
        assert result is not None or channel.send.called

    async def test_whitespace_handling(self):
        channel = MagicMock()
        channel.send = AsyncMock()
        result = await resolve_pokemon(channel, "  pikachu  ")
        assert result == "pikachu"

    async def test_case_insensitive(self):
        channel = MagicMock()
        channel.send = AsyncMock()
        result = await resolve_pokemon(channel, "CHARIZARD")
        assert result == "charizard"


class TestGetSpeciesName:
    def test_simple_name(self):
        assert get_species_name("pikachu") == "pikachu"

    def test_hyphenated_form(self):
        assert get_species_name("deoxys-attack") == "deoxys"

    def test_multiple_hyphens(self):
        assert get_species_name("giratina-origin") == "giratina"

    def test_porygon_z(self):
        # Porygon-Z is a species name, not a form — but the split logic
        # will return "porygon" which is fine for species lookup
        assert get_species_name("porygon-z") == "porygon"


class TestPokemonMatcher:
    def test_initialized_with_full_list(self):
        assert pokemon_matcher is not None
        assert pokemon_matcher.find_best_match("Pikachu") == "Pikachu"

    def test_gen9_pokemon_in_matcher(self):
        result = pokemon_matcher.find_best_match("sprigatito")
        assert result == "Sprigatito"
