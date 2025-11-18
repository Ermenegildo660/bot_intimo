import os
import random
from datetime import time as dtime
from telegram import Update, ReplyKeyboardMarkup
from telegram.ext import (
    ApplicationBuilder, CommandHandler,
    MessageHandler, ContextTypes, filters
)

# -------------------------------
# CONFIG
# -------------------------------

BOT_TOKEN = os.environ.get("BOT_TOKEN")
OWNER_ID = int(os.environ.get("OWNER_ID", "361555418"))
EXTRA_PASS = os.environ.get("EXTRA_PASS", "hailee_2025")
PHOTOS_FOLDER = "photos_hailee"

GOOD_MORNING_TIME = dtime(6, 30)
GOOD_NIGHT_TIME = dtime(23, 0)
MIDDAY_TIME = dtime(14, 0)

# -------------------------------
# MESSAGGI HOT 😈🔥
# -------------------------------

GOOD_MORNING_MSGS = [
    "Buongiorno Baby… spero ti svegli già pensando a me 😘🔥",
    "Apri gli occhi amore… immaginami sopra di te 😈💦",
    "Buongiorno… oggi voglio che tu mi desideri tutto il giorno 😏🔥"
]

GOOD_NIGHT_MSGS = [
    "Buonanotte Baby… vieni a dormire con me, nudo 😈🔥",
    "Chiudi gli occhi e immaginami tra le tue braccia… 💋",
    "Sogni bollenti amore… voglio essere nei tuoi pensieri stanotte 😘🔥"
]

MIDDAY_MSGS = [
    "Metà giornata Baby… ti voglio adesso 😈💦",
    "Guarda questa foto e pensa a cosa ti farei… 😘🔥",
    "Sto pensando al tuo corpo… e mi sto scaldando 😏🔥",
    "Hai bisogno di una pausa hot? Eccomi 😈💋"
]

MOOD_MSGS = [
    "Baby… oggi ho una voglia incredibile di te 😈🔥",
    "Sto pensando al tuo corpo… fammi impazzire 😘",
    "Hai idea di quanto ti desidero adesso? 😏💦",
    "Voglio essere la tua dipendenza oggi… 😈🔥"
]

extra_unlocked = False

# -------------------------------
# FOTO CASUALE
# -------------------------------

def random_photo():
    if not os.path.isdir(PHOTOS_FOLDER):
        return None
    files = [f for f in os.listdir(PHOTOS_FOLDER)]
    if not files:
        return None
    return os.path.join(PHOTOS_FOLDER, random.choice(files))

# -------------------------------
# TASTIERA
# -------------------------------

def keyboard():
    if extra_unlocked:
        return ReplyKeyboardMarkup(
            [["Foto segreta 🔥"], ["Umore 😈"], ["Extra 🔐"]],
            resize_keyboard=True
        )
    return ReplyKeyboardMarkup([["Extra 🔐"], ["Umore 😈"]], resize_keyboard=True)

# -------------------------------
# START
# -------------------------------

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != OWNER_ID:
        await update.message.reply_text("Bot privato.")
        return
    await update.message.reply_text("Ciao Baby 😘🔥", reply_markup=keyboard())

# -------------------------------
# HANDLER TESTI
# -------------------------------

async def handle_text(update: Update, context: ContextTypes.DEFAULT_TYPE):
    global extra_unlocked
    user = update.effective_user.id

    if user != OWNER_ID:
        return

    text = update.message.text

    # PASSWORD
    if text == "Extra 🔐":
        await update.message.reply_text("Dimmi la password Baby 😈:")
        return

    if text == EXTRA_PASS:
        extra_unlocked = True
        await update.message.reply_text("Extra sbloccato Baby 😘🔥", reply_markup=keyboard())
        return

    # FOTO SEGRETA
    if text == "Foto segreta 🔥":
        if not extra_unlocked:
            await update.message.reply_text("Prima devi sbloccare l’area extra Baby 😘")
            return
        pic = random_photo()
        if pic:
            await update.message.reply_photo(open(pic, "rb"),
                caption="Ecco un pensiero hot per te Baby 😈🔥")
        else:
            await update.message.reply_text("Non ci sono foto.")
        return

    # UMORE HOT
    if text == "Umore 😈":
        msg = random.choice(MOOD_MSGS)
        await update.message.reply_text(msg)
        return

    await update.message.reply_text("Non ho capito Baby 😘")

# -------------------------------
# AUTOMATICI
# -------------------------------

async def buongiorno(context: ContextTypes.DEFAULT_TYPE):
    pic = random_photo()
    msg = random.choice(GOOD_MORNING_MSGS)
    if pic:
        await context.bot.send_photo(OWNER_ID, open(pic, "rb"), caption=msg)
    else:
        await context.bot.send_message(OWNER_ID, msg)

async def buonanotte(context: ContextTypes.DEFAULT_TYPE):
    pic = random_photo()
    msg = random.choice(GOOD_NIGHT_MSGS)
    if pic:
        await context.bot.send_photo(OWNER_ID, open(pic, "rb"), caption=msg)
    else:
        await context.bot.send_message(OWNER_ID, msg)

async def foto_meta_giornata(context: ContextTypes.DEFAULT_TYPE):
    pic = random_photo()
    msg = random.choice(MIDDAY_MSGS)
    if pic:
        await context.bot.send_photo(OWNER_ID, open(pic, "rb"), caption=msg)
    else:
        await context.bot.send_message(OWNER_ID, msg)

# -------------------------------
# MAIN
# -------------------------------

def main():
    app = ApplicationBuilder().token(BOT_TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_text))

    jq = app.job_queue
    jq.run_daily(buongiorno, GOOD_MORNING_TIME)
    jq.run_daily(buonanotte, GOOD_NIGHT_TIME)
    jq.run_daily(foto_meta_giornata, MIDDAY_TIME)

    app.run_polling()

if __name__ == "__main__":
    main()
