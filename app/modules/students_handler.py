from app.modules.database import Users
from app import bot, db

from telebot import types


def student_full_name(message: types.Message):
    try:
        chat_id = message.from_user.id
        user = Users
        user.full_name = message.text
        user.tid = message.from_user.id
        msg = bot.reply_to(message, "Теперь введите свою группу.\nНапример: КИ20-06б")
        bot.register_next_step_handler(msg, student_group)
        db.add_user(user)
    except Exception as e:
        bot.reply_to(message, 'oooops')


def student_group(message: types.Message):
    try:
        chat_id = message.from_user.id
        user = db.search_user(message.from_user.id)
        user.group = message.text
        msg = bot.reply_to(message, "Теперь введите свой поток.\nНапример: КИ20 ИВТ")
        bot.register_next_step_handler(msg, student_flow)
        db.update_user_info(user)
    except Exception as e:
        bot.reply_to(message, 'oooops')


def student_flow(message: types.Message):
    try:
        chat_id = message.from_user.id
        user = db.search_user(message.from_user.id)
        user.flow = message.text
        bot.send_message(chat_id, f"Вы успешно добавлены в базу со следующими данными:\nИмя:{user.full_name}, группа:{user.group}, поток:{user.flow}")
        db.update_user_info(user)
    except Exception as e:
        bot.reply_to(message, 'oooops')

