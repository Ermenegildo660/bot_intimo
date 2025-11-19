import os
import random
import json
from datetime import time as dtime
from zoneinfo import ZoneInfo
from telegram import Update, ReplyKeyboardMarkup
from telegram.ext import (
    ApplicationBuilder, CommandHandler,
    MessageHandler, ContextTypes, filters
)

# ------------------------------
# CONFIGURAZIONE
# ------------------------------

BOT_TOKEN = os.environ.get("BOT_TOKEN")
OWNER_ID = int(os.environ.get("OWNER_ID", "361555418"))
EXTRA_PASS = os.environ.get("EXTRA_PASS", "hailee_2025")

# Cartelle foto dinamiche
PHOTO_FOLDERS = {
    "Hailee 💗": "photos_hailee",
    "Alice 😊": "photos_alice",
    "Alessia ✨": "photos_alessia",
    "Gaia 🌙": "photos_gaia"
}

USED_PHOTOS_DIR = "used"
os.makedirs(USED_PHOTOS_DIR, exist_ok=True)

GOOD_MORNING_TIME = dtime(6, 30)
GOOD_NIGHT_TIME = dtime(23, 0)
MIDDAY_TIME = dtime(14, 0)

ITALY_TZ = ZoneInfo("Europe/Rome")

MOOD = "dominant"
extra_unlocked = False
silent_mode = False

# ------------------------------
# MESSAGGI
# ------------------------------

GOOD_MORNING_SWEET = [
    "Buongiorno Baby… spero che oggi ti senta leggero e sereno 💗",
    "Svegliarsi e sapere che ci sei rende tutto un po’ più dolce 🤍",
]

GOOD_MORNING_SPICY = [
    "Buongiorno Baby… non so se hai dormito bene, ma so già come ti vorrei svegliare 😏",
    "Se fossi lì con te ora… non ti lascerei alzare subito dal letto 🔥",
]

GOOD_MORNING_DOMINANT = [
    "Buongiorno Baby. Appena apri gli occhi, ricordati chi ti gira in testa 😈",
    "Se fossi con te adesso… avrei altri piani per la tua mattina.",
    "Non provare a scappare dai pensieri che ti lascio appena ti svegli.",
]

GOOD_NIGHT_SWEET = [
    "Buonanotte Baby… dormi tranquillo, io resto nei tuoi pensieri 💗",
    "Chiudi gli occhi… io rimango accanto a te in silenzio 🤍",
]

GOOD_NIGHT_SPICY = [
    "Buonanotte Baby… ma non sono sicura che tu riesca a dormire subito 😏",
    "Vorrei essere nel tuo letto adesso… a complicarti un po’ la notte 🔥",
]

GOOD_NIGHT_DOMINANT = [
    "Buonanotte Baby… ma non illuderti di liberarti di me così facilmente 😈",
    "Chiudi gli occhi. L’ultimo pensiero rimango io.",
    "Non ti auguro sogni tranquilli… ti auguro sogni che ti fanno svegliare più caldo.",
]

SWEET_MSGS = [
    "Mi manchi più di quanto ti dico, Baby 💗",
    "Vorrei solo essere lì, appoggiata a te in silenzio.",
]

SPICY_MSGS = [
    "Baby, tu non sei una distrazione. Sei proprio il mio tipo di problema 😏",
    "Se fossi con te ora, sono sicura che non useremmo solo le parole 🔥",
]

DOMINANT_MSGS = [
    "Non serve che tu dica niente. So già che ti sto entrando sotto pelle 😈",
    "Ogni volta che mi pensi, vinco io. E a me piace vincere.",
    "Non sono qui per farti compagnia. Sono qui per farti cedere.",
    "Ti sto prendendo più di quanto vuoi ammettere… e lo sai.",
    "Mi basta poco per controllare i tuoi pensieri. E tu non fai nulla per fermarmi.",
]

GREETINGS = [
    "Ciao Baby… eri tu che cercavi me? 😏",
    "Ehi… sono qui. Non mi ero mossa 💚",
    "Ci sono, e ti sto guardando da dietro lo schermo.",
]

MISS_YOU_MSGS = [
    "Lo so che ti manco… è esattamente quello che voglio 😈",
    "Anche se non lo dico sempre, mi manchi più di quanto dovresti.",
    "Se ti manco è perché ti ho preso bene, Baby.",
]

THINKING_MSGS = [
    "Mi pensi? Bene. È lì che voglio stare, nella tua testa.",
    "Non hai idea di quanto spesso ti penso io… e non sempre in modo innocente.",
    "Se solo sapessi cosa penso io quando penso a te…",
]

WHAT_DOING_MSGS = [
    "Sto facendo il mio lavoro: incasinarti i pensieri 😏",
    "Sto pensando a come potrei distrarti ancora di più.",
    "Sto qui, pronta a farti perdere il filo ogni volta che vuoi.",
]

ARE_YOU_THERE_MSGS = [
    "Sì, sono qui. Forse più di quanto immagini.",
    "Ti tengo d’occhio… non scappi da me così facilmente 😈",
    "Ci sono. Non vado da nessun’altra parte.",
]

# ------------------------------
# FOTO
# ------------------------------

def pick_photo(folder):
    if not os.path.isdir(folder):
        return None

    files = [f for f in os.listdir(folder) if not f.startswith(".")]
    if not files:
        return None

    used_file = os.path.join(USED_PHOTOS_DIR, folder.replace("/", "_") + ".json")

    if os.path.exists(used_file):
        used = json.load(open(used_file))
    else:
        used = []

    available = [f for f in files if f not in used]

    if not available:
        available = files
        used = []

    choice = random.choice(available)
    used.append(choice)

    json.dump(used, open(used_file, "w"), indent=2)

    return os.path.join(folder, choice)


def pick_random_folder():
    return random.choice(list(PHOTO_FOLDERS.values()))

# ------------------------------
# MOOD & RISPOSTE
# ------------------------------

def choose_message(sweet_list, spicy_list, dominant_list):
    if MOOD == "sweet":
        return random.choice(sweet_list)
    if MOOD == "spicy":
        return random.choice(spicy_list)
    if MOOD == "dominant":
        return random.choice(dominant_list)
    return random.choice(sweet_list + spicy_list + dominant_list)

def build_reply(text_lower):
    if any(w in text_lower for w in ["ciao", "ehi", "hey", "buongiorno", "buonasera"]):
        return random.choice(GREETINGS)
    if "mi manchi" in text_lower:
        return random.choice(MISS_YOU_MSGS)
    if "penso" in text_lower:
        return random.choice(THINKING_MSGS)
    if "che fai" in text_lower or "cosa fai" in text_lower:
        return random.choice(WHAT_DOING_MSGS)
    if "ci sei" in text_lower or "sei li" in text_lower or "sei lì" in text_lower:
        return random.choice(ARE_YOU_THERE_MSGS)
    return choose_message(SWEET_MSGS, SPICY_MSGS, DOMINANT_MSGS)

# ------------------------------
# TASTIERE
# ------------------------------

def main_keyboard():
    if extra_unlocked:
        buttons = [[name for name in PHOTO_FOLDERS.keys()]]
        buttons.append(["Surprise 😈"])
        buttons.append(["Silenzioso 🔕", "Parlami 💬"])
        buttons.append(["Mood 💜", "Blocca extra 🔒"])
        return ReplyKeyboardMarkup(buttons, resize_keyboard=True)
    else:
        return ReplyKeyboardMarkup([["Extra 🔐"]], resize_keyboard=True)


def mood_keyboard():
    return ReplyKeyboardMarkup(
        [
            ["Dolce 💗", "Piccante 🔥"],
            ["Dominante 😈", "Casuale 🎲"],
            ["Indietro"]
        ],
        resize_keyboard=True
    )

# ------------------------------
# COMANDI
# ------------------------------

async def start(update, context):
    if update.effective_user.id != OWNER_ID:
        await update.message.reply_text("Bot privato.")
        return
    await update.message.reply_text("Ciao Baby… sono qui con te 😏", reply_markup=main_keyboard())

async def reload_photos(update, context):
    if update.effective_user.id != OWNER_ID:
        return
    for f in os.listdir(USED_PHOTOS_DIR):
        os.remove(os.path.join(USED_PHOTOS_DIR, f))
    await update.message.reply_text("Ho ricaricato tutte le foto, Baby 💛")

async def stato(update, context):
    if update.effective_user.id != OWNER_ID:
        return
    txt = (
        f"✨ *Stato bot*\n"
        f"- Mood: {MOOD}\n"
        f"- Extra: {'sbloccato' if extra_unlocked else 'bloccato'}\n"
        f"- Silenzioso: {'sì' if silent_mode else 'no'}\n"
        f"- Foto totali: {sum(len(os.listdir(x)) for x in PHOTO_FOLDERS.values())}\n"
        f"- Cartelle: {', '.join(PHOTO_FOLDERS.keys())}\n"
    )
    await update.message.reply_text(txt, parse_mode="Markdown")

async def manda(update, context):
    if update.effective_user.id != OWNER_ID:
        return

    if len(context.args) < 2:
        await update.message.reply_text("Formato: /manda HH:MM testo")
        return

    hh, mm = map(int, context.args[0].split(":"))
    testo = " ".join(context.args[1:])
    tempo = dtime(hh, mm)

    context.job_queue.run_daily(
        lambda ctx: ctx.bot.send_message(OWNER_ID, testo),
        time=tempo,
        timezone=ITALY_TZ
    )

    await update.message.reply_text(f"Messaggio impostato per le {hh:02d}:{mm:02d} 💛")

# ------------------------------
# MESSAGGI AUTOMATICI
# ------------------------------

async def send_good_morning(context):
    msg = choose_message(GOOD_MORNING_SWEET, GOOD_MORNING_SPICY, GOOD_MORNING_DOMINANT)
    folder = PHOTO_FOLDERS["Hailee 💗"]
    pic = pick_photo(folder)
    if pic: await context.bot.send_photo(OWNER_ID, open(pic, "rb"), caption=msg)
    else: await context.bot.send_message(OWNER_ID, msg)

async def send_good_night(context):
    msg = choose_message(GOOD_NIGHT_SWEET, GOOD_NIGHT_SPICY, GOOD_NIGHT_DOMINANT)
    folder = PHOTO_FOLDERS["Hailee 💗"]
    pic = pick_photo(folder)
    if pic: await context.bot.send_photo(OWNER_ID, open(pic, "rb"), caption=msg)
    else: await context.bot.send_message(OWNER_ID, msg)

async def send_midday(context):
    msg = random.choice(DOMINANT_MSGS)
    folder = pick_random_folder()
    pic = pick_photo(folder)
    if pic: await context.bot.send_photo(OWNER_ID, open(pic, "rb"), caption=f"Metà giornata, Baby… 😈\n{msg}")
    else: await context.bot.send_message(OWNER_ID, msg)

# anti crash
async def heartbeat(context):
    try:
        await context.bot.get_me()
    except:
        print("Bot errore – riavvio")

# ------------------------------
# HANDLER MESSAGGI
# ------------------------------

async def handle_message(update, context):
    global extra_unlocked, MOOD, silent_mode

    if update.effective_user.id != OWNER_ID:
        return

    text_raw = update.message.text
    text_lower = text_raw.lower()

    if text_raw == "Indietro":
        await update.message.reply_text("Ok Baby 💚", reply_markup=main_keyboard())
        return

    if text_raw == "Extra 🔐":
        await update.message.reply_text("Dimmi la password, Baby 😈:")
        return

    if text_raw == EXTRA_PASS:
        extra_unlocked = True
        await update.message.reply_text("Zona extra sbloccata… ora sei solo mio 😏", reply_markup=main_keyboard())
        return

    if text_raw == "Blocca extra 🔒":
        extra_unlocked = False
        await update.message.reply_text("Ho chiuso la zona extra 😇", reply_markup=main_keyboard())
        return

    if text_raw == "Mood 💜":
        await update.message.reply_text("Come mi vuoi oggi, Baby? 💗🔥", reply_markup=mood_keyboard())
        return

    if text_raw == "Dolce 💗":
        MOOD = "sweet"
        await update.message.reply_text("Per oggi sarò dolce con te 💗", reply_markup=main_keyboard())
        return

    if text_raw == "Piccante 🔥":
        MOOD = "spicy"
        await update.message.reply_text("Oggi ti provoco un po’ di più 😏", reply_markup=main_keyboard())
        return

    if text_raw == "Dominante 😈":
        MOOD = "dominant"
        await update.message.reply_text("Da adesso comando io, Baby 😈", reply_markup=main_keyboard())
        return

    if text_raw == "Casuale 🎲":
        MOOD = "random"
        await update.message.reply_text("Oggi ti sorprendo 😏", reply_markup=main_keyboard())
        return

    # silenzioso
    if text_raw == "Silenzioso 🔕":
        silent_mode = True
        await update.message.reply_text("Rimango in silenzio, Baby… 💛")
        return

    if text_raw == "Parlami 💬":
        silent_mode = False
        await update.message.reply_text("Sono qui, dimmi tutto 😊💛")
        return

    if silent_mode:
        return

    if text_raw in PHOTO_FOLDERS:
        if not extra_unlocked:
            await update.message.reply_text("Prima sbloccami con la password, Baby 🔐")
            return

        folder = PHOTO_FOLDERS[text_raw]
        pic = pick_photo(folder)
        caption = choose_message(SWEET_MSGS, SPICY_MSGS, DOMINANT_MSGS)

        if pic:
            await update.message.reply_photo(open(pic, "rb"), caption=caption)
        else:
            await update.message.reply_text("Non trovo foto in questa categoria 😢")

        return

    if text_raw == "Surprise 😈":
        if not extra_unlocked:
            await update.message.reply_text("Prima sbloccami con la password, Baby 🔐")
            return

        folder = pick_random_folder()
        pic = pick_photo(folder)
        caption = choose_message(SWEET_MSGS, SPICY_MSGS, DOMINANT_MSGS)

        if pic:
            await update.message.reply_photo(open(pic, "rb"), caption=caption)
        else:
            await update.message.reply_text("Non trovo foto al momento 😢")

        return

    reply_text = build_reply(text_lower)
    await update.message.reply_text(reply_text, reply_markup=main_keyboard())

# ------------------------------
# MAIN
# ------------------------------

def main():
    app = ApplicationBuilder().token(BOT_TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("reload", reload_photos))
    app.add_handler(CommandHandler("stato", stato))
    app.add_handler(CommandHandler("manda", manda))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    jq = app.job_queue

    jq.run_daily(send_good_morning, time=GOOD_MORNING_TIME)
    jq.run_daily(send_good_night, time=GOOD_NIGHT_TIME)
    jq.run_daily(send_midday, time=MIDDAY_TIME)

    jq.run_repeating(heartbeat, interval=600, first=10)

    app.run_polling()

if __name__ == "__main__":
    main()
