import sys
import os
import pytest
from unittest.mock import AsyncMock, MagicMock

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from data.api import PokeAPIClient
from data.cache import PokeCache
from data.service import PokeDataService


@pytest.fixture
def mock_client():
    client = MagicMock(spec=PokeAPIClient)
    client.get_pokemon = AsyncMock()
    client.get_species = AsyncMock()
    client.get_move = AsyncMock()
    client.get_type = AsyncMock()
    client.get_evolution_chain = AsyncMock()
    client.get_growth_rate = AsyncMock()
    client.get_ability = AsyncMock()
    return client


@pytest.fixture
def cache():
    return PokeCache()


@pytest.fixture
def service(mock_client, cache):
    return PokeDataService(mock_client, cache)
