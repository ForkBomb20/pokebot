"""
Command handlers for PokéBot
"""
import discord
import pandas as pd
from table2ascii import table2ascii as t2a, PresetStyle

from data.pokedata import (
    getPokemonData, getSpeciesData, getMoves, getDamageRelations,
    getTypes, getGrowthRateData, getTheGenus, getDescription,
    getFirstGen, getEvolutions, find_game_version, serebiiURL
)
from utils.image_utils import merge_images_vert, create_type_image
from bot.core import VERSION_MAP, SESSION_MAP

# Reference to the global state maps from core.py
# These should be imported or passed in instead of reimplementing
# VERSION_MAP = {}
# SESSION_MAP = {}


async def process_pokemon_message(bot, message, session_map, version_map):
    """Process a message as a Pokemon name when in a session"""
    game = session_map[str(message.author.id)]
    gen = find_game_version(game)
    pokemon = message.content.strip().lower()
    
    if gen is None:
        await message.channel.send("That is not a valid game!")
    else:
        try:
            await process_pokemon_data(message, pokemon, gen, game)
        except Exception as e:
            await message.channel.send(f"There was an error processing your request: {str(e)}")


async def process_pokemon_data(message, pokemon, gen, game):
    """Process Pokemon data and send embeds"""
    # Get Pokemon data
    poke_data = getPokemonData(pokemon)
    species_data = getSpeciesData(pokemon)
    first_gen = getFirstGen(species_data)
    types = getTypes(poke_data, gen)
    id_filled = str(poke_data["id"]).zfill(3)
    
    # Define type color map
    type_color_map = {
        "fire": 0xFF4500, "water": 0x1E90FF, "grass": 0x7CFC00, "electric": 0xFFFF00,
        "ice": 0xADD8E6, "fighting": 0xB22222, "poison": 0x9932CC, "ground": 0xDEB887,
        "flying": 0x87CEEB, "psychic": 0xFF69B4, "bug": 0x6B8E23, "rock": 0x8B4513,
        "ghost": 0x663399, "dark": 0x000000, "dragon": 0x483D8B, "steel": 0xB0C4DE,
        "fairy": 0xFFB6C1, "normal": 0x808080
    }
    
    if gen >= first_gen:
        embed_color = type_color_map.get(types[0].lower(), 0xFF0000)
        
        # Create basic embed with Pokemon info
        genus = getTheGenus(species_data)
        description = getDescription(species_data, gen)
        basic_embed = create_basic_embed(pokemon, id_filled, genus, description, embed_color, gen)
        
        # Add growth rate info
        rate = getGrowthRateData(pokemon)
        basic_embed.add_field(name="Growth Rate", value=rate, inline=False)
        
        # Set thumbnail to Pokemon sprite
        sprite_url = poke_data["sprites"]["front_default"]
        basic_embed.set_thumbnail(url=sprite_url)
        await message.channel.send(embed=basic_embed)
        
        # Create and send damage relations embed
        damage_relations = getDamageRelations(types)
        dr_embed = create_damage_relations_embed(damage_relations, embed_color)
        
        # Create type image file
        file = create_type_image(types)
        filename = file.filename
        dr_embed.set_thumbnail(url=f"attachment://{filename}")
        await message.channel.send(file=file, embed=dr_embed)
        
        # Get and send move data
        moves_values = getMoves(poke_data, game)
        await message.channel.send(f"```{moves_values}```")
    else:
        await message.channel.send(f"Sorry! {pokemon} does not exist in generation {gen}")


def create_basic_embed(pokemon, id_filled, genus, description, embed_color, gen):
    """Create the basic Pokemon information embed"""
    basic_embed = discord.Embed(
        title=f"{pokemon.capitalize()} #{id_filled}",
        url=serebiiURL(gen, id_filled),
        description=f"**{genus}**:\n {description}",
        color=embed_color
    )
    basic_embed.set_author(name="Pokebot", icon_url="https://emoji.gg/assets/emoji/pokeball_light.png")
    return basic_embed


def create_damage_relations_embed(damage_relations, embed_color):
    """Create the damage relations embed"""
    type_data = {"Types": list(damage_relations.keys()), "Damage From": list(damage_relations.values())}
    damage_table = pd.DataFrame.from_dict(type_data).values.tolist()
    output = t2a(body=damage_table, style=PresetStyle.thin_compact)
    
    dr_embed = discord.Embed(
        title="Damage Taken", 
        description=f"```\n{output}\n```", 
        color=embed_color
    )
    dr_embed.set_author(name="Pokebot", icon_url="https://emoji.gg/assets/emoji/pokeball_light.png")
    dr_embed.set_thumbnail(url="attachment://type.png")
    
    return dr_embed


def register_commands(bot):
    """Register all bot commands"""
    
    @bot.command(name="learnset")
    async def learnset(ctx, pokemon, game=""):
        """Get the learnset for a Pokemon"""
        if game == "" and VERSION_MAP.get(str(ctx.message.author.id)):
            game = VERSION_MAP[str(ctx.message.author.id)]
        
        pokemon = pokemon.lower().strip()
        game = game.strip()
        
        try:
            data = getPokemonData(pokemon)
            moves_values = getMoves(data, game)
            await ctx.send(f"```{moves_values}```")
        except Exception as e:
            await ctx.send(f"Could not find that pokemon or learnset. Check your spelling and parameters.")
    
    @bot.command(name="evolution")
    async def evolution(ctx, pokemon):
        """Get evolution information for a Pokemon"""
        pokemon = pokemon.lower().strip()
        
        try:
            species = getSpeciesData(pokemon)
            names, conditions = getEvolutions(species)
            evo_str = format_evolution_chains(names, conditions)
            await ctx.send(f"```{evo_str}```")
        except Exception as e:
            await ctx.send(f"Could not find that pokemon or evolution data. Check spelling and parameters.")
    
    @bot.command(name="data")
    async def data(ctx, pokemon, gen):
        """Get general data for a Pokemon in a specific generation"""
        pokemon = pokemon.strip().lower()
        gen = int(gen.strip())
        
        try:
            # Reusing the process_pokemon_data function but adapted for this command
            poke_data = getPokemonData(pokemon)
            species_data = getSpeciesData(pokemon)
            first_gen = getFirstGen(species_data)
            types = getTypes(poke_data, gen)
            id_filled = str(poke_data["id"]).zfill(3)
            
            # Define type color map (could be moved to a constants file)
            type_color_map = {
                "fire": 0xFF4500, "water": 0x1E90FF, "grass": 0x7CFC00, "electric": 0xFFFF00,
                "ice": 0xADD8E6, "fighting": 0xB22222, "poison": 0x9932CC, "ground": 0xDEB887,
                "flying": 0x87CEEB, "psychic": 0xFF69B4, "bug": 0x6B8E23, "rock": 0x8B4513,
                "ghost": 0x663399, "dark": 0x000000, "dragon": 0x483D8B, "steel": 0xB0C4DE,
                "fairy": 0xFFB6C1, "normal": 0x808080
            }
            
            if gen >= first_gen:
                embed_color = type_color_map.get(types[0].lower(), 0xFF0000)
                
                # Create basic embed with Pokemon info
                genus = getTheGenus(species_data)
                description = getDescription(species_data, gen)
                basic_embed = create_basic_embed(pokemon, id_filled, genus, description, embed_color, gen)
                
                # Add growth rate info
                rate = getGrowthRateData(pokemon)
                basic_embed.add_field(name="Growth Rate", value=rate, inline=False)
                
                # Set thumbnail to Pokemon sprite
                sprite_url = poke_data["sprites"]["front_default"]
                basic_embed.set_thumbnail(url=sprite_url)
                await ctx.send(embed=basic_embed)
                
                # Create and send damage relations embed
                damage_relations = getDamageRelations(types)
                dr_embed = create_damage_relations_embed(damage_relations, embed_color)
                
                # Create type image file
                file = create_type_image(types)
                filename = file.filename
                dr_embed.set_thumbnail(url=f"attachment://{filename}")
                await ctx.send(file=file, embed=dr_embed)
            else:
                await ctx.send(f"Sorry! {pokemon} does not exist in generation {gen}")
        except Exception as e:
            await ctx.send(f"Could not find that pokemon or data. Check your spelling and parameters.")
    
    @bot.command(name="game")
    async def game(ctx, game):
        """Set your default game version"""
        game = game.strip().lower()
        VERSION_MAP[str(ctx.message.author.id)] = game
        await ctx.send(f"{ctx.message.author.name}'s game set to {game}")
    
    @bot.command(name="session")
    async def session(ctx, game):
        """Start a Pokemon session with a specific game version"""
        game = game.strip().lower()
        SESSION_MAP[str(ctx.message.author.id)] = game
        await ctx.send(f"{ctx.message.author.name} has started a {game} session\nJust type a Pokemon species to get all data but evolution(s).")


def format_evolution_chains(names, conditions):
    """Format evolution chains for display"""
    output_lines = []
    for i, chain in enumerate(names):
        if (i > 0):
            output_lines.append("\n")
        output_lines.append(f"Path {i + 1}: " + ", ".join([name.title() for name in chain]))
        max_conditions_length = max(len(conditions[i][k]) for k in range(1, len(chain)))
        evolution_steps = []

        for k in range(len(chain) - 1):
            c = conditions[i][k + 1]
            step_details = [f"{chain[k].title()} -> {chain[k + 1].title()}"]
            for key in c.keys():
                if isinstance(c[key], dict):
                    step_details.append(f"{key}: {c[key]['name'].replace('-', ' ').title()}")
                else:
                    step_details.append(f"{key}: {str(c[key])}")
            while len(step_details) < max_conditions_length + 1:
                step_details.append("")  # For vertical alignment
            evolution_steps.append(step_details)

        # Aligning vertically
        for line_parts in zip(*evolution_steps):
            output_lines.append("    ".join(f"{part:40}" for part in line_parts))

    return "\n".join(output_lines)