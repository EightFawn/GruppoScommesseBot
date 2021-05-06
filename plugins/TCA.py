from pykeyboard import InlineKeyboard
from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardButton

from config.variabili import chatScommesse, tiratori
from funzioni import *
from funzioni import giocatore_random, setta_scommessa


@Client.on_message(
    filters.command(["tira", "tira@GestoreScommesseGiochiBot", "tca"]) & filters.chat(chatScommesse) | filters.regex(
        r"^Tiro Con L'Arco 🏹$"))
def tira(_, message):
    utente = str(message.from_user.id)
    codice = codice_func()

    keyboard = InlineKeyboard(row_width=1)
    keyboard.add(
        InlineKeyboardButton("Tira 🏹", callback_data=f"tira|{utente}|{codice}"),
        InlineKeyboardButton("Cancella Tiro ❌", callback_data=f"Cancella|{utente}|{codice}")
    )

    tiratori[f"{utente}{codice}"] = dict()
    tiratori[f"{utente}{codice}"]["tiro"] = 1
    tiratori[f"{utente}{codice}"]["risultati"] = []

    message.reply(
        f"{message.from_user.first_name} clicca qui sotto per iniziare a tirare",
        reply_markup=keyboard,
        quote=False
    )


@Client.on_message(filters.command("stca"))
def regolamento_tca(_, message):
    message.reply("""👁‍🗨 <b>Tiro Con L'Arco</b> 🏹: <i>molto intuitivo e veloce</i>.\n I due <i>(o più)</i> 
    giocatori, dopo aver precedentemente fatto apparire il messaggio del bot <u>utilizzando il comando o l'apposito 
    bottone</u>, <b>tirano le tre frecce a disposizione</b>. <b>Chi totalizza il punteggio più alto vince</b>.\n 
    <i>Il punteggio massimo ottenibile è 75 (3 tiri * 25 punti max l'uno)</i>\n <b>Si prega di non flooddare</b> <i>( 
    premere ripetutamente in un breve lasso di tempo)</i> <b>il bottone sotto il messaggio del bot, per evitare 
    malfunzionamenti</b>\n""")


@Client.on_callback_query()
def tira_query(app, callback_query):
    if "tira" in callback_query.data:
        frasi_effetto = ["Hai lanciato una **freccia** che è andata **{punti}** metri lontana",
                         "Con una sola **freccia** sei riuscito ad uccidere ben **{punti}** uccellini in volo",
                         "**{giocatore}** ti fa incazzare, dalla rabbia gli spari **{punti}** frecce sul petto "
                         "lasciandolo a terra stecchito",
                         '**Edo ⚡️** viene da te e con aria soddisfatta ti dice __Haha, sono il dio supremo__\nDalla '
                         'rabbia gli tiri una freccia che gli leva **{punti}** punti vita!',
                         "Non hai tempo di tirare fuori la freccia, prendi l'arco e lo **spacchi in testa** a **{"
                         "giocatore}** provocandogli **{punti}** danni",
                         "Sbagli a lanciare la freccia e **ti colpisci un piede**, incomici a bestemmiare "
                         "**selvaggemente**\nDio scende in terra **incazzato** perché gli hai levato **{punti}** punti "
                         "vita",
                         "@dod1c1 spara {punti} frecce a @tdjj05 su una di queste è scalfito il messaggio \"DRICER SEI "
                         "UN TESTA DI CAZZO\""]

        codice = callback_query.data.split("|")[2]
        utente = int(callback_query.data.split("|")[1])
        tag_utente = f"{utente}{codice}"
        try:
            tiratori[tag_utente]
        except KeyError:
            callback_query.answer("Il bot è stato riavviato mentre giocavi, rilancia il comando /tca")
            return


        if callback_query.from_user.id != utente:
            callback_query.answer("Eh, volevi!")
            return


        numero = random.randint(1, 25)

        giocatore_random_var = giocatore_random(utente, callback_query.message.chat.id, app)
        frase = random.choice(frasi_effetto).format(punti=numero, giocatore=giocatore_random_var)

        tiratori[tag_utente]["risultati"].append(numero)

        keyboard = InlineKeyboard(row_width=1)
        keyboard.add(
            InlineKeyboardButton("Tira 🏹", callback_data=f"tira|{utente}|{codice}")
        )

        counter = 1
        tiri = ""
        for tiro in tiratori[tag_utente]["risultati"]:
            tiri += f"**Tiro {counter}:** __{tiro}__\n"
            counter += 1

        if counter > 3:
            giocatore = app.get_users(utente).first_name
            tot_punti = sum(tiratori[tag_utente]["risultati"])

            if tot_punti < 15:
                commento = "(un po' una merda)"
            elif tot_punti < 40:
                commento = "(meh)"
            elif tot_punti < 50:
                commento = "(incominciamo a ragionare)"
            elif tot_punti < 60:
                commento = "(bella giocata)"
            elif tot_punti < 75:
                commento = "(non vantarti, è solo culo)"
            elif tot_punti == 75:
                commento = "(hai barato ammettilo!)"
            else:
                commento = ""

            callback_query.edit_message_text(
                f"Tiri un' ultima __freccia potentissima__ verso il cielo superando i __confini dell'universo__ che "
                f"ti conferisce **{numero}** punti!\n\nBeh che dire **{giocatore}**, hai distrutto l'universo per "
                f"divertirti un po' ma nel mentre hai totalizzato **{tot_punti}** punti\n\n**__Questi sono stati i "
                f"tuoi tiri__** {commento}\n{tiri}\n**Totale:** {tot_punti} "
            )

            setta_scommessa(callback_query.from_user, "Tiro con l'arco", tot_punti)

        else:
            if counter > 3:
                callback_query.edit_message_text(
                    f"Contano solo i primi 3 tiri!\nNon cheatare mai più o ban!\n\n**__Questi infatti sono stati i "
                    f"tuoi tiri__**\n{tiri} "
                )
            else:
                callback_query.edit_message_text(
                    f"{frase}\n\n{tiri}",
                    reply_markup=keyboard
                )

        tiratori[tag_utente]["tiro"] += 1

    elif "Cancella" in callback_query.data:
        utente = callback_query.data.split("|")[1]

        if callback_query.from_user.id != int(utente):
            callback_query.answer("Non si può più, F!")
            return

        callback_query.edit_message_text("Tiro annullato 😢")
