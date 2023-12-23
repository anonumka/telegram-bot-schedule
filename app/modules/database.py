import csv

from app.modules.question_handler import Question
from app.modules.logger import message_log_system


class User:
    tid: int
    full_name: str
    group: str


class Flow:
    name: str
    students: list

    def __init__(self):
        self.name = ""
        self.students = []


class Database:
    def __init__(self):
        self.users = dict()
        try:
            with open('users.csv', 'r') as f:
                reader = list(csv.reader(f, delimiter=';'))
                message_log_system(0, f"Count of loaded students: {len(reader) - 1}")
                if len(reader) > 0:
                    for tid, name, group in reader[1:]:
                        user = User()
                        user.tid = int(tid)
                        user.full_name = name
                        user.group = group
                        self.users[int(tid)] = user
                else:
                    message_log_system(1, f"File `users.csv` is empty")
        except IOError:
            open('users.csv', 'w')
            message_log_system(1, f"File `users.csv` not found: {IOError.strerror}")

        self.flows = dict()
        try:
            with open('flows.csv', 'r') as f:
                reader = list(csv.reader(f, delimiter=';'))
                message_log_system(0, f"Count of loaded flows: {len(list(reader)) - 1}")
                if len(reader) > 0:
                    for name, students in reader[1:]:
                        flow = Flow()
                        flow.name = name
                        for tid in students.split(','):
                            flow.students.append(int(tid))
                        self.flows[name] = flow
                else:
                    message_log_system(1, f"File `flows.csv` is empty")
        except IOError:
            open('flows.csv', 'w')
            message_log_system(1, f"File `flows.csv` not found: {IOError.strerror}")

        self.questions = []
        try:
            with open('questions.csv', 'r') as f:
                reader = list(csv.reader(f, delimiter=';'))
                message_log_system(0, f"Count of loaded questions: {len(list(reader)) - 1}")
                if len(reader) > 0:
                    for flow, date, question, answer in reader[1:]:
                        question = Question()
                        question.flow = flow
                        question.date = date
                        question.question = question
                        question.answer = answer

                        self.questions.append(question)
                else:
                    message_log_system(1, f"File `questions.csv` is empty")
        except IOError:
            open('questions.csv', 'w')
            message_log_system(1, f"File `questions.csv` not found: {IOError.strerror}")


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
                field = ["name", "students"]
                writer.writerow(field)
                for flow_name in list(self.flows):
                    flow = self.flows[flow_name]
                    students_tid = ','.join(flow.students)
                    writer.writerow([flow.name, students_tid])
        except IOError:
            message_log_system(1, f"File `{filename}` failed on create: {IOError.strerror}")

    def write_questions_csv(self):
        filename = 'questions.csv'
        try:
            with open(filename, 'w') as f:
                writer = csv.writer(f, delimiter=';')
                field = ["flow", "date", "question", "answer"]
                writer.writerow(field)
                for question in self.questions:
                    writer.writerow([question.flow, question.date, question.question, question.answer])
        except IOError:
            message_log_system(1, f"File `{filename}` failed on create: {IOError.strerror}")

    def add_flow(self, flow: Flow):
        self.flows[flow.name] = flow
        self.write_flows_csv()

    def search_flow(self, flow_name: str) -> Flow | None:
        if flow_name in self.flows:
            return self.flows[flow_name]
        return None

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

    def add_question(self, question: Question):
        self.questions.append(question)
        self.write_questions_csv()

    def delete_question(self, question: Question):
        self.questions.remove(question)
        self.write_questions_csv()

    def dates_questions_of_flow(self, flow_name: str):
        result = []
        for question in self.questions:
            if question.flow == flow_name:
                result.append(question.date)
        return result

    def search_question(self, flow: str, date: str):
        for question in self.questions:
            if question.flow == flow and question.date == date:
                return question

        return None


    def check_student_in_flow(self, tid_student: str, flow_name: str):
        flow = self.search_flow(flow_name)

        for tid in flow.students:
            if tid == tid_student:
                return True

        return False
