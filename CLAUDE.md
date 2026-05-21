# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

PokéBot is a Discord bot that provides Pokémon data (stats, types, moves, evolutions, damage relations) by querying the [PokéAPI](https://pokeapi.co/api/v2/). It supports generation-aware lookups (Gen I through Gen VIII) and includes fuzzy name matching for user input.

## Running the Bot

```bash
python -m pokebot
```

Requires a `.env` file with `DISCORD_TOKEN` set. The bot uses command prefix `!` by default (configurable via `COMMAND_PREFIX` env var).

## Dependencies

```bash
pip install -r requirements.txt
```

Dev dependencies (pytest, black, mypy) are declared in `pyproject.toml` under `[project.optional-dependencies]`:
```bash
pip install -e ".[dev]"
```

The project uses Python 3.10+ with a local virtualenv at `env/`.

## Architecture

**Entry point:** `__main__.py` → loads config → creates bot → runs bot.

**Core flow:**
- `bot/core.py` — Creates the discord.py `Bot` instance, manages global `VERSION_MAP` (user's default game) and `SESSION_MAP` (active session per user). Intercepts messages in the hardcoded channel to route them through session-based Pokémon lookup.
- `bot/commands.py` — All `!`-prefixed commands (`!learnset`, `!evolution`, `!data`, `!game`, `!session`). Contains the full Pokémon name list and the `PokemonFuzzyMatcher` instance. Builds Discord embeds with type images, damage tables, and move learnsets.
- `data/pokedata.py` — All PokeAPI interaction. Functions are `@lru_cache`-decorated. Handles version/generation mapping via `VERSIONS`, `VERSION_GROUPS`, and `VERSION_MAPPINGS` dicts. Key functions: `getPokemonData`, `getSpeciesData`, `getMoves`, `getDamageRelations`, `getEvolutions`.
- `config/config.py` — Loads `.env` via python-dotenv.
- `utils/fuzzy.py` — `PokemonFuzzyMatcher` class using Levenshtein distance for typo-tolerant Pokémon name lookup.
- `utils/image_utils.py` — Merges type panel GIFs into combined images for dual-type Pokémon. Outputs to `assets/generated/`.

**Assets:**
- `assets/type_panels/` — 18 GIF images (one per type) used as source for type badge images.
- `assets/generated/` — Runtime-generated combined type images (gitignored in practice, though currently untracked).

## Key Design Decisions

- Game versions map to PokeAPI "version groups" via `VERSION_MAPPINGS` in `data/pokedata.py`. Generation is determined by index position in the `VERSIONS` list (1-indexed).
- Sessions are channel-locked to a specific channel ID (`1236106872264724480` in `bot/core.py`). During a session, bare Pokémon names (single-word, no `!` prefix) trigger data lookup.
- Dual-type Pokémon damage relations are computed by multiplying individual type multipliers together.
- The `POKEMON` list in `commands.py` covers Gen I–VIII (through Enamorus) and includes alternate forms (e.g., `Deoxys-attack`, `Giratina-origin`).
