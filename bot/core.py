import aiohttp
import discord
from discord.ext import commands

from data.api import PokeAPIClient
from data.cache import PokeCache
from data.service import PokeDataService
from bot.helpers import resolve_pokemon, get_species_name
from bot.embeds import create_basic_embed, create_damage_relations_embed, create_stats_embed
from utils.image_utils import create_type_image


class PokeBot(commands.Bot):
    def __init__(self, config: dict):
        intents = discord.Intents.default()
        intents.message_content = True

        super().__init__(
            command_prefix=config.get("prefix", "!"),
            intents=intents,
        )
        self.config = config
        self.http_session: aiohttp.ClientSession = None
        self.poke_client: PokeAPIClient = None
        self.cache: PokeCache = None
        self.poke_service: PokeDataService = None
        self.version_map: dict = {}
        self.session_map: dict = {}

    async def setup_hook(self):
        self.http_session = aiohttp.ClientSession()
        self.poke_client = PokeAPIClient(self.http_session)
        self.cache = PokeCache(persist_path=self.config.get("session_persist_path"))
        self.poke_service = PokeDataService(self.poke_client, self.cache)

        self.version_map, self.session_map = self.cache.load_sessions()

        print("Warming growth rate cache...")
        await self.cache.warm_growth_rates(self.poke_client)
        print("Growth rate cache ready.")

        from bot.commands import setup_commands
        await setup_commands(self)

    async def on_ready(self):
        print(f"{self.user} has connected to Discord")
        try:
            synced = await self.tree.sync()
            print(f"Synced {len(synced)} slash commands.")
        except Exception as e:
            print(f"Failed to sync commands: {e}")

    async def on_message(self, message: discord.Message):
        if message.author.bot:
            return

        user_id = str(message.author.id)
        session_channel = self.config.get("session_channel_id")

        if (
            user_id in self.session_map
            and len(message.content.strip().split()) == 1
            and not message.content.strip().startswith(self.command_prefix)
            and (session_channel is None or message.channel.id == session_channel)
        ):
            await self._handle_session_message(message)

        await self.process_commands(message)

    async def _handle_session_message(self, message: discord.Message):
        user_id = str(message.author.id)
        game = self.session_map[user_id]
        gen = PokeDataService.find_game_version(game)

        if gen is None:
            await message.channel.send("Your session game is not valid. Use `!session <game>` to start a new one.")
            return

        name = await resolve_pokemon(message.channel, message.content.strip())
        if not name:
            return

        service = self.poke_service
        species_name = get_species_name(name)

        try:
            poke_data = await service.get_pokemon_data(name)
            species_data = await service.get_species_data(species_name)
            first_gen = service.get_first_gen(species_data)

            if gen < first_gen:
                await message.channel.send(f"{name.title()} does not exist in Generation {gen}.")
                return

            types = await service.get_types(poke_data, gen)
            dex_num = str(poke_data["id"]).zfill(3)
            genus = service.get_genus(species_data)
            description = service.get_description(species_data, gen)
            growth_rate = service.get_growth_rate(species_name)
            sprite_url = poke_data["sprites"]["front_default"] or ""

            basic_embed = create_basic_embed(
                name, dex_num, genus, description, types, gen, sprite_url, growth_rate
            )
            await message.channel.send(embed=basic_embed)

            damage_relations = await service.get_damage_relations(types)
            dr_embed = create_damage_relations_embed(damage_relations, types)
            file = create_type_image(types)
            dr_embed.set_thumbnail(url=f"attachment://{file.filename}")
            await message.channel.send(file=file, embed=dr_embed)

            stats = service.get_base_stats(poke_data)
            stats_embed = create_stats_embed(name, stats, types)
            await message.channel.send(embed=stats_embed)

        except Exception as e:
            await message.channel.send(f"Error fetching data: {e}")

    async def close(self):
        if self.http_session:
            await self.http_session.close()
        await super().close()


def create_bot(config: dict) -> PokeBot:
    return PokeBot(config)


def run_bot(bot: PokeBot, token: str):
    bot.run(token)
