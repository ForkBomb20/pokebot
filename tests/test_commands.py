import pytest
from unittest.mock import patch, MagicMock, AsyncMock
import json

from bot.commands import (
    process_pokemon_message, process_pokemon_data,
    create_basic_embed, create_damage_relations_embed,
    format_evolution_chains, pokemon_matcher, POKEMON
)


class TestPokemonList:
    def test_list_not_empty(self):
        assert len(POKEMON) > 0

    def test_gen1_starters_present(self):
        assert "Bulbasaur" in POKEMON
        assert "Charmander" in POKEMON
        assert "Squirtle" in POKEMON

    def test_gen8_pokemon_present(self):
        assert "Grookey" in POKEMON
        assert "Zacian" in POKEMON

    def test_alternate_forms_present(self):
        assert "Deoxys-attack" in POKEMON
        assert "Deoxys-defense" in POKEMON
        assert "Giratina-altered" in POKEMON
        assert "Giratina-origin" in POKEMON

    def test_special_names_present(self):
        assert "Mr. Mime" in POKEMON
        assert "Ho-Oh" in POKEMON
        assert "Porygon-Z" in POKEMON
        assert "Type: Null" in POKEMON
        assert "Tapu Koko" in POKEMON

    def test_last_pokemon_is_enamorus(self):
        assert POKEMON[-1] == "Enamorus"


class TestPokemonMatcher:
    def test_matcher_initialized(self):
        assert pokemon_matcher is not None

    def test_matcher_exact_match(self):
        assert pokemon_matcher.find_best_match("Pikachu") == "Pikachu"

    def test_matcher_typo(self):
        assert pokemon_matcher.find_best_match("pikchu") == "Pikachu"

    def test_matcher_case_insensitive(self):
        assert pokemon_matcher.find_best_match("CHARIZARD") == "Charizard"


class TestProcessPokemonMessage:
    @pytest.fixture
    def mock_message(self):
        msg = MagicMock()
        msg.author.id = 12345
        msg.content = "pikachu"
        msg.channel.send = AsyncMock()
        return msg

    @pytest.mark.asyncio
    @patch("bot.commands.process_pokemon_data", new_callable=AsyncMock)
    async def test_valid_pokemon_valid_game(self, mock_process, mock_message):
        bot = MagicMock()
        session_map = {"12345": "red"}
        version_map = {}

        await process_pokemon_message(bot, mock_message, session_map, version_map)
        mock_process.assert_called_once()

    @pytest.mark.asyncio
    async def test_invalid_game_sends_error(self, mock_message):
        bot = MagicMock()
        session_map = {"12345": "notarealgame"}
        version_map = {}

        await process_pokemon_message(bot, mock_message, session_map, version_map)
        mock_message.channel.send.assert_called_with("That is not a valid game!")

    @pytest.mark.asyncio
    async def test_unrecognized_pokemon_sends_not_found(self, mock_message):
        mock_message.content = "xyzxyzxyz"
        bot = MagicMock()
        session_map = {"12345": "red"}
        version_map = {}

        await process_pokemon_message(bot, mock_message, session_map, version_map)
        call_args = mock_message.channel.send.call_args[1] if mock_message.channel.send.call_args[1] else {}
        call_str = mock_message.channel.send.call_args[0][0] if mock_message.channel.send.call_args[0] else ""
        assert "not found" in call_str

    @pytest.mark.asyncio
    @patch("bot.commands.process_pokemon_data", new_callable=AsyncMock)
    async def test_fuzzy_correction_notifies_user(self, mock_process, mock_message):
        mock_message.content = "pikchu"  # typo
        bot = MagicMock()
        session_map = {"12345": "red"}
        version_map = {}

        await process_pokemon_message(bot, mock_message, session_map, version_map)
        # Should send "Did you mean" message
        first_call = mock_message.channel.send.call_args_list[0][0][0]
        assert "Did you mean" in first_call

    @pytest.mark.asyncio
    @patch("bot.commands.process_pokemon_data", new_callable=AsyncMock)
    async def test_exact_match_no_correction_message(self, mock_process, mock_message):
        mock_message.content = "pikachu"
        bot = MagicMock()
        session_map = {"12345": "red"}
        version_map = {}

        await process_pokemon_message(bot, mock_message, session_map, version_map)
        # Should NOT send "Did you mean" - only process_pokemon_data is called
        for call in mock_message.channel.send.call_args_list:
            if call[0]:
                assert "Did you mean" not in call[0][0]


class TestProcessPokemonData:
    @pytest.fixture
    def mock_message(self):
        msg = MagicMock()
        msg.channel.send = AsyncMock()
        return msg

    @pytest.mark.asyncio
    @patch("bot.commands.create_type_image")
    @patch("bot.commands.getDamageRelations")
    @patch("bot.commands.getGrowthRateData")
    @patch("bot.commands.getDescription")
    @patch("bot.commands.getTheGenus")
    @patch("bot.commands.getTypes")
    @patch("bot.commands.getFirstGen")
    @patch("bot.commands.getSpeciesData")
    @patch("bot.commands.getPokemonData")
    @patch("bot.commands.getMoves")
    async def test_sends_embeds_for_valid_pokemon(
        self, mock_moves, mock_poke, mock_species, mock_first_gen,
        mock_types, mock_genus, mock_desc, mock_growth, mock_damage, mock_type_img,
        mock_message
    ):
        mock_poke.return_value = {
            "id": 25,
            "sprites": {"front_default": "https://example.com/25.png"}
        }
        mock_species.return_value = {}
        mock_first_gen.return_value = 0
        mock_types.return_value = ["electric"]
        mock_genus.return_value = "The Mouse Pokémon"
        mock_desc.return_value = "A description"
        mock_growth.return_value = "Medium Fast"
        mock_damage.return_value = {"normal": 1, "fire": 1}
        mock_type_img.return_value = MagicMock(filename="electric.png")
        mock_moves.return_value = "move table"

        await process_pokemon_data(mock_message, "pikachu", 1, "red")
        assert mock_message.channel.send.call_count == 3  # basic embed, damage embed, moves

    @pytest.mark.asyncio
    @patch("bot.commands.getFirstGen")
    @patch("bot.commands.getTypes")
    @patch("bot.commands.getSpeciesData")
    @patch("bot.commands.getPokemonData")
    async def test_pokemon_not_in_generation(
        self, mock_poke, mock_species, mock_types, mock_first_gen, mock_message
    ):
        mock_poke.return_value = {"id": 25}
        mock_species.return_value = {}
        mock_first_gen.return_value = 5  # Pokemon first appears in gen 5
        mock_types.return_value = ["electric"]

        await process_pokemon_data(mock_message, "pikachu", 1, "red")  # gen 1 < gen 5
        call_str = mock_message.channel.send.call_args[0][0]
        assert "does not exist in generation" in call_str

    @pytest.mark.asyncio
    @patch("bot.commands.getFirstGen")
    @patch("bot.commands.getTypes")
    @patch("bot.commands.getSpeciesData")
    @patch("bot.commands.getPokemonData")
    async def test_alternate_form_uses_species_name(
        self, mock_poke, mock_species, mock_types, mock_first_gen, mock_message
    ):
        mock_poke.return_value = {"id": 386}
        mock_species.return_value = {}
        mock_first_gen.return_value = 10  # ensure "not in gen" path for simplicity
        mock_types.return_value = ["psychic"]

        await process_pokemon_data(mock_message, "deoxys-attack", 3, "ruby")
        # Should call getSpeciesData with "deoxys" not "deoxys-attack"
        mock_species.assert_called_with("deoxys")


class TestCreateBasicEmbed:
    def test_returns_embed(self):
        import discord
        embed = create_basic_embed("pikachu", "025", "The Mouse Pokémon", "A Pokemon", 0xFFFF00, 1)
        assert isinstance(embed, discord.Embed)

    def test_embed_title_contains_name(self):
        embed = create_basic_embed("pikachu", "025", "The Mouse Pokémon", "A Pokemon", 0xFFFF00, 1)
        assert "Pikachu" in embed.title

    def test_embed_title_contains_dex_number(self):
        embed = create_basic_embed("pikachu", "025", "The Mouse Pokémon", "A Pokemon", 0xFFFF00, 1)
        assert "025" in embed.title

    def test_embed_has_serebii_url(self):
        embed = create_basic_embed("pikachu", "025", "The Mouse Pokémon", "A Pokemon", 0xFFFF00, 1)
        assert "serebii.net" in embed.url

    def test_embed_description_contains_genus(self):
        embed = create_basic_embed("pikachu", "025", "The Mouse Pokémon", "A Pokemon", 0xFFFF00, 1)
        assert "Mouse Pokémon" in embed.description

    def test_embed_color_set(self):
        embed = create_basic_embed("pikachu", "025", "The Mouse Pokémon", "A Pokemon", 0xFFFF00, 1)
        assert embed.color.value == 0xFFFF00


class TestCreateDamageRelationsEmbed:
    def test_returns_embed(self):
        import discord
        damage_relations = {"normal": 1, "fire": 2, "water": 0.5}
        embed = create_damage_relations_embed(damage_relations, 0xFFFF00)
        assert isinstance(embed, discord.Embed)

    def test_embed_title_is_damage_taken(self):
        damage_relations = {"normal": 1, "fire": 2}
        embed = create_damage_relations_embed(damage_relations, 0xFFFF00)
        assert embed.title == "Damage Taken"

    def test_embed_description_contains_table(self):
        damage_relations = {"normal": 1, "fire": 2, "water": 0.5}
        embed = create_damage_relations_embed(damage_relations, 0xFFFF00)
        assert "```" in embed.description


class TestFormatEvolutionChains:
    def test_single_linear_chain(self):
        names = [["pichu", "pikachu", "raichu"]]
        conditions = [
            [{}, {"min_happiness": 220, "trigger": {"name": "level-up"}}, {"item": {"name": "thunder-stone"}, "trigger": {"name": "use-item"}}]
        ]
        result = format_evolution_chains(names, conditions)
        assert "Path 1:" in result
        assert "Pichu" in result
        assert "Pikachu" in result
        assert "Raichu" in result

    def test_branching_chains(self):
        names = [["eevee", "vaporeon"], ["eevee", "jolteon"], ["eevee", "flareon"]]
        conditions = [
            [{}, {"item": {"name": "water-stone"}, "trigger": {"name": "use-item"}}],
            [{}, {"item": {"name": "thunder-stone"}, "trigger": {"name": "use-item"}}],
            [{}, {"item": {"name": "fire-stone"}, "trigger": {"name": "use-item"}}],
        ]
        result = format_evolution_chains(names, conditions)
        assert "Path 1:" in result
        assert "Path 2:" in result
        assert "Path 3:" in result

    def test_contains_evolution_conditions(self):
        names = [["pichu", "pikachu", "raichu"]]
        conditions = [
            [{}, {"min_happiness": 220, "trigger": {"name": "level-up"}}, {"item": {"name": "thunder-stone"}, "trigger": {"name": "use-item"}}]
        ]
        result = format_evolution_chains(names, conditions)
        assert "thunder-stone" in result.lower() or "Thunder Stone" in result

    def test_shows_item_conditions(self):
        names = [["eevee", "vaporeon"]]
        conditions = [
            [{}, {"item": {"name": "water-stone"}, "trigger": {"name": "use-item"}}]
        ]
        result = format_evolution_chains(names, conditions)
        assert "Water Stone" in result or "water-stone" in result.lower()
