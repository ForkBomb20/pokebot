import discord
from discord.ext import commands
from discord import app_commands

from bot.helpers import resolve_pokemon, pokemon_matcher, send_response
from bot.views import MovesView, MOVES_PER_PAGE
from bot.embeds import create_moves_embed


class LearnsetCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    async def _pokemon_autocomplete(self, interaction: discord.Interaction, current: str) -> list[app_commands.Choice[str]]:
        if not current:
            return []
        matches = pokemon_matcher.find_multiple_matches(current, threshold=0.4, max_results=10)
        return [app_commands.Choice(name=m[0], value=m[0].lower()) for m in matches]

    @commands.command(name="learnset")
    async def learnset_prefix(self, ctx, pokemon: str, game: str = ""):
        """Get the learnset for a Pokemon"""
        if not game and self.bot.version_map.get(str(ctx.author.id)):
            game = self.bot.version_map[str(ctx.author.id)]

        name = await resolve_pokemon(ctx, pokemon)
        if not name:
            return
        await self._show_learnset(ctx, name, game.strip().lower())

    @app_commands.command(name="learnset", description="Get a Pokemon's level-up learnset")
    @app_commands.describe(pokemon="Pokemon name", game="Game version (e.g. red, sword, scarlet)")
    @app_commands.autocomplete(pokemon=_pokemon_autocomplete)
    async def learnset_slash(self, interaction: discord.Interaction, pokemon: str, game: str):
        await interaction.response.defer()
        name = await resolve_pokemon(interaction, pokemon)
        if not name:
            return
        await self._show_learnset(interaction, name, game.strip().lower())

    async def _show_learnset(self, destination, pokemon: str, game: str):
        service = self.bot.poke_service
        poke_data = await service.get_pokemon_data(pokemon)
        moves = await service.get_moves(poke_data, game)
        types = await service.get_types(poke_data, service.find_game_version(game) or 1)

        if not moves:
            await _send(destination, f"No level-up moves found for **{pokemon.title()}** in **{game}**.")
            return

        if len(moves) <= MOVES_PER_PAGE:
            embed = create_moves_embed(moves, pokemon, game, 1, 1, types)
            await _send(destination, embed=embed)
        else:
            view = MovesView(moves, pokemon, game, types)
            embed = view.get_embed()
            await _send(destination, embed=embed, view=view)


_send = send_response
