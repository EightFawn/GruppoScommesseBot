import os

from peewee import fn

from ORM.ScommesseORM import Utente, Scommessa
import random


def codice_func():
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


def giocatore_random(utente, chat_id: int, app):
    flag = True
    while flag:
        try:
            giocatore_random = random.choice(app.get_chat_members(chat_id))
            if giocatore_random.user.id != utente and giocatore_random.user.is_bot is not False:
                return giocatore_random.user.first_name
            else:
                giocatore_random = random.choice(app.get_chat_members(chat_id))
                if giocatore_random.user.id != utente and giocatore_random.user.is_bot is not False:
                    return giocatore_random.user.first_name
                else:
                    return ""
        except ValueError:
            return "Anatras02"


def is_utente(utente_id: int):
    query = Utente.select().where(Utente.id == utente_id)
    if query.exists():
        return True
    else:
        return False


def setta_utente(utente, invitato_da=None):
    if not is_utente(utente.id):
        if invitato_da is not None:
            invitato_da = Utente.select().where(id == invitato_da).get()
            return Utente.create(id=utente.id, username=utente.username, invitatoDa=invitato_da).execute()
        else:
            return Utente.create(id=utente.id, username=utente.username).execute()
    else:
        return Utente.update(username=utente.username).where(Utente.id == utente.id).execute()


def setta_scommessa(utente, tipo_scommessa: str, risultato=None):
    setta_utente(utente)
    Scommessa.create(utente=utente.id, tipo=tipo_scommessa, risultato=risultato)


def aggiungi_punti(num: int):
    return format(num, ',d').replace(",", ".")


def get_soldi(user):
    setta_utente(user)
    soldi = Utente.select(Utente.soldi).where(Utente.id == user.id).get().soldi
    return soldi


def aggiorna_soldi(user_id: int, soldi: int):
    if soldi < 0:
        soldi = 0
    Utente.update(soldi=soldi).where(Utente.id == user_id).execute()


def numero_scommesse_gioco(gioco: str):
    return (
        Scommessa.
            select(Scommessa, fn.COUNT(Scommessa.id).alias('count')).
            where(Scommessa.tipo ** f"{gioco}%").
            get().
            count
    )


def get_tot_storia_pagamento(storia: [float]):
    tot = 0
    max = float('-inf')
    for pagamento in storia:
        prezzo = pagamento.price
        if prezzo > max:
            max = prezzo
        tot += prezzo

    if max == float('-inf'):
        max = 0

    return [tot, max]
