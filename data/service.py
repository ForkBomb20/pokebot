import asyncio
from math import floor

from data.api import PokeAPIClient
from data.cache import PokeCache
from data.constants import (
    VERSIONS, VERSION_MAPPINGS, GENERATIONS, ALL_TYPES, SEREBII_ABBRS,
)


class PokeDataService:
    def __init__(self, client: PokeAPIClient, cache: PokeCache):
        self._client = client
        self._cache = cache

    async def get_pokemon_data(self, name: str) -> dict:
        name = name.strip().lower()
        cached = self._cache.get_pokemon(name)
        if cached:
            return cached
        data = await self._client.get_pokemon(name)
        self._cache.set_pokemon(name, data)
        return data

    async def get_species_data(self, name: str) -> dict:
        name = name.strip().lower()
        cached = self._cache.get_species(name)
        if cached:
            return cached
        data = await self._client.get_species(name)
        self._cache.set_species(name, data)
        return data

    async def get_types(self, poke_data: dict, gen: int) -> list[str]:
        types = []
        if poke_data["past_types"]:
            key_gen_name = poke_data["past_types"][0]["generation"]["name"]
            gen_num = GENERATIONS.index(key_gen_name) + 1
            if gen <= gen_num:
                for slot in poke_data["past_types"][0]["types"]:
                    types.append(slot["type"]["name"])
            else:
                for slot in poke_data["types"]:
                    types.append(slot["type"]["name"])
        else:
            for slot in poke_data["types"]:
                types.append(slot["type"]["name"])
        return types

    async def get_damage_relations(self, types: list[str]) -> dict[str, float]:
        async def fetch_type_multipliers(type_name: str) -> dict[str, float]:
            cached = self._cache.get_type(type_name)
            if cached:
                type_data = cached
            else:
                type_data = await self._client.get_type(type_name)
                self._cache.set_type(type_name, type_data)

            dr = type_data["damage_relations"]
            double_from = {t["name"] for t in dr["double_damage_from"]}
            half_from = {t["name"] for t in dr["half_damage_from"]}
            none_from = {t["name"] for t in dr["no_damage_from"]}

            multipliers = {}
            for t in ALL_TYPES:
                if t in double_from:
                    multipliers[t] = 2.0
                elif t in half_from:
                    multipliers[t] = 0.5
                elif t in none_from:
                    multipliers[t] = 0.0
                else:
                    multipliers[t] = 1.0
            return multipliers

        results = await asyncio.gather(*[fetch_type_multipliers(t) for t in types])

        if len(results) == 1:
            return results[0]

        combined = {}
        for t in ALL_TYPES:
            combined[t] = 1.0
            for r in results:
                combined[t] *= r[t]
        return combined

    async def get_moves(self, poke_data: dict, game: str) -> list[dict]:
        version_group = VERSION_MAPPINGS.get(game.strip().lower())
        if not version_group:
            return []

        move_urls = []
        for move in poke_data["moves"]:
            for vgd in move["version_group_details"]:
                if (vgd["version_group"]["name"] == version_group and
                        vgd["move_learn_method"]["name"] == "level-up"):
                    move_urls.append((move["move"]["name"], move["move"]["url"], vgd["level_learned_at"]))
                    break

        async def fetch_move(name: str, url: str, level: int) -> dict:
            cached = self._cache.get_move(url)
            if cached:
                move_data = cached
            else:
                move_data = await self._client.get_move(url)
                self._cache.set_move(url, move_data)
            return {
                "level": level,
                "name": name,
                "type": move_data["type"]["name"],
                "category": move_data["damage_class"]["name"],
                "power": move_data["power"],
                "accuracy": move_data["accuracy"],
                "pp": move_data["pp"],
            }

        results = await asyncio.gather(*[fetch_move(n, u, l) for n, u, l in move_urls])
        return sorted(results, key=lambda m: m["level"])

    async def get_evolutions(self, species_data: dict) -> tuple[list[list[str]], list[list[dict]]]:
        url = species_data["evolution_chain"]["url"]
        evo_data = await self._client.get_evolution_chain(url)
        chain = evo_data["chain"]

        evolution_chains = []
        evolution_conditions = []

        def recurse(node, current_chain, current_conditions):
            current_chain.append(node["species"]["name"])

            if node["evolution_details"]:
                conditions = {}
                for key, value in node["evolution_details"][0].items():
                    if value not in [None, False, "", 0]:
                        conditions[key] = value
                current_conditions.append(conditions)
            else:
                current_conditions.append({})

            if not node["evolves_to"]:
                evolution_chains.append(current_chain.copy())
                evolution_conditions.append(current_conditions.copy())
            for next_node in node["evolves_to"]:
                recurse(next_node, current_chain.copy(), current_conditions.copy())

        recurse(chain, [], [])
        return evolution_chains, evolution_conditions

    def get_growth_rate(self, name: str) -> str:
        return self._cache.get_growth_rate(name)

    def get_genus(self, species_data: dict) -> str:
        for genus in species_data["genera"]:
            if genus["language"]["name"] == "en":
                return "The " + genus["genus"]
        return ""

    def get_description(self, species_data: dict, gen: int) -> str:
        versions = VERSIONS[gen - 1] if gen <= len(VERSIONS) else []
        for entry in species_data["flavor_text_entries"]:
            if entry["version"]["name"] in versions and entry["language"]["name"] == "en":
                return entry["flavor_text"].replace("\n", " ").replace("\f", " ")
        return "No description available."

    def get_first_gen(self, species_data: dict) -> int:
        gen_name = species_data["generation"]["name"]
        return GENERATIONS.index(gen_name) + 1

    def get_base_stats(self, poke_data: dict) -> list[dict]:
        return [
            {"name": stat["stat"]["name"], "value": stat["base_stat"]}
            for stat in poke_data["stats"]
        ]

    async def get_abilities(self, poke_data: dict) -> list[dict]:
        async def fetch_ability(ability_entry: dict) -> dict:
            url = ability_entry["ability"]["url"]
            data = await self._client.get_ability(url)
            flavor = ""
            for entry in data.get("flavor_text_entries", []):
                if entry["language"]["name"] == "en":
                    flavor = entry["flavor_text"].replace("\n", " ").replace("\f", " ")
                    break
            return {
                "name": ability_entry["ability"]["name"].replace("-", " ").title(),
                "is_hidden": ability_entry["is_hidden"],
                "description": flavor,
            }

        results = await asyncio.gather(*[fetch_ability(a) for a in poke_data["abilities"]])
        return sorted(results, key=lambda a: a["is_hidden"])

    def get_capture_rate(self, species_data: dict, poke_data: dict, level: int, hp_pct: float, ball: float, status: float) -> float:
        rate = int(species_data["capture_rate"])
        base_hp = [stat["base_stat"] for stat in poke_data["stats"] if stat["stat"]["name"] == "hp"][0]
        max_hp = floor((2 * base_hp * level / 100)) + level + 10
        current_hp = max_hp * hp_pct
        chance = ((1 + (max_hp * 3 - current_hp * 2) * rate * ball * status) / (3 * max_hp)) / 256
        return min(max(chance, 0.0), 1.0)

    @staticmethod
    def find_game_version(game: str) -> int | None:
        for index, version_list in enumerate(VERSIONS):
            if game in version_list:
                return index + 1
        return None

    @staticmethod
    def serebii_url(gen: int, dex_num: str) -> str:
        if gen > len(SEREBII_ABBRS):
            abbr = SEREBII_ABBRS[-1]
        else:
            abbr = SEREBII_ABBRS[gen - 1]
        suffix = f"-{abbr}" if abbr else ""
        return f"https://www.serebii.net/pokedex{suffix}/{dex_num}.shtml"
