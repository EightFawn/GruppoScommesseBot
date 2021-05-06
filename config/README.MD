# File config

In questa cartella andranno inseriti i seguenti file

- config.ini --> Contiene i file di configurazione del bot quindi deve essere composto così
     ``` 
      [pyrogram]
      api_id = il_tuo_api_id
      api_hash = il_tuo_api_hash
      bot_token = il_tuo_token
    ```
- tokens.json --> Contiene i token
    ``` json
        {
          "LootBotApi": "il_tuo_token_api_lootbot"
        }
    ```
- variabili.py --> Contiene le variabili iniziali di configurazione
  ```python
    admin: [int|str] = ["lista amministratori bot"]
    tokens: dict = "il contenuto di tokens.json""
    chatScommesse: [int|str] = ["i gruppi in cui il bot funziona"]
    tiratori: dict = dict() # deve essere un dict vuoto
  ```

Una volta settati questi valori non dovrai più fare altro qui!