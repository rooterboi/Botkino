"""Render bepul tarifida disk vaqtinchalik. Baza avtomatik admin chatiga yuboriladi,
pin qilinadi va qayta ishga tushganda o'sha pin qilingan fayldan tiklanadi."""
import asyncio
import logging
import os
import sqlite3
import tempfile
from aiogram.exceptions import TelegramAPIError, TelegramBadRequest, TelegramForbiddenError
from aiogram.types import FSInputFile
from config import ADMINS, BACKUP_HOURS, DB_PATH

log = logging.getLogger(__name__)
state = {"blocked": False}  # tiklash muvaffaqiyatsiz bo'lsa, eski zaxirani ustiga yozmaslik uchun


def primary():
    return min(ADMINS) if ADMINS else None


def valid_db(path):
    try:
        c = sqlite3.connect(path)
        c.execute("SELECT COUNT(*) FROM users").fetchone()
        c.close()
        return True
    except sqlite3.Error:
        return False


def _snapshot(dst):
    src, out = sqlite3.connect(DB_PATH), sqlite3.connect(dst)
    src.backup(out)
    src.close()
    out.close()


async def send_backup(bot):
    admin = primary()
    if not admin or state["blocked"] or not os.path.exists(DB_PATH):
        return False
    tmp = os.path.join(tempfile.gettempdir(), "kino_backup.db")
    try:
        await asyncio.to_thread(_snapshot, tmp)
        prev = None
        try:
            prev = (await bot.get_chat(admin)).pinned_message
        except TelegramAPIError:
            pass
        msg = await bot.send_document(admin, FSInputFile(tmp, filename="kino_backup.db"),
                                      caption="💾 Avto-zaxira (pin qilingan, o'chirmang)", disable_notification=True)
        await bot.pin_chat_message(admin, msg.message_id, disable_notification=True)
        if prev:
            try:
                await bot.delete_message(admin, prev.message_id)
            except TelegramAPIError:
                pass
        return True
    except Exception:
        log.exception("Zaxira xatosi")
        return False


async def restore_if_needed(bot):
    admin = primary()
    if not admin or os.path.exists(DB_PATH):
        return
    pm = None
    for _ in range(3):
        try:
            pm = (await bot.get_chat(admin)).pinned_message
            break
        except (TelegramBadRequest, TelegramForbiddenError):
            log.info("Admin chatida zaxira yo'q (admin botni /start qilmagan bo'lishi mumkin)")
            return
        except TelegramAPIError as ex:
            log.warning("get_chat xato: %s", ex)
            await asyncio.sleep(3)
    else:
        state["blocked"] = True
        return
    if not pm or not pm.document:
        log.info("Pin qilingan zaxira topilmadi — yangi baza yaratiladi")
        return
    tmp = DB_PATH + ".dl"
    try:
        await bot.download(pm.document.file_id, destination=tmp)
        if valid_db(tmp):
            os.replace(tmp, DB_PATH)
            log.info("✅ Baza zaxiradan tiklandi")
        else:
            raise ValueError("zaxira fayli yaroqsiz")
    except Exception:
        log.exception("Tiklash muvaffaqiyatsiz — zaxira bloklandi")
        state["blocked"] = True


async def backup_loop(bot):
    await asyncio.sleep(300)
    while True:
        await send_backup(bot)
        await asyncio.sleep(BACKUP_HOURS * 3600)
