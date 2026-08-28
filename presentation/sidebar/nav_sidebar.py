# Menu de navigation a gauche de l'ecran, avec les boutons vers chaque page

from PyQt6.QtWidgets import QPushButton, QWidget, QVBoxLayout, QHBoxLayout, QLabel, QFrame
from PyQt6.QtCore import Qt, pyqtSignal as Signal

from shared.constants import C, PAGES
from shared.scaling import S
from presentation.theme.theme_manager import ThemeManager


def luma(hex_col: str) -> float:
    h = hex_col.lstrip('#')
    r, g, b = int(h[0:2], 16), int(h[2:4], 16), int(h[4:6], 16)
    return 0.299 * r + 0.587 * g + 0.114 * b


def blend(fg: str, bg: str, alpha: float) -> str:
    def c(h):
        h = h.lstrip('#')
        return int(h[0:2], 16), int(h[2:4], 16), int(h[4:6], 16)
    fr, fg_, fb = c(fg)
    br, bg_, bb = c(bg)
    return f"#{round(fr * alpha + br * (1 - alpha)):02X}{round(fg_ * alpha + bg_ * (1 - alpha)):02X}{round(fb * alpha + bb * (1 - alpha)):02X}"


def readable_on(bg_hex: str, candidate: str) -> str:
    if abs(luma(bg_hex) - luma(candidate)) >= 80:
        return candidate
    return "#f0f4f8" if luma(bg_hex) < 128 else "#101820"


class NavButton(QPushButton):
    def __init__(self, icon: str, label: str, page_key: str, parent=None):
        super().__init__(parent)
        self.page_key = page_key
        self.setCheckable(True)
        self.setFixedHeight(S.nav_btn_h)
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        lay = QHBoxLayout(self)
        lay.setContentsMargins(S.margin_card, 0, S.spacing_md, 0)
        lay.setSpacing(S.spacing_md)
        self.icon_lbl = QLabel(icon)
        self.icon_lbl.setFixedWidth(S.icon_col_w)
        self.icon_lbl.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents)
        self.text_lbl = QLabel(label)
        self.text_lbl.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents)
        lay.addWidget(self.icon_lbl)
        lay.addWidget(self.text_lbl, 1)
        self.active = False
        self.refresh(False)
        ThemeManager.instance().theme_changed.connect(lambda: self.refresh(self.active))

    def refresh(self, active: bool) -> None:
        self.active = active
        if active:
            accent_bg = blend(C['accent'], C['bg_deep'], 0.22)
            tx_col  = readable_on(accent_bg, C['text_primary'])
            ic_col  = readable_on(accent_bg, C['accent'])
            self.icon_lbl.setStyleSheet(f"font-size:{S.font_icon}px;background:transparent;border:none;color:{ic_col};")
            self.text_lbl.setStyleSheet(f"font-size:{S.font_base}px;background:transparent;border:none;color:{tx_col};font-weight:600;")
            self.setStyleSheet(f"QPushButton{{background:{accent_bg};border:none;border-left:3px solid {C['accent']};border-radius:0;}}QPushButton:hover{{background:{blend(C['accent'], C['bg_deep'], 0.30)};}}")
        else:
            ic_col = C["text_muted"]
            tx_col = C["text_secondary"]
            self.icon_lbl.setStyleSheet(f"font-size:{S.font_icon}px;background:transparent;border:none;color:{ic_col};")
            self.text_lbl.setStyleSheet(f"font-size:{S.font_base}px;background:transparent;border:none;color:{tx_col};font-weight:400;")
            self.setStyleSheet(f"QPushButton{{background:transparent;border:none;border-radius:0;}}QPushButton:hover{{background:{C['bg_elevated']};border-left:3px solid {C['border']};}}")

    def set_active(self, active: bool) -> None:
        self.setChecked(active)
        self.refresh(active)


# Barre laterale qui affiche les boutons NavButton et gere la page active
class Sidebar(QWidget):
    page_changed = Signal(str)

    NAV_ITEMS = [
        ("home",       "⌂", "Accueil"),
        ("import",     "↑", "Import"),
        ("table",      "≡", "Tableau"),
        ("chart",      "◈", "Graphique"),
        ("comparison", "⊞", "Comparaison"),
    ]

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFixedWidth(S.sidebar_w)
        self.buttons: dict[str, NavButton] = {}
        self.current = "home"
        self.build_ui()
        self.restyle()
        ThemeManager.instance().theme_changed.connect(self.restyle)

    def build_ui(self) -> None:
        lay = QVBoxLayout(self)
        lay.setContentsMargins(0, 0, 0, 0)
        lay.setSpacing(0)
        header = QWidget()
        header.setFixedHeight(S.header_h)
        hl = QHBoxLayout(header)
        hl.setContentsMargins(S.margin_card, 0, S.spacing_md, 0)
        hl.setSpacing(S.spacing_md)
        self.lbl_logo = QLabel("◉")
        self.lbl_title = QLabel("StuGo CO2")
        hl.addWidget(self.lbl_logo); hl.addWidget(self.lbl_title, 1)
        lay.addWidget(header)
        lay.addWidget(self.sep())
        lay.addSpacing(S.spacing_sm)
        for key, icon, label in self.NAV_ITEMS:
            btn = NavButton(icon, label, key)
            btn.clicked.connect(lambda _, k=key: self.on(k))
            self.buttons[key] = btn
            lay.addWidget(btn)
        lay.addStretch()
        lay.addWidget(self.sep())
        btn_h = NavButton("?", "Aide", "help")
        btn_h.clicked.connect(lambda: self.on("help"))
        self.buttons["help"] = btn_h
        lay.addWidget(btn_h)
        btn_s = NavButton("⚙", "Parametres", "settings")
        btn_s.clicked.connect(lambda: self.on("settings"))
        self.buttons["settings"] = btn_s
        lay.addWidget(btn_s)
        self.lbl_ver = QLabel("  v7.0")
        self.lbl_ver.setFixedHeight(S.spacing_lg + S.spacing_md)
        lay.addWidget(self.lbl_ver)
        self.buttons["home"].set_active(True)

    def sep(self) -> QFrame:
        sep = QFrame()
        sep.setFrameShape(QFrame.Shape.HLine)
        sep.setStyleSheet(f"background:{C['border']};border:none;")
        sep.setFixedHeight(1)
        return sep

    def restyle(self) -> None:
        self.setFixedWidth(S.sidebar_w)
        self.setStyleSheet(f"background:{C['bg_deep']};border-right:1px solid {C['border']};")
        if hasattr(self, 'lbl_logo'):
            self.lbl_logo.setStyleSheet(f"color:{C['accent']};font-size:{S.font_xl}px;background:transparent;")
        if hasattr(self, 'lbl_title'):
            self.lbl_title.setStyleSheet(f"color:{C['text_primary']};font-size:{S.font_base + 1}px;font-weight:700;background:transparent;")
        if hasattr(self, 'lbl_ver'):
            self.lbl_ver.setStyleSheet(f"color:{C['text_muted']};font-size:{S.font_sm}px;background:transparent;")

    def on(self, key: str) -> None:
        self.buttons[self.current].set_active(False)
        self.current = key
        self.buttons[key].set_active(True)
        self.page_changed.emit(key)

    def set_page(self, key: str) -> None:
        if key in self.buttons:
            self.buttons[self.current].set_active(False)
            self.current = key
            self.buttons[key].set_active(True)
