# Modele de base pour un widget qui doit se restyler quand le theme change

from abc import abstractmethod
from PyQt6.QtWidgets import QWidget
from shared.logging.file_logger import log_error, log_msg

class BaseStyledWidget(QWidget):

    def __init__(self, parent=None):
        super().__init__(parent)
        self.init_widget()
        try:
            from presentation.theme.theme_manager import ThemeManager
            ThemeManager.instance().theme_changed.connect(self.restyle)
        except Exception as e:
            log_error("base_widget.BaseStyledWidget.__init__", e)

    def init_widget(self) -> None:
        pass

    @abstractmethod
    def restyle(self) -> None: ...
