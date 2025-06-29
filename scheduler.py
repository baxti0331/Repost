import time
import logging
from database import Database
from telebot import TeleBot
from config import TELEGRAM_API_TOKEN, SCHEDULER_CHECK_INTERVAL

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def run_scheduler():
    bot_api = TeleBot(TELEGRAM_API_TOKEN)
    db = Database()

    while True:
        try:
            due_posts = db.get_due_posts()
            for post in due_posts:
                user_id = post["user_id"]
                message = post["message"]
                channels = post["channels"]

                user_channels = db.get_user_channels(user_id)
                success = 0
                errors = []

                for ch_id in channels:
                    if ch_id not in user_channels:
                        continue
                    try:
                        bot_api.send_message(chat_id=ch_id, text=message, parse_mode='HTML')
                        success += 1
                    except Exception as e:
                        errors.append(str(e))

                result_message = f"Запланированное сообщение отправлено.\nУспешно: {success}\nОшибки: {len(errors)}"
                try:
                    bot_api.send_message(chat_id=user_id, text=result_message)
                except Exception as e:
                    logger.error(f"Ошибка уведомления пользователя: {e}")

                db.remove_scheduled_post(post["id"])

            time.sleep(SCHEDULER_CHECK_INTERVAL)

        except Exception as e:
            logger.error(f"Ошибка в планировщике: {e}")
            time.sleep(SCHEDULER_CHECK_INTERVAL)

if __name__ == "__main__":
    run_scheduler()