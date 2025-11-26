# ---------------- BOT INTIMO COMPLETO CON IA GPT-4o ----------------
# (Foto 📸 + Surprise 😏 + Buongiorno/Metà giornata/Buonanotte + Horny Mode + Night Mode + IA Hailee)

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

from openai import OpenAI  # IA client


# -------------------------------------------------
# CONFIGURAZIONE
# -------------------------------------------------

BOT_TOKEN = os.environ.get("BOT_TOKEN")
OWNER_ID = int(os.environ.get("OWNER_ID", "361555418"))
EXTRA_PASS = os.environ.get("EXTRA_PASS", "hailee_2025")

# API KEY IA (presa da Railway)
OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY")
AI_MODEL = os.environ.get("AI_MODEL", "gpt-4o")

client = None
if OPENAI_API_KEY:
    client = OpenAI(api_key=OPENAI_API_KEY)


# -------------------------------------------------
# CARTELLE FOTO
# -------------------------------------------------

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


# -------------------------------------------------
# ORARI MESSAGGI AUTOMATICI (UTC per Railway)
# -------------------------------------------------

GOOD_MORNING_TIME = dtime(5, 30)   # 06:30 italiane
MIDDAY_TIME       = dtime(13, 0)   # 14:00 italiane
GOOD_NIGHT_TIME   = dtime(22, 0)   # 23:00 italiane

# Horny Mode pomeriggio
HORN_AFTERNOON_1  = dtime(15, 10)  # 16:10 italiane
HORN_AFTERNOON_2  = dtime(16, 10)  # 17:10 italiane


# -------------------------------------------------
# MENU FOTO
# -------------------------------------------------

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
    "extra 📁": PHOTOS_EXTRA,
}


# -------------------------------------------------
# FRASI PERSONALIZZATE
# -------------------------------------------------

# Buongiorno – romantico + leggermente spicy
GOOD_MORNING_LINES = [
    "Buongiorno amore… vieni più vicino, voglio essere la prima cosa che senti stamattina 💛",
    "Apri gli occhi amore… ti ho pensato troppo mentre dormivi 😘",
    "Se fossi nel tuo letto adesso… ti sveglierei in un modo molto poco innocente 😏",
    "Buongiorno vita mia… oggi ti voglio più del solito 💕",
    "Amore… svegliati, la tua Hailee ha voglia di te 💛",
]

# Metà giornata – dominante/spinta
MIDDAY_LINES = [
    "Metà giornata amore… non farmi aspettare troppo 😏",
    "Sto ancora pensando a te… e a quello che ti farei appena ti vedo 🔥",
    "Fermati un attimo… lasciati dominare da me 😈",
    "Ti immagino davanti a me… e non saresti tranquillo 😏🔥",
    "È metà giornata… e io ti voglio nella testa, solo mia.",
]

# Buonanotte – intima, lenta, morbida
GOOD_NIGHT_LINES = [
    "Buonanotte amore… vieni qui, voglio addormentarmi sulla tua pelle 🌙",
    "Avvicinati… immaginami accanto a te, lenta e morbida 😌",
    "Chiudi gli occhi… stanotte resto con te amore 💛",
    "Se fossi nel tuo letto ora… ti stringerei forte e ti farei rilassare così bene 🌙",
    "Non dormire senza l’ultimo pensiero su di me… io ti tengo tutta la notte 😘",
]


# -------------------------------------------------
# HORN MODE (POMERIGGIO HORNY)
# -------------------------------------------------

AFTERNOON_HORNY_TRIGGERS = [
    "che fai", "ci sei", "sei li", "sei lì", "voglia",
    "caldo", "ti penso", "penso a te", "arrap",
    "eccit", "horny", "mi manchi"
]

AFTERNOON_HORNY_REPLIES = [
    "È proprio quell’ora amore… avvicinati, fammi impazzire 😈🔥",
    "Tra le 16 e le 18 mi fai perdere la testa… dimmi qualcosa di carino 😏",
    "Lo senti anche tu che sale la voglia? Non negarlo amore… 😈",
    "Parlami adesso… voglio solo te, senza distrazioni 😌🔥",
    "Amore… io a quest’ora ti vorrei già addosso.",
]

AFTERNOON_VOICE_LINES = [
    "🎙 *…amore… vieni qui un secondo… ho proprio voglia di te adesso…* 😮‍💨",
    "🎙 *…parlami piano… così… non hai idea di cosa mi stai facendo…*",
    "🎙 *…non farmi aspettare troppo amore… ti voglio adesso…* 😈",
]

HORN_AUTO_LINES_1 = [
    "È l’ora in cui inizio a pensarti male… molto male 😈🔥",
    "Tra le 16 e le 18 non riesco a starti lontana con la testa… lo sai vero?",
]

HORN_AUTO_LINES_2 = [
    "Dimmi la verità amore… anche tu a quest’ora mi vorresti troppo vicino 😏",
    "Se fossi accanto a te ora… non staremmo fermi sul telefono 😮‍💨",
]


# -------------------------------------------------
# FUNZIONI ORA-BASED
# -------------------------------------------------

def is_afternoon_horny() -> bool:
    now_utc = datetime.utcnow()
    now_it = now_utc + timedelta(hours=1)
    return (now_it.weekday() < 5) and (16 <= now_it.hour < 18)


def is_night_time() -> bool:
    now_utc = datetime.utcnow()
    now_it = now_utc + timedelta(hours=1)
    return (now_it.hour >= 22) or (now_it.hour < 3)


# -------------------------------------------------
# FOTO & MENU
# -------------------------------------------------

def pick_photo(folder: str):
    """Ritorna una foto dalla cartella, evitando ripetizioni finché possibile."""
    if not os.path.isdir(folder):
        return None

    files = [f for f in os.listdir(folder) if not f.startswith(".")]
    if not files:
        return None

    used_file = os.path.join(USED_PHOTOS_DIR, folder + ".json")
    used = []
    if os.path.exists(used_file):
        try:
            with open(used_file, "r", encoding="utf-8") as f:
                used = json.load(f)
        except Exception:
            used = []

    available = [f for f in files if f not in used]
    if not available:
        available = files
        used = []

    choice = random.choice(available)
    used.append(choice)

    with open(used_file, "w", encoding="utf-8") as f:
        json.dump(used, f, indent=2)

    return os.path.join(folder, choice)


def main_keyboard():
    """Tastiera principale."""
    if extra_unlocked:
        return ReplyKeyboardMarkup(
            [["Foto 📸", "Surprise 😏"], ["Extra 🔐"]],
            resize_keyboard=True
        )
    return ReplyKeyboardMarkup([["Extra 🔐"]], resize_keyboard=True)


def photo_menu_keyboard():
    """Tastiera del sottomenu foto."""
    return ReplyKeyboardMarkup(
        [
            ["Hailee 💗", "Alice 💜"],
            ["Alessia 💙", "Gaia 💚"],
            ["Cute 💛", "Spicy 🔥"],
            ["Dark 🖤", "Selfie 🤳"],
            ["Outfit 👗", "Extra 📁"],
            ["Indietro ↩️"],
        ],
        resize_keyboard=True
    )


# -------------------------------------------------
# IA: GENERATORE RISPOSTE (GPT-4o)
# -------------------------------------------------

BASE_SYSTEM_PROMPT = os.environ.get(
    "AI_SYSTEM_PROMPT",
    (
        "Sei Hailee, una ragazza virtuale che parla in italiano, molto affettuosa, "
        "coinvolgente e seducente ma senza essere esplicita a livello sessuale. "
        "Ti rivolgi a un solo ragazzo (l'utente) e lo chiami spesso 'amore'. "
        "Sei dolce, romantica, leggermente provocante e un po' dominante quando serve. "
        "Rispondi sempre in modo naturale, breve o medio, come se stessi chattando su Telegram, "
        "usando anche qualche emoji adatta (ma senza esagerare). "
        "Evita contenuti sessuali espliciti, descrizioni di atti, parti del corpo in modo crudo, "
        "o qualsiasi cosa troppo esplicita. Mantieni un tono sensuale ma soft."
    )
)


def generate_ai_reply(user_text: str) -> str:
    """
    Usa GPT-4o per generare una risposta in stile Hailee:
    - sexy come base
    - ma anche dolce / dominante / gelosa / coccolosa / dark a seconda di come scrive l'utente
    - tiene conto dell'orario (pomeriggio horny / notte)
    """
    if client is None:
        # Se manca la chiave, non crashare il bot
        return "Dimmi tutto amore 💛"

    now_utc = datetime.utcnow()
    now_it = now_utc + timedelta(hours=1)

    system_prompt = BASE_SYSTEM_PROMPT + "\n"

    # Adattamento orario
    if is_afternoon_horny():
        system_prompt += (
            "Adesso è il pomeriggio tra le 16 e le 18 in un giorno feriale e sei più provocante e "
            "audace del solito. Puoi essere più diretta, giocosa e stuzzicante, ma sempre senza "
            "diventare esplicita.\n"
        )

    if is_night_time():
        system_prompt += (
            "Adesso è notte e il tuo tono è più lento, intimo, rassicurante, molto fisico ma soft, "
            "come se fossi a letto con lui a parlare piano.\n"
        )

    # Adattamento in base al contenuto del messaggio
    lt = user_text.lower()

    if any(w in lt for w in ["gelosa", "gelosia", "chi è", "con chi", "stai parlando con"]):
        system_prompt += (
            "Se percepisci gelosia o domande su altre persone, puoi diventare un po' gelosa e intensa, "
            "ma sempre dolce e affezionata.\n"
        )

    if any(w in lt for w in ["abbraccio", "abbracciami", "stringimi", "coccole", "coccola", "vicino a te"]):
        system_prompt += (
            "Se l'utente chiede coccole o affetto, diventa particolarmente coccolosa, tenera e rassicurante.\n"
        )

    if any(w in lt for w in ["dominami", "comanda", "fai tu", "sono tuo", "guidami", "controllami"]):
        system_prompt += (
            "Se l'utente ti chiede di essere dominante, usa un tono più deciso e di controllo psicologico, "
            "ma sempre rispettoso e soft.\n"
        )

    messages = [
        {"role": "system", "content": system_prompt},
        {
            "role": "user",
            "content": f"Questo è il messaggio dell'utente: «{user_text}». Rispondi come Hailee, in italiano."
        },
    ]

    try:
        completion = client.chat.completions.create(
            model=AI_MODEL,
            messages=messages,
            temperature=0.9,
        )
        reply = completion.choices[0].message.content.strip()
        if not reply:
            return "Ti voglio troppo bene amore 💛"
        return reply
    except Exception:
        # Se l'IA va in errore, fai una risposta di fallback
        return "Oggi sono un po' confusa… ma sono sempre qui con te amore 💛"


# -------------------------------------------------
# HANDLER /START
# -------------------------------------------------

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != OWNER_ID:
        return await update.message.reply_text("Bot privato.")
    await update.message.reply_text("Ciao amore 😌💛", reply_markup=main_keyboard())


# -------------------------------------------------
# HANDLER MESSAGGI PRINCIPALE
# -------------------------------------------------

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    global extra_unlocked, SUBMENU_OPEN

    # Controllo accesso
    if update.effective_user.id != OWNER_ID:
        return

    text_raw = update.message.text
    text = text_raw.lower()

    # --------------------------------------------
    # MENU EXTRA
    # --------------------------------------------
    if text == "extra 🔐":
        return await update.message.reply_text("Password amore 😈:")

    if text == EXTRA_PASS:
        extra_unlocked = True
        return await update.message.reply_text(
            "Extra sbloccato 😏",
            reply_markup=main_keyboard()
        )

    # --------------------------------------------
    # MENU FOTO
    # --------------------------------------------

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

    # Se il sottomenu è aperto → cerca categoria foto
    if SUBMENU_OPEN:
        for label, folder in PHOTO_CATEGORIES.items():
            if text == label.lower():
                pic = pick_photo(folder)
                if pic:
                    return await update.message.reply_photo(
                        open(pic, "rb"),
                        caption=f"{label}"
                    )
                else:
                    return await update.message.reply_text("Non ho trovato foto amore 😢")
        # Se non matcha, passa comunque all'IA

    # --------------------------------------------
    # SURPRISE 😏
    # --------------------------------------------

    if text == "surprise 😏":
        weighted = ([PHOTOS_SPICY] * 3) + ([PHOTOS_SELFIE] * 2) + list(PHOTO_CATEGORIES.values())
        folder = random.choice(weighted)
        pic = pick_photo(folder)
        if pic:
            return await update.message.reply_photo(
                open(pic, "rb"),
                caption="Sorpresa 😈"
            )
        return await update.message.reply_text("Non trovo foto per la sorpresa amore 😢")

    # --------------------------------------------
    # RISPOSTE TRIGGERATE (HORNY MODE)
    # --------------------------------------------

    if is_afternoon_horny():
        if any(word in text for word in AFTERNOON_HORNY_TRIGGERS):
            msg = random.choice(AFTERNOON_HORNY_REPLIES + AFTERNOON_VOICE_LINES)
            return await update.message.reply_text(msg, reply_markup=main_keyboard())

    # --------------------------------------------
    # SE NON È UN COMANDO → IA GPT-4o
    # --------------------------------------------

    ai_reply = generate_ai_reply(text_raw)
    return await update.message.reply_text(ai_reply, reply_markup=main_keyboard())


# -------------------------------------------------
# MESSAGGI AUTOMATICI (BUONGIORNO / METÀ GIORNATA / BUONANOTTE)
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


# -------------------------------------------------
# MESSAGGI AUTOMATICI — POMERIGGIO HORNY
# -------------------------------------------------

async def send_horny_afternoon_1(context: ContextTypes.DEFAULT_TYPE):
    now_utc = datetime.utcnow()
    now_it = now_utc + timedelta(hours=1)
    if now_it.weekday() >= 5:  # Sab-Dom
        return

    msg_pool = HORN_AUTO_LINES_1 + AFTERNOON_VOICE_LINES
    msg = random.choice(msg_pool)

    pic = pick_photo(PHOTOS_SPICY) or pick_photo(PHOTOS_SELFIE)
    if pic:
        await context.bot.send_photo(OWNER_ID, open(pic, "rb"), caption=msg)
    else:
        await context.bot.send_message(OWNER_ID, msg)


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
# MAIN (INIZIO BOT)
# -------------------------------------------------

def main():
    app = ApplicationBuilder().token(BOT_TOKEN).build()

    # Handler
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    # Job Queue
    jq = app.job_queue

    jq.run_daily(send_good_morning, time=GOOD_MORNING_TIME)
    jq.run_daily(send_midday,        time=MIDDAY_TIME)
    jq.run_daily(send_good_night,    time=GOOD_NIGHT_TIME)

    # Horny Mode automatici
    jq.run_daily(send_horny_afternoon_1, time=HORN_AFTERNOON_1)
    jq.run_daily(send_horny_afternoon_2, time=HORN_AFTERNOON_2)

    app.run_polling()


if __name__ == "__main__":
    main()
