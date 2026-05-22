import discord
from discord.ext import commands
from discord import app_commands

from bot.helpers import resolve_pokemon, get_species_name, pokemon_matcher, send_response
from data.catch import calculate_catch_rate, ALL_BALLS
from data.constants import TYPE_COLOR_MAP

VALID_STATUSES = ["none", "sleep", "freeze", "paralysis", "burn", "poison"]

BALL_DISPLAY = {
    "poke": "Poké Ball", "great": "Great Ball", "ultra": "Ultra Ball",
    "master": "Master Ball", "net": "Net Ball", "nest": "Nest Ball",
    "repeat": "Repeat Ball", "timer": "Timer Ball", "dive": "Dive Ball",
    "dusk": "Dusk Ball", "quick": "Quick Ball", "luxury": "Luxury Ball",
    "premier": "Premier Ball", "heal": "Heal Ball", "level": "Level Ball",
    "lure": "Lure Ball", "moon": "Moon Ball", "love": "Love Ball",
    "fast": "Fast Ball", "heavy": "Heavy Ball", "friend": "Friend Ball",
    "sport": "Sport Ball", "safari": "Safari Ball", "dream": "Dream Ball",
    "beast": "Beast Ball",
}

CONDITION_DESCRIPTIONS = {
    "night": "Night time / dark area",
    "cave": "Inside a cave",
    "water": "Bug or Water-type target / surfing",
    "fishing": "While fishing",
    "first_turn": "First turn of battle",
    "registered": "Already caught this species",
    "moon_stone": "Target evolves with Moon Stone",
    "opposite_gender": "Opposite gender to your Pokemon",
    "fast_pokemon": "Target has base Speed ≥ 100",
    "ultra_beast": "Target is an Ultra Beast",
    "sleep": "Target is sleeping (for Dream Ball)",
    "bug": "Target is Bug-type",
}


class CatchCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    async def _pokemon_autocomplete(self, interaction: discord.Interaction, current: str) -> list[app_commands.Choice[str]]:
        if not current:
            return []
        matches = pokemon_matcher.find_multiple_matches(current, threshold=0.4, max_results=10)
        return [app_commands.Choice(name=m[0], value=m[0].lower()) for m in matches]

    async def _ball_autocomplete(self, interaction: discord.Interaction, current: str) -> list[app_commands.Choice[str]]:
        if not current:
            return [app_commands.Choice(name=BALL_DISPLAY[b], value=b) for b in ["poke", "great", "ultra", "dusk", "quick", "net", "timer", "repeat", "nest", "dive"]]
        current_lower = current.lower()
        matches = [(k, v) for k, v in BALL_DISPLAY.items() if current_lower in k or current_lower in v.lower()]
        return [app_commands.Choice(name=v, value=k) for k, v in matches[:10]]

    async def _status_autocomplete(self, interaction: discord.Interaction, current: str) -> list[app_commands.Choice[str]]:
        return [app_commands.Choice(name=s.title(), value=s) for s in VALID_STATUSES if current.lower() in s]

    @app_commands.command(name="catch", description="Calculate catch probability for a Pokemon")
    @app_commands.describe(
        pokemon="Target Pokemon",
        gen="Generation (1-9)",
        ball="Ball type (default: poke)",
        hp="Target HP percentage 1-100 (default: 100)",
        status="Status condition (default: none)",
        level="Target's level (default: 50)",
        conditions="Conditions: night, cave, water, fishing, first_turn, registered, bug (comma-separated)",
    )
    @app_commands.autocomplete(pokemon=_pokemon_autocomplete, ball=_ball_autocomplete, status=_status_autocomplete)
    async def catch_slash(self, interaction: discord.Interaction, pokemon: str, gen: int, ball: str = "poke", hp: int = 100, status: str = "none", level: int = 50, conditions: str = ""):
        await interaction.response.defer()
        name = await resolve_pokemon(interaction, pokemon)
        if not name:
            return
        await self._show_catch(interaction, name, gen, ball, hp, status, level, conditions)

    @commands.command(name="catch")
    async def catch_prefix(self, ctx, pokemon: str, gen: str, ball: str = "poke", hp: str = "100", status: str = "none", level: str = "50", conditions: str = ""):
        """Calculate catch rate: !catch <pokemon> <gen> [ball] [hp%] [status] [level] [conditions]"""
        name = await resolve_pokemon(ctx, pokemon)
        if not name:
            return
        await self._show_catch(ctx, name, int(gen), ball, int(hp), status, int(level), conditions)

    async def _show_catch(self, destination, pokemon: str, gen: int, ball: str, hp: int, status: str, level: int, conditions_str: str):
        if gen < 1 or gen > 9:
            await _send(destination, "Generation must be between 1 and 9.")
            return
        if hp < 1 or hp > 100:
            await _send(destination, "HP must be between 1 and 100.")
            return
        if level < 1 or level > 100:
            await _send(destination, "Level must be between 1 and 100.")
            return
        if ball not in BALL_DISPLAY:
            await _send(destination, f"Unknown ball type. Options: {', '.join(ALL_BALLS)}")
            return
        if status not in VALID_STATUSES:
            await _send(destination, f"Unknown status. Options: {', '.join(VALID_STATUSES)}")
            return

        conditions = set()
        if conditions_str:
            conditions = {c.strip().lower() for c in conditions_str.split(",") if c.strip()}

        service = self.bot.poke_service
        species_name = get_species_name(pokemon)

        poke_data = await service.get_pokemon_data(pokemon)
        species_data = await service.get_species_data(species_name)
        types = await service.get_types(poke_data, gen)

        base_catch_rate = int(species_data["capture_rate"])

        # Auto-detect type-based conditions
        if "water" in types:
            conditions.add("water")
        if "bug" in types:
            conditions.add("bug")

        # Calculate probability for the specified ball
        prob = calculate_catch_rate(base_catch_rate, float(hp), ball, status, gen, level, conditions)

        # Calculate comparison probabilities
        comparison_balls = ["poke", "great", "ultra"]
        if ball not in comparison_balls:
            comparison_balls.append(ball)
        comparison_balls = list(dict.fromkeys(comparison_balls))

        comparisons = {}
        for b in comparison_balls:
            comparisons[b] = calculate_catch_rate(base_catch_rate, float(hp), b, status, gen, level, conditions)

        embed = self._build_embed(pokemon, types, gen, ball, hp, status, level, conditions, base_catch_rate, prob, comparisons)
        await _send(destination, embed=embed)

    def _build_embed(self, pokemon: str, types: list[str], gen: int, ball: str, hp: int, status: str, level: int, conditions: set, base_rate: int, prob: float, comparisons: dict) -> discord.Embed:
        color = TYPE_COLOR_MAP.get(types[0], 0x808080)

        embed = discord.Embed(
            title=f"Catch Rate — {pokemon.title()}",
            description=f"Gen {gen} | Lv{level} | {hp}% HP | {status.title()} | {BALL_DISPLAY[ball]}",
            color=color,
        )

        # Main result
        pct = prob * 100
        avg_attempts = 1 / prob if prob > 0 else float('inf')

        if prob >= 1.0:
            result_str = "**Guaranteed capture!**"
        else:
            result_str = f"**{pct:.1f}%** chance per throw\n~**{avg_attempts:.1f}** throws on average"

        embed.add_field(name=f"🎯 {BALL_DISPLAY[ball]}", value=result_str, inline=False)

        # Comparison table
        lines = []
        for b, p in comparisons.items():
            marker = " ◀" if b == ball else ""
            if p >= 1.0:
                lines.append(f"`{BALL_DISPLAY[b]:<14}` 100.0% (guaranteed){marker}")
            else:
                avg = 1 / p if p > 0 else 9999
                lines.append(f"`{BALL_DISPLAY[b]:<14}` {p*100:>5.1f}% (~{avg:.0f} throws){marker}")

        embed.add_field(name="📊 Comparison", value="\n".join(lines), inline=False)

        # Conditions footer
        cond_parts = [f"Base rate: {base_rate}/255"]
        if conditions:
            cond_parts.append(f"Active: {', '.join(sorted(conditions))}")
        embed.set_footer(text=" | ".join(cond_parts))

        return embed


_send = send_response
