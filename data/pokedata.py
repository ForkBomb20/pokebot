"""
Pokemon data retrieval and processing functions
"""
import requests
import json
import pandas as pd
from table2ascii import table2ascii as t2a, PresetStyle
from math import floor
from functools import lru_cache

# Constants
VERSIONS = [
    ["red", "blue", "yellow"],
    ["gold", "silver", "crystal"],
    ["ruby", "saphire", "emerald", "firered", "leafgreen"],
    ["diamond", "pearl", "platinum", "heartgold", "soulsilver"],
    ["black", "white", "black2", "white2"],
    ["x", "y", "omega-ruby", "alpha-saphire"],
    ["sun", "moon", "ultra-sun", "ultra-moon", "lets-go-pikachu", "lets-go-eevee"],
    ["sword", "shield"]
]

VERSION_GROUPS = [
    ["red-blue", "yellow"],
    ["gold-silver", "crystal"],
    ["ruby-saphire", "emerald", "firered-leafgreen"],
    ["diamond-pearl", "platinum", "heartgold-soulsilver"],
    ["black-white", "black-2-white-2"],
    ["x-y", "omega-ruby-alpha-saphire"],
    ["sun-moon", "ultra-sun-ultra-moon", "lets-go-pikachu-lets-go-eevee"],
    ["sword-shield"]
]

VERSION_MAPPINGS = {
    "red": "red-blue", "blue": "red-blue", "yellow": "yellow",
    "gold": "gold-silver", "silver": "gold-silver", "crystal": "crystal",
    "ruby": "ruby-saphire", "saphire": "ruby-saphire", "emerald": "emerald",
    "firered": "firered-leafgreen", "leafgreen": "firered-leafgreen",
    "diamond": "diamond-pearl", "pearl": "diamond-pearl", "platinum": "platinum",
    "heartgold": "heartgold-soulsilver", "soulsilver": "heartgold-soulsilver",
    "black": "black-white", "white": "black-white", "black2": "black-2-white-2", "white2": "black-2-white-2",
    "x": "x-y", "y": "x-y", "omega-ruby": "omega-ruby-alpha-saphire", "alpha-saphire": "omega-ruby-alpha-saphire",
    "sun": "sun-moon", "moon": "sun-moon", "ultra-sun": "ultra-sun-ultra-moon", "ultra-moon": "ultra-sun-ultra-moon",
    "lets-go-pikachu": "lets-go-pikachu-lets-go-eevee", "lets-go-eevee": "lets-go-pikachu-lets-go-eevee",
    "sword": "sword-shield", "shield": "sword-shield"
}

GENERATIONS = [
    "generation-i", "generation-ii", "generation-iii", "generation-iv",
    "generation-v", "generation-vi", "generation-vii", "generation-viii"
]


@lru_cache(maxsize=100)
def getPokemonData(name):
    """Get Pokemon data from the API"""
    name = name.strip().lower()
    json_text = requests.get(f"https://pokeapi.co/api/v2/pokemon/{name}/").text
    poke_data = json.loads(json_text)
    return poke_data


@lru_cache(maxsize=100)
def getSpeciesData(name):
    """Get Pokemon species data from the API"""
    name = name.strip().lower()
    json_text = requests.get(f"https://pokeapi.co/api/v2/pokemon-species/{name}/").text
    species_data = json.loads(json_text)
    return species_data


def getTheGenus(species_data):
    """Get the genus of a Pokemon"""
    genus_name = ""
    for genus in species_data["genera"]:
        if genus["language"]["name"] == "en":
            genus_name = genus["genus"]
    return "The " + genus_name


def getFirstGen(species_data):
    """Get the first generation a Pokemon appeared in"""
    first_gen = species_data["generation"]["name"]
    gen = GENERATIONS.index(first_gen)
    return gen


def getDescription(species_data, gen):
    """Get a Pokemon's description for a specific generation"""
    flavor_text_entries = species_data["flavor_text_entries"]
    versions = VERSIONS[gen - 1]
    description = "No Description"
    for flavor_text in flavor_text_entries:
        if flavor_text["version"]["name"] in versions and flavor_text["language"]["name"] == "en":
            return flavor_text["flavor_text"]
    return description


def getLocations(poke_data, gen):
    """Get locations where a Pokemon can be found"""
    location_url = poke_data["location_area_encounters"]
    json_text = requests.get(location_url).text
    location_data = json.loads(json_text)

    locations = []
    for location in location_data:
        version_details = location["version_details"]
        for version in version_details:
            if version["version"]["name"] in VERSIONS[gen - 1]:
                location_name = location["location_area"]["name"].replace("-", " ")
                encounter_details = version["encounter_details"]
                min_level = encounter_details[0]["min_level"]
                max_level = encounter_details[0]["max_level"]
                chance = version["max_chance"]
                # Return or append to locations list as needed
    return locations


@lru_cache(maxsize=50)
def getGrowthRateData(name):
    """Get a Pokemon's growth rate data"""
    name = name.lower().strip()
    slow = json.loads(requests.get("https://pokeapi.co/api/v2/growth-rate/1/").text)
    medium = json.loads(requests.get("https://pokeapi.co/api/v2/growth-rate/2/").text)
    fast = json.loads(requests.get("https://pokeapi.co/api/v2/growth-rate/3/").text)
    medium_slow = json.loads(requests.get("https://pokeapi.co/api/v2/growth-rate/4/").text)
    slow_fast = json.loads(requests.get("https://pokeapi.co/api/v2/growth-rate/5/").text)
    fast_slow = json.loads(requests.get("https://pokeapi.co/api/v2/growth-rate/6/").text)

    slow_pokemon = slow["pokemon_species"]
    medium_pokemon = medium_slow["pokemon_species"]
    fast_pokemon = fast["pokemon_species"]
    medium_slow_pokemon = medium_slow["pokemon_species"]
    slow_fast_pokemon = slow_fast["pokemon_species"]
    fast_slow_pokemon = fast_slow["pokemon_species"]

    slow_names = [mon["name"] for mon in slow_pokemon]
    medium_names = [mon["name"] for mon in medium_pokemon]
    fast_names = [mon["name"] for mon in fast_pokemon]
    medium_slow_names = [mon["name"] for mon in medium_slow_pokemon]
    slow_fast_names = [mon["name"] for mon in slow_fast_pokemon]
    fast_slow_names = [mon["name"] for mon in fast_slow_pokemon]

    if name in slow_names:
        return "Slow"
    elif name in medium_names:
        return "Medium"
    elif name in fast_names:
        return "Fast"
    elif name in medium_slow_names:
        return "Medium Slow"
    elif name in slow_fast_names:
        return "Slow Then Very Fast"
    elif name in fast_slow_names:
        return "Fast Then Very Slow"
    else:
        return "Medium Fast, Eratic, or Unknown"


def getTypes(poke_data, gen):
    """Get a Pokemon's types for a specific generation"""
    types = []

    if len(poke_data["past_types"]) != 0:
        key_gen_name = poke_data["past_types"][0]["generation"]["name"]
        gen_num = GENERATIONS.index(key_gen_name) + 1
        if gen <= gen_num:
            types_data = poke_data["past_types"][0]["types"]
            for slot in types_data:
                types.append(slot["type"]["name"])
        else:
            types_data = poke_data["types"]
            for slot in types_data:
                types.append(slot["type"]["name"])
    else:
        types_data = poke_data["types"]
        for slot in types_data:
            types.append(slot["type"]["name"])

    return types


# @lru_cache(maxsize=50)
def getDamageRelations(types):
    """Get damage relations for a Pokemon's types"""
    if not isinstance(types, tuple):
        types = tuple(types)  # Convert list to tuple for caching
        
    all_types = [
        "normal", "fire", "water", "electric", "grass", "ice", "fighting", "poison",
        "ground", "flying", "psychic", "bug", "rock", "ghost", "dragon", "dark", "steel", "fairy"
    ]

    @lru_cache(maxsize=20)
    def get_multipliers(type_name):
        response = requests.get(f"https://pokeapi.co/api/v2/type/{type_name}")
        type_data = json.loads(response.text)["damage_relations"]

        double_from = [cur_type["name"] for cur_type in type_data["double_damage_from"]]
        half_from = [cur_type["name"] for cur_type in type_data["half_damage_from"]]
        none_from = [cur_type["name"] for cur_type in type_data["no_damage_from"]]

        multipliers = {}
        for atype in all_types:
            if atype in double_from:
                multipliers[atype] = 2
            elif atype in half_from:
                multipliers[atype] = 0.5
            elif atype in none_from:
                multipliers[atype] = 0
            else:
                multipliers[atype] = 1
        return multipliers

    if len(types) == 1:
        return get_multipliers(types[0])
    else:
        multipliers = {}
        for type_name in types:
            multipliers[type_name] = get_multipliers(type_name)

        return {k: multipliers[types[0]][k] * multipliers[types[1]][k] for k in multipliers[types[0]]}


def getMoves(poke_data, game):
    """Get moves a Pokemon can learn in a specific game"""
    moves_data = poke_data["moves"]
    df_moves_data = []
    
    for move in moves_data:
        version_group_details = move["version_group_details"]
        for version in version_group_details:
            if (version["version_group"]["name"] == VERSION_MAPPINGS.get(game) and 
                version["move_learn_method"]["name"] == "level-up"):
                
                move_name = move["move"]["name"]
                data_url = move["move"]["url"]
                learn_level = version["level_learned_at"]

                move_json = requests.get(data_url).text
                move_data = json.loads(move_json)

                ptype = move_data["type"]["name"]
                category = move_data["damage_class"]["name"]
                pwr = move_data["power"]
                acc = move_data["accuracy"]
                pp = move_data["pp"]

                row = {
                    "Level": learn_level, 
                    "Move": move_name, 
                    "Type": ptype,
                    "Category": category, 
                    "Power": pwr, 
                    "Accuracy": acc, 
                    "PP": pp
                }
                df_moves_data.append(row)

    if not df_moves_data:
        return "No level-up moves found for this Pokemon in this game version."
        
    moves = pd.DataFrame(df_moves_data)
    sorted_moves = moves.sort_values(by=["Level"])

    table_string = t2a(header=sorted_moves.columns.tolist(),
                       body=sorted_moves.values.tolist(),
                       style=PresetStyle.thin_compact)

    return table_string

def getEvolutions(species_data):
    """Get evolutions for a particular pokemon species."""
    evo_chain_url = species_data["evolution_chain"]["url"]
    evo_json = json.loads(requests.get(evo_chain_url).text)
    chain = evo_json["chain"]

    def extract_evolution_chain(chain):
        """
        Recursively extracts the evolution chain and conditions from the given chain dictionary.
        """

        def recurse_evolutions(chain, current_chain, current_conditions):
            current_species = chain['species']['name']
            current_chain.append(current_species)

            # Collect evolution details for current species
            if chain['evolution_details']:
                conditions = {}
                for detail in chain['evolution_details'][0]:
                    condition_value = chain['evolution_details'][0][detail]
                    if condition_value not in [None, False, "", 0]:
                        conditions[detail] = condition_value
                current_conditions.append(conditions)
            else:
                current_conditions.append({})

            if not chain['evolves_to']:
                evolution_chains.append(current_chain.copy())
                evolution_conditions.append(current_conditions.copy())
            for next_chain in chain['evolves_to']:
                recurse_evolutions(next_chain, current_chain.copy(), current_conditions.copy())

        evolution_chains = []
        evolution_conditions = []
        recurse_evolutions(chain, [], [])
        return evolution_chains, evolution_conditions

    # Example JSON data

    return extract_evolution_chain(chain)

def getCaptureRate(species_data, poke_data, level, p, ball, status):
    rate = int(species_data["capture_rate"])
    base = [stat for stat in poke_data["stats"] if stat["name"] == "hp"][0]
    max_hp = floor((2*base*level/100)) + level + 10
    chance = (( 1 + max_hp*(3-2*p) * rate * ball * status) / ( 3 * max_hp )) / 256

    return chance

def find_game_version(game):
    for index, version_list in enumerate(VERSIONS):
        if game in version_list:
            return index + 1
    return None

def serebiiURL(gen, dex_num):
    games_abbrs = ["", "gs", "rs", "dp", "bw", "xy", "sm", "swsh"]
    abbr = games_abbrs[gen - 1]
    if abbr != "":
        abbr = "-" + abbr
    url = f"https://www.serebii.net/pokedex{abbr}/{dex_num}.shtml"
    return url