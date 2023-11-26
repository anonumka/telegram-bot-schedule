from app import bot, db
from app.modules.markup_handler import teacher_main_menu
from app.modules.question import Question

from telebot import types


class TeacherHandler:
    def __init__(self):
        self.question = Question()
        self.flow = []

    def teacher_start_create_flow(self, message: types.Message):
        try:
            chat_id = message.from_user.id
            msg = bot.reply_to(message, "Перечислите группы в потоке"
                                        ".\nНапример: КИ20-06б, КИ20-07б, КИ20-08б")
            self.flow.append(message.text)
            bot.register_next_step_handler(msg, self.teacher_end_create_flow)
        except Exception as e:
            bot.reply_to(message, 'Error in time craete a flow')

    def teacher_end_create_flow(self, message: types.Message):
        try:
            chat_id = message.from_user.id
            bot.send_message(chat_id, "Поток добавлен успешно", reply_markup=teacher_main_menu())

            groups_list: str = message.text
            db.add_flow([self.flow[-1], groups_list])
        except Exception as e:
            bot.reply_to(message, 'Error in time craete a flow')

    def teacher_create_question(self, message: types.Message):
        try:
            chat_id = message.from_user.id
            self.question.flow = message.text
            msg = bot.reply_to(message, "Какой вопрос задать студентам?")
            bot.register_next_step_handler(msg, self.teacher_question_name)
        except Exception as e:
            bot.reply_to(message, 'oooops')

    def teacher_question_name(self, message: types.Message):
        try:
            chat_id = message.from_user.id
            self.question.name = message.text
            msg = bot.reply_to(message, "Задайте время в минутах")
            bot.register_next_step_handler(msg, self.teacher_question_timer)
        except Exception as e:
            bot.reply_to(message, 'oooops')

    def teacher_question_timer(self, message: types.Message):
        try:
            chat_id = message.from_user.id
            bot.send_message(chat_id, "Вопрос успешно создан и выслан студентам")
            self.question.timer = message.text
            self.question.start()
        except Exception as e:
            bot.reply_to(message, 'oooops')

