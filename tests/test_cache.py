import pytest
import os
import json
import tempfile
from unittest.mock import AsyncMock, MagicMock

from data.cache import PokeCache


class TestPokeCache:
    def test_pokemon_set_and_get(self):
        cache = PokeCache()
        cache.set_pokemon("pikachu", {"id": 25})
        assert cache.get_pokemon("pikachu") == {"id": 25}

    def test_pokemon_get_miss(self):
        cache = PokeCache()
        assert cache.get_pokemon("pikachu") is None

    def test_pokemon_case_insensitive(self):
        cache = PokeCache()
        cache.set_pokemon("Pikachu", {"id": 25})
        assert cache.get_pokemon("pikachu") == {"id": 25}

    def test_species_set_and_get(self):
        cache = PokeCache()
        cache.set_species("pikachu", {"name": "pikachu"})
        assert cache.get_species("pikachu")["name"] == "pikachu"

    def test_move_set_and_get(self):
        cache = PokeCache()
        url = "https://pokeapi.co/api/v2/move/85/"
        cache.set_move(url, {"name": "thunderbolt"})
        assert cache.get_move(url)["name"] == "thunderbolt"

    def test_type_set_and_get(self):
        cache = PokeCache()
        cache.set_type("electric", {"damage_relations": {}})
        assert cache.get_type("electric") is not None

    def test_growth_rate_get(self):
        cache = PokeCache()
        cache._growth_rates["pikachu"] = "Medium Fast"
        assert cache.get_growth_rate("pikachu") == "Medium Fast"

    def test_growth_rate_unknown(self):
        cache = PokeCache()
        assert cache.get_growth_rate("unknown") == "Unknown"


class TestWarmGrowthRates:
    async def test_populates_cache(self):
        cache = PokeCache()
        client = MagicMock()

        async def mock_growth_rate(rate_id):
            return {"pokemon_species": [{"name": f"pokemon_{rate_id}"}]}

        client.get_growth_rate = AsyncMock(side_effect=mock_growth_rate)
        await cache.warm_growth_rates(client)

        assert cache.get_growth_rate("pokemon_1") == "Slow"
        assert cache.get_growth_rate("pokemon_3") == "Fast"
        assert cache.get_growth_rate("pokemon_4") == "Medium Slow"


class TestSessionPersistence:
    def test_save_and_load(self, tmp_path):
        path = str(tmp_path / "sessions.json")
        cache = PokeCache(persist_path=path)

        version_map = {"123": "red"}
        session_map = {"456": "sword"}
        cache.save_sessions(version_map, session_map)

        cache2 = PokeCache(persist_path=path)
        loaded_v, loaded_s = cache2.load_sessions()
        assert loaded_v == {"123": "red"}
        assert loaded_s == {"456": "sword"}

    def test_load_missing_file(self):
        cache = PokeCache(persist_path="/nonexistent/path.json")
        v, s = cache.load_sessions()
        assert v == {}
        assert s == {}

    def test_no_persist_path_no_op(self):
        cache = PokeCache(persist_path=None)
        cache.save_sessions({"a": "b"}, {"c": "d"})
        v, s = cache.load_sessions()
        assert v == {}
        assert s == {}
