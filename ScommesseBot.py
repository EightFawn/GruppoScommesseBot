import os

from pyrogram import Client, filters
from pyrogram.types import ReplyKeyboardRemove, InlineKeyboardButton, InlineKeyboardMarkup, ReplyKeyboardMarkup
from pyrogram.errors import RPCError

import random
import json
import re
from random import randint
import operator
import datetime
from LootBotApi import LootBotApi

from ORM.ScommesseORM import *

with open('config/tokens.json', 'r') as fp:
    tokens = json.load(fp)

api = LootBotApi(tokens["LootBotApi"])


ultimiMsg = dict()

app = Client("ScommesseBot", config_file="config/config.ini")

chatScommesse = [-1001415212125,"Anatras02"]

tiratore = {}

def checkSpam(userID: int):
    try:
        ultimiMsg[userID]
    except KeyError:
        ultimiMsg[userID] = dict()
        ultimiMsg[userID] = datetime.datetime.now()
        return False

    dataOra = datetime.datetime.now()
    dataUltimoMsg = ultimiMsg[userID]
    diff = (dataOra - dataUltimoMsg).total_seconds()

    if diff < 1:
        return True
    else:
        ultimiMsg[userID] = dataOra
        return False


def codiceFunc():
    filename = "fileStats/counter.txt"
    if os.path.isfile(filename):
        file = open(filename, "r")
        counter = int(file.readline())
        file.close()
        file = open(filename, "w")
        counter += 1
        file.write(str(counter))
        file.close()
    else:
        file = open(filename, "w+")
        counter = 1
        file.write(str(counter))
        file.close()

    return counter

def giocatoreRandom(utente, chatId: int):
    flag = True
    while flag:
        try:
            giocatoreRandom = random.choice(app.get_chat_members(chatId))
            if giocatoreRandom.user.id != utente and giocatoreRandom.user.is_bot != False:
                flag = False
                return giocatoreRandom.user.first_name
            else:
                giocatoreRandom = random.choice(app.get_chat_members(chatId))
                if giocatoreRandom.user.id != utente and giocatoreRandom.user.is_bot != False:
                    flag = False
                    return giocatoreRandom.user.first_name
                else:
                    return ""
        except ValueError:
            return "Anatras02"


def isUtente(utenteID: int):
    query = Utente.select().where(Utente.id == utenteID)
    if (query.exists()):
        return True
    else:
        return False


def settaUtente(utente, invitatoDa=None):
    if not isUtente(utente.id):
        if invitatoDa != None:
            invitatoDa = Utente.select().where(id == invitatoDa).get()
            return Utente.create(id=utente.id, username=utente.username, invitatoDa=invitatoDa).execute()
        else:
            return Utente.create(id=utente.id, username=utente.username).execute()
    else:
        return Utente.update(username=utente.username).where(Utente.id == utente.id).execute()


def settaScommessa(utente, tipoScommessa: str, risultato=None):
    settaUtente(utente)
    Scommessa.create(utente=utente.id, tipo=tipoScommessa, risultato=risultato)


def aggiungiPunti(num: int):
    return format(num, ',d').replace(",", ".")


@app.on_message(filters.command("ordina"))
def ordina(_, message):
    numeri = list()

    for numero in message.command:
        try:
            numeri.append(int(numero))
        except ValueError:
            pass

    sort = sorted(numeri, reverse=True)

    messaggio = ""
    for numero in sort:
        messaggio += f"`{numero}` "

    if messaggio == "":
        message.reply("Devi inserire almeno un numero!")
    else:
        message.reply(f"Numeri ordinati (ordine decrescente): {messaggio}")


@app.on_message(filters.command(["dado"]) & filters.chat(chatScommesse) | filters.regex(r"^Dado 🎲$"))
def dado(client, message):
    rx = r'/dado\s+(\d+)'
    mo = re.match(rx, message.text)
    if mo:
        maxFacce = 999999999
        if int(mo.group(1)) > maxFacce:
            message.reply(f"Puoi tirare un dato di massimo {aggiungiPunti(maxFacce)} di facce!")
            return

        dado = aggiungiPunti(randint(1, int(mo.group(1))))

        app.send_message(message.chat.id,
                         f"@{message.from_user.username} hai appena tirato un dado a **{aggiungiPunti(int(mo.group(1)))}** facce.\nÈ uscito il numero **{str(dado)}**")
        settaScommessa(message.from_user, f"Dado {mo.group(1)}", dado)
    else:
        risultato = app.send_dice(message.chat.id, reply_to_message_id=message.message_id)
        settaScommessa(message.from_user, f"Dado 6", risultato.dice.value)


@app.on_message(filters.command("scommesse"))
def listaScommesse(_, message):
    scommesse = Scommessa.select().join(Utente, on=Scommessa.utente == Utente.id).order_by(Scommessa.data.desc()).limit(
        15).get()
    messaggio = ""

    for scommessa in scommesse:
        messaggio += f"**{scommessa.tipo}**\n>**Username:** {scommessa.utente.username}\n>**Risultato:** {scommessa.risultato}\n>**Data Scommessa:** {scommessa.data}\n\n"

    message.reply(f"**Attenzione, vengono mostrate solo le ultime 15 scommesse!**\n\n{messaggio}")


def numScommesseGioco(gioco: str):
    return (
        Scommessa.
            select(Scommessa, fn.COUNT(Scommessa.id).alias('count')).
            where(Scommessa.tipo ** f"{gioco}%").
            get().
            count
    )


@app.on_message(filters.command("stats") | filters.regex(r"^Statistiche 📊$"))
def stats(_, message):
    scommesseGiocate = Scommessa.select(Scommessa, fn.COUNT(Scommessa.id).alias('count')).get().count
    utentiTot = Utente.select(Utente, fn.COUNT(Utente.id).alias('count')).get().count
    scommesse = dict()
    data = Scommessa.select().limit(1).get()

    scommesse["Dado"] = numScommesseGioco("Dado")
    scommesse["TCA"] = numScommesseGioco("Tiro Con L'Arco")
    scommesse["ToC"] = numScommesseGioco("Testa o Croce")
    scommesse["Carte"] = numScommesseGioco("Carte")
    scommesse["Freccette"] = numScommesseGioco("Freccette")
    scommesse["Rune"] = numScommesseGioco("Rune")

    messaggio = f"""Ciao **{message.from_user.username}** ecco le statistiche riguardanti le scommesse (A partire dal {data})!\nIn totale sono state giocate **{scommesseGiocate}** scommesse, divise in questa maniera:
        > Dado: {scommesse["Dado"]}
        > Tiro Con L'Arco: {scommesse["TCA"]}
        > Carte: {scommesse["Carte"]}
        > Rune: {scommesse["Rune"]}
        > Freccette: {scommesse["Freccette"]}
        > Testa o Croce: {scommesse["ToC"]}\n
        Il gioco più giocato dai nostri **{utentiTot}** giocatori è **{max(scommesse.items(), key=operator.itemgetter(1))[0]}**
        """

    message.reply(messaggio.replace("\t", "prova prova prova"))


@app.on_message(filters.command(["freccette"]) & filters.chat(chatScommesse) | filters.regex(r"^Freccette 🎯$"))
def freccette(_, message):
    risultato = app.send_dice(message.chat.id, "🎯", reply_to_message_id=message.message_id)
    settaScommessa(message.from_user, f"Freccette", risultato.dice.value)


@app.on_message(
    filters.command(["carte"]) & (filters.chat(chatScommesse) | filters.private) | filters.regex(r"^Carte 🃏$"))
def carte(_, message):
    numero = ["A", "2", "3", "4", "5", "6", "7", "8", "9", "10", "J", "Q", "K"]
    seme = ["♣️", "♠️", "♦️", "♥️"]
    flag = True

    while flag:
        numero1 = random.choice(numero)
        numero2 = random.choice(numero)

        utente = message.from_user.id

        seme1 = random.choice(seme)
        seme2 = random.choice(seme)

        if random.randint(1, 100) <= 2:
            if random.randint(1, 2) == 1:
                carta1 = "Jolly 🃏"
                carta2 = f"{numero2} {seme2}"
            else:
                carta1 = f"{numero1} {seme1}"
                carta2 = "Jolly 🃏"
        else:
            carta1 = f"{numero1} {seme1}"
            carta2 = f"{numero2} {seme2}"

        if carta1 != carta2:
            flag = False

    message.reply(
        f"{message.from_user.username}, mischi per bene il mazzo, improvvisamente sfili dall'alto le prime due carte, sono: {carta1} e {carta2}!")
    settaScommessa(message.from_user, f"Carte", f"{carta1} {carta2}")


@app.on_message(filters.command(["ToC"]) & filters.chat(chatScommesse) | filters.regex(r"^Testa o Croce 🌕$"))
def ToC(_, message):
    TestaoCroce = ["TESTA", "CROCE"]
    risultato = random.choice(TestaoCroce)
    message.reply(
        f"{message.from_user.username}, tiri la moneta per aria, questa fa un paio di giri, torna a terra e... **E' USCITO {risultato}**!",
        quote=False)
    settaScommessa(message.from_user, "Testa o Croce", risultato)


@app.on_message(filters.command(["sorte"]) & filters.chat(chatScommesse) | filters.regex(r"^Sorte 🐉$"))
def sorte(_, message):
    sorte = ["🐇", "🐓", "🐉"]
    sortato = random.choice(sorte)

    message.reply(
        f"@{message.from_user.username}, dopo la tua (non) meritata vincita decidi di sfidare il Fato, lui dall'alto ti fa cadere in testa un animale di buon auspicio: {sortato}!",
        quote=False)


"""
Funzioni apertura e chiusura tastiera
"""


@app.on_message(filters.command(["tastiera"]))
def tastiera(_, message):
    app.send_message(
        message.chat.id,  # Edit this
        "Ecco la tastiera con i giochi!",
        reply_markup=ReplyKeyboardMarkup(
            [
                ["Carte 🃏", "Tiro Con L'Arco 🏹"],
                ["Testa o Croce 🌕", "Dado 🎲"],
                ["Rune 🔮", "Freccette 🎯"],
                ["Random ❓"],
                ["Sorte 🐉", "/gruzzolo 💸"],
                ["Statistiche 📊", "Chiudi ❌"]
            ],
            resize_keyboard=True  # Make the keyboard smaller
        )
    )


@app.on_message(filters.command(["chiudi"]) | filters.regex(r"^Chiudi ❌$"))
def chiudi(_, message):
    message.reply("Okay, ho chiuso la tastiera!", reply_markup=ReplyKeyboardRemove())


@app.on_message(filters.command("rune") & filters.chat(chatScommesse) | filters.regex(r"^Rune 🔮$"))
def rune(_, message):
    utente = message.from_user.id
    simboli = ["🌱", "🔥", "💧", "🌑"]

    simbolo = random.choice(simboli)

    message.reply(
        f"@{message.from_user.username}, invochi il grande mago di Aci Trezza che controvoglia ti fa la rivelazione: la tua runa è {simbolo}!")
    settaScommessa(message.from_user, "Rune", simbolo)


@app.on_message(filters.command("random") & filters.chat(chatScommesse) | filters.regex(r"^Random ❓$"))
def randomGioco(_, message):
    utente = message.from_user.id

    giochi = ["Carte", "Tiro Con L'Arco", "Freccette", "Rune", "Dado"]
    modalità = ["BO3", "Secca"]

    giocoScelto = random.choice(giochi)

    if giocoScelto == "Tiro Con L'Arco":
        modalitàScelta = "Secca"
    else:
        modalitàScelta = random.choice(modalità)

    message.reply(
        f"@{message.from_user.username}, sei talmente indeciso da affidare a un computer la tua scelta, immetti i dati e pochi secondi dopo esce il risultato: giocherai a **{giocoScelto} {modalitàScelta}**!")


@app.on_message(filters.command(["tira", "tira@GestoreScommesseGiochiBot", "tca"]) & filters.chat(chatScommesse) | filters.regex(r"^Tiro Con L'Arco 🏹$"))
def tira(_, message):
    utente = str(message.from_user.id)
    codice = codiceFunc()

    markup = InlineKeyboardMarkup(
        [
            [
                InlineKeyboardButton(
                    "Tira 🏹",
                    callback_data="tira|{}|{}".format(utente, codice)
                )
            ],
            [
                InlineKeyboardButton(
                    "Cancella Tiro ❌",
                    callback_data="Cancella|{}|{}".format(utente, codice)
                )
            ]
        ]
    )

    tiratore[f"{utente}{codice}"] = dict()
    tiratore[f"{utente}{codice}"]["tiro"] = 1
    tiratore[f"{utente}{codice}"]["risultati"] = []
    tiratore[f"{utente}{codice}"]["countSpam"] = 0

    message.reply(
        f"{message.from_user.first_name} clicca qui sotto per iniziare a tirare",
        reply_markup=markup,
        quote=False
    )


@app.on_callback_query()
def tiraQuery(_, callback_query):
    if "tira" in callback_query.data:
        frasiEffetto = ["Hai lanciato una **freccia** che è andata **{punti}** metri lontana",
                        "Con una sola **freccia** sei riuscito ad uccidere ben **{punti}** uccellini in volo",
                        "**{giocatore}** ti fa incazzare, dalla rabbia gli spari **{punti}** frecce sul petto lasciandolo a terra stecchito",
                        '**Edo ⚡️** viene da te e con aria soddisfatta ti dice __Haha, sono il dio supremo__\nDalla rabbia gli tiri una freccia che gli leva **{punti}** punti vita!',
                        "Non hai tempo di tirare fuori la freccia, prendi l'arco e lo **spacchi in testa** a **{giocatore}** provocandogli **{punti}** danni",
                        "Sbagli a lanciare la freccia e **ti colpisci un piede**, incomici a bestemmiare **selvaggemente**\nDio scende in terra **incazzato** perchè gli hai levato **{punti}** punti vita",
                        "@dod1c1 spara {punti} frecce a @tdjj05 su una di queste è scalfito il messaggio \"DRICER SEI UN TESTA DI CAZZO\""]

        codice = callback_query.data.split("|")[2]
        utente = int(callback_query.data.split("|")[1])
        try:
            tiratore[f"{utente}{codice}"]["countSpam"] += 1
        except KeyError:
            callback_query.answer("Il bot è stato riavviato mentre giocavi, rilancia il comando /tca")
            return

        if tiratore[f"{utente}{codice}"]["countSpam"] >= 2:
            callback_query.answer("Non spammare..")
            tiratore[f"{utente}{codice}"]["countSpam"] = 0
            return

        if callback_query.from_user.id != utente:
            callback_query.answer("Eh, volevi!")
            return

        tagUtente = f"{utente}{codice}"

        numero = random.randint(1, 25)

        giocatoreRandomVar = giocatoreRandom(utente, callback_query.message.chat.id)
        frase = random.choice(frasiEffetto).format(punti=numero, giocatore=giocatoreRandomVar)

        tiratore[tagUtente]["risultati"].append(numero)

        markup = InlineKeyboardMarkup(
            [
                [
                    InlineKeyboardButton(
                        "Tira 🏹",
                        callback_data="tira|{}|{}".format(utente, codice)
                    )
                ],
            ]
        )

        counter = 1
        tiri = ""
        for tiro in tiratore[tagUtente]["risultati"]:
            tiri += f"**Tiro {counter}:** __{tiro}__\n"
            counter += 1

        if counter > 3:
            giocatore = app.get_users(utente).first_name
            totPunti = sum(tiratore[tagUtente]["risultati"])

            if totPunti < 15:
                commento = "(un po' una merda)"
            elif totPunti < 40:
                commento = "(meh)"
            elif totPunti < 50:
                commento = "(incominciamo a ragionare)"
            elif totPunti < 60:
                commento = "(bella giocata)"
            elif totPunti < 75:
                commento = "(non vantarti, è solo culo)"
            elif totPunti == 75:
                commento = "(hai barato ammettilo!)"
            else:
                commento = ""

            callback_query.edit_message_text(
                f"Tiri un' ultima __freccia potentissima__ verso il cielo superando i __confini dell'universo__ che ti conferisce **{numero}** punti!\n\nBeh che dire **{giocatore}**, hai distrutto l'universo per divertirti un po' ma nel mentre hai totalizzato **{totPunti}** punti\n\n**__Questi sono stati i tuoi tiri__** {commento}\n{tiri}\n**Totale:** {totPunti}"
            )

            settaScommessa(callback_query.from_user, "Tiro con l'arco", totPunti)

        else:
            if counter > 3:
                callback_query.edit_message_text(
                    f"Contano solo i primi 3 tiri!\nNon cheatare mai più o ban!\n\n**__Questi infatti sono stati i tuoi tiri__**\n{tiri}\n**Totale:** {totPunti}"
                )
            else:
                callback_query.edit_message_text(
                    f"{frase}\n\n{tiri}",
                    reply_markup=markup
                )

        tiratore[tagUtente]["tiro"] += 1
        tiratore[f"{utente}{codice}"]["countSpam"] = 0

    elif "Cancella" in callback_query.data:
        utente = callback_query.data.split("|")[1]

        if callback_query.from_user.id != int(utente):
            callback_query.answer("Non si può più, F!")
            return

        callback_query.edit_message_text("Tiro annullato 😢")


@app.on_message(filters.command("cheat") & filters.reply & filters.user(["Anatras02", "tdjj05", "liuDci"]))
def cheat(_, message):
    app.send_message(message.chat.id,
                     f"Complimenti **{message.reply_to_message.from_user.username}**, i cheat sono stati attivati con successo!")


def getSoldi(user):
    settaUtente(user)
    soldi = Utente.select(Utente.soldi).where(Utente.id==user.id).get().soldi
    return soldi


def aggiornaSoldi(userID: int, soldi: int):
    if soldi < 0:
        soldi = 0
    Utente.update(soldi=soldi).where(Utente.id == userID).execute()


@app.on_message(filters.command("soldi") & (filters.chat(chatScommesse) | filters.private))
def soldi(_, message):
    soldiVar = getSoldi(message.from_user)
    soldi = f"{aggiungiPunti(soldiVar)}$"

    message.reply(f"Soldi Gruppo Scommesse: {soldi}")


admin = ["Anatras02", "tdjj05", "Dichi_28"]


@app.on_message(filters.command("dai") & filters.reply & filters.chat(chatScommesse))
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

        if soldi > getSoldi(pagante):
            if message.from_user.username not in admin:
                message.reply("Non hai abbastanza soldi.")
                return

        if ricevente.is_bot:
            message.reply("Non puoi dare i tuoi soldi ad un bot...")
            return

        if soldi > 1000000000:
            message.reply("Non puoi pagare così tanto, il limite è 1.000.000.000$")
            return

        soldiPagante = getSoldi(pagante) - soldi
        soldiRicevente = getSoldi(ricevente) + soldi

        if message.from_user.username not in admin:
            aggiornaSoldi(pagante.id, soldiPagante)

        aggiornaSoldi(ricevente.id, soldiRicevente)

        message.reply(f"@{pagante.username} hai inviato **{aggiungiPunti(soldi)}$** a @{ricevente.username}")



@app.on_message(filters.command("sdado"))
def dadoRegolamento(_, message):
    message.reply(
        "👁‍🗨 <b>Dado</b> 🎲: gioco classico.\nI due <i>(o più)</i> giocatori <b>a turno tirano il dado</b>, esce un <i>numero tra 1 e 6</i> (compresi). <b>Chi totalizza il numero più alto vince il turno</b>.<i>In alternativa</i> si può scegliere il <b>numero massimo di facce del dado</b> <u>attraverso il comando</u> \"<u>/dado</u> <b>n</b>\" dove <b>n</b> è un numero intero. (Es. \"/dado 420\" restituisce un numero compreso tra 1 e 420)\nSe non specificato <b>BO3</b>")


@app.on_message(filters.command("stoc"))
def regolamentoTOC(_, message):
    message.reply(
        "👁‍🗨 <b>Testa o Croce</b> 🌕: gioco classico.\nUno dei due giocatori <i>sceglie se puntare su Testa o su Croce</i>, all'avversario sarà assegnato di conseguenza l'altro.\nSempre uno dei due tira la moneta. <b>Vince il giocatore che tra i due ha scommesso su quella faccia</b>.\nSe non specificato <b>secca</b>")


@app.on_message(filters.command("scarte"))
def regolamentoCarte(_, message):
    message.reply(
        "👁‍🗨 <b>Carte</b> 🃏: <i>Gioco semplice, simile al dado, ma con le carte</i>.\n\nDopo aver <u>eseguito il comando</u> <b>vengono estratte 2 carte a caso dal mazzo di 52</b>. Tra le due <b>si individua la migliore</b>, che va <b>contro la migliore dell'avversario</b>.\nChi ha <b>la carta più di valore tra le due vince</b>.\n<i>La scala dei numeri è come quella del Poker</i>: A, K, Q, J, 10, 9, 8, 7, 6, 5, 4, 3, 2.\n(In ordine decrescente)\n\n<i>Il valore delle carte non è dato solo dal numero, ma anche dal seme</i>:\n♥️>♦️;\n♦️>♣️;\n♣️>♠️;\ndi conseguenza ♥️ <b>è il seme migliore</b> e ♠️ <b>è il seme peggiore</b>.\n\n<b>Per esempio</b>:\nGiocatore 1 ha 3♥️ e 2♣️; Giocatore 2 ha 2♥️ e 3♦️\nVince il <b>3♥️ del Giocatore 1</b> <i>(essendo cuori più grande di fiori e quadri, gli altri due semi non vengono considerati)</i>.\n<b>Oppure:</b> se Giocatore 1 ha 2♥️ e 2♣️, mentre Giocatore 2 ha 2♦️ e 2♥️, <b>vince il Giocatore 2</b> siccome <b>quadri è più grande di fiori</b> <i>(in questo caso i cuori non si considerano, pur essendo i più grandi, perché in pareggio)</i>.\n\nC'è inoltre una <b>bassa probabilità</b> che capiti un <b>\"🃏 Jolly!\"</b>, nel caso <b>si vince al 100%</b> <i>(a meno che non esca anche all'avversario)</i>.\nSe non specificato <b>BO3</b>")


@app.on_message(filters.command("srune"))
def regolamentoRune(_, message):
    message.reply(
        "👁‍🗨 <b>4 Rune</b> 🔮: <i>Gioco simile alle carte, ma con meno possibilità</i>.\n🌑 → <b>perde contro tutto</b>\n🔥 → <b>batte</b> 🌱\n💧 → <b>batte</b> 🔥\n🌱 → <b>batte</b> 💧\nSe non specificato <b>BO3 e sorte</b>")


@app.on_message(filters.command("stca"))
def regolamentoTCA(_, message):
    message.reply(
        "👁‍🗨 <b>Tiro Con L'Arco</b> 🏹: <i>molto intuitivo e veloce</i>.\nI due <i>(o più)</i> giocatori, dopo aver precedentemente fatto apparire il messaggio del bot <u>utilizzando il comando o l'apposito bottone</u>, <b>tirano le tre frecce a disposizione</b>. <b>Chi totalizza il punteggio più alto vince</b>.\n<i>Il punteggio massimo ottenibile è 75 (3 tiri * 25 punti max l'uno)</i>\n<b>Si prega di non flooddare</b> <i>(premere ripetutamente in un breve lasso di tempo)</i> <b>il bottone sotto il messaggio del bot, per evitare malfunzionamenti</b>\n")


@app.on_message(filters.command("sfreccette"))
def regolamentoFreccette(_, message):
    message.reply(
        "👁‍🗨 <b>Freccette</b> 🎯: <i>minigioco implementato da Telegram</i>.\nI giocatori <i>a turno tirano la freccetta</i>. <b>Chi si avvicina di più al centro vince il turno</b>.\nSe non specificato <b>BO3</b>")


@app.on_message(filters.command("invita"))
def linkInvito(_, message):
    link = f"https://telegram.me/GestoreScommesseGiochiBot?start={str(message.from_user.id)[::-1]}"
    app.send_message(message.chat.id, f"{message.from_user.username} ecco il tuo link di invito: `{link}`")


@app.on_message(filters.command(["start", "prova"]))
def start(_, message):
    utenteID = message.from_user.id

    link = app.get_chat(chatScommesse).invite_link
    if link == None:
        link = app.export_chat_invite_link(chatScommesse)

    markup = InlineKeyboardMarkup(
        [
            [
                InlineKeyboardButton(
                    "Entra nel gruppo 😃",
                    url=link
                )
            ],
        ]
    )

    if not isUtente(utenteID):
        try:
            utenteIDInvito = str(message.command[1])[::-1]
            try:
                app.send_message(utenteIDInvito,
                                 f"**{message.from_user.username}** si è appena registrato con il tuo codice di invito 🥳")
                settaUtente(message.from_user, utenteIDInvito)
            except RPCError as e:
                print(str(e))
        except IndexError:
            pass

        app.send_message(message.chat.id,
                         f"Benvenuto **{message.from_user.username}**!\nPer entrare nel gruppo premi qui sotto 👇🏻",
                         reply_markup=markup)
    else:
        app.send_message(message.chat.id, "Sei già membro del gruppo!\nPer rientrare nel gruppo premi qui sotto 👇🏻",
                         reply_markup=markup)


@app.on_message(filters.chat(chatScommesse) & filters.new_chat_members)
def nuovo(_, message):
    utenteID = message.from_user.id
    prezzo = "2500k"
    paga = False

    if not isUtente(utenteID):
        paga = True
        settaUtente(message.from_user)
    else:
        query = Utente.select().where(Utente.id == utenteID)
        if (query.exists()):
            paga = True
            app.send_message("Anatras02", f"/paga {prezzo},{message.from_user.username}")
            Utente.update(utenteID=utenteID).execute()
    if paga:
        app.send_message("Anatras02", f"/paga {prezzo},{message.from_user.username}")


def getTotStoriaPagamento(storia: [float]):
    tot = 0
    max = float('-inf')
    for pagamento in storia:
        prezzo = pagamento.price
        if (prezzo > max):
            max = prezzo
        tot += prezzo

    if (max == float('-inf')):
        max = 0

    return [tot, max]


@app.on_message(filters.command("ludopatia") & filters.reply)
def spese(_, message):
    giocatore1 = message.from_user.username
    giocatore2 = message.reply_to_message.from_user.username
    inviatiJSON = api.get_history(fromPlayer=giocatore1, toPlayer=giocatore2)
    storia = getTotStoriaPagamento(inviatiJSON)
    inviati = storia[0]
    maxInviati = storia[1]
    ricevutiJSON = api.get_history(fromPlayer=giocatore2, toPlayer=giocatore1)
    storia = getTotStoriaPagamento(ricevutiJSON)
    ricevuti = storia[0]
    maxRicevuti = storia[1]

    bilancioTmp = ricevuti - inviati
    bilancio = aggiungiPunti(bilancioTmp)
    if (bilancioTmp > 0):
        bilancio = f"+{bilancio} 📈"
    elif bilancioTmp < 0:
        bilancio = f"{bilancio} 📉"
    else:
        bilancio = f"{bilancio} ⚖️"

    if (maxInviati > maxRicevuti):
        max = maxInviati
    else:
        max = maxRicevuti

    totale = inviati + ricevuti

    msg = f"**Storico {giocatore1} 👉 {giocatore2}**\n**Soldi inviati:** {aggiungiPunti(inviati)}\n**Soldi ricevuti:** {aggiungiPunti(ricevuti)}\n**Totale:** {aggiungiPunti(totale)}\n**Bilancio:** {bilancio}\n\n**Scommessa più alta:** {aggiungiPunti(max)}"
    app.send_message(message.chat.id, msg)


app.run()
