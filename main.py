import logging
import telebot
import sqlite3
import os
from telebot.types import ReplyKeyboardMarkup, KeyboardButton


logging.basicConfig(level=logging.INFO)

# Получаем токен из переменной окружения (РЕКОМЕНДУЕТСЯ)
TOKEN = os.getenv("TELEGRAM_BOT_TOKEN", "8142382126:AAGFi4UEy7OWvQEiU5RAnxN9A6vXj_GrtqI")
bot = telebot.TeleBot(TOKEN)


def get_db_connection():
    conn = sqlite3.connect("support_requests.db", check_same_thread=False)
    return conn, conn.cursor()


conn, cursor = get_db_connection()
cursor.execute('''CREATE TABLE IF NOT EXISTS requests (
                 id INTEGER PRIMARY KEY AUTOINCREMENT,
                 user_id INTEGER,
                 message TEXT,
                 department TEXT,
                 timestamp DATETIME DEFAULT CURRENT_TIMESTAMP)''')
conn.commit()
conn.close()


FAQ = {
    "Как сделать заказ?": "Вы можете оформить заказ через наш сайт в разделе 'Каталог'.",
    "Как отменить заказ?": "Для отмены заказа обратитесь в отдел продаж или напишите нам в поддержку."
}


def save_request(user_id, message, department):
    try:
        conn, cursor = get_db_connection()
        cursor.execute("INSERT INTO requests (user_id, message, department) VALUES (?, ?, ?)",
                       (user_id, message, department))
        conn.commit()
        conn.close()
        logging.info(f"Запрос сохранён: {message} в отдел {department}")
    except sqlite3.Error as e:
        logging.error(f"Ошибка базы данных: {e}")


@bot.message_handler(commands=["start"])
def start(message):
    markup = ReplyKeyboardMarkup(resize_keyboard=True)
    markup.add(KeyboardButton("📋 Часто задаваемые вопросы"))
    markup.add(KeyboardButton("🔧 Связаться с программистами"), KeyboardButton("📦 Связаться с отделом продаж"))
    bot.send_message(message.chat.id, "Привет! Я бот технической поддержки. Чем могу помочь?", reply_markup=markup)


@bot.message_handler(func=lambda message: message.text == "📋 Часто задаваемые вопросы")
def faq(message):
    response = "Часто задаваемые вопросы:\n"
    for q, a in FAQ.items():
        response += f"\n*{q}*\n{a}\n"
    bot.send_message(message.chat.id, response, parse_mode="Markdown")


@bot.message_handler(func=lambda message: message.text == "📦 Связаться с отделом продаж")
def contact_sales(message):
    bot.send_message(message.chat.id, "Опишите вашу проблему, и мы передадим её в отдел продаж.")


@bot.message_handler(func=lambda message: message.text == "🔧 Связаться с программистами")
def contact_dev(message):
    bot.send_message(message.chat.id, "Опишите вашу проблему, и мы передадим её программистам.")


@bot.message_handler(func=lambda message: True)
def handle_request(message):
    department = "программисты" if "программист" in message.text.lower() else "отдел продаж"
    save_request(message.from_user.id, message.text, department)
    bot.send_message(message.chat.id, f"Ваш запрос передан в {department}.")


@bot.message_handler(commands=["requests"])
def view_requests(message):
    ADMIN_ID = 1489502411  # Укажите свой Telegram ID
    if message.from_user.id != ADMIN_ID:
        bot.send_message(message.chat.id, "У вас нет доступа к этой команде.")
        return

    conn, cursor = get_db_connection()
    cursor.execute("SELECT id, user_id, message, department, timestamp FROM requests")
    requests = cursor.fetchall()
    conn.close()

    if not requests:
        bot.send_message(message.chat.id, "Запросов пока нет.")
        return

    response = "📌 *Список запросов:*\n"
    for req in requests:
        response += f"\n📍 *ID:* {req[0]}\n👤 *Пользователь:* {req[1]}\n🏢 *Отдел:* {req[3]}\n📩 *Запрос:* {req[2]}\n🕒 *Дата:* {req[4]}\n"
    bot.send_message(message.chat.id, response, parse_mode="Markdown")

# Запуск бота
if __name__ == "__main__":
    logging.info("Бот запущен...")
    bot.polling(none_stop=True)
