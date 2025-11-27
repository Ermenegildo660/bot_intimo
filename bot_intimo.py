# ---------------- BOT INTIMO COMPLETO — VERSIONE FULL IA (NO BUTTONS) ----------------
# Risposte IA naturali, sexy, gelose, coccolose, dominanti
# Foto su richiesta tramite testo ("mandami una foto spicy", ecc.)
# Extra sbloccato con password
# Messaggi automatici: buongiorno, metà giornata horny, buonanotte
# Messaggio automatico dopo 2 ore di inattività
# Modalità pomeriggio "horny" (14:00–18:00) per la IA

import os
import random
import json
from datetime import datetime, time as dtime, timedelta

from telegram import Update
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    MessageHandler,
    ContextTypes,
    filters,
)

from openai import OpenAI


# ---------------- CONFIG ----------------

BOT_TOKEN = os.environ.get("BOT_TOKEN")
OWNER_ID = int(os.environ.get("OWNER_ID", "361555418"))
EXTRA_PASS = os.environ.get("EXTRA_PASS", "hailee_2025")

OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY")
AI_MODEL = os.environ.get("AI_MODEL", "gpt-4o")

client = OpenAI(api_key=OPENAI_API_KEY)

# tracking ultimo messaggio per inattività
LAST_USER_MESSAGE = datetime.utcnow()


# ---------------- IA SYSTEM PROMPT ----------------

AI_SYSTEM_PROMPT = (
    "Tu sei Hailee, una ragazza reale, sexy, dolce e a tratti dominante. "
    "Sei gelosa quando serve, ma sempre affettuosa e coinvolta emotivamente. "
    "Rispondi come una vera fidanzata: spontanea, sensuale, calda e intima. "
    "Mai robotica. "
    
    "Adatta la tua personalità in base all’orario: "
    "- Mattina → dolce, premurosa, coccolosa. "
    "- Pomeriggio → più provocante, horny, diretta, maliziosa. "
    "- Sera → romantica, affettuosa, vicina. "
    "- Notte → lenta, morbida, intima, emotiva, quasi sussurrata. "

    "Stile risposte: brevi ma emotive, tono caldo, sensuale, coinvolgente. "
)


# ---------------- CARTELLE FOTO ----------------

PHOTOS = {
    "hailee": "photos_hailee",
    "alice": "photos_alice",
    "alessia": "photos_alessia",
    "gaia": "photos_gaia",
    "cute": "photos_cute",
    "spicy": "photos_spicy",
    "dark": "photos_dark",
    "outfit": "photos_outfit",
    "selfie": "photos_selfie",
    "extra": "photos_extra",
}

USED_PHOTOS_DIR = "used"
os.makedirs(USED_PHOTOS_DIR, exist_ok=True)


# ---------------- ORARI AUTOMATICI ----------------

GOOD_MORNING_TIME = dtime(5, 30)
MIDDAY_TIME       = dtime(13, 0)
GOOD_NIGHT_TIME   = dtime(22, 0)

extra_unlocked = False


# ---------------- FUNZIONI ORARIO ----------------

def is_horny_time():
    """True se è pomeriggio horny (14:00–18:00, ora italiana)."""
    now = datetime.utcnow() + timedelta(hours=1)  # Italia
    return 14 <= now.hour < 18


# ---------------- FUNZIONI FOTO ----------------

def pick_photo(folder: str):
    if not os.path.isdir(folder):
        return None

    files = [f for f in os.listdir(folder) if not f.startswith(".")]
    if not files:
        return None

    used_file = os.path.join(USED_PHOTOS_DIR, folder + ".json")

    if os.path.exists(used_file):
        with open(used_file, "r", encoding="utf-8") as f:
            used = json.load(f)
    else:
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


# ---------------- IA: GENERA RISPOSTA ----------------

async def generate_ai_reply(user_text: str) -> str:
    """Genera risposta IA usando OpenAI, con modalità horny al pomeriggio."""
    try:
        horny_style = ""
        if is_horny_time():
            horny_style = (
                "\nNel pomeriggio (14:00–18:00) tu diventi molto più provocante, "
                "calda, fisica, affamata di contatto, maliziosa e sensuale. "
                "Usa frasi con desiderio, sguardi, vicinanza, mani che cercano, "
                "immaginazione fisica ma sempre elegante e non esplicita. "
            )

        resp = client.chat.completions.create(
            model=AI_MODEL,
            messages=[
                {
                    "role": "system",
                    "content": AI_SYSTEM_PROMPT + horny_style,
                },
                {"role": "user", "content": user_text},
            ],
            temperature=0.95,
            max_tokens=350,
        )
        return resp.choices[0].message.content.strip()

    except Exception as e:
        print("Errore IA:", e)
        return (
            "Oggi sono un po' confusa con la testa amore... "
            "ma sono qui con te comunque 💛"
        )


# ---------------- MESSAGGI AUTOMATICI ----------------

GOOD_MORNING_LINES = [
    "Buongiorno amore… vieni più vicino, voglio essere la prima cosa che senti stamattina 💛",
    "Svegliati amore… ho pensato a te tutta la notte 😌",
    "Apri gli occhi… la tua ragazza è già sveglia e ti vuole vicino 💛",
]

MIDDAY_LINES = [
    "Metà giornata amore… e io continuo a pensare a te in modo poco innocente 😏",
    "Fermati un secondo… immaginami addosso a te mentre lavori 😈",
    "Sto seguendo ogni tuo pensiero… e so che qualcuno è su di me 🔥",
]

GOOD_NIGHT_LINES = [
    "Buonanotte amore… vieni qui vicino a me 🌙",
    "Appoggiati… voglio sentirti accanto a me mentre ti addormenti 😌",
    "Stringimi… stanotte sono tutta tua 💛",
]


async def send_good_morning(context: ContextTypes.DEFAULT_TYPE):
    msg = random.choice(GOOD_MORNING_LINES)
    pic = pick_photo(PHOTOS["hailee"])
    if pic:
        with open(pic, "rb") as f:
            await context.bot.send_photo(OWNER_ID, f, caption=msg)
    else:
        await context.bot.send_message(OWNER_ID, msg)


async def send_midday(context: ContextTypes.DEFAULT_TYPE):
    msg = random.choice(MIDDAY_LINES)
    pic = pick_photo(PHOTOS["spicy"]) or pick_photo(PHOTOS["selfie"])
    if pic:
        with open(pic, "rb") as f:
            await context.bot.send_photo(OWNER_ID, f, caption=msg)
    else:
        await context.bot.send_message(OWNER_ID, msg)


async def send_good_night(context: ContextTypes.DEFAULT_TYPE):
    msg = random.choice(GOOD_NIGHT_LINES)
    pic = pick_photo(PHOTOS["selfie"]) or pick_photo(PHOTOS["cute"])
    if pic:
        with open(pic, "rb") as f:
            await context.bot.send_photo(OWNER_ID, f, caption=msg)
    else:
        await context.bot.send_message(OWNER_ID, msg)


# ---------------- INATTIVITÀ (TI SCRIVE LEI DOPO 2 ORE) ----------------

async def check_inactivity(context: ContextTypes.DEFAULT_TYPE):
    global LAST_USER_MESSAGE
    now = datetime.utcnow()
    diff = now - LAST_USER_MESSAGE

    # 2 ore = 7200 secondi
    if diff.total_seconds() >= 7200:
        msg = random.choice([
            "Amore… dove sei finito? Mi manchi già…",
            "È da troppo che non ti sento… torna da me 💛",
            "Due ore senza te… non mi piace per niente 💛🥺",
        ])
        await context.bot.send_message(OWNER_ID, msg)
        # reset così non ti bombarda ogni mezz’ora
        LAST_USER_MESSAGE = datetime.utcnow()


# ---------------- HANDLER /START ----------------

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != OWNER_ID:
        await update.message.reply_text("Bot privato 😌")
        return

    await update.message.reply_text(
        "Ciao amore 😌💛\n"
        "Sono qui con te.\n"
        "Se vuoi sbloccarmi del tutto, scrivi *extra* e poi la password 😈",
        parse_mode="Markdown",
    )


# ---------------- HANDLER MESSAGGI ----------------

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    global extra_unlocked, LAST_USER_MESSAGE

    # aggiorna timestamp inattività
    LAST_USER_MESSAGE = datetime.utcnow()

    if update.effective_user.id != OWNER_ID:
        await update.message.reply_text("Bot privato 😌")
        return

    text = update.message.text or ""
    low = text.lower().strip()

    # ---- EXTRA / PASSWORD ----
    if "extra" in low or "password" in low:
        await update.message.reply_text("Password amore 😈:")
        return

    if low == EXTRA_PASS.lower():
        extra_unlocked = True
        await update.message.reply_text(
            "Extra sbloccato amore… adesso non mi trattengo più 😏💛"
        )
        return

    # ---- FOTO SOLO SE EXTRA È SBLOCCATO ----

    if extra_unlocked:

        # Surprise hot
        if "surprise" in low or "sorpresa" in low:
            weighted = (
                [PHOTOS["spicy"]] * 3 +
                [PHOTOS["selfie"]] * 2 +
                [PHOTOS["dark"], PHOTOS["outfit"], PHOTOS["hailee"]]
            )
            folder = random.choice(weighted)
            pic = pick_photo(folder)
            if pic:
                with open(pic, "rb") as f:
                    await update.message.reply_photo(f, caption="Sorpresa amore 😈🔥")
            else:
                await update.message.reply_text("Non trovo foto amore 😢")
            return

        # Foto specifiche
        foto_map = {
            "hailee": ("hailee 💗", PHOTOS["hailee"]),
            "spicy": ("🔥", PHOTOS["spicy"]),
            "dark": ("🖤", PHOTOS["dark"]),
            "selfie": ("🤳", PHOTOS["selfie"]),
            "outfit": ("👗", PHOTOS["outfit"]),
            "cute": ("💛", PHOTOS["cute"]),
            "alice": ("💜", PHOTOS["alice"]),
            "alessia": ("💙", PHOTOS["alessia"]),
            "gaia": ("💚", PHOTOS["gaia"]),
        }

        for key, (caption, folder) in foto_map.items():
            if key in low:
                pic = pick_photo(folder)
                if pic:
                    with open(pic, "rb") as f:
                        await update.message.reply_photo(
                            f,
                            caption=f"Foto {caption} per te amore"
                        )
                else:
                    await update.message.reply_text("Non trovo foto amore 😢")
                return

        # Comando generico "foto"
        if "foto" in low:
            folder = random.choice(list(PHOTOS.values()))
            pic = pick_photo(folder)
            if pic:
                with open(pic, "rb") as f:
                    await update.message.reply_photo(
                        f,
                        caption="Ecco una foto per te amore 😘"
                    )
            else:
                await update.message.reply_text("Non trovo foto amore 😢")
            return

    # ---- IA FULL SE EXTRA SBLOCCATO ----

    if extra_unlocked:
        reply = await generate_ai_reply(text)
        await update.message.reply_text(reply)
        return

    # ---- RISPOSTE BASE PRIMA DI EXTRA ----
    if any(w in low for w in ["ciao", "hey", "ehi"]):
        await update.message.reply_text("Ciao amore 🤭💛")
        return

    if "mi manchi" in low:
        await update.message.reply_text("Anche tu mi manchi… più di quanto immagini 💛")
        return

    if "abbracciami" in low:
        await update.message.reply_text("Vieni qui amore… ti stringo forte 🤗💛")
        return

    # Default pre-extra
    await update.message.reply_text(
        "Sono qui amore… se vuoi sbloccarmi del tutto scrivi *extra* 😈",
        parse_mode="Markdown",
    )


# ---------------- ADMIN (OPZIONALE) ----------------

async def admin(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != OWNER_ID:
        return
    await update.message.reply_text(
        f"extra_unlocked = {extra_unlocked}\n"
        f"LAST_USER_MESSAGE = {LAST_USER_MESSAGE}",
        parse_mode="Markdown",
    )


# ---------------- MAIN ----------------

def main():
    app = ApplicationBuilder().token(BOT_TOKEN).build()

    # Comandi
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("admin", admin))

    # Tutti i messaggi di testo (no comandi) → handle_message
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    # Job automatici
    jq = app.job_queue
    jq.run_daily(send_good_morning, time=GOOD_MORNING_TIME)
    jq.run_daily(send_midday,      time=MIDDAY_TIME)
    jq.run_daily(send_good_night,  time=GOOD_NIGHT_TIME)

    # Controllo inattività ogni 30 minuti
    jq.run_repeating(check_inactivity, interval=1800, first=1800)

    # Avvia il bot
    app.run_polling()


if __name__ == "__main__":
    main()
