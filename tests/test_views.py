import pytest
from unittest.mock import AsyncMock, MagicMock, patch
import discord

from bot.views import MovesView, MOVES_PER_PAGE


@pytest.fixture
def sample_moves():
    return [
        {"level": i, "name": f"move-{i}", "type": "normal", "category": "physical", "power": 40, "accuracy": 100, "pp": 35}
        for i in range(1, 31)
    ]


class TestMovesView:
    def test_initialization(self, sample_moves):
        view = MovesView(sample_moves, "pikachu", "red", ["electric"])
        assert view.page == 1
        assert view.total_pages == 2

    def test_total_pages_calculation(self):
        moves_20 = [{"level": i, "name": f"m{i}", "type": "n", "category": "p", "power": 1, "accuracy": 1, "pp": 1} for i in range(20)]
        view = MovesView(moves_20, "pikachu", "red", ["electric"])
        assert view.total_pages == 2

    def test_single_page(self):
        moves_5 = [{"level": i, "name": f"m{i}", "type": "n", "category": "p", "power": 1, "accuracy": 1, "pp": 1} for i in range(5)]
        view = MovesView(moves_5, "pikachu", "red", ["electric"])
        assert view.total_pages == 1

    def test_get_page_moves_first_page(self, sample_moves):
        view = MovesView(sample_moves, "pikachu", "red", ["electric"])
        page_moves = view.get_page_moves()
        assert len(page_moves) == MOVES_PER_PAGE
        assert page_moves[0]["level"] == 1

    def test_get_page_moves_second_page(self, sample_moves):
        view = MovesView(sample_moves, "pikachu", "red", ["electric"])
        view.page = 2
        page_moves = view.get_page_moves()
        assert len(page_moves) == 15
        assert page_moves[0]["level"] == 16

    def test_get_embed_returns_embed(self, sample_moves):
        view = MovesView(sample_moves, "pikachu", "red", ["electric"])
        embed = view.get_embed()
        assert isinstance(embed, discord.Embed)

    def test_buttons_disabled_on_first_page(self, sample_moves):
        view = MovesView(sample_moves, "pikachu", "red", ["electric"])
        assert view.prev_button.disabled is True
        assert view.next_button.disabled is False

    def test_buttons_disabled_on_last_page(self, sample_moves):
        view = MovesView(sample_moves, "pikachu", "red", ["electric"])
        view.page = view.total_pages
        view._update_buttons()
        assert view.prev_button.disabled is False
        assert view.next_button.disabled is True
