import os
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes
from telegram import Update

TOKEN = os.getenv("TELEGRAM_TOKEN")
PORT = int(os.getenv("PORT", 8443))
RENDER_HOST = os.getenv("RENDER_EXTERNAL_HOSTNAME")

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Привет! Я бот с ИИ. Отправь мне сообщение.")

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_text = update.message.text

    # Здесь будет вызов API Gemini или другого ИИ
    # Для примера просто повторим сообщение
    response_text = f"Ты написал: {user_text}"

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