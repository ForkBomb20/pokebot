import pytest
from unittest.mock import AsyncMock, MagicMock
import json

from data.service import PokeDataService
from data.constants import GENERATIONS


MOCK_POKEMON_DATA = {
    "id": 25,
    "name": "pikachu",
    "types": [
        {"slot": 1, "type": {"name": "electric", "url": "https://pokeapi.co/api/v2/type/13/"}}
    ],
    "past_types": [],
    "stats": [
        {"base_stat": 35, "effort": 0, "stat": {"name": "hp"}},
        {"base_stat": 55, "effort": 0, "stat": {"name": "attack"}},
        {"base_stat": 40, "effort": 0, "stat": {"name": "defense"}},
        {"base_stat": 50, "effort": 0, "stat": {"name": "special-attack"}},
        {"base_stat": 50, "effort": 0, "stat": {"name": "special-defense"}},
        {"base_stat": 90, "effort": 2, "stat": {"name": "speed"}},
    ],
    "abilities": [
        {"ability": {"name": "static", "url": "https://pokeapi.co/api/v2/ability/9/"}, "is_hidden": False, "slot": 1},
        {"ability": {"name": "lightning-rod", "url": "https://pokeapi.co/api/v2/ability/31/"}, "is_hidden": True, "slot": 3},
    ],
    "sprites": {"front_default": "https://example.com/pikachu.png"},
    "moves": [
        {
            "move": {"name": "thunder-shock", "url": "https://pokeapi.co/api/v2/move/84/"},
            "version_group_details": [
                {"level_learned_at": 1, "move_learn_method": {"name": "level-up"}, "version_group": {"name": "red-blue"}}
            ]
        },
        {
            "move": {"name": "thunderbolt", "url": "https://pokeapi.co/api/v2/move/85/"},
            "version_group_details": [
                {"level_learned_at": 26, "move_learn_method": {"name": "level-up"}, "version_group": {"name": "red-blue"}}
            ]
        },
        {
            "move": {"name": "surf", "url": "https://pokeapi.co/api/v2/move/57/"},
            "version_group_details": [
                {"level_learned_at": 0, "move_learn_method": {"name": "machine"}, "version_group": {"name": "red-blue"}}
            ]
        },
    ],
}

MOCK_SPECIES_DATA = {
    "name": "pikachu",
    "generation": {"name": "generation-i"},
    "capture_rate": 190,
    "genera": [
        {"genus": "Mouse Pokémon", "language": {"name": "en"}},
        {"genus": "ねずみポケモン", "language": {"name": "ja"}},
    ],
    "flavor_text_entries": [
        {"flavor_text": "Electricity text.", "language": {"name": "en"}, "version": {"name": "red"}},
        {"flavor_text": "Gold text.", "language": {"name": "en"}, "version": {"name": "gold"}},
    ],
    "evolution_chain": {"url": "https://pokeapi.co/api/v2/evolution-chain/10/"},
}

MOCK_MAGNEMITE_DATA = {
    "id": 81,
    "types": [
        {"slot": 1, "type": {"name": "electric"}},
        {"slot": 2, "type": {"name": "steel"}},
    ],
    "past_types": [
        {
            "generation": {"name": "generation-i"},
            "types": [{"slot": 1, "type": {"name": "electric"}}],
        }
    ],
    "stats": [{"base_stat": 25, "stat": {"name": "hp"}}],
    "abilities": [],
    "sprites": {"front_default": ""},
    "moves": [],
}

MOCK_EVOLUTION_CHAIN = {
    "chain": {
        "species": {"name": "pichu"},
        "evolution_details": [],
        "evolves_to": [
            {
                "species": {"name": "pikachu"},
                "evolution_details": [{"min_happiness": 220, "trigger": {"name": "level-up"}, "min_level": None, "item": None, "held_item": None, "known_move": None, "known_move_type": None, "location": None, "needs_overworld_rain": False, "party_species": None, "party_type": None, "relative_physical_stats": None, "time_of_day": "", "trade_species": None, "turn_upside_down": False, "gender": None}],
                "evolves_to": [
                    {
                        "species": {"name": "raichu"},
                        "evolution_details": [{"item": {"name": "thunder-stone"}, "trigger": {"name": "use-item"}, "min_happiness": None, "min_level": None, "held_item": None, "known_move": None, "known_move_type": None, "location": None, "needs_overworld_rain": False, "party_species": None, "party_type": None, "relative_physical_stats": None, "time_of_day": "", "trade_species": None, "turn_upside_down": False, "gender": None}],
                        "evolves_to": [],
                    }
                ],
            }
        ],
    }
}

MOCK_EEVEE_CHAIN = {
    "chain": {
        "species": {"name": "eevee"},
        "evolution_details": [],
        "evolves_to": [
            {"species": {"name": "vaporeon"}, "evolution_details": [{"item": {"name": "water-stone"}, "trigger": {"name": "use-item"}, "min_level": None, "min_happiness": None}], "evolves_to": []},
            {"species": {"name": "jolteon"}, "evolution_details": [{"item": {"name": "thunder-stone"}, "trigger": {"name": "use-item"}, "min_level": None, "min_happiness": None}], "evolves_to": []},
            {"species": {"name": "flareon"}, "evolution_details": [{"item": {"name": "fire-stone"}, "trigger": {"name": "use-item"}, "min_level": None, "min_happiness": None}], "evolves_to": []},
        ],
    }
}


class TestGetPokemonData:
    async def test_fetches_and_caches(self, service, mock_client, cache):
        mock_client.get_pokemon.return_value = MOCK_POKEMON_DATA
        result = await service.get_pokemon_data("pikachu")
        assert result["id"] == 25
        mock_client.get_pokemon.assert_called_once()

        # Second call should use cache
        result2 = await service.get_pokemon_data("pikachu")
        assert result2["id"] == 25
        assert mock_client.get_pokemon.call_count == 1

    async def test_strips_and_lowercases(self, service, mock_client):
        mock_client.get_pokemon.return_value = MOCK_POKEMON_DATA
        await service.get_pokemon_data("  Pikachu  ")
        mock_client.get_pokemon.assert_called_with("pikachu")


class TestGetSpeciesData:
    async def test_fetches_and_caches(self, service, mock_client):
        mock_client.get_species.return_value = MOCK_SPECIES_DATA
        result = await service.get_species_data("pikachu")
        assert result["name"] == "pikachu"
        assert mock_client.get_species.call_count == 1

        await service.get_species_data("pikachu")
        assert mock_client.get_species.call_count == 1


class TestGetTypes:
    async def test_single_type(self, service):
        types = await service.get_types(MOCK_POKEMON_DATA, 1)
        assert types == ["electric"]

    async def test_past_types_old_gen(self, service):
        types = await service.get_types(MOCK_MAGNEMITE_DATA, 1)
        assert types == ["electric"]

    async def test_past_types_new_gen(self, service):
        types = await service.get_types(MOCK_MAGNEMITE_DATA, 3)
        assert types == ["electric", "steel"]


class TestGetDamageRelations:
    async def test_single_type(self, service, mock_client):
        mock_client.get_type.return_value = {
            "damage_relations": {
                "double_damage_from": [{"name": "ground"}],
                "half_damage_from": [{"name": "flying"}, {"name": "steel"}, {"name": "electric"}],
                "no_damage_from": [],
            }
        }
        result = await service.get_damage_relations(["electric"])
        assert result["ground"] == 2.0
        assert result["flying"] == 0.5
        assert result["normal"] == 1.0

    async def test_dual_type_multiplies(self, service, mock_client):
        async def mock_get_type(name):
            if name == "fire":
                return {"damage_relations": {
                    "double_damage_from": [{"name": "water"}, {"name": "rock"}],
                    "half_damage_from": [{"name": "fire"}, {"name": "grass"}, {"name": "bug"}],
                    "no_damage_from": [],
                }}
            return {"damage_relations": {
                "double_damage_from": [{"name": "electric"}, {"name": "rock"}],
                "half_damage_from": [{"name": "bug"}, {"name": "grass"}],
                "no_damage_from": [{"name": "ground"}],
            }}

        mock_client.get_type.side_effect = mock_get_type
        result = await service.get_damage_relations(["fire", "flying"])
        assert result["rock"] == 4.0
        assert result["ground"] == 0.0
        assert result["bug"] == 0.25
        assert result["grass"] == 0.25

    async def test_returns_18_types(self, service, mock_client):
        mock_client.get_type.return_value = {
            "damage_relations": {
                "double_damage_from": [], "half_damage_from": [], "no_damage_from": [],
            }
        }
        result = await service.get_damage_relations(["normal"])
        assert len(result) == 18


class TestGetMoves:
    async def test_fetches_level_up_moves(self, service, mock_client):
        mock_client.get_move.return_value = {
            "type": {"name": "electric"}, "damage_class": {"name": "special"},
            "power": 40, "accuracy": 100, "pp": 30,
        }
        moves = await service.get_moves(MOCK_POKEMON_DATA, "red")
        assert len(moves) == 2
        assert moves[0]["name"] == "thunder-shock"
        assert moves[1]["name"] == "thunderbolt"

    async def test_sorted_by_level(self, service, mock_client):
        mock_client.get_move.return_value = {
            "type": {"name": "electric"}, "damage_class": {"name": "special"},
            "power": 90, "accuracy": 100, "pp": 15,
        }
        moves = await service.get_moves(MOCK_POKEMON_DATA, "red")
        levels = [m["level"] for m in moves]
        assert levels == sorted(levels)

    async def test_excludes_machine_moves(self, service, mock_client):
        mock_client.get_move.return_value = {
            "type": {"name": "water"}, "damage_class": {"name": "special"},
            "power": 90, "accuracy": 100, "pp": 15,
        }
        moves = await service.get_moves(MOCK_POKEMON_DATA, "red")
        names = [m["name"] for m in moves]
        assert "surf" not in names

    async def test_invalid_game_returns_empty(self, service, mock_client):
        moves = await service.get_moves(MOCK_POKEMON_DATA, "notarealgame")
        assert moves == []


class TestGetEvolutions:
    async def test_linear_chain(self, service, mock_client):
        mock_client.get_evolution_chain.return_value = MOCK_EVOLUTION_CHAIN
        names, conditions = await service.get_evolutions(MOCK_SPECIES_DATA)
        assert len(names) == 1
        assert names[0] == ["pichu", "pikachu", "raichu"]

    async def test_branching_chain(self, service, mock_client):
        mock_client.get_evolution_chain.return_value = MOCK_EEVEE_CHAIN
        species = {"evolution_chain": {"url": "https://pokeapi.co/api/v2/evolution-chain/67/"}}
        names, conditions = await service.get_evolutions(species)
        assert len(names) == 3
        assert all(c[0] == "eevee" for c in names)

    async def test_conditions_length_matches_chain(self, service, mock_client):
        mock_client.get_evolution_chain.return_value = MOCK_EVOLUTION_CHAIN
        names, conditions = await service.get_evolutions(MOCK_SPECIES_DATA)
        for i, chain in enumerate(names):
            assert len(conditions[i]) == len(chain)


class TestGetGrowthRate:
    async def test_returns_cached_rate(self, service, cache):
        cache._growth_rates["pikachu"] = "Medium Fast"
        result = service.get_growth_rate("pikachu")
        assert result == "Medium Fast"

    async def test_unknown_returns_unknown(self, service):
        result = service.get_growth_rate("nonexistent")
        assert result == "Unknown"


class TestGetGenus:
    def test_english_genus(self, service):
        result = service.get_genus(MOCK_SPECIES_DATA)
        assert result == "The Mouse Pokémon"

    def test_no_english_returns_empty(self, service):
        species = {"genera": [{"genus": "test", "language": {"name": "ja"}}]}
        assert service.get_genus(species) == ""


class TestGetDescription:
    def test_finds_gen1_description(self, service):
        result = service.get_description(MOCK_SPECIES_DATA, 1)
        assert "Electricity" in result

    def test_finds_gen2_description(self, service):
        result = service.get_description(MOCK_SPECIES_DATA, 2)
        assert "Gold" in result

    def test_no_match_returns_default(self, service):
        result = service.get_description(MOCK_SPECIES_DATA, 9)
        assert "No description" in result


class TestGetFirstGen:
    def test_gen1(self, service):
        assert service.get_first_gen(MOCK_SPECIES_DATA) == 1

    def test_gen5(self, service):
        species = {"generation": {"name": "generation-v"}}
        assert service.get_first_gen(species) == 5


class TestGetBaseStats:
    def test_returns_stat_list(self, service):
        stats = service.get_base_stats(MOCK_POKEMON_DATA)
        assert len(stats) == 6
        assert stats[0] == {"name": "hp", "value": 35}
        assert stats[5] == {"name": "speed", "value": 90}


class TestGetAbilities:
    async def test_fetches_abilities(self, service, mock_client):
        mock_client.get_ability.return_value = {
            "flavor_text_entries": [
                {"flavor_text": "Contact may paralyze.", "language": {"name": "en"}},
            ]
        }
        abilities = await service.get_abilities(MOCK_POKEMON_DATA)
        assert len(abilities) == 2
        assert abilities[0]["name"] == "Static"
        assert abilities[0]["is_hidden"] is False
        assert abilities[1]["name"] == "Lightning Rod"
        assert abilities[1]["is_hidden"] is True


class TestFindGameVersion:
    def test_gen1(self):
        assert PokeDataService.find_game_version("red") == 1

    def test_gen9(self):
        assert PokeDataService.find_game_version("scarlet") == 9

    def test_invalid(self):
        assert PokeDataService.find_game_version("fake") is None


class TestSerebiiUrl:
    def test_gen1_no_suffix(self):
        assert PokeDataService.serebii_url(1, "025") == "https://www.serebii.net/pokedex/025.shtml"

    def test_gen2(self):
        assert PokeDataService.serebii_url(2, "025") == "https://www.serebii.net/pokedex-gs/025.shtml"

    def test_gen9(self):
        assert PokeDataService.serebii_url(9, "025") == "https://www.serebii.net/pokedex-sv/025.shtml"


class TestGetCaptureRate:
    def test_basic_calculation(self, service):
        result = service.get_capture_rate(MOCK_SPECIES_DATA, MOCK_POKEMON_DATA, 50, 0.5, 1.0, 1.0)
        assert isinstance(result, float)
        assert 0 <= result <= 1

    def test_higher_rate_gives_higher_chance(self, service):
        low = service.get_capture_rate({"capture_rate": 45}, MOCK_POKEMON_DATA, 50, 0.5, 1.0, 1.0)
        high = service.get_capture_rate({"capture_rate": 255}, MOCK_POKEMON_DATA, 50, 0.5, 1.0, 1.0)
        assert high > low
