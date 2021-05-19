import re, datetime

from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from pyrogram.errors import FloodWait

from config.variabili import chatScommesse, tiratori
from funzioni import giocatore_random, setta_scommessa, codice_func

comandi = ["sacchi", "sacchi@GestoreScommesseGiochiBot"]

def genera_mappa(num_attuale, num_max):
    casella = "⬛️"
    muri  = "⬜️" 
    giocatore = "💰"
    arrivo = "🏁" 
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
        if stato == 0:
            if giocatore in percorso[casella_corrente:casella_corrente + peso]:
                peso -= 1
            if "🏁" in percorso[casella_corrente:casella_corrente + peso]:
                peso -= 1
            if len(percorso) < (casella_corrente + peso):
                rimanenti = ((casella_corrente + peso) - len(percorso)) / 2
                mappa += percorso[casella_corrente:len(percorso)] + muri * int(rimanenti)
                finito = True
            else:
                mappa += percorso[casella_corrente:(casella_corrente + peso)] + "\n"
                casella_corrente += peso
            peso = 2
            stato += 1
        elif stato == 1:
            if giocatore in percorso[casella_corrente:casella_corrente + peso]:
                peso -= 1
            if "🏁" in percorso[casella_corrente:casella_corrente + peso]:
                peso -= 1
            if len(percorso) < (casella_corrente + peso):
                finito = True
            else:
                mappa += (muri * 9) + percorso[casella_corrente:casella_corrente + peso] + "\n"
                casella_corrente += peso
                if casella_corrente + peso == len(percorso):
                    finito = True
            peso = 20
            stato += 1
        elif stato == 2:
            if giocatore in percorso[casella_corrente:casella_corrente + peso]:
                peso -= 1
            if "🏁" in percorso[casella_corrente:casella_corrente + peso]:
                peso -= 1
            if len(percorso) < (casella_corrente + peso):
                rimanenti = ((casella_corrente + peso) - len(percorso)) / 2
                mappa += muri * int(rimanenti) + percorso[casella_corrente:len(percorso)][::-1]
                finito = True
            else:
                mappa += percorso[casella_corrente:(casella_corrente + peso)][::-1] + "\n"
                casella_corrente += peso
            peso = 2
            stato += 1
        elif stato == 3:
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

@Client.on_message(filters.command("sacchi")) # | filters.regex(r"^Corsa con i sacchi$")) #& filters.chat(chatScommesse)
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
    tiratori[f"{giocatore}{codice}"]["durata_fw"] = 0
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
    num_click = tiratori[f"{giocatore}{codice}"]["num_click"] 
    chat_id = callback_query.message.chat.id

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

    if tiratori[f"{giocatore}{codice}"]["durata_fw"] == 0 or datetime.datetime.now() > tiratori[f"{giocatore}{codice}"]["durata_fw"]:
        print(f'"durata_fw {tiratori[f"{giocatore}{codice}"]["durata_fw"]}')
        try:
            num_prossimo = 0
            sim_arrivo = "🏁"
            if len(tiratori[tag_utente]["risultati"]) == 0:
                num_prossimo = num_attuale + numero
            else:
                spostamento = sum(tiratori[tag_utente]["risultati"])
                num_prossimo = num_attuale + spostamento + numero
                tiratori[f"{giocatore}{codice}"]["risultati"].clear()    
            percorso = genera_mappa(num_prossimo, num_max)
            if sim_arrivo in percorso:
                callback_data = f"premi|{giocatore}|{codice}|{num_prossimo}|{num_max}"
                bottone = [[InlineKeyboardButton("premi", callback_data = callback_data)]]
                tastiera = InlineKeyboardMarkup(bottone)
                messaggio_vecchio = callback_query.message.text
                if messaggio_vecchio == percorso:
                    print("return")
                    callback_query.answer()
                    return
                else:
                    callback_query.edit_message_text(text = f"{percorso}", reply_markup = tastiera)
                tiratori[f"{giocatore}{codice}"]["num_click"] = num_click + 1
                callback_query.answer()
            else:
                callback_query.edit_message_text(text = f"{percorso}\n\nHai finito il percorso in {num_click + 1} click.")
                callback_query.answer()
        except FloodWait as fw:
            print(f"fw {fw}")
            #app.send_message(chat_id, "Anti flood")
            rx = r'[0-9]+'
            mo = re.findall(rx, str(fw))
            print(f"mo {mo}")
            if mo:
                durata = int(mo[1])
                print(f"durata {durata}")
                ora = datetime.datetime.now()
                sec_fw = datetime.timedelta(seconds = durata)
                ora_fine = ora + sec_fw
                print(f"ora fine {ora_fine}")
                tiratori[f"{giocatore}{codice}"]["durata_fw"] = ora_fine
                
                tiratori[tag_utente]["risultati"].append(numero)
            
                spostamento = sum(tiratori[tag_utente]["risultati"])
                num_prossimo = num_attuale + spostamento
                print(f"num prossimo {num_prossimo}")
                if num_prossimo >= (int(num_max) - 1):
                    tiratori[tag_utente]["risultati"].pop()
                    callback_query.answer(f"@{giocatore} hai finito il percorso in {num_click} click.")
                    return
                tiratori[f"{giocatore}{codice}"]["num_click"] = num_click + 1
                callback_query.answer()
            else:
                callback_query.answer("C'è stato un problema con il floodwait, contatta gli admin e aspetta la sua fine.")
    else:
        print(f'"durata_fw {tiratori[f"{giocatore}{codice}"]["durata_fw"]}')
        tiratori[tag_utente]["risultati"].append(numero)
        spostamento = sum(tiratori[tag_utente]["risultati"])
        num_prossimo = num_attuale + spostamento
        print(f"num prossimo {num_prossimo}")
        if num_prossimo >= (int(num_max) - 1):
            tiratori[tag_utente]["risultati"].pop()
            callback_query.answer(f"@{giocatore} hai finito il percorso in {num_click} click.")
            return
        tiratori[f"{giocatore}{codice}"]["num_click"] = num_click + 1
        callback_query.answer()