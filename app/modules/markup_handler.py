from telebot.types import ReplyKeyboardMarkup, KeyboardButton


def teacher_main_menu():
    markup = ReplyKeyboardMarkup(resize_keyboard=True)
    item1 = KeyboardButton('Потоки')
    item2 = KeyboardButton('Вопросы')
    markup.add(item1, item2)
    print(markup)
    return markup


def teacher_flows_button():
    markup = ReplyKeyboardMarkup(resize_keyboard=True)
    item1 = KeyboardButton('Добавить поток')
    item2 = KeyboardButton('Удалить поток')
    markup.add(item1, item2)
    return markup


def teacher_question_button():
    markup = ReplyKeyboardMarkup(resize_keyboard=True)
    item1 = KeyboardButton('Задать вопрос')
    item2 = KeyboardButton('Ответы на вопрос')
    markup.add(item1, item2)
    return markup


def teacher_get_flows(flows: []):
    markup = ReplyKeyboardMarkup(resize_keyboard=True)
    flow_list = []
    for flow in flows:
        flow_list.append(flow.name)

    return markup.row(*flow_list)
