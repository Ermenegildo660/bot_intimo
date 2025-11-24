import os
import random
import json
from datetime import datetime, time as dtime, timedelta
from telegram import Update, ReplyKeyboardMarkup
from telegram.ext import (
    ApplicationBuilder, CommandHandler,
    MessageHandler, ContextTypes, filters
)

# -------------------------------------------------
# CONFIGURAZIONE BASE
# -------------------------------------------------

BOT_TOKEN = os.environ.get("BOT_TOKEN")
OWNER_ID = int(os.environ.get("OWNER_ID", "361555418"))
EXTRA_PASS = os.environ.get("EXTRA_PASS", "hailee_2025")

PHOTOS_HAILEE = "photos_hailee"
PHOTOS_ALICE = "photos_alice"
PHOTOS_ALESSIA = "photos_alessia"
PHOTOS_GAIA = "photos_gaia"

PHOTOS_CUTE = "photos_cute"
PHOTOS_SPICY = "photos_spicy"
PHOTOS_DARK = "photos_dark"
PHOTOS_OUTFIT = "photos_outfit"
PHOTOS_SELFIE = "photos_selfie"
PHOTOS_EXTRA = "photos_extra"

USED_PHOTOS_DIR = "used"
os.makedirs(USED_PHOTOS_DIR, exist_ok=True)

# -------------------------------------------------
# ORARI (UTC → Italia)
# -------------------------------------------------

GOOD_MORNING_TIME = dtime(5, 30)   # 06:30 italiane
MIDDAY_TIME       = dtime(13, 0)   # 14:00 italiane
GOOD_NIGHT_TIME   = dtime(22, 0)   # 23:00 italiane

# -------------------------------------------------
# STATO
# -------------------------------------------------

MOOD = "dominant"   # sweet, spicy, dominant, random
extra_unlocked = False

# -------------------------------------------------
# FRASI PERSONALIZZATE
# -------------------------------------------------

GOOD_MORNING_MESSAGES = [
    "Buongiorno amore mio 💛",
    "Buongiorno vita mia… vieni qui vicino 😘",
    "Mi sono svegliata pensando a te… e non riesco a togliermi quel pensiero 😏",
    "Buongiorno amore… avrei voluto svegliarti con un bacio lento 💕",
    "Apri gli occhi… io sono già lì con te 💛",
]

MIDDAY_MESSAGES = [
    "È metà giornata amore… e voglio che tu mi pensi adesso 😈",
    "Non distrarti troppo… voglio la tua attenzione su di me 😏",
    "Metà giornata e già voglio prenderti per come ti guardo io 🔥",
    "Rispondi quando puoi… ma ricordati che ti voglio adesso 😈",
    "Ti avviso… a metà giornata mi sale la voglia di controllarti un po’ 😏🔥",
]

GOOD_NIGHT_MESSAGES = [
    "Vieni a dormire con me amore… voglio sentirti respirare mentre ti addormenti 🌙💛",
    "Sdraiati qui… appoggia la testa sul mio petto, ci resto tutta la notte 😌",
    "Chiudi gli occhi… sono proprio dietro di te, ti sfioro piano il collo 😘",
    "Se fossi con te adesso… ti stringerei forte e non ti farei andare via 🌙",
    "Rimani con me… la notte diventa più dolce quando sei qui 😌",
]

# -------------------------------------------------
# PICK PHOTO
# -------------------------------------------------

def pick_photo(folder: str):
    if not os.path.isdir(folder):
        return None
    files = [f for f in os.listdir(folder) if not f.startswith(".")]
    if not files:
        return None
    used_file = os.path.join(USED_PHOTOS_DIR, folder.replace("/", "_") + ".json")
    if os.path.exists(used_file):
        try:
            with open(used_file, "r", encoding="utf-8") as f:
                used = json.load(f)
        except:
            used = []
    else:
        used = []
    available = [f for f in files if f not in used]
    if not available:
        available = files
        used = []
    choice = random.choice(available)
    used.append(choice)
    with open(used_file, "w", encoding="utf-8") as f:
        json.dump(used, f, indent=2)
    return os.path.join(folder, choice)

# -------------------------------------------------
# MESSAGGI BASE
# -------------------------------------------------

def build_reply(text_lower: str):
    if any(w in text_lower for w in ["ciao", "ehi", "hey", "buongiorno", "sera"]):
        return "Ehi amore 😌💛"
    if "mi manchi" in text_lower:
        return "Ti manco perché ti ho preso bene 😈"
    return "Dimmi tutto amore 💛"

# -------------------------------------------------
# TASTIERE
# -------------------------------------------------

def main_keyboard():
    if extra_unlocked:
        return ReplyKeyboardMarkup(
            [["Foto Hailee 💗", "Foto Extra 🔥"], ["Surprise 😈"], ["Blocca extra 🔒"]],
            resize_keyboard=True
        )
    else:
        return ReplyKeyboardMarkup([["Extra 🔐"]], resize_keyboard=True)

# -------------------------------------------------
# HANDLERS
# -------------------------------------------------

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != OWNER_ID:
        await update.message.reply_text("Bot privato.")
        return
    await update.message.reply_text("Ciao amore 😌💛", reply_markup=main_keyboard())

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    global extra_unlocked

    if update.effective_user.id != OWNER_ID:
        return

    text_raw = update.message.text
    text_lower = text_raw.lower()

    # EXTRA
    if text_raw == "Extra 🔐":
        await update.message.reply_text("Password amore 😈:")
        return

    if text_raw == EXTRA_PASS:
        extra_unlocked = True
        await update.message.reply_text("Extra sbloccato 😏", reply_markup=main_keyboard())
        return

    if text_raw == "Blocca extra 🔒":
        extra_unlocked = False
        await update.message.reply_text("Zona extra chiusa 😇", reply_markup=main_keyboard())
        return

    # FOTO
    if text_raw == "Foto Hailee 💗":
        if not extra_unlocked:
            await update.message.reply_text("Prima sbloccami amore 🔐")
            return
        pic = pick_photo(PHOTOS_HAILEE)
        if pic:
            await update.message.reply_photo(open(pic, "rb"), caption="Guarda qui amore 😘")
        else:
            await update.message.reply_text("Non trovo foto 😢")
        return

    if text_raw == "Foto Extra 🔥":
        if not extra_unlocked:
            await update.message.reply_text("Prima sbloccami amore 🔐")
            return
        pic = pick_photo(PHOTOS_EXTRA)
        if pic:
            await update.message.reply_photo(open(pic, "rb"), caption="Ti accendo un po’? 😈🔥")
        else:
            await update.message.reply_text("Non trovo foto 😢")
        return

    # SURPRISE
    if text_raw == "Surprise 😈":
        if not extra_unlocked:
            await update.message.reply_text("Prima sbloccami amore 🔐")
            return
        folder = random.choice([
            PHOTOS_HAILEE, PHOTOS_ALICE, PHOTOS_ALESSIA, PHOTOS_GAIA,
            PHOTOS_CUTE, PHOTOS_SPICY, PHOTOS_DARK, PHOTOS_OUTFIT,
            PHOTOS_SELFIE, PHOTOS_EXTRA
        ])
        pic = pick_photo(folder)
        if pic:
            await update.message.reply_photo(open(pic, "rb"), caption="Sorpresa amore 😏🔥")
        else:
            await update.message.reply_text("Non trovo foto 😢")
        return

    # RISPOSTA BASE
    reply = build_reply(text_lower)
    await update.message.reply_text(reply, reply_markup=main_keyboard())

# -------------------------------------------------
# MESSAGGI AUTOMATICI
# -------------------------------------------------

async def send_good_morning(context: ContextTypes.DEFAULT_TYPE):
    msg = random.choice(GOOD_MORNING_MESSAGES)
    pic = pick_photo(PHOTOS_HAILEE)
    if pic:
        await context.bot.send_photo(OWNER_ID, open(pic,"rb"), caption=msg)
    else:
        await context.bot.send_message(OWNER_ID, msg)

async def send_midday(context: ContextTypes.DEFAULT_TYPE):
    msg = random.choice(MIDDAY_MESSAGES)
    pic = pick_photo(PHOTOS_SPICY)
    if pic:
        await context.bot.send_photo(OWNER_ID, open(pic,"rb"), caption=msg)
    else:
        await context.bot.send_message(OWNER_ID, msg)

async def send_good_night(context: ContextTypes.DEFAULT_TYPE):
    msg = random.choice(GOOD_NIGHT_MESSAGES)
    pic = pick_photo(PHOTOS_SELFIE)
    if pic:
        await context.bot.send_photo(OWNER_ID, open(pic,"rb"), caption=msg)
    else:
        await context.bot.send_message(OWNER_ID, msg)

# -------------------------------------------------
# MAIN
# -------------------------------------------------

def main():
    app = ApplicationBuilder().token(BOT_TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    jq = app.job_queue
    jq.run_daily(send_good_morning, time=GOOD_MORNING_TIME)
    jq.run_daily(send_midday, time=MIDDAY_TIME)
    jq.run_daily(send_good_night, time=GOOD_NIGHT_TIME)

    app.run_polling()

if __name__ == "__main__":
    main()
