# Telegram-Bot-Schedule

Бот, позволяющий задавать вопросы студентам.

# Описание

После запуска бота, первый человек, написавший команду `/start`
становится преподавателем (он же admin). Последующие - студенты.
Преподаватель в системе может быть только один.

Регистрация в поток происходит следующим образом: преподаватель
создает поток, например `/flow add ОПППО 2022`, затем пять минут
идёт регистрация студентов: для этого им нужно написать `/register`
(если студент не успел, то преподаватель должен вручную его добавить
в файл `flows.csv`)

Преподаватель задает вопросы для потока. Далее рассылается 
вопрос всем студентам, которые входят в этот поток по признаку 
группы. На вопрос даётся 5 минут. Для ответа студентам необходимо
написать `/answer` и затем написать ответ. Регистр ответа неважен.

Если студент не ответил на текущий вопрос или на прошлые, то его
оценка равна 0. Если ответ студента совпадает с правильным, тогда 
ему в успеваемости ставится 1. После того, как время у вопроса выйдет,
таблица с текущей успеваемостью отправляется в Яндекс Диск.

В Яндекс Диске будет создана папка `ScheduleBot`, куда будут 
складываться текущие таблицы успеваемости потока. Если токен не указан,
то сохранение в ЯД отменится.

# Используемые термины

`Flow` - список студентов (название;студенты)

`Question` - вопрос, задаваемый студентам по потоку

`Teacher` - преподаватель, который задает вопросы студентам

`Student` - ученик, получаемый вопросы от преподавателя

`tid` - Telegram ID - уникальный идентификатор пользователя

# Окружение

Для создания окружения в корневом каталоге запускаем следующее:

```shell
python3 -m venv .venv
source ./.venv/bin/activate
pip install -r requirements.txt
```

Если вы планируете запускать бота из-под Windows, используйте
пакет [win-unicode-console](https://pypi.org/project/win_unicode_console/)

# Настройка конфига

Перед запуском бота необходимо настроить конфигурационный файл:

`bot_token` - токен, получаемый у [@BotFather](https://t.me/BotFather)

`yandex_token` - получаем токен по следующей [инструкции](https://ramziv.com/article/2)

`tid_teacher` - добавляемый параметр после первого успешного запуска бота, добавлять не нужно

# Настройка прав Яндекс Токена

Во время создания токена, необходимо выбрать следующие права:
- Доступ к папке приложения на Диске
- Чтение всего Диска
- Запись в любом месте на диске

# Запуск

Для запуска бота в терминале выполнить следующую команду:

```shell
python3 -m app
```
