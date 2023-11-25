import telebot
from telebot import types

from app import bot, db
from app.modules.database import Users
from app.modules.students_handler import student_full_name

from app.modules.markup_handler import teacher_main_menu
from app.modules.teacher_handler import TeacherHandler
teacher = TeacherHandler()


# Handle '/start'
@bot.message_handler(commands=['start'])
def send_welcome(message):
    if db.search_user(message.from_user.id) is not None:
        msg = "Вы уже есть в системе."
        bot.send_message(message.chat.id, msg)

    if not db.check_exist_teacher():
        bot.send_message(message.chat.id, "Добро пожаловать! Вы назначены преподавателем. "
                                          "Вы будете перенесены во вкладку создания потока")
        msg = bot.reply_to(message, "Введите название для потока.\nНапример: КИ20 ИВТ ЧТ 12:00")
        bot.register_next_step_handler(msg, teacher.teacher_start_create_flow)
    else:
        msg = bot.reply_to(message, "Добро пожаловать! Вы назначены студентом.\nВведите своё ФИО")
        bot.register_next_step_handler(msg, student_full_name)


@bot.message_handler(content_types='text')
def recive_text(message):
    if message.text == "Потоки":
        bot.send_message(message.chat.id, "Начат процесс создания потока")
        msg = bot.reply_to(message, "Введите название для потока, а в новой строке перечислите группы в потоке"
                                    ".\nНапример: \nКИ20 ИВТ ЧТ 12:00\nКИ20-06б, КИ20-07б, КИ20-08б")
        bot.register_next_step_handler(msg, teacher_end_create_flow)
    elif message.text == "Вопрос":
        bot.send_message(message.chat.id, "Начат процесс сбора информации по вопросу")
        msg = bot.reply_to(message, "Выберите поток")
        bot.register_next_step_handler(msg, teacher_end_create_flow)