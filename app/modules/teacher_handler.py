from app import bot, db
from app.modules.markup_handler import teacher_main_menu
from app.modules.question_handler import Question
from app.modules.students_handler import start_question
from app.modules.database import Flow

from telebot import types


class TeacherHandler:

    def __init__(self):
        self.flows_arr = []
        self.questions_arr = []
        self.flows_del = []

    def teacher_start_create_flow(self, message: types.Message):
        try:
            # TODO: Исправить ввод flow и question
            flow = Flow()
            flow.name = message.text
            self.flows_arr.append(flow)

            msg = bot.reply_to(message, "Перечислите группы в потоке"
                                        ".\nНапример: КИ20-06б, КИ20-07б, КИ20-08б")
            bot.register_next_step_handler(msg, self.teacher_end_create_flow)
        except Exception as e:
            bot.reply_to(message, f'Ошибка в создании потока: {e}')

    def teacher_end_create_flow(self, message: types.Message):
        try:
            # TODO: Проверка входной строки
            groups_list: str = message.text
            flow = self.flows_arr[-1]
            flow.groups = groups_list
            db.add_flow(flow)
            self.flows_arr.clear()

            chat_id = message.from_user.id
            bot.send_message(chat_id, "Поток добавлен успешно", reply_markup=teacher_main_menu())
        except Exception as e:
            bot.reply_to(message, f'Ошибка в создании потока: {e}')

    def teacher_delete_flow(self, message: types.Message):
        try:
            # TODO: Проверка входной строки
            flow_delete = message.text
            self.flows_del.append(flow_delete)

            msg = bot.reply_to(message, "Вы уверены в удалении потока? (Да/нет)")
            bot.register_next_step_handler(msg, self.teacher_delete_flow)
        except Exception as e:
            bot.reply_to(message, f'Ошибка в удалении потока: {e}')

    def teacher_delete_flow_accept(self, message: types.Message):
        try:
            # TODO: Проверка входной строки
            flow_delete = self.flows_del[-1]
            db.remove_flow(flow_delete)
            self.flows_del.clear()

            chat_id = message.from_user.id
            bot.send_message(chat_id, "Успех", reply_markup=teacher_main_menu())
        except Exception as e:
            bot.reply_to(message, f'Ошибка в удалении потока: {e}')

    def teacher_create_question(self, message: types.Message):
        try:
            # TODO: Проверка входной строки
            question = Question()
            question.flow = message.text
            self.questions_arr.append(question)

            msg = bot.reply_to(message, "Какой вопрос задать студентам?")
            bot.register_next_step_handler(msg, self.teacher_question_name)
        except Exception as e:
            bot.reply_to(message, f'Ошибка в создании вопроса: {e}')

    def teacher_question_name(self, message: types.Message):
        try:
            # TODO: Проверка входной строки
            question = self.questions_arr[-1]
            question.name = message.text
            self.questions_arr[-1] = question

            msg = bot.reply_to(message, "Задайте время в минутах")
            bot.register_next_step_handler(msg, self.teacher_question_timer)
        except Exception as e:
            bot.reply_to(message, f'Ошибка в создании вопроса: {e}')

    def teacher_question_timer(self, message: types.Message):
        try:
            # TODO: Проверка входной строки
            question = self.questions_arr[-1]
            question.time = int(message.text)
            start_question(question)

            chat_id = message.from_user.id
            bot.send_message(chat_id, "Вопрос успешно создан и выслан студентам")
        except Exception as e:
            bot.reply_to(message, f'Ошибка в создании вопроса: {e}')
