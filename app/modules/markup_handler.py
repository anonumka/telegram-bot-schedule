from telebot.types import ReplyKeyboardMarkup, KeyboardButton


def create_keyboard_layout(items: [], additional_buttons=None, back_button=False):
    if additional_buttons is None:
        additional_buttons = []
    markup = ReplyKeyboardMarkup(row_width=1, resize_keyboard=True)

    row = []
    row_num = 0
    for count, item in enumerate(items, 1):
        row.append(KeyboardButton(text=item))
        if count % 3 == 0:
            markup.row(*row)
            row_num += 1
            row = []
    if row:
        markup.row(*row)

    for button in additional_buttons:
        markup.add(KeyboardButton(text=button))

    if back_button:
        markup.add(KeyboardButton(text="Назад"))

    return markup


def teacher_main_menu():
    items = ['Потоки', 'Вопросы']
    return create_keyboard_layout(items, back_button=False)


def teacher_flows_button():
    items = ['Добавить поток', 'Удалить поток']
    return create_keyboard_layout(items, back_button=True)


def teacher_accept_button():
    items = ['Да', 'Нет']
    return create_keyboard_layout(items, back_button=True)


def teacher_question_button():
    items = ['Задать вопрос', 'Посмотреть ответы']
    return create_keyboard_layout(items, back_button=True)


def teacher_get_flows(flows: dict):
    return create_keyboard_layout(list(flows), back_button=True)


def students_main_menu():
    items = ['Поменять информацию о себе']
    return create_keyboard_layout(items, back_button=False)


def students_change_about_me_buttons():
    items = ['ФИО', 'Группу']
    return create_keyboard_layout(items, back_button=True)


def only_back_button():
    return create_keyboard_layout([], back_button=True)
