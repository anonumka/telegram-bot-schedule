from app.modules.database import Users
from app import bot, db


def teacher_full_name(message):
    try:
        chat_id = message.chat.id
        user = Users
        user.full_name = message.text
        user.tid = message.from_user.id
        user.flow = user.group = "Преподаватель"
        bot.send_message(chat_id, "Отлично! Далее следует заняться добавлением потоков")
        db.add_user(user)
    except Exception as e:
        bot.reply_to(message, 'oooops')
