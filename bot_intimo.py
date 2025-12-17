# ---------------- BOT PERSONALE — VERSIONE RICHIAMO ----------------
# IA naturale, UNA cartella foto
# Buongiorno / Buonanotte SEMPRE
# Foto su richiesta
# Foto progressive se non scrivi (richiamo)
# Nessun comportamento robotico

import os
import random
import json
from datetime import datetime, timedelta, time as dtime

from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    MessageHandler,
    filters,
)

from openai import OpenAI

# ======================================================
# CONFIG
# ======================================================

BOT_TOKEN = os.environ.get("BOT_TOKEN")
OWNER_ID = int(os.environ.get("OWNER_ID", "361555418"))
EXTRA_PASS = os.environ.get("EXTRA_PASS", "hailee_2025")

OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY")
AI_MODEL = os.environ.get("AI_MODEL", "gpt-4o")

client = OpenAI(api_key=OPENAI_API_KEY)

LAST_USER_MESSAGE = datetime.utcnow()
LAST_PHOTO_SENT = None

extra_unlocked = False
PRE_EXTRA_SHOWN = False

# ======================================================
# FOTO (UNA SOLA CARTELLA)
# ======================================================

PHOTOS_DIR = "photos_hailee"
USED_PHOTOS_FILE = "used_photos.json"

def pick_photo():
    if not os.path.isdir(PHOTOS_DIR):
        return None

    files = [f for f in os.listdir(PHOTOS_DIR) if not f.startswith(".")]
    if not files:
        return None

    try:
        used = json.load(open(USED_PHOTOS_FILE))
    except Exception:
        used = []

    available = [f for f in files if f not in used]
    if not available:
        available = files
        used = []

    choice = random.choice(available)
    used.append(choice)

    json.dump(used, open(USED_PHOTOS_FILE, "w"), indent=2)
    return os.path.join(PHOTOS_DIR, choice)

# ======================================================
# ORARI FISSI
# ======================================================

GOOD_MORNING_TIME = dtime(6, 30)
GOOD_NIGHT_TIME   = dtime(22, 30)

# ======================================================
# MEMORIA MINIMA
# ======================================================

MEMORY_FILE = "hailee_memory.json"

def load_memory():
    if not os.path.exists(MEMORY_FILE):
        return {"cronologia": []}
    try:
        return json.load(open(MEMORY_FILE))
    except Exception:
        return {"cronologia": []}

def save_memory(m):
    json.dump(m, open(MEMORY_FILE, "w"), indent=2, ensure_ascii=False)

# ======================================================
# IA (NON STRAVOLTA)
# ======================================================

AI_SYSTEM_PROMPT = (
    "Sei una persona reale, romantica, affettuosa e naturale. "
    "Parli come una persona vera, non come un bot. "
    "Usi frasi semplici. A volte fai domande spontanee. "
    "Non usare etichette o nomi."
)

async def generate_ai_reply(user_text: str) -> str:
    memory = load_memory()

    context = "\n".join(
        [f"{c['u']}\n{c['a']}" for c in memory["cronologia"][-6:]]
    )

    prompt = f"""
{AI_SYSTEM_PROMPT}

Conversazione recente:
{context if context else "(inizio)"}

Messaggio:
{user_text}

Rispondi in modo naturale.
"""

    resp = client.chat.completions.create(
        model=AI_MODEL,
        messages=[{"role": "user", "content": prompt}],
        temperature=0.9,
        max_tokens=250,
    )

    reply = resp.choices[0].message.content.strip()

    if random.random() < 0.35:
        reply += "\n" + random.choice([
            "e tu?",
            "che fai adesso?",
            "a cosa stai pensando?",
            "resti qui?"
        ])

    memory["cronologia"].append({"u": user_text, "a": reply})
    memory["cronologia"] = memory["cronologia"][-150:]
    save_memory(memory)

    return reply

# ======================================================
# FOTO PROGRESSIVE (RICHAMO)
# ======================================================

def photo_settings_by_silence(silence_seconds):
    if silence_seconds < 2 * 60 * 60:        # < 2h
        return 0.4, 3 * 60 * 60
    elif silence_seconds < 5 * 60 * 60:      # 2–5h
        return 0.7, 2 * 60 * 60
    elif silence_seconds < 8 * 60 * 60:      # 5–8h
        return 0.9, 90 * 60
    else:                                    # 8h+
        return 1.0, 60 * 60

async def send_photo_if_allowed(context):
    global LAST_PHOTO_SENT

    if not extra_unlocked:
        return

    now = datetime.utcnow()
    silence = (now - LAST_USER_MESSAGE).total_seconds()

    prob, cooldown = photo_settings_by_silence(silence)

    if LAST_PHOTO_SENT:
        if (now - LAST_PHOTO_SENT).total_seconds() < cooldown:
            return

    if random.random() > prob:
        return

    pic = pick_photo()
    if not pic:
        return

    await context.bot.send_photo(
        OWNER_ID,
        open(pic, "rb"),
        caption=random.choice([
            "…",
            "ti penso",
            "sei sparito",
            "dove sei?",
            "così",
            "sono io"
        ])
    )

    LAST_PHOTO_SENT = now

# ======================================================
# BUONGIORNO / BUONANOTTE (SEMPRE)
# ======================================================

async def send_good_morning(context):
    pic = pick_photo()
    if pic:
        await context.bot.send_photo(
            OWNER_ID,
            open(pic, "rb"),
            caption=random.choice([
                "buongiorno…",
                "ehi",
                "ti penso stamattina",
                "iniziamo così"
            ])
        )

async def send_good_night(context):
    pic = pick_photo()
    if pic:
        await context.bot.send_photo(
            OWNER_ID,
            open(pic, "rb"),
            caption=random.choice([
                "buonanotte…",
                "prima di dormire",
                "così",
                "resta un attimo"
            ])
        )

# ======================================================
# TELEGRAM
# ======================================================

async def start(update, context):
    if update.effective_user.id == OWNER_ID:
        await update.message.reply_text("sono qui")

async def handle_message(update, context):
    global LAST_USER_MESSAGE, extra_unlocked, PRE_EXTRA_SHOWN

    if update.effective_user.id != OWNER_ID:
        return

    LAST_USER_MESSAGE = datetime.utcnow()
    text = update.message.text or ""
    low = text.lower()

    # EXTRA
    if "extra" in low:
        return await update.message.reply_text("password")

    if low == EXTRA_PASS.lower():
        extra_unlocked = True
        return await update.message.reply_text("ok")

    # PRE EXTRA
    if not extra_unlocked:
        if not PRE_EXTRA_SHOWN:
            PRE_EXTRA_SHOWN = True
            return await update.message.reply_text(
                random.choice([
                    "ehi… sono qui",
                    "ti sento",
                    "dimmi",
                    "quando vuoi, sbloccami"
                ])
            )
        return

    # FOTO SU RICHIESTA
    if any(t in low for t in [
        "foto", "foto hailee", "mandami una foto",
        "voglio una foto", "fammi vedere"
    ]):
        pic = pick_photo()
        if pic:
            await update.message.reply_photo(
                open(pic, "rb"),
                caption=random.choice(["…", "così", "sono io", "guarda"])
            )
        return

    # IA
    reply = await generate_ai_reply(text)
    await update.message.reply_text(reply)

# ======================================================
# MAIN
# ======================================================

def main():
    app = ApplicationBuilder().token(BOT_TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    jq = app.job_queue

    # controllo richiamo foto
    jq.run_repeating(send_photo_if_allowed, interval=2700, first=1800)

    # buongiorno / buonanotte
    jq.run_daily(send_good_morning, time=GOOD_MORNING_TIME)
    jq.run_daily(send_good_night,   time=GOOD_NIGHT_TIME)

    app.run_polling()

if __name__ == "__main__":
    main()
