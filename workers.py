import asyncio
import logging
import aiohttp
from aiogram.exceptions import TelegramAPIError
import db
from kb import B, ikb

log = logging.getLogger(__name__)


async def _notify(bot, uid, text, kb=None):
    try:
        await bot.send_message(uid, text, reply_markup=kb)
    except TelegramAPIError:
        pass
    await asyncio.sleep(0.05)


async def expiry_loop(bot):
    """Har soatda: tugashiga 3 kun qolganlarga eslatma, muddati tugaganlarni oddiyga o'tkazish."""
    while True:
        try:
            for uid in await db.expiring_users(3):
                await _notify(bot, uid, "⏰ Premium obunangiz 3 kundan kamroq vaqtda tugaydi. Uzaytirishni unutmang!",
                              ikb([B("💎 Uzaytirish", "prem")]))
                await db.mark_notified(uid)
            for uid in await db.expire_users():
                await _notify(bot, uid, "⌛ Premium obunangiz muddati tugadi. Qayta faollashtirish uchun:",
                              ikb([B("💎 Premium sotib olish", "prem")]))
        except Exception:
            log.exception("expiry_loop")
        await asyncio.sleep(3600)


async def keepalive_loop(base_url):
    """Render bepul tarifida 15 daqiqa trafik bo'lmasa uxlab qoladi — o'zimizga ping."""
    await asyncio.sleep(60)
    async with aiohttp.ClientSession(timeout=aiohttp.ClientTimeout(total=20)) as s:
        while True:
            try:
                await s.get(f"{base_url}/health")
            except Exception as ex:
                log.warning("keepalive: %s", ex)
            await asyncio.sleep(600)
