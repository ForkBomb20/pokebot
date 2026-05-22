# PokéBot Commands

All commands support slash (`/`) and prefix (`!`). Pokemon names have fuzzy matching and autocomplete.

## Pokemon Info

**`/data <pokemon> <gen>`** — Full overview (info, type chart, stats) for a specific generation
**`/stats <pokemon>`** — Base stat bar chart
**`/abilities <pokemon>`** — Abilities with descriptions (hidden marked)
**`/evolution <pokemon>`** — Evolution chain with conditions
**`/learnset <pokemon> <game>`** — Level-up moves for a game version (paginated)

## Damage Calculator

**`/calc <attacker> <defender> <gen> [atk_level] [def_level] [move]`**
Calculates damage from attacker to defender. Blank set (31 IVs, 0 EVs, neutral). Shows all damaging moves sorted by damage, or one specific move.

**`/matchup <pokemon1> <pokemon2> <gen> [level1] [level2] [move1] [move2]`**
Full head-to-head — both sides' moves against each other.

Levels default to 50. Respects gen-accurate mechanics (physical/special split, stat formulas, STAB, type effectiveness).

Icons: ✨ super effective | 💥 4x | 🛡️ resisted | ⛔ immune

## Sessions

**`/session <game>`** — Start a session; just type a Pokemon name to see its data
**`/game <game>`** — Set your default game version for `/learnset`
**`/endsession`** — End your session

## Game Versions
red, blue, yellow, gold, silver, crystal, ruby, sapphire, emerald, firered, leafgreen, diamond, pearl, platinum, heartgold, soulsilver, black, white, black2, white2, x, y, omega-ruby, alpha-sapphire, sun, moon, ultra-sun, ultra-moon, sword, shield, scarlet, violet
