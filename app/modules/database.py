import csv
import os
import shutil
from datetime import datetime, timedelta
import yadisk

from app.modules.json_parser import settings, write_config
from app.modules.question_handler import Question
from app.modules.logger import message_log_system

folder_tables = "stats/"
if not os.path.isdir(folder_tables):
    os.mkdir(folder_tables)

folder_backups = "stats/backups/"
if not os.path.isdir(folder_backups):
    os.mkdir(folder_backups)


class User:
    tid: int
    full_name: str
    group: str


class Flow:
    name: str
    groups: str


def check_exist_teacher(tid: int):
    if settings["tid_teacher"] == "":
        settings["tid_teacher"] = tid
        write_config(settings)
        message_log_system(0, f"{tid} now is teacher")
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


def add_column_to_csv(filepath: str, filename: str, new_list: []):
    backup_filename = folder_backups + 'backup_' + filename
    shutil.copy(filepath, backup_filename)

    with open(backup_filename, 'r') as ist, \
            open(filepath, 'w') as ost:
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

        time = datetime.now()
        column_answers = [time.strftime("%Y-%m-%d_%H.%M")]
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
                add_row_user_in_table_performance(path_file, full_name, group)
                column_answers.append(mark)

    add_column_to_csv(path_file, filename, column_answers)
    sort_two_column_csv_file(path_file)
    message_log_system(0, f"File `{filename}` successfully recorded")
    send_file_to_yandex_disk(path_file)


def send_file_to_yandex_disk(filepath: str):
    token = settings["yandex_token"]
    filename = filepath.split("/", -1)[-1]

    y = yadisk.YaDisk(token=token)
    if not y.is_dir('ScheduleBot'):
        y.mkdir('ScheduleBot')

    y.upload(filepath, f'/ScheduleBot/{filename}', overwrite=True)
    message_log_system(0, f"{filename} uploaded to Yandex Disk")


class Database:
    def __init__(self):
        self.users = dict()
        try:
            with open('users.csv', 'r') as f:
                reader = list(csv.reader(f, delimiter=';'))
                message_log_system(0, f"Count of flows: {len(reader) - 1}")
                if len(reader) > 0:
                    for tid, name, group in reader[1:]:
                        user = User()
                        user.tid = int(tid)
                        user.full_name = name
                        user.group = group
                        self.users[tid] = user
                else:
                    message_log_system(1, f"File `users.csv` is empty")
        except IOError:
            open('users.csv', 'w')
            message_log_system(1, f"File `users.csv` not found: {IOError.strerror}")

        self.flows = dict()
        try:
            with open('flows.csv', 'r') as f:
                reader = list(csv.reader(f, delimiter=';'))
                message_log_system(0, f"Count of flows: {len(list(reader)) - 1}")
                if len(reader) > 0:
                    for name, groups in reader[1:]:
                        flow = Flow()
                        flow.name = name
                        flow.groups = groups
                        self.flows[name] = flow
                else:
                    message_log_system(1, f"File `flows.csv` is empty")
        except IOError:
            open('flows.csv', 'w')
            message_log_system(1, f"File `flows.csv` not found: {IOError.strerror}")


    def write_users_csv(self):
        filename = 'users.csv'
        try:
            with open(filename, 'w') as f:
                writer = csv.writer(f, delimiter=';')
                field = ["tid", "full_name", "group"]
                writer.writerow(field)
                for tid in self.users.keys():
                    writer.writerow([self.users[tid].tid, self.users[tid].full_name, self.users[tid].group])
        except IOError:
            message_log_system(1, f"File `{filename}` failed on create: {IOError.strerror}")

    def write_flows_csv(self):
        filename = 'flows.csv'
        try:
            with open(filename, 'w') as f:
                writer = csv.writer(f, delimiter=';')
                field = ["name", "groups"]
                writer.writerow(field)
                for flow_name in list(self.flows):
                    flow = self.flows[flow_name]
                    writer.writerow([flow.name, flow.groups])
        except IOError:
            message_log_system(1, f"File `{filename}` failed on create: {IOError.strerror}")

    def add_flow(self, flow: Flow):
        self.flows[flow.name] = flow
        self.write_flows_csv()

    def search_flow(self, flow_name: str):
        if flow_name in self.flows:
            return True
        return False

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

    def check_group_in_flow(self, group_name: str, flow_name: str):
        groups = self.get_groups_flow(flow_name)

        for group in groups:
            if group == group_name:
                return True

        return False

    def get_tid_students_flow(self, flow_name: str):
        groups = self.get_groups_flow(flow_name)

        user_list = []
        for tid_user in list(self.users):
            for group in groups:
                if group == self.users[tid_user].group:
                    user_list.append(self.users[tid_user].tid)

        return user_list
