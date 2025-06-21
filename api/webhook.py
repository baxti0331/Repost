import os
from telebot import types
from bot import TelegramBot
from telebot import TeleBot
from database import Database

API_TOKEN = os.getenv("TELEGRAM_API_TOKEN")

bot_api = TeleBot(API_TOKEN)
db = Database()
telegram_bot = TelegramBot(bot=bot_api, db=db)

def handler(request):
    # Проверяем метод
    if request.method != "POST":
        return ("Method Not Allowed", 405)

    # Проверяем Content-Type
    if request.headers.get("content-type") == "application/json":
        json_string = request.get_data().decode("utf-8")
        update = types.Update.de_json(json_string)
        telegram_bot.process_new_updates([update])
        return ("", 200)
    else:
        return ("Forbidden", 403)
