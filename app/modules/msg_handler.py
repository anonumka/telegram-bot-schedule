from app import bot, db
from app.modules.database import check_its_teacher, check_exist_teacher
from app.modules.students_handler import student_full_name

from app.modules.markup_handler import (teacher_flows_button, teacher_question_button, teacher_main_menu,
                                        teacher_get_flows)
from app.modules.teacher_handler import TeacherHandler

teacher = TeacherHandler()


# Handle '/start'
@bot.message_handler(commands=['start'])
def send_welcome(message):
    if db.search_user(message.from_user.id) is not None:
        msg_send = "Вы уже есть в системе."
        bot.send_message(message.chat.id, msg_send)

    if not check_exist_teacher(message.chat.id):
        bot.send_message(message.chat.id, "Добро пожаловать! Вы назначены преподавателем. "
                                          "Вы будете перенесены во вкладку создания потока")
        msg = bot.reply_to(message, "Введите название для потока.\nНапример: КИ20 ИВТ ЧТ 12:00")
        bot.register_next_step_handler(msg, teacher.teacher_start_create_flow)
    else:
        msg = bot.reply_to(message, "Добро пожаловать! Вы назначены студентом.\nВведите своё ФИО")
        bot.register_next_step_handler(msg, student_full_name)


@bot.message_handler(content_types='text',
                     func=lambda m: m.text == 'Потоки' and check_its_teacher(m.from_user.id))
def admin_flows_menu(message):
    bot.send_message(message.chat.id, "Выберите действие с потоком", reply_markup=teacher_flows_button())


@bot.message_handler(content_types='text',
                     func=lambda m: m.text == 'Добавить поток' and check_its_teacher(m.from_user.id))
def admin_flow_add(message):
    bot.send_message(message.chat.id, "Начат процесс создания потока", reply_markup=None)
    msg_send = bot.reply_to(message, "Введите название для потока.\nНапример: КИ20 ИВТ ЧТ 12:00")
    bot.register_next_step_handler(msg_send, teacher.teacher_start_create_flow)


@bot.message_handler(content_types='text',
                     func=lambda m: m.text == 'Удалить поток' and check_its_teacher(m.from_user.id))
def admin_flow_rem(message):
    bot.send_message(message.chat.id, "Начат процесс удаления вопроса")
    msg = bot.reply_to(message, "Выберите поток, который будет удалён",
                       reply_markup=teacher_get_flows(db.flow_list()))
    bot.register_next_step_handler(msg, teacher.teacher_delete_flow)
    pass


@bot.message_handler(content_types='text',
                     func=lambda m: m.text == 'Вопросы' and check_its_teacher(m.from_user.id))
def admin_questions_menu(message):
    bot.send_message(message.chat.id, "Выберите действие с вопросом", reply_markup=teacher_question_button())


@bot.message_handler(content_types='text',
                     func=lambda m: m.text == 'Задать вопрос' and check_its_teacher(m.from_user.id))
def admin_questions_create(message):
    bot.send_message(message.chat.id, "Начат процесс создания вопроса")
    msg = bot.reply_to(message, "Выберите поток, которому будет задан вопрос",
                       reply_markup=teacher_get_flows(db.flow_list()))
    bot.register_next_step_handler(msg, teacher.teacher_create_question)


@bot.message_handler(content_types='text',
                     func=lambda m: m.text == 'Посмотреть ответы' and check_its_teacher(m.from_user.id))
def admin_question_view(message):
    # TODO: Реализация просмотра ответа
    pass


@bot.message_handler(content_types='text',
                     func=lambda m: check_its_teacher(m.from_user.id))
def admin_error_message(message):
    if message.text == 'Главное меню':
        bot.clear_step_handler_by_chat_id(chat_id=message.chat.id)
    else:
        bot.send_message(message.chat.id, "Неизвестная команда", reply_markup=teacher_main_menu())


@bot.message_handler(content_types='text',
                     func=len(teacher.questions_arr) and teacher.questions_arr[-1].status)
def student_send_answer(message):
    bot.send_message(message.chat.id, "Ваш ответ успешно добавлен")
    teacher.questions_arr[-1].answer.append([message.chat.id, message.text])


@bot.message_handler(content_types='text')
def student_send_answer(message):
    # TODO: Проверка если пользователь не авторизован
    bot.send_message(message.chat.id, "Вопрос либо закончился, либо еще не начат.")
