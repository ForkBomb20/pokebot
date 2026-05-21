import discord

from bot.embeds import create_moves_embed

MOVES_PER_PAGE = 15


class MovesView(discord.ui.View):
    def __init__(self, moves: list[dict], pokemon: str, game: str, types: list[str], timeout: float = 120):
        super().__init__(timeout=timeout)
        self.moves = moves
        self.pokemon = pokemon
        self.game = game
        self.types = types
        self.page = 1
        self.total_pages = max(1, (len(moves) + MOVES_PER_PAGE - 1) // MOVES_PER_PAGE)
        self._update_buttons()

    def get_page_moves(self) -> list[dict]:
        start = (self.page - 1) * MOVES_PER_PAGE
        return self.moves[start:start + MOVES_PER_PAGE]

    def get_embed(self) -> discord.Embed:
        return create_moves_embed(
            self.get_page_moves(), self.pokemon, self.game,
            self.page, self.total_pages, self.types,
        )

    def _update_buttons(self):
        self.prev_button.disabled = self.page <= 1
        self.next_button.disabled = self.page >= self.total_pages

    @discord.ui.button(label="Previous", style=discord.ButtonStyle.secondary, emoji="◀")
    async def prev_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        self.page -= 1
        self._update_buttons()
        await interaction.response.edit_message(embed=self.get_embed(), view=self)

    @discord.ui.button(label="Next", style=discord.ButtonStyle.secondary, emoji="▶")
    async def next_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        self.page += 1
        self._update_buttons()
        await interaction.response.edit_message(embed=self.get_embed(), view=self)

    async def on_timeout(self):
        for item in self.children:
            item.disabled = True
