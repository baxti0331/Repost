import os
from flask import Flask, request, abort
import telebot

API_TOKEN = os.getenv("TELEGRAM_API_TOKEN")  # В Render нужно добавить переменную окружения TELEGRAM_API_TOKEN

WEBHOOK_URL_BASE = os.getenv("WEBHOOK_URL_BASE")  # Например https://your-service.onrender.com
WEBHOOK_URL_PATH = f"/webhook/{API_TOKEN}"

bot = telebot.TeleBot(API_TOKEN)
app = Flask(__name__)

# Пример простой команды
@bot.message_handler(commands=['start'])
def start_handler(message):
    bot.send_message(message.chat.id, "Привет! Я работаю через webhook.")

# Обработчик webhook
@app.route(WEBHOOK_URL_PATH, methods=['POST'])
def webhook():
    if request.headers.get('content-type') == 'application/json':
        json_string = request.get_data().decode('utf-8')
        update = telebot.types.Update.de_json(json_string)
        bot.process_new_updates([update])
        return '', 200
    else:
        abort(403)

if __name__ == "__main__":
    # Удаляем старый webhook (на случай перезапуска)
    bot.remove_webhook()

    # Устанавливаем webhook
    bot.set_webhook(url=WEBHOOK_URL_BASE + WEBHOOK_URL_PATH)

    # Запускаем Flask-сервер
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)