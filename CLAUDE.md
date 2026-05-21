# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

PokéBot is a Discord bot that provides Pokémon data (stats, types, moves, evolutions, abilities, damage relations) by querying the [PokéAPI](https://pokeapi.co/api/v2/). Supports Gen I through Gen IX with generation-aware lookups, slash commands with autocomplete, and fuzzy name matching.

## Running the Bot

```bash
python -m pokebot
```

Requires a `.env` file with:
- `DISCORD_TOKEN` (required)
- `COMMAND_PREFIX` (default: `!`)
- `SESSION_CHANNEL_ID` (optional, restricts session mode to one channel)
- `SESSION_PERSIST_PATH` (default: `data/sessions.json`)

## Commands

```
pytest                          # Run all tests
pytest tests/test_service.py    # Run a single test module
pytest -k "test_fuzzy"          # Run tests matching pattern
```

## Dependencies

```bash
pip install -r requirements.txt          # Runtime
pip install -e ".[dev]"                   # Dev (pytest, pytest-asyncio, aioresponses)
```

Requires Python 3.10+. Uses discord.py 2.x with slash commands and aiohttp for async API calls.

## Architecture

```
bot/
  core.py              # PokeBot class, setup_hook lifecycle, session message handler
  commands/            # Cog-based command modules (slash + prefix)
    data.py            # /data - Pokemon info embed
    learnset.py        # /learnset - paginated move tables
    evolution.py       # /evolution - evolution chain display
    session.py         # /session, /game, /endsession
    stats.py           # /stats - base stat bars
    abilities.py       # /abilities - ability descriptions
  helpers.py           # resolve_pokemon (shared fuzzy match + messaging)
  embeds.py            # All embed builders (stats bars, type effectiveness, etc.)
  views.py             # MovesView pagination with Previous/Next buttons
data/
  constants.py         # VERSIONS, TYPE_COLOR_MAP, POKEMON list, GENERATIONS, etc.
  api.py               # PokeAPIClient - async aiohttp wrapper with semaphore
  cache.py             # PokeCache - in-memory cache + session JSON persistence
  service.py           # PokeDataService - orchestration, asyncio.gather for parallel fetches
config/
  config.py            # Loads .env via python-dotenv
utils/
  fuzzy.py             # PokemonFuzzyMatcher (Levenshtein distance)
  image_utils.py       # Type panel image merging
```

## Key Design Decisions

- **Async all the way**: `aiohttp.ClientSession` created in `setup_hook()`, shared across all requests. `asyncio.gather` parallelizes move detail fetches (biggest latency win).
- **Growth rate cache**: Warmed at startup (6 API calls once) so individual Pokemon lookups never hit growth rate endpoints.
- **Cog + slash commands**: Each command module is a Cog with both `@commands.command()` (prefix) and `@app_commands.command()` (slash). Autocomplete uses the fuzzy matcher.
- **PokeDataService**: Single orchestration layer — Cogs never call the API directly. Handles caching, species name extraction, type resolution.
- **Session persistence**: `version_map` and `session_map` saved to JSON on every mutation, loaded at startup.
- **Pagination**: Move lists > 15 entries use `discord.ui.View` with Previous/Next buttons.
- **`resolve_pokemon` helper**: All commands use the same fuzzy match flow (match → correction message → lowercase name). Eliminates duplication.
- **Generation awareness**: `past_types` used to show correct typing for older gens (e.g., Magnemite pure Electric in Gen I). `get_first_gen` prevents showing Pokemon in games where they don't exist.
