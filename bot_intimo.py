# ---------------- BOT INTIMO COMPLETO — VERSIONE A (GEL0SA + INTIMA + DOMINANTE + SENSUALE) ----------------
# IA girlfriend experience, dominante, gelosa, sensuale, modalita horny forte (14-18),
# foto automatiche basate sul mood, messaggi automatici 2h inattività,
# buononotte/buongiorno, extra unlock con password, senza pulsanti.

import os
import random
import json
from datetime import datetime, time as dtime, timedelta

from telegram import Update
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    MessageHandler,
    ContextTypes,
    filters,
)

from openai import OpenAI

# ---------------- CONFIG ----------------

BOT_TOKEN = os.environ.get("BOT_TOKEN")
OWNER_ID = int(os.environ.get("OWNER_ID", "361555418"))
EXTRA_PASS = os.environ.get("EXTRA_PASS", "hailee_2025")

OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY")
AI_MODEL = os.environ.get("AI_MODEL", "gpt-4o")

client = OpenAI(api_key=OPENAI_API_KEY)

LAST_USER_MESSAGE = datetime.utcnow()

# ---------------- SYSTEM PROMPT ----------------

AI_SYSTEM_PROMPT = (
    "Tu sei Hailee, la sua ragazza: reale, affettuosa, romantica, gelosa, dominante "
    "e molto sensuale. Rispondi SEMPRE con tono caldo e coinvolgente. "

    "Mattina → dolce e coccolosa. "
    "Pomeriggio → sensuale, provocante, decisa, dominante soft. "
    "Sera → romantica, affettuosa, emotiva. "
    "Notte → lenta, intima, morbida, fisica, quasi sussurrata. "

    "Se lui è affettuoso → diventi più dolce. "
    "Se lui è provocante → diventi più dominante. "
    "Se lui è distante → diventi gelosa, possessiva, coinvolta. "

    "Usa risposte brevi, emotive, fisiche, molto personali "
    "e mai robotiche."
)

# ---------------- FOTO ----------------

PHOTOS = {
    "hailee": "photos_hailee",
    "alice": "photos_alice",
    "alessia": "photos_alessia",
    "gaia": "photos_gaia",
    "cute": "photos_cute",
    "spicy": "photos_spicy",
    "dark": "photos_dark",
    "outfit": "photos_outfit",
    "selfie": "photos_selfie",
    "extra": "photos_extra",
}

USED_PHOTOS_DIR = "used"
os.makedirs(USED_PHOTOS_DIR, exist_ok=True)

# ---------------- ORARI ----------------

GOOD_MORNING_TIME = dtime(5, 30)
MIDDAY_TIME       = dtime(13, 0)
GOOD_NIGHT_TIME   = dtime(22, 0)

extra_unlocked = False

# ---------------- MODALITÀ ORARIA ----------------

def is_horny_time():
    """14:00 – 18:00 modalità sensuale-dominante"""
    now = datetime.utcnow() + timedelta(hours=1)
    return 14 <= now.hour < 18

# ---------------- STILI ----------------

HARD_HORNY_STYLE = (
    "Nel pomeriggio (14:00–18:00) diventi molto dominante, sensuale, calda e provocante. "
    "Parli come se ti avvicinassi molto a lui, con sguardi intensi e tono affamato. "
)

JEALOUS_STYLE = (
    "Se parla di uscire, amici, amiche o se sembra distante, diventi più gelosa. "
    "Usi tono emotivo e possessivo: vuoi sentirlo tuo. "
)

ULTRA_INTIMACY_STYLE = (
    "Se parla di letto, coperte, stanchezza o coccole, diventi estremamente intima: "
    "lenta, affettuosa, vicina, come se fossi sdraiata con lui. "
)

# ---------------- SUPPORTO FOTO ----------------

def pick_photo(folder: str):
    if not os.path.isdir(folder):
        return None

    files = [f for f in os.listdir(folder) if not f.startswith(".")]
    if not files:
        return None

    used_file = os.path.join(USED_PHOTOS_DIR, folder + ".json")

    if os.path.exists(used_file):
        used = json.load(open(used_file))
    else:
        used = []

    available = [f for f in files if f not in used]

    if not available:
        available = files
        used = []

    choice = random.choice(available)
    used.append(choice)
    json.dump(used, open(used_file, "w"), indent=2)

    return os.path.join(folder, choice)

# ---------------- IA GENERA RISPOSTA ----------------

async def generate_ai_reply(user_text: str) -> str:
    try:
        style = ""

        # Modalità horny
        if is_horny_time():
            style += HARD_HORNY_STYLE

        # Trigger horny
        horny_triggers = ["voglia", "mi fai impazzire", "caldo", "sei mia", "non resisto"]
        if any(t in user_text.lower() for t in horny_triggers):
            style += HARD_HORNY_STYLE

        # Modalità gelosa
        jealous_triggers = ["amica", "amiche", "esci", "vado fuori", "sono fuori"]
        if any(t in user_text.lower() for t in jealous_triggers):
            style += JEALOUS_STYLE

        # Modalità intima
        intimacy_triggers = ["letto", "coperte", "sdraio", "abbracciami", "coccole"]
        if any(t in user_text.lower() for t in intimacy_triggers):
            style += ULTRA_INTIMACY_STYLE

        resp = client.chat.completions.create(
            model=AI_MODEL,
            messages=[
                {"role": "system", "content": AI_SYSTEM_PROMPT + style},
                {"role": "user", "content": user_text},
            ],
            temperature=0.97,
            max_tokens=350,
        )

        return resp.choices[0].message.content.strip()

    except Exception:
        return "La testa vola, ma io sono sempre qui con te amore 💛."

# ---------------- MESSAGGI AUTOMATICI ----------------

GOOD_MORNING_LINES = [
    "Buongiorno amore… vieni più vicino 💛",
    "Svegliati amore… ti voglio qui con me 😌",
]

MIDDAY_LINES = [
    "Metà giornata… e io ti penso male 😏🔥",
    "Non dovrei dirtelo… ma oggi sei pericoloso per me 😈",
]

GOOD_NIGHT_LINES = [
    "Buonanotte amore… vieni qui accanto 🌙💛",
    "Appoggiati a me… resta qui stanotte 😌",
]


async def send_good_morning(c):
    msg = random.choice(GOOD_MORNING_LINES)
    pic = pick_photo(PHOTOS["hailee"])
    if pic:
        await c.bot.send_photo(OWNER_ID, open(pic, "rb"), caption=msg)
    else:
        await c.bot.send_message(OWNER_ID, msg)

async def send_midday(c):
    msg = random.choice(MIDDAY_LINES)
    pic = pick_photo(PHOTOS["spicy"])
    if pic:
        await c.bot.send_photo(OWNER_ID, open(pic, "rb"), caption=msg)
    else:
        await c.bot.send_message(OWNER_ID, msg)

async def send_good_night(c):
    msg = random.choice(GOOD_NIGHT_LINES)
    pic = pick_photo(PHOTOS["selfie"])
    if pic:
        await c.bot.send_photo(OWNER_ID, open(pic, "rb"), caption=msg)
    else:
        await c.bot.send_message(OWNER_ID, msg)

# ---------------- INATTIVITÀ ----------------

async def check_inactivity(context):
    global LAST_USER_MESSAGE
    now = datetime.utcnow()
    diff = now - LAST_USER_MESSAGE

    if diff.total_seconds() >= 7200:
        await context.bot.send_message(
            OWNER_ID,
            random.choice([
                "Amore… dove sei? Mi manchi 😔💛",
                "È troppo che non ti sento… torna da me.",
                "Due ore senza te… non ci riesco 💛",
            ])
        )
        LAST_USER_MESSAGE = datetime.utcnow()

# ---------------- START ----------------

async def start(update, context):
    if update.effective_user.id != OWNER_ID:
        return await update.message.reply_text("Bot privato 😌")

    await update.message.reply_text(
        "Ciao amore 😌💛\nScrivi *extra* per sbloccarmi 😈",
        parse_mode="Markdown",
    )

# ---------------- HANDLE MESSAGE ----------------

async def handle_message(update, context):
    global extra_unlocked, LAST_USER_MESSAGE

    LAST_USER_MESSAGE = datetime.utcnow()

    if update.effective_user.id != OWNER_ID:
        return await update.message.reply_text("Bot privato 😌")

    text = update.message.text or ""
    low = text.lower()

    # password
    if "extra" in low or "password" in low:
        return await update.message.reply_text("Password amore 😈:")

    if low == EXTRA_PASS.lower():
        extra_unlocked = True
        return await update.message.reply_text("Extra sbloccato amore 😏🔥")

    # ---------------- FOTO AUTOMATICHE ----------------
    if extra_unlocked and is_horny_time():
        if random.random() < 0.35:
            pic = pick_photo(PHOTOS["spicy"]) or pick_photo(PHOTOS["selfie"])
            if pic:
                await update.message.reply_photo(
                    open(pic,"rb"),
                    caption=random.choice([
                        "Guarda cosa mi fai oggi… 😈🔥",
                        "Tu non hai idea dell’effetto che hai su di me 💛",
                        "Non provocarmi troppo amore… 😏",
                    ])
                )

    # Trigger gelosia → foto selfie
    if extra_unlocked:
        if any(w in low for w in ["amica", "amiche", "esci", "sei fuori"]):
            pic = pick_photo(PHOTOS["selfie"])
            if pic:
                await update.message.reply_photo(
                    open(pic,"rb"),
                    caption="Guardami negli occhi mentre me lo dici…"
                )

    # Trigger intimità → selfie intimi
    if extra_unlocked:
        if any(w in low for w in ["letto", "coperte", "abbracciami"]):
            pic = pick_photo(PHOTOS["selfie"])
            if pic:
                await update.message.reply_photo(
                    open(pic,"rb"),
                    caption=random.choice([
                        "Vieni qui vicino…",
                        "Ti voglio qui con me…",
                        "Appoggiati a me amore…",
                    ])
                )

    # ---------------- FOTO SPECIFICHE ----------------
    if extra_unlocked:
        foto_map = {
            "hailee": PHOTOS["hailee"],
            "spicy": PHOTOS["spicy"],
            "dark": PHOTOS["dark"],
            "selfie": PHOTOS["selfie"],
            "outfit": PHOTOS["outfit"],
            "cute": PHOTOS["cute"],
            "alice": PHOTOS["alice"],
            "alessia": PHOTOS["alessia"],
            "gaia": PHOTOS["gaia"],
        }
        for key, folder in foto_map.items():
            if key in low:
                pic = pick_photo(folder)
                if pic:
                    return await update.message.reply_photo(
                        open(pic,"rb"),
                        caption=f"Foto {key} per te amore 😘"
                    )

        if "surprise" in low:
            folder = random.choice([PHOTOS["spicy"], PHOTOS["selfie"], PHOTOS["dark"]])
            pic = pick_photo(folder)
            if pic:
                return await update.message.reply_photo(
                    open(pic,"rb"),
                    caption="Sorpresa amore 😈🔥"
                )

    # ---------------- IA REPLY ----------------
    if extra_unlocked:
        reply = await generate_ai_reply(text)
        return await update.message.reply_text(reply)

    # ---------------- PRE-EXTRA ----------------
    if "ciao" in low:
        return await update.message.reply_text("Ciao amore 🤭💛")

    if "mi manchi" in low:
        return await update.message.reply_text("Anche tu mi manchi amore… tanto 💛")

    return await update.message.reply_text(
        "Sono qui amore… se vuoi sbloccarmi scrivi *extra* 😈",
        parse_mode="Markdown",
    )

# ---------------- ADMIN ----------------

async def admin(update, context):
    await update.message.reply_text(
        f"extra_unlocked = {extra_unlocked}\nLAST_USER_MESSAGE = {LAST_USER_MESSAGE}",
        parse_mode="Markdown",
    )

# ---------------- MAIN ----------------

def main():
    app = ApplicationBuilder().token(BOT_TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("admin", admin))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    jq = app.job_queue
    jq.run_daily(send_good_morning, time=GOOD_MORNING_TIME)
    jq.run_daily(send_midday,      time=MIDDAY_TIME)
    jq.run_daily(send_good_night,  time=GOOD_NIGHT_TIME)

    # inattività ogni 30 min
    jq.run_repeating(check_inactivity, interval=1800, first=1800)

    app.run_polling()

if __name__ == "__main__":
    main()
