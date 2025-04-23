import json
import logging
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, CallbackContext

# Configuración de logging para ver los errores y mensajes
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)
logger = logging.getLogger(__name__)

# Token de tu bot de Telegram
TOKEN = '7729311647:AAGvqUqoqh9CW-CyPYn9eQMwuGhx1fW0fYU'

# URL de la WebApp de Render (deja este campo vacío y reemplázalo con tu URL de WebApp de Render)
WEB_APP_URL = "<TU_URL_RENDER>"

# Ruta del archivo JSON para almacenar los datos de los usuarios
USERS_FILE = 'users.json'

# Leer los datos de los usuarios desde el archivo JSON
def load_users():
    try:
        with open(USERS_FILE, 'r') as file:
            return json.load(file)
    except (FileNotFoundError, json.JSONDecodeError):
        return {}

# Guardar los datos de los usuarios en el archivo JSON
def save_users(users):
    with open(USERS_FILE, 'w') as file:
        json.dump(users, file)

# Comando /start
async def start(update: Update, context: CallbackContext):
    user = update.message.from_user
    message = f"¡Hola {user.first_name}! Bienvenido al bot de inversión.\n\n" \
              f"Por favor, regístrate proporcionando tu ID de Payeer y tu correo de Binance.\n\n" \
              f"Comienza escribiendo /register para registrarte."
    await update.message.reply_text(message)

# Comando /register
async def register(update: Update, context: CallbackContext):
    user = update.message.from_user
    message = "Por favor, envíame tu ID de Payeer y tu correo de Binance (uno por mensaje)."
    await update.message.reply_text(message)

    # Guardar la etapa del registro para saber cuándo el usuario ha enviado su ID de Payeer
    users = load_users()
    users[user.id] = {'stage': 'waiting_for_payeer'}
    save_users(users)

# Función para manejar los mensajes del usuario
async def handle_message(update: Update, context: CallbackContext):
    user = update.message.from_user
    message = update.message.text.strip()

    users = load_users()

    # Verificar si el usuario está en proceso de registro
    if user.id in users and users[user.id].get('stage') == 'waiting_for_payeer':
        # Guardar el ID de Payeer
        users[user.id]['payeer_id'] = message
        users[user.id]['stage'] = 'waiting_for_email'
        save_users(users)

        # Pedir el correo de Binance
        response = "Ahora, por favor, envíame tu correo de Binance."
        await update.message.reply_text(response)
        return

    # Verificar si el usuario ha enviado el correo de Binance
    if user.id in users and users[user.id].get('stage') == 'waiting_for_email':
        # Guardar el correo de Binance
        users[user.id]['binance_email'] = message
        users[user.id]['stage'] = 'registered'
        save_users(users)

        # Confirmación de registro y enviar el enlace a la WebApp
        response = f"¡Te has registrado exitosamente!\n\n" \
                   f"Ahora puedes comenzar a ganar dinero haciendo tareas y viendo anuncios.\n\n" \
                   f"Accede a tu cuenta aquí: {WEB_APP_URL}"
        await update.message.reply_text(response)
        return

    # Si el usuario no está en proceso de registro
    await update.message.reply_text("Por favor, utiliza /register para comenzar el registro.")

# Función para manejar errores
def error(update: Update, context: CallbackContext):
    logger.warning(f"Update {update} caused error {context.error}")

def main():
    # Crear la aplicación y conectar el bot de Telegram
    application = Application.builder().token(TOKEN).build()

    # Comandos del bot
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("register", register))

    # Manejar mensajes
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    # Manejar errores
    application.add_error_handler(error)

    # Ejecutar el bot
    application.run_polling()

if __name__ == '__main__':
    main()

