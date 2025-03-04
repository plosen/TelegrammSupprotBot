import logging
import telebot
import sqlite3
import os

TOKEN = "8142382126:AAGFi4UEy7OWvQEiU5RAnxN9A6vXj_GrtqI"
bot = telebot.TeleBot(TOKEN)

conn = sqlite3.connect("support_requests.db", check_same_thread=False )
cursor = conn.cursor()

cursor.execute('''CREATE TABLE IF NOT EXISTS request (
                    id INTEGER PRIMARY KEY,
                    user_id INTEGER,
                    message TEXT,
                    department TEXT)''')

conn.commit()

FAQ = {
    "Как сделать заказ?": "Вы можете оформить заказ через наш сайт в разделе 'Каталог'.",
    "Как отменить заказ?": "Для отмены заказа обратитесь в отдел продаж или напишите нам в поддержку."
}

@bot.message_handler(commands=["start"])
def start(message):
    markup = telebot.types.ReplyKeyboardMarkup(resize_keyboard=True)
    markup.add("📋 Часто задаваемые вопросы")
    markup.add("🔧 Связаться с программистами", "📦 Связаться с отделом продаж")
    bot.send_message(message.chat.id, "Привет! Я бот технической поддержки. Чем могу помочь?", reply_markup=markup)


@bot.message_handler(func=lambda message: message.text == "📋 Часто задаваемые вопросы")
def faq(message):
    response = "Часто задаваемые вопросы:\n"
    for q, a in FAQ.items():
        response += f"\n*{q}*\n{a}\n"
        bot.send_message(message.chat.id, response, parse_mode="Markdown")


@bot.message_handler(func=lambda message: message.text == "🔧 Связаться с программистами")
def contact_sales(message):
    bot.send_message(message.chat.id, "Опишите вашу проблему, и мы передадим её в отдел продаж.")

@bot.message_handler(func=lambda message: True)
def handle_request(message):
    department = "программисты" if "программист" in message.text.lower() else "отдел продаж"

