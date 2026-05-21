import discord
from discord.ext import commands
from discord import app_commands

from bot.helpers import resolve_pokemon, pokemon_matcher
from bot.embeds import create_abilities_embed


class AbilitiesCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    async def _pokemon_autocomplete(self, interaction: discord.Interaction, current: str) -> list[app_commands.Choice[str]]:
        if not current:
            return []
        matches = pokemon_matcher.find_multiple_matches(current, threshold=0.4, max_results=10)
        return [app_commands.Choice(name=m[0], value=m[0].lower()) for m in matches]

    @commands.command(name="abilities")
    async def abilities_prefix(self, ctx, pokemon: str):
        """Get abilities for a Pokemon"""
        name = await resolve_pokemon(ctx, pokemon)
        if not name:
            return
        await self._show_abilities(ctx, name)

    @app_commands.command(name="abilities", description="Get abilities for a Pokemon")
    @app_commands.describe(pokemon="Pokemon name")
    @app_commands.autocomplete(pokemon=_pokemon_autocomplete)
    async def abilities_slash(self, interaction: discord.Interaction, pokemon: str):
        await interaction.response.defer()
        name = await resolve_pokemon(interaction, pokemon)
        if not name:
            return
        await self._show_abilities(interaction, name)

    async def _show_abilities(self, destination, pokemon: str):
        service = self.bot.poke_service
        poke_data = await service.get_pokemon_data(pokemon)
        types = await service.get_types(poke_data, 9)
        abilities = await service.get_abilities(poke_data)
        embed = create_abilities_embed(pokemon, abilities, types)

        if isinstance(destination, discord.Interaction):
            await destination.followup.send(embed=embed)
        else:
            await destination.send(embed=embed)
