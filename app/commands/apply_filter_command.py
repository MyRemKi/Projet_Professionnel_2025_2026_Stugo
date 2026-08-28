# Action qui applique les filtres choisis par l'utilisateur sur les donnees

from app.commands.base_command import Command

class ApplyFilterCommand(Command):
    def __init__(self, filter_sidebar, data_service) -> None:
        self.sidebar = filter_sidebar
        self.svc     = data_service

    def execute(self) -> bool:
        try:
            self.svc.apply_filters(self.sidebar)
            return True
        except Exception as e:
            print(f"[ApplyFilterCommand] {e}")
            return False

    @property
    def description(self) -> str:
        return "Application des filtres"
