from telebot import types

from app import bot, database
from app.modules.database import User
from app.modules.markup_handler import students_main_menu
from app.modules.logger import message_log_system


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
        message_log_system(2, f"Failed creation a student: {e}")


def student_group(message: types.Message):
    try:
        user = database.search_user(message.from_user.id)
        user.group = message.text
        database.update_user_info(user)
        database.write_users_csv()

        message_log_system(0, f"New student: `{user.full_name}` from `{user.group}`")

        chat_id = message.from_user.id
        bot.send_message(chat_id,
                         f"Вы успешно добавлены в базу со следующими данными:\n"
                         f"Имя:{user.full_name}, группа:{user.group}")
    except Exception as e:
        bot.reply_to(message, f'Ошибка ввода во время создания студента: {e}')
        message_log_system(2, f"Failed creation a student: {e}")


def student_change_about_me(message: types.Message):
    try:
        if check_back_button(message):
            return

        answer = message.text
        if answer == "ФИО":
            msg = bot.reply_to(message, "Теперь введите новое ФИО")
            bot.register_next_step_handler(msg, student_change_full_name)
        elif answer == "Группу":
            msg = bot.reply_to(message, "Теперь введите новую группу")
            bot.register_next_step_handler(msg, student_change_group)
        else:
            msg = bot.reply_to(message, "Неверно введен текст. Введите ФИО или Группу")
            bot.register_next_step_handler(msg, student_change_about_me)
    except Exception as e:
        bot.reply_to(message, f'Ошибка ввода во изменения данных о студенте: {e}')
        message_log_system(2, f"Failed change info about student: {e}")


def student_change_full_name(message: types.Message):
    try:
        if check_back_button(message):
            return

        new_full_name = message.text
        user = database.search_user(message.from_user.id)
        old_full_name = user.full_name
        user.full_name = new_full_name
        database.update_user_info(user)
        database.write_users_csv()

        message_log_system(0, f"Student `{old_full_name}` change full name on `{new_full_name}`")

        chat_id = message.from_user.id
        bot.send_message(chat_id,
                         f"Вы успешно поменяли о себе информацию:\n"
                         f"Имя:{user.full_name}, группа:{user.group}")
    except Exception as e:
        bot.reply_to(message, f'Произошла ошибка: {e}')
        message_log_system(2, f"Failed change full name of student: {e}")


def student_change_group(message: types.Message):
    try:
        if check_back_button(message):
            return

        new_group = message.text
        user = database.search_user(message.from_user.id)
        old_group = user.group
        user.group = new_group
        database.update_user_info(user)
        database.write_users_csv()

        message_log_system(0, f"Student `{user.full_name}` change "
                              f"group from `{old_group}` on `{new_group}`")

        chat_id = message.from_user.id
        bot.send_message(chat_id,
                         f"Вы успешно поменяли о себе информацию:\n"
                         f"Имя:{user.full_name}, группа:{user.group}")
    except Exception as e:
        bot.reply_to(message, f'Произошла ошибка: {e}')
        message_log_system(2, f"Failed change group of student: {e}")
