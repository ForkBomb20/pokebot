import asyncio
import aiohttp

BASE_URL = "https://pokeapi.co/api/v2"


class PokeAPIClient:
    def __init__(self, session: aiohttp.ClientSession, max_concurrent: int = 10):
        self._session = session
        self._semaphore = asyncio.Semaphore(max_concurrent)

    async def _get(self, url: str) -> dict:
        async with self._semaphore:
            async with self._session.get(url) as resp:
                resp.raise_for_status()
                return await resp.json()

    async def get_pokemon(self, name: str) -> dict:
        name = name.strip().lower()
        return await self._get(f"{BASE_URL}/pokemon/{name}/")

    async def get_species(self, name: str) -> dict:
        name = name.strip().lower()
        return await self._get(f"{BASE_URL}/pokemon-species/{name}/")

    async def get_move(self, url: str) -> dict:
        return await self._get(url)

    async def get_move_by_name(self, name: str) -> dict:
        name = name.strip().lower()
        return await self._get(f"{BASE_URL}/move/{name}/")

    async def get_type(self, name: str) -> dict:
        name = name.strip().lower()
        return await self._get(f"{BASE_URL}/type/{name}/")

    async def get_evolution_chain(self, url: str) -> dict:
        return await self._get(url)

    async def get_growth_rate(self, rate_id: int) -> dict:
        return await self._get(f"{BASE_URL}/growth-rate/{rate_id}/")

    async def get_ability(self, url: str) -> dict:
        return await self._get(url)
