from typing import Optional
import discord

from utils.fuzzy import PokemonFuzzyMatcher
from data.constants import POKEMON

pokemon_matcher = PokemonFuzzyMatcher(POKEMON)


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


async def _send(destination, content: str):
    """Send a message to either an Interaction, Context, or channel."""
    if isinstance(destination, discord.Interaction):
        if destination.response.is_done():
            await destination.followup.send(content)
        else:
            await destination.response.send_message(content)
    elif hasattr(destination, "send"):
        await destination.send(content)
