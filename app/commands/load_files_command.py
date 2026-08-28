# Action qui charge des fichiers Excel/CSV, avec possibilite d'annuler (undo)

from app.commands.base_command import Command

class LoadFilesCommand(Command):
    def __init__(self, filepaths: list[str], data_service) -> None:
        self.paths  = filepaths
        self.svc    = data_service
        self.loaded: set[str] = set()

    def execute(self) -> bool:
        try:
            self.loaded = self.svc.load_files(self.paths)
            return bool(self.loaded)
        except Exception as e:
            print(f"[LoadFilesCommand] {e}")
            return False

    def undo(self) -> bool:
        try:
            for uid in self.loaded:
                self.svc.remove_file(uid)
            return True
        except Exception:
            return False

    def can_undo(self) -> bool:
        return bool(self.loaded)

    @property
    def description(self) -> str:
        return f"Chargement {len(self.paths)} fichier(s)"
