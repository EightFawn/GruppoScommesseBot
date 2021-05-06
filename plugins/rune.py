import random

from pyrogram import Client, filters

from config.variabili import chatScommesse
from funzioni import setta_scommessa


@Client.on_message(filters.command("rune") & filters.chat(chatScommesse) | filters.regex(r"^Rune 🔮$"))
def rune(app, message):
    simboli = ["🌱", "🔥", "💧", "🌑"]

    simbolo = random.choice(simboli)

    message.reply(
        f"@{message.from_user.username}, invochi il grande mago di Aci Trezza che controvoglia ti fa la rivelazione: "
        f"la tua runa è {simbolo}!"
    )
    setta_scommessa(message.from_user, "Rune", simbolo)


@Client.on_message(filters.command("srune"))
def regolamento_rune(app, message):
    message.reply("""
            👁‍🗨 <b>4 Rune</b> 🔮: <i>Gioco simile alle carte, ma con meno possibilità</i>.\n🌑 → <b>perde contro "
            "tutto</b>\n🔥 → <b>batte</b> 🌱\n💧 → <b>batte</b> 🔥\n🌱 → <b>batte</b> 💧\nSe non specificato <b>BO3 e "
            "sorte</b>
        """)
