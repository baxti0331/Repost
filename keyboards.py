from telebot.types import InlineKeyboardButton, InlineKeyboardMarkup
from typing import Dict, List
from config import BUTTONS  # Предполагается, что у тебя есть словарь с текстами кнопок

class Keyboards:
    @staticmethod
    def main_menu() -> InlineKeyboardMarkup:
        keyboard = [
            [InlineKeyboardButton("📤 Отправить сообщение сейчас", callback_data="post_now")],
            [InlineKeyboardButton("⏰ Запланировать сообщение", callback_data="schedule_post")],
            [InlineKeyboardButton("➕ Добавить канал/группу", callback_data="add_channel")],
            [InlineKeyboardButton("📋 Мои каналы и группы", callback_data="list_channels")],
            [InlineKeyboardButton("⏱️ Запланированные посты", callback_data="scheduled_posts")],
            [InlineKeyboardButton("🗑 Удалить канал/группу", callback_data="remove_channel")]
        ]
        return InlineKeyboardMarkup(keyboard)

    # ... остальной код клавиатур из твоего примера
