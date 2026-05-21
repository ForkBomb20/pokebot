import asyncio
import json
import os
from typing import Optional

from data.api import PokeAPIClient


GROWTH_RATE_NAMES = {
    1: "Slow",
    2: "Medium",
    3: "Fast",
    4: "Medium Slow",
    5: "Slow Then Very Fast",
    6: "Fast Then Very Slow",
}


class PokeCache:
    def __init__(self, persist_path: Optional[str] = None):
        self._pokemon: dict[str, dict] = {}
        self._species: dict[str, dict] = {}
        self._moves: dict[str, dict] = {}
        self._types: dict[str, dict] = {}
        self._growth_rates: dict[str, str] = {}
        self._persist_path = persist_path

    async def warm_growth_rates(self, client: PokeAPIClient):
        results = await asyncio.gather(
            *[client.get_growth_rate(i) for i in range(1, 7)]
        )
        for rate_id, data in enumerate(results, start=1):
            rate_name = GROWTH_RATE_NAMES[rate_id]
            for species in data["pokemon_species"]:
                self._growth_rates[species["name"]] = rate_name

    def get_growth_rate(self, name: str) -> str:
        return self._growth_rates.get(name.lower().strip(), "Unknown")

    def get_pokemon(self, name: str) -> Optional[dict]:
        return self._pokemon.get(name.lower().strip())

    def set_pokemon(self, name: str, data: dict):
        self._pokemon[name.lower().strip()] = data

    def get_species(self, name: str) -> Optional[dict]:
        return self._species.get(name.lower().strip())

    def set_species(self, name: str, data: dict):
        self._species[name.lower().strip()] = data

    def get_move(self, url: str) -> Optional[dict]:
        return self._moves.get(url)

    def set_move(self, url: str, data: dict):
        self._moves[url] = data

    def get_type(self, name: str) -> Optional[dict]:
        return self._types.get(name.lower().strip())

    def set_type(self, name: str, data: dict):
        self._types[name.lower().strip()] = data

    def save_sessions(self, version_map: dict, session_map: dict):
        if not self._persist_path:
            return
        os.makedirs(os.path.dirname(self._persist_path), exist_ok=True)
        data = {"version_map": version_map, "session_map": session_map}
        with open(self._persist_path, "w") as f:
            json.dump(data, f)

    def load_sessions(self) -> tuple[dict, dict]:
        if not self._persist_path or not os.path.exists(self._persist_path):
            return {}, {}
        with open(self._persist_path, "r") as f:
            data = json.load(f)
        return data.get("version_map", {}), data.get("session_map", {})
