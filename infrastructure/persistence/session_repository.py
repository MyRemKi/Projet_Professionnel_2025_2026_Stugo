# Sauvegarde la session (fichiers charges, filtres actifs) dans un fichier JSON

import os
import json
from shared.logging.file_logger import log_error
from shared.paths import APP_DATA_DIR as APP_DIR


class SessionRepository:
    _instance = None

    @classmethod
    def instance(cls):
        if cls._instance is None:
            cls._instance = SessionRepository()
        return cls._instance

    def __init__(self):
        os.makedirs(APP_DIR, exist_ok=True)
        self.session_file = os.path.join(APP_DIR, "session.json")

    def get_session_dir(self) -> str:
        return APP_DIR

    def read(self, path: str) -> dict:
        try:
            if os.path.exists(path):
                with open(path, "r", encoding="utf-8") as f:
                    return json.load(f)
        except Exception as e:
            log_error("SessionRepo", e)
        return {}

    def write(self, path: str, data: dict) -> bool:
        try:
            os.makedirs(os.path.dirname(path), exist_ok=True)
            with open(path, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
            return True
        except Exception as e:
            log_error("SessionRepo", e)
            return False

    def load_session(self) -> dict:
        return self.read(self.session_file)

    def save_session(self, data: dict) -> bool:
        return self.write(self.session_file, data)

    def clear_session(self) -> bool:
        try:
            if os.path.exists(self.session_file):
                os.remove(self.session_file)
            return True
        except Exception as e:
            log_error("SessionRepo", e)
            return False
