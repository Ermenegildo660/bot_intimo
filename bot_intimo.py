import os
import random
from datetime import time as dtime
from telegram import Update, ReplyKeyboardMarkup
from telegram.ext import (
    ApplicationBuilder, CommandHandler,
    MessageHandler, ContextTypes, filters
)

# ------------------------------
# CONFIG
# ------------------------------

BOT_TOKEN = os.environ.get("BOT_TOKEN")
OWNER_ID = int(os.environ.get("OWNER_ID", "361555418"))
EXTRA_PASS = os.environ.get("EXTRA_PASS", "hailee_2025")
PHOTOS_FOLDER = "photos_hailee"

# ---- Messaggi Buongiorno / Buonanotte (sensuali ma non espliciti)

GOOD_MORNING_MSGS = [
    "Buongiorno… ho pensato a te appena mi sono svegliata ☀️💕",
    "Apri gli occhi… qualcuno ti pensa già molto forte 💗",
    "Vorrei svegliarti con un abbraccio lento e pieno di calore 💕",
    "Nuovo giorno… ma il mio primo pensiero rimani sempre tu 💛"
]

GOOD_NIGHT_MSGS = [
    "Buonanotte… vorrei essere la tua ultima dolcezza prima di dormire 🌙💗",
    "Chiudi gli occhi… e immaginami vicina a te 🌙💕",
    "Riposa bene… ti lascio un pensiero tenero tutto per te 💛",
    "Che i tuoi sogni siano leggeri e pieni di cose belle… come te 🌙✨"
]

# ------------------------------
# EXTRA
# ------------------------------

extra_unlocked = False

def random_photo():
    """Ritorna una foto casuale dalla cartella."""
    if not os.path.isdir(PHOTOS_FOLDER):
        return None
    files = os.listdir(PHOTOS_FOLDER)
    if not files:
        return None
    return os.path.join(PHOTOS_FOLDER, random.choice(files))

def keyboard():
    """Tastiera dinamica."""
    if extra_unlocked:
        return ReplyKeyboardMarkup([
            ["Foto segreta"],
            ["Extra 🔐"]
        ], resize_keyboard=True)
    return ReplyKeyboardMarkup([["Extra 🔐"]], resize_keyboard=True)

# ------------------------------
# START
# ------------------------------

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != OWNER_ID:
        await update.message.reply_text("Bot privato.")
        return
    await update.message.reply_text("Bot attivo 💗", reply_markup=keyboard())

# ------------------------------
# MESSAGGI TESTUALI
# ------------------------------

async def handle_text(update: Update, context: ContextTypes.DEFAULT_TYPE):
    global extra_unlocked

    if update.effective_user.id != OWNER_ID:
        return

    text = update.message.text

    # --- Richiesta password extra
    if text == "Extra 🔐":
        await update.message.reply_text("Inserisci la password per accedere all'area riservata:")
        return

    # --- Password corretta
    if text == EXTRA_PASS:
        extra_unlocked = True
        await update.message.reply_text(
            "Accesso extra approvato 💗",
            reply_markup=keyboard()
        )
        return

    # --- Foto segreta
    if text == "Foto segreta":
        if not extra_unlocked:
            await update.message.reply_text("Devi prima sbloccare l'area Extra 🔐")
            return

        pic = random_photo()
        if pic:
            await update.message.reply_photo(
                photo=open(pic, "rb"),
                caption="Ecco un pensiero dolce e un po' speciale per te 💕"
            )
        else:
            await update.message.reply_text("Nessuna foto trovata nella cartella.")
        return

    # --- Comando non riconosciuto
    await update.message.reply_text("Non ho capito…")

# ------------------------------
# BUONGIORNO AUTOMATICO
# ------------------------------

async def buongiorno(context: ContextTypes.DEFAULT_TYPE):
    pic = random_photo()
    msg = random.choice(GOOD_MORNING_MSGS)

    if pic:
        await context.bot.send_photo(OWNER_ID, open(pic, "rb"), caption=msg)
    else:
        await context.bot.send_message(OWNER_ID, msg)

# ------------------------------
# BUONANOTTE AUTOMATICO
# ------------------------------

async def buonanotte(context: ContextTypes.DEFAULT_TYPE):
    pic = random_photo()
    msg = random.choice(GOOD_NIGHT_MSGS)

    if pic:
        await context.bot.send_photo(OWNER_ID, open(pic, "rb"), caption=msg)
    else:
        await context.bot.send_message(OWNER_ID, msg)

# ------------------------------
# MAIN (Railway friendly)
# ------------------------------

def main():
    app = ApplicationBuilder().token(BOT_TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_text))

    jq = app.job_queue
    jq.run_daily(buongiorno, time=dtime(6, 30))
    jq.run_daily(buonanotte, time=dtime(23, 0))

    app.run_polling()

if __name__ == "__main__":
    main()
