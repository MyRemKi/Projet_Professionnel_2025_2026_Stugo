# Petits widgets de base reutilises partout dans l'interface (bouton, badge, separateur...)

from PyQt6.QtWidgets import QLabel, QPushButton, QFrame, QVBoxLayout, QWidget, QHBoxLayout, QLineEdit
from PyQt6.QtCore import Qt, pyqtSignal as Signal
from PyQt6.QtGui import QIntValidator, QDoubleValidator

from shared.constants import C
from shared.scaling import S
from shared.color_utils import contrast_text
from presentation.theme.theme_manager import ThemeManager


class Separator(QFrame):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFrameShape(QFrame.Shape.HLine)
        self.setFixedHeight(1)
        self.r()
        ThemeManager.instance().theme_changed.connect(self.r)

    def r(self):
        self.setStyleSheet(f"background:{C['border']};border:none;")


class Badge(QLabel):
    def __init__(self, text: str, color: str | None = None, parent=None):
        super().__init__(text, parent)
        self.color = color or C["accent"]
        self.setFixedHeight(max(20, S.btn_h_sm))
        self.r()
        ThemeManager.instance().theme_changed.connect(self.r)

    def r(self):
        txt = contrast_text(self.color)
        h = max(20, S.btn_h_sm)
        self.setFixedHeight(h)
        self.setStyleSheet(f"background:{self.color};color:{txt};border-radius:{h // 2}px;padding:1px {S.spacing_sm + 2}px;font-size:{S.font_sm}px;font-weight:700;letter-spacing:0.3px;")


class PrimaryButton(QPushButton):
    def __init__(self, text: str, icon: str = "", parent=None):
        super().__init__(f"{icon}  {text}" if icon else text, parent)
        self.setMinimumHeight(S.btn_h_lg)
        self.r()
        ThemeManager.instance().theme_changed.connect(self.r)

    def r(self):
        txt = contrast_text(C["accent"])
        self.setMinimumHeight(S.btn_h_lg)
        self.setStyleSheet(f"""
            QPushButton {{
                background:{C['accent']};
                color:{txt};
                border:none;
                border-radius:{S.r_sm()};
                padding:{round(S.dpi_scale*6)}px {round(S.dpi_scale*18)}px;
                font-size:{S.font_base}px;
                font-weight:700;
                min-height:{S.btn_h_lg}px;
            }}
            QPushButton:hover {{
                background:{C['border_light']};
                color:{C['text_primary']};
            }}
            QPushButton:pressed {{ opacity:0.8; }}
            QPushButton:disabled {{
                background:{C['bg_hover']};
                color:{C['text_muted']};
            }}
        """)


class DangerButton(QPushButton):
    def __init__(self, text: str, parent=None):
        super().__init__(text, parent)
        self.setMinimumHeight(S.btn_h)
        self.r()
        ThemeManager.instance().theme_changed.connect(self.r)

    def r(self):
        self.setMinimumHeight(S.btn_h)
        self.setStyleSheet(f"""
            QPushButton {{
                background:transparent;
                color:{C['red']};
                border:1px solid {C['red']};
                border-radius:{S.r_sm()};
                padding:{round(S.dpi_scale*5)}px {round(S.dpi_scale*12)}px;
                font-size:{S.font_base}px;
                font-weight:600;
                min-height:{S.btn_h}px;
            }}
            QPushButton:hover {{
                background:rgba(255,82,82,0.12);
                color:#ff7070;
                border-color:#ff6060;
            }}
        """)


class SmallLabel(QLabel):
    def __init__(self, text: str = "", parent=None):
        super().__init__(text, parent)
        self.r()
        ThemeManager.instance().theme_changed.connect(self.r)

    def r(self):
        self.setStyleSheet(f"color:{C['text_muted']};font-size:{S.font_sm}px;")


class StatCard(QWidget):
    def __init__(self, label: str, value: str = "—", color: str | None = None, parent=None):
        super().__init__(parent)
        self.col = color or C["accent"]
        lay = QVBoxLayout(self)
        lay.setContentsMargins(S.margin_card, S.spacing_md, S.margin_card, S.spacing_md)
        lay.setSpacing(S.spacing_sm // 2)
        self.lbl_val = QLabel(value)
        self.lbl_key = QLabel(label)
        lay.addWidget(self.lbl_val)
        lay.addWidget(self.lbl_key)
        self.setMinimumHeight(S.stat_h)
        self.r()
        ThemeManager.instance().theme_changed.connect(self.r)

    def r(self):
        self.lbl_val.setStyleSheet(f"color:{self.col};font-size:{S.font_md + 2}px;font-weight:700;font-family:'Consolas','Courier New',monospace;")
        self.lbl_key.setStyleSheet(f"color:{C['text_muted']};font-size:{S.font_sm}px;")
        self.setMinimumHeight(S.stat_h)
        self.setStyleSheet(f"background:{C['bg_elevated']};border-radius:{S.r_md()};border:1px solid {C['border']};border-left:3px solid {self.col};")

    def set_value(self, v: str) -> None:
        self.lbl_val.setText(str(v))


class StepWidget(QWidget):
    valueChanged = Signal(object)

    def __init__(self, lo=0, hi=100, val=0, decimals=0, step=1, parent=None):
        super().__init__(parent)
        self.lo         = lo
        self.hi         = hi
        self.dec_digits = decimals
        self.step       = step
        self.val        = float(val) if decimals else int(val)

        lay = QHBoxLayout(self)
        lay.setContentsMargins(0, 0, 0, 0)
        lay.setSpacing(0)

        bw = max(40, round(S.dpi_scale * 42))

        self.btn_m = QPushButton("-")
        self.btn_m.setFixedWidth(bw)
        self.btn_m.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_m.setFocusPolicy(Qt.FocusPolicy.NoFocus)

        self.edit = QLineEdit(self.fmt(self.val))
        self.edit.setAlignment(Qt.AlignmentFlag.AlignCenter)
        if decimals:
            self.edit.setValidator(QDoubleValidator(float(lo), float(hi), decimals))
        else:
            self.edit.setValidator(QIntValidator(int(lo), int(hi)))

        self.btn_p = QPushButton("+")
        self.btn_p.setFixedWidth(bw)
        self.btn_p.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_p.setFocusPolicy(Qt.FocusPolicy.NoFocus)

        lay.addWidget(self.btn_m)
        lay.addWidget(self.edit, 1)
        lay.addWidget(self.btn_p)

        self.btn_m.clicked.connect(self.dec)
        self.btn_p.clicked.connect(self.inc)
        self.edit.editingFinished.connect(self.on_edit)

        self.restyle()
        ThemeManager.instance().theme_changed.connect(self.restyle)

    def fmt(self, v) -> str:
        return f"{v:.{self.dec_digits}f}" if self.dec_digits else str(int(v))

    def dec(self): self.apply(self.val - self.step)
    def inc(self): self.apply(self.val + self.step)

    def on_edit(self):
        try:
            raw = self.edit.text().replace(',', '.')
            v = float(raw) if self.dec_digits else int(raw)
        except (ValueError, OverflowError):
            self.edit.setText(self.fmt(self.val))
            return
        self.apply(v)

    def apply(self, v):
        v = float(v) if self.dec_digits else int(v)
        v = max(self.lo, min(self.hi, v))
        if v != self.val:
            self.val = v
            self.edit.setText(self.fmt(v))
            self.valueChanged.emit(v)

    def value(self): return self.val
    def setValue(self, v):
        self.val = float(v) if self.dec_digits else int(v)
        self.edit.setText(self.fmt(self.val))
    def setRange(self, lo, hi): self.lo = lo; self.hi = hi
    def setDecimals(self, d): self.dec_digits = d
    def setAlignment(self, a): self.edit.setAlignment(a)

    def restyle(self):
        r = S.r_sm()
        shared = f"border:1px solid {C['border']};font-size:{S.font_base + 6}px;font-weight:700;min-height:{S.input_h}px;padding:0 8px;"
        self.btn_m.setStyleSheet(f"""
            QPushButton {{
                background:{C['bg_elevated']};color:{C['text_primary']};
                {shared}
                border-right:none;
                border-top-left-radius:{r}px;border-bottom-left-radius:{r}px;
            }}
            QPushButton:hover {{
                background:{C['accent_dim']};color:{C['accent']};
                border-color:{C['accent']};
            }}
            QPushButton:pressed {{background:{C['accent']};color:{C['bg_deep']};}}
        """)
        self.btn_p.setStyleSheet(f"""
            QPushButton {{
                background:{C['bg_elevated']};color:{C['text_primary']};
                {shared}
                border-left:none;
                border-top-right-radius:{r}px;border-bottom-right-radius:{r}px;
            }}
            QPushButton:hover {{
                background:{C['accent_dim']};color:{C['accent']};
                border-color:{C['accent']};
            }}
            QPushButton:pressed {{background:{C['accent']};color:{C['bg_deep']};}}
        """)
        self.edit.setStyleSheet(f"""
            QLineEdit {{
                background:{C['bg_input']};color:{C['text_primary']};
                border-top:1px solid {C['border']};
                border-bottom:1px solid {C['border']};
                border-left:none;border-right:none;
                font-size:{S.font_base}px;font-weight:600;
                min-height:{S.input_h}px;padding:0 2px;
            }}
            QLineEdit:focus {{
                border-top-color:{C['accent']};
                border-bottom-color:{C['accent']};
            }}
        """)
