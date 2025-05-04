"""
Main entry point for the PokéBot application
"""
from bot.core import create_bot, run_bot
from config.config import load_config

def main():
    """Main function to run the bot"""
    # Load environment variables and configuration
    config = load_config()
    print("Hello")
    
    # Create the bot instance
    bot = create_bot(config)
    
    # Run the bot
    run_bot(bot, config.get('token'))

if __name__ == "__main__":
    main()