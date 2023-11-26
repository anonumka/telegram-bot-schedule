import telebot
from telebot import types

from app import bot, db
from app.modules.database import check_its_teacher, check_exist_teacher
from app.modules.students_handler import student_full_name

from app.modules.markup_handler import teacher_flows_button, teacher_question_button, teacher_main_menu
from app.modules.teacher_handler import TeacherHandler
teacher = TeacherHandler()


# Handle '/start'
@bot.message_handler(commands=['start'])
def send_welcome(message):
    if db.search_user(message.from_user.id) is not None:
        msg = "Вы уже есть в системе."
        bot.send_message(message.chat.id, msg)

    if not check_exist_teacher(message.chat.id):
        bot.send_message(message.chat.id, "Добро пожаловать! Вы назначены преподавателем. "
                                          "Вы будете перенесены во вкладку создания потока")
        msg = bot.reply_to(message, "Введите название для потока.\nНапример: КИ20 ИВТ ЧТ 12:00")
        bot.register_next_step_handler(msg, teacher.teacher_start_create_flow)
    else:
        msg = bot.reply_to(message, "Добро пожаловать! Вы назначены студентом.\nВведите своё ФИО")
        bot.register_next_step_handler(msg, student_full_name)


@bot.message_handler(content_types='text')
def receive_text(message):
    if message.text == "Потоки" and db.check_its_teacher(message.chat.id):
        bot.send_message(message.chat.id, "Выберите действие с потоком", reply_markup=teacher_flows_button())
    elif message.text == "Добавить поток" and db.check_its_teacher():
        bot.send_message(message.chat.id, "Начат процесс создания потока")
        msg = bot.reply_to(message, "Введите название для потока.\nНапример: КИ20 ИВТ ЧТ 12:00")
        bot.register_next_step_handler(msg, teacher.teacher_start_create_flow)
    # elif message.text == "Удалить поток" and db.check_its_teacher(message.chat.id):
        # TODO: Реализация удаления потока
    elif message.text == "Вопрос" and db.check_its_teacher(message.chat.id):
        bot.send_message(message.chat.id, "Выберите действие с вопросом", reply_markup=teacher_question_button())
    elif message.text == "Задать вопрос" and db.check_its_teacher(message.chat.id):
        bot.send_message(message.chat.id, "Начат процесс создания вопроса")
        msg = bot.reply_to(message, "Выберите поток, которому будет задан вопрос")
        bot.register_next_step_handler(msg, teacher.teacher_create_question)
    # elif message.text == "Ответы на вопрос" and db.check_its_teacher(message.chat.id):
        # TODO: Реализация просмотра ответа
    elif db.check_its_teacher(message.chat.id):
        bot.send_message(message.chat.id, "Неизвестная команда", reply_markup=teacher_main_menu())
    # elif not db.check_its_teacher(message.chat.id) and TeacherHandler.question.status == True:
        # TODO: Записать ответ в question
    else:
        bot.send_message(message.chat.id, "Вопрос либо закончился, либо еще не начат.", reply_markup=teacher_flows_button())
