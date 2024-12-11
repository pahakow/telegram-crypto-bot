import os
import json
import telebot
from flask import Flask, request
from apscheduler.schedulers.background import BackgroundScheduler
from datetime import datetime
import pytz
from dotenv import load_dotenv

# Завантаження змінних середовища
load_dotenv()

# Конфігурація
API_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN', '7672310143:AAFOKOHkZheEwEshezGhCUb8pb1AJYj_Csk')
CHANNEL_NAME = os.getenv('CHANNEL_NAME', '@cruptoprofit_ua')

# Ініціалізація бота і Flask
bot = telebot.TeleBot(API_TOKEN)
app = Flask(__name__)

# Змінна для відстеження останньої відправки
last_send_time = None

def get_next_quote():
    try:
        with open('quotes.json', 'r', encoding='utf-8') as file:
            quotes = json.load(file)
        
        # Отримуємо день року (1-365)
        warsaw_tz = pytz.timezone('Europe/Warsaw')
        day_of_year = datetime.now(warsaw_tz).timetuple().tm_yday
        
        # Вибираємо цитату за номером дня
        quote = quotes.get(str(day_of_year), "Немає цитати на сьогодні.")
        return quote
    except Exception as e:
        print(f"Помилка отримання цитати: {e}")
        return "Помилка отримання цитати"

def send_daily_quote():
    global last_send_time
    warsaw_tz = pytz.timezone('Europe/Warsaw')
    current_time = datetime.now(warsaw_tz)

    # Перевіряємо чи не відправляли сьогодні
    if last_send_time is not None:
        if current_time.date() == last_send_time.date():
            print(f"Цитату вже було надіслано сьогодні о {last_send_time}")
            return

    try:
        quote = get_next_quote()
        message_text = f"💎 Цитати про криптовалюту на кожен день... \n\n{quote}"
        
        bot.send_message(CHANNEL_NAME, message_text)
        last_send_time = current_time
        print(f"Цитату надіслано успішно: {current_time}")
    except Exception as e:
        print(f"Помилка надсилання цитати: {e}")

# Налаштування планувальника
scheduler = BackgroundScheduler(timezone=pytz.timezone('Europe/Warsaw'))
scheduler.add_job(send_daily_quote, 'cron', hour=9, minute=0)
scheduler.start()

@bot.message_handler(commands=['start', 'help'])
def send_welcome(message):
    bot.reply_to(message, "👋 Привіт! Я бот для щоденних криптовалютних цитат.")

@bot.message_handler(commands=['test'])
def test_quote(message):
    global last_send_time
    last_send_time = None  # Скидаємо для тестування
    send_daily_quote()
    bot.reply_to(message, "✅ Тестова цитата надіслана!")

@app.route('/', methods=['GET', 'POST'])
def webhook():
    if request.method == 'POST':
        json_string = request.get_data().decode('utf-8')
        update = telebot.types.Update.de_json(json_string)
        bot.process_new_updates([update])
        return 'OK', 200
    return 'Бот працює', 200

if __name__ == '__main__':
    # Спроба встановити вебхук
    try:
        WEBHOOK_URL = os.getenv('WEBHOOK_URL')
        if WEBHOOK_URL:
            bot.set_webhook(url=WEBHOOK_URL)
            print(f"Вебхук встановлено на {WEBHOOK_URL}")
    except Exception as e:
        print(f"Помилка встановлення вебхука: {e}")
    
    # Запуск Flask застосунку
    port = int(os.getenv('PORT', 8080))
    app.run(host='0.0.0.0', port=port)