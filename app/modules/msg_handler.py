import telebot
from telebot import types

from app import bot, db
from app.modules.database import Users
from app.modules.teacher_handler import teacher_full_name


# Handle '/start'
@bot.message_handler(commands=['start'])
def send_welcome(message):
    # TODO: Check count of users (if == 0; then this user = teacher)
    if db.search_user(message.from_user.id) is not None:
        msg = "Вы уже есть в системе."
        bot.send_message(message.chat.id, msg)

    if not db.check_exist_teacher():
        msg = "Добро пожаловать! Вы назначены преподавателем.\nВведите своё ФИО."
        bot.register_next_step_handler(msg, teacher_full_name)

    msg = "Добро пожаловать! Вы назначены студентов.\nВведите своё ФИО"
    bot.register_next_step_handler(msg, teacher_full_name)

