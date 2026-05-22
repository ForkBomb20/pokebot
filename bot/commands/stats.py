import discord
from discord.ext import commands
from discord import app_commands

from bot.helpers import resolve_pokemon, pokemon_matcher, send_response
from bot.embeds import create_stats_embed


class StatsCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    async def _pokemon_autocomplete(self, interaction: discord.Interaction, current: str) -> list[app_commands.Choice[str]]:
        if not current:
            return []
        matches = pokemon_matcher.find_multiple_matches(current, threshold=0.4, max_results=10)
        return [app_commands.Choice(name=m[0], value=m[0].lower()) for m in matches]

    @commands.command(name="stats")
    async def stats_prefix(self, ctx, pokemon: str):
        """Get base stats for a Pokemon"""
        name = await resolve_pokemon(ctx, pokemon)
        if not name:
            return
        await self._show_stats(ctx, name)

    @app_commands.command(name="stats", description="Get base stats for a Pokemon")
    @app_commands.describe(pokemon="Pokemon name")
    @app_commands.autocomplete(pokemon=_pokemon_autocomplete)
    async def stats_slash(self, interaction: discord.Interaction, pokemon: str):
        await interaction.response.defer()
        name = await resolve_pokemon(interaction, pokemon)
        if not name:
            return
        await self._show_stats(interaction, name)

    async def _show_stats(self, destination, pokemon: str):
        service = self.bot.poke_service
        poke_data = await service.get_pokemon_data(pokemon)
        types = await service.get_types(poke_data, 9)
        stats = service.get_base_stats(poke_data)
        embed = create_stats_embed(pokemon, stats, types)
        await send_response(destination, embed=embed)
