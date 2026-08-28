# Liste les differents etats possibles de l'application

from enum import Enum, auto

class AppStateEnum(Enum):
    IDLE    = auto()
    LOADING = auto()
    READY   = auto()
    ERROR   = auto()
