from flask import Flask, request
import telebot
import os
from dotenv import load_dotenv

load_dotenv()

bot = telebot.TeleBot(os.environ.get("BOT_TOKEN"))  

app = Flask(__name__)

@app.route('/webhook', methods=['POST'])
def webhook():
    json_str = request.get_data(as_text=True)
    update = telebot.types.Update.de_json(json_str)
    bot.process_new_updates([update])
    return '', 200

@app.route('/set_webhook', methods=['GET'])
def set_webhook():
    webhook_url = os.environ.get("WEBHOOK_URL") 
    bot.remove_webhook()
    bot.set_webhook(url=webhook_url)
    return "Webhook set!", 200

@bot.message_handler(commands=['start']) 
def start(message):
    bot.send_message(message.chat.id, 'Вас приветствует мастер-бот!\nЗагружайте и просматривайте документы в пару кликов:)\nНачать: /enter')

@bot.message_handler(commands=['enter'])  
def main(message):
    markup = types.InlineKeyboardMarkup()
    btn1 = types.InlineKeyboardButton('Загрузить', callback_data='download')
    btn2 = types.InlineKeyboardButton('Получить', callback_data='get')
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
        file_path = os.path.join('documents', filename)  # Выбор папки для сохранения
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
    # Поиск файла в папке
    filename = None
    for file in os.listdir('documents'):
        name_without_extension = file.split(".")[0]
        if name_without_extension == message.text:
            filename = file
            break

    if filename:
        # Если файл найден, то он отправляется пользователю
        bot.send_document(message.chat.id, open(f'documents/{filename}', 'rb'))
        bot.send_message(message.chat.id, "Вернуться на начальный экран? /enter")
    else:
        bot.send_message(message.chat.id, "Файл не найден. Попробуйте еще раз\nВернуться на начальный экран? /enter")

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)  # Запуск Flask приложения
