import os
import logging
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes
import httpx
import asyncio

logging.basicConfig(level=logging.INFO)

TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
GEMINI_API_URL = "https://api.gemini.com/v1/ai/generate"  # Замени на правильный, если другой

if not TELEGRAM_TOKEN or not GEMINI_API_KEY:
    raise RuntimeError("Необходимо задать TELEGRAM_TOKEN и GEMINI_API_KEY в переменных окружения")

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Привет! Отправь мне текст, и я отвечу с помощью Gemini AI.")

async def chat_with_gemini(prompt: str) -> str:
    headers = {
        "Authorization": f"Bearer {GEMINI_API_KEY}",
        "Content-Type": "application/json",
    }
    json_data = {
        "prompt": prompt,
        "max_tokens": 150,
        # Добавь нужные параметры по документации Gemini AI
    }
    async with httpx.AsyncClient() as client:
        resp = await client.post(GEMINI_API_URL, headers=headers, json=json_data)
        resp.raise_for_status()
        data = resp.json()
        # Предположим, что ответ в data['choices'][0]['text'] (проверь в своей документации)
        return data.get("choices", [{}])[0].get("text", "Извините, ответа нет")

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_text = update.message.text
    try:
        reply = await chat_with_gemini(user_text)
    except Exception as e:
        logging.error(f"Ошибка при запросе к Gemini: {e}")
        reply = "Извините, произошла ошибка при обращении к AI."
    await update.message.reply_text(reply)

if __name__ == "__main__":
    app = ApplicationBuilder().token(TELEGRAM_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    app.run_polling()