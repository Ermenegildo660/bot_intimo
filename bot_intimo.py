import os
import random
import json
from datetime import datetime, time as dtime, timedelta

from telegram import Update, ReplyKeyboardMarkup
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    MessageHandler,
    ContextTypes,
    filters,
)

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

# Tutte le cartelle (per Surprise, ecc.)
ALL_PHOTO_FOLDERS = [
    PHOTOS_HAILEE,
    PHOTOS_ALICE,
    PHOTOS_ALESSIA,
    PHOTOS_GAIA,
    PHOTOS_CUTE,
    PHOTOS_SPICY,
    PHOTOS_DARK,
    PHOTOS_OUTFIT,
    PHOTOS_SELFIE,
    PHOTOS_EXTRA,
]

USED_PHOTOS_DIR = "used"
os.makedirs(USED_PHOTOS_DIR, exist_ok=True)

# Orari in UTC per avere orari giusti in Italia su Railway
GOOD_MORNING_TIME = dtime(5, 30)   # 06:30 italiane
MIDDAY_TIME       = dtime(13, 0)   # 14:00 italiane
GOOD_NIGHT_TIME   = dtime(22, 0)   # 23:00 italiane

# Stato
extra_unlocked = False

# -------------------------------------------------
# FRASI PERSONALIZZATE
# -------------------------------------------------

GOOD_MORNING_MESSAGES = [
    "Buongiorno amore 💛",
    "Buongiorno vita mia 😌",
    "Vorrei averti nel mio letto appena sveglio 💕",
    "Ti voglio vicino già da stamattina 💛",
]

MIDDAY_MESSAGES = [
    "Metà giornata amore 😏",
    "Sto pensando a te proprio ora…",
    "Mi mancano già le tue mani 😈",
    "È metà giornata… fammi venire voglia di te 🔥",
]

GOOD_NIGHT_MESSAGES = [
    "Vieni più vicino… stanotte sei mio 🌙",
    "Appoggiati a me… dormi con me 🖤",
    "La notte ti voglio tutto per me 😈",
    "Stringimi… restiamo così fino a domattina 💛",
]

# Frasi per le foto
PHOTO_CAPTIONS_SOFT = [
    "Ti lascio questa… pensami bene 💛",
    "Tienimi con te per un po’ 😌",
    "Guardami… e dimmi che non ti manco.",
]

PHOTO_CAPTIONS_SPICY = [
    "Dimmi che questa ti accende un po’ 😈",
    "Immagina di avermi proprio lì davanti a te 🔥",
    "Lo sai che così ti provoco apposta, vero? 😏",
]

PHOTO_CAPTIONS_DOMINANT = [
    "Guarda bene… oggi comando io 😈",
    "Non distogliere lo sguardo, amore.",
    "Questa la voglio solo per te… e per la tua testa 😏",
]

NIGHT_INTIMATE = [
    "Vieni più vicino… la notte ti voglio solo mio 🌙",
    "Parlami piano… come se fossi sul tuo collo 😘",
    "Così… resta vicino a me stanotte 💛",
    "La notte con te è pericolosa… ma mi piace 😈",
]

# -------------------------------------------------
# UTILS FOTO (anti-ripetizione)
# -------------------------------------------------

def pick_photo(folder: str) -> str | None:
    """Ritorna una foto casuale dalla cartella, evitando ripetizioni finché possibile."""
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
        except Exception:
            used = []
    else:
        used = []

    available = [f for f in files if f not in used]

    if not available:
        # reset ciclo
        available = files
        used = []

    choice = random.choice(available)
    used.append(choice)

    with open(used_file, "w", encoding="utf-8") as f:
        json.dump(used, f, indent=2)

    return os.path.join(folder, choice)

# -------------------------------------------------
# TASTIERE
# -------------------------------------------------

def main_keyboard() -> ReplyKeyboardMarkup:
    # Mostriamo sempre Foto / Extra / Surprise
    return ReplyKeyboardMarkup(
        [["Foto 📸", "Extra 🔐", "Surprise 😏"]],
        resize_keyboard=True,
    )

def photos_keyboard() -> ReplyKeyboardMarkup:
    # Menu categorie foto
    keyboard = [
        ["Hailee 💗", "Alice 💙"],
        ["Alessia 💜", "Gaia 💚"],
        ["Cute 🧸", "Spicy 🔥"],
        ["Dark 🌑", "Outfit 👗"],
        ["Selfie 🤳", "Extra 🔥🔥"],
        ["Indietro 🔙"],
    ]
    return ReplyKeyboardMarkup(keyboard, resize_keyboard=True)

# Mappa tra testo bottone e cartella
PHOTO_BUTTON_MAP = {
    "Hailee 💗": PHOTOS_HAILEE,
    "Alice 💙": PHOTOS_ALICE,
    "Alessia 💜": PHOTOS_ALESSIA,
    "Gaia 💚": PHOTOS_GAIA,
    "Cute 🧸": PHOTOS_CUTE,
    "Spicy 🔥": PHOTOS_SPICY,
    "Dark 🌑": PHOTOS_DARK,
    "Outfit 👗": PHOTOS_OUTFIT,
    "Selfie 🤳": PHOTOS_SELFIE,
    "Extra 🔥🔥": PHOTOS_EXTRA,
}

# -------------------------------------------------
# FUNZIONI DI STATO
# -------------------------------------------------

def is_night_intimacy() -> bool:
    # Consideriamo notte 22:00–03:00 italiane (UTC+1 su Railway)
    now_utc = datetime.utcnow()
    now_it = now_utc + timedelta(hours=1)
    return now_it.hour >= 22 or now_it.hour < 3

# -------------------------------------------------
# HANDLER /START
# -------------------------------------------------

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != OWNER_ID:
        await update.message.reply_text("Bot privato.")
        return

    await update.message.reply_text(
        "Ciao amore 😌💛",
        reply_markup=main_keyboard(),
    )

# -------------------------------------------------
# HANDLER MESSAGGI
# -------------------------------------------------

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    global extra_unlocked

    if update.effective_user.id != OWNER_ID:
        return

    text_raw = update.message.text
    text = text_raw.lower()

    # ---------------- EXTRA / PASSWORD ----------------

    if text_raw == "Extra 🔐":
        await update.message.reply_text("Password amore 😈:", reply_markup=main_keyboard())
        # segno che sto aspettando la password
        context.user_data["waiting_password"] = True
        return

    if context.user_data.get("waiting_password") and text_raw == EXTRA_PASS:
        extra_unlocked = True
        context.user_data["waiting_password"] = False
        await update.message.reply_text(
            "Zona extra sbloccata… ora sei solo mio 😏",
            reply_markup=main_keyboard(),
        )
        return

    # Se scrive qualcosa dopo aver sbagliato, tolgo il flag
    if context.user_data.get("waiting_password") and text_raw != EXTRA_PASS:
        context.user_data["waiting_password"] = False
        await update.message.reply_text("Password sbagliata amore 😈", reply_markup=main_keyboard())
        return

    # ---------------- MENU FOTO / CATEGORIE ----------------

    if text_raw == "Foto 📸":
        if not extra_unlocked:
            await update.message.reply_text(
                "Prima sbloccami con la password, Baby 🔐",
                reply_markup=main_keyboard(),
            )
            return

        await update.message.reply_text(
            "Scegli da dove vuoi che ti mandi una foto 😏",
            reply_markup=photos_keyboard(),
        )
        return

    if text_raw == "Indietro 🔙":
        await update.message.reply_text("Torno qui da te 💛", reply_markup=main_keyboard())
        return

    # Se preme una categoria foto
    if text_raw in PHOTO_BUTTON_MAP:
        if not extra_unlocked:
            await update.message.reply_text(
                "Prima sbloccami con la password, Baby 🔐",
                reply_markup=main_keyboard(),
            )
            return

        folder = PHOTO_BUTTON_MAP[text_raw]
        pic = pick_photo(folder)
        if not pic:
            await update.message.reply_text("Non trovo foto in quella categoria 😢", reply_markup=photos_keyboard())
            return

        caption_pool = PHOTO_CAPTIONS_SOFT + PHOTO_CAPTIONS_SPICY + PHOTO_CAPTIONS_DOMINANT
        caption = random.choice(caption_pool)
        await update.message.reply_photo(open(pic, "rb"), caption=caption, reply_markup=photos_keyboard())
        return

    # ---------------- SURPRISE ----------------

    if text_raw == "Surprise 😏":
        if not extra_unlocked:
            await update.message.reply_text(
                "Prima sbloccami con la password, Baby 🔐",
                reply_markup=main_keyboard(),
            )
            return

        folder = random.choice(ALL_PHOTO_FOLDERS)
        pic = pick_photo(folder)
        if not pic:
            await update.message.reply_text("Nessuna foto amore…", reply_markup=main_keyboard())
            return

        caption = random.choice(
            ["Sorpresa 😈", "Non te l’aspettavi questa, vero? 😏", "Tieniti forte… 🔥"]
        )
        await update.message.reply_photo(open(pic, "rb"), caption=caption, reply_markup=main_keyboard())
        return

    # ---------------- RISPOSTE LIBERE ----------------

    # Se è notte, risposte più intime
    if is_night_intimacy():
        msg = random.choice(NIGHT_INTIMATE)
        await update.message.reply_text(msg, reply_markup=main_keyboard())
        return

    # Alcune parole chiave
    if any(w in text for w in ["ciao", "ehi", "hey", "buongiorno", "buonasera"]):
        await update.message.reply_text("Ehi amore 😌💛", reply_markup=main_keyboard())
        return

    if "mi manchi" in text:
        await update.message.reply_text("Ti manco perché ti ho preso bene 😈", reply_markup=main_keyboard())
        return

    if any(w in text for w in ["voglia", "caldo", "accendo", "brividi"]):
        await update.message.reply_text(
            random.choice(PHOTO_CAPTIONS_SPICY + PHOTO_CAPTIONS_DOMINANT),
            reply_markup=main_keyboard(),
        )
        return

    # Default
    await update.message.reply_text("Dimmi tutto amore 💛", reply_markup=main_keyboard())

# -------------------------------------------------
# MESSAGGI AUTOMATICI (GOOD MORNING / MIDDAY / NIGHT)
# -------------------------------------------------

async def send_good_morning(context: ContextTypes.DEFAULT_TYPE):
    msg = random.choice(GOOD_MORNING_MESSAGES)
    pic = pick_photo(PHOTOS_HAILEE)
    if pic:
        await context.bot.send_photo(OWNER_ID, open(pic, "rb"), caption=msg)
    else:
        await context.bot.send_message(OWNER_ID, msg)

async def send_midday(context: ContextTypes.DEFAULT_TYPE):
    msg = random.choice(MIDDAY_MESSAGES)
    pic = pick_photo(PHOTOS_SPICY)
    if pic:
        await context.bot.send_photo(OWNER_ID, open(pic, "rb"), caption=msg)
    else:
        await context.bot.send_message(OWNER_ID, msg)

async def send_good_night(context: ContextTypes.DEFAULT_TYPE):
    msg = random.choice(GOOD_NIGHT_MESSAGES)
    pic = pick_photo(PHOTOS_SELFIE)
    if pic:
        await context.bot.send_photo(OWNER_ID, open(pic, "rb"), caption=msg)
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
