import csv
import os
from datetime import datetime

from app.modules.json_parser import settings, write_config
from app.modules.question_handler import Question


class User:
    tid: int
    full_name: str
    group: str
    flow: str


class Flow:
    name: str
    groups: str


def check_exist_teacher(tid: int):
    if settings["tid_teacher"] == "":
        settings["tid_teacher"] = tid
        write_config(settings)
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
    try:
        with open(f'questions/{time}.csv', 'w') as f:
            writer = csv.writer(f, delimiter=';')
            field = ["full_name", "group", "answer"]
            writer.writerow(field)
            for answer in question.answers:
                writer.writerow([answer[0], answer[1], answer[2]])
    except IOError:
        print(f"Не удалось открыть файл: {IOError.strerror}.\nКонец записи.")


class Database:
    def __init__(self):
        self.users = []
        try:
            with open('users.csv') as f:
                reader = csv.reader(f, delimiter=';')
                tmp = list(reader)
                len_reader = len(tmp)
                if len_reader > 1:
                    for i in range(len(tmp) - 1):
                        if len(tmp[i + 1]) == 2:
                            user = User()
                            user.tid = tmp[i + 1][0]
                            user.full_name = tmp[i + 1][1]
                            user.group = tmp[i + 1][2]
                            user.flow = tmp[i + 1][3]
                            self.users.append(user)
        except IOError:
            print(f"Не удалось открыть файл: {IOError.strerror}.\nСоздаем пустой словарь.")

        self.flows = []
        try:
            with open('flows.csv') as f:
                reader = csv.reader(f, delimiter=';')
                tmp = list(reader)
                len_reader = len(tmp)
                if len_reader > 1:
                    for i in range(len(tmp) - 1):
                        if len(tmp[i + 1]) == 2:
                            flow = Flow()
                            flow.name = tmp[i + 1][0]
                            flow.groups = tmp[i + 1][1]
                            self.flows.append(flow)

        except IOError:
            print(f"Не удалось открыть файл: {IOError.strerror}.\nСоздаем пустой словарь.")

    def write_users_csv(self):
        try:
            with open('users.csv', 'w') as f:
                writer = csv.writer(f, delimiter=';')
                field = ["tid", "full_name", "group", "flow"]
                writer.writerow(field)
                for user in self.users:
                    writer.writerow([user.tid, user.full_name, user.group, user.flow])
        except IOError:
            print(f"Не удалось открыть файл: {IOError.strerror}.\nКонец записи.")

    def write_flows_csv(self):
        try:
            with open('flows.csv', 'w') as f:
                writer = csv.writer(f, delimiter=';')
                field = ["name", "groups"]
                writer.writerow(field)
                for flow in self.flows:
                    writer.writerow([flow.name, flow.groups])
        except IOError:
            print(f"Не удалось открыть файл: {IOError.strerror}.\nКонец записи.")

    def add_flow(self, flow: Flow):
        self.flows.append(flow)
        self.write_flows_csv()

    def remove_flow(self, flow_name: str):
        flow_del = self.search_flow(flow_name)
        self.flows.remove(flow_del)
        self.write_flows_csv()

    def search_flow(self, search_name: str):
        for flow in self.flows:
            if flow.name == search_name:
                return flow

    def flow_list(self):
        return self.flows

    def search_user(self, tid: int):
        for user in self.users:
            if user.tid == tid:
                return user

        return None

    def add_user(self, new_user: User):
        self.users.append(new_user)

    def update_user_info(self, new_user: User):
        for user in self.users:
            if user.tid == new_user.tid:
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

    def get_count_flows(self):
        return len(self.flows)

    # TODO: Send file to YD
