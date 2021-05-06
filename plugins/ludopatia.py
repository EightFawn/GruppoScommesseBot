from LootBotApi import LootBotApi
from pyrogram import Client, filters

from config.variabili import tokens
from funzioni import get_tot_storia_pagamento, aggiungi_punti


@Client.on_message(filters.command("ludopatia") & filters.reply)
def ludopatia(app, message):
    api = LootBotApi(tokens["LootBotApi"])

    giocatore1 = message.from_user.username
    giocatore2 = message.reply_to_message.from_user.username
    inviati_json = api.get_history(fromPlayer=giocatore1, toPlayer=giocatore2)
    storia = get_tot_storia_pagamento(inviati_json)
    inviati = storia[0]
    max_inviati = storia[1]
    ricevuti_json = api.get_history(fromPlayer=giocatore2, toPlayer=giocatore1)
    storia = get_tot_storia_pagamento(ricevuti_json)
    ricevuti = storia[0]
    max_ricevuti = storia[1]

    bilancio_tmp = ricevuti - inviati
    bilancio = aggiungi_punti(bilancio_tmp)
    if bilancio_tmp > 0:
        bilancio = f"+{bilancio} 📈"
    elif bilancio_tmp < 0:
        bilancio = f"{bilancio} 📉"
    else:
        bilancio = f"{bilancio} ⚖️"

    if max_inviati > max_ricevuti:
        max = max_inviati
    else:
        max = max_ricevuti

    totale = inviati + ricevuti

    msg = f"**Storico {giocatore1} 👉 {giocatore2}**\n**Soldi inviati:** {aggiungi_punti(inviati)}\n**Soldi ricevuti:** {aggiungi_punti(ricevuti)}\n**Totale:** {aggiungi_punti(totale)}\n**Bilancio:** {bilancio}\n\n**Scommessa più alta:** {aggiungi_punti(max)} "
    app.send_message(message.chat.id, msg)
