import json
from app.modules.logger import message_log_system

input_file = open('config.json')
settings = json.load(input_file)
input_file.close()


def write_config(data):
    with open('config.json', 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=4)


def check_exist_teacher(tid: int):
    if settings["tid_teacher"] == "":
        settings["tid_teacher"] = tid
        write_config(settings)
        message_log_system(0, f"{tid} now is teacher")
        return 0

    return 1


def check_its_teacher(tid: int):
    return 1 if settings["tid_teacher"] == tid else 0
