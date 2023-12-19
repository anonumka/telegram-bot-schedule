from telebot import types

from app import bot, database
from app.modules.database import User
from app.modules.markup_handler import students_main_menu


def check_back_button(message):
    if message.text == "Назад":
        bot.clear_step_handler_by_chat_id(chat_id=message.chat.id)
        bot.reply_to(message, "Выберите действие", reply_markup=students_main_menu())
        return 1
    return 0


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


def student_change_about_me(message: types.Message):
    try:
        if check_back_button(message):
            return

        answer = message.text
        if answer == "ФИО":
            msg = bot.reply_to(message, "Теперь введите новое ФИО")
            bot.register_next_step_handler(msg, student_group)
        elif answer == "Группу":
            msg = bot.reply_to(message, "Теперь введите новую группу")
            bot.register_next_step_handler(msg, student_group)
    except Exception as e:
        bot.reply_to(message, f'Ошибка ввода во время создания студента: {e}')


def student_change_full_name(message: types.Message):
    try:
        if check_back_button(message):
            return

        new_full_name = message.text
        user = database.search_user(message.from_user.id)
        user.full_name = new_full_name
        database.update_user_info(user)
        database.write_users_csv(user)

        chat_id = message.from_user.id
        bot.send_message(chat_id,
                         f"Вы успешно поменяли о себе информацию:\n"
                         f"Имя:{user.full_name}, группа:{user.group}")
    except Exception as e:
        bot.reply_to(message, f'Ошибка ввода во время создания студента: {e}')


def student_change_group(message: types.Message):
    try:
        if check_back_button(message):
            return

        new_group = message.text
        user = database.search_user(message.from_user.id)
        user.group = new_group
        database.update_user_info(user)
        database.write_users_csv(user)

        chat_id = message.from_user.id
        bot.send_message(chat_id,
                         f"Вы успешно поменяли о себе информацию:\n"
                         f"Имя:{user.full_name}, группа:{user.group}")
    except Exception as e:
        bot.reply_to(message, f'Ошибка ввода во время создания студента: {e}')
