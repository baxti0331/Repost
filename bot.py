import os
import httpx
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes
from telegram import Update

TOKEN = os.getenv("TELEGRAM_TOKEN")
PORT = int(os.getenv("PORT", 8443))
RENDER_HOST = os.getenv("RENDER_EXTERNAL_HOSTNAME")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")  # Твой API ключ Gemini
GEMINI_API_URL = "https://api.gemini.com/v1/ai/generate"  # Пример URL (замени на настоящий)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Привет! Отправь мне сообщение, и я отвечу с помощью Gemini AI.")

async def call_gemini_api(prompt: str) -> str:
    headers = {
        "Authorization": f"Bearer {GEMINI_API_KEY}",
        "Content-Type": "application/json"
    }
    json_data = {
        "prompt": prompt,
        "max_tokens": 150
    }
    async with httpx.AsyncClient() as client:
        resp = await client.post(GEMINI_API_URL, json=json_data, headers=headers, timeout=10)
        resp.raise_for_status()
        data = resp.json()
        # Предполагаем, что ответ в data['choices'][0]['text']
        return data.get("choices", [{}])[0].get("text", "Извините, ответ не получен.")

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_text = update.message.text
    try:
        response_text = await call_gemini_api(user_text)
    except Exception as e:
        response_text = f"Ошибка при вызове AI: {e}"
    await update.message.reply_text(response_text)

if __name__ == "__main__":
    app = ApplicationBuilder().token(TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    WEBHOOK_PATH = f"/{TOKEN}"
    WEBHOOK_URL = f"https://{RENDER_HOST}{WEBHOOK_PATH}"

    app.run_webhook(
        listen="0.0.0.0",
        port=PORT,
        url_path=TOKEN,
        webhook_url=WEBHOOK_URL
    )