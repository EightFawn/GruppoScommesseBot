import re

from pyrogram import Client, filters

from config.variabili import chatScommesse
from funzioni import aggiungi_punti, setta_scommessa
import random


@Client.on_message(filters.command(["dado"]) & filters.chat(chatScommesse) | filters.regex(r"^Dado 🎲$"))
def dado(app, message):
    rx = r'/dado\s+(\d+)'
    mo = re.match(rx, message.text)
    if mo:
        max_facce = 999999999
        if int(mo.group(1)) > max_facce:
            message.reply(f"Puoi tirare un dato di massimo {aggiungi_punti(max_facce)} di facce!")
            return

        valore_dado = aggiungi_punti(random.randint(1, int(mo.group(1))))

        app.send_message(
            message.chat.id,
            f"@{message.from_user.username} hai appena tirato un dado a **{aggiungi_punti(int(mo.group(1)))}** facce"
            f".\nÈ uscito il numero **{str(valore_dado)}** "
        )
        setta_scommessa(message.from_user, f"Dado {mo.group(1)}", valore_dado)
    else:
        risultato = app.send_dice(message.chat.id, reply_to_message_id=message.message_id)
        setta_scommessa(message.from_user, f"Dado 6", risultato.dice.value)


@Client.on_message(filters.command("sdado"))
def dato_regolamento(app, message):
    message.reply(
        "👁‍🗨 <b>Dado</b> 🎲: gioco classico.\nI due <i>(o più)</i> giocatori <b>a turno tirano il dado</b>, "
        "esce un <i>numero tra 1 e 6</i> (compresi). <b>Chi totalizza il numero più alto vince il turno</b>.<i>In "
        "alternativa</i> si può scegliere il <b>numero massimo di facce del dado</b> <u>attraverso il comando</u> "
        "\"<u>/dado</u> <b>n</b>\" dove <b>n</b> è un numero intero. (Es. \"/dado 420\" restituisce un numero "
        "compreso tra 1 e 420)\nSe non specificato <b>BO3</b>"
    )
