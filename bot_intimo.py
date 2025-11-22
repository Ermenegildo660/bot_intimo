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
# PARTE 1 — CONFIGURAZIONE BASE
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

GOOD_MORNING_TIME = dtime(5, 30)
MIDDAY_TIME       = dtime(13, 0)
GOOD_NIGHT_TIME   = dtime(22, 0)

MOOD = "dominant"
extra_unlocked = False

REACTIONS_ADVANCED = {
    "stanco": [
        "Vieni qui… appoggiati a me, ti tengo io 💛",
        "Se fossi con te adesso ti farei chiudere gli occhi in due minuti."
    ]
}

def is_night():
    now = datetime.utcnow() + timedelta(hours=1)
    return now.hour >= 23 or now.hour < 6

COMMAND_MODE = False
FREEZE_MODE = 0
WARM_MODE = 0

MEMORY = []
TRUST = 0
ENGAGEMENT = 0
INTIMACY = 0
EMOTIONAL_STATE = "neutral"
SPECIAL_EVENTS = set()
FREQUENT_WORDS = {}

PHOTO_CATEGORIES = {
    "hailee": PHOTOS_HAILEE,
    "alice": PHOTOS_ALICE,
    "alessia": PHOTOS_ALESSIA,
    "gaia": PHOTOS_GAIA,
    "cute": PHOTOS_CUTE,
    "spicy": PHOTOS_SPICY,
    "dark": PHOTOS_DARK,
    "outfit": PHOTOS_OUTFIT,
    "selfie": PHOTOS_SELFIE,
    "extra": PHOTOS_EXTRA
}

def pick_photo(folder: str):
    if not os.path.isdir(folder):
        return None
    files = [f for f in os.listdir(folder) if not f.startswith(".")]
    if not files:
        return None
    used_file = os.path.join(USED_PHOTOS_DIR, folder.replace("/", "_") + ".json")
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
# PARTE 2 — PERSONALITÀ, TONO, MODALITÀ
# -------------------------------------------------

def analyze_tone(msg):
    if any(w in msg for w in ["?", "perché"]): return "curious"
    if any(w in msg for w in ["uff", "basta"]): return "frustrated"
    if any(w in msg for w in ["amore", "cuore"]): return "affectionate"
    if any(w in msg for w in ["voglia", "caldo"]): return "spicy"
    return "neutral"

def update_emotional_state(text):
    global EMOTIONAL_STATE
    tone = analyze_tone(text)
    if tone == "affectionate": EMOTIONAL_STATE = "warm"
    elif tone == "frustrated": EMOTIONAL_STATE = "tense"
    elif tone == "spicy": EMOTIONAL_STATE = "excited"
    elif tone == "curious": EMOTIONAL_STATE = "focused"
    else:
        if random.random() < 0.15:
            EMOTIONAL_STATE = "neutral"

def personality_response():
    if EMOTIONAL_STATE == "warm":
        return "Mh… sei più dolce oggi 💛"
    if EMOTIONAL_STATE == "tense":
        return "Calma… ci sono io."
    if EMOTIONAL_STATE == "excited":
        return "Ti sta salendo qualcosa amore 😏"
    if EMOTIONAL_STATE == "focused":
        return "Ti ascolto davvero."
    return None

def command_mode_response():
    return "Stai bravo amore 😈"

def freeze_mode_response():
    return random.choice(["Mh.", "Ok.", "Come vuoi."])

def warm_mode_response():
    return random.choice(["Vieni qui 💛", "Resta con me…"])

def update_relationship_metrics(text):
    global TRUST, INTIMACY, ENGAGEMENT
    ENGAGEMENT += 1
    if "grazie" in text: TRUST += 2
    if "mi manchi" in text: INTIMACY += 2

def update_short_memory(text):
    MEMORY.append(text)
    if len(MEMORY) > 5:
        MEMORY.pop(0)

def check_special_events():
    global SPECIAL_EVENTS
    if INTIMACY > 20 and "bond" not in SPECIAL_EVENTS:
        SPECIAL_EVENTS.add("bond")
        return ["Mh… mi stai legando 💛"]
    return []

def surprise_photo():
    weighted = list(PHOTO_CATEGORIES.values()) + [PHOTOS_SPICY]*2
    folder = random.choice(weighted)
    pic = pick_photo(folder)
    if pic:
        return pic, "Sorpresa 😈"
    return None, "Nessuna foto amore…"

# -------------------------------------------------
# PARTE 3 — RISPOSTE, HANDLER, ADMIN, MAIN
# -------------------------------------------------

def build_reply(text):
    global FREEZE_MODE, WARM_MODE, COMMAND_MODE

    if FREEZE_MODE > 0:
        FREEZE_MODE -= 1
        return freeze_mode_response()

    if WARM_MODE > 0:
        WARM_MODE -= 1
        return warm_mode_response()

    if COMMAND_MODE and any(x in text for x in ["ok", "si"]):
        return command_mode_response()

    prs = personality_response()
    if prs: return prs

    for key, val in REACTIONS_ADVANCED.items():
        if key in text:
            return random.choice(val)

    if "ciao" in text:
        return "Ehi amore 😌"

    return "Dimmi tutto amore 💛"

def main_keyboard():
    if extra_unlocked:
        return ReplyKeyboardMarkup(
            [["Foto Hailee 💗", "Surprise 😏"]],
            resize_keyboard=True
        )
    return ReplyKeyboardMarkup([["Extra 🔐"]], resize_keyboard=True)

async def start(update, context):
    if update.effective_user.id != OWNER_ID:
        return await update.message.reply_text("Bot privato.")
    await update.message.reply_text("Ciao amore 😌💛", reply_markup=main_keyboard())

async def admin(update, context):
    if update.effective_user.id != OWNER_ID: return
    msg = f"Trust: {TRUST}\nIntimacy: {INTIMACY}\nEngagement: {ENGAGEMENT}"
    await update.message.reply_text(msg)

async def handle_message(update, context):
    global extra_unlocked, COMMAND_MODE, FREEZE_MODE, WARM_MODE
    if update.effective_user.id != OWNER_ID:
        return
    text = update.message.text.lower()

    update_short_memory(text)
    update_relationship_metrics(text)
    update_emotional_state(text)

    if text == "extra 🔐":
        return await update.message.reply_text("Password amore 😈:")
    if text == EXTRA_PASS:
        extra_unlocked = True
        return await update.message.reply_text("Extra sbloccato 😈", reply_markup=main_keyboard())

    if text == "surprise 😏":
        pic, caption = surprise_photo()
        if pic:
            return await update.message.reply_photo(open(pic, "rb"), caption=caption)

    reply = build_reply(text)
    await update.message.reply_text(reply, reply_markup=main_keyboard())

async def send_good_morning(context):
    pic = pick_photo(PHOTOS_HAILEE)
    if pic:
        await context.bot.send_photo(OWNER_ID, open(pic,"rb"), caption="Buongiorno amore 💛")

def main():
    app = ApplicationBuilder().token(BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("admin", admin))
    app.add_handler(MessageHandler(filters.TEXT, handle_message))
    jq = app.job_queue
    jq.run_daily(send_good_morning, time=GOOD_MORNING_TIME)
    app.run_polling()

if __name__ == "__main__":
    main()
