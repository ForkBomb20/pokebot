"""
Configuration management for PokéBot
"""
import os
from dotenv import load_dotenv

def load_config():
    """Load configuration from environment variables"""
    # Load environment variables from .env file
    load_dotenv()
    
    # Create configuration dictionary
    config = {
        'token': os.getenv('DISCORD_TOKEN'),
        'prefix': os.getenv('COMMAND_PREFIX', '!'),
        'assets_path': os.path.join(os.path.dirname(os.path.dirname(__file__)), 'assets'),
    }
    
    return config