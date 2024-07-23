import requests
import json
import pandas as pd
from table2ascii import table2ascii as t2a, PresetStyle
from math import floor

VERSIONS = [["red", "blue", "yellow"], ["gold", "silver", "crystal"], ["ruby", "saphire", "emerald", "firered", "leafgreen"],
            ["diamond", "pearl", "platinum", "heartgold", "soulsilver"], [
                "black", "white", "black2", "white2"], ["x", "y", "omega-ruby", "alpha-saphire"],
            ["sun", "moon", "ultra-sun", "ultra-moon", "lets-go-pikachu", "lets-go-eevee"], ["sword", "shield"]]

VERSION_GROUPS = [["red-blue", "yellow"], ["gold-silver", "crystal"], ["ruby-saphire", "emerald", "firered-leafgreen"],
                  ["diamond-pearl", "platinum", "heartgold-soulsilver"], ["black-white",
                                                                          "black-2-white-2"], ["x-y", "omega-ruby-alpha-saphire"],
                  ["sun-moon", "ultra-sun-ultra-moon", "lets-go-pikachu-lets-go-eevee"], ["sword-shield"]]

VERSION_MAPPINGS = {"red":"red-blue", "blue":"red-blue", "yellow":"yellow", "gold":"gold-silver",
                    "silver":"gold-silver", "crystal":"crystal", "ruby":"ruby-saphire", "saphire":"ruby-saphire",
                    "emerald":"emerald", "firered":"firered-leafgreen", "leafgreen":"firered-leafgreen",
                    "diamond":"diamond-pearl", "pearl":"diamond-pearl", "platinum":"platinum",
                    "heartgold":"heartgold-soulsilver", "soulsilver":"heartgold-soulsilver", "black":"black-white",
                    "white":"black-white","black2":"black-2-white-2", "white2":"black-2-white-2",
                    "x":"x-y", "y":"x-y", "omega-ruby":"omega-ruby-alpha-saphire", "alpha-saphire":"omega-ruby-alpha-saphire",
                    "sun":"sun-moon", "moon":"sun-moon", "ultra-sun":"ultra-sun-ultra-moon", "ultra-moon":"ultra-sun-ultra-moon",
                    "lets-go-pikachu":"lets-go-pikachu-lets-go-eevee", "lets-go-eevee":"lets-go-pikachu-lets-go-eevee",
                    "sword":"sword-shield", "shield":"sword-shield"}


GENERATIONS = ["generation-i", "generation-ii", "generation-iii", "generation-iv",
               "generation-v", "generation-vi", "generation-vii", "generation-viii"]


def getPokemonData(name):
    name = name.strip().lower()
    json_text = requests.get(f"https://pokeapi.co/api/v2/pokemon/{name}/").text
    poke_data = json.loads(json_text)
    return poke_data


def getSpeciesData(name):
    name = name.strip().lower()
    json_text = requests.get(
        f"https://pokeapi.co/api/v2/pokemon-species/{name}/").text
    species_data = json.loads(json_text)
    return species_data

def getTheGenus(species_data):
    genus_name = ""
    for genus in species_data["genera"]:
        if genus["language"]["name"] == "en":
            genus_name = genus["genus"]
    return "The " + genus_name


def getFirstGen(species_data):
    first_gen = species_data["generation"]["name"]
    gen = GENERATIONS.index(first_gen)
    return gen


def getDescription(species_data, gen):
    flavor_text_entries = species_data["flavor_text_entries"]
    versions = VERSIONS[gen - 1]
    description = "No Description"
    for flavor_text in flavor_text_entries:
        if flavor_text["version"]["name"] in versions and flavor_text["language"]["name"] == "en":
            return flavor_text["flavor_text"]

    return description


def getLocations(poke_data, gen):
    location_url = poke_data["location_area_encounters"]
    json_text = requests.get(location_url).text
    location_data = json.loads(json_text)

    locations = []
    for location in location_data:
        version_details = location["version_details"]
        for version in version_details:
            if version["version"]["name"] in VERSIONS[gen - 1]:
                location_name = location["location_area"]["name"].replace(
                    "-", " ")
                encounter_details = version["encounter_details"]
                min_level = encounter_details[0]["min_level"]
                max_level = encounter_details[0]["max_level"]
                chance = version["max_chance"]


def getGrowthRateData(name):
    name = name.lower().strip()
    slow = json.loads(requests.get(
        "https://pokeapi.co/api/v2/growth-rate/1/").text)
    medium = json.loads(requests.get(
        "https://pokeapi.co/api/v2/growth-rate/2/").text)
    fast = json.loads(requests.get(
        "https://pokeapi.co/api/v2/growth-rate/3/").text)
    medium_slow = json.loads(requests.get(
        "https://pokeapi.co/api/v2/growth-rate/4/").text)
    slow_fast = json.loads(requests.get(
        "https://pokeapi.co/api/v2/growth-rate/5/").text)
    fast_slow = json.loads(requests.get(
        "https://pokeapi.co/api/v2/growth-rate/6/").text)

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


# def getDamageRelations(types):
#     all_types = ["normal", "fire", "water", "electric", "grass", "ice", "fighting", "poison",
#                  "ground", "flying", "psychic", "bug", "rock", "ghost", "dragon", "dark", "steel", "fairy"]
#     damage_relations = {}
#     if len(types) == 1:
#         json_text = requests.get(
#             f"https://pokeapi.co/api/v2/type/{types[0]}").text
#         type_data = json.loads(json_text)
#         damage_relations_dict = type_data["damage_relations"]
#         double_from = [cur_type["name"]
#                        for cur_type in damage_relations_dict["double_damage_from"]]
#         double_to = [cur_type["name"]
#                      for cur_type in damage_relations_dict["double_damage_to"]]
#         half_from = [cur_type["name"]
#                      for cur_type in damage_relations_dict["half_damage_from"]]
#         half_to = [cur_type["name"]
#                    for cur_type in damage_relations_dict["double_damage_to"]]
#         none_from = [cur_type["name"]
#                      for cur_type in damage_relations_dict["no_damage_from"]]
#         none_to = [cur_type["name"]
#                    for cur_type in damage_relations_dict["no_damage_to"]]
#         multipliers = {}
#         for atype in all_types:
#             if atype in double_from:
#                 multipliers[atype] = 2
#             elif atype in half_from:
#                 multipliers[atype] = 0.5
#             elif atype in none_from:
#                 multipliers[atype] = 0
#             else:
#                 multipliers[atype] = 1
#         damage_relations = multipliers
#     else:
#         for type in types:
#             json_text = requests.get(
#                 f"https://pokeapi.co/api/v2/type/{type}").text
#             type_data = json.loads(json_text)
#             damage_relations_dict = type_data["damage_relations"]
#             double_from = [cur_type["name"]
#                            for cur_type in damage_relations_dict["double_damage_from"]]
#             double_to = [cur_type["name"]
#                          for cur_type in damage_relations_dict["double_damage_to"]]
#             half_from = [cur_type["name"]
#                          for cur_type in damage_relations_dict["half_damage_from"]]
#             half_to = [cur_type["name"]
#                        for cur_type in damage_relations_dict["double_damage_to"]]
#             none_from = [cur_type["name"]
#                          for cur_type in damage_relations_dict["no_damage_from"]]
#             none_to = [cur_type["name"]
#                        for cur_type in damage_relations_dict["no_damage_to"]]
#             effected = double_from + double_to + half_from + half_to + none_from + none_to
#             multipliers = {}
#             for atype in all_types:
#                 if atype in double_from:
#                     multipliers[atype] = 2
#                 elif atype in half_from:
#                     multipliers[atype] = 0.5
#                 elif atype in none_from:
#                     multipliers[atype] = 0
#                 else:
#                     multipliers[atype] = 1
#             damage_relations[type] = multipliers
#         damage_relations = {
#             k: damage_relations[types[0]][k] * damage_relations[types[1]][k] for k in damage_relations[types[0]]}

#     return damage_relations


def getDamageRelations(types):
    all_types = ["normal", "fire", "water", "electric", "grass", "ice", "fighting", "poison",
                 "ground", "flying", "psychic", "bug", "rock", "ghost", "dragon", "dark", "steel", "fairy"]

    def get_multipliers(type_name):
        response = requests.get(f"https://pokeapi.co/api/v2/type/{type_name}")
        type_data = json.loads(response.text)["damage_relations"]

        double_from = [cur_type["name"]
                       for cur_type in type_data["double_damage_from"]]
        double_to = [cur_type["name"]
                     for cur_type in type_data["double_damage_to"]]
        half_from = [cur_type["name"]
                     for cur_type in type_data["half_damage_from"]]
        half_to = [cur_type["name"]
                   for cur_type in type_data["double_damage_to"]]
        none_from = [cur_type["name"]
                     for cur_type in type_data["no_damage_from"]]
        none_to = [cur_type["name"] for cur_type in type_data["no_damage_to"]]
        effected = double_from + double_to + half_from + half_to + none_from + none_to

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
        for type in types:
            multipliers[type] = get_multipliers(type)

        return {k: multipliers[types[0]][k] * multipliers[types[1]][k] for k in multipliers[types[0]]}


# def getMoves(poke_data, gen):
#     moves_data = poke_data["moves"]
#     df_moves_data = []
#     version_group = VERSION_GROUPS[gen - 1]
#     for move in moves_data:
#         version_group_details = move["version_group_details"]
#         for version in version_group_details:
#             if version["version_group"]["name"] == version_group[0] and version["move_learn_method"]["name"] == "level-up":
#                 move_name = move["move"]["name"]
#                 data_url = move["move"]["url"]
#                 learn_level = version["level_learned_at"]

#                 move_json = requests.get(data_url).text
#                 move_data = json.loads(move_json)

#                 type = move_data["type"]["name"]
#                 category = move_data["damage_class"]["name"]
#                 pwr = move_data["power"]
#                 acc = move_data["accuracy"]
#                 pp = move_data["pp"]

#                 row = {"Level": learn_level, "Move": move_name, "Type": type,
#                        "Category": category, "Power": pwr, "Accuracy": acc, "PP": pp}
#                 df_moves_data.append(row)

#                 moves = pd.DataFrame(df_moves_data)
#                 sorted_moves = moves.sort_values(by=["Level"])

#     return sorted_moves.to_string(index=False, col_space=14, justify="left")

def getMoves(poke_data, game):
    moves_data = poke_data["moves"]
    df_moves_data = []
    # version_group = VERSION_GROUPS[gen - 1]
    for move in moves_data:
        version_group_details = move["version_group_details"]
        for version in version_group_details:
            if version["version_group"]["name"] == VERSION_MAPPINGS[game] and version["move_learn_method"]["name"] == "level-up":
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

                row = {"Level": learn_level, "Move": move_name, "Type": ptype,
                       "Category": category, "Power": pwr, "Accuracy": acc, "PP": pp}
                df_moves_data.append(row)

    moves = pd.DataFrame(df_moves_data)
    sorted_moves = moves.sort_values(by=["Level"])

    table_string = t2a(header=sorted_moves.columns.tolist(), body=sorted_moves.values.tolist(), style=PresetStyle.thin_compact )

    # Create a list of strings representing each row in the table
    # rows = []
    # rows = []
    # for index, row in sorted_moves.iterrows():
    #     row_string = "| ".join(str(value) for value in row.values)
    #     rows.append(f"|{row_string}|")
    #
    # # Create the header row
    # header_row = "| ".join(sorted_moves.columns)
    # header_row = f"|{header_row}|"
    #
    # # Join all rows together into a single string
    # table_string = "\n".join([header_row] + rows)

    return table_string

def getEvolutions(species_data):
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





# def main():
#     print(getEvolutions("regirock", 6))


# if __name__ == "__main__":
#     main()
  