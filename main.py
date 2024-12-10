import os
import json
import telebot
from flask import Flask, request
from apscheduler.schedulers.background import BackgroundScheduler
from datetime import datetime
import pytz  # Додаємо імпорт для роботи з часовими поясами
from dotenv import load_dotenv

# Завантаження змінних середовища
load_dotenv()

# Конфігурація
API_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN', '7672310143:AAFOKOHkZheEwEshezGhCUb8pb1AJYj_Csk')
CHANNEL_NAME = os.getenv('CHANNEL_NAME', '@cruptoprofit_ua')

# Ініціалізація бота і Flask
bot = telebot.TeleBot(API_TOKEN)
app = Flask(__name__)

def load_quotes():
    try:
        with open('quotes.json', 'r', encoding='utf-8') as file:
            quotes = json.load(file)
            print("Цитати успішно завантажено")
            return quotes
    except Exception as e:
        print(f"Помилка завантаження цитат: {e}")
        return {}

# Глобальні змінні
quotes = load_quotes()
current_index = 1

def send_daily_quote():
    global current_index, quotes
    try:
        if current_index > len(quotes):
            current_index = 1
        
        quote = quotes.get(str(current_index), "Немає цитати на сьогодні.")
        message_text = f"💎 Цитати про криптовалюту на кожен день... \n\n{quote}"
        
        bot.send_message(CHANNEL_NAME, message_text)
        warsaw_tz = pytz.timezone('Europe/Warsaw')
        current_time = datetime.now(warsaw_tz)
        print(f"Цитату надіслано успішно: {current_time}")
        
        current_index += 1
    except Exception as e:
        print(f"Помилка надсилання цитати: {e}")

# Налаштування планувальника
scheduler = BackgroundScheduler()
scheduler.add_job(send_daily_quote, 'cron', hour=9, minute=0, timezone=pytz.timezone('Europe/Warsaw'))
scheduler.start()

@bot.message_handler(commands=['start', 'help'])
def send_welcome(message):
    bot.reply_to(message, "👋 Привіт! Я бот для щоденних криптовалютних цитат.")

@bot.message_handler(commands=['test'])
def test_quote(message):
    send_daily_quote()
    bot.reply_to(message, "✅ Те