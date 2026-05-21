import discord
from discord.ext import commands
from discord import app_commands

from bot.helpers import resolve_pokemon, get_species_name, pokemon_matcher
from bot.embeds import create_evolution_embed


class EvolutionCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    async def _pokemon_autocomplete(self, interaction: discord.Interaction, current: str) -> list[app_commands.Choice[str]]:
        if not current:
            return []
        matches = pokemon_matcher.find_multiple_matches(current, threshold=0.4, max_results=10)
        return [app_commands.Choice(name=m[0], value=m[0].lower()) for m in matches]

    @commands.command(name="evolution")
    async def evolution_prefix(self, ctx, pokemon: str):
        """Get evolution information for a Pokemon"""
        name = await resolve_pokemon(ctx, pokemon)
        if not name:
            return
        await self._show_evolution(ctx, name)

    @app_commands.command(name="evolution", description="Get evolution chain for a Pokemon")
    @app_commands.describe(pokemon="Pokemon name")
    @app_commands.autocomplete(pokemon=_pokemon_autocomplete)
    async def evolution_slash(self, interaction: discord.Interaction, pokemon: str):
        await interaction.response.defer()
        name = await resolve_pokemon(interaction, pokemon)
        if not name:
            return
        await self._show_evolution(interaction, name)

    async def _show_evolution(self, destination, pokemon: str):
        service = self.bot.poke_service
        species_name = get_species_name(pokemon)
        species_data = await service.get_species_data(species_name)
        poke_data = await service.get_pokemon_data(pokemon)
        types = await service.get_types(poke_data, 9)

        names, conditions = await service.get_evolutions(species_data)
        embed = create_evolution_embed(names, conditions, types)
        await _send(destination, embed=embed)


async def _send(destination, content=None, **kwargs):
    if isinstance(destination, discord.Interaction):
        await destination.followup.send(content, **kwargs)
    else:
        if content:
            await destination.send(content, **kwargs)
        else:
            await destination.send(**kwargs)
