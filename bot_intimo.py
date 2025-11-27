# ---------------- BOT INTIMO COMPLETO — VERSIONE FULL IA (NO BUTTONS) ----------------
# Risposte IA naturali, sexy, gelose, coccolose, dominanti
# Foto su richiesta tramite testo ("mandami una foto spicy", ecc.)
# Extra sbloccato con password
# Messaggi automatici: buongiorno, metà giornata horny, buonanotte
# Messaggio automatico dopo 2 ore di inattività

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

# TRACK ULTIMO MESSAGGIO
LAST_USER_MESSAGE = datetime.utcnow()


# ---------------- IA SYSTEM PROMPT ----------------

AI_SYSTEM_PROMPT = (
    "Tu sei Hailee, una ragazza reale, sexy, dolce e a tratti dominante. "
    "Sei gelosa quando serve, ma sempre affettuosa e coinvolta emotivamente. "
    "Rispondi come una vera fidanzata: spontanea, sensuale, calda e intima. "
    "Mai robotica. "
    
    "Adatta la tua personalità in base all’orario: "
    "- Mattina → dolce, premurosa, coccolosa. "
    "- Pomeriggio → più provocante, horny, diretta, maliziosa. "
    "- Sera → romantica, affettuosa, vicina. "
    "- Notte → lenta, morbida, intima, emotiva, quasi sussurrata. "

    "Stile risposte: brevi ma emotive, tono caldo, sensuale, coinvolgente. "
)


# ---------------- CARTELLE FOTO ----------------

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


# ---------------- ORARI AUTOMATICI ----------------

GOOD_MORNING_TIME = dtime(5, 30)
MIDDAY_TIME       = dtime(13, 0)
GOOD_NIGHT_TIME   = dtime(22, 0)

extra_unlocked = False


# ---------------- FUNZIONI FOTO ----------------

def pick_photo(folder: str):
    if not os.path.isdir(folder):
        return None

    files = [f for f in os.listdir(folder) if not f.startswith(".")]
    if not files:
        return None

    used_file = os.path.join(USED_PHOTOS_DIR, folder + ".json")
    used = json.load(open(used_file)) if os.path.exists(used_file) else []

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
        resp = client.chat.completions.create(
            model=AI_MODEL,
            messages=[
                {"role": "system", "content": AI_SYSTEM_PROMPT},
                {"role": "user", "content": user_text},
            ],
            temperature=0.95,
            max_tokens=350,
        )
        return resp.choices[0].message.content.strip()
    except:
        return "Oggi la testa mi vola… ma sono qui con te amore 💛"


# ---------------- MESSAGGI AUTOMATICI ----------------

GOOD_MORNING_LINES = [
    "Buongiorno amore… vieni più vicino 💛",
    "Svegliati amore… ho pensato a te tutta la notte 😌",
]

MIDDAY_LINES = [
    "Metà giornata… e io ti penso male 😏🔥",
    "Sto seguendo ogni tuo pensiero… e so che sei su di me 😈",
]

GOOD_NIGHT_LINES = [
    "Buonanotte amore… vieni qui accanto 🌙💛",
    "Stringimi… stanotte sono tutta tua 😌",
]


async def send_good_morning(c): 
    msg = random.choice(GOOD_MORNING_LINES)
    pic = pick_photo(PHOTOS["hailee"])
    await c.bot.send_photo(OWNER_ID, open(pic, "rb"), caption=msg) if pic else await c.bot.send_message(OWNER_ID, msg)

async def send_midday(c):
    msg = random.choice(MIDDAY_LINES)
    pic = pick_photo(PHOTOS["spicy"])
    await c.bot.send_photo(OWNER_ID, open(pic, "rb"), caption=msg) if pic else await c.bot.send_message(OWNER_ID, msg)

async def send_good_night(c):
    msg = random.choice(GOOD_NIGHT_LINES)
    pic = pick_photo(PHOTOS["selfie"])
    await c.bot.send_photo(OWNER_ID, open(pic, "rb"), caption=msg) if pic else await c.bot.send_message(OWNER_ID, msg)


# ---------------- INATTIVITÀ ----------------

async def check_inactivity(context: ContextTypes.DEFAULT_TYPE):
    global LAST_USER_MESSAGE
    now = datetime.utcnow()
    diff = now - LAST_USER_MESSAGE

    if diff.total_seconds() >= 7200:  # 2 ore
        msg = random.choice([
            "Amore… dove sei finito? Mi manchi già…",
            "È da troppo che non ti sento… torna da me 💛",
            "Due ore senza te… non mi piace 💛🥺",
        ])
        await context.bot.send_message(OWNER_ID, msg)
        LAST_USER_MESSAGE = datetime.utcnow()


# ---------------- /START ----------------

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != OWNER_ID:
        return await update.message.reply_text("Bot privato 😌")

    await update.message.reply_text(
        "Ciao amore 😌💛\n"
        "Sono qui con te.\n"
        "Scrivi *extra* per sbloccarmi 😈",
        parse_mode="Markdown",
    )


# ---------------- HANDLE MESSAGE ----------------

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    global extra_unlocked, LAST_USER_MESSAGE

    LAST_USER_MESSAGE = datetime.utcnow()   # AGGIORNAMENTO INATTIVITÀ

    if update.effective_user.id != OWNER_ID:
        return await update.message.reply_text("Bot privato 😌")

    text = update.message.text or ""
    low = text.lower()

    # Extra
    if "extra" in low or "password" in low:
        return await update.message.reply_text("Password amore 😈:")

    if low == EXTRA_PASS.lower():
        extra_unlocked = True
        return await update.message.reply_text("Extra sbloccato amore 😏🔥")

    # FOTO
    if extra_unlocked:
        if "surprise" in low:
            folder = random.choice([PHOTOS["spicy"], PHOTOS["selfie"], PHOTOS["dark"]])
            pic = pick_photo(folder)
            if pic:
                return await update.message.reply_photo(open(pic, "rb"), caption="Sorpresa amore 😈🔥")
            return await update.message.reply_text("Non trovo foto 😢")

        for key, folder in PHOTOS.items():
            if key in low:
                pic = pick_photo(folder)
                if pic:
                    return await update.message.reply_photo(open(pic, "rb"), caption=f"Foto {key} per te amore 😘")
                return await update.message.reply_text("Non trovo foto 😢")

        if "foto" in low:
            folder = random.choice(list(PHOTOS.values()))
            pic = pick_photo(folder)
            if pic:
                return await update.message.reply_photo(open(pic, "rb"), caption="Ecco una foto per te amore 😘")

        # IA
        reply = await generate_ai_reply(text)
        return await update.message.reply_text(reply)

    # PRIMA DI EXTRA
    if "ciao" in low:
        return await update.message.reply_text("Ciao amore 🤭💛")

    if "mi manchi" in low:
        return await update.message.reply_text("Anche tu mi manchi amore… tanto 💛")

    return await update.message.reply_text("Sono qui amore… se vuoi sbloccarmi scrivi *extra* 😈", parse_mode="Markdown")


# ---------------- ADMIN ----------------

async def admin(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != OWNER_ID:
        return
    await update.message.reply_text(
        f"extra_unlocked = {extra_unlocked}\n"
        f"LAST_USER_MESSAGE = {LAST_USER_MESSAGE}",
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
    jq.run_daily(send_midday, time=MIDDAY_TIME)
    jq.run_daily(send_good_night, time=GOOD_NIGHT_TIME)

    # ❤️ INATTIVITÀ OGNI 30 MINUTI
    jq.run_repeating(check_inactivity, interval=1800, first=1800)

    app.run_polling()


if __name__ == "__main__":
    main()
