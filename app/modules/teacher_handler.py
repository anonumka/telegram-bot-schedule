import time

from app import bot, database
from app.modules.markup_handler import teacher_main_menu, teacher_accept_button, only_back_button, \
                                        create_keyboard_layout
from app.modules.question_handler import Question
from app.modules.database import Flow
from app.modules.logger import message_log_system

from telebot import types
from datetime import datetime


class TeacherHandler:

    def __init__(self):
        self.flows_add = None
        self.question = None
        self.flows_del = None

    def check_back_button(self, message) -> bool:
        if message.text == "Назад":
            self.flows_add = None
            self.flows_del = None

            bot.clear_step_handler_by_chat_id(chat_id=message.chat.id)
            bot.reply_to(message, "Выберите действие", reply_markup=teacher_main_menu())
            return True
        return False

    def teacher_create_flow(self, message: types.Message, name_flow: str = None) -> None:
        flow = Flow()
        flow.name = name_flow if name_flow is not None else message.text
        if self.flows_add is not None:
            bot.send_message(message.chat.id, f"Еще действует регистрация в поток {self.flows_add.name}")
            bot.reply_to(message, "Выберите действие", reply_markup=teacher_main_menu())
        elif self.question is not None and self.question.status:
            bot.send_message(message.chat.id, "Запрещено редактировать потоки во время активного вопроса")
            bot.reply_to(message, "Выберите действие", reply_markup=teacher_main_menu())
        else:
            self.flows_add = flow
            chat_id = message.from_user.id
            try:
                bot.send_message(chat_id, "Поток создан. Студентам даётся пять минут на регистрацию",
                                 reply_markup=teacher_main_menu())
                time.sleep(60.0 * 5)
                database.add_flow(self.flows_add)
                self.flows_add = None
            except Exception as e:
                bot.reply_to(message, f'Ошибка в отправки сообщения: {e}')
                message_log_system(2, f"Failed creation a flow: {e}")


    def teacher_delete_flow(self, message: types.Message, flow_name: str = None) -> None:
        flow_delete = flow_name if not None else message.text
        if self.check_back_button(message):
            return
        elif database.search_flow(flow_delete) is None:
             bot.reply_to(message, "Данного потока не существует", reply_markup=teacher_accept_button())
        elif self.question is not None and self.question.status:
            bot.send_message(message.chat.id, "Запрещено редактировать потоки во время активного вопроса")
            bot.reply_to(message, "Выберите действие", reply_markup=teacher_main_menu())
        else:
            if len(self.flows_del) == 0:
                self.flows_del.append(flow_delete)
            else:
                self.flows_del[-1] = flow_delete
            try:
                msg = bot.reply_to(message, "Вы уверены в удалении потока? (Да/нет)", reply_markup=teacher_accept_button())
                bot.register_next_step_handler(msg, self.teacher_delete_flow_accept)
            except Exception as e:
                bot.reply_to(message, f'Ошибка в удалении потока: {e}')
                message_log_system(2, f"Failed deleting a flow: {e}")


    def teacher_delete_flow_accept(self, message: types.Message):
        try:
            if self.check_back_button(message):
                return

            chat_id = message.from_user.id
            if message.text.lower() == "да":
                flow_delete = self.flows_del[-1]
                database.remove_flow(flow_delete)
                bot.send_message(chat_id, "Успех.", reply_markup=teacher_main_menu())

                message_log_system(0, f"{message.chat.id} remove a flow `{flow_delete}`")
            elif message.text.lower() == "нет":
                bot.send_message(chat_id, "Отмена.", reply_markup=teacher_main_menu())
            else:
                bot.send_message(chat_id, "Неверный ввод текста. Повторите попытку.",
                                 reply_markup=teacher_accept_button())
                msg = bot.reply_to(message, "Вы уверены в удалении потока? (Да/нет)")
                bot.register_next_step_handler(msg, self.teacher_delete_flow_accept)
                return

            self.flows_del.clear()
        except Exception as e:
            bot.reply_to(message, f'Ошибка в удалении потока: {e}')
            message_log_system(2, f"Failed deleting a flow: {e}")

    def teacher_create_question(self, message: types.Message):
        try:
            if self.check_back_button(message):
                return

            elif self.question is not None and self.question.status:
                bot.clear_step_handler_by_chat_id(chat_id=message.chat.id)
                bot.reply_to(message, "Запрещено создавать вопросы, когда один из них активен",
                             reply_markup=teacher_main_menu())
                return

            if database.search_flow(message.text) is None:
                bot.reply_to(message, "Данного потока не существует", reply_markup=only_back_button())
                return

            question = Question()
            question.flow = message.text
            self.question = question

            msg = bot.reply_to(message, "Какой вопрос задать студентам?", reply_markup=only_back_button())
            bot.register_next_step_handler(msg, self.teacher_question_name)
        except Exception as e:
            bot.reply_to(message, f'Ошибка в создании вопроса: {e}')
            message_log_system(2, f"Failed creation a question: {e}")


    def teacher_remove_question_flow(self, message: types.Message):
        try:
            if self.check_back_button(message):
                return

            elif self.question is not None and self.question.status:
                bot.clear_step_handler_by_chat_id(chat_id=message.chat.id)
                bot.reply_to(message, "Запрещено удалять вопросы, когда один из них активен",
                             reply_markup=teacher_main_menu())
                return

            if database.search_flow(message.text) is None:
                bot.reply_to(message, "Данного потока не существует", reply_markup=only_back_button())
                return

            question = Question()
            question.flow = message.text
            self.question = question

            msg = bot.reply_to(message, "На какую дату необходимо удалить вопрос?",
                               reply_markup=create_keyboard_layout(database.dates_questions_of_flow(question.flow),
                                                                   back_button=True))
            bot.register_next_step_handler(msg, self.teacher_remove_question_date)
        except Exception as e:
            bot.reply_to(message, f'Ошибка в создании вопроса: {e}')
            message_log_system(2, f"Failed creation a question: {e}")


    def teacher_remove_question_date(self, message: types.Message):
        try:
            if self.check_back_button(message):
                return

            flow = self.question.flow
            date = message.text
            try:
                datetime.strptime(date, "%d.%m.%Y")
            except ValueError:
                bot.reply_to(message, "Неверно введена дата. Пример: дд.мм.гггг", reply_markup=teacher_main_menu())
                return

            question = database.search_question(self.question.flow, date)
            if question is None:
                bot.reply_to(message, f"Вопрос для потока {flow} на {date} не найден", reply_markup=teacher_main_menu())
                return

            database.delete_question(question)
            self.question = None
            bot.reply_to(message, "Вопрос успешно удалён", reply_markup=teacher_main_menu())
        except Exception as e:
            bot.reply_to(message, f'Ошибка в создании вопроса: {e}')
            message_log_system(2, f"Failed creation a question: {e}")


    def teacher_question_name(self, message: types.Message):
        try:
            if self.check_back_button(message):
                return

            self.question.question = message.text

            msg = bot.reply_to(message, "Какой правильный ответ на данный вопрос?", reply_markup=only_back_button())
            bot.register_next_step_handler(msg, self.teacher_question_answer)
        except Exception as e:
            bot.reply_to(message, f'Ошибка в создании вопроса: {e}')
            message_log_system(2, f"Failed creation a question: {e}")

    def teacher_question_answer(self, message: types.Message):
        try:
            if self.check_back_button(message):
                return

            self.question.answer = message.text
            msg = bot.reply_to(message, "Задайте дату, когда задать вопрос в формате: дд.мм.гггг",
                               reply_markup=only_back_button())
            bot.register_next_step_handler(msg, self.teacher_question_date)
        except Exception as e:
            bot.reply_to(message, f'Ошибка в создании вопроса: {e}')
            message_log_system(2, f"Failed creation a question: {e}")

    def teacher_question_date(self, message: types.Message):
        if self.check_back_button(message):
            return

        answer = message.text
        try:
            datetime.strptime(answer, "%d.%m.%Y")
        except ValueError:
            msg = bot.reply_to(message, "Неверно введена дата. Пример: дд.мм.гггг", reply_markup=only_back_button())
            bot.register_next_step_handler(msg, self.teacher_question_date)
            return

        self.question.date = answer
        if database.search_question(self.question.flow, answer) is not None:
            bot.reply_to(message, f"На {answer} у потока {self.question.flow} уже запланирован вопрос: "
                                  f"'{self.question.question}'", reply_markup=teacher_main_menu())
            return


        message_log_system(0, f"{message.chat.id} create a question "
                              f"`{self.question.question}` with answer `{self.question.answer}` for "
                              f"`{self.question.flow}` on `{self.question.date}`.")

        database.add_question(self.question)
        self.question = None

        try:
            bot.reply_to(message, "Вопрос создан", reply_markup=only_back_button())
        except Exception as e:
            bot.reply_to(message, f'Ошибка в создании вопроса: {e}')
            message_log_system(2, f"Failed creation a question: {e}")


    def teacher_start_question(self, message: types.Message, name_flow: str = None):
        try:
            if self.check_back_button(message):
                return

            elif self.question is not None and self.question.status:
                bot.clear_step_handler_by_chat_id(chat_id=message.chat.id)
                bot.reply_to(message, "Запрещено задавать вопросы, пока создается или активен другой",
                             reply_markup=teacher_main_menu())
                return

            flow_name = name_flow if name_flow is not None else message.text
            flow = database.search_flow(flow_name)
            if flow is None:
                bot.reply_to(message, f"Поток {flow_name} не найден", reply_markup=teacher_main_menu())
                return

            date = datetime.today().strftime('%d.%m.%Y')
            self.question = database.search_question(flow_name, date)
            if self.question is None:
                bot.reply_to(message, "Вопроса на данный день и поток не сущесвтует", reply_markup=teacher_main_menu())
                return

            self.question.start_question()
            for tid in flow.students:
                bot.send_message(tid, f"Вопрос: {self.question.question}\nНа ответ вам даётся 5 минут.")
                message_log_system(0, f"User {tid} recieved question {self.question.question}")

            bot.reply_to(message, "Вопрос отправлен", reply_markup=teacher_main_menu())

            time.sleep(300.0)
            if self.question.status is True:
                self.question.stop_question()

            database.delete_question(self.question)
            bot.reply_to(message, f"На вопрос ответили {len(self.question.answers)}, где правильных ответов "
                                  f"{self.question.get_count_right_answers()}", reply_markup=teacher_main_menu())
        except Exception as e:
            bot.reply_to(message, f'Ошибка в создании вопроса: {e}')
            message_log_system(2, f"Failed start a question: {e}")


def add_question(question_info: [], message: types.Message) -> None:
    flow, date, question, answer = question_info

    question = Question()
    if database.search_flow(flow) is None:
        bot.reply_to(message, f"Поток {flow} не существует", reply_markup=teacher_main_menu())
        return
    question.flow = flow

    try:
        datetime.strptime(date, "%d.%m.%Y")
    except ValueError:
        bot.reply_to(message, "Неверно введена дата. Пример: дд.мм.гггг", reply_markup=teacher_main_menu())
        return

    if datetime.today().strftime("%d.%m.%Y") > date:
        bot.reply_to(message, "Запрещено создвать вопросы на прошедшие даты", reply_markup=teacher_main_menu())
        return
    question.date = date

    question_planned = database.search_question(flow, date)
    if question_planned is not None:
        bot.reply_to(message, f"На {date} у потока {flow} уже запланирован вопрос {question_planned.question}",
                     reply_markup=teacher_main_menu())
        return

    question.question = question
    question.answer = answer

    database.add_question(question)
    message_log_system(0, f"{message.chat.id} create a question "
                          f"`{question.question}` with answer `{question.answer}` for "
                          f"`{question.flow}` on {question.date}.")
    bot.reply_to(message, f"Вопрос `{question.question}` с ответом `{question.answer}` для потока "
                          f"`{question.flow}` на {question.date} успешно создан.", reply_markup=teacher_main_menu())
    return

def rem_question(question_info: [], message: types.Message):
    flow, date = question_info

    if database.search_flow(flow) is None:
        bot.reply_to(message, f"Поток {flow} не существует", reply_markup=teacher_main_menu())
        return

    try:
        datetime.strptime(date, "%d.%m.%Y")
    except ValueError:
        bot.reply_to(message, "Неверно введена дата. Пример: дд.мм.гггг", reply_markup=teacher_main_menu())
        return

    question = database.search_question(flow, date)
    if question is None:
        bot.reply_to(message, f"Вопрос для потока {flow} на {date} не найден", reply_markup=teacher_main_menu())
        return

    database.delete_question(question)
    bot.reply_to(message, "Успех", reply_markup=teacher_main_menu())
    return
