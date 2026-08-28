# Centralise la communication entre la fenetre principale et ses pages/menus

from PyQt6.QtCore import QObject
from shared.logging.file_logger import log_error, log_msg

class UIMediator(QObject):
    _instance = None

    @classmethod
    def instance(cls):
        if cls._instance is None:
            cls._instance = UIMediator()
        return cls._instance

    def __init__(self):
        super().__init__()
        self.components: dict[str, object] = {}

    def register(self, name: str, component: object) -> None:
        self.components[name] = component

    def get(self, name: str):
        return self.components.get(name)

    def notify(self, sender: str, event: str, payload=None) -> None:
        try:
            from app.events.event_bus import EventBus
            EventBus.instance().publish(f"{sender}.{event}", payload)
        except Exception as e:
            log_error("ui_mediator.UIMediator.notify", e)
