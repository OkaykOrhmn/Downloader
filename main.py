import asyncio
import logging
import sys
from aiohttp import web
from aiogram import Dispatcher
from aiogram.webhook.aiohttp_server import SimpleRequestHandler, setup_application
from bot_instance import bot
from bot.handlers.user_handler import user_router
from bot.config import BotConfig

# Extend config with webhook settings
config = BotConfig(
    admin_ids=[1568352369, 23847983],
    welcome_message="Welcome to our Bot! 🤖",
    webhook_url="https://your-domain.com/webhook",  # Replace with your public URL
    webhook_port=8443,  # or 443, 80, etc.
)

def register_routers(dp: Dispatcher) -> None:
    dp.include_router(user_router)

async def on_startup(bot_instance):
    await bot_instance.set_webhook(config.webhook_url)

async def main() -> None:
    dp = Dispatcher()
    dp["config"] = config
    register_routers(dp)

    # Set webhook on startup
    await bot.set_webhook(config.webhook_url)

    # Create aiohttp web application
    app = web.Application()
    # Setup the webhook handler
    webhook_requests_handler = SimpleRequestHandler(
        dispatcher=dp,
        bot=bot,
    )
    webhook_requests_handler.register(app, path="/webhook")

    # Prepare the application (for shutdown cleanup)
    setup_application(app, dp, bot=bot)

    # Run aiohttp server on the specified port
    runner = web.AppRunner(app)
    await runner.setup()
    site = web.TCPSite(runner, host="0.0.0.0", port=config.webhook_port)
    await site.start()
    logging.info(f"Webhook server running on port {config.webhook_port}")

    # Keep the server running
    await asyncio.Event().wait()

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, stream=sys.stdout)
    asyncio.run(main())