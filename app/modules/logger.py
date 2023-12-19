import logging
import os
from datetime import datetime

app_path = "logs"
if not os.path.isdir(app_path):
    os.mkdir(app_path)


def message_log_system(message_type: int, text: str) -> None:
    """Logging of messages in working of program"""
    time = datetime.now().strftime("%H:%M:%S")
    match message_type:
        case 0:
            msg = f"[I] {time} {text}"
        case 1:
            msg = f"[W] {time} {text}"
        case 2:
            msg = f"[E] {time} {text}"
        case _:
            msg = "[E] Error type logging level"

    logging.error(msg)
    print(msg)


def configure_logging():
    """Configuration of logger"""
    if not os.path.isdir(app_path):
        os.mkdir(app_path)

    time = datetime.now().strftime("%Y-%m-%d_%H.%M")
    logging.basicConfig(format="%(message)s",
                        filename=f"{app_path}/bot-logger_{time}.log",
                        filemode="w"
                        )
    logging.disable(level=logging.WARNING)


configure_logging()
