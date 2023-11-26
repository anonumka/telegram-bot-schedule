import csv
import os
from datetime import datetime

from app.modules.json_parser import settings, flows
from app.modules.question_handler import Question

class Users:
    tid: int
    full_name: str
    group: str
    flow: str


def check_exist_teacher(tid: int):
    if settings["tid_teacher"] == "":
        settings["tid_teacher"] = tid
        return 0

    return 1

def check_its_teacher(tid: int):
    if settings["tid_teacher"] == tid:
        return 1

    return 0

def write_question_csv(question: Question):
    if not os.path.isdir("questions"):
        os.mkdir("questions")

    time = datetime.now().strftime("%Y-%m-%d_%H.%M")
    with open(f'questions/{time}.csv', 'w') as f:
        writer = csv.writer(f, delimiter=';')
        writer.writerows(question.answer)


class Database:
    def __init__(self):
        try:
            with open('users.csv') as f:
                reader = csv.reader(f, delimiter=';')
                self.users = list(reader)
        except IOError:
            print(f"Не удалось открыть файл: {IOError.strerror}.\nСоздаем пустой словарь.")
            self.users = []

        try:
            with open('flows.csv') as f:
                reader = csv.reader(f, delimiter=';')
                self.flows = list(reader)
        except IOError:
            print(f"Не удалось открыть файл: {IOError.strerror}.\nСоздаем пустой словарь.")
            self.flows = []

    def write_users_csv(self):
        try:
            with open('users.csv', 'w') as f:
                writer = csv.writer(f, delimiter=';')
                writer.writerows(self.users)
        except IOError:
            print(f"Не удалось открыть файл: {IOError.strerror}.\nКонец записи.")

    def add_flow(self, flow: []):
        self.flows.append(flow)

    def search_flow(self, search_name: str):
        for flow in self.flows:
            for name in flow[0]:
                if name == search_name:
                    return flow

    def update_flow(self, search_flow: []):
        for i in range(len(self.flows)):
            for j in range(len(self.flows[i])):
                if self.flows[i][j] == search_flow[0]:
                    self.flows[i] = search_flow

    def flow_list(self):
        return self.flows

    def write_flows_config(self, tid: int):
        new_settings = settings
        new_settings["tid_teacher"] = tid

    def search_user(self, tid: int):
        for user in self.users:
            if str(user.tid) == str(tid):
                return user

        return None

    def add_user(self, new_user: Users):
        user = [str(new_user.tid), new_user.full_name, new_user.group, new_user.flow]
        self.users.append(user)

    def update_user_info(self, new_user: Users):
        for user in self.users:
            if str(user.tid) == str(new_user.tid):
                user.full_name = new_user.full_name
                user.group = new_user.group
                user.flow = new_user.flow
                return

        self.add_user(new_user)

    def get_tid_students_flow(self, flows: []):
        user_list = []
        for user in self.users:
            for flow in flows:
                if user.flow == flow[0]:
                    user_list.append(user.tid)

        return user_list


    # TODO: Send file to YD
