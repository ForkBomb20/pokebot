import pytest
from unittest.mock import patch, MagicMock
import json

from data.pokedata import (
    getPokemonData, getSpeciesData, getTheGenus, getFirstGen,
    getDescription, getTypes, getDamageRelations, getMoves,
    getEvolutions, find_game_version, serebiiURL, getCaptureRate,
    VERSIONS, VERSION_GROUPS, VERSION_MAPPINGS, GENERATIONS
)


MOCK_POKEMON_DATA = {
    "id": 25,
    "name": "pikachu",
    "types": [
        {"slot": 1, "type": {"name": "electric", "url": "https://pokeapi.co/api/v2/type/13/"}}
    ],
    "past_types": [],
    "stats": [
        {"base_stat": 35, "effort": 0, "stat": {"name": "hp", "url": "https://pokeapi.co/api/v2/stat/1/"}},
        {"base_stat": 55, "effort": 0, "stat": {"name": "attack", "url": "https://pokeapi.co/api/v2/stat/2/"}},
        {"base_stat": 40, "effort": 0, "stat": {"name": "defense", "url": "https://pokeapi.co/api/v2/stat/3/"}},
        {"base_stat": 50, "effort": 0, "stat": {"name": "special-attack", "url": "https://pokeapi.co/api/v2/stat/4/"}},
        {"base_stat": 50, "effort": 0, "stat": {"name": "special-defense", "url": "https://pokeapi.co/api/v2/stat/5/"}},
        {"base_stat": 90, "effort": 2, "stat": {"name": "speed", "url": "https://pokeapi.co/api/v2/stat/6/"}},
    ],
    "sprites": {"front_default": "https://raw.githubusercontent.com/PokeAPI/sprites/master/sprites/pokemon/25.png"},
    "moves": [
        {
            "move": {"name": "thunder-shock", "url": "https://pokeapi.co/api/v2/move/84/"},
            "version_group_details": [
                {
                    "level_learned_at": 1,
                    "move_learn_method": {"name": "level-up", "url": "https://pokeapi.co/api/v2/move-learn-method/1/"},
                    "order": None,
                    "version_group": {"name": "red-blue", "url": "https://pokeapi.co/api/v2/version-group/1/"}
                }
            ]
        },
        {
            "move": {"name": "thunderbolt", "url": "https://pokeapi.co/api/v2/move/85/"},
            "version_group_details": [
                {
                    "level_learned_at": 26,
                    "move_learn_method": {"name": "level-up", "url": "https://pokeapi.co/api/v2/move-learn-method/1/"},
                    "order": None,
                    "version_group": {"name": "red-blue", "url": "https://pokeapi.co/api/v2/version-group/1/"}
                }
            ]
        },
        {
            "move": {"name": "surf", "url": "https://pokeapi.co/api/v2/move/57/"},
            "version_group_details": [
                {
                    "level_learned_at": 0,
                    "move_learn_method": {"name": "machine", "url": "https://pokeapi.co/api/v2/move-learn-method/4/"},
                    "order": None,
                    "version_group": {"name": "red-blue", "url": "https://pokeapi.co/api/v2/version-group/1/"}
                }
            ]
        }
    ],
    "location_area_encounters": "https://pokeapi.co/api/v2/pokemon/25/encounters"
}

MOCK_SPECIES_DATA = {
    "name": "pikachu",
    "generation": {"name": "generation-i", "url": "https://pokeapi.co/api/v2/generation/1/"},
    "capture_rate": 190,
    "genera": [
        {"genus": "ねずみポケモン", "language": {"name": "ja", "url": "https://pokeapi.co/api/v2/language/1/"}},
        {"genus": "Mouse Pokémon", "language": {"name": "en", "url": "https://pokeapi.co/api/v2/language/9/"}}
    ],
    "flavor_text_entries": [
        {
            "flavor_text": "When several of these POKéMON gather, their electricity could build and cause lightning storms.",
            "language": {"name": "en", "url": "https://pokeapi.co/api/v2/language/9/"},
            "version": {"name": "red", "url": "https://pokeapi.co/api/v2/version/1/"}
        },
        {
            "flavor_text": "This intelligent POKéMON roasts hard BERRIES with electricity to make them tender enough to eat.",
            "language": {"name": "en", "url": "https://pokeapi.co/api/v2/language/9/"},
            "version": {"name": "gold", "url": "https://pokeapi.co/api/v2/version/4/"}
        },
        {
            "flavor_text": "日本語テキスト",
            "language": {"name": "ja", "url": "https://pokeapi.co/api/v2/language/1/"},
            "version": {"name": "red", "url": "https://pokeapi.co/api/v2/version/1/"}
        }
    ],
    "evolution_chain": {"url": "https://pokeapi.co/api/v2/evolution-chain/10/"}
}

MOCK_CHARIZARD_DATA = {
    "id": 6,
    "name": "charizard",
    "types": [
        {"slot": 1, "type": {"name": "fire", "url": "https://pokeapi.co/api/v2/type/10/"}},
        {"slot": 2, "type": {"name": "flying", "url": "https://pokeapi.co/api/v2/type/3/"}}
    ],
    "past_types": [],
    "stats": [
        {"base_stat": 78, "effort": 0, "stat": {"name": "hp", "url": "https://pokeapi.co/api/v2/stat/1/"}},
    ],
    "sprites": {"front_default": "https://example.com/charizard.png"},
    "moves": []
}

MOCK_MAGNEMITE_DATA = {
    "id": 81,
    "name": "magnemite",
    "types": [
        {"slot": 1, "type": {"name": "electric", "url": "https://pokeapi.co/api/v2/type/13/"}},
        {"slot": 2, "type": {"name": "steel", "url": "https://pokeapi.co/api/v2/type/9/"}}
    ],
    "past_types": [
        {
            "generation": {"name": "generation-i", "url": "https://pokeapi.co/api/v2/generation/1/"},
            "types": [
                {"slot": 1, "type": {"name": "electric", "url": "https://pokeapi.co/api/v2/type/13/"}}
            ]
        }
    ],
    "stats": [],
    "sprites": {"front_default": "https://example.com/magnemite.png"},
    "moves": []
}

MOCK_EVOLUTION_CHAIN = {
    "chain": {
        "species": {"name": "pichu", "url": "https://pokeapi.co/api/v2/pokemon-species/172/"},
        "evolution_details": [],
        "evolves_to": [
            {
                "species": {"name": "pikachu", "url": "https://pokeapi.co/api/v2/pokemon-species/25/"},
                "evolution_details": [
                    {
                        "gender": None, "held_item": None, "item": None,
                        "known_move": None, "known_move_type": None, "location": None,
                        "min_affection": None, "min_beauty": None, "min_happiness": 220,
                        "min_level": None, "needs_overworld_rain": False,
                        "party_species": None, "party_type": None,
                        "relative_physical_stats": None, "time_of_day": "",
                        "trade_species": None,
                        "trigger": {"name": "level-up", "url": "https://pokeapi.co/api/v2/evolution-trigger/1/"},
                        "turn_upside_down": False
                    }
                ],
                "evolves_to": [
                    {
                        "species": {"name": "raichu", "url": "https://pokeapi.co/api/v2/pokemon-species/26/"},
                        "evolution_details": [
                            {
                                "gender": None, "held_item": None,
                                "item": {"name": "thunder-stone", "url": "https://pokeapi.co/api/v2/item/83/"},
                                "known_move": None, "known_move_type": None, "location": None,
                                "min_affection": None, "min_beauty": None, "min_happiness": None,
                                "min_level": None, "needs_overworld_rain": False,
                                "party_species": None, "party_type": None,
                                "relative_physical_stats": None, "time_of_day": "",
                                "trade_species": None,
                                "trigger": {"name": "use-item", "url": "https://pokeapi.co/api/v2/evolution-trigger/3/"},
                                "turn_upside_down": False
                            }
                        ],
                        "evolves_to": []
                    }
                ]
            }
        ]
    }
}

MOCK_EEVEE_EVOLUTION_CHAIN = {
    "chain": {
        "species": {"name": "eevee", "url": "https://pokeapi.co/api/v2/pokemon-species/133/"},
        "evolution_details": [],
        "evolves_to": [
            {
                "species": {"name": "vaporeon", "url": "https://pokeapi.co/api/v2/pokemon-species/134/"},
                "evolution_details": [
                    {
                        "gender": None, "held_item": None,
                        "item": {"name": "water-stone", "url": "https://pokeapi.co/api/v2/item/84/"},
                        "known_move": None, "known_move_type": None, "location": None,
                        "min_affection": None, "min_beauty": None, "min_happiness": None,
                        "min_level": None, "needs_overworld_rain": False,
                        "party_species": None, "party_type": None,
                        "relative_physical_stats": None, "time_of_day": "",
                        "trade_species": None,
                        "trigger": {"name": "use-item", "url": "https://pokeapi.co/api/v2/evolution-trigger/3/"},
                        "turn_upside_down": False
                    }
                ],
                "evolves_to": []
            },
            {
                "species": {"name": "jolteon", "url": "https://pokeapi.co/api/v2/pokemon-species/135/"},
                "evolution_details": [
                    {
                        "gender": None, "held_item": None,
                        "item": {"name": "thunder-stone", "url": "https://pokeapi.co/api/v2/item/83/"},
                        "known_move": None, "known_move_type": None, "location": None,
                        "min_affection": None, "min_beauty": None, "min_happiness": None,
                        "min_level": None, "needs_overworld_rain": False,
                        "party_species": None, "party_type": None,
                        "relative_physical_stats": None, "time_of_day": "",
                        "trade_species": None,
                        "trigger": {"name": "use-item", "url": "https://pokeapi.co/api/v2/evolution-trigger/3/"},
                        "turn_upside_down": False
                    }
                ],
                "evolves_to": []
            },
            {
                "species": {"name": "flareon", "url": "https://pokeapi.co/api/v2/pokemon-species/136/"},
                "evolution_details": [
                    {
                        "gender": None, "held_item": None,
                        "item": {"name": "fire-stone", "url": "https://pokeapi.co/api/v2/item/82/"},
                        "known_move": None, "known_move_type": None, "location": None,
                        "min_affection": None, "min_beauty": None, "min_happiness": None,
                        "min_level": None, "needs_overworld_rain": False,
                        "party_species": None, "party_type": None,
                        "relative_physical_stats": None, "time_of_day": "",
                        "trade_species": None,
                        "trigger": {"name": "use-item", "url": "https://pokeapi.co/api/v2/evolution-trigger/3/"},
                        "turn_upside_down": False
                    }
                ],
                "evolves_to": []
            }
        ]
    }
}


class TestVersionConstants:
    def test_versions_has_8_generations(self):
        assert len(VERSIONS) == 8

    def test_gen1_games(self):
        assert "red" in VERSIONS[0]
        assert "blue" in VERSIONS[0]
        assert "yellow" in VERSIONS[0]

    def test_gen8_games(self):
        assert "sword" in VERSIONS[7]
        assert "shield" in VERSIONS[7]

    def test_version_groups_has_8_entries(self):
        assert len(VERSION_GROUPS) == 8

    def test_version_mappings_covers_all_games(self):
        for gen_games in VERSIONS:
            for game in gen_games:
                assert game in VERSION_MAPPINGS, f"{game} missing from VERSION_MAPPINGS"

    def test_version_mappings_values_exist_in_groups(self):
        all_groups = [g for gen in VERSION_GROUPS for g in gen]
        for game, group in VERSION_MAPPINGS.items():
            assert group in all_groups, f"Mapping {game}->{group} not in VERSION_GROUPS"

    def test_generations_list(self):
        assert len(GENERATIONS) == 8
        assert GENERATIONS[0] == "generation-i"
        assert GENERATIONS[7] == "generation-viii"


class TestFindGameVersion:
    def test_gen1_red(self):
        assert find_game_version("red") == 1

    def test_gen1_yellow(self):
        assert find_game_version("yellow") == 1

    def test_gen2_gold(self):
        assert find_game_version("gold") == 2

    def test_gen3_ruby(self):
        assert find_game_version("ruby") == 3

    def test_gen4_platinum(self):
        assert find_game_version("platinum") == 4

    def test_gen5_black(self):
        assert find_game_version("black") == 5

    def test_gen6_x(self):
        assert find_game_version("x") == 6

    def test_gen7_sun(self):
        assert find_game_version("sun") == 7

    def test_gen8_sword(self):
        assert find_game_version("sword") == 8

    def test_invalid_game(self):
        assert find_game_version("notarealgame") is None

    def test_empty_string(self):
        assert find_game_version("") is None


class TestSerebiiURL:
    def test_gen1_url_no_suffix(self):
        url = serebiiURL(1, "025")
        assert url == "https://www.serebii.net/pokedex/025.shtml"

    def test_gen2_url(self):
        url = serebiiURL(2, "025")
        assert url == "https://www.serebii.net/pokedex-gs/025.shtml"

    def test_gen3_url(self):
        url = serebiiURL(3, "025")
        assert url == "https://www.serebii.net/pokedex-rs/025.shtml"

    def test_gen4_url(self):
        url = serebiiURL(4, "025")
        assert url == "https://www.serebii.net/pokedex-dp/025.shtml"

    def test_gen5_url(self):
        url = serebiiURL(5, "025")
        assert url == "https://www.serebii.net/pokedex-bw/025.shtml"

    def test_gen8_url(self):
        url = serebiiURL(8, "025")
        assert url == "https://www.serebii.net/pokedex-swsh/025.shtml"

    def test_three_digit_dex_num(self):
        url = serebiiURL(1, "150")
        assert "150.shtml" in url


class TestGetTheGenus:
    def test_english_genus(self):
        result = getTheGenus(MOCK_SPECIES_DATA)
        assert result == "The Mouse Pokémon"

    def test_skips_non_english(self):
        species_data = {
            "genera": [
                {"genus": "ねずみポケモン", "language": {"name": "ja"}},
            ]
        }
        result = getTheGenus(species_data)
        assert result == "The "

    def test_multiple_languages_picks_english(self):
        species_data = {
            "genera": [
                {"genus": "Souris", "language": {"name": "fr"}},
                {"genus": "Mouse Pokémon", "language": {"name": "en"}},
                {"genus": "Maus", "language": {"name": "de"}},
            ]
        }
        result = getTheGenus(species_data)
        assert result == "The Mouse Pokémon"


class TestGetFirstGen:
    def test_gen1_pokemon(self):
        assert getFirstGen(MOCK_SPECIES_DATA) == 0

    def test_gen2_pokemon(self):
        species_data = {"generation": {"name": "generation-ii"}}
        assert getFirstGen(species_data) == 1

    def test_gen5_pokemon(self):
        species_data = {"generation": {"name": "generation-v"}}
        assert getFirstGen(species_data) == 4

    def test_gen8_pokemon(self):
        species_data = {"generation": {"name": "generation-viii"}}
        assert getFirstGen(species_data) == 7


class TestGetDescription:
    def test_finds_english_description_gen1(self):
        result = getDescription(MOCK_SPECIES_DATA, 1)
        assert "POKéMON" in result
        assert "electricity" in result

    def test_finds_gen2_description(self):
        result = getDescription(MOCK_SPECIES_DATA, 2)
        assert "intelligent" in result

    def test_no_description_for_gen_returns_default(self):
        species_data = {
            "flavor_text_entries": [
                {"flavor_text": "Text", "language": {"name": "en"}, "version": {"name": "sword"}}
            ]
        }
        result = getDescription(species_data, 1)
        assert result == "No Description"

    def test_skips_non_english_entries(self):
        species_data = {
            "flavor_text_entries": [
                {"flavor_text": "日本語", "language": {"name": "ja"}, "version": {"name": "red"}},
            ]
        }
        result = getDescription(species_data, 1)
        assert result == "No Description"


class TestGetTypes:
    def test_single_type_no_past(self):
        types = getTypes(MOCK_POKEMON_DATA, 1)
        assert types == ["electric"]

    def test_dual_type_no_past(self):
        types = getTypes(MOCK_CHARIZARD_DATA, 1)
        assert types == ["fire", "flying"]

    def test_past_types_returns_old_type_for_old_gen(self):
        # Magnemite was pure Electric in Gen I, gained Steel in Gen II
        types = getTypes(MOCK_MAGNEMITE_DATA, 1)
        assert types == ["electric"]

    def test_past_types_returns_current_type_for_new_gen(self):
        # Gen II onward, Magnemite is Electric/Steel
        types = getTypes(MOCK_MAGNEMITE_DATA, 3)
        assert types == ["electric", "steel"]

    def test_past_types_boundary_gen(self):
        # The boundary generation itself should still use past types
        # past_types generation is "generation-i" (index 0), gen_num = 1
        # gen <= gen_num (1 <= 1) -> uses past types
        types = getTypes(MOCK_MAGNEMITE_DATA, 1)
        assert types == ["electric"]


class TestGetDamageRelations:
    @patch("data.pokedata.requests.get")
    def test_single_type_electric(self, mock_get):
        mock_response = MagicMock()
        mock_response.text = json.dumps({
            "damage_relations": {
                "double_damage_from": [{"name": "ground"}],
                "half_damage_from": [{"name": "flying"}, {"name": "steel"}, {"name": "electric"}],
                "no_damage_from": []
            }
        })
        mock_get.return_value = mock_response

        result = getDamageRelations(("electric",))
        assert result["ground"] == 2
        assert result["flying"] == 0.5
        assert result["steel"] == 0.5
        assert result["electric"] == 0.5
        assert result["normal"] == 1
        assert result["fire"] == 1

    @patch("data.pokedata.requests.get")
    def test_dual_type_multiplies_correctly(self, mock_get):
        fire_response = MagicMock()
        fire_response.text = json.dumps({
            "damage_relations": {
                "double_damage_from": [{"name": "water"}, {"name": "ground"}, {"name": "rock"}],
                "half_damage_from": [{"name": "fire"}, {"name": "grass"}, {"name": "ice"}, {"name": "bug"}, {"name": "steel"}, {"name": "fairy"}],
                "no_damage_from": []
            }
        })
        flying_response = MagicMock()
        flying_response.text = json.dumps({
            "damage_relations": {
                "double_damage_from": [{"name": "electric"}, {"name": "ice"}, {"name": "rock"}],
                "half_damage_from": [{"name": "fighting"}, {"name": "bug"}, {"name": "grass"}],
                "no_damage_from": [{"name": "ground"}]
            }
        })

        def side_effect(url):
            if "fire" in url:
                return fire_response
            return flying_response

        mock_get.side_effect = side_effect

        result = getDamageRelations(("fire", "flying"))
        assert result["rock"] == 4       # 2 * 2
        assert result["ground"] == 0     # 2 * 0 (immune)
        assert result["bug"] == 0.25     # 0.5 * 0.5
        assert result["grass"] == 0.25   # 0.5 * 0.5
        assert result["ice"] == 1        # 0.5 (fire resists) * 2 (flying weak)
        assert result["water"] == 2      # 2 * 1
        assert result["electric"] == 2   # 1 * 2

    @patch("data.pokedata.requests.get")
    def test_returns_all_18_types(self, mock_get):
        mock_response = MagicMock()
        mock_response.text = json.dumps({
            "damage_relations": {
                "double_damage_from": [],
                "half_damage_from": [],
                "no_damage_from": []
            }
        })
        mock_get.return_value = mock_response

        result = getDamageRelations(("normal",))
        assert len(result) == 18

    @patch("data.pokedata.requests.get")
    def test_accepts_list_input(self, mock_get):
        mock_response = MagicMock()
        mock_response.text = json.dumps({
            "damage_relations": {
                "double_damage_from": [{"name": "ground"}],
                "half_damage_from": [],
                "no_damage_from": []
            }
        })
        mock_get.return_value = mock_response

        result = getDamageRelations(["electric"])
        assert result["ground"] == 2


class TestGetMoves:
    @patch("data.pokedata.requests.get")
    def test_gets_level_up_moves_only(self, mock_get):
        mock_response = MagicMock()
        mock_response.text = json.dumps({
            "type": {"name": "electric"},
            "damage_class": {"name": "special"},
            "power": 40,
            "accuracy": 100,
            "pp": 30
        })
        mock_get.return_value = mock_response

        result = getMoves(MOCK_POKEMON_DATA, "red")
        assert "thunder-shock" in result
        assert "thunderbolt" in result
        # surf is learned via machine, should be excluded
        assert "surf" not in result

    @patch("data.pokedata.requests.get")
    def test_moves_sorted_by_level(self, mock_get):
        mock_response = MagicMock()
        mock_response.text = json.dumps({
            "type": {"name": "electric"},
            "damage_class": {"name": "special"},
            "power": 90,
            "accuracy": 100,
            "pp": 15
        })
        mock_get.return_value = mock_response

        result = getMoves(MOCK_POKEMON_DATA, "red")
        # Level 1 (thunder-shock) should appear before level 26 (thunderbolt)
        assert result.index("thunder-shock") < result.index("thunderbolt")

    def test_no_moves_for_invalid_game(self):
        result = getMoves(MOCK_POKEMON_DATA, "notarealgame")
        assert "No level-up moves found" in result

    def test_no_moves_for_empty_game(self):
        result = getMoves(MOCK_POKEMON_DATA, "")
        assert "No level-up moves found" in result


class TestGetEvolutions:
    @patch("data.pokedata.requests.get")
    def test_linear_chain_pichu_pikachu_raichu(self, mock_get):
        mock_response = MagicMock()
        mock_response.text = json.dumps(MOCK_EVOLUTION_CHAIN)
        mock_get.return_value = mock_response

        names, conditions = getEvolutions(MOCK_SPECIES_DATA)
        assert len(names) == 1
        assert names[0] == ["pichu", "pikachu", "raichu"]

    @patch("data.pokedata.requests.get")
    def test_branching_evolution_eevee(self, mock_get):
        mock_response = MagicMock()
        mock_response.text = json.dumps(MOCK_EEVEE_EVOLUTION_CHAIN)
        mock_get.return_value = mock_response

        species_data = {"evolution_chain": {"url": "https://pokeapi.co/api/v2/evolution-chain/67/"}}
        names, conditions = getEvolutions(species_data)
        assert len(names) == 3
        assert all(chain[0] == "eevee" for chain in names)
        assert ["eevee", "vaporeon"] in names
        assert ["eevee", "jolteon"] in names
        assert ["eevee", "flareon"] in names

    @patch("data.pokedata.requests.get")
    def test_conditions_match_chain_length(self, mock_get):
        mock_response = MagicMock()
        mock_response.text = json.dumps(MOCK_EVOLUTION_CHAIN)
        mock_get.return_value = mock_response

        names, conditions = getEvolutions(MOCK_SPECIES_DATA)
        # Each chain and its conditions list should have the same length
        for i, chain in enumerate(names):
            assert len(conditions[i]) == len(chain)

    @patch("data.pokedata.requests.get")
    def test_evolution_conditions_contain_trigger(self, mock_get):
        mock_response = MagicMock()
        mock_response.text = json.dumps(MOCK_EVOLUTION_CHAIN)
        mock_get.return_value = mock_response

        names, conditions = getEvolutions(MOCK_SPECIES_DATA)
        # pikachu->raichu requires thunder-stone
        raichu_conditions = conditions[0][2]
        assert "item" in raichu_conditions
        assert raichu_conditions["item"]["name"] == "thunder-stone"


class TestGetPokemonData:
    @patch("data.pokedata.requests.get")
    def test_calls_correct_url(self, mock_get):
        mock_response = MagicMock()
        mock_response.text = json.dumps(MOCK_POKEMON_DATA)
        mock_get.return_value = mock_response

        getPokemonData.cache_clear()
        getPokemonData("pikachu")
        mock_get.assert_called_with("https://pokeapi.co/api/v2/pokemon/pikachu/")

    @patch("data.pokedata.requests.get")
    def test_strips_and_lowercases(self, mock_get):
        mock_response = MagicMock()
        mock_response.text = json.dumps(MOCK_POKEMON_DATA)
        mock_get.return_value = mock_response

        getPokemonData.cache_clear()
        getPokemonData("  Pikachu  ")
        mock_get.assert_called_with("https://pokeapi.co/api/v2/pokemon/pikachu/")

    @patch("data.pokedata.requests.get")
    def test_returns_parsed_json(self, mock_get):
        mock_response = MagicMock()
        mock_response.text = json.dumps(MOCK_POKEMON_DATA)
        mock_get.return_value = mock_response

        getPokemonData.cache_clear()
        result = getPokemonData("pikachu")
        assert result["id"] == 25
        assert result["name"] == "pikachu"


class TestGetSpeciesData:
    @patch("data.pokedata.requests.get")
    def test_calls_correct_url(self, mock_get):
        mock_response = MagicMock()
        mock_response.text = json.dumps(MOCK_SPECIES_DATA)
        mock_get.return_value = mock_response

        getSpeciesData.cache_clear()
        getSpeciesData("pikachu")
        mock_get.assert_called_with("https://pokeapi.co/api/v2/pokemon-species/pikachu/")

    @patch("data.pokedata.requests.get")
    def test_strips_and_lowercases(self, mock_get):
        mock_response = MagicMock()
        mock_response.text = json.dumps(MOCK_SPECIES_DATA)
        mock_get.return_value = mock_response

        getSpeciesData.cache_clear()
        getSpeciesData("  Pikachu  ")
        mock_get.assert_called_with("https://pokeapi.co/api/v2/pokemon-species/pikachu/")


class TestGetCaptureRate:
    def test_basic_calculation(self):
        species_data = {"capture_rate": 190}
        poke_data = {
            "stats": [
                {"base_stat": 35, "stat": {"name": "hp"}},
                {"base_stat": 55, "stat": {"name": "attack"}},
            ]
        }
        result = getCaptureRate(species_data, poke_data, level=50, p=0.5, ball=1, status=1)
        assert isinstance(result, float)
        assert result > 0

    def test_higher_capture_rate_gives_higher_chance(self):
        poke_data = {
            "stats": [{"base_stat": 50, "stat": {"name": "hp"}}]
        }
        low_rate = getCaptureRate({"capture_rate": 45}, poke_data, 50, 0.5, 1, 1)
        high_rate = getCaptureRate({"capture_rate": 255}, poke_data, 50, 0.5, 1, 1)
        assert high_rate > low_rate
