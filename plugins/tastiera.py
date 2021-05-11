from pyrogram import Client, filters
from pyrogram.types import ReplyKeyboardMarkup, ReplyKeyboardRemove


@Client.on_message(filters.command(["tastiera"]))
def tastiera(app, message):
    app.send_message(
        message.chat.id,  # Edit this
        "Ecco la tastiera con i giochi!",
        reply_markup=ReplyKeyboardMarkup(
            [
                ["Carte 🃏", "Tiro Con L'Arco 🏹"],
                ["Testa o Croce 🌕", "Dado 🎲"],
                ["Rune 🔮", "Freccette 🎯"],
                ["Corsa con i sacchi"],
                ["Random ❓"],
                ["Sorte 🐉", "/gruzzolo 💸"],
                ["Statistiche 📊", "Chiudi ❌"]
            ],
            resize_keyboard=True  # Make the keyboard smaller
        )
    )


@Client.on_message(filters.command(["chiudi"]) | filters.regex(r"^Chiudi ❌$"))
def chiudi(_, message):
    message.reply("Okay, ho chiuso la tastiera!", reply_markup=ReplyKeyboardRemove())
