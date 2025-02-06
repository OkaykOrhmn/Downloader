import asyncio
import logging
import sys
from aiogram import Dispatcher
from bot_instance import bot
from bot.handlers.user_handler import user_router
from bot.config import BotConfig


def register_routers(dp: Dispatcher) -> None:
    """Register all routers in the application."""

    dp.include_router(user_router)


async def main() -> None:
    """Main function of the bot application."""
    config = BotConfig(
        admin_ids=[1568352369, 23847983], welcome_message="Welcome to our Bot! 🤖"
    )
    # Initialize Bot instance with default bot properties which will be passed to all API calls
    dp = Dispatcher()
    dp["config"] = config

    register_routers(dp)

    # And the run events dispatching
    await dp.start_polling(bot)


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, stream=sys.stdout)
    asyncio.run(main())
