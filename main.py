import json
import os
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes, ConversationHandler, CallbackQueryHandler

TOKEN = os.getenv("7729311647:AAGvqUqoqh9CW-CyPYn9eQMwuGhx1fW0fYU")
DATA_FILE = "users.json"

ASK_PAYEER, ASK_EMAIL = range(2)

def load_users():
    if not os.path.exists(DATA_FILE):
        with open(DATA_FILE, "w") as f:
            json.dump({}, f)
    with open(DATA_FILE, "r") as f:
        return json.load(f)

def save_users(users):
    with open(DATA_FILE, "w") as f:
        json.dump(users, f, indent=2)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [[InlineKeyboardButton("✅ Regístrate", callback_data="register")]]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text("¡Bienvenido! Para comenzar a ganar, regístrate con tu ID de Payeer y correo de Binance o correo USDT.", reply_markup=reply_markup)

async def register_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.callback_query.answer()
    await update.callback_query.message.reply_text("Por favor, envía tu ID de Payeer:")
    return ASK_PAYEER

async def get_payeer(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["payeer"] = update.message.text.strip()
    await update.message.reply_text("Ahora envía tu correo de Binance o correo donde recibes USDT:")
    return ASK_EMAIL

async def get_email(update: Update, context: ContextTypes.DEFAULT_TYPE):
    email = update.message.text.strip()
    payeer = context.user_data["payeer"]
    user_id = str(update.effective_user.id)

    users = load_users()
    users[user_id] = {
        "telegram_id": user_id,
        "payeer": payeer,
        "email": email
    }
    save_users(users)

    keyboard = [[InlineKeyboardButton("🌐 Ir a la WebApp", url="https://tusitio.com/webapp")]]  # CAMBIA ESTA URL LUEGO
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await update.message.reply_text("✅ Registro completo. ¡Ya puedes comenzar a ganar!", reply_markup=reply_markup)
    return ConversationHandler.END

async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Registro cancelado.")
    return ConversationHandler.END

def main():
    application = Application.builder().token(TOKEN).build()

    conv_handler = ConversationHandler(
        entry_points=[CommandHandler("start", start)],
        states={
            ASK_PAYEER: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_payeer)],
            ASK_EMAIL: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_email)],
        },
        fallbacks=[CommandHandler("cancel", cancel)],
    )

    application.add_handler(conv_handler)
    application.add_handler(CallbackQueryHandler(register_callback, pattern="register"))

    application.run_polling()

if __name__ == "__main__":
    main()
