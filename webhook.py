import os
from flask import Flask, request, abort
from telebot import TeleBot, types
from bot import TelegramBot
from database import Database
from config import TELEGRAM_API_TOKEN

app = Flask(__name__)

bot_api = TeleBot(TELEGRAM_API_TOKEN)
db = Database()
telegram_bot = TelegramBot(bot=bot_api, db=db)

@app.route('/webhook', methods=['POST'])
def webhook_handler():
    if request.headers.get('content-type') == 'application/json':
        json_string = request.get_data().decode('utf-8')
        update = types.Update.de_json(json_string)
        telegram_bot.process_new_updates([update])
        return '', 200
    else:
        abort(403)

@app.route('/')
def index():
    return "Bot is running", 200

if __name__ == "__main__":
    port = int(os.environ.get('PORT', 5000))
    app.run(host="0.0.0.0", port=port)
