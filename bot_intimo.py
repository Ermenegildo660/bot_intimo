# ---------------- BOT INTIMO COMPLETO ----------------
# (Versione con MENU FOTO 📸 + Surprise 😏 + Buongiorno/Buonanotte/Metà giornata)

import os
import random
import json
from datetime import datetime, time as dtime, timedelta
from telegram import Update, ReplyKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, ContextTypes, filters

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

GOOD_MORNING_TIME = dtime(5, 30)   # 06:30 italiane
MIDDAY_TIME       = dtime(13, 0)   # 14:00 italiane
GOOD_NIGHT_TIME   = dtime(22, 0)   # 23:00 italiane

# -------- FRASI PERSONALIZZATE (OPZIONE B) --------

GOOD_MORNING_MESSAGES = [
    "Buongiorno amore 💛",
    "Buongiorno vita mia 😌",
    "Vorrei averti nel mio letto appena sveglio 💕",
    "Ti voglio vicino già da stamattina 💛"
]

MIDDAY_MESSAGES = [
    "Metà giornata amore 😏",
    "Sto pensando a te proprio ora…",
    "Mi mancano già le tue mani 😈",
    "È metà giornata… fammi venire voglia di te 🔥"
]

GOOD_NIGHT_MESSAGES = [
    "Vieni più vicino… stanotte sei mio 🌙",
    "Appoggiati a me… dormi con me 🖤",
    "La notte ti voglio tutto per me 😈",
    "Stringimi… restiamo così fino a domattina 💛"
]

SUBMENU_OPEN = False
extra_unlocked = False

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

def pick_photo(folder):
    if not os.path.isdir(folder):
        return None
    files = [f for f in os.listdir(folder) if not f.startswith(".")]
    if not files:
        return None
    used_file = os.path.join(USED_PHOTOS_DIR, folder + ".json")
    used = []
    if os.path.exists(used_file):
        with open(used_file, "r") as f:
            used = json.load(f)
    available = [f for f in files if f not in used]
    if not available:
        available = files
        used = []
    choice = random.choice(available)
    used.append(choice)
    with open(used_file, "w") as f:
        json.dump(used, f, indent=2)
    return os.path.join(folder, choice)

def main_keyboard():
    if extra_unlocked:
        return ReplyKeyboardMarkup(
            [["Foto 📸", "Surprise 😏"], ["Extra 🔐"]],
            resize_keyboard=True)
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

async def start(update, context):
    if update.effective_user.id != OWNER_ID:
        return await update.message.reply_text("Bot privato.")
    await update.message.reply_text("Ciao amore 😌💛", reply_markup=main_keyboard())


# --- Heat Level Detection ---
def detect_heat_level(text):
    triggers = ["voglia","caldo","bacio","toccami","stringimi","dominami","desidero"]
    return sum(1 for t in triggers if t in text.lower())

# --- Heat Reaction ---
def heat_reaction(level):
    if level >= 3:
        return random.choice(DOMINANT_STRONG)
    if level == 2:
        return random.choice(SPICY_EXTRA)
    return None

# --- Night Intimacy Check ---
def is_night_intimacy():
    now = datetime.utcnow() + timedelta(hours=1)
    return now.hour >= 22 or now.hour < 3

async def handle_message(update, context):
    global extra_unlocked, SUBMENU_OPEN

    if update.effective_user.id != OWNER_ID:
        return

    text = update.message.text.lower()

    if text == "extra 🔐":
        return await update.message.reply_text("Password amore 😈:")

    if text == EXTRA_PASS:
        extra_unlocked = True
        heat = detect_heat_level(text)
    hr = heat_reaction(heat)
    if hr:
        return await update.message.reply_text(hr, reply_markup=main_keyboard())
    if is_night_intimacy():
        return await update.message.reply_text(random.choice(NIGHT_INTIMATE), reply_markup=main_keyboard())
    return await update.message.reply_text("Dimmi tutto amore 💛", reply_markup=main_keyboard())

    if text == "foto 📸":
        SUBMENU_OPEN = True
        return await update.message.reply_text("Scegli la categoria amore 😌📸", reply_markup=photo_menu_keyboard())

    if text == "indietro ↩️":
        SUBMENU_OPEN = False
        heat = detect_heat_level(text)
    hr = heat_reaction(heat)
    if hr:
        return await update.message.reply_text(hr, reply_markup=main_keyboard())
    if is_night_intimacy():
        return await update.message.reply_text(random.choice(NIGHT_INTIMATE), reply_markup=main_keyboard())
    return await update.message.reply_text("Dimmi tutto amore 💛", reply_markup=main_keyboard())

    if SUBMENU_OPEN:
        for label, folder in PHOTO_CATEGORIES.items():
            if text == label.lower():
                pic = pick_photo(folder)
                if pic:
                    return await update.message.reply_photo(open(pic,"rb"), caption=f"{label}")
                else:
                    return await update.message.reply_text("Non ho trovato foto amore 😢")

    if text == "surprise 😏":
        weighted = ([PHOTOS_SPICY]*3) + ([PHOTOS_SELFIE]*2) + list(PHOTO_CATEGORIES.values())
        folder = random.choice(weighted)
        pic = pick_photo(folder)
        if pic:
            return await update.message.reply_photo(open(pic, "rb"), caption="Sorpresa 😈")
        return await update.message.reply_text("Non trovo foto per la sorpresa amore 😢")

    heat = detect_heat_level(text)
    hr = heat_reaction(heat)
    if hr:
        return await update.message.reply_text(hr, reply_markup=main_keyboard())
    if is_night_intimacy():
        return await update.message.reply_text(random.choice(NIGHT_INTIMATE), reply_markup=main_keyboard())
    return await update.message.reply_text("Dimmi tutto amore 💛", reply_markup=main_keyboard())


# ---------------- MESSAGGI AUTOMATICI ----------------

async def send_good_morning(context):
    msg = "Buongiorno amore 💛"
    pic = pick_photo(PHOTOS_HAILEE)
    if pic:
        await context.bot.send_photo(OWNER_ID, open(pic,"rb"), caption=msg)
    else:
        await context.bot.send_message(OWNER_ID, msg)

async def send_midday(context):
    msg = "Metà giornata amore 😏"
    pic = pick_photo(PHOTOS_SPICY)
    if pic:
        await context.bot.send_photo(OWNER_ID, open(pic,"rb"), caption=msg)
    else:
        await context.bot.send_message(OWNER_ID, msg)

async def send_good_night(context):
    msg = "Buonanotte amore 😌🌙"
    pic = pick_photo(PHOTOS_SELFIE)
    if pic:
        await context.bot.send_photo(OWNER_ID, open(pic,"rb"), caption=msg)
    else:
        await context.bot.send_message(OWNER_ID, msg)

# ---------------- MAIN ----------------

def main():
    app = ApplicationBuilder().token(BOT_TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT, handle_message))

    jq = app.job_queue
    jq.run_daily(send_good_morning, time=GOOD_MORNING_TIME)
    jq.run_daily(send_midday, time=MIDDAY_TIME)
    jq.run_daily(send_good_night, time=GOOD_NIGHT_TIME)

    app.run_polling()

if __name__ == "__main__":
    main()
