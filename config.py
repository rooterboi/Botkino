import hashlib
import os
from dotenv import load_dotenv

load_dotenv()
BOT_TOKEN = os.getenv("BOT_TOKEN", "")
ADMINS = {int(x) for x in os.getenv("ADMINS", "").replace(" ", "").split(",") if x.isdigit()}
DB_PATH = os.getenv("DB_PATH", "kino.db")
# Render RENDER_EXTERNAL_URL ni o'zi beradi -> webhook rejimi. Lokalda bo'sh -> polling.
BASE_URL = (os.getenv("WEBHOOK_URL") or os.getenv("RENDER_EXTERNAL_URL") or "").rstrip("/")
PORT = int(os.getenv("PORT", "10000"))
SECRET = hashlib.sha256(BOT_TOKEN.encode()).hexdigest()[:32]
BACKUP_HOURS = float(os.getenv("BACKUP_HOURS", "6"))
