
from app import db, bot

import threading

class Question:
    name: str
    flow: str
    time: int
    status: bool

    def start(self):
        tids = db.get_tid_students_flow(flows=self.flow)
        for tid in tids:
            bot.send_message(tid, f"{self.name}\nНа ответ вам {self.time} минут.")

        self.status = True
        threading.Timer(60.0 * self.time, self.stop).start()

    def stop(self):
        self.status = False
        # TODO: send answer
