import os
from dotenv import load_dotenv


def load_config() -> dict:
    load_dotenv()

    session_channel = os.getenv("SESSION_CHANNEL_ID")
    dev_guild = os.getenv("DEV_GUILD_ID")
    bot_channel = os.getenv("BOT_CHANNEL_ID")

    config = {
        "token": os.getenv("DISCORD_TOKEN"),
        "prefix": os.getenv("COMMAND_PREFIX", "!"),
        "assets_path": os.path.join(os.path.dirname(os.path.dirname(__file__)), "assets"),
        "session_channel_id": int(session_channel) if session_channel else None,
        "session_persist_path": os.getenv("SESSION_PERSIST_PATH", "data/sessions.json"),
        "dev_guild_id": int(dev_guild) if dev_guild else None,
        "bot_channel_id": int(bot_channel) if bot_channel else None,
    }

    return config
