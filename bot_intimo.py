
# ---------------- BOT INTIMO COMPLETO CON MENU FOTO 📸 ----------------

import os
import random
import json
from datetime import datetime, time as dtime, timedelta
from telegram import Update, ReplyKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, ContextTypes, filters

# -------------------------------------------------
# CONFIGURAZIONE BASE
# -------------------------------------------------

BOT_TOKEN = os.environ.get("BOT_TOKEN")
OWNER_ID = int(os.environ.get("OWNER_ID", "361555418"))
EXTRA_PASS = os.environ.get("EXTRA_PASS", "hailee_2025")

# Cartelle foto
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

GOOD_MORNING_TIME = dtime(5, 30)
MIDDAY_TIME       = dtime(13, 0)
GOOD_NIGHT_TIME   = dtime(22, 0)

MOOD = "dominant"
extra_unlocked = False
SUBMENU_OPEN = False  # stato per il menu FOTO 📸

# -------------------------------------------------
# FUNZIONI FOTO
# -------------------------------------------------

PHOTO_CATEGORIES = {
    "hailee 💗": PHOTOS_HAILEE,
    "alice 💜": PHOTOS_ALICE,
    "alessia 💙": PHOTOS_ALESSIA,
    "gaia 💚": PHOTOS_GAIA,
    "cute 💛": PHOTOS_CUTE,
    "spicy 🔥": PHOTOS_SPICY,
    "dark 🖤": PHOTOS_DARK,
    "selfie 🤳": PHOTOS_SELFIE,
    "outfit 👗": PHOTOS_OUTFIT,
    "extra 📁": PHOTOS_EXTRA
}

def pick_photo(folder: str):
    if not os.path.isdir(folder):
        return None

    files = [f for f in os.listdir(folder) if not f.startswith(".")]
    if not files:
        return None

    used_file = os.path.join(USED_PHOTOS_DIR, folder + ".json")

    if os.path.exists(used_file):
        with open(used_file, "r") as f:
            used = json.load(f)
    else:
        used = []

    available = [f for f in files if f not in used]

    if not available:
        available = files
        used = []

    choice = random.choice(available)
    used.append(choice)

    with open(used_file, "w") as f:
        json.dump(used, f, indent=2)

    return os.path.join(folder, choice)

# -------------------------------------------------
# TASTIERE
# -------------------------------------------------

def main_keyboard():
    if extra_unlocked:
        return ReplyKeyboardMarkup(
            [["Foto 📸", "Surprise 😏"], ["Extra 🔐"]],
            resize_keyboard=True
        )
    return ReplyKeyboardMarkup([["Extra 🔐"]], resize_keyboard=True)

def photo_menu_keyboard():
    return ReplyKeyboardMarkup(
        [
            ["Hailee 💗", "Alice 💜"],
            ["Alessia 💙", "Gaia 💚"],
            ["Cute 💛", "Spicy 🔥"],
            ["Dark 🖤", "Selfie 🤳"],
            ["Outfit 👗", "Extra 📁"],
            ["Indietro ↩️"]
        ],
        resize_keyboard=True
    )

# -------------------------------------------------
# HANDLER
# -------------------------------------------------

async def start(update, context):
    if update.effective_user.id != OWNER_ID:
        return await update.message.reply_text("Bot privato.")
    await update.message.reply_text("Ciao amore 😌💛", reply_markup=main_keyboard())

async def handle_message(update, context):
    global extra_unlocked, SUBMENU_OPEN

    if update.effective_user.id != OWNER_ID:
        return

    text = update.message.text.lower()

    # PASSWORD EXTRA
    if text == "extra 🔐":
        return await update.message.reply_text("Password amore 😈:")

    if text == EXTRA_PASS:
        extra_unlocked = True
        return await update.message.reply_text("Extra sbloccato 😏", reply_markup=main_keyboard())

    # MENU FOTO PRINCIPALE
    if text == "foto 📸":
        SUBMENU_OPEN = True
        return await update.message.reply_text("Scegli la categoria amore 😌📸", reply_markup=photo_menu_keyboard())

    # USCITA DAL MENU FOTO
    if text == "indietro ↩️":
        SUBMENU_OPEN = False
        return await update.message.reply_text("Tornata al menu principale amore 💛", reply_markup=main_keyboard())

    # SELEZIONE CATEGORIA FOTO
    if SUBMENU_OPEN:
        for label, folder in PHOTO_CATEGORIES.items():
            if text == label.lower():
                pic = pick_photo(folder)
                if pic:
                    return await update.message.reply_photo(open(pic,"rb"), caption=f"{label}")
                else:
                    return await update.message.reply_text("Non ho trovato foto amore 😢")

    # SURPRISE
    if text == "surprise 😏":
        # Pescata speciale potenziata
        weighted = (
            [PHOTOS_SPICY]*3 +
            [PHOTOS_SELFIE]*2 +
            list(PHOTO_CATEGORIES.values())
        )
        folder = random.choice(weighted)
        pic = pick_photo(folder)
        if pic:
            return await update.message.reply_photo(open(pic,"rb"), caption="Sorpresa 😈")
        return await update.message.reply_text("Non trovo foto per la sorpresa… 😢")

    # RISPOSTA GENERICA
    return await update.message.reply_text("Dimmi tutto amore 💛", reply_markup=main_keyboard())

# -------------------------------------------------
# FUNZIONI AUTOMATICHE
# -------------------------------------------------

async def send_good_morning(context):
    pic = pick_photo(PHOTOS_HAILEE)
    if pic:
        await context.bot.send_photo(OWNER_ID, open(pic,"rb"), caption="Buongiorno amore 💛")

# -------------------------------------------------
# MAIN
# -------------------------------------------------

def main():
    app = ApplicationBuilder().token(BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT, handle_message))

    jq = app.job_queue
    jq.run_daily(send_good_morning, time=GOOD_MORNING_TIME)

    app.run_polling()

if __name__ == "__main__":
    main()
