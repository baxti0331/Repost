from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, CallbackQueryHandler, CommandHandler, ContextTypes, MessageHandler, filters
import sympy
import os

TOKEN = os.environ.get("TOKEN")

user_data = {}

def get_keyboard():
    keyboard = [
        [InlineKeyboardButton("7", callback_data="7"),
         InlineKeyboardButton("8", callback_data="8"),
         InlineKeyboardButton("9", callback_data="9"),
         InlineKeyboardButton("/", callback_data="/")],

        [InlineKeyboardButton("4", callback_data="4"),
         InlineKeyboardButton("5", callback_data="5"),
         InlineKeyboardButton("6", callback_data="6"),
         InlineKeyboardButton("*", callback_data="*")],

        [InlineKeyboardButton("1", callback_data="1"),
         InlineKeyboardButton("2", callback_data="2"),
         InlineKeyboardButton("3", callback_data="3"),
         InlineKeyboardButton("-", callback_data="-")],

        [InlineKeyboardButton("0", callback_data="0"),
         InlineKeyboardButton(".", callback_data="."),
         InlineKeyboardButton("=", callback_data="="),
         InlineKeyboardButton("+", callback_data="+")],

        [InlineKeyboardButton("(", callback_data="("),
         InlineKeyboardButton(")", callback_data=")"),
         InlineKeyboardButton("C", callback_data="C"),
         InlineKeyboardButton("sqrt", callback_data="sqrt")],

        [InlineKeyboardButton("π", callback_data="pi"),
         InlineKeyboardButton("^", callback_data="**"),
         InlineKeyboardButton("sin", callback_data="sin"),
         InlineKeyboardButton("cos", callback_data="cos")],

        [InlineKeyboardButton("tan", callback_data="tan"),
         InlineKeyboardButton("log", callback_data="log")]
    ]
    return InlineKeyboardMarkup(keyboard)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_chat.id
    user_data[chat_id] = {"expression": "", "awaiting_quadratic": False}
    await update.message.reply_text(
        "Я умный калькулятор!\nМожно вводить выражения или пользоваться кнопками.\nКоманда /quadratic — для квадратных уравнений.",
        reply_markup=get_keyboard()
    )

async def quadratic(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_chat.id
    user_data[chat_id] = {"expression": "", "awaiting_quadratic": True}
    await update.message.reply_text("Введи коэффициенты через пробел: `a b c`\nПример: `1 -3 2`", parse_mode="Markdown")

async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    chat_id = query.message.chat_id

    if chat_id not in user_data:
        user_data[chat_id] = {"expression": "", "awaiting_quadratic": False}

    text = query.data
    expr = user_data[chat_id]["expression"]

    if text == "C":
        user_data[chat_id]["expression"] = ""
        await query.edit_message_text(text="Очистили!", reply_markup=get_keyboard())
    elif text == "=":
        try:
            result = sympy.sympify(expr, evaluate=True)
            await query.edit_message_text(text=f"Результат: {result}", reply_markup=get_keyboard())
            user_data[chat_id]["expression"] = str(result)
        except:
            await query.edit_message_text(text="Ошибка!", reply_markup=get_keyboard())
            user_data[chat_id]["expression"] = ""
    else:
        expr += "pi" if text == "pi" else text
        user_data[chat_id]["expression"] = expr
        await query.edit_message_text(text=expr, reply_markup=get_keyboard())

async def handle_text(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_chat.id
    text = update.message.text

    if chat_id not in user_data:
        user_data[chat_id] = {"expression": "", "awaiting_quadratic": False}

    if user_data[chat_id]["awaiting_quadratic"]:
        try:
            a, b, c = map(float, text.strip().split())
            x = sympy.symbols('x')
            solutions = sympy.solve(a*x**2 + b*x + c, x)
            await update.message.reply_text(f"Корни уравнения: {solutions}")
        except:
            await update.message.reply_text("Ошибка: проверь ввод.")
        user_data[chat_id]["awaiting_quadratic"] = False
    else:
        try:
            result = sympy.sympify(text, evaluate=True)
            await update.message.reply_text(f"Ответ: {result}")
        except:
            await update.message.reply_text("Ошибка в выражении.")

if __name__ == '__main__':
    PORT = int(os.environ.get("PORT", 8443))
    DOMAIN = os.environ.get('RENDER_EXTERNAL_HOSTNAME')
    WEBHOOK_URL = f"https://{DOMAIN}/bot"

    app = ApplicationBuilder().token(TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("quadratic", quadratic))
    app.add_handler(CallbackQueryHandler(button_handler))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_text))

    app.run_webhook(
        listen="0.0.0.0",
        port=PORT,
        webhook_url=WEBHOOK_URL
    )