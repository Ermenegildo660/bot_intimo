import os
import random
from telegram import Update, ReplyKeyboardMarkup
from telegram.ext import (
    ApplicationBuilder, CommandHandler,
    MessageHandler, ContextTypes, filters
)

BOT_TOKEN = os.environ.get("BOT_TOKEN")
OWNER_ID = int(os.environ.get("OWNER_ID", "361555418"))
EXTRA_PASS = os.environ.get("EXTRA_PASS", "hailee_2025")
PHOTOS_FOLDER = "photos_hailee"

GOOD_MORNING_MSGS = [
    "Buongiorno… un pensiero speciale per te 💗",
    "Sveglia amore… guarda chi pensa a te ☀️",
    "Nuovo giorno, stesso pensiero: tu 💕"
]

GOOD_NIGHT_MSGS = [
    "Buonanotte amore… sogni dolcissimi 🌙❤️",
    "Chiudi gli occhi, sono vicino a te 🌙",
    "Sogni belli… io ti penso 💕"
]

extra_unlocked = False

def random_photo():
    if not os.path.isdir(PHOTOS_FOLDER):
        return None
    files = [f for f in os.listdir(PHOTOS_FOLDER)]
    if not files:
        return None
    return os.path.join(PHOTOS_FOLDER, random.choice(files))

def keyboard():
    if extra_unlocked:
        return ReplyKeyboardMarkup([["Foto segreta"], ["Extra 🔐"]], resize_keyboard=True)
    return ReplyKeyboardMarkup([["Extra 🔐"]], resize_keyboard=True)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != OWNER_ID:
        await update.message.reply_text("Bot privato.")
        return
    await update.message.reply_text("Bot attivo.", reply_markup=keyboard())

async def handle_text(update: Update, context: ContextTypes.DEFAULT_TYPE):
    global extra_unlocked

    if update.effective_user.id != OWNER_ID:
        return

    text = update.message.text

    if text == "Extra 🔐":
        await update.message.reply_text("Inserisci la password:")
        return

    if text == EXTRA_PASS:
        extra_unlocked = True
        await update.message.reply_text("Extra sbloccato 🔥", reply_markup=keyboard())
        return

    if text == "Foto segreta":
        if not extra_unlocked:
            await update.message.reply_text("Prima devi sbloccare l'extra.")
            return
        pic = random_photo()
        if pic:
            await update.message.reply_photo(
                open(pic, "rb"),
                caption="Ecco il tuo pensiero speciale ❤️"
            )
        else:
            await update.message.reply_text("Nessuna foto trovata.")
        return

    await update.message.reply_text("Comando non riconosciuto.")

def main():
    app = ApplicationBuilder().token(BOT_TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_text))

    app.run_polling()

if __name__ == "__main__":
    main()
