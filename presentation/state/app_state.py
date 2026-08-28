# Retient dans quel etat se trouve l'application (chargement, prete, erreur...)

from presentation.state.states import AppStateEnum
from PyQt6.QtCore import QObject, pyqtSignal as Signal

class AppState(QObject):
    _instance = None
    state_changed = Signal(object)

    @classmethod
    def instance(cls):
        if cls._instance is None:
            cls._instance = AppState()
        return cls._instance

    def __init__(self):
        super().__init__()
        self.state = AppStateEnum.IDLE

    @property
    def current(self) -> AppStateEnum:
        return self.state

    def transition(self, new_state: AppStateEnum) -> None:
        if new_state != self.state:
            self.state = new_state
            self.state_changed.emit(new_state)

    def is_ready(self) -> bool:
        return self.state == AppStateEnum.READY

    def is_loading(self) -> bool:
        return self.state == AppStateEnum.LOADING
