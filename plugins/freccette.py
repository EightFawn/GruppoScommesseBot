from pyrogram import Client, filters

from config.variabili import chatScommesse
from funzioni import setta_scommessa


@Client.on_message(filters.command(["freccette"]) & filters.chat(chatScommesse) | filters.regex(r"^Freccette 🎯$"))
def freccette(app, message):
    risultato = app.send_dice(message.chat.id, "🎯", reply_to_message_id=message.message_id)
    setta_scommessa(message.from_user, f"Freccette", risultato.dice.value)


@Client.on_message(filters.command("sfreccette"))
def regolamento_freccette(_, message):
    message.reply(
        "👁‍🗨 <b>Freccette</b> 🎯: <i>minigioco implementato da Telegram</i>.\nI giocatori <i>a turno tirano la "
        "freccetta</i>. <b>Chi si avvicina di più al centro vince il turno</b>.\nSe non specificato <b>BO3</b>"
    )
