from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup

from config.variabili import chatScommesse
from funzioni import giocatore_random, setta_scommessa

comandi = ["sacchi", "sacchi@GestoreScommesseGiochiBot"]

def genera_mappa(num_attuale, num_max):
    casella = "⬛️"
    muri  = "⬜️"
    giocatore = "💰"
    arrivo = "🏁"
    caselle_percorse = casella * int(num_attuale)
    caselle_rimanenti = casella * (int(num_max) - int(num_attuale) - 2)
    percorso = "abcdefghijklmnopqrstuv"#caselle_percorse + giocatore + caselle_rimanenti + arrivo
    #mappa = percorso[:int(num_attuale)] + giocatore + percorso[int(num_attuale)+2:len(percorso)-2] + arrivo
    mappa = ""
    casella_corrente = 0
    stato = 0
    finito = False
    while finito == False:
        if stato == 0:
            if len(percorso) < (casella_corrente + 10):
                mappa += percorso[casella_corrente:len(percorso)]
                finito = True
                return mappa
            else:
                mappa += percorso[casella_corrente:(casella_corrente + 10)] + "\n"
                casella_corrente += 10
            stato += 1
        elif stato == 1:
            if len(percorso) < (casella_corrente + 1):
                finito = True
                return mappa
            else:
                mappa += (muri * 9) + percorso[casella_corrente:casella_corrente + 1] + "\n"
                casella_corrente += 1
            stato += 1
        elif stato == 2:
            if len(percorso) < (casella_corrente + 10):
                mappa += percorso[casella_corrente:len(percorso)][::-1]
                finito = True
                return mappa
            else:
                mappa += percorso[casella_corrente:(casella_corrente + 10)][::-1] + "\n"
                casella_corrente += 10
            stato += 1
        elif stato == 3:
            if len(percorso) < (casella_corrente + 1):
                finito = True
                return mappa
            else:
                mappa += percorso[casella_corrente:(casella_corrente + 1)] + muri * 9 + "\n"
                casella_corrente += 1
            stato = 0
    #mappa = (percorso[:10] + "\n" + muri * 9 + percorso[10:11] + "\n"
    #        + percorso[11:21][::-1] + "\n"+ percorso[21:22] + muri * 9 + "\n")
    return mappa

@Client.on_message(filters.command(comandi) & filters.chat(chatScommesse) | filters.regex(r"^Corsa con i sacchi$"))
def sacchi(client, message):
    num_max = 22
    num_attuale = 0
    num_click = 0
    giocatore = message.from_user.username
    callback_data = f"premi|{giocatore}|{num_attuale}|{num_max}|{num_click}"

    bottone = [[InlineKeyboardButton("premi", callback_data = callback_data)]]
    tastiera = InlineKeyboardMarkup(bottone)
    message.reply_text("premi su", reply_markup = tastiera)

@Client.on_callback_query(filters.regex("^premi"))
def premi(app, callback_query):
    data = callback_query.data
    giocatore = data.split("|")[1]
    num_attuale = int(data.split("|")[2])
    num_max = data.split("|")[3]
    num_click = int(data.split("|")[4]) + 1
    callback_data = f"premi|{giocatore}|{num_attuale}|{num_max}|{num_click}"

    bottone = [[InlineKeyboardButton("premi", callback_data = callback_data)]]
    tastiera = InlineKeyboardMarkup(bottone)
    percorso = genera_mappa(num_attuale, num_max)
    callback_query.edit_message_text(text = f"{percorso}", reply_markup = tastiera)
    callback_query.answer()