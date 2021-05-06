import random

from pyrogram import Client, filters

from config.variabili import chatScommesse
from funzioni import setta_scommessa


@Client.on_message(filters.command(["ToC"]) & filters.chat(chatScommesse) | filters.regex(r"^Testa o Croce 🌕$"))
def toc(app, message):
    testa_o_croce = ["TESTA", "CROCE"]
    risultato = random.choice(testa_o_croce)
    message.reply(
        f"{message.from_user.username}, tiri la moneta per aria, questa fa un paio di giri, torna a terra e... **E' "
        f"USCITO {risultato}**!",
        quote=False)
    setta_scommessa(message.from_user, "Testa o Croce", risultato)


@Client.on_message(filters.command("stoc"))
def regolamento_toc(app, message):
    message.reply(
        "👁‍🗨 <b>Testa o Croce</b> 🌕: gioco classico.\nUno dei due giocatori <i>sceglie se puntare su Testa o su "
        "Croce</i>, all'avversario sarà assegnato di conseguenza l'altro.\nSempre uno dei due tira la moneta. "
        "<b>Vince il giocatore che tra i due ha scommesso su quella faccia</b>.\nSe non specificato <b>secca</b>"
    )
