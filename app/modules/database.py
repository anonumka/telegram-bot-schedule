import csv


class Users:
    tid: int
    full_name: str
    group: str
    flow: str


class Database:
    def __init__(self):
        try:
            with open('users.csv') as f:
                reader = csv.reader(f, delimiter=';')
                self.users = list(reader)
        except IOError:
            print(f"Не удалось открыть файл: {IOError.strerror}.\nСоздаем пустой словарь.")
            self.users = []

    def write_users_csv(self):
        try:
            with open('users.csv', 'w') as f:
                writer = csv.writer(f, delimiter=';')
                writer.writerows(self.users)
        except IOError:
            print(f"Не удалось открыть файл: {IOError.strerror}.\nКонец записи.")

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

    def check_exist_teacher(self):
        for user in self.users:
            if user.group == "Преподаватель":
                return 1

        return 0

    # TODO: Send file to YD
