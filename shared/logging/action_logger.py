# Garde en memoire l'historique des actions faites par l'utilisateur (import, export, theme...)

import json
from datetime import datetime


class ActionLogger:
    _instance: "ActionLogger | None" = None

    def __init__(self) -> None:
        self.logs: list[dict] = []

    @classmethod
    def instance(cls) -> "ActionLogger":
        if cls._instance is None:
            cls._instance = ActionLogger()
        return cls._instance

    def log(self, action_type: str, message: str) -> dict:
        entry = {"ts": datetime.now().strftime("%H:%M:%S"), "date": datetime.now().strftime("%d/%m/%Y"), "type": action_type, "message": message}
        self.logs.append(entry)
        return entry

    def get_logs(self) -> list[dict]:
        return list(reversed(self.logs))

    def clear(self) -> None:
        self.logs.clear()

    def to_json(self) -> str:
        try:
            return json.dumps(self.logs)
        except Exception:
            return "[]"

    def from_json(self, data: str) -> None:
        try:
            self.logs = json.loads(data)
        except Exception:
            pass
