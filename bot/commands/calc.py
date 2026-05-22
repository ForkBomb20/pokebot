import asyncio
import discord
from discord.ext import commands
from discord import app_commands

from bot.helpers import resolve_pokemon, get_species_name, pokemon_matcher, move_autocomplete
from data.damage import (
    compute_stats,
    calculate_move_damage,
    GEN_DEFAULT_GAMES,
)
from data.constants import TYPE_COLOR_MAP, ALL_TYPES, GENERATIONS


class CalcCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self._type_data_cache: list[dict] | None = None
        self._gen_charts: dict[int, dict[tuple[str, str], float]] = {}

    async def _fetch_all_type_data(self) -> list[dict]:
        if self._type_data_cache is not None:
            return self._type_data_cache

        cache = self.bot.cache
        client = self.bot.poke_client

        async def fetch_type(t: str):
            cached = cache.get_type(t)
            if cached:
                return cached
            data = await client.get_type(t)
            cache.set_type(t, data)
            return data

        self._type_data_cache = await asyncio.gather(*[fetch_type(t) for t in ALL_TYPES])
        return self._type_data_cache

    async def _get_type_chart(self, gen: int) -> dict[tuple[str, str], float]:
        if gen in self._gen_charts:
            return self._gen_charts[gen]

        all_type_data = await self._fetch_all_type_data()
        gen_name = GENERATIONS[gen - 1]
        gen_index = gen - 1

        chart = {}
        for type_data in all_type_data:
            atk_type = type_data["name"]

            # Find the applicable damage relations for this gen
            # past_damage_relations entries apply to that gen and all prior
            dr = type_data["damage_relations"]
            for past in type_data.get("past_damage_relations", []):
                past_gen_name = past["generation"]["name"]
                past_gen_index = GENERATIONS.index(past_gen_name)
                if gen_index <= past_gen_index:
                    dr = past["damage_relations"]
                    break

            for t in dr.get("double_damage_to", []):
                chart[(atk_type, t["name"])] = 2.0
            for t in dr.get("half_damage_to", []):
                chart[(atk_type, t["name"])] = 0.5
            for t in dr.get("no_damage_to", []):
                chart[(atk_type, t["name"])] = 0.0

        self._gen_charts[gen] = chart
        return chart

    async def _pokemon_autocomplete(self, interaction: discord.Interaction, current: str) -> list[app_commands.Choice[str]]:
        if not current:
            return []
        matches = pokemon_matcher.find_multiple_matches(current, threshold=0.4, max_results=10)
        return [app_commands.Choice(name=m[0], value=m[0].lower()) for m in matches]

    async def _move_autocomplete(self, interaction: discord.Interaction, current: str) -> list[app_commands.Choice[str]]:
        return await move_autocomplete(self.bot, current)

    @app_commands.command(name="calc", description="Calculate damage from one Pokemon to another")
    @app_commands.describe(
        attacker="Attacking Pokemon",
        defender="Defending Pokemon",
        gen="Generation (1-9)",
        attacker_level="Attacker's level (default 50)",
        defender_level="Defender's level (default 50)",
        move="Specific move to calculate (optional, shows all if omitted)",
    )
    @app_commands.autocomplete(attacker=_pokemon_autocomplete, defender=_pokemon_autocomplete, move=_move_autocomplete)
    async def calc_slash(self, interaction: discord.Interaction, attacker: str, defender: str, gen: int, attacker_level: int = 50, defender_level: int = 50, move: str = ""):
        await interaction.response.defer()
        atk_name = await resolve_pokemon(interaction, attacker)
        if not atk_name:
            return
        def_name = await resolve_pokemon(interaction, defender)
        if not def_name:
            return
        await self._show_calc(interaction, atk_name, def_name, gen, attacker_level, defender_level, move.strip().lower() or None)

    @commands.command(name="calc")
    async def calc_prefix(self, ctx, attacker: str, defender: str, gen: str, attacker_level: str = "50", defender_level: str = "50", move: str = ""):
        """Calculate damage: !calc <attacker> <defender> <gen> [atk_level] [def_level] [move]"""
        atk_name = await resolve_pokemon(ctx, attacker)
        if not atk_name:
            return
        def_name = await resolve_pokemon(ctx, defender)
        if not def_name:
            return
        await self._show_calc(ctx, atk_name, def_name, int(gen), int(attacker_level), int(defender_level), move.strip().lower() or None)

    @app_commands.command(name="matchup", description="Show full matchup between two Pokemon (both sides)")
    @app_commands.describe(
        pokemon1="First Pokemon",
        pokemon2="Second Pokemon",
        gen="Generation (1-9)",
        level1="First Pokemon's level (default 50)",
        level2="Second Pokemon's level (default 50)",
        move1="Specific move for Pokemon 1 (optional)",
        move2="Specific move for Pokemon 2 (optional)",
    )
    @app_commands.autocomplete(pokemon1=_pokemon_autocomplete, pokemon2=_pokemon_autocomplete, move1=_move_autocomplete, move2=_move_autocomplete)
    async def matchup_slash(self, interaction: discord.Interaction, pokemon1: str, pokemon2: str, gen: int, level1: int = 50, level2: int = 50, move1: str = "", move2: str = ""):
        await interaction.response.defer()
        name1 = await resolve_pokemon(interaction, pokemon1)
        if not name1:
            return
        name2 = await resolve_pokemon(interaction, pokemon2)
        if not name2:
            return
        await self._show_matchup(interaction, name1, name2, gen, level1, level2, move1.strip().lower() or None, move2.strip().lower() or None)

    @commands.command(name="matchup")
    async def matchup_prefix(self, ctx, pokemon1: str, pokemon2: str, gen: str, level1: str = "50", level2: str = "50", move1: str = "", move2: str = ""):
        """Show full matchup: !matchup <pokemon1> <pokemon2> <gen> [level1] [level2] [move1] [move2]"""
        name1 = await resolve_pokemon(ctx, pokemon1)
        if not name1:
            return
        name2 = await resolve_pokemon(ctx, pokemon2)
        if not name2:
            return
        await self._show_matchup(ctx, name1, name2, int(gen), int(level1), int(level2), move1.strip().lower() or None, move2.strip().lower() or None)

    async def _fetch_move_by_name(self, name: str) -> dict | None:
        try:
            move_data = await self.bot.poke_client.get_move_by_name(name)
            return {
                "level": 0,
                "name": move_data["name"],
                "type": move_data["type"]["name"],
                "category": move_data["damage_class"]["name"],
                "power": move_data["power"],
                "accuracy": move_data["accuracy"],
                "pp": move_data["pp"],
            }
        except Exception:
            return None

    async def _fetch_pokemon_context(self, service, name: str, gen: int) -> tuple[dict, dict, list[str], int] | str:
        species_name = get_species_name(name)
        poke_data = await service.get_pokemon_data(name)
        species_data = await service.get_species_data(species_name)
        first_gen = service.get_first_gen(species_data)

        if gen < first_gen:
            return f"{name.title()} does not exist in Generation {gen}."

        types = await service.get_types(poke_data, gen)
        return poke_data, species_data, types, first_gen

    async def _show_calc(self, destination, attacker: str, defender: str, gen: int, atk_level: int, def_level: int, move_filter: str | None):
        if gen < 1 or gen > 9:
            await _send(destination, "Generation must be between 1 and 9.")
            return
        if not (1 <= atk_level <= 100) or not (1 <= def_level <= 100):
            await _send(destination, "Level must be between 1 and 100.")
            return

        service = self.bot.poke_service

        atk_ctx = await self._fetch_pokemon_context(service, attacker, gen)
        if isinstance(atk_ctx, str):
            await _send(destination, atk_ctx)
            return
        atk_data, _, atk_types, _ = atk_ctx

        def_ctx = await self._fetch_pokemon_context(service, defender, gen)
        if isinstance(def_ctx, str):
            await _send(destination, def_ctx)
            return
        def_data, _, def_types, _ = def_ctx

        if move_filter:
            move_data = await self._fetch_move_by_name(move_filter)
            if not move_data:
                await _send(destination, f"Move **{move_filter.replace('-', ' ').title()}** not found.")
                return
            if not move_data["power"]:
                await _send(destination, f"**{move_filter.replace('-', ' ').title()}** is a status move and deals no damage.")
                return
            available_moves = [move_data]
        else:
            game = GEN_DEFAULT_GAMES[gen]
            atk_moves_raw = await service.get_moves(atk_data, game)
            available_moves = [m for m in atk_moves_raw if m["level"] <= atk_level and m["power"]]

            if not available_moves:
                await _send(destination, f"{attacker.title()} has no damaging moves at level {atk_level} in Gen {gen}.")
                return

        atk_stats = compute_stats(service.get_base_stats(atk_data), atk_level, gen)
        def_stats = compute_stats(service.get_base_stats(def_data), def_level, gen)

        type_chart = await self._get_type_chart(gen)

        results = _calc_move_results(available_moves, atk_stats, def_stats, atk_types, def_types, atk_level, gen, type_chart)

        embed = self._build_embed(attacker, defender, atk_types, def_types, atk_level, def_level, gen, results, def_stats["hp"])
        await _send(destination, embed=embed)

    async def _show_matchup(self, destination, pokemon1: str, pokemon2: str, gen: int, level1: int, level2: int, move1_filter: str | None, move2_filter: str | None):
        if gen < 1 or gen > 9:
            await _send(destination, "Generation must be between 1 and 9.")
            return
        if not (1 <= level1 <= 100) or not (1 <= level2 <= 100):
            await _send(destination, "Level must be between 1 and 100.")
            return

        service = self.bot.poke_service

        ctx1 = await self._fetch_pokemon_context(service, pokemon1, gen)
        if isinstance(ctx1, str):
            await _send(destination, ctx1)
            return
        data1, _, types1, _ = ctx1

        ctx2 = await self._fetch_pokemon_context(service, pokemon2, gen)
        if isinstance(ctx2, str):
            await _send(destination, ctx2)
            return
        data2, _, types2, _ = ctx2

        if move1_filter:
            move1_data = await self._fetch_move_by_name(move1_filter)
            if not move1_data or not move1_data["power"]:
                moves1 = []
            else:
                moves1 = [move1_data]
        else:
            game = GEN_DEFAULT_GAMES[gen]
            moves1_raw = await service.get_moves(data1, game)
            moves1 = [m for m in moves1_raw if m["level"] <= level1 and m["power"]]

        if move2_filter:
            move2_data = await self._fetch_move_by_name(move2_filter)
            if not move2_data or not move2_data["power"]:
                moves2 = []
            else:
                moves2 = [move2_data]
        else:
            game = GEN_DEFAULT_GAMES[gen]
            moves2_raw = await service.get_moves(data2, game)
            moves2 = [m for m in moves2_raw if m["level"] <= level2 and m["power"]]

        stats1 = compute_stats(service.get_base_stats(data1), level1, gen)
        stats2 = compute_stats(service.get_base_stats(data2), level2, gen)

        type_chart = await self._get_type_chart(gen)

        results_1v2 = _calc_move_results(moves1, stats1, stats2, types1, types2, level1, gen, type_chart)
        results_2v1 = _calc_move_results(moves2, stats2, stats1, types2, types1, level2, gen, type_chart)

        embed = discord.Embed(
            title=f"{pokemon1.title()} vs {pokemon2.title()} — Full Matchup",
            description=f"Gen {gen} | Blank set (31 IVs, 0 EVs, neutral)",
            color=TYPE_COLOR_MAP.get(types1[0], 0x808080),
        )

        lines1 = _format_results(results_1v2)
        lines2 = _format_results(results_2v1)

        embed.add_field(
            name=f"⚔️ {pokemon1.title()} (Lv{level1}) → {pokemon2.title()} ({stats2['hp']} HP)",
            value=lines1 or "No damaging moves",
            inline=False,
        )
        embed.add_field(
            name=f"⚔️ {pokemon2.title()} (Lv{level2}) → {pokemon1.title()} ({stats1['hp']} HP)",
            value=lines2 or "No damaging moves",
            inline=False,
        )

        t1_str = "/".join(t.title() for t in types1)
        t2_str = "/".join(t.title() for t in types2)
        embed.set_footer(text=f"{t1_str} vs {t2_str}")
        await _send(destination, embed=embed)

    def _build_embed(
        self,
        attacker: str,
        defender: str,
        atk_types: list[str],
        def_types: list[str],
        atk_level: int,
        def_level: int,
        gen: int,
        results: list[dict],
        defender_hp: int,
    ) -> discord.Embed:
        color = TYPE_COLOR_MAP.get(atk_types[0], 0x808080)
        embed = discord.Embed(
            title=f"{attacker.title()} vs {defender.title()}",
            description=f"Gen {gen} | Lv{atk_level} → Lv{def_level} | Blank set (31 IVs, 0 EVs, neutral)",
            color=color,
        )

        lines = _format_results(results)

        embed.add_field(
            name=f"Damage to {defender.title()} ({defender_hp} HP)",
            value=lines or "No damaging moves",
            inline=False,
        )

        atk_type_str = "/".join(t.title() for t in atk_types)
        def_type_str = "/".join(t.title() for t in def_types)
        embed.set_footer(text=f"{atk_type_str} → {def_type_str}")

        return embed


def _calc_move_results(moves, atk_stats, def_stats, atk_types, def_types, level, gen, type_chart):
    results = []
    seen = set()
    for move in moves:
        if move["name"] in seen:
            continue
        seen.add(move["name"])
        r = calculate_move_damage(move, atk_stats, def_stats, atk_types, def_types, level, gen, type_chart)
        if r:
            results.append(r)
    results.sort(key=lambda x: x["max_damage"], reverse=True)
    return results


def _format_results(results: list[dict]) -> str:
    lines = []
    for r in results:
        eff_str = _effectiveness_str(r["effectiveness"])
        move_display = r["move"].replace("-", " ").title()
        lines.append(
            f"`{move_display:<20}` {eff_str} "
            f"**{r['min_damage']}-{r['max_damage']}** "
            f"({r['min_pct']:.1f}-{r['max_pct']:.1f}%)"
        )
    return "\n".join(lines)


def _effectiveness_str(eff: float) -> str:
    if eff == 0:
        return "⛔"
    elif eff >= 4:
        return "💥"
    elif eff >= 2:
        return "✨"
    elif eff <= 0.25:
        return "🛡️🛡️"
    elif eff <= 0.5:
        return "🛡️"
    return "▪️"


async def _send(destination, content=None, **kwargs):
    if isinstance(destination, discord.Interaction):
        await destination.followup.send(content, **kwargs)
    else:
        if content:
            await destination.send(content, **kwargs)
        else:
            await destination.send(**kwargs)
