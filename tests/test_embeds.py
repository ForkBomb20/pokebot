import pytest
import discord

from bot.embeds import (
    create_basic_embed, create_stats_embed, create_damage_relations_embed,
    create_evolution_embed, create_abilities_embed, create_moves_embed,
    get_type_color, STAT_DISPLAY_NAMES,
)


class TestGetTypeColor:
    def test_known_type(self):
        assert get_type_color(["fire"]) == 0xEE8130

    def test_unknown_type_fallback(self):
        assert get_type_color(["nonexistent"]) == 0x808080

    def test_uses_first_type(self):
        assert get_type_color(["water", "flying"]) == 0x6390F0


class TestCreateBasicEmbed:
    def test_returns_embed(self):
        embed = create_basic_embed("pikachu", "025", "The Mouse Pokémon", "A Pokémon.", ["electric"], 1, "http://img.png", "Medium Fast")
        assert isinstance(embed, discord.Embed)

    def test_title_contains_name(self):
        embed = create_basic_embed("pikachu", "025", "The Mouse Pokémon", "A Pokémon.", ["electric"], 1, "http://img.png", "Medium Fast")
        assert "Pikachu" in embed.title

    def test_title_contains_dex_num(self):
        embed = create_basic_embed("pikachu", "025", "The Mouse Pokémon", "A Pokémon.", ["electric"], 1, "http://img.png", "Medium Fast")
        assert "#025" in embed.title

    def test_footer_shows_generation(self):
        embed = create_basic_embed("pikachu", "025", "The Mouse Pokémon", "A Pokémon.", ["electric"], 3, "http://img.png", "Medium Fast")
        assert "3" in embed.footer.text

    def test_has_type_field(self):
        embed = create_basic_embed("pikachu", "025", "The Mouse Pokémon", "A Pokémon.", ["fire", "flying"], 1, "http://img.png", "Slow")
        type_field = next(f for f in embed.fields if f.name == "Type")
        assert "Fire" in type_field.value
        assert "Flying" in type_field.value


class TestCreateStatsEmbed:
    def test_returns_embed(self):
        stats = [{"name": "hp", "value": 35}, {"name": "attack", "value": 55}]
        embed = create_stats_embed("pikachu", stats, ["electric"])
        assert isinstance(embed, discord.Embed)

    def test_contains_stat_bars(self):
        stats = [
            {"name": "hp", "value": 35}, {"name": "attack", "value": 55},
            {"name": "defense", "value": 40}, {"name": "special-attack", "value": 50},
            {"name": "special-defense", "value": 50}, {"name": "speed", "value": 90},
        ]
        embed = create_stats_embed("pikachu", stats, ["electric"])
        assert "█" in embed.description
        assert "░" in embed.description

    def test_shows_total(self):
        stats = [{"name": "hp", "value": 100}, {"name": "attack", "value": 50}]
        embed = create_stats_embed("pikachu", stats, ["electric"])
        assert "TOTAL" in embed.description
        assert "150" in embed.description


class TestCreateDamageRelationsEmbed:
    def test_returns_embed(self):
        relations = {"ground": 2.0, "electric": 0.5, "flying": 0.5, "normal": 1.0}
        embed = create_damage_relations_embed(relations, ["electric"])
        assert isinstance(embed, discord.Embed)

    def test_shows_weaknesses(self):
        relations = {"ground": 2.0, "normal": 1.0}
        embed = create_damage_relations_embed(relations, ["electric"])
        assert any("Weak" in f.name for f in embed.fields)

    def test_shows_resistances(self):
        relations = {"electric": 0.5, "normal": 1.0}
        embed = create_damage_relations_embed(relations, ["electric"])
        assert any("Resist" in f.name for f in embed.fields)

    def test_shows_immunities(self):
        relations = {"ground": 0.0, "normal": 1.0}
        embed = create_damage_relations_embed(relations, ["ghost"])
        assert any("Immune" in f.name for f in embed.fields)


class TestCreateEvolutionEmbed:
    def test_returns_embed(self):
        names = [["pichu", "pikachu", "raichu"]]
        conditions = [[{}, {"min_happiness": 220}, {"item": {"name": "thunder-stone"}}]]
        embed = create_evolution_embed(names, conditions, ["electric"])
        assert isinstance(embed, discord.Embed)

    def test_shows_pokemon_names(self):
        names = [["pichu", "pikachu", "raichu"]]
        conditions = [[{}, {"min_happiness": 220}, {"item": {"name": "thunder-stone"}}]]
        embed = create_evolution_embed(names, conditions, ["electric"])
        field_text = embed.fields[0].value
        assert "Pichu" in field_text
        assert "Pikachu" in field_text
        assert "Raichu" in field_text

    def test_branching_shows_multiple_paths(self):
        names = [["eevee", "vaporeon"], ["eevee", "jolteon"]]
        conditions = [[{}, {"item": {"name": "water-stone"}}], [{}, {"item": {"name": "thunder-stone"}}]]
        embed = create_evolution_embed(names, conditions, ["normal"])
        assert len(embed.fields) == 2


class TestCreateAbilitiesEmbed:
    def test_returns_embed(self):
        abilities = [
            {"name": "Static", "is_hidden": False, "description": "Contact may paralyze."},
            {"name": "Lightning Rod", "is_hidden": True, "description": "Draws Electric moves."},
        ]
        embed = create_abilities_embed("pikachu", abilities, ["electric"])
        assert isinstance(embed, discord.Embed)

    def test_marks_hidden_ability(self):
        abilities = [
            {"name": "Lightning Rod", "is_hidden": True, "description": "Draws Electric moves."},
        ]
        embed = create_abilities_embed("pikachu", abilities, ["electric"])
        assert "(Hidden)" in embed.fields[0].name


class TestCreateMovesEmbed:
    def test_returns_embed(self):
        moves = [{"level": 1, "name": "tackle", "type": "normal", "category": "physical", "power": 40, "accuracy": 100, "pp": 35}]
        embed = create_moves_embed(moves, "pikachu", "red", 1, 1, ["electric"])
        assert isinstance(embed, discord.Embed)

    def test_contains_move_data(self):
        moves = [{"level": 1, "name": "tackle", "type": "normal", "category": "physical", "power": 40, "accuracy": 100, "pp": 35}]
        embed = create_moves_embed(moves, "pikachu", "red", 1, 1, ["electric"])
        assert "tackle" in embed.description

    def test_shows_page_info_when_paginated(self):
        moves = [{"level": 1, "name": "tackle", "type": "normal", "category": "physical", "power": 40, "accuracy": 100, "pp": 35}]
        embed = create_moves_embed(moves, "pikachu", "red", 2, 3, ["electric"])
        assert "2/3" in embed.footer.text
