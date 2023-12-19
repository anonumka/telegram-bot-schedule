from telebot import types

from app import bot, database
from app.modules.database import User


def student_full_name(message: types.Message):
    try:
        user = User
        user.full_name = message.text
        user.tid = message.from_user.id
        database.add_user(user)

        msg = bot.reply_to(message, "Теперь введите свою группу.\nНапример: КИ20-06б")
        bot.register_next_step_handler(msg, student_group)
    except Exception as e:
        bot.reply_to(message, f'Ошибка ввода во время создания студента: {e}')


def student_group(message: types.Message):
    try:
        user = database.search_user(message.from_user.id)
        user.group = message.text
        database.update_user_info(user)
        database.write_users_csv(user)

        chat_id = message.from_user.id
        bot.send_message(chat_id,
                         f"Вы успешно добавлены в базу со следующими данными:\n"
                         f"Имя:{user.full_name}, группа:{user.group}")
    except Exception as e:
        bot.reply_to(message, f'Ошибка ввода во время создания студента: {e}')

