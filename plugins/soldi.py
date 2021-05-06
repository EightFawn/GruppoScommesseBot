import re

from pyrogram import Client, filters

from config.variabili import chatScommesse, admin
from funzioni import get_soldi, aggiungi_punti, aggiorna_soldi


@Client.on_message(filters.command("soldi") & (filters.chat(chatScommesse) | filters.private))
def soldi(_, message):
    soldi_var = get_soldi(message.from_user)
    soldi = f"{aggiungi_punti(soldi_var)}$"

    message.reply(f"Soldi Gruppo Scommesse: {soldi}")


@Client.on_message(filters.command("dai") & filters.reply & filters.chat(chatScommesse))
def dai(_, message):
    messaggio = message.text.replace(".", "")
    rx = r'/dai\s+(\d+)'
    mo = re.match(rx, messaggio)

    if mo:
        pagante = message.from_user
        ricevente = message.reply_to_message.from_user
        soldi = int(mo.group(1))

        if pagante == ricevente:
            if message.from_user.username not in admin:
                message.reply("Non puoi pagarti da solo..")
                return

        if soldi > get_soldi(pagante):
            if message.from_user.username not in admin:
                message.reply("Non hai abbastanza soldi.")
                return

        if ricevente.is_bot:
            message.reply("Non puoi dare i tuoi soldi ad un bot...")
            return

        if soldi > 1000000000:
            message.reply("Non puoi pagare così tanto, il limite è 1.000.000.000$")
            return

        soldi_pagante = get_soldi(pagante) - soldi
        soldi_ricevente = get_soldi(ricevente) + soldi

        if message.from_user.username not in admin:
            aggiorna_soldi(pagante.id, soldi_pagante)

        aggiorna_soldi(ricevente.id, soldi_ricevente)

        message.reply(f"@{pagante.username} hai inviato **{aggiungi_punti(soldi)}$** a @{ricevente.username}")
