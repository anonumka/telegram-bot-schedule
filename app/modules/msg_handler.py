from app import bot, database
from app.modules.database import check_its_teacher, check_exist_teacher
from app.modules.students_handler import student_full_name, student_change_about_me

from app.modules.markup_handler import (teacher_flows_button, teacher_question_button, teacher_main_menu,
                                        teacher_get_flows, students_change_about_me_buttons)
from app.modules.teacher_handler import TeacherHandler
from app.modules.logger import message_log_system

teacher = TeacherHandler()


# Handle '/start'
@bot.message_handler(commands=['start'])
def send_welcome(message):
    message_log_system(0, f"{message.chat.id} send {message.text}")
    if not check_exist_teacher(message.chat.id):
        bot.send_message(message.chat.id, "Добро пожаловать! Вы назначены преподавателем. ")
        bot.reply_to(message, "Выберите действие", reply_markup=teacher_main_menu())
    elif check_its_teacher(message.from_user.id):
        bot.send_message(message.chat.id, "Вы уже преподаватель.")
    elif database.search_user(message.from_user.id) is not None:
        msg_send = "Вы уже есть в системе."
        bot.send_message(message.chat.id, msg_send)
    else:
        msg = bot.reply_to(message, "Добро пожаловать! Вы назначены студентом.\nВведите своё ФИО")
        bot.register_next_step_handler(msg, student_full_name)


@bot.message_handler(content_types='text',
                     func=lambda m: m.text == 'Потоки' and check_its_teacher(m.from_user.id))
def admin_flows_menu(message):
    message_log_system(0, f"{message.chat.id} send {message.text}")
    bot.send_message(message.chat.id, "Выберите действие с потоком", reply_markup=teacher_flows_button())


@bot.message_handler(content_types='text',
                     func=lambda m: m.text == 'Добавить поток' and check_its_teacher(m.from_user.id))
def admin_flow_add(message):
    message_log_system(0, f"{message.chat.id} send {message.text}")
    bot.send_message(message.chat.id, "Начат процесс создания потока", reply_markup=None)
    msg_send = bot.reply_to(message, "Введите название для потока.\nНапример: КИ20 ИВТ ЧТ 12:00")
    bot.register_next_step_handler(msg_send, teacher.teacher_start_create_flow)


@bot.message_handler(content_types='text',
                     func=lambda m: m.text == 'Удалить поток' and check_its_teacher(m.from_user.id))
def admin_flow_rem(message):
    message_log_system(0, f"{message.chat.id} send {message.text}")
    bot.send_message(message.chat.id, "Начат процесс удаления вопроса")
    msg = bot.reply_to(message, "Выберите поток, который будет удалён",
                       reply_markup=teacher_get_flows(database.flow_dict()))
    bot.register_next_step_handler(msg, teacher.teacher_delete_flow)
    pass


@bot.message_handler(content_types='text',
                     func=lambda m: m.text == 'Вопросы' and check_its_teacher(m.from_user.id))
def admin_questions_menu(message):
    message_log_system(0, f"{message.chat.id} send {message.text}")
    bot.send_message(message.chat.id, "Выберите действие с вопросом", reply_markup=teacher_question_button())


@bot.message_handler(content_types='text',
                     func=lambda m: m.text == 'Задать вопрос' and check_its_teacher(m.from_user.id))
def admin_questions_create(message):
    message_log_system(0, f"{message.chat.id} send {message.text}")
    bot.send_message(message.chat.id, "Начат процесс создания вопроса")
    msg = bot.reply_to(message, "Выберите поток, которому будет задан вопрос",
                       reply_markup=teacher_get_flows(database.flow_dict()))
    bot.register_next_step_handler(msg, teacher.teacher_create_question)


@bot.message_handler(content_types='text',
                     func=lambda m: m.text == 'Посмотреть ответы' and check_its_teacher(m.from_user.id))
def admin_question_view(message):
    message_log_system(0, f"{message.chat.id} send {message.text}")
    if len(teacher.questions_arr) == 0:
        bot.send_message(message.chat.id, "Актуальных вопросов нет", reply_markup=teacher_main_menu())
        return

    question = teacher.questions_arr[-1]
    res_text = f"Вопрос: {question.name}\nПравильный ответ: {question.answer}\n"
    for answer in question.answers:
        res_text += f"{answer[0]}: {answer[2]}\n"

    bot.send_message(message.chat.id, res_text, reply_markup=teacher_main_menu())


@bot.message_handler(content_types='text',
                     func=lambda m: check_its_teacher(m.from_user.id))
def admin_error_message(message):
    message_log_system(0, f"{message.chat.id} send {message.text}")
    if message.text == 'Назад':
        bot.clear_step_handler_by_chat_id(chat_id=message.chat.id)
        bot.reply_to(message, "Выберите действие", reply_markup=teacher_main_menu())
    else:
        bot.send_message(message.chat.id, "Неизвестная команда", reply_markup=teacher_main_menu())


@bot.message_handler(content_types='text',
                     func=lambda m: m.text == 'Изменить' and not check_its_teacher(m.from_user.id))
def student_change_data(message):
    message_log_system(0, f"{message.chat.id} send {message.text}")
    bot.send_message(message.chat.id, "Начат процесс изменения данных")
    msg = bot.reply_to(message, "Какой тип данных хотите изменить?", reply_markup=students_change_about_me_buttons())
    bot.register_next_step_handler(msg, student_change_about_me)


@bot.message_handler(content_types='text',
                     func=len(teacher.questions_arr) and teacher.questions_arr[-1].status)
def student_send_answer(message):
    student = database.search_user(message.from_user.id)
    if database.check_group_in_flow(student.group, teacher.questions_arr[-1].flow):
        message_log_system(0, f"{message.chat.id} send {message.text}")
        for full_name, group, answer in teacher.questions_arr[-1].answers:
            if full_name == student.full_name and group == student.group:
                bot.send_message(message.chat.id, "Вы уже отвечали на данный вопрос")
                return

        teacher.questions_arr[-1].answers.append([student.full_name, student.group, message.text])
        bot.send_message(message.chat.id, "Ваш ответ успешно добавлен")


@bot.message_handler(content_types='text')
def student_send_unknown(message):
    message_log_system(0, f"{message.chat.id} send {message.text}")
    student = database.search_user(message.from_user.id)
    if student is None:
        bot.send_message(message.chat.id, "Перед использованием бота, вам необходимо зарегистрироваться: /start")
    else:
        bot.send_message(message.chat.id, "Вопрос для Вашей группы либо закончился, либо еще не начат.")
