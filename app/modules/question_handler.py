class Question:
    name: str
    flow: str
    time: int
    status: bool
    answers: []

    def __init__(self):
        self.name = ""
        self.flow = ""
        self.time = 0
        self.status = False
