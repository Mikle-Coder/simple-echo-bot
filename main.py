import logging
import sys
from aiohttp import web
import asyncio
from aiogram import Bot, Dispatcher, Router, types, enums
from aiogram.filters import CommandStart
from aiogram.types import Message
from aiogram.utils.markdown import hbold
from aiogram.webhook.aiohttp_server import SimpleRequestHandler, setup_application

from os import getenv
from dotenv import load_dotenv


load_dotenv()
BOT_TOKEN = getenv("BOT_TOKEN")
WEB_SERVER_HOST = getenv("WEB_SERVER_HOST")
WEB_SERVER_PORT = int(getenv("WEB_SERVER_PORT"))
WEBHOOK_PATH = getenv("WEBHOOK_PATH")
WEBHOOK_URL = getenv("WEBHOOK_URL")


router = Router()

@router.message(CommandStart())
async def command_start_handler(message: Message) -> None:
    logging.debug(f"Received command_start: {message}")
    await message.answer(f"Hello, {hbold(message.from_user.full_name)}!")


@router.message()
async def echo_handler(message: types.Message) -> None:
    logging.debug(f"Received message: {message}")
    try:
        await message.send_copy(chat_id=message.chat.id)
    except TypeError:
        await message.answer("Nice try!")


async def on_startup(bot: Bot) -> None:
    logging.info("Bot has been started")
    await bot.set_webhook(f"{WEBHOOK_URL}{WEBHOOK_PATH}")
    logging.info("Webhook has been set up")

async def on_shutdown(bot: Bot) -> None:
    logging.warning("Bot is being shut down...")
    await bot.delete_webhook()

async def main() -> None:
    bot = Bot(token=BOT_TOKEN, parse_mode=enums.ParseMode.HTML)
    dp = Dispatcher()
    dp.include_router(router)

    dp.startup.register(on_startup)
    dp.shutdown.register(on_shutdown)

    app = web.Application()

    webhook_requests_handler = SimpleRequestHandler(
        dispatcher=dp,
        bot=bot,
    )

    webhook_requests_handler.register(app, path=WEBHOOK_PATH)
    setup_application(app, dp, bot=bot)

    await web._run_app(app, host=WEB_SERVER_HOST, port=WEB_SERVER_PORT)


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, stream=sys.stdout)
    logging.getLogger('aiogram').setLevel(logging.DEBUG)
    asyncio.run(main())
