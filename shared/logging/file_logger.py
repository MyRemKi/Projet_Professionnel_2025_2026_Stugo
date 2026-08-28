# Ecrit les messages de log dans un fichier texte (un fichier par jour)

import os
import sys
import threading
from datetime import datetime
from shared.paths import APP_DATA_DIR as APP_DATA

if getattr(sys, "frozen", False):
    LOGS_DIR = os.path.join(APP_DATA, "logs")
else:
    project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    LOGS_DIR = os.path.join(project_root, "logs")


class FileLogger:
    _instance: "FileLogger | None" = None
    lock = threading.Lock()

    @classmethod
    def instance(cls) -> "FileLogger":
        with cls.lock:
            if cls._instance is None:
                cls._instance = FileLogger()
        return cls._instance

    def __init__(self) -> None:
        self.today: str = ""
        self.path: str = ""

    def log(self, context: str, message: str) -> None:
        try:
            with self.lock:
                now      = datetime.now()
                date_str = now.strftime("%Y-%m-%d")
                time_str = now.strftime("%H:%M")
                if date_str != self.today:
                    self.today = date_str
                    os.makedirs(LOGS_DIR, exist_ok=True)
                    self.path = os.path.join(LOGS_DIR, f"log-{date_str}.txt")
                with open(self.path, "a", encoding="utf-8") as f:
                    f.write(f"{time_str} = [{context}] {message}\n")
        except Exception:
            pass


def log_error(context: str, error: Exception) -> None:
    try:
        FileLogger.instance().log(context, str(error))
    except Exception:
        pass


def log_msg(context: str, message: str) -> None:
    try:
        FileLogger.instance().log(context, message)
    except Exception:
        pass
