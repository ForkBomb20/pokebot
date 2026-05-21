import discord

from data.constants import TYPE_COLOR_MAP
from data.service import PokeDataService


STAT_DISPLAY_NAMES = {
    "hp": "HP",
    "attack": "ATK",
    "defense": "DEF",
    "special-attack": "SP.ATK",
    "special-defense": "SP.DEF",
    "speed": "SPD",
}

MAX_STAT = 255
BAR_LENGTH = 16


def get_type_color(types: list[str]) -> int:
    return TYPE_COLOR_MAP.get(types[0], 0x808080)


def create_basic_embed(
    pokemon: str,
    dex_num: str,
    genus: str,
    description: str,
    types: list[str],
    gen: int,
    sprite_url: str,
    growth_rate: str,
) -> discord.Embed:
    color = get_type_color(types)
    embed = discord.Embed(
        title=f"{pokemon.title()} #{dex_num}",
        url=PokeDataService.serebii_url(gen, dex_num),
        description=f"**{genus}**\n{description}",
        color=color,
    )
    type_str = " / ".join(t.title() for t in types)
    embed.add_field(name="Type", value=type_str, inline=True)
    embed.add_field(name="Growth Rate", value=growth_rate, inline=True)
    embed.set_thumbnail(url=sprite_url)
    embed.set_footer(text=f"Generation {gen}")
    return embed


def create_stats_embed(pokemon: str, stats: list[dict], types: list[str]) -> discord.Embed:
    color = get_type_color(types)
    lines = []
    total = 0
    for stat in stats:
        name = STAT_DISPLAY_NAMES.get(stat["name"], stat["name"].upper())
        value = stat["value"]
        total += value
        filled = round(value / MAX_STAT * BAR_LENGTH)
        bar = "█" * filled + "░" * (BAR_LENGTH - filled)
        lines.append(f"`{name:<7} {bar} {value:>3}`")

    lines.append(f"`{'TOTAL':<7} {'':>{BAR_LENGTH}} {total:>3}`")

    embed = discord.Embed(
        title=f"{pokemon.title()} - Base Stats",
        description="\n".join(lines),
        color=color,
    )
    return embed


def create_damage_relations_embed(damage_relations: dict[str, float], types: list[str]) -> discord.Embed:
    color = get_type_color(types)

    weak_to = []
    resist = []
    immune = []
    for t, mult in sorted(damage_relations.items()):
        display = f"{t.title()}"
        if mult == 0:
            immune.append(display)
        elif mult > 1:
            weak_to.append(f"{display} ({mult}x)")
        elif mult < 1:
            resist.append(f"{display} ({mult}x)")

    embed = discord.Embed(title="Type Effectiveness", color=color)
    if weak_to:
        embed.add_field(name="Weak To", value="\n".join(weak_to), inline=True)
    if resist:
        embed.add_field(name="Resists", value="\n".join(resist), inline=True)
    if immune:
        embed.add_field(name="Immune To", value="\n".join(immune), inline=True)

    type_str = " / ".join(t.title() for t in types)
    embed.set_footer(text=type_str)
    return embed


def create_evolution_embed(
    names: list[list[str]],
    conditions: list[list[dict]],
    types: list[str],
) -> discord.Embed:
    color = get_type_color(types)
    embed = discord.Embed(title="Evolution Chain", color=color)

    for i, chain in enumerate(names):
        path_parts = []
        for j, name in enumerate(chain):
            path_parts.append(f"**{name.title()}**")
            if j < len(chain) - 1:
                cond = conditions[i][j + 1]
                cond_str = _format_condition(cond)
                path_parts.append(f" --[{cond_str}]--> ")

        path_label = f"Path {i + 1}" if len(names) > 1 else "Evolution"
        embed.add_field(name=path_label, value="".join(path_parts), inline=False)

    return embed


def _format_condition(cond: dict) -> str:
    parts = []
    if "min_level" in cond:
        parts.append(f"Lv. {cond['min_level']}")
    if "min_happiness" in cond:
        parts.append(f"Happiness {cond['min_happiness']}")
    if "item" in cond and isinstance(cond["item"], dict):
        parts.append(cond["item"]["name"].replace("-", " ").title())
    if "held_item" in cond and isinstance(cond["held_item"], dict):
        parts.append(f"Hold {cond['held_item']['name'].replace('-', ' ').title()}")
    if "known_move" in cond and isinstance(cond["known_move"], dict):
        parts.append(f"Know {cond['known_move']['name'].replace('-', ' ').title()}")
    if "known_move_type" in cond and isinstance(cond["known_move_type"], dict):
        parts.append(f"Know {cond['known_move_type']['name'].title()} move")
    if "time_of_day" in cond and cond["time_of_day"]:
        parts.append(cond["time_of_day"].title())
    if "location" in cond and isinstance(cond["location"], dict):
        parts.append(cond["location"]["name"].replace("-", " ").title())
    if "trigger" in cond and isinstance(cond["trigger"], dict):
        trigger = cond["trigger"]["name"]
        if trigger == "trade" and not parts:
            parts.append("Trade")
        elif trigger == "use-item" and not any("Stone" in p or "item" in p.lower() for p in parts):
            pass
    if not parts:
        parts.append("Level Up")
    return ", ".join(parts)


def create_abilities_embed(pokemon: str, abilities: list[dict], types: list[str]) -> discord.Embed:
    color = get_type_color(types)
    embed = discord.Embed(title=f"{pokemon.title()} - Abilities", color=color)

    for ability in abilities:
        name = ability["name"]
        if ability["is_hidden"]:
            name += " (Hidden)"
        embed.add_field(
            name=name,
            value=ability["description"] or "No description available.",
            inline=False,
        )
    return embed


def create_moves_embed(moves: list[dict], pokemon: str, game: str, page: int, total_pages: int, types: list[str]) -> discord.Embed:
    color = get_type_color(types)
    embed = discord.Embed(
        title=f"{pokemon.title()} - Learnset ({game.title()})",
        color=color,
    )

    lines = []
    lines.append("`Lv  Move                Type         Cat      Pwr  Acc  PP`")
    lines.append("`" + "-" * 58 + "`")
    for move in moves:
        pwr = str(move["power"]) if move["power"] else "-"
        acc = str(move["accuracy"]) if move["accuracy"] else "-"
        line = (
            f"`{move['level']:<3} {move['name']:<20}"
            f"{move['type']:<13}{move['category']:<9}"
            f"{pwr:<5}{acc:<5}{move['pp']}`"
        )
        lines.append(line)

    embed.description = "\n".join(lines)
    if total_pages > 1:
        embed.set_footer(text=f"Page {page}/{total_pages} | Generation move data")
    else:
        embed.set_footer(text="Level-up moves")
    return embed
