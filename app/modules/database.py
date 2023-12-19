import csv
import os
import shutil
from datetime import datetime

from app.modules.json_parser import settings, write_config
from app.modules.question_handler import Question

folder_tables = "stats/"
if not os.path.isdir(folder_tables):
    os.mkdir(folder_tables)


class User:
    tid: int
    full_name: str
    group: str


class Flow:
    name: str
    groups: str

    def append(self, flow):
        pass


def check_exist_teacher(tid: int):
    if settings["tid_teacher"] == "":
        settings["tid_teacher"] = tid
        write_config(settings)
        return 0

    return 1


def check_its_teacher(tid: int):
    return 1 if settings["tid_teacher"] == tid else 0


def sort_two_column_csv_file(filename: str):
    with open(filename, 'r') as f:
        unsorted_csv = csv.DictReader(f, delimiter=';')
        sortedlist = sorted(unsorted_csv, key=lambda r: (r['group'], r['full_name']), reverse=False)

    with open(filename, 'r') as f:
        reader = csv.DictReader(f, delimiter=';')
        fieldnames = reader.fieldnames

    with open(filename, 'w') as f:
        writer = csv.DictWriter(f, delimiter=';', fieldnames=fieldnames)
        writer.writeheader()
        for row in sortedlist:
            writer.writerow(row)


def add_column_to_csv(filename: str, new_list: []):
    backup_filename = 'backup_' + filename
    shutil.copy(filename, backup_filename)
    with open(backup_filename, 'r') as ist, \
            open(filename, 'w') as ost:
        csv_reader = csv.reader(ist, delimiter=';')
        csv_writer = csv.writer(ost, delimiter=';')
        for i, row in enumerate(csv_reader, 0):
            row.append(new_list[i])
            csv_writer.writerow(row)


def add_row_user_in_table_performance(filename: str, full_name: str, group: str):
    with open(filename, 'r') as f:
        reader = csv.DictReader(f, delimiter=';')
        fieldnames = reader.fieldnames

    row_elem = [full_name, group]
    for i in range(len(fieldnames) - 2):
        row_elem.append(0)

    with open(filename, 'a') as f_object:
        writer_object = csv.writer(f_object, delimiter=';')
        writer_object.writerow(row_elem)
        f_object.close()


def add_marks_to_table_performance(question: Question):
    filename = f'table_performance_{question.flow}.csv'
    path_file = folder_tables + filename
    if os.path.isfile(path_file) is False:
        with open(path_file, 'w') as f:
            writer = csv.writer(f, delimiter=';')
            field = ["full_name", "group"]
            writer.writerow(field)

    with open(path_file, 'r') as ist:
        reader = csv.reader(ist, delimiter=';')
        next(reader)
        rows = list(reader)

        time = datetime.now().strftime("%d:%m:%Y %H:%M")
        column_answers = [time]

        for row in rows:
            find = False
            for full_name, group, answer_student in question.answers:
                if full_name == row[0] and group == row[1]:
                    mark = 1 if answer_student.lower() == question.answer.lower() else 0
                    column_answers.append(mark)
                    find = True
                    break

            if not find:
                column_answers.append(0)

        for full_name, group, answer_student in question.answers:
            find = False
            for row in rows:
                if full_name == row[0] and group == row[1]:
                    find = True
                    break

            if not find:
                mark = 1 if answer_student.lower() == question.answer.lower() else 0
                add_row_user_in_table_performance(filename, full_name, group)
                column_answers.append(mark)

    add_column_to_csv(path_file, column_answers)
    sort_two_column_csv_file(path_file)


class Database:
    def __init__(self):
        self.users = dict()
        try:
            with open('users.csv', 'r+') as f:
                reader = csv.reader(f, delimiter=';')
                if len(list(reader)) != 0:
                    next(reader)
                    for tid, name, group, flows in reader:
                        user = User()
                        user.tid = tid
                        user.full_name = name
                        user.group = group
                        user.flow = flows
                        self.users[tid] = user
        except IOError:
            print(f"Ошибка: {IOError.strerror}.\nСоздаем новый файл.")

        self.flows = dict()
        try:
            with open('flows.csv', 'r') as f:
                reader = csv.reader(f, delimiter=';')
                next(reader)
                for name, groups in reader:
                    flow = Flow()
                    flow.name = name
                    flow.groups = groups
                    self.flows[name] = flow

        except IOError:
            print(f"Ошибка: {IOError.strerror}.\nСоздаем новый файл.")

    def write_users_csv(self, user: User):
        filename = 'users.csv'
        if os.path.isfile(filename) is True:
            with open(filename, 'a') as f:
                writer = csv.writer(f, delimiter=';')
                writer.writerow([user.tid, user.full_name, user.group])
        else:
            with open('users.csv', 'w') as f:
                writer = csv.writer(f, delimiter=';')
                field = ["tid", "full_name", "group", "flow"]
                writer.writerow(field)
                writer.writerow([user.tid, user.full_name, user.group])

    def write_flows_csv(self):
        try:
            with open('flows.csv', 'w') as f:
                writer = csv.writer(f, delimiter=';')
                field = ["name", "groups"]
                writer.writerow(field)
                for flow_name in list(self.flows):
                    flow = self.flows[flow_name]
                    writer.writerow([flow.name, flow.groups])
        except IOError:
            print(f"Не удалось открыть файл: {IOError.strerror}.\nКонец записи.")

    def add_flow(self, flow: Flow):
        self.flows[flow.name] = flow
        self.write_flows_csv()

    def remove_flow(self, flow_name: str):
        del self.flows[flow_name]
        self.write_flows_csv()

    def flow_dict(self):
        return self.flows

    def search_user(self, tid: int):
        if tid in self.users:
            return self.users.get(tid)
        return None

    def add_user(self, new_user: User):
        self.users[new_user.tid] = new_user
        # self.write_users_csv(new_user)

    def update_user_info(self, new_user: User):
        self.users[new_user.tid] = new_user
        # self.add_user(new_user)

    def get_groups_flow(self, flow_name: str):
        for flow in self.flows:
            if flow_name == flow:
                return self.flows[flow_name].groups.split(', ')

    def get_tid_students_flow(self, flow_name: str):
        groups = self.get_groups_flow(flow_name)

        user_list = []
        for user in list(self.users):
            for group in groups:
                if group == user.group:
                    user_list.append(user.tid)

        return user_list

    # TODO: Send file to YD
