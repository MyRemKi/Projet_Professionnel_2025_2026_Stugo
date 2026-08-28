# Modele de base commun a toutes les pages de l'application

from abc import abstractmethod
from PyQt6.QtWidgets import QWidget
import pandas as pd
from shared.logging.file_logger import log_error, log_msg

class BasePage(QWidget):

    def __init__(self, parent=None):
        super().__init__(parent)
        self.build_ui()
        self.connect_theme()

    @abstractmethod
    def build_ui(self) -> None: ...

    def connect_theme(self) -> None:
        try:
            from presentation.theme.theme_manager import ThemeManager
            ThemeManager.instance().theme_changed.connect(self.restyle)
        except Exception as e:
            log_error("base_page.BasePage.connect_theme", e)

    def restyle(self) -> None:
        pass

    def update_data(self, df: pd.DataFrame) -> None:
        pass
