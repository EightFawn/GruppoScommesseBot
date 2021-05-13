import re, datetime

from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup

from config.variabili import chatScommesse, tiratori
from funzioni import giocatore_random, setta_scommessa, codice_func

comandi = ["sacchi", "sacchi@GestoreScommesseGiochiBot"]

def genera_mappa(num_attuale, num_max):
    casella = "⬛️"#"n" 
    muri  = "⬜️"#"b" 
    giocatore = "💰"#"g" 
    arrivo = "🏁"#"a" 
    num_attuale = int(num_attuale)
    num_max = int(num_max)
    if num_attuale >= num_max - 1:
        arrivo = ""
        num_attuale = num_max -1
    if num_attuale < 0:
        num_attuale = 0
    caselle_percorse = casella * num_attuale
    caselle_rimanenti = casella * (num_max - num_attuale - 2)
    percorso = caselle_percorse + giocatore + caselle_rimanenti + arrivo
    mappa = ""
    peso = 20
    casella_corrente = 0
    stato = 0
    finito = False
    while finito == False:
        '''print(f"len perc {len(percorso)}")
        print(f"casella corr {casella_corrente}")
        print(f"stato {stato}")
        print(f"finito {finito}")'''
        if stato == 0:
            if giocatore in percorso[casella_corrente:casella_corrente + peso]:
                peso -= 1
            if "🏁" in percorso[casella_corrente:casella_corrente + peso]:
                peso -= 1
            print(f"len perc 0 {len(percorso)}")
            print(f"casella corr 0 {casella_corrente}")
            print(f"peso 0 {peso}")
            if len(percorso) < (casella_corrente + peso):
                rimanenti = ((casella_corrente + peso) - len(percorso)) / 2
                mappa += percorso[casella_corrente:len(percorso)] + muri * int(rimanenti)
                print("finito 0")
                finito = True
            else:
                mappa += percorso[casella_corrente:(casella_corrente + peso)] + "\n"
                casella_corrente += peso
                print("continua 0")
            peso = 2
            stato += 1
        elif stato == 1:
            if giocatore in percorso[casella_corrente:casella_corrente + peso]:
                peso -= 1
            if "🏁" in percorso[casella_corrente:casella_corrente + peso]:
                peso -= 1
            print(f"len perc 1 {len(percorso)}")
            print(f"casella corr 1 {casella_corrente}")
            print(f"peso 1 {peso}")
            if len(percorso) < (casella_corrente + peso):
                print("finito 1")
                finito = True
            else:
                mappa += (muri * 9) + percorso[casella_corrente:casella_corrente + peso] + "\n"
                casella_corrente += peso
                if casella_corrente + peso == len(percorso):
                    finito = True
                print("continua 1")
            peso = 20
            stato += 1
        elif stato == 2:
            if giocatore in percorso[casella_corrente:casella_corrente + peso]:
                peso -= 1
            if "🏁" in percorso[casella_corrente:casella_corrente + peso]:
                peso -= 1
            print(f"len perc 2 {len(percorso)}")
            print(f"casella corr 2 {casella_corrente}")
            print(f"peso 2 {peso}")
            if len(percorso) < (casella_corrente + peso):
                rimanenti = ((casella_corrente + peso) - len(percorso)) / 2
                mappa += muri * int(rimanenti) + percorso[casella_corrente:len(percorso)][::-1]
                print("finito 2")
                finito = True
            else:
                mappa += percorso[casella_corrente:(casella_corrente + peso)][::-1] + "\n"
                casella_corrente += peso
                print("continua 2")
            peso = 2
            stato += 1
        elif stato == 3:
            print(f"len perc 3 {len(percorso)}")
            print(f"casella corr 3 {casella_corrente}")
            print(f"peso 3 {peso}")
            if giocatore in percorso[casella_corrente:casella_corrente + peso]:
                peso -= 1
            if "🏁" in percorso[casella_corrente:casella_corrente + peso]:
                peso -= 1
            if len(percorso) < (casella_corrente + peso):
                finito = True
            else:
                mappa += percorso[casella_corrente:(casella_corrente + peso)] + muri * 9 + "\n"
                casella_corrente += peso
                if casella_corrente == len(percorso):
                    finito = True
            peso = 20
            stato = 0
    return mappa

@Client.on_message(filters.command(comandi) & filters.chat(chatScommesse) | filters.regex(r"^Corsa con i sacchi$"))
def sacchi(client, message):
    num_max = 10
    rx = r'/sacchi\s+(\d+)'
    mo = re.match(rx, message.text)
    if mo:
        max_percorso = 30
        if int(mo.group(1)) > max_percorso:
            message.reply(f"Puoi fare un percorso di massimo {max_percorso} caselle!")
            return
        else:
            num_max = int(mo.group(1))
    num_attuale = 0
    giocatore = message.from_user.username
    codice = codice_func()
    tiratori[f"{giocatore}{codice}"] = dict()
    tiratori[f"{giocatore}{codice}"]["ora_inizio"] = datetime.datetime.now().strftime("%d/%m/%Y,%H:%M:%S:%f")
    tiratori[f"{giocatore}{codice}"]["risultati"] = []
    tiratori[f"{giocatore}{codice}"]["num_click"] = 0
    callback_data = f"premi|{giocatore}|{codice}|{num_attuale}|{num_max}"

    bottone = [[InlineKeyboardButton("premi", callback_data = callback_data)]]
    tastiera = InlineKeyboardMarkup(bottone)
    percorso = genera_mappa(num_attuale, num_max)
    message.reply_text(percorso, reply_markup = tastiera)

@Client.on_callback_query(filters.regex("^premi"))
def premi(app, callback_query):
    data = callback_query.data
    giocatore = data.split("|")[1]
    codice = data.split("|")[2]
    num_attuale = int(data.split("|")[3])
    num_max = data.split("|")[4]
    num_click = tiratori[f"{giocatore}{codice}"]["num_click"] + 1

    if callback_query.from_user.username != giocatore:
            callback_query.answer("Eh, volevi!")
            return

    numero = 1
    tag_utente = f"{giocatore}{codice}"
    try:
        tiratori[tag_utente]
    except KeyError:
        callback_query.answer("Il bot è stato riavviato mentre giocavi, rilancia il comando /tca")
        return
    tiratori[tag_utente]["risultati"].append(numero)
    tiratori[f"{giocatore}{codice}"]["num_click"] = num_click
    ora_ultimo_update = datetime.datetime.strptime(tiratori[tag_utente]["ora_inizio"], "%d/%m/%Y,%H:%M:%S:%f")
    attesa_aggiornamento = datetime.timedelta(seconds = 3)
    
    if datetime.datetime.now() > (ora_ultimo_update + attesa_aggiornamento):
        spostamento = sum(tiratori[tag_utente]["risultati"])
        num_prossimo = num_attuale + spostamento
        tiratori[tag_utente]["risultati"].clear()
        tiratori[tag_utente]["ora_inizio"] = datetime.datetime.now().strftime("%d/%m/%Y,%H:%M:%S:%f")

        sim_arrivo = "🏁"
        percorso = genera_mappa(num_prossimo, num_max)
        if sim_arrivo in percorso:
            callback_data = f"premi|{giocatore}|{codice}|{num_prossimo}|{num_max}"
            bottone = [[InlineKeyboardButton("premi", callback_data = callback_data)]]
            tastiera = InlineKeyboardMarkup(bottone)
            callback_query.edit_message_text(text = f"{percorso}", reply_markup = tastiera)
        else:
            callback_query.edit_message_text(text = f"{percorso}\n\nHai finito il percorso in {num_click} click.")
    callback_query.answer()