from math import floor, ceil, sqrt


PHYSICAL_TYPES = {"normal", "fighting", "flying", "poison", "ground", "rock", "bug", "ghost", "steel"}
SPECIAL_TYPES = {"fire", "water", "grass", "electric", "psychic", "ice", "dragon", "dark"}

GEN_DEFAULT_GAMES = {
    1: "yellow",
    2: "crystal",
    3: "emerald",
    4: "platinum",
    5: "black2",
    6: "omega-ruby",
    7: "ultra-sun",
    8: "sword",
    9: "scarlet",
}


def poke_round(value: float) -> int:
    return floor(value + 0.5)


def calc_stat_gen12(base: int, level: int, is_hp: bool) -> int:
    dv = 15
    stat_exp = 65535
    ev_contribution = floor(ceil(sqrt(stat_exp)) / 4)
    if is_hp:
        return floor(((base + dv) * 2 + ev_contribution) * level / 100) + level + 10
    return floor(((base + dv) * 2 + ev_contribution) * level / 100) + 5


def calc_stat_gen3plus(base: int, level: int, is_hp: bool) -> int:
    iv = 31
    ev = 0
    if is_hp:
        return floor((2 * base + iv + floor(ev / 4)) * level / 100) + level + 10
    return floor((2 * base + iv + floor(ev / 4)) * level / 100) + 5


def calc_stat(base: int, level: int, is_hp: bool, gen: int) -> int:
    if gen <= 2:
        return calc_stat_gen12(base, level, is_hp)
    return calc_stat_gen3plus(base, level, is_hp)


def get_offensive_stat_name(move_type: str, gen: int, move_category: str) -> str:
    if gen <= 3:
        if move_type in PHYSICAL_TYPES:
            return "attack"
        return "special-attack"
    return "attack" if move_category == "physical" else "special-attack"


def get_defensive_stat_name(move_type: str, gen: int, move_category: str) -> str:
    if gen == 1:
        if move_type in PHYSICAL_TYPES:
            return "defense"
        return "special-attack"
    if gen <= 3:
        if move_type in PHYSICAL_TYPES:
            return "defense"
        return "special-defense"
    return "defense" if move_category == "physical" else "special-defense"


def get_single_type_effectiveness(move_type: str, def_type: str, type_chart: dict) -> float:
    return type_chart.get((move_type, def_type), 1.0)


def get_type_effectiveness(move_type: str, defender_types: list[str], type_chart: dict) -> float:
    multiplier = 1.0
    for def_type in defender_types:
        multiplier *= type_chart.get((move_type, def_type), 1.0)
    return multiplier


def _apply_type_effectiveness_per_type(damage: int, move_type: str, defender_types: list[str], type_chart: dict) -> int:
    for def_type in defender_types:
        eff = type_chart.get((move_type, def_type), 1.0)
        damage = floor(damage * eff)
    return damage


def calc_damage_gen12(
    level: int,
    power: int,
    attack_stat: int,
    defense_stat: int,
    stab: bool,
    move_type: str,
    defender_types: list[str],
    type_chart: dict,
) -> tuple[int, int]:
    # Gen I-II order: Base → STAB → Type1 → Type2 → Random
    base = floor(floor(floor(2 * level / 5 + 2) * power * attack_stat / defense_stat) / 50)
    base = min(base, 997) + 2

    if stab:
        base = floor(base * 3 / 2)

    base = _apply_type_effectiveness_per_type(base, move_type, defender_types, type_chart)

    if base == 0:
        return 0, 0

    min_roll = floor(base * 217 / 255)
    max_roll = floor(base * 255 / 255)

    return max(min_roll, 1), max(max_roll, 1)


def calc_damage_gen34(
    level: int,
    power: int,
    attack_stat: int,
    defense_stat: int,
    stab: bool,
    move_type: str,
    defender_types: list[str],
    type_chart: dict,
) -> tuple[int, int]:
    # Gen III-IV order: Base → Random → STAB → Type1 → Type2
    base = floor(floor(floor(2 * level / 5 + 2) * power * attack_stat / defense_stat) / 50) + 2

    def apply_after_random(damage: int) -> int:
        if stab:
            damage = floor(damage * 3 / 2)
        damage = _apply_type_effectiveness_per_type(damage, move_type, defender_types, type_chart)
        return damage

    min_roll = apply_after_random(floor(base * 85 / 100))
    max_roll = apply_after_random(floor(base * 100 / 100))

    if min_roll == 0 and max_roll == 0:
        return 0, 0

    return max(min_roll, 1), max(max_roll, 1)


def calc_damage_gen5plus(
    level: int,
    power: int,
    attack_stat: int,
    defense_stat: int,
    stab: bool,
    move_type: str,
    defender_types: list[str],
    type_chart: dict,
) -> tuple[int, int]:
    # Gen V+ order: Base → Random → STAB (pokeRound, 4096 system) → Type1 → Type2
    base = floor(floor(floor(2 * level / 5 + 2) * power * attack_stat / defense_stat) / 50) + 2

    stab_mod = 6144 if stab else 4096

    def apply_after_random(damage: int) -> int:
        damage = poke_round(damage * stab_mod / 4096)
        damage = _apply_type_effectiveness_per_type(damage, move_type, defender_types, type_chart)
        return damage

    min_roll = apply_after_random(floor(base * 85 / 100))
    max_roll = apply_after_random(floor(base * 100 / 100))

    if min_roll == 0 and max_roll == 0:
        return 0, 0

    return max(min_roll, 1), max(max_roll, 1)


def calc_damage(
    level: int,
    power: int,
    attack_stat: int,
    defense_stat: int,
    gen: int,
    stab: bool,
    move_type: str,
    defender_types: list[str],
    type_chart: dict,
) -> tuple[int, int]:
    if gen <= 2:
        return calc_damage_gen12(level, power, attack_stat, defense_stat, stab, move_type, defender_types, type_chart)
    elif gen <= 4:
        return calc_damage_gen34(level, power, attack_stat, defense_stat, stab, move_type, defender_types, type_chart)
    else:
        return calc_damage_gen5plus(level, power, attack_stat, defense_stat, stab, move_type, defender_types, type_chart)


def calculate_move_damage(
    move: dict,
    attacker_stats: dict[str, int],
    defender_stats: dict[str, int],
    attacker_types: list[str],
    defender_types: list[str],
    level: int,
    gen: int,
    type_chart: dict,
) -> dict | None:
    power = move.get("power")
    if not power:
        return None

    move_type = move["type"]
    move_category = move.get("category", "physical")

    atk_stat_name = get_offensive_stat_name(move_type, gen, move_category)
    def_stat_name = get_defensive_stat_name(move_type, gen, move_category)

    atk_stat = attacker_stats[atk_stat_name]
    def_stat = defender_stats[def_stat_name]

    stab = move_type in attacker_types
    effectiveness = get_type_effectiveness(move_type, defender_types, type_chart)

    min_dmg, max_dmg = calc_damage(
        level, power, atk_stat, def_stat, gen, stab, move_type, defender_types, type_chart
    )

    hp = defender_stats["hp"]
    min_pct = min_dmg / hp * 100 if hp > 0 else 0
    max_pct = max_dmg / hp * 100 if hp > 0 else 0

    return {
        "move": move["name"],
        "type": move_type,
        "category": move_category if gen >= 4 else ("Physical" if move_type in PHYSICAL_TYPES else "Special"),
        "power": power,
        "min_damage": min_dmg,
        "max_damage": max_dmg,
        "min_pct": min_pct,
        "max_pct": max_pct,
        "effectiveness": effectiveness,
    }


def compute_stats(base_stats: list[dict], level: int, gen: int) -> dict[str, int]:
    stats = {}
    for stat in base_stats:
        name = stat["name"]
        base = stat["value"]
        is_hp = name == "hp"
        stats[name] = calc_stat(base, level, is_hp, gen)
    return stats
