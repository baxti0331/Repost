import os

TELEGRAM_API_TOKEN = os.getenv("TELEGRAM_API_TOKEN")

# Интервал проверки запланированных сообщений в секундах (для scheduler.py)
SCHEDULER_CHECK_INTERVAL = 30
