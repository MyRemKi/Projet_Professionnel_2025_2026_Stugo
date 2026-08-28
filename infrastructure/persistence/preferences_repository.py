# Sauvegarde les preferences utilisateur (theme, colonnes visibles...) dans un fichier JSON

import os
import json
from shared.logging.file_logger import log_error
from shared.paths import APP_DATA_DIR as APP_DIR


class PreferencesRepository:
    _instance = None

    @classmethod
    def instance(cls):
        if cls._instance is None:
            cls._instance = PreferencesRepository()
        return cls._instance

    def __init__(self):
        os.makedirs(APP_DIR, exist_ok=True)
        self.prefs_file = os.path.join(APP_DIR, "prefs.json")

    def load(self) -> dict:
        try:
            if os.path.exists(self.prefs_file):
                with open(self.prefs_file, "r", encoding="utf-8") as f:
                    return json.load(f)
        except Exception as e:
            log_error("PrefsRepo", e)
        return {}

    def save(self, data: dict) -> bool:
        try:
            with open(self.prefs_file, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
            return True
        except Exception as e:
            log_error("PrefsRepo", e)
            return False
