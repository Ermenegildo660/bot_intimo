# ---------------- BOT INTIMO COMPLETO — VERSIONE STABILE ----------------
# IA personale (invariata), UNA sola cartella foto,
# invio foto casuale + per inattività (realistico),
# extra unlock, messaggi automatici, niente categorie.

import os
import random
import json
from datetime import datetime, time as dtime, timedelta
from zoneinfo import ZoneInfo

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

ROME_TZ = ZoneInfo("Europe/Rome")

LAST_USER_MESSAGE = datetime.utcnow()
LAST_PHOTO_SENT = None
extra_unlocked = False

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

    if os.path.exists(USED_PHOTOS_FILE):
        try:
            used = json.load(open(USED_PHOTOS_FILE))
        except Exception:
            used = []
    else:
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
# TEMPI FOTO (UMANI)
# ======================================================

MIN_SILENCE_FOR_PHOTO = 90 * 60      # 90 min senza scrivere
PHOTO_COOLDOWN = 3 * 60 * 60         # minimo 3 ore tra due foto

# ======================================================
# MEMORIA (MINIMA – IA INVARIATA)
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
    "Sei una persona reale, romantica, affettuosa, sensibile e un po' gelosa. "
    "Parli in modo naturale, non robotico. "
    "Usi frasi brevi. A volte fai domande spontanee. "
    "Non usare etichette o nomi. "
)

async def generate_ai_reply(user_text: str) -> str:
    memory = load_memory()

    ctx = []
    for c in memory["cronologia"][-6:]:
        ctx.append(c["u"])
        ctx.append(c["a"])
    context = "\n".join(ctx)

    prompt = f"""
{AI_SYSTEM_PROMPT}

Conversazione recente:
{context if context else "(inizio)"}

Messaggio:
{user_text}

Rispondi in modo naturale, umano.
"""

    resp = client.chat.completions.create(
        model=AI_MODEL,
        messages=[{"role": "user", "content": prompt}],
        temperature=0.9,
        max_tokens=250,
    )

    reply = resp.choices[0].message.content.strip()

    # Domanda spontanea (non sempre)
    if random.random() < 0.35:
        reply += "\n" + random.choice([
            "e tu?",
            "che fai adesso?",
            "a cosa stai pensando?",
            "resti qui un attimo?"
        ])

    memory["cronologia"].append({"u": user_text, "a": reply})
    memory["cronologia"] = memory["cronologia"][-150:]
    save_memory(memory)

    return reply

# ======================================================
# FOTO SMART (CASUALI + INATTIVITÀ)
# ======================================================

async def send_photo_if_allowed(context):
    global LAST_PHOTO_SENT

    if not extra_unlocked:
        return

    now = datetime.utcnow()

    # cooldown
    if LAST_PHOTO_SENT and (now - LAST_PHOTO_SENT).total_seconds() < PHOTO_COOLDOWN:
        return

    silence = (now - LAST_USER_MESSAGE).total_seconds()
    if silence < MIN_SILENCE_FOR_PHOTO:
        return

    # non sempre
    if random.random() < 0.5:
        return

    pic = pick_photo()
    if not pic:
        return

    await context.bot.send_photo(
        OWNER_ID,
        open(pic, "rb"),
        caption=random.choice(["…", "ti penso", "così", "guarda"])
    )

    LAST_PHOTO_SENT = now

# ======================================================
# INATTIVITÀ
# ======================================================

async def check_inactivity(context):
    global LAST_USER_MESSAGE

    now = datetime.utcnow()
    diff = (now - LAST_USER_MESSAGE).total_seconds()

    # prova foto prima
    if diff >= MIN_SILENCE_FOR_PHOTO:
        await send_photo_if_allowed(context)

    # messaggio dopo 2h
    if diff >= 7200:
        await context.bot.send_message(
            OWNER_ID,
            random.choice([
                "Dove sei…?",
                "È un po’ che non ti sento.",
                "Mi manchi."
            ])
        )
        LAST_USER_MESSAGE = datetime.utcnow()

# ======================================================
# TELEGRAM
# ======================================================

async def start(update, context):
    if update.effective_user.id != OWNER_ID:
        return
    await update.message.reply_text("sono qui")

async def handle_message(update, context):
    global LAST_USER_MESSAGE, extra_unlocked

    if update.effective_user.id != OWNER_ID:
        return

    LAST_USER_MESSAGE = datetime.utcnow()
    text = update.message.text.lower()

    if "extra" in text:
        return await update.message.reply_text("password")

    if text == EXTRA_PASS.lower():
        extra_unlocked = True
        return await update.message.reply_text("ok")

    if not extra_unlocked:
        return await update.message.reply_text("scrivimi")

    reply = await generate_ai_reply(update.message.text)
    await update.message.reply_text(reply)

# ======================================================
# MAIN
# ======================================================

def main():
    app = ApplicationBuilder().token(BOT_TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    jq = app.job_queue

    # controllo foto casuali ogni 45 min
    jq.run_repeating(send_photo_if_allowed, interval=2700, first=1800)

    # controllo inattività ogni 30 min
    jq.run_repeating(check_inactivity, interval=1800, first=1800)

    app.run_polling()

if __name__ == "__main__":
    main()
