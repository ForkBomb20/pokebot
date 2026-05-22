from typing import Optional
import discord

from utils.fuzzy import PokemonFuzzyMatcher
from data.constants import POKEMON

pokemon_matcher = PokemonFuzzyMatcher(POKEMON)

_move_list_cache: list[str] | None = None


async def get_move_list(bot) -> list[str]:
    global _move_list_cache
    if _move_list_cache is not None:
        return _move_list_cache

    async with bot.http_session.get("https://pokeapi.co/api/v2/move?limit=1000") as resp:
        data = await resp.json()
        _move_list_cache = [m["name"] for m in data["results"]]
    return _move_list_cache


async def move_autocomplete(bot, current: str) -> list:
    from discord import app_commands
    if not current:
        return []
    moves = await get_move_list(bot)
    current_lower = current.lower().replace(" ", "-")
    matches = [m for m in moves if m.startswith(current_lower)]
    if len(matches) < 10:
        matches += [m for m in moves if current_lower in m and m not in matches]
    return [
        app_commands.Choice(name=m.replace("-", " ").title(), value=m)
        for m in matches[:10]
    ]


async def resolve_pokemon(
    destination,
    user_input: str,
    threshold: float = 0.7,
) -> Optional[str]:
    """
    Fuzzy-match user input to a Pokemon name.
    Sends correction/suggestion messages to the destination.
    Returns the lowercase Pokemon name, or None if no match found.

    destination: discord.Interaction, ctx, or message.channel
    """
    user_input = user_input.strip()
    matched = pokemon_matcher.find_best_match(user_input, threshold=threshold)

    if not matched:
        suggestions = pokemon_matcher.find_multiple_matches(user_input, threshold=0.4, max_results=3)
        if suggestions:
            suggestion_text = ", ".join([m[0] for m in suggestions])
            msg = f"Pokemon '{user_input}' not found. Did you mean: **{suggestion_text}**?"
        else:
            msg = f"Pokemon '{user_input}' not found. Please check your spelling."
        await _send(destination, msg)
        return None

    if matched.lower() != user_input.lower():
        await _send(destination, f"Showing data for **{matched}**:")

    return matched.lower()


def get_species_name(pokemon: str) -> str:
    """Extract the species name from a potentially hyphenated form name."""
    if "-" in pokemon:
        return pokemon.split("-")[0]
    return pokemon


async def send_response(destination, content=None, **kwargs):
    if isinstance(destination, discord.Interaction):
        if destination.response.is_done():
            await destination.followup.send(content, **kwargs)
        else:
            await destination.response.send_message(content, **kwargs)
    elif hasattr(destination, "send"):
        if content:
            await destination.send(content, **kwargs)
        else:
            await destination.send(**kwargs)


async def _send(destination, content: str):
    await send_response(destination, content)
