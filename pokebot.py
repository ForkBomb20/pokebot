import json.decoder
import os
import discord
import pandas as pd
from discord.ext import commands
from discord_slash import SlashCommand, SlashContext
from dotenv import load_dotenv
from pokedata import getPokemonData, getSpeciesData, getMoves, getDamageRelations, getTypes, getGrowthRateData, getTheGenus, getDescription, getFirstGen, getEvolutions, find_game_version
from table2ascii import table2ascii as t2a, PresetStyle
from PIL import Image

load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')

# client = discord.Client()
bot = commands.Bot(command_prefix="!")

VERSION_MAP = {}
SESSION_MAP = {}


def merge_images_vert(file1, file2):
    """Merge two images into one, displayed side by side
    :param file1: path to first image file
    :param file2: path to second image file
    :return: the merged Image object
    """
    image1 = Image.open(file1)
    image2 = Image.open(file2)

    (width1, height1) = image1.size
    (width2, height2) = image2.size

    result_width = max(width1, width2)
    result_height = height1 + height2

    result = Image.new('RGB', (result_width, result_height))

    result.paste(im=image1, box=(0, 0))
    result.paste(im=image2, box=(0, height1))
    result = result.resize(
        (round(result.size[0] * 2), round(result.size[1] * 2)))
    return result


def serebiiURL(gen, dex_num):
    games_abbrs = ["", "gs", "rs", "dp", "bw", "xy", "sm", "swsh"]
    abbr = games_abbrs[gen - 1]
    if abbr != "":
        abbr = "-" + abbr
    url = f"https://www.serebii.net/pokedex{abbr}/{dex_num}.shtml"
    return url


@bot.event
async def on_ready():
    print(f'{bot.user} has connect to Discord')


@bot.event
async def on_message(message):
    if str(message.author.id) in SESSION_MAP:
        game = SESSION_MAP[str(message.author.id)]
        gen = find_game_version(game)
        pokemon = message.content.strip().lower()
        if gen == None:
            message.channel.send("That is not a valid game!")
        else:
            try:
                poke_data = getPokemonData(pokemon)
                species_data = getSpeciesData(pokemon)
                first_gen = getFirstGen(species_data)
                types = getTypes(poke_data, gen)
                id = poke_data["id"]
                id_filled = str(id).zfill(3)

                type_color_map = {
                    "fire": 0xFF4500,  # Bright orange for Fire
                    "water": 0x1E90FF,  # Blue for Water
                    "grass": 0x7CFC00,  # Green for Grass
                    "electric": 0xFFFF00,  # Yellow for Electric
                    "ice": 0xADD8E6,  # Light blue for Ice
                    "fighting": 0xB22222,  # Dark red for Fighting
                    "poison": 0x9932CC,  # Purple for Poison
                    "ground": 0xDEB887,  # Brown for Ground
                    "flying": 0x87CEEB,  # Sky blue for Flying
                    "psychic": 0xFF69B4,  # Pink for Psychic
                    "bug": 0x6B8E23,  # Olive green for Bug
                    "rock": 0x8B4513,  # Saddle brown for Rock
                    "ghost": 0x663399,  # Dark purple for Ghost
                    "dark": 0x000000,  # Black for Dark
                    "dragon": 0x483D8B,  # Dark slate blue for Dragon
                    "steel": 0xB0C4DE,  # Light steel blue for Steel
                    "fairy": 0xFFB6C1,  # Light pink for Fairy
                    "normal": 0x808080  # Grey for Normal
                }
                embed_color = type_color_map.get(types[0].lower(), 0xFF0000)

                if gen >= first_gen:
                    genus = getTheGenus(species_data)
                    description = getDescription(species_data, gen)
                    basic_embed = discord.Embed(title=f"{pokemon.capitalize()} #{id_filled}", url=serebiiURL(
                        gen, id_filled), description=f"**{genus}**:\n {description}", color=embed_color)
                    rate = getGrowthRateData(pokemon)
                    abilities = None
                    basic_embed.add_field(name="Growth Rate", value=rate, inline=False)
                    basic_embed.set_author(
                        name="Pokebot", icon_url="https://emoji.gg/assets/emoji/pokeball_light.png")
                    sprite_url = poke_data["sprites"]["front_default"]
                    basic_embed.set_thumbnail(url=sprite_url)
                    await message.channel.send(embed=basic_embed)

                    damage_relations = getDamageRelations(types)
                    type_data = {"Types": list(damage_relations.keys(
                    )), "Damage From": list(damage_relations.values())}
                    damage_table = pd.DataFrame.from_dict(type_data)
                    damage_table = damage_table.values.tolist()
                    output = t2a(body=damage_table, style=PresetStyle.thin_compact)

                    if len(types) == 2:
                        type1 = types[0]
                        type2 = types[1]
                        im1 = f"./type_panels/{type1}.gif"
                        im2 = f"./type_panels/{type2}.gif"
                        img = merge_images_vert(im1, im2)
                        img = img.resize((round(img.size[0] * 2), round(img.size[1] * 2)))
                        img = img.save("type.png")
                    elif len(types) == 1:
                        path = f"type_panels/{types[0]}.gif"
                        img = Image.open(path)
                        img = img.resize((round(img.size[0] * 2), round(img.size[1] * 2)))
                        img = img.save("type.png")

                    file = discord.File(fp="type.png", filename="type.png")

                    dr_embed = discord.Embed(
                        title="Damage Taken", description=f"```\n{output}\n```", color=embed_color)
                    dr_embed.set_author(
                        name="Pokebot", icon_url="https://emoji.gg/assets/emoji/pokeball_light.png")
                    dr_embed.set_thumbnail(url="attachment://type.png")

                    await message.channel.send(file=file, embed=dr_embed)

                else:
                    await message.channel.send(f"Sorry! {pokemon} does not exist in generation {gen}")

            except:
                message.channel.send("There was an error fetching Pokemon data.")

            try:
                data = getPokemonData(pokemon)
                moves_values = getMoves(data, game)
                await message.channel.send(f"```{moves_values}```")

            except:
                message.channel.send("There was an error fetching Pokemon move data.")

    await bot.process_commands(message)


@bot.command(name="learnset")
async def learnset(ctx, pokemon, game=""):
    if game == "" and VERSION_MAP[str(ctx.message.author.id)]:
        game = VERSION_MAP[str(ctx.message.author.id)]
    pokemon = pokemon.lower().strip()
    game = game.strip()
    data = getPokemonData(pokemon)
    moves_values = getMoves(data, game)
    # getEvolutions(data)
    await ctx.send(f"```{moves_values}```")


@learnset.error
async def learnset_error(ctx, error):
    if isinstance(error, commands.CommandOnCooldown):
        message = f"This command is on cooldown. Please try again after {round(error.retry_after, 1)} seconds."
    elif isinstance(error, commands.MissingPermissions):
        message = "You are missing the required permissions to run this command!"
    elif isinstance(error, commands.MissingRequiredArgument):
        message = f"Missing a required argument: `{error.param}`"
    elif isinstance(error, commands.ConversionError):
        message = "`str(error)`"
    elif isinstance(error, commands.CommandInvokeError):
        message = "Could not find that pokemon or learnset. Check your spelling and parameters."
    else:
        message = "Oh no! Something went wrong while running the command!"

    await ctx.send(message, delete_after=5)
    await ctx.message.delete(delay=5)

@bot.command(name="evolution")
async def evolution(ctx, pokemon):
    pokemon = pokemon.lower().strip()
    species = getSpeciesData(pokemon)
    names, conditions = getEvolutions(species)

    def format_evolution_chains(names, conditions):
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
                    step_details.append(
                        "")  # Ensuring all lists have the same number of elements for vertical alignment
                evolution_steps.append(step_details)

            # Aligning vertically
            for line_parts in zip(*evolution_steps):
                output_lines.append("    ".join(f"{part:40}" for part in line_parts))  # Adjust the width as needed

        return "\n".join(output_lines)

    evo_str = format_evolution_chains(names, conditions)

    await ctx.send(f"```{evo_str}```")


@evolution.error
async def evolution_error(ctx, error):
    if isinstance(error, commands.CommandOnCooldown):
        message = f"This command is on cooldown. Please try again after {round(error.retry_after, 1)} seconds."
    elif isinstance(error, commands.MissingPermissions):
        message = "You are missing the required permissions to run this command!"
    elif isinstance(error, commands.MissingRequiredArgument):
        message = f"Missing a required argument: `{error.param}`"
    elif isinstance(error, commands.ConversionError):
        message = "`str(error)`"
    elif isinstance(error, commands.CommandInvokeError):
        message = "Could not find that pokemon or evolution data. Check spelling and parameters."
    else:
        message = "Oh no! Something went wrong while running the command!"

    await ctx.send(message, delete_after=5)
    await ctx.message.delete(delay=5)


@bot.command()
async def data(ctx, pokemon, gen):
    pokemon = pokemon.strip().lower()
    gen = int(gen.strip())
    poke_data = getPokemonData(pokemon)
    species_data = getSpeciesData(pokemon)
    first_gen = getFirstGen(species_data)
    types = getTypes(poke_data, gen)
    id = poke_data["id"]
    id_filled = str(id).zfill(3)

    type_color_map = {
        "fire": 0xFF4500,  # Bright orange for Fire
        "water": 0x1E90FF,  # Blue for Water
        "grass": 0x7CFC00,  # Green for Grass
        "electric": 0xFFFF00,  # Yellow for Electric
        "ice": 0xADD8E6,  # Light blue for Ice
        "fighting": 0xB22222,  # Dark red for Fighting
        "poison": 0x9932CC,  # Purple for Poison
        "ground": 0xDEB887,  # Brown for Ground
        "flying": 0x87CEEB,  # Sky blue for Flying
        "psychic": 0xFF69B4,  # Pink for Psychic
        "bug": 0x6B8E23,  # Olive green for Bug
        "rock": 0x8B4513,  # Saddle brown for Rock
        "ghost": 0x663399,  # Dark purple for Ghost
        "dark": 0x000000,  # Black for Dark
        "dragon": 0x483D8B,  # Dark slate blue for Dragon
        "steel": 0xB0C4DE,  # Light steel blue for Steel
        "fairy": 0xFFB6C1,  # Light pink for Fairy
        "normal": 0x808080  # Grey for Normal
    }
    embed_color = type_color_map.get(types[0].lower(), 0xFF0000)

    if gen >= first_gen:
        genus = getTheGenus(species_data)
        description = getDescription(species_data, gen)
        basic_embed = discord.Embed(title=f"{pokemon.capitalize()} #{id_filled}", url=serebiiURL(
            gen, id_filled), description=f"**{genus}**:\n {description}", color=embed_color)
        rate = getGrowthRateData(pokemon)
        abilities = None
        basic_embed.add_field(name="Growth Rate", value=rate, inline=False)
        basic_embed.set_author(
            name="Pokebot", icon_url="https://emoji.gg/assets/emoji/pokeball_light.png")
        sprite_url = poke_data["sprites"]["front_default"]
        basic_embed.set_thumbnail(url=sprite_url)
        await ctx.send(embed=basic_embed)

        damage_relations = getDamageRelations(types)
        type_data = {"Types": list(damage_relations.keys(
        )), "Damage From": list(damage_relations.values())}
        damage_table = pd.DataFrame.from_dict(type_data)
        damage_table = damage_table.values.tolist()
        output = t2a(body=damage_table, style=PresetStyle.thin_compact)

        if len(types) == 2:
            type1 = types[0]
            type2 = types[1]
            im1 = f"./type_panels/{type1}.gif"
            im2 = f"./type_panels/{type2}.gif"
            img = merge_images_vert(im1, im2)
            img = img.resize((round(img.size[0] * 2), round(img.size[1] * 2)))
            img = img.save("type.png")
        elif len(types) == 1:
            path = f"type_panels/{types[0]}.gif"
            img = Image.open(path)
            img = img.resize((round(img.size[0] * 2), round(img.size[1] * 2)))
            img = img.save("type.png")

        file = discord.File(fp="type.png", filename="type.png")

        dr_embed = discord.Embed(
            title="Damage Taken", description=f"```\n{output}\n```", color=embed_color)
        dr_embed.set_author(
            name="Pokebot", icon_url="https://emoji.gg/assets/emoji/pokeball_light.png")
        dr_embed.set_thumbnail(url="attachment://type.png")

        await ctx.send(file=file, embed=dr_embed)

    else:
        await ctx.send(f"Sorry! {pokemon} does not exist in generation {gen}")


@data.error
async def data_error(ctx, error):
    if isinstance(error, commands.CommandOnCooldown):
        message = f"This command is on cooldown. Please try again after {round(error.retry_after, 1)} seconds."
    elif isinstance(error, commands.MissingPermissions):
        message = "You are missing the required permissions to run this command!"
    elif isinstance(error, commands.MissingRequiredArgument):
        message = f"Missing a required argument: `{error.param}`"
    elif isinstance(error, commands.ConversionError):
        message = "`str(error)`"
    elif isinstance(error, commands.CommandInvokeError):
        message = "Could not find that pokemon or data. Check your spelling and parameters."
    else:
        message = "Oh no! Something went wrong while running the command!"

    await ctx.send(message, delete_after=5)
    await ctx.message.delete(delay=5)

@bot.command(name="game")
async def game(ctx, game):
    game = game.strip().lower()
    VERSION_MAP[str(ctx.message.author.id)] = game
    await ctx.send(f"{ctx.message.author.name}'s game set to {game}")


@learnset.error
async def game_error(ctx, error):
    if isinstance(error, commands.CommandOnCooldown):
        message = f"This command is on cooldown. Please try again after {round(error.retry_after, 1)} seconds."
    elif isinstance(error, commands.MissingPermissions):
        message = "You are missing the required permissions to run this command!"
    elif isinstance(error, commands.MissingRequiredArgument):
        message = f"Missing a required argument: `{error.param}`"
    elif isinstance(error, commands.ConversionError):
        message = "`str(error)`"
    elif isinstance(error, commands.CommandInvokeError):
        message = "Could not find that pokemon or learnset. Check your spelling and parameters."
    else:
        message = "Oh no! Something went wrong while running the command!"

    await ctx.send(message, delete_after=5)
    await ctx.message.delete(delay=5)

@bot.command(name="session")
async def session(ctx, game):
    game = game.strip().lower()
    SESSION_MAP[str(ctx.message.author.id)] = game
    await ctx.send(f"{ctx.message.author.name} has started a {game} session\nJust type a Pokemon species to get all data but evolution(s).")


@learnset.error
async def session_error(ctx, error):
    if isinstance(error, commands.CommandOnCooldown):
        message = f"This command is on cooldown. Please try again after {round(error.retry_after, 1)} seconds."
    elif isinstance(error, commands.MissingPermissions):
        message = "You are missing the required permissions to run this command!"
    elif isinstance(error, commands.MissingRequiredArgument):
        message = f"Missing a required argument: `{error.param}`"
    elif isinstance(error, commands.ConversionError):
        message = "`str(error)`"
    elif isinstance(error, commands.CommandInvokeError):
        message = "Could not find that pokemon or learnset. Check your spelling and parameters."
    else:
        message = "Oh no! Something went wrong while running the command!"

    await ctx.send(message, delete_after=5)
    await ctx.message.delete(delay=5)



bot.run(TOKEN)
