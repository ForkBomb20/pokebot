import pytest

from data.constants import (
    VERSIONS, VERSION_GROUPS, VERSION_MAPPINGS, GENERATIONS,
    ALL_TYPES, TYPE_COLOR_MAP, SEREBII_ABBRS, POKEMON,
)


class TestVersions:
    def test_has_9_generations(self):
        assert len(VERSIONS) == 9

    def test_gen1_games(self):
        assert "red" in VERSIONS[0]
        assert "blue" in VERSIONS[0]
        assert "yellow" in VERSIONS[0]

    def test_gen8_games(self):
        assert "sword" in VERSIONS[7]
        assert "shield" in VERSIONS[7]

    def test_gen9_games(self):
        assert "scarlet" in VERSIONS[8]
        assert "violet" in VERSIONS[8]


class TestVersionGroups:
    def test_has_9_entries(self):
        assert len(VERSION_GROUPS) == 9

    def test_gen9_group(self):
        assert "scarlet-violet" in VERSION_GROUPS[8]


class TestVersionMappings:
    def test_covers_all_games(self):
        for gen_games in VERSIONS:
            for game in gen_games:
                assert game in VERSION_MAPPINGS, f"{game} missing from VERSION_MAPPINGS"

    def test_values_exist_in_groups(self):
        all_groups = [g for gen in VERSION_GROUPS for g in gen]
        for game, group in VERSION_MAPPINGS.items():
            assert group in all_groups, f"Mapping {game}->{group} not in VERSION_GROUPS"

    def test_gen9_mappings(self):
        assert VERSION_MAPPINGS["scarlet"] == "scarlet-violet"
        assert VERSION_MAPPINGS["violet"] == "scarlet-violet"


class TestGenerations:
    def test_has_9_entries(self):
        assert len(GENERATIONS) == 9

    def test_first_gen(self):
        assert GENERATIONS[0] == "generation-i"

    def test_last_gen(self):
        assert GENERATIONS[8] == "generation-ix"


class TestAllTypes:
    def test_has_18_types(self):
        assert len(ALL_TYPES) == 18

    def test_includes_fairy(self):
        assert "fairy" in ALL_TYPES

    def test_no_duplicates(self):
        assert len(ALL_TYPES) == len(set(ALL_TYPES))


class TestTypeColorMap:
    def test_has_entry_for_each_type(self):
        for t in ALL_TYPES:
            assert t in TYPE_COLOR_MAP

    def test_colors_are_ints(self):
        for color in TYPE_COLOR_MAP.values():
            assert isinstance(color, int)


class TestSerebiiAbbrs:
    def test_has_9_entries(self):
        assert len(SEREBII_ABBRS) == 9

    def test_gen1_is_empty(self):
        assert SEREBII_ABBRS[0] == ""

    def test_gen9_is_sv(self):
        assert SEREBII_ABBRS[8] == "sv"


class TestPokemonList:
    def test_not_empty(self):
        assert len(POKEMON) > 0

    def test_gen1_starters(self):
        assert "Bulbasaur" in POKEMON
        assert "Charmander" in POKEMON
        assert "Squirtle" in POKEMON

    def test_gen9_starters(self):
        assert "Sprigatito" in POKEMON
        assert "Fuecoco" in POKEMON
        assert "Quaxly" in POKEMON

    def test_special_names(self):
        assert "Mr. Mime" in POKEMON
        assert "Ho-Oh" in POKEMON
        assert "Porygon-Z" in POKEMON
        assert "Type: Null" in POKEMON

    def test_gen9_last_pokemon(self):
        assert "Pecharunt" in POKEMON
