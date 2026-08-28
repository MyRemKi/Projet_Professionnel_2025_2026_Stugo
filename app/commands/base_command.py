# Modele de base pour une action annulable (executer / annuler)

from abc import ABC, abstractmethod

class Command(ABC):
    @abstractmethod
    def execute(self) -> bool: ...
    def undo(self) -> bool: return False
    def can_undo(self) -> bool: return False
    @property
    def description(self) -> str: return self.__class__.__name__

# Garde en memoire les dernieres actions faites, pour pouvoir les annuler (undo)
class CommandHistory:
    def __init__(self, max_size: int = 50):
        self.done: list[Command] = []
        self.max = max_size

    def execute(self, cmd: Command) -> bool:
        ok = cmd.execute()
        if ok:
            self.done.append(cmd)
            if len(self.done) > self.max:
                self.done.pop(0)
        return ok

    def undo_last(self) -> bool:
        for cmd in reversed(self.done):
            if cmd.can_undo():
                ok = cmd.undo()
                if ok:
                    self.done.remove(cmd)
                return ok
        return False

    def clear(self) -> None:
        self.done.clear()
