import logging
from telebot import TeleBot, types
from keyboards import Keyboards
from database import Database

logger = logging.getLogger(__name__)

class TelegramBot:
    def __init__(self, bot: TeleBot, db: Database):
        self.bot = bot
        self.db = db

        @self.bot.message_handler(commands=['start'])
        def start_handler(message: types.Message):
            self.bot.send_message(message.chat.id, "Привет! Я бот с вебхуком.")
            self.bot.send_message(message.chat.id, "Главное меню:", reply_markup=Keyboards.main_menu())

        @self.bot.message_handler(commands=['menu'])
        def menu_handler(message: types.Message):
            self.bot.send_message(message.chat.id, "Главное меню:", reply_markup=Keyboards.main_menu())

        @self.bot.callback_query_handler(func=lambda call: True)
        def callback_handler(call: types.CallbackQuery):
            data = call.data
            if data == "post_now":
                self.bot.answer_callback_query(call.id, "Отправка сообщения сейчас пока не реализована.")
            elif data == "schedule_post":
                self.bot.answer_callback_query(call.id, "Планирование поста пока не реализовано.")
            elif data == "add_channel":
                self.bot.answer_callback_query(call.id, "Добавление канала пока не реализовано.")
            elif data == "list_channels":
                self.bot.answer_callback_query(call.id, "Список каналов пока не реализован.")
            elif data == "scheduled_posts":
                self.bot.answer_callback_query(call.id, "Запланированные посты пока не реализованы.")
            elif data == "remove_channel":
                self.bot.answer_callback_query(call.id, "Удаление канала пока не реализовано.")
            else:
                self.bot.answer_callback_query(call.id, f"Нажата кнопка: {data}")

    def process_new_updates(self, updates):
        self.bot.process_new_updates(updates)