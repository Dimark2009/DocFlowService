import os
import asyncio
import logging
from aiohttp import web
import telebot
from dotenv import load_dotenv

load_dotenv()

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize the bot
BOT_TOKEN = os.environ.get("BOT_TOKEN")
bot = telebot.TeleBot(BOT_TOKEN)

# Create an aiohttp web application
app = web.Application()

# Define the webhook route
async def handle_webhook(request):
    json_data = await request.json()
    update = telebot.types.Update.de_json(json_data)
    bot.process_new_updates([update])
    return web.Response(status=200)

# Set the webhook URL
async def set_webhook():
    webhook_url = f"https://docflowservice.onrender.com/{BOT_TOKEN}"  # Replace with your actual webhook URL
    bot.remove_webhook()
    bot.set_webhook(url=webhook_url)

# Register the webhook route
app.router.add_post(f'/{BOT_TOKEN}', handle_webhook)

# Define command handlers
@bot.message_handler(commands=['start'])
def start(message):
    bot.send_message(message.chat.id, 'Вас приветствует мастер-бот!\nЗагружайте и просматривайте документы в пару кликов:)\nНачать: /enter')

@bot.message_handler(commands=['enter'])
def main(message):
    markup = telebot.types.InlineKeyboardMarkup()
    btn1 = telebot.types.InlineKeyboardButton('Загрузить', callback_data='download')
    btn2 = telebot.types.InlineKeyboardButton('Получить', callback_data='get')
    markup.row(btn1, btn2)
    bot.send_message(message.chat.id, 'Выберите команду', reply_markup=markup)

@bot.message_handler(commands=['info'])
def info(message):
    bot.send_message(message.chat.id, 'Master bot V1.0.')

@bot.message_handler(content_types=['document'])
def get_document(message):
    if message.document:
        filename = message.document.file_name
        file_info = bot.get_file(message.document.file_id)
        downloaded_file = bot.download_file(file_info.file_path)
        file_path = os.path.join('documents', filename)
        with open(file_path, 'wb') as file:
            file.write(downloaded_file)
            bot.reply_to(message, 'Документ сохранен!\nВернуться на начальный экран? /enter')
    else:
        bot.send_message(message.chat.id, "Не удалось сохранить документ")

@bot.callback_query_handler(func=lambda callback: True)
def callback_message(callback):
    if callback.data == 'download':
        bot.send_message(callback.message.chat.id, 'Загрузите документ')
    elif callback.data == 'get':
        bot.send_message(callback.message.chat.id, 'Введите название документа')

@bot.message_handler()
def doc_name(message):
    filename = None
    for file in os.listdir('documents'):
        name_without_extension = file.split(".")[0]
        if name_without_extension == message.text:
            filename = file
            break

    if filename:
        bot.send_document(message.chat.id, open(f'documents/{filename}', 'rb'))
        bot.send_message(message.chat.id, "Вернуться на начальный экран? /enter")
    else:
        bot.send_message(message.chat.id, "Файл не найден. Попробуйте еще раз\nВернуться на начальный экран? /enter")

# Start the server and set the webhook
if __name__ == "__main__":
    logger.info("Setting webhook...")
    asyncio.run(set_webhook())  # Set the webhook
    web.run_app(app, port=8443)  # Run the aiohttp web server on port 8443
