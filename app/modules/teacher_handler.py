import time

from app import bot, database
from app.modules.markup_handler import teacher_main_menu, teacher_accept_button, only_back_button
from app.modules.question_handler import Question
from app.modules.database import Flow, add_marks_to_table_performance
from app.modules.logger import message_log_system

from telebot import types


class TeacherHandler:

    def __init__(self):
        self.flows_add = None
        self.questions_arr = []
        self.flows_del = None

    def check_back_button(self, message) -> bool:
        if message.text == "Назад":
            self.flows_add.clear()
            self.flows_del.clear()
            self.questions_arr.clear()

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
        elif len(self.questions_arr) > 0 and self.questions_arr[-1].status:
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
        elif not database.search_flow(flow_delete):
             bot.reply_to(message, "Данного потока не существует", reply_markup=teacher_accept_button())
        elif len(self.questions_arr) > 0 and self.questions_arr[-1].status:
            bot.send_message(message.chat.id, "Запрещено редактировать потоки во время активного вопроса")
            bot.reply_to(message, "Выберите действие", reply_markup=teacher_main_menu())
        else:
            if not database.search_flow(flow_delete):
                bot.reply_to(message, "Данного потока не существует", reply_markup=teacher_accept_button())
                return

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

            if len(self.questions_arr) > 0:
                bot.clear_step_handler_by_chat_id(chat_id=message.chat.id)
                bot.reply_to(message, "Дождитеcь конца прошлого вопроса", reply_markup=teacher_main_menu())
                return

            if not database.search_flow(message.text):
                bot.reply_to(message, "Данного потока не существует", reply_markup=only_back_button())
                return

            question = Question()
            question.flow = message.text
            self.questions_arr.append(question)

            msg = bot.reply_to(message, "Какой вопрос задать студентам?", reply_markup=only_back_button())
            bot.register_next_step_handler(msg, self.teacher_question_name)
        except Exception as e:
            bot.reply_to(message, f'Ошибка в создании вопроса: {e}')
            message_log_system(2, f"Failed creation a question: {e}")

    def teacher_question_name(self, message: types.Message):
        try:
            if self.check_back_button(message):
                return

            question = self.questions_arr[-1]
            question.name = message.text
            self.questions_arr[-1] = question

            msg = bot.reply_to(message, "Какой правильный ответ на данный вопрос?", reply_markup=only_back_button())
            bot.register_next_step_handler(msg, self.teacher_question_answer)
        except Exception as e:
            bot.reply_to(message, f'Ошибка в создании вопроса: {e}')
            message_log_system(2, f"Failed creation a question: {e}")

    def teacher_question_answer(self, message: types.Message):
        try:
            if self.check_back_button(message):
                return

            question = self.questions_arr[-1]
            question.answer = message.text
            self.questions_arr[-1] = question

            msg = bot.reply_to(message, "Задайте время в минутах", reply_markup=only_back_button())
            bot.register_next_step_handler(msg, self.teacher_question_timer)
        except Exception as e:
            bot.reply_to(message, f'Ошибка в создании вопроса: {e}')
            message_log_system(2, f"Failed creation a question: {e}")

    def teacher_question_timer(self, message: types.Message):
        try:
            if self.check_back_button(message):
                return

            answer = message.text
            if not answer.isdigit() or int(answer) < 0:
                msg = bot.reply_to(message, "Используйте целое положительное число для установки минут",
                                   reply_markup=only_back_button())
                bot.register_next_step_handler(msg, self.teacher_question_timer)
                return

            question = self.questions_arr[-1]
            question.time = int(answer)
            chat_id = message.from_user.id

            message_log_system(0, f"{message.chat.id} create a question "
                                  f"`{question.name}` with answer `{question.answer}` for "
                                  f"`{question.flow}` on `{question.time}` minutes.")

            tid_list = database.get_tid_students_flow(question.flow)
            for tid in tid_list:
                bot.send_message(tid, f"Вопрос: {question.name}\nНа ответ вам {question.time} минут.")

            status = question.start_question()
            bot.send_message(chat_id, status, reply_markup=teacher_main_menu())
            time.sleep(60.0 * question.time)
            add_marks_to_table_performance(question)

            self.questions_arr.clear()

        except Exception as e:
            bot.reply_to(message, f'Ошибка в создании вопроса: {e}')
            message_log_system(2, f"Failed creation a question: {e}")
