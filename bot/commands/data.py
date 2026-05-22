import discord
from discord.ext import commands
from discord import app_commands

from bot.helpers import resolve_pokemon, get_species_name, pokemon_matcher, send_response
from bot.embeds import create_basic_embed, create_damage_relations_embed, create_stats_embed
from utils.image_utils import create_type_image


class DataCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    async def _pokemon_autocomplete(self, interaction: discord.Interaction, current: str) -> list[app_commands.Choice[str]]:
        if not current:
            return []
        matches = pokemon_matcher.find_multiple_matches(current, threshold=0.4, max_results=10)
        return [app_commands.Choice(name=m[0], value=m[0].lower()) for m in matches]

    @commands.command(name="data")
    async def data_prefix(self, ctx, pokemon: str, gen: str):
        """Get general data for a Pokemon in a specific generation"""
        name = await resolve_pokemon(ctx, pokemon)
        if not name:
            return
        await self._show_data(ctx, name, int(gen.strip()))

    @app_commands.command(name="data", description="Get Pokemon data for a specific generation")
    @app_commands.describe(pokemon="Pokemon name", gen="Generation number (1-9)")
    @app_commands.autocomplete(pokemon=_pokemon_autocomplete)
    async def data_slash(self, interaction: discord.Interaction, pokemon: str, gen: int):
        await interaction.response.defer()
        name = await resolve_pokemon(interaction, pokemon)
        if not name:
            return
        await self._show_data(interaction, name, gen)

    async def _show_data(self, destination, pokemon: str, gen: int):
        service = self.bot.poke_service
        species_name = get_species_name(pokemon)

        poke_data = await service.get_pokemon_data(pokemon)
        species_data = await service.get_species_data(species_name)
        first_gen = service.get_first_gen(species_data)

        if gen < first_gen:
            await _send(destination, f"{pokemon.title()} does not exist in Generation {gen}.")
            return

        types = await service.get_types(poke_data, gen)
        dex_num = str(poke_data["id"]).zfill(3)
        genus = service.get_genus(species_data)
        description = service.get_description(species_data, gen)
        growth_rate = service.get_growth_rate(species_name)
        sprite_url = poke_data["sprites"]["front_default"] or ""

        basic_embed = create_basic_embed(
            pokemon, dex_num, genus, description, types, gen, sprite_url, growth_rate
        )

        damage_relations = await service.get_damage_relations(types)
        dr_embed = create_damage_relations_embed(damage_relations, types)

        stats = service.get_base_stats(poke_data)
        stats_embed = create_stats_embed(pokemon, stats, types)

        file = create_type_image(types)
        dr_embed.set_thumbnail(url=f"attachment://{file.filename}")

        await _send(destination, embed=basic_embed)
        await _send(destination, file=file, embed=dr_embed)
        await _send(destination, embed=stats_embed)


_send = send_response
