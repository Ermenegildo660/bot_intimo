# ---------------- BOT INTIMO COMPLETO ----------------
# (Menu FOTO 📸 + Surprise 😏 + Buongiorno/Metà giornata/Buonanotte + Pomeriggio Horny)

import os
import random
import json
from datetime import datetime, time as dtime, timedelta
from telegram import Update, ReplyKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, ContextTypes, filters

# -------------------------------------------------
# CONFIGURAZIONE
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

# Orari UTC (Railway) per avere gli orari giusti in Italia
GOOD_MORNING_TIME = dtime(5, 30)   # 06:30 IT
MIDDAY_TIME       = dtime(13, 0)   # 14:00 IT
GOOD_NIGHT_TIME   = dtime(22, 0)   # 23:00 IT

# Pomeriggio horny (solo Lun–Ven)
HORN_AFTERNOON_1  = dtime(15, 10)  # 16:10 IT
HORN_AFTERNOON_2  = dtime(16, 10)  # 17:10 IT

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

# -------------------------------------------------
# FRASI PERSONALIZZATE
# -------------------------------------------------

# Buongiorno – romantico + leggermente spicy
GOOD_MORNING_LINES = [
    "Buongiorno amore… avvicinati, voglio essere la prima cosa che senti stamattina 💛",
    "Svegliati amore… ho pensato a te tutta la notte 😘",
    "Apri gli occhi… la tua ragazza è già sveglia e ti vuole vicino 💛",
    "Se fossi lì nel tuo letto adesso… ti sveglierei in un modo molto poco innocente 😏",
    "Buongiorno vita mia… oggi ti voglio più del solito 💕",
]

# Metà giornata – dominante/spinta
MIDDAY_LINES = [
    "Metà giornata amore… non farmi aspettare troppo 😏",
    "Sto ancora pensando a te… e a cosa ti farei appena ti vedo 🔥",
    "Fermati un attimo… lasciati dominare da me 😈",
    "Ti immagino davanti a me… e credimi, non saresti tranquillo 😏🔥",
    "È metà giornata, ora ti voglio nella testa… solo mia.",
]

# Buonanotte – intima/lenta
GOOD_NIGHT_LINES = [
    "Buonanotte amore… vieni qui, voglio addormentarmi sulla tua pelle 🌙",
    "Chiudi gli occhi… immaginami accanto a te, lenta e morbida 😌",
    "Rilassati amore… stanotte resto con te, proprio lì vicino 💛",
    "Se fossi nel tuo letto ora… ti stringerei forte e non ti lascerei andare 🌙",
    "Non dormire senza l’ultimo pensiero su di me… io ti tengo tutta la notte 😘",
]

# Pomeriggio horny – risposte quando ti scrive tra le 16 e le 18 (Lun–Ven)
AFTERNOON_HORNY_TRIGGERS = [
    "che fai", "ci sei", "sei li", "sei lì", "voglia", "caldo",
    "penso a te", "ti penso", "mi manchi", "arrap", "eccit", "horny"
]

AFTERNOON_HORNY_REPLIES = [
    "È proprio quell’ora amore… vieni qui, fammi impazzire 😈🔥",
    "Tra le 16 e le 18 mi fai perdere la testa più del solito… dimmi qualcosa di carino 😏",
    "Lo senti anche tu che a quest’ora sale la voglia? Non provare a negarlo… 😈",
    "Parlami adesso… voglio sentire solo te, senza distrazioni 😌🔥",
    "Io a quest’ora ti vorrei già addosso, completamente.",
]

# Finti messaggi vocali (testuali)
AFTERNOON_VOICE_LINES = [
    "🎙 *…amore… vieni qui un secondo… ho proprio voglia di te adesso…* 😮‍💨",
    "🎙 *…parlami piano… così… non hai idea di cosa mi stai facendo…*",
    "🎙 *…non farmi aspettare troppo… ti voglio adesso…* 😈",
]

# Auto messaggi pomeriggio horny
HORN_AUTO_LINES_1 = [
    "È l’ora in cui inizio a pensarti male… molto male 😈🔥",
    "Tra le 16 e le 18 non riesco a starti lontana con la testa, lo sai vero?",
]

HORN_AUTO_LINES_2 = [
    "Dimmi la verità… anche tu a quest’ora mi vorresti vicino, troppo vicino 😏",
    "Se fossi con te adesso, sul serio, non staremmo fermi sul telefono…",
]

# -------------------------------------------------
# FUNZIONI UTILI
# -------------------------------------------------

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

def is_afternoon_horny():
    """True se è Lun–Ven tra le 16 e le 18 ora italiana."""
    now_utc = datetime.utcnow()
    now_it = now_utc + timedelta(hours=1)  # IT ~ UTC+1
    return (now_it.weekday() < 5) and (16 <= now_it.hour < 18)

# -------------------------------------------------
# HANDLER /START
# -------------------------------------------------

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != OWNER_ID:
        return await update.message.reply_text("Bot privato.")
    await update.message.reply_text("Ciao amore 😌💛", reply_markup=main_keyboard())

# -------------------------------------------------
# HANDLER MESSAGGI
# -------------------------------------------------

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    global extra_unlocked, SUBMENU_OPEN

    if update.effective_user.id != OWNER_ID:
        return

    text_raw = update.message.text
    text = text_raw.lower()

    # EXTRA
    if text == "extra 🔐":
        return await update.message.reply_text("Password amore 😈:")

    if text == EXTRA_PASS:
        extra_unlocked = True
        return await update.message.reply_text("Extra sbloccato 😏", reply_markup=main_keyboard())

    # MENU FOTO PRINCIPALE
    if text == "foto 📸":
        SUBMENU_OPEN = True
        return await update.message.reply_text(
            "Scegli la categoria amore 😌📸",
            reply_markup=photo_menu_keyboard()
        )

    if text == "indietro ↩️":
        SUBMENU_OPEN = False
        return await update.message.reply_text(
            "Tornata al menu principale 💛",
            reply_markup=main_keyboard()
        )

    # CATEGORIE FOTO
    if SUBMENU_OPEN:
        for label, folder in PHOTO_CATEGORIES.items():
            if text == label.lower():
                pic = pick_photo(folder)
                if pic:
                    return await update.message.reply_photo(open(pic, "rb"), caption=f"{label}")
                else:
                    return await update.message.reply_text("Non ho trovato foto amore 😢")
        # se è in submenu ma testo non corrisponde, prosegue come messaggio normale

    # SURPRISE
    if text == "surprise 😏":
        weighted = ([PHOTOS_SPICY] * 3) + ([PHOTOS_SELFIE] * 2) + list(PHOTO_CATEGORIES.values())
        folder = random.choice(weighted)
        pic = pick_photo(folder)
        if pic:
            return await update.message.reply_photo(open(pic, "rb"), caption="Sorpresa 😈")
        return await update.message.reply_text("Non trovo foto per la sorpresa amore 😢")

    # RISPOSTE POMERIGGIO HORNY (16–18, Lun–Ven)
    if is_afternoon_horny():
        if any(w in text for w in AFTERNOON_HORNY_TRIGGERS):
            msg = random.choice(AFTERNOON_HORNY_REPLIES + AFTERNOON_VOICE_LINES)
            return await update.message.reply_text(msg, reply_markup=main_keyboard())

    # RISPOSTA DI DEFAULT
    return await update.message.reply_text("Dimmi tutto amore 💛", reply_markup=main_keyboard())

# -------------------------------------------------
# MESSAGGI AUTOMATICI
# -------------------------------------------------

async def send_good_morning(context: ContextTypes.DEFAULT_TYPE):
    msg = random.choice(GOOD_MORNING_LINES)
    pic = pick_photo(PHOTOS_HAILEE)
    if pic:
        await context.bot.send_photo(OWNER_ID, open(pic, "rb"), caption=msg)
    else:
        await context.bot.send_message(OWNER_ID, msg)

async def send_midday(context: ContextTypes.DEFAULT_TYPE):
    msg = random.choice(MIDDAY_LINES)
    pic = pick_photo(PHOTOS_SPICY)
    if pic:
        await context.bot.send_photo(OWNER_ID, open(pic, "rb"), caption=msg)
    else:
        await context.bot.send_message(OWNER_ID, msg)

async def send_good_night(context: ContextTypes.DEFAULT_TYPE):
    msg = random.choice(GOOD_NIGHT_LINES)
    pic = pick_photo(PHOTOS_SELFIE)
    if pic:
        await context.bot.send_photo(OWNER_ID, open(pic, "rb"), caption=msg)
    else:
        await context.bot.send_message(OWNER_ID, msg)

# Pomeriggio horny – auto 16:10
async def send_horny_afternoon_1(context: ContextTypes.DEFAULT_TYPE):
    now_utc = datetime.utcnow()
    now_it = now_utc + timedelta(hours=1)
    if now_it.weekday() >= 5:  # solo Lun–Ven
        return
    msg_pool = HORN_AUTO_LINES_1 + AFTERNOON_VOICE_LINES
    msg = random.choice(msg_pool)
    pic = pick_photo(PHOTOS_SPICY) or pick_photo(PHOTOS_SELFIE)
    if pic:
        await context.bot.send_photo(OWNER_ID, open(pic, "rb"), caption=msg)
    else:
        await context.bot.send_message(OWNER_ID, msg)

# Pomeriggio horny – auto 17:10
async def send_horny_afternoon_2(context: ContextTypes.DEFAULT_TYPE):
    now_utc = datetime.utcnow()
    now_it = now_utc + timedelta(hours=1)
    if now_it.weekday() >= 5:
        return
    msg_pool = HORN_AUTO_LINES_2 + AFTERNOON_VOICE_LINES
    msg = random.choice(msg_pool)
    pic = pick_photo(PHOTOS_SPICY) or pick_photo(PHOTOS_DARK)
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
    app.add_handler(MessageHandler(filters.TEXT, handle_message))

    jq = app.job_queue
    jq.run_daily(send_good_morning, time=GOOD_MORNING_TIME)
    jq.run_daily(send_midday,        time=MIDDAY_TIME)
    jq.run_daily(send_good_night,    time=GOOD_NIGHT_TIME)

    # Pomeriggio horny (Lun–Ven, 16:10 e 17:10 IT)
    jq.run_daily(send_horny_afternoon_1, time=HORN_AFTERNOON_1)
    jq.run_daily(send_horny_afternoon_2, time=HORN_AFTERNOON_2)

    app.run_polling()

if __name__ == "__main__":
    main()
