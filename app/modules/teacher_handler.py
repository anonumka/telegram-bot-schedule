from app import bot, db
from app.modules.markup_handler import teacher_main_menu
from app.modules.question_handler import Question
from app.modules.students_handler import start_question
from app.modules.database import Flow

from telebot import types


class TeacherHandler:

    def __init__(self):
        self.question = Question()
        self.flow = Flow()

    def teacher_start_create_flow(self, message: types.Message):
        try:
            chat_id = message.from_user.id
            msg = bot.reply_to(message, "Перечислите группы в потоке"
                                        ".\nНапример: КИ20-06б, КИ20-07б, КИ20-08б")

            self.flow.id = db.get_count_flows()
            self.flow.name = message.text
            bot.register_next_step_handler(msg, self.teacher_end_create_flow)
        except Exception as e:
            bot.reply_to(message, f'Ошибка в создании потока: {e}')

    def teacher_end_create_flow(self, message: types.Message):
        try:
            chat_id = message.from_user.id
            bot.send_message(chat_id, "Поток добавлен успешно", reply_markup=teacher_main_menu())

            groups_list: str = message.text
            self.flow.groups = groups_list
            db.add_flow(self.flow)
        except Exception as e:
            bot.reply_to(message, f'Ошибка в создании потока: {e}')

    def teacher_create_question(self, message: types.Message):
        try:
            chat_id = message.from_user.id
            self.question.flow = message.text
            msg = bot.reply_to(message, "Какой вопрос задать студентам?")
            bot.register_next_step_handler(msg, self.teacher_question_name)
        except Exception as e:
            bot.reply_to(message, f'Ошибка в создании вопроса: {e}')

    def teacher_question_name(self, message: types.Message):
        try:
            chat_id = message.from_user.id
            self.question.name = message.text
            msg = bot.reply_to(message, "Задайте время в минутах")
            bot.register_next_step_handler(msg, self.teacher_question_timer)
        except Exception as e:
            bot.reply_to(message, f'Ошибка в создании вопроса: {e}')

    def teacher_question_timer(self, message: types.Message):
        try:
            chat_id = message.from_user.id
            bot.send_message(chat_id, "Вопрос успешно создан и выслан студентам")
            self.question.time = int(message.text)
            start_question(self.question)
        except Exception as e:
            bot.reply_to(message, f'Ошибка в создании вопроса: {e}')

