import os

TELEGRAM_API_TOKEN = os.getenv("TELEGRAM_API_TOKEN")
SCHEDULER_CHECK_INTERVAL = int(os.getenv("SCHEDULER_CHECK_INTERVAL", 60))  # интервал в секундах

if not TELEGRAM_API_TOKEN:
    raise ValueError("Переменная окружения TELEGRAM_API_TOKEN не установлена!")