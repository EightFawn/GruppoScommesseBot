import random

from pyrogram import Client, filters

from config.variabili import chatScommesse
from funzioni import setta_scommessa


@Client.on_message(
    filters.command(["carte"]) & (filters.chat(chatScommesse) | filters.private) | filters.regex(r"^Carte 🃏$"))
def carte(_, message):
    numero = ["A", "2", "3", "4", "5", "6", "7", "8", "9", "10", "J", "Q", "K"]
    seme = ["♣️", "♠️", "♦️", "♥️"]
    flag = True

    while flag:
        numero1 = random.choice(numero)
        numero2 = random.choice(numero)
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
        f"{message.from_user.username}, mischi per bene il mazzo, improvvisamente sfili dall'alto le prime due carte, "
        f"sono: {carta1} e {carta2}!")
    setta_scommessa(message.from_user, f"Carte", f"{carta1} {carta2}")


@Client.on_message(filters.command("scarte"))
def regolamento_carte(_, message):
    message.reply(
        "👁‍🗨 <b>Carte</b> 🃏: <i>Gioco semplice, simile al dado, ma con le carte</i>.\n\nDopo aver <u>eseguito il "
        "comando</u> <b>vengono estratte 2 carte a caso dal mazzo di 52</b>. Tra le due <b>si individua la "
        "migliore</b>, che va <b>contro la migliore dell'avversario</b>.\nChi ha <b>la carta più di valore tra le due "
        "vince</b>.\n<i>La scala dei numeri è come quella del Poker</i>: A, K, Q, J, 10, 9, 8, 7, 6, 5, 4, 3, "
        "2.\n(In ordine decrescente)\n\n<i>Il valore delle carte non è dato solo dal numero, ma anche dal "
        "seme</i>:\n♥️>♦️;\n♦️>♣️;\n♣️>♠️;\ndi conseguenza ♥️ <b>è il seme migliore</b> e ♠️ <b>è il seme "
        "peggiore</b>.\n\n<b>Per esempio</b>:\nGiocatore 1 ha 3♥️ e 2♣️; Giocatore 2 ha 2♥️ e 3♦️\nVince il <b>3♥️ "
        "del Giocatore 1</b> <i>(essendo cuori più grande di fiori e quadri, gli altri due semi non vengono "
        "considerati)</i>.\n<b>Oppure:</b> se Giocatore 1 ha 2♥️ e 2♣️, mentre Giocatore 2 ha 2♦️ e 2♥️, <b>vince il "
        "Giocatore 2</b> siccome <b>quadri è più grande di fiori</b> <i>(in questo caso i cuori non si considerano, "
        "pur essendo i più grandi, perché in pareggio)</i>.\n\nC'è inoltre una <b>bassa probabilità</b> che capiti un "
        "<b>\"🃏 Jolly!\"</b>, nel caso <b>si vince al 100%</b> <i>(a meno che non esca anche "
        "all'avversario)</i>.\nSe non specificato <b>BO3</b>"
    )
