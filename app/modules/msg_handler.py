from app import bot, database
from app.modules.json_parser import check_its_teacher, check_exist_teacher
from app.modules.students_handler import student_full_name, student_change_about_me

from app.modules.markup_handler import (teacher_flows_button, teacher_question_button, teacher_main_menu,
                                        teacher_get_flows, students_change_about_me_buttons, only_back_button,
                                        students_main_menu)
from app.modules.teacher_handler import TeacherHandler, add_question, rem_question
from app.modules.logger import message_log_system
from app.modules.utils import get_question_info

teacher = TeacherHandler()


# Handle '/start'
@bot.message_handler(commands=['start'])
def send_welcome(message):
    message_log_system(0, f"{message.chat.id} send {message.text}")
    if not check_exist_teacher(message.chat.id):
        bot.send_message(message.chat.id, "Добро пожаловать! Вы назначены преподавателем. ")
        bot.reply_to(message, "Выберите действие", reply_markup=teacher_main_menu())
    elif check_its_teacher(message.from_user.id):
        bot.send_message(message.chat.id, "Вы уже зарегистрированы как преподаватель.")
    elif database.search_user(message.from_user.id) is not None:
        msg_send = "Вы уже есть в системе."
        bot.send_message(message.chat.id, msg_send)
    else:
        msg = bot.reply_to(message, "Добро пожаловать! Вы назначены студентом.\nВведите своё ФИО")
        bot.register_next_step_handler(msg, student_full_name)


@bot.message_handler(commands=['flow'], func=lambda m: check_its_teacher(m.from_user.id))
def teacher_send_flow(message):
    message_log_system(0, f"{message.chat.id} send {message.text}")
    data = message.text.split(' ', 2)
    if len(data) < 3 or (data[1] != "add" and data[1] != "rem"):
        bot.send_message(message.chat.id, "Неверно введена команда, связанная с потоками.\n"
                                          "Примеры команды: \n"
                                          "/flow add Информатика 2022\n"
                                          "/flow rem Информатика 2022")
        bot.reply_to(message, "Выберите действие", reply_markup=teacher_main_menu())
        return

    if teacher.question is not None and teacher.question.status:
        bot.send_message(message.chat.id, "Запрещено редактировать потоки во время активного вопроса")
        bot.reply_to(message, "Выберите действие", reply_markup=teacher_main_menu())
        return

    flow_name = data[2]
    if data[1] == "add":
        teacher.teacher_create_flow(message, flow_name)
    elif data[1] == 'rem':
        teacher.teacher_delete_flow(message, flow_name)


@bot.message_handler(commands=['question'], func=lambda m: check_its_teacher(m.from_user.id))
def teacher_send_question(message):
    message_log_system(0, f"{message.chat.id} send {message.text}")
    data = message.text.split(' ', 2)
    if 1 >= len(data) <= 4:
        bot.send_message(message.chat.id, "Неверно введена команда, связанная с вопросом.\n"
                                          "Примеры команды: \n"
                                          "/question add Информатика 2022; 01.02.2024; Какая тут ошибка?; Неверный ввод\n"
                                          "/question rem Информатика 2022; 01.02.2024")
        bot.reply_to(message, "Выберите действие", reply_markup=teacher_main_menu())
        return

    question_info = data[2].split('; ')
    if data[1] == "add":
        if teacher.question is not None and teacher.question.status:
            bot.send_message(message.chat.id, "Запрещено редактировать вопросы во время активного вопроса")
            bot.reply_to(message, "Выберите действие", reply_markup=teacher_main_menu())
            return

        if len(question_info) != 4:
            bot.send_message(message.chat.id, "Ошибка ввода команды 'add'. Пример:\n"
                                              "/question add Информатика 2022; 01.02.2024; Какая тут ошибка?; "
                                              "Неверный ввод\n")
            bot.reply_to(message, "Выберите действие", reply_markup=teacher_main_menu())
            return

        add_question(question_info, message)
    elif data[1] == "rem":
        if teacher.question is not None and teacher.question.status:
            bot.send_message(message.chat.id, "Запрещено редактировать вопросы во время активного вопроса")
            bot.reply_to(message, "Выберите действие", reply_markup=teacher_main_menu())
            return

        if len(question_info) != 2:
            bot.send_message(message.chat.id, "Ошибка ввода команды 'add'. Пример:\n"
                                              "/question rem Информатика 2022; 01.02.2024;")
            bot.reply_to(message, "Выберите действие", reply_markup=teacher_main_menu())
            return

        rem_question(question_info, message)

    elif data[1] == "start":
        flow_name = data[2]
        teacher.teacher_start_question(message, flow_name)
    elif data[1] == "stop":
        if teacher.question is None or teacher.question.status is False:
            bot.send_message(message.chat.id, "Ошибка ввода команды 'stop'. Нет запущенных вопросов")
            bot.reply_to(message, "Выберите действие", reply_markup=teacher_main_menu())
        else:
            teacher.question.stop_question()
            bot.reply_to(message, "Вопрос успешно завершен и сохранен", reply_markup=teacher_main_menu())
    elif data[1] == "info":
        if teacher.question is None or teacher.question.status is False:
            bot.send_message(message.chat.id, "Ошибка ввода команды 'info'. Нет запущенных вопросов")
            bot.reply_to(message, "Выберите действие", reply_markup=teacher_main_menu())
        else:
            res_text = get_question_info(teacher.question)
            bot.send_message(message.chat.id, res_text, reply_markup=teacher_main_menu())
    else:
        bot.send_message(message.chat.id, f"Команда {data[1]} не найдена. Список команд: add, rem, start, stop, info")
        bot.reply_to(message, "Выберите действие", reply_markup=teacher_main_menu())
        return


@bot.message_handler(content_types='text',  func=lambda m: m.text == 'Потоки' and check_its_teacher(m.from_user.id))
def admin_flows_menu(message):
    message_log_system(0, f"{message.chat.id} send {message.text}")
    bot.send_message(message.chat.id, "Выберите действие с потоком", reply_markup=teacher_flows_button())


@bot.message_handler(content_types='text',
                     func=lambda m: m.text == 'Добавить поток' and check_its_teacher(m.from_user.id))
def admin_flow_add(message):
    message_log_system(0, f"{message.chat.id} send {message.text}")
    if teacher.flows_add is not None:
        bot.send_message(message.chat.id, f"Еще действует регистрация в поток {teacher.flows_add.name}")
        bot.reply_to(message, "Выберите действие", reply_markup=teacher_main_menu())
        return

    bot.send_message(message.chat.id, "Начат процесс создания потока", reply_markup=only_back_button())
    msg_send = bot.reply_to(message, "Введите название для потока.\nНапример: КИ20 ИВТ ЧТ 12:00")
    bot.register_next_step_handler(msg_send, teacher.teacher_create_flow)


@bot.message_handler(content_types='text',
                     func=lambda m: m.text == 'Удалить поток' and check_its_teacher(m.from_user.id))
def admin_flow_rem(message):
    message_log_system(0, f"{message.chat.id} send {message.text}")
    if len(database.flow_dict()) > 0:
        bot.send_message(message.chat.id, "Начат процесс удаления вопроса")
        msg = bot.reply_to(message, "Выберите поток, который будет удалён",
                           reply_markup=teacher_get_flows(database.flow_dict()))
        bot.register_next_step_handler(msg, teacher.teacher_remove_question_flow)
    else:
        bot.send_message(message.chat.id, "Список потоков пуст", reply_markup=teacher_main_menu())


@bot.message_handler(content_types='text', func=lambda m: m.text == 'Вопросы' and check_its_teacher(m.from_user.id))
def admin_questions_menu(message):
    message_log_system(0, f"{message.chat.id} send {message.text}")
    bot.send_message(message.chat.id, "Выберите действие с вопросом", reply_markup=teacher_question_button())


@bot.message_handler(content_types='text',
                     func=lambda m: m.text == 'Добавить вопрос' and check_its_teacher(m.from_user.id))
def admin_questions_create(message):
    message_log_system(0, f"{message.chat.id} send {message.text}")
    bot.send_message(message.chat.id, "Начат процесс создания вопроса")
    msg = bot.reply_to(message, "Выберите поток, которому будет задан вопрос",
                       reply_markup=teacher_get_flows(database.flow_dict()))
    bot.register_next_step_handler(msg, teacher.teacher_create_question)


@bot.message_handler(content_types='text',
                     func=lambda m: m.text == 'Удалить вопрос' and check_its_teacher(m.from_user.id))
def admin_questions_remove(message):
    message_log_system(0, f"{message.chat.id} send {message.text}")
    bot.send_message(message.chat.id, "Начат процесс удаления вопроса")
    msg = bot.reply_to(message, "Выберите поток, у которого необходимо удалить вопрос",
                       reply_markup=teacher_get_flows(database.flow_dict()))
    bot.register_next_step_handler(msg, teacher.teacher_remove_question_flow)


@bot.message_handler(content_types='text',
                     func=lambda m: m.text == 'Задать вопрос' and check_its_teacher(m.from_user.id))
def admin_questions_remove(message):
    message_log_system(0, f"{message.chat.id} send {message.text}")
    msg = bot.reply_to(message, "Выберите поток, которому будет задан вопрос",
                       reply_markup=teacher_get_flows(database.flow_dict()))
    bot.register_next_step_handler(msg, teacher.teacher_start_question)


@bot.message_handler(content_types='text',
                     func=lambda m: m.text == 'Остановить вопрос' and check_its_teacher(m.from_user.id))
def admin_questions_remove(message):
    message_log_system(0, f"{message.chat.id} send {message.text}")
    if teacher.question is None or teacher.question.status is False:
        bot.send_message(message.chat.id, "Ошибка ввода. Нет запущенных вопросов")
        bot.reply_to(message, "Выберите действие", reply_markup=teacher_main_menu())
    else:
        teacher.question.stop_question()
        bot.reply_to(message, "Вопрос успешно завершен и сохранен", reply_markup=teacher_main_menu())


@bot.message_handler(content_types='text',
                     func=lambda m: m.text == 'Посмотреть ответы' and check_its_teacher(m.from_user.id))
def admin_question_view(message):
    message_log_system(0, f"{message.chat.id} send {message.text}")
    if teacher.question is None:
        bot.send_message(message.chat.id, "Актуальных вопросов нет", reply_markup=teacher_main_menu())
        return

    res_text = get_question_info(teacher.question)
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


@bot.message_handler(commands=['register'])
def student_send_register(message):
    if teacher.flows_add is not None:
        student = database.search_user(message.from_user.id)
        if student is None:
            bot.send_message(message.chat.id, "Перед регистрацией в поток, необходимо зарегистрироваться в "
                                              "системе: /start", reply_markup=students_main_menu())
            return

        for other_tid in teacher.flows_add.students:
            if student.tid == other_tid:
                bot.send_message(message.chat.id, "Вы уже записаны в данном потоке", reply_markup=students_main_menu())
            else:
                teacher.flows_add.students.append(student.tid)
                bot.send_message(message.chat.id, f"Вы успешно добавлены в поток {teacher.flows_add.name}",
                                 reply_markup=students_main_menu())
                message_log_system(0, f"{student.full_name} from {student.group} registered to "
                                      f"{teacher.flows_add.name}")


@bot.message_handler(commands=['answer'])
def student_send_answer(message):
    data = message.text.split(' ', 1)
    if len(data) < 1:
        bot.send_message(message.chat.id, "Используйте /answer ответ",
                         reply_markup=students_main_menu())
    else:
        if teacher.question is not None and teacher.question.status:
            student = database.search_user(message.from_user.id)
            if student is None:
                bot.send_message(message.chat.id, "Чтобы пользоваться системой, вам необходимо зарегистрироваться: "
                                                  "/start", reply_markup=students_main_menu())
                return

            if database.check_student_in_flow(student.group, teacher.question.flow):
                for full_name, group, answer in teacher.question.answers:
                    if full_name == student.full_name and group == student.group:
                        bot.send_message(message.chat.id, "Вы уже отвечали на данный вопрос",
                                         reply_markup=students_main_menu())
                        return

                teacher.question.answers.append([student.full_name, student.group, data[1]])
                bot.send_message(message.chat.id, f"Ваш ответ `{data[1]}` успешно добавлен", reply_markup=students_main_menu())


@bot.message_handler(content_types='text')
def student_send_unknown(message):
    message_log_system(0, f"{message.chat.id} send {message.text}")
    if teacher.flows_add is None and teacher.question is None:
        student = database.search_user(message.from_user.id)
        if student is None:
            bot.send_message(message.chat.id, "Перед использованием бота, вам необходимо зарегистрироваться: /start")
    elif teacher.flows_add is not None:
        bot.send_message(message.chat.id, "Для добавления в поток, необходимо использовать команду: /register")
    elif teacher.question is not None and teacher.question.status:
        bot.send_message(message.chat.id, "Для ответа на вопрос, необходимо использовать команду /answer и ответ")
