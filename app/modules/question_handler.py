class Question:
    name: str
    flow: str
    time: int
    status: bool
    answer: str
    answers: []

    def __init__(self):
        self.name = ""
        self.flow = ""
        self.time = 0
        self.answer = ""
        self.answers = []
        self.status = False

    def start_question(self):
        self.status = True

        # Check working
        # user2 = ["Student1", "КИ20-07б", "10"]
        # user3 = ["Student2", "КИ20-06б", "15"]
        # user4 = ["Student3", "КИ20-06б", "15?"]
        # user1 = ["Student4", "КИ20-06б", "90?"]
        # user5 = ["Student5", "КИ20-09б", "20"]
        # self.answers.extend([user2, user4, user3])

        return "Вопрос создан"

    def stop_question(self):
        self.status = False
