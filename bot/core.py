"""
Core bot functionality for PokéBot
"""
from discord.ext import commands

# Global state for the bot
VERSION_MAP = {}
SESSION_MAP = {}

def create_bot(config):
    """Create and configure the bot instance"""
    bot = commands.Bot(command_prefix=config.get('prefix', '!'))
    
    # Register the on_ready event
    @bot.event
    async def on_ready():
        print(f'{bot.user} has connected to Discord')
    
    # Register on_message event to handle Pokemon sessions
    @bot.event
    async def on_message(message):
        if str(message.author.id) in SESSION_MAP and len(message.content.strip().split(" ")) == 1:
            from bot.commands import process_pokemon_message
            await process_pokemon_message(bot, message, SESSION_MAP, VERSION_MAP)
        
        # Make sure we process commands
        await bot.process_commands(message)
    
    # Import and add all commands
    from bot.commands import register_commands
    register_commands(bot)
    
    return bot

def run_bot(bot, token):
    """Run the bot with the provided token"""
    bot.run(token)