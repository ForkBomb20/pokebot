import discord
from discord.ext import commands
from discord import app_commands

from data.service import PokeDataService


class SessionCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="game")
    async def game_prefix(self, ctx, game: str):
        """Set your default game version"""
        game = game.strip().lower()
        gen = PokeDataService.find_game_version(game)
        if gen is None:
            await ctx.send(f"'{game}' is not a recognized game version.")
            return
        self.bot.version_map[str(ctx.author.id)] = game
        self.bot.cache.save_sessions(self.bot.version_map, self.bot.session_map)
        await ctx.send(f"{ctx.author.name}'s game set to **{game.title()}** (Gen {gen}).")

    @app_commands.command(name="game", description="Set your default game version")
    @app_commands.describe(game="Game version (e.g. red, sword, scarlet)")
    async def game_slash(self, interaction: discord.Interaction, game: str):
        game = game.strip().lower()
        gen = PokeDataService.find_game_version(game)
        if gen is None:
            await interaction.response.send_message(f"'{game}' is not a recognized game version.")
            return
        self.bot.version_map[str(interaction.user.id)] = game
        self.bot.cache.save_sessions(self.bot.version_map, self.bot.session_map)
        await interaction.response.send_message(f"{interaction.user.name}'s game set to **{game.title()}** (Gen {gen}).")

    @commands.command(name="session")
    async def session_prefix(self, ctx, game: str):
        """Start a Pokemon session with a specific game version"""
        game = game.strip().lower()
        gen = PokeDataService.find_game_version(game)
        if gen is None:
            await ctx.send(f"'{game}' is not a recognized game version.")
            return
        self.bot.session_map[str(ctx.author.id)] = game
        self.bot.cache.save_sessions(self.bot.version_map, self.bot.session_map)
        await ctx.send(
            f"{ctx.author.name} started a **{game.title()}** session.\n"
            f"Type a Pokemon name to get its data. Use `!endsession` to stop."
        )

    @app_commands.command(name="session", description="Start a Pokemon lookup session for a game version")
    @app_commands.describe(game="Game version (e.g. red, sword, scarlet)")
    async def session_slash(self, interaction: discord.Interaction, game: str):
        game = game.strip().lower()
        gen = PokeDataService.find_game_version(game)
        if gen is None:
            await interaction.response.send_message(f"'{game}' is not a recognized game version.")
            return
        self.bot.session_map[str(interaction.user.id)] = game
        self.bot.cache.save_sessions(self.bot.version_map, self.bot.session_map)
        await interaction.response.send_message(
            f"{interaction.user.name} started a **{game.title()}** session.\n"
            f"Type a Pokemon name to get its data. Use `/endsession` to stop."
        )

    @commands.command(name="endsession")
    async def endsession_prefix(self, ctx):
        """End your current Pokemon session"""
        user_id = str(ctx.author.id)
        if user_id in self.bot.session_map:
            del self.bot.session_map[user_id]
            self.bot.cache.save_sessions(self.bot.version_map, self.bot.session_map)
            await ctx.send(f"{ctx.author.name}'s session has ended.")
        else:
            await ctx.send("You don't have an active session.")

    @app_commands.command(name="endsession", description="End your current Pokemon lookup session")
    async def endsession_slash(self, interaction: discord.Interaction):
        user_id = str(interaction.user.id)
        if user_id in self.bot.session_map:
            del self.bot.session_map[user_id]
            self.bot.cache.save_sessions(self.bot.version_map, self.bot.session_map)
            await interaction.response.send_message(f"{interaction.user.name}'s session has ended.")
        else:
            await interaction.response.send_message("You don't have an active session.")
