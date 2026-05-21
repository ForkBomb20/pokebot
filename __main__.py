from bot.core import create_bot, run_bot
from config.config import load_config


def main():
    config = load_config()
    bot = create_bot(config)
    run_bot(bot, config.get("token"))


if __name__ == "__main__":
    main()
