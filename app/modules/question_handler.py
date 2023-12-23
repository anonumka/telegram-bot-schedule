import csv
import os
import shutil
from datetime import datetime
import yadisk

from app.modules.json_parser import settings
from app.modules.logger import message_log_system


class Question:
    flow: str
    date: str
    question: str
    answer: str

    status: bool
    answers: []

    def __init__(self):
        self.flow = ""
        self.date = ""
        self.question = ""
        self.answer = ""

        self.answers = []
        self.status = False

    def start_question(self) -> None:
        self.status = True

        # Check working
        # user2 = ["Student1", "КИ20-07б", "10"]
        # user3 = ["Student2", "КИ20-06б", "15"]
        # user4 = ["Student3", "КИ20-06б", "15?"]
        # user1 = ["Student4", "КИ20-06б", "90?"]
        # user5 = ["Student5", "КИ20-09б", "20"]
        # self.answers.extend([user2, user4, user3])

    def stop_question(self) -> None:
        self.status = False
        add_marks_to_table_performance(self)


    def get_count_right_answers(self) -> int:
        count = 0
        for _, _, answer in self.answers:
            count += 1 if answer.lower() == self.answer.lower() else 0
        return count


folder_tables = "stats/"
if not os.path.isdir(folder_tables):
    os.mkdir(folder_tables)

folder_backups = "stats/backups/"
if not os.path.isdir(folder_backups):
    os.mkdir(folder_backups)


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

        time_date = datetime.now()
        column_answers = [time_date.strftime("%d:%m_%H:%M")]
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
    if "yandex_token" in settings:
        token = settings["yandex_token"]
    else:
        message_log_system(0, f"Not write to YD: not token")
        return

    filename = filepath.split("/", -1)[-1]

    try:
        y = yadisk.YaDisk(token=token)
        if not y.is_dir('ScheduleBot'):
            y.mkdir('ScheduleBot')
        y.upload(filepath, f'/ScheduleBot/{filename}', overwrite=True)
        message_log_system(0, f"{filename} uploaded to Yandex Disk")
    except Exception as e:
        message_log_system(2, f"{filename} not uploaded to Yandex Disk: {e}")
