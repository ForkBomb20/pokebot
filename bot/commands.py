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
from utils.fuzzy import PokemonFuzzyMatcher

POKEMON = ['Bulbasaur', 'Ivysaur', 'Venusaur', 'Charmander', 'Charmeleon', 'Charizard', 'Squirtle', 'Wartortle', 'Blastoise', 'Caterpie', 'Metapod', 'Butterfree', 'Weedle', 'Kakuna', 'Beedrill', 'Pidgey', 'Pidgeotto', 'Pidgeot', 'Rattata', 'Raticate', 'Spearow', 'Fearow', 'Ekans', 'Arbok', 'Pikachu', 'Raichu', 'Sandshrew', 'Sandslash', 'Nidoran♀', 'Nidorina', 'Nidoqueen', 'Nidoran♂', 'Nidorino', 'Nidoking', 'Clefairy', 'Clefable', 'Vulpix', 'Ninetales', 'Jigglypuff', 'Wigglytuff', 'Zubat', 'Golbat', 'Oddish', 'Gloom', 'Vileplume', 'Paras', 'Parasect', 'Venonat', 'Venomoth', 'Diglett', 'Dugtrio', 'Meowth', 'Persian', 'Psyduck', 'Golduck', 'Mankey', 'Primeape', 'Growlithe', 'Arcanine', 'Poliwag', 'Poliwhirl', 'Poliwrath', 'Abra', 'Kadabra', 'Alakazam', 'Machop', 'Machoke', 'Machamp', 'Bellsprout', 'Weepinbell', 'Victreebel', 'Tentacool', 'Tentacruel', 'Geodude', 'Graveler', 'Golem', 'Ponyta', 'Rapidash', 'Slowpoke', 'Slowbro', 'Magnemite', 'Magneton', 'Farfetch’d', 'Doduo', 'Dodrio', 'Seel', 'Dewgong', 'Grimer', 'Muk', 'Shellder', 'Cloyster', 'Gastly', 'Haunter', 'Gengar', 'Onix', 'Drowzee', 'Hypno', 'Krabby', 'Kingler', 'Voltorb', 'Electrode', 'Exeggcute', 'Exeggutor', 'Cubone', 'Marowak', 'Hitmonlee', 'Hitmonchan', 'Lickitung', 'Koffing', 'Weezing', 'Rhyhorn', 'Rhydon', 'Chansey', 'Tangela', 'Kangaskhan', 'Horsea', 'Seadra', 'Goldeen', 'Seaking', 'Staryu', 'Starmie', 'Mr. Mime', 'Scyther', 'Jynx', 'Electabuzz', 'Magmar', 'Pinsir', 'Tauros', 'Magikarp', 'Gyarados', 'Lapras', 'Ditto', 'Eevee', 'Vaporeon', 'Jolteon', 'Flareon', 'Porygon', 'Omanyte', 'Omastar', 'Kabuto', 'Kabutops', 'Aerodactyl', 'Snorlax', 'Articuno', 'Zapdos', 'Moltres', 'Dratini', 'Dragonair', 'Dragonite', 'Mewtwo', 'Mew', 'Chikorita', 'Bayleef', 'Meganium', 'Cyndaquil', 'Quilava', 'Typhlosion', 'Totodile', 'Croconaw', 'Feraligatr', 'Sentret', 'Furret', 'Hoothoot', 'Noctowl', 'Ledyba', 'Ledian', 'Spinarak', 'Ariados', 'Crobat', 'Chinchou', 'Lanturn', 'Pichu', 'Cleffa', 'Igglybuff', 'Togepi', 'Togetic', 'Natu', 'Xatu', 'Mareep', 'Flaaffy', 'Ampharos', 'Bellossom', 'Marill', 'Azumarill', 'Sudowoodo', 'Politoed', 'Hoppip', 'Skiploom', 'Jumpluff', 'Aipom', 'Sunkern', 'Sunflora', 'Yanma', 'Wooper', 'Quagsire', 'Espeon', 'Umbreon', 'Murkrow', 'Slowking', 'Misdreavus', 'Unown', 'Wobbuffet', 'Girafarig', 'Pineco', 'Forretress', 'Dunsparce', 'Gligar', 'Steelix', 'Snubbull', 'Granbull', 'Qwilfish', 'Scizor', 'Shuckle', 'Heracross', 'Sneasel', 'Teddiursa', 'Ursaring', 'Slugma', 'Magcargo', 'Swinub', 'Piloswine', 'Corsola', 'Remoraid', 'Octillery', 'Delibird', 'Mantine', 'Skarmory', 'Houndour', 'Houndoom', 'Kingdra', 'Phanpy', 'Donphan', 'Porygon2', 'Stantler', 'Smeargle', 'Tyrogue', 'Hitmontop', 'Smoochum', 'Elekid', 'Magby', 'Miltank', 'Blissey', 'Raikou', 'Entei', 'Suicune', 'Larvitar', 'Pupitar', 'Tyranitar', 'Lugia', 'Ho-Oh', 'Celebi', 'Treecko', 'Grovyle', 'Sceptile', 'Torchic', 'Combusken', 'Blaziken', 'Mudkip', 'Marshtomp', 'Swampert', 'Poochyena', 'Mightyena', 'Zigzagoon', 'Linoone', 'Wurmple', 'Silcoon', 'Beautifly', 'Cascoon', 'Dustox', 'Lotad', 'Lombre', 'Ludicolo', 'Seedot', 'Nuzleaf', 'Shiftry', 'Taillow', 'Swellow', 'Wingull', 'Pelipper', 'Ralts', 'Kirlia', 'Gardevoir', 'Surskit', 'Masquerain', 'Shroomish', 'Breloom', 'Slakoth', 'Vigoroth', 'Slaking', 'Nincada', 'Ninjask', 'Shedinja', 'Whismur', 'Loudred', 'Exploud', 'Makuhita', 'Hariyama', 'Azurill', 'Nosepass', 'Skitty', 'Delcatty', 'Sableye', 'Mawile', 'Aron', 'Lairon', 'Aggron', 'Meditite', 'Medicham', 'Electrike', 'Manectric', 'Plusle', 'Minun', 'Volbeat', 'Illumise', 'Roselia', 'Gulpin', 'Swalot', 'Carvanha', 'Sharpedo', 'Wailmer', 'Wailord', 'Numel', 'Camerupt', 'Torkoal', 'Spoink', 'Grumpig', 'Spinda', 'Trapinch', 'Vibrava', 'Flygon', 'Cacnea', 'Cacturne', 'Swablu', 'Altaria', 'Zangoose', 'Seviper', 'Lunatone', 'Solrock', 'Barboach', 'Whiscash', 'Corphish', 'Crawdaunt', 'Baltoy', 'Claydol', 'Lileep', 'Cradily', 'Anorith', 'Armaldo', 'Feebas', 'Milotic', 'Castform', 'Kecleon', 'Shuppet', 'Banette', 'Duskull', 'Dusclops', 'Tropius', 'Chimecho', 'Absol', 'Wynaut', 'Snorunt', 'Glalie', 'Spheal', 'Sealeo', 'Walrein', 'Clamperl', 'Huntail', 'Gorebyss', 'Relicanth', 'Luvdisc', 'Bagon', 'Shelgon', 'Salamence', 'Beldum', 'Metang', 'Metagross', 'Regirock', 'Regice', 'Registeel', 'Latias', 'Latios', 'Kyogre', 'Groudon', 'Rayquaza', 'Jirachi', 'Deoxys-attack', 'Deoxys-defense', "Deoxys-speed", 'Deoxys-normal', 'Turtwig', 'Grotle', 'Torterra', 'Chimchar', 'Monferno', 'Infernape', 'Piplup', 'Prinplup', 'Empoleon', 'Starly', 'Staravia', 'Staraptor', 'Bidoof', 'Bibarel', 'Kricketot', 'Kricketune', 'Shinx', 'Luxio', 'Luxray', 'Budew', 'Roserade', 'Cranidos', 'Rampardos', 'Shieldon', 'Bastiodon', 'Burmy', 'Wormadam', 'Mothim', 'Combee', 'Vespiquen', 'Pachirisu', 'Buizel', 'Floatzel', 'Cherubi', 'Cherrim', 'Shellos', 'Gastrodon', 'Ambipom', 'Drifloon', 'Drifblim', 'Buneary', 'Lopunny', 'Mismagius', 'Honchkrow', 'Glameow', 'Purugly', 'Chingling', 'Stunky', 'Skuntank', 'Bronzor', 'Bronzong', 'Bonsly', 'Mime Jr.', 'Happiny', 'Chatot', 'Spiritomb', 'Gible', 'Gabite', 'Garchomp', 'Munchlax', 'Riolu', 'Lucario', 'Hippopotas', 'Hippowdon', 'Skorupi', 'Drapion', 'Croagunk', 'Toxicroak', 'Carnivine', 'Finneon', 'Lumineon', 'Mantyke', 'Snover', 'Abomasnow', 'Weavile', 'Magnezone', 'Lickilicky', 'Rhyperior', 'Tangrowth', 'Electivire', 'Magmortar', 'Togekiss', 'Yanmega', 'Leafeon', 'Glaceon', 'Gliscor', 'Mamoswine', 'Porygon-Z', 'Gallade', 'Probopass', 'Dusknoir', 'Froslass', 'Rotom', 'Uxie', 'Mesprit', 'Azelf', 'Dialga', 'Palkia', 'Heatran', 'Regigigas', 'Giratina-altered', 'Giratina-origin', 'Cresselia', 'Phione', 'Manaphy', 'Darkrai', 'Shaymin-land', 'Shaymin-sky', 'Arceus', 'Victini', 'Snivy', 'Servine', 'Serperior', 'Tepig', 'Pignite', 'Emboar', 'Oshawott', 'Dewott', 'Samurott', 'Patrat', 'Watchog', 'Lillipup', 'Herdier', 'Stoutland', 'Purrloin', 'Liepard', 'Pansage', 'Simisage', 'Pansear', 'Simisear', 'Panpour', 'Simipour', 'Munna', 'Musharna', 'Pidove', 'Tranquill', 'Unfezant', 'Blitzle', 'Zebstrika', 'Roggenrola', 'Boldore', 'Gigalith', 'Woobat', 'Swoobat', 'Drilbur', 'Excadrill', 'Audino', 'Timburr', 'Gurdurr', 'Conkeldurr', 'Tympole', 'Palpitoad', 'Seismitoad', 'Throh', 'Sawk', 'Sewaddle', 'Swadloon', 'Leavanny', 'Venipede', 'Whirlipede', 'Scolipede', 'Cottonee', 'Whimsicott', 'Petilil', 'Lilligant', 'Basculin', 'Sandile', 'Krokorok', 'Krookodile', 'Darumaka', 'Darmanitan', 'Maractus', 'Dwebble', 'Crustle', 'Scraggy', 'Scrafty', 'Sigilyph', 'Yamask', 'Cofagrigus', 'Tirtouga', 'Carracosta', 'Archen', 'Archeops', 'Trubbish', 'Garbodor', 'Zorua', 'Zoroark', 'Minccino', 'Cinccino', 'Gothita', 'Gothorita', 'Gothitelle', 'Solosis', 'Duosion', 'Reuniclus', 'Ducklett', 'Swanna', 'Vanillite', 'Vanillish', 'Vanilluxe', 'Deerling', 'Sawsbuck', 'Emolga', 'Karrablast', 'Escavalier', 'Foongus', 'Amoonguss', 'Frillish', 'Jellicent', 'Alomomola', 'Joltik', 'Galvantula', 'Ferroseed', 'Ferrothorn', 'Klink', 'Klang', 'Klinklang', 'Tynamo', 'Eelektrik', 'Eelektross', 'Elgyem', 'Beheeyem', 'Litwick', 'Lampent', 'Chandelure', 'Axew', 'Fraxure', 'Haxorus', 'Cubchoo', 'Beartic', 'Cryogonal', 'Shelmet', 'Accelgor', 'Stunfisk', 'Mienfoo', 'Mienshao', 'Druddigon', 'Golett', 'Golurk', 'Pawniard', 'Bisharp', 'Bouffalant', 'Rufflet', 'Braviary', 'Vullaby', 'Mandibuzz', 'Heatmor', 'Durant', 'Deino', 'Zweilous', 'Hydreigon', 'Larvesta', 'Volcarona', 'Cobalion', 'Terrakion', 'Virizion', 'Tornadus', 'Thundurus', 'Reshiram', 'Zekrom', 'Landorus', 'Kyurem', 'Keldeo-Ordinary', 'Keldeo-Resolute', 'Meloetta', 'Genesect', 'Chespin', 'Quilladin', 'Chesnaught', 'Fennekin', 'Braixen', 'Delphox', 'Froakie', 'Frogadier', 'Greninja', 'Bunnelby', 'Diggersby', 'Fletchling', 'Fletchinder', 'Talonflame', 'Scatterbug', 'Spewpa', 'Vivillon', 'Litleo', 'Pyroar', 'Flabébé', 'Floette', 'Florges', 'Skiddo', 'Gogoat', 'Pancham', 'Pangoro', 'Furfrou', 'Espurr', 'Meowstic', 'Honedge', 'Doublade', 'Aegislash', 'Spritzee', 'Aromatisse', 'Swirlix', 'Slurpuff', 'Inkay', 'Malamar', 'Binacle', 'Barbaracle', 'Skrelp', 'Dragalge', 'Clauncher', 'Clawitzer', 'Helioptile', 'Heliolisk', 'Tyrunt', 'Tyrantrum', 'Amaura', 'Aurorus', 'Sylveon', 'Hawlucha', 'Dedenne', 'Carbink', 'Goomy', 'Sliggoo', 'Goodra', 'Klefki', 'Phantump', 'Trevenant', 'Pumpkaboo', 'Gourgeist', 'Bergmite', 'Avalugg', 'Noibat', 'Noivern', 'Xerneas', 'Yveltal', 'Zygarde', 'Diancie', 'Hoopa', 'Volcanion', 'Rowlet', 'Dartrix', 'Decidueye', 'Litten', 'Torracat', 'Incineroar', 'Popplio', 'Brionne', 'Primarina', 'Pikipek', 'Trumbeak', 'Toucannon', 'Yungoos', 'Gumshoos', 'Grubbin', 'Charjabug', 'Vikavolt', 'Crabrawler', 'Crabominable', 'Oricorio', 'Cutiefly', 'Ribombee', 'Rockruff', 'Lycanroc', 'Wishiwashi', 'Mareanie', 'Toxapex', 'Mudbray', 'Mudsdale', 'Dewpider', 'Araquanid', 'Fomantis', 'Lurantis', 'Morelull', 'Shiinotic', 'Salandit', 'Salazzle', 'Stufful', 'Bewear', 'Bounsweet', 'Steenee', 'Tsareena', 'Comfey', 'Oranguru', 'Passimian', 'Wimpod', 'Golisopod', 'Sandygast', 'Palossand', 'Pyukumuku', 'Type: Null', 'Silvally', 'Minior', 'Komala', 'Turtonator', 'Togedemaru', 'Mimikyu', 'Bruxish', 'Drampa', 'Dhelmise', 'Jangmo-o', 'Hakamo-o', 'Kommo-o', 'Tapu Koko', 'Tapu Lele', 'Tapu Bulu', 'Tapu Fini', 'Cosmog', 'Cosmoem', 'Solgaleo', 'Lunala', 'Nihilego', 'Buzzwole', 'Pheromosa', 'Xurkitree', 'Celesteela', 'Kartana', 'Guzzlord', 'Necrozma', 'Magearna', 'Marshadow', 'Poipole', 'Naganadel', 'Stakataka', 'Blacephalon', 'Zeraora', 'Meltan', 'Melmetal', 'Grookey', 'Thwackey', 'Rillaboom', 'Scorbunny', 'Raboot', 'Cinderace', 'Sobble', 'Drizzile', 'Inteleon', 'Skwovet', 'Greedent', 'Rookidee', 'Corvisquire', 'Corviknight', 'Blipbug', 'Dottler', 'Orbeetle', 'Nickit', 'Thievul', 'Gossifleur', 'Eldegoss', 'Wooloo', 'Dubwool', 'Chewtle', 'Drednaw', 'Yamper', 'Boltund', 'Rolycoly', 'Carkol', 'Coalossal', 'Applin', 'Flapple', 'Appletun', 'Silicobra', 'Sandaconda', 'Cramorant', 'Arrokuda', 'Barraskewda', 'Toxel', 'Toxtricity', 'Sizzlipede', 'Centiskorch', 'Clobbopus', 'Grapploct', 'Sinistea', 'Polteageist', 'Hatenna', 'Hattrem', 'Hatterene', 'Impidimp', 'Morgrem', 'Grimmsnarl', 'Obstagoon', 'Perrserker', 'Cursola', "Sirfetch'd", 'Mr. Rime', 'Runerigus', 'Milcery', 'Alcremie', 'Falinks', 'Pincurchin', 'Snom', 'Frosmoth', 'Stonjourner', 'Eiscue', 'Indeedee', 'Morpeko', 'Cufant', 'Copperajah', 'Dracozolt', 'Arctozolt', 'Dracovish', 'Arctovish', 'Duraludon', 'Dreepy', 'Drakloak', 'Dragapult', 'Zacian', 'Zamazenta', 'Eternatus', 'Kubfu', 'Urshifu', 'Zarude', 'Regieleki', 'Regidrago', 'Glastrier', 'Spectrier', 'Calyrex', 'Wyrdeer', 'Kleavor', 'Ursaluna', 'Basculegion', 'Sneasler', 'Overqwil', 'Enamorus']
pokemon_matcher = PokemonFuzzyMatcher(POKEMON)

# Reference to the global state maps from core.py
# These should be imported or passed in instead of reimplementing
# VERSION_MAP = {}
# SESSION_MAP = {}


async def process_pokemon_message(bot, message, session_map, version_map):
    """Process a message as a Pokemon name when in a session"""
    game = session_map[str(message.author.id)]
    gen = find_game_version(game)
    
    user_input = message.content.strip()
    pokemon = pokemon_matcher.find_best_match(user_input, threshold=0.7)

    if not pokemon:
        # Suggest alternatives if no good match found
        suggestions = pokemon_matcher.find_multiple_matches(user_input, threshold=0.4, max_results=3)
        if suggestions:
            suggestion_text = ", ".join([match[0] for match in suggestions])
            await message.channel.send(f"❌ Pokemon '{user_input}' not found. Did you mean: **{suggestion_text}**?")
        else:
            await message.channel.send(f"❌ Pokemon '{user_input}' not found. Please check your spelling.")
        return

    # Add this to inform user if we corrected their input
    if pokemon.lower() != user_input.lower():
        await message.channel.send(f"Did you mean **{pokemon}**? Showing data for {pokemon}:")

    pokemon = pokemon.lower()  # Keep your existing lowercase requirement
    
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
    species_name = None
    if len(pokemon.split("-")) > 1:
        species_name = pokemon.split("-")[0]
    else:
        species_name = pokemon
    poke_data = getPokemonData(pokemon)
    species_data = getSpeciesData(species_name)
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
        
        user_input = pokemon.strip()
        matched_pokemon = pokemon_matcher.find_best_match(user_input, threshold=0.7)

        if not matched_pokemon:
            suggestions = pokemon_matcher.find_multiple_matches(user_input, threshold=0.4, max_results=3)
            if suggestions:
                suggestion_text = ", ".join([match[0] for match in suggestions])
                await ctx.send(f"❌ Pokemon '{user_input}' not found. Did you mean: **{suggestion_text}**?")
            else:
                await ctx.send(f"❌ Pokemon '{user_input}' not found. Please check your spelling.")
            return

        if matched_pokemon.lower() != user_input.lower():
            await ctx.send(f"Did you mean **{matched_pokemon}**? Showing learnset for {matched_pokemon}:")

        pokemon = matched_pokemon.lower()
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
        user_input = pokemon.strip()
        matched_pokemon = pokemon_matcher.find_best_match(user_input, threshold=0.7)

        if not matched_pokemon:
            suggestions = pokemon_matcher.find_multiple_matches(user_input, threshold=0.4, max_results=3)
            if suggestions:
                suggestion_text = ", ".join([match[0] for match in suggestions])
                await ctx.send(f"❌ Pokemon '{user_input}' not found. Did you mean: **{suggestion_text}**?")
            else:
                await ctx.send(f"❌ Pokemon '{user_input}' not found. Please check your spelling.")
            return

        if matched_pokemon.lower() != user_input.lower():
            await ctx.send(f"Did you mean **{matched_pokemon}**? Showing evolution data for {matched_pokemon}:")

        pokemon = matched_pokemon.lower()
        
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
        user_input = pokemon.strip()
        matched_pokemon = pokemon_matcher.find_best_match(user_input, threshold=0.7)

        if not matched_pokemon:
            suggestions = pokemon_matcher.find_multiple_matches(user_input, threshold=0.4, max_results=3)
            if suggestions:
                suggestion_text = ", ".join([match[0] for match in suggestions])
                await ctx.send(f"❌ Pokemon '{user_input}' not found. Did you mean: **{suggestion_text}**?")
            else:
                await ctx.send(f"❌ Pokemon '{user_input}' not found. Please check your spelling.")
            return

        if matched_pokemon.lower() != user_input.lower():
            await ctx.send(f"Did you mean **{matched_pokemon}**? Showing data for {matched_pokemon}:")

        pokemon = matched_pokemon.lower()
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