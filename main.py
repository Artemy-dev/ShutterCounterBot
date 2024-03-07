import requests
import os
import telebot
from config import TOKEN  # Импортирует API-TOKEN из файла config.py

bot = telebot.TeleBot(TOKEN)


@bot.message_handler(commands=['start'])
def send_welcome(message):
    bot.reply_to(message, 'Перетащите сюда файл для отправки без сжатия (Размер не более 20 Мб.)')


# Обрабатываем текстовые сообщения, которые содержат документ (фото)
@bot.message_handler(content_types=['document'])
def handle_docs_photo(message):
    try:
        # получаем файл присланнный пользователем и сохраняем его в каталог files
        file_info = bot.get_file(message.document.file_id)
        downloaded_file = bot.download_file(file_info.file_path)
        src = 'files/' + message.document.file_name

        with open(src, 'wb') as new_file:
            new_file.write(downloaded_file)

        # создаем список, содержащий имена фотографий в каталоге files и записываем последний элемент в img_f
        photo_dir = os.listdir('files')
        img_f = ''.join(photo_dir[-1])
        # указываем ссылку на сервер и путь к файлу (фотографии)
        url = 'https://exifmeta.com/api/upload'
        file_path = f'/Users/macbook/PycharmProjects/exif_fuji/files/{img_f}'

        with open(file_path, 'rb') as file:
            files = {'file': file}
            # отправляем POST-запрос
            response = requests.post(url, files=files).json()

            if 'MakerNotes:ImageCount' in response['RAW']:  # FujiFilm
                result = response['RAW']['MakerNotes:ImageCount']
                bot.reply_to(message, f'Срабатываний затвора: {result}')
                os.remove(file_path)
            elif 'MakerNotes:ShutterCount' in response['RAW']:  # Nikon, Sony
                result = response['RAW']['MakerNotes:ShutterCount']
                bot.reply_to(message, f'Срабатываний затвора: {result}')
                os.remove(file_path)
            else:
                bot.reply_to(message, 'Не удается определить.')
                os.remove(file_path)

    except Exception:
        bot.reply_to(message, 'Ошибка: файл слишком большой. ')


bot.infinity_polling()
