import asyncio
import logging
import signal
from aiohttp import web
from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.types import ErrorEvent
from aiogram.webhook.aiohttp_server import SimpleRequestHandler, setup_application

import backup
import db
import workers
from config import ADMINS, BASE_URL, BOT_TOKEN, PORT, SECRET
from handlers import admin, user
from middlewares import Throttle

PATH = "/webhook"


async def on_error(event: ErrorEvent):
    logging.error("Handler xatosi: %s", event.exception, exc_info=event.exception)
    return True


async def health(_):
    return web.Response(text="ok")


async def run_webhook(bot, dp):
    app = web.Application()
    app.router.add_get("/", health)
    app.router.add_get("/health", health)
    SimpleRequestHandler(dispatcher=dp, bot=bot, secret_token=SECRET).register(app, path=PATH)
    setup_application(app, dp, bot=bot)
    runner = web.AppRunner(app)
    await runner.setup()
    await web.TCPSite(runner, "0.0.0.0", PORT).start()  # port avval ochiladi (Render talabi)
    await bot.set_webhook(BASE_URL + PATH, secret_token=SECRET, allowed_updates=dp.resolve_used_update_types())
    logging.info("Webhook: %s", BASE_URL + PATH)
    stop = asyncio.Event()
    loop = asyncio.get_running_loop()
    for sig in (signal.SIGINT, signal.SIGTERM):
        try:
            loop.add_signal_handler(sig, stop.set)
        except NotImplementedError:
            pass
    await stop.wait()
    await runner.cleanup()


async def main():
    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(name)s: %(message)s")
    if not BOT_TOKEN:
        raise SystemExit("BOT_TOKEN topilmadi")
    if not ADMINS:
        logging.warning("ADMINS bo'sh — admin panel ishlamaydi!")
    bot = Bot(BOT_TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML))
    await backup.restore_if_needed(bot)
    await db.init_db()
    dp = Dispatcher(storage=MemoryStorage())
    dp.message.outer_middleware(Throttle())
    dp.callback_query.outer_middleware(Throttle())
    dp.include_router(admin.router)
    dp.include_router(user.router)
    dp.errors.register(on_error)
    tasks = [asyncio.create_task(workers.expiry_loop(bot)), asyncio.create_task(backup.backup_loop(bot))]
    try:
        if BASE_URL:
            tasks.append(asyncio.create_task(workers.keepalive_loop(BASE_URL)))
            await run_webhook(bot, dp)
        else:
            await bot.delete_webhook(drop_pending_updates=True)
            await dp.start_polling(bot)
    finally:
        for t in tasks:
            t.cancel()
        await backup.send_backup(bot)  # o'chishdan oldin oxirgi zaxira
        await bot.session.close()


if __name__ == "__main__":
    asyncio.run(main())
