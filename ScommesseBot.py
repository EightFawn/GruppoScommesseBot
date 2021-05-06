from pyrogram import Client, filters

plugins = dict(root="plugins")
app = Client("ScommesseBot", config_file="config/config.ini", plugins=plugins).run()

