import operator

from peewee import fn
from pyrogram import Client, filters

from ORM.ScommesseORM import Scommessa, Utente
from funzioni import numero_scommesse_gioco


@Client.on_message(filters.command("scommesse"))
def lista_scommesse(_, message):
    scommesse = Scommessa.select().join(Utente, on=Scommessa.utente == Utente.id).order_by(Scommessa.data.desc()).limit(
        15).get()
    messaggio = ""

    for scommessa in scommesse:
        messaggio += f"**{scommessa.tipo}**\n>**Username:** {scommessa.utente.username}\n>**Risultato:** {scommessa.risultato}\n>**Data Scommessa:** {scommessa.data}\n\n "

    message.reply(f"**Attenzione, vengono mostrate solo le ultime 15 scommesse!**\n\n{messaggio}")


@Client.on_message(filters.command("stats") | filters.regex(r"^Statistiche 📊$"))
def stats(_, message):
    scommesse_giocate = Scommessa.select(Scommessa, fn.COUNT(Scommessa.id).alias('count')).get().count
    utenti_tot = Utente.select(Utente, fn.COUNT(Utente.id).alias('count')).get().count
    scommesse = dict()
    data = Scommessa.select().limit(1).get()

    scommesse["Dado"] = numero_scommesse_gioco("Dado")
    scommesse["TCA"] = numero_scommesse_gioco("Tiro Con L'Arco")
    scommesse["ToC"] = numero_scommesse_gioco("Testa o Croce")
    scommesse["Carte"] = numero_scommesse_gioco("Carte")
    scommesse["Freccette"] = numero_scommesse_gioco("Freccette")
    scommesse["Rune"] = numero_scommesse_gioco("Rune")

    messaggio = f"""Ciao **{message.from_user.username}** ecco le statistiche riguardanti le scommesse (A partire dal {data})!\nIn totale sono state giocate **{scommesse_giocate}** scommesse, divise in questa maniera: 
        > Dado: {scommesse["Dado"]}
        > Tiro Con L'Arco: {scommesse["TCA"]}
        > Carte: {scommesse["Carte"]}
        > Rune: {scommesse["Rune"]}
        > Freccette: {scommesse["Freccette"]}
        > Testa o Croce: {scommesse["ToC"]}\n
        Il gioco più giocato dai nostri **{utenti_tot}** giocatori è **{max(scommesse.items(), key=operator.itemgetter(1))[0]}** 
        """

    message.reply(messaggio.replace("\t", "prova prova prova"))
