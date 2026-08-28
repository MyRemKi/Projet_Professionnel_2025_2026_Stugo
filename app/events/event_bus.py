# Permet a un composant de prevenir les autres qu'un evenement s'est produit

from PyQt6.QtCore import QObject, pyqtSignal as Signal
from typing import Callable, Any

class EventBus(QObject):
    _instance = None
    signal = Signal(str, object)

    @classmethod
    def instance(cls):
        if cls._instance is None:
            cls._instance = EventBus()
        return cls._instance

    def __init__(self):
        super().__init__()
        self.subscribers: dict[str, list[Callable]] = {}
        self.signal.connect(self.dispatch)

    def publish(self, event_type: str, payload: Any = None) -> None:
        try:
            self.signal.emit(event_type, payload)
        except Exception as e:
            print(f"[EventBus] {event_type}: {e}")

    def subscribe(self, event_type: str, handler: Callable) -> None:
        self.subscribers.setdefault(event_type, []).append(handler)

    def unsubscribe(self, event_type: str, handler: Callable) -> None:
        try:
            self.subscribers.get(event_type, []).remove(handler)
        except ValueError:
            pass

    def dispatch(self, event_type: str, payload: Any) -> None:
        for h in list(self.subscribers.get(event_type, [])):
            try:
                h(payload)
            except Exception as e:
                print(f"[EventBus] handler {event_type}: {e}")
