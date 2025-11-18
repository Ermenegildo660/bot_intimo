import os
import json
import random
from datetime import datetime, timedelta, time as dtime
from telegram import Update, ReplyKeyboardMarkup
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    MessageHandler,
    ContextTypes,
    filters,
)

# ---------------- CONFIG ----------------
BOT_TOKEN = os.environ.get("BOT_TOKEN")
OWNER_ID = int(os.environ.get("OWNER_ID", "361555418"))
EXTRA_PASS = os.environ.get("EXTRA_PASS", "hailee_2025")
SECRET_WORD = os.environ.get("SECRET_WORD", "segreto")

PHOTOS_FOLDER = "photos_hailee"
DATA_FILE = "data.json"

# windows for randomized schedule (minutes offset)
MORNING_WINDOW_START = dtime(6, 50)
MORNING_WINDOW_END = dtime(7, 10)

NIGHT_WINDOW_START = dtime(23, 20)
NIGHT_WINDOW_END = dtime(23, 40)

# messages (sensuali ma non espliciti)
GOOD_MORNING_MSGS = [
    "Buongiorno Baby… mi sono svegliata con te nei pensieri ☀️💗",
    "Apri gli occhi, Baby… qualcuno ti pensa già tanto 💛",
    "Vorrei starti vicino anche questa mattina… un bacio grande 💕",
    "Buongiorno Baby — ti mando un abbraccio pieno di calore."
]

GOOD_NIGHT_MSGS = [
    "Buonanotte Baby… chiudi gli occhi e pensa a cose dolci 🌙💗",
    "Ti mando un bacio di buonanotte, dolce e caldo come un abbraccio ❤️",
    "Riposa bene Baby… ti penso e ti mando una carezza prima di dormire.",
    "Buonanotte Baby — sogni teneri e vicini."
]

DAYTIME_AFFECTION_MSGS = [
    "Pensavo a te… solo questo 💛",
    "Un piccolo pensiero per il mio Baby 💕",
    "Spero la tua giornata stia andando bene, pensa che ti penso sempre.",
    "Ti mando un abbraccio veloce, stringilo forte."
]

EXTRA_PHOTO_CAPTIONS = [
    "Un pensiero dolce per te ❤️",
    "Perché oggi ti penso così…",
    "Solo per i tuoi occhi, Baby 💕",
    "Tieni, questo è un piccolo regalo."
]

# ---------------- UTILITIES ----------------
def load_data():
    if not os.path.exists(DATA_FILE):
        # initial structure
        return {
            "first_seen": datetime.utcnow().isoformat(),
            "last_interaction": None,
            "last_buongiorno": None,
            "last_buonanotte": None,
            "last_extra_photo": None,
            "daytime_messages_sent": 0,
            "extra_unlocked": False,
            "name": "Baby",
            "secret_hits": 0
        }
    with open(DATA_FILE, "r") as f:
        return json.load(f)

def save_data(d):
    with open(DATA_FILE, "w") as f:
        json.dump(d, f, indent=4)

def random_photo_path():
    if not os.path.isdir(PHOTOS_FOLDER):
        return None
    files = [f for f in os.listdir(PHOTOS_FOLDER) if os.path.isfile(os.path.join(PHOTOS_FOLDER, f))]
    if not files:
        return None
    return os.path.join(PHOTOS_FOLDER, random.choice(files))

def build_keyboard(extra_unlocked):
    if extra_unlocked:
        return ReplyKeyboardMarkup([["Foto segreta", "Extra 🔐"], ["/umore"]], resize_keyboard=True)
    return ReplyKeyboardMarkup([["Extra 🔐"], ["/umore"]], resize_keyboard=True)

def time_to_next(random_start: dtime, random_end: dtime) -> float:
    """Return seconds from now to next occurrence inside today's (or tomorrow's) window randomly chosen."""
    now = datetime.now()
    # choose today's date for window start and end
    start_dt = datetime.combine(now.date(), random_start)
    end_dt = datetime.combine(now.date(), random_end)
    # if end already passed, schedule for tomorrow
    if end_dt <= now:
        start_dt += timedelta(days=1)
        end_dt += timedelta(days=1)
    # choose random second between start_dt and end_dt
    span = (end_dt - start_dt).total_seconds()
    if span <= 0:
        return 0
    offset = random.randint(0, int(span))
    target = start_dt + timedelta(seconds=offset)
    return max(0, (target - now).total_seconds())

# ---------------- HANDLERS ----------------
async def start_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    if user_id != OWNER_ID:
        await update.message.reply_text("Questo bot è privato.")
        return
    data = load_data()
    extra = data.get("extra_unlocked", False)
    await update.message.reply_text(f"Ciao {data.get('name','Baby')} 💗 — sono qui.", reply_markup=build_keyboard(extra))

async def handle_text(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    if user_id != OWNER_ID:
        return

    text = update.message.text.strip()
    data = load_data()
    # update last interaction every time user writes
    data["last_interaction"] = datetime.utcnow().isoformat()
    save_data(data)

    # Extra flow
    if text == "Extra 🔐":
        await update.message.reply_text("Inserisci la password per sbloccare l'area Extra:")
        return

    if text == data.get("extra_pass", EXTRA_PASS) or text == EXTRA_PASS:
        data["extra_unlocked"] = True
        save_data(data)
        await update.message.reply_text("Accesso Extra approvato 💗", reply_markup=build_keyboard(True))
        return

    if text.lower() == "foto segreta" or text.lower() == "foto":
        if not data.get("extra_unlocked", False):
            await update.message.reply_text("Devi prima sbloccare l'area Extra.")
            return
        path = random_photo_path()
        if path:
            caption = random.choice(EXTRA_PHOTO_CAPTIONS)
            await update.message.reply_photo(open(path, "rb"), caption=caption)
            data["last_extra_photo"] = datetime.utcnow().isoformat()
            save_data(data)
        else:
            await update.message.reply_text("Nessuna foto disponibile in questo momento.")
        return

    # Secret word triggers playful response
    if text.lower() == SECRET_WORD.lower():
        data["secret_hits"] = data.get("secret_hits", 0) + 1
        save_data(data)
        await update.message.reply_text("Shh… parola segreta riconosciuta. Ho qualcosa solo per te 💫")
        # small surprise: send a random affection message
        await update.message.reply_text(random.choice(DAYTIME_AFFECTION_MSGS))
        return

    # /umore command via text or explicit command handler
    if text.startswith("/umore") or text.lower().startswith("umore"):
        # formats: /umore bene  OR  /umore stanco
        parts = text.split()
        mood = parts[1].lower() if len(parts) > 1 else "bene"
        replies = {
            "bene": f"Che bello sentirlo, {data.get('name','Baby')}! Ti meriti una giornata luminosa ☀️",
            "stanco": "Mi spiace, vorrei abbracciarti forte e farti riposare 💛",
            "triste": "Sono qui con te, sempre. Respiro insieme a te 💕",
            "carico": "Spacca tutto oggi Baby! Sono fiera di te 🔥",
        }
        await update.message.reply_text(replies.get(mood, "Capito. Ti sono vicina ❤️"))
        return

    # default response
    await update.message.reply_text("Ti ascolto Baby… dimmi pure 💗")

# ---------------- SCHEDULED TASKS ----------------
# Each scheduled function will reschedule itself for the next random time
async def send_buongiorno(context: ContextTypes.DEFAULT_TYPE):
    data = load_data()
    data["last_buongiorno"] = datetime.utcnow().isoformat()
    save_data(data)

    path = random_photo_path()
    msg = random.choice(GOOD_MORNING_MSGS)
    if path:
        await context.bot.send_photo(OWNER_ID, open(path, "rb"), caption=msg)
    else:
        await context.bot.send_message(OWNER_ID, msg)

    # schedule a follow-up in 1 hour if no interaction
    def schedule_followup(job_ctx):
        # job will run after 3600s; used placeholder, we schedule below via run_once
        pass

    async def follow_up_check(ctx: ContextTypes.DEFAULT_TYPE):
        d = load_data()
        last_int = d.get("last_interaction")
        last_bu = d.get("last_buongiorno")
        # if last_interaction is None or earlier than last_buongiorno, send gentle nudge
        if last_bu and (not last_int or last_int < last_bu):
            await ctx.bot.send_message(OWNER_ID, "Ehi Baby… ti sei alzato? 💛")
        # after checking, schedule next random morning
        schedule_next_buongiorno(ctx.job.queue)

    # schedule follow up in 3600 seconds (1 hour)
    context.job_queue.run_once(lambda ctx: context.application.create_task(follow_up_check(ctx)), when=3600, name=f"follow_bu_{OWNER_ID}")

async def send_buonanotte(context: ContextTypes.DEFAULT_TYPE):
    data = load_data()
    data["last_buonanotte"] = datetime.utcnow().isoformat()
    save_data(data)

    path = random_photo_path()
    msg = random.choice(GOOD_NIGHT_MSGS)
    if path:
        await context.bot.send_photo(OWNER_ID, open(path, "rb"), caption=msg)
    else:
        await context.bot.send_message(OWNER_ID, msg)

    # schedule next random night
    schedule_next_buonanotte(context.job.queue)

async def send_daytime_affection(context: ContextTypes.DEFAULT_TYPE):
    """Send one daytime affection message and schedule next daytime message within same day window."""
    data = load_data()
    msg = random.choice(DAYTIME_AFFECTION_MSGS)
    await context.bot.send_message(OWNER_ID, msg)
    data["daytime_messages_sent"] = data.get("daytime_messages_sent", 0) + 1
    save_data(data)
    # schedule next daytime affectionate message randomly between 12:00 and 18:00 (once per day)
    # To keep it simple: schedule next in 24h +/- random 0-3h
    delay = 24*3600 + random.randint(-10800, 10800)  # next day +/- 3 hours
    context.job_queue.run_once(lambda ctx: context.application.create_task(send_daytime_affection(ctx)), when=delay, name=f"daytime_{OWNER_ID}")

async def send_extra_photo_job(context: ContextTypes.DEFAULT_TYPE):
    """Send an automatic extra photo every 48-72 hours (approx)."""
    data = load_data()
    path = random_photo_path()
    if path:
        caption = random.choice(EXTRA_PHOTO_CAPTIONS)
        await context.bot.send_photo(OWNER_ID, open(path, "rb"), caption=caption)
        data["last_extra_photo"] = datetime.utcnow().isoformat()
        save_data(data)
    # schedule next in 48-72 hours
    delay = random.randint(48*3600, 72*3600)
    context.job_queue.run_once(lambda ctx: context.application.create_task(send_extra_photo_job(ctx)), when=delay, name=f"extra_photo_{OWNER_ID}")

# ---------------- SCHEDULING HELPERS ----------------
def schedule_next_buongiorno(job_queue):
    seconds = time_to_next(MORNING_WINDOW_START, MORNING_WINDOW_END)
    job_queue.run_once(lambda ctx: ctx.application.create_task(send_buongiorno(ctx)), when=seconds, name=f"buongiorno_{OWNER_ID}")

def schedule_next_buonanotte(job_queue):
    seconds = time_to_next(NIGHT_WINDOW_START, NIGHT_WINDOW_END)
    job_queue.run_once(lambda ctx: ctx.application.create_task(send_buonanotte(ctx)), when=seconds, name=f"buonanotte_{OWNER_ID}")

def schedule_initial_jobs(job_queue):
    # schedule first random morning and night
    schedule_next_buongiorno(job_queue)
    schedule_next_buonanotte(job_queue)
    # schedule daytime affection first occurrence in next few hours (random)
    delay_day = random.randint(2*3600, 8*3600)  # between 2 and 8 hours from now
    job_queue.run_once(lambda ctx: ctx.application.create_task(send_daytime_affection(ctx)), when=delay_day, name=f"daytime_init_{OWNER_ID}")
    # schedule first extra photo
    delay_photo = random.randint(48*3600, 72*3600)
    job_queue.run_once(lambda ctx: ctx.application.create_task(send_extra_photo_job(ctx)), when=delay_photo, name=f"extra_init_{OWNER_ID}")

# ---------------- MAIN ----------------
def main():
    app = ApplicationBuilder().token(BOT_TOKEN).build()

    app.add_handler(CommandHandler("start", start_handler))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_text))

    # schedule initial jobs once app starts
    jq = app.job_queue
    # Note: job_queue exists because requirements include job-queue extra
    schedule_initial_jobs(jq)

    app.run_polling()

if __name__ == "__main__":
    main()
