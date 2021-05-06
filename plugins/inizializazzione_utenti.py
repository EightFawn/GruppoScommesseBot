from pykeyboard import InlineKeyboard
from pyrogram import Client, filters
from pyrogram.errors import RPCError
from pyrogram.types import InlineKeyboardButton

from ORM.ScommesseORM import Utente
from config.variabili import chatScommesse
from funzioni import is_utente, setta_utente


@Client.on_message(filters.command("invita"))
def link_invito(app, message):
    link = f"https://telegram.me/GestoreScommesseGiochiBot?start={str(message.from_user.id)[::-1]}"
    app.send_message(message.chat.id, f"{message.from_user.username} ecco il tuo link di invito: `{link}`")


@Client.on_message(filters.command("start"))
def start(app, message):
    utente_id = message.from_user.id

    link = app.get_chat(chatScommesse).invite_link
    if link is None:
        link = app.export_chat_invite_link(chatScommesse)

    keyboard = InlineKeyboard(row_width=1)
    keyboard.add(
        InlineKeyboardButton("Entra nel gruppo 😃", url=link)
    )

    if not is_utente(utente_id):
        try:
            utente_id_invito = str(message.command[1])[::-1]
            try:
                app.send_message(
                    utente_id_invito,
                    f"**{message.from_user.username}** si è appena registrato con il tuo codice di "
                    f"invito 🥳"
                )
                setta_utente(message.from_user, utente_id_invito)
            except RPCError as e:
                print(str(e))
        except IndexError:
            pass

        app.send_message(
            message.chat.id,
            f"Benvenuto **{message.from_user.username}**!\nPer entrare nel gruppo premi qui sotto 👇🏻",
            reply_markup=keyboard
        )
    else:
        app.send_message(
            message.chat.id, "Sei già membro del gruppo!\nPer rientrare nel gruppo premi qui sotto 👇🏻",
            reply_markup=keyboard
        )


@Client.on_message(filters.chat(chatScommesse) & filters.new_chat_members)
def nuovo(app, message):
    utente_id = message.from_user.id
    prezzo = "2500k"
    paga = False

    if not is_utente(utente_id):
        paga = True
        setta_utente(message.from_user)
    else:
        query = Utente.select().where(Utente.id == utente_id)
        if query.exists():
            paga = True
            app.send_message("Anatras02", f"/paga {prezzo},{message.from_user.username}")
            Utente.update(utenteID=utente_id).execute()
    if paga:
        app.send_message("Anatras02", f"/paga {prezzo},{message.from_user.username}")
