# Fabrique des widgets prets a l'emploi (labels, combo, spinbox) avec le bon style

from PyQt6.QtWidgets import QLabel, QPushButton, QComboBox
from shared.constants import C
from shared.scaling import S
from presentation.widgets.primitives import StepWidget

class WidgetFactory:

    @staticmethod
    def muted_label(text: str) -> QLabel:
        l = QLabel(text)
        l.setStyleSheet(f"color:{C['text_muted']};font-size:{S.font_sm}px;")
        return l

    @staticmethod
    def accent_label(text: str, bold: bool = False) -> QLabel:
        l = QLabel(text)
        fw = "700" if bold else "400"
        l.setStyleSheet(f"color:{C['accent']};font-size:{S.font_sm}px;font-weight:{fw};")
        return l

    @staticmethod
    def section_label(text: str) -> QLabel:
        l = QLabel(text)
        l.setStyleSheet(f"color:{C['text_muted']};font-size:{S.font_tiny + 1}px;font-weight:700;letter-spacing:0.8px;")
        return l

    @staticmethod
    def combo(min_width: int = 120, min_height: int = None) -> QComboBox:
        cb = QComboBox()
        cb.setMinimumWidth(round(S.dpi_scale * min_width))
        cb.setMinimumHeight(min_height or S.input_h)
        return cb

    @staticmethod
    def spinbox(lo: int = 0, hi: int = 100, value: int = 1, width: int = 60) -> StepWidget:
        sp = StepWidget(lo=lo, hi=hi, val=value)
        sp.setMinimumWidth(round(S.dpi_scale * width))
        sp.setMinimumHeight(S.input_h)
        return sp
