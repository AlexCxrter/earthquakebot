import requests
from aiogram import Bot, Dispatcher, types
import asyncio
import datetime
from googletrans import Translator

# Здесь укажите токен своего бота
API_TOKEN = '6927801495:AAF1qQCRAPWh4SZZ1IjSCg5h9u7yNSqAPeU'

bot = Bot(token=API_TOKEN)
dp = Dispatcher(bot)

async def get_earthquakes(start_time, end_time):
    url = f"https://earthquake.usgs.gov/fdsnws/event/1/query?format=geojson&starttime={start_time}&endtime={end_time}"
    response = requests.get(url)
    if response.status_code == 200:
        data = response.json()
        earthquakes = data["features"]
        return earthquakes
    else:
        return None

async def translate_location(location):
    translator = Translator()
    translation = translator.translate(location, dest='ru')
    return translation.text

@dp.message_handler(commands=['start', 'help'])
async def send_welcome(message: types.Message):
    # Создаем клавиатуру с кнопками для выбора периода землетрясений
    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
    button1 = types.KeyboardButton("За последний час")
    button2 = types.KeyboardButton("За последние 3 часа")
    button3 = types.KeyboardButton("За 24 часа")
    keyboard.add(button1, button2, button3)
    await message.reply("Привет! Я бот, который может предоставить информацию о землетрясениях. Выбери период, чтобы получить информацию о землетрясениях за этот период.", reply_markup=keyboard)

@dp.message_handler()
async def check_message(message: types.Message):
    if message.text == "За последний час":
        await get_recent_earthquakes(message, hours=1)
    elif message.text == "За последние 3 часа":
        await get_recent_earthquakes(message, hours=3)
    elif message.text == "За 24 часа":
        await get_recent_earthquakes(message, hours=24)
    else:
        await message.reply("Выбери период: 'За последний час', 'За последние 3 часа' или 'За 24 часа'.")

async def get_recent_earthquakes(message: types.Message, hours):
    now = datetime.datetime.utcnow()
    start_time = now - datetime.timedelta(hours=hours)
    start_time_iso = start_time.isoformat()  # Формат ISO 8601
    end_time_iso = now.isoformat()  # Формат ISO 8601

    earthquakes = await get_earthquakes(start_time_iso, end_time_iso)
    if earthquakes:
        await message.reply(f"Землетрясения за последние {hours} часа:")
        for earthquake in earthquakes:
            magnitude = earthquake["properties"]["mag"]
            place = earthquake["properties"]["place"]
            translated_place = await translate_location(place)
            time_ms = earthquake["properties"]["time"]
            time_sec = time_ms / 1000
            time = datetime.datetime.fromtimestamp(time_sec).strftime('%Y-%m-%d %H:%M:%S')
            await message.reply(f"Магнитуда: {magnitude}\nМесто: {translated_place}\nВремя: {time}")
    else:
        await message.reply("Извините, произошла ошибка при получении информации о землетрясениях.")

if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    loop.create_task(dp.start_polling())
    loop.run_forever()
