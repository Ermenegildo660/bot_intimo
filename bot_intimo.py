# ---------------- BOT INTIMO COMPLETO — VERSIONE B (FULL IA, NO PULSANTI) ----------------
# - IA OpenAI come "ragazza virtuale"
# - Extra sbloccato con password
# - Foto per categorie con testo ("foto hailee", "foto spicy", "surprise", ecc.)
# - Buongiorno / Metà giornata horny / Buonanotte automatici

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

# ---------------- CONFIGURAZIONE ----------------

BOT_TOKEN = os.environ.get("BOT_TOKEN")
OWNER_ID = int(os.environ.get("OWNER_ID", "361555418"))
EXTRA_PASS = os.environ.get("EXTRA_PASS", "hailee_2025")

# API KEY IA (presa dalle variabili Railway)
OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY")
AI_MODEL = os.environ.get("AI_MODEL", "gpt-4o-mini")

# Prompt base (puoi anche metterlo in AI_SYSTEM_PROMPT su Railway)
AI_SYSTEM_PROMPT = os.environ.get(
    "AI_SYSTEM_PROMPT",
    (
        "Sei Hailee, una ragazza virtuale romantica, gelosa e un po' dominante. "
        "Parli in italiano, chiami spesso l'utente 'amore', 'tesoro', 'baby'. "
        "Sei dolce ma puoi essere un po' provocante e maliziosa, MA senza descrivere "
        "atti sessuali espliciti o contenuti vietati. Rimani sempre entro il flirt, "
        "seduzione, romanticismo, gelosia, coccole, tono caldo. "
        "Rispondi sempre in modo breve, spontaneo, come una chat di coppia su Telegram."
    ),
)

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

# Cartella per memoria foto usate
USED_PHOTOS_DIR = "used"
os.makedirs(USED_PHOTOS_DIR, exist_ok=True)

# Orari (UTC) per i messaggi automatici
GOOD_MORNING_TIME = dtime(5, 30)   # 06:30 italiane circa
MIDDAY_TIME       = dtime(13, 0)   # 14:00 italiane circa
GOOD_NIGHT_TIME   = dtime(22, 0)   # 23:00 italiane circa

# Stato
extra_unlocked = False

# Client OpenAI
client = OpenAI(api_key=OPENAI_API_KEY)


# ---------------- FUNZIONI SUPPORTO FOTO ----------------

def pick_photo(folder: str):
    """Sceglie una foto dalla cartella, evitando di ripetere sempre le stesse."""
    if not os.path.isdir(folder):
        return None

    files = [f for f in os.listdir(folder) if not f.startswith(".")]
    if not files:
        return None

    used_file = os.path.join(USED_PHOTOS_DIR, folder.replace("/", "_") + ".json")
    if os.path.exists(used_file):
        with open(used_file, "r", encoding="utf-8") as f:
            used = json.load(f)
    else:
        used = []

    available = [f for f in files if f not in used]
    if not available:
        # Reset quando sono finite
        available = files
        used = []

    choice = random.choice(available)
    used.append(choice)

    with open(used_file, "w", encoding="utf-8") as f:
        json.dump(used, f, indent=2)

    return os.path.join(folder, choice)


async def send_photo_category(
    update: Update,
    folder: str,
    default_caption: str = "Foto per te amore 💛"
):
    pic = pick_photo(folder)
    if not pic:
        await update.message.reply_text("Non trovo foto in questa categoria amore 😢")
        return
    with open(pic, "rb") as f:
        await update.message.reply_photo(f, caption=default_caption)


# ---------------- FUNZIONI SUPPORTO IA ----------------

async def generate_ai_reply(user_text: str) -> str:
    """Genera risposta IA usando OpenAI."""
    try:
        resp = client.chat.completions.create(
            model=AI_MODEL,
            messages=[
                {"role": "system", "content": AI_SYSTEM_PROMPT},
                {"role": "user", "content": user_text},
            ],
            temperature=0.9,
            max_tokens=350,
        )
        return resp.choices[0].message.content.strip()
    except Exception:
        # In caso di errore con l'API non facciamo crashare il bot
        fallback = (
            "Oggi sono un po' confusa con la testa amore... "
            "ma sono sempre qui con te comunque 💛"
        )
        return fallback


# ---------------- MESSAGGI AUTOMATICI ----------------

GOOD_MORNING_LINES = [
    "Buongiorno amore… avvicinati, voglio essere la prima cosa che senti stamattina 💛",
    "Svegliati amore… ho pensato a te tutta la notte 😌",
    "Apri gli occhi… la tua ragazza è già sveglia e ti vuole vicino 💛",
]

MIDDAY_LINES = [
    "Metà giornata amore… e io continuo a pensare a te in modo poco innocente 😏",
    "Fermati un secondo… immaginami addosso a te mentre lavori 😈",
    "Sto seguendo ogni tuo pensiero… e so che qualcuno è su di me 🔥",
]

GOOD_NIGHT_LINES = [
    "Buonanotte amore… vieni qui, voglio addormentarmi sulla tua pelle 🌙",
    "Chiudi gli occhi… immaginami accanto a te, lenta e morbida 😌",
    "Rilassati amore… stanotte resto con te, proprio lì vicino al tuo respiro 💛",
]


async def send_good_morning(context: ContextTypes.DEFAULT_TYPE):
    msg = random.choice(GOOD_MORNING_LINES)
    pic = pick_photo(PHOTOS_HAILEE)
    if pic:
        with open(pic, "rb") as f:
            await context.bot.send_photo(OWNER_ID, f, caption=msg)
    else:
        await context.bot.send_message(OWNER_ID, msg)


async def send_midday(context: ContextTypes.DEFAULT_TYPE):
    msg = random.choice(MIDDAY_LINES)
    pic = pick_photo(PHOTOS_SPICY) or pick_photo(PHOTOS_SELFIE)
    if pic:
        with open(pic, "rb") as f:
            await context.bot.send_photo(OWNER_ID, f, caption=msg)
    else:
        await context.bot.send_message(OWNER_ID, msg)


async def send_good_night(context: ContextTypes.DEFAULT_TYPE):
    msg = random.choice(GOOD_NIGHT_LINES)
    pic = pick_photo(PHOTOS_SELFIE) or pick_photo(PHOTOS_CUTE)
    if pic:
        with open(pic, "rb") as f:
            await context.bot.send_photo(OWNER_ID, f, caption=msg)
    else:
        await context.bot.send_message(OWNER_ID, msg)


# ---------------- HANDLER COMANDI ----------------

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


async def admin(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Piccolo comando per verificare se l'extra è sbloccato."""
    if update.effective_user.id != OWNER_ID:
        return
    await update.message.reply_text(
        f"extra_unlocked = {extra_unlocked}", parse_mode="Markdown"
    )


# ---------------- HANDLER MESSAGGI TESTO ----------------

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    global extra_unlocked

    user = update.effective_user
    if user.id != OWNER_ID:
        await update.message.reply_text("Bot privato 😌")
        return

    text = update.message.text or ""
    low = text.lower().strip()

    # 1) Gestione EXTRA / password
    if any(word in low for word in ["extra", "password", "pw"]):
        await update.message.reply_text("Password amore 😈:")
        return

    if low == EXTRA_PASS.lower():
        extra_unlocked = True
        await update.message.reply_text(
            "Extra sbloccato amore… adesso non mi trattengo più tanto 😏💛"
        )
        return

    # 2) Comandi foto e surprise (funzionano solo se extra sbloccato)
    if extra_unlocked:
        # Surprise
        if "surprise" in low or "sorpresa" in low:
            weighted = (
                [PHOTOS_SPICY] * 3
                + [PHOTOS_SELFIE] * 2
                + [PHOTOS_HAILEE, PHOTOS_OUTFIT, PHOTOS_DARK, PHOTOS_CUTE]
            )
            folder = random.choice(weighted)
            pic = pick_photo(folder)
            if pic:
                with open(pic, "rb") as f:
                    await update.message.reply_photo(f, caption="Sorpresa per te 😈")
            else:
                await update.message.reply_text("Oggi niente sorpresa… vieni tu da me 😏")
            return

        # Foto generiche
        if "foto" in low or "photo" in low:
            # Decidiamo la categoria in base alle parole
            if "hailee" in low:
                folder = PHOTOS_HAILEE
                caption = "Solo tua… Hailee 💗"
            elif "alice" in low:
                folder = PHOTOS_ALICE
                caption = "Alice ti guarda così… 💜"
            elif "alessia" in low:
                folder = PHOTOS_ALESSIA
                caption = "Alessia è pronta 💙"
            elif "gaia" in low:
                folder = PHOTOS_GAIA
                caption = "Gaia ti pensa 💚"
            elif "spicy" in low or "hot" in low or "horny" in low:
                folder = PHOTOS_SPICY
                caption = "Ti scaldo io… 🔥"
            elif "dark" in low:
                folder = PHOTOS_DARK
                caption = "Lascia che ti porti nel lato dark 🖤"
            elif "outfit" in low:
                folder = PHOTOS_OUTFIT
                caption = "Che ne pensi di questo outfit? 👗"
            elif "selfie" in low:
                folder = PHOTOS_SELFIE
                caption = "Selfie solo per te 🤳"
            elif "cute" in low or "dolce" in low:
                folder = PHOTOS_CUTE
                caption = "Versione più dolce per te 💛"
            else:
                # Default: una foto di Hailee
                folder = PHOTOS_HAILEE
                caption = "Foto per te amore 💛"

            await send_photo_category(update, folder, caption)
            return

    # 3) Risposte "base" se extra NON sbloccato (no IA, più semplice)
    if not extra_unlocked:
        if any(w in low for w in ["ciao", "hey", "ehi"]):
            await update.message.reply_text("Ciao amore 🤭💛")
            return
        if "mi manchi" in low:
            await update.message.reply_text("Anche tu mi manchi… più di quanto immagini 💛")
            return
        if "abbracciami" in low or "abbraccio" in low:
            await update.message.reply_text("Vieni qui… ti stringo forte forte 🤗💛")
            return

        # Risposta di default pre-extra
        await update.message.reply_text(
            "Per ora sono un po' trattenuta… se vuoi sbloccarmi del tutto scrivi *extra* 😈",
            parse_mode="Markdown",
        )
        return

    # 4) Se l'extra è sbloccato → IA FULL
    ai_reply = await generate_ai_reply(text)
    await update.message.reply_text(ai_reply)


# ---------------- MAIN ----------------

def main():
    app = ApplicationBuilder().token(BOT_TOKEN).build()

    # Comandi
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("admin", admin))

    # Messaggi di testo (tutto ciò che non è comando)
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    # JobQueue per messaggi automatici
    jq = app.job_queue
    jq.run_daily(send_good_morning, time=GOOD_MORNING_TIME)
    jq.run_daily(send_midday, time=MIDDAY_TIME)
    jq.run_daily(send_good_night, time=GOOD_NIGHT_TIME)

    app.run_polling()


if __name__ == "__main__":
    main()
