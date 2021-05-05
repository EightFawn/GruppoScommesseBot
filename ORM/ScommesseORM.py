from peewee import *
from datetime import datetime

db = SqliteDatabase("ScommesseDB.db")


class Utente(Model):
    id = IntegerField(primary_key=True)
    username = CharField()
    soldi = IntegerField(default=0)
    invitatoDa = ForeignKeyField('self', null=True, default=None)

    class Meta:
        database = db


class Scommessa(Model):
    id = PrimaryKeyField()
    utente = ForeignKeyField(Utente)
    tipo = CharField()
    risultato = CharField()
    data = DateTimeField(default=datetime.now)

    class Meta:
        database = db


def initialize_db():
    db.connect()
    db.create_tables([Utente, Scommessa], safe=True)
    db.close()


initialize_db()
