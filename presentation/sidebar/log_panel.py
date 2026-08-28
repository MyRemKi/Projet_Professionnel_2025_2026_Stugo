# Panneau qui affiche le journal des actions et gere la sauvegarde/reprise de session

from PyQt6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QTextEdit, QFrame, QMessageBox
from PyQt6.QtCore import Qt, pyqtSignal as Signal
from PyQt6.QtGui import QFont

from shared.constants import C
from shared.scaling import S
from shared.logging.action_logger import ActionLogger
from presentation.theme.theme_manager import ThemeManager
from presentation.widgets.primitives import PrimaryButton


class LogSessionPanel(QWidget):
    save_requested   = Signal()
    resume_requested = Signal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self.logger = ActionLogger.instance()
        self.setFixedWidth(S.log_w)
        self.build_ui()
        self.restyle()
        ThemeManager.instance().theme_changed.connect(self.restyle)
        ThemeManager.instance().theme_changed.connect(self.refresh)

    def build_ui(self) -> None:
        lay = QVBoxLayout(self)
        lay.setContentsMargins(0, 0, 0, 0)
        lay.setSpacing(0)
        self.header = QWidget()
        self.header.setFixedHeight(S.header_h - S.spacing_md)
        hl = QHBoxLayout(self.header)
        hl.setContentsMargins(S.margin_card, 0, S.spacing_sm, 0)
        hl.setSpacing(0)
        self.h_title = QLabel("Journal d'activite")
        hl.addWidget(self.h_title, 1)
        self.btn_clear = QPushButton("Vider")
        self.btn_clear.setFixedHeight(S.btn_h_sm)
        self.btn_clear.setMinimumWidth(round(S.dpi_scale * 55))
        self.btn_clear.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_clear.clicked.connect(self.clear)
        hl.addWidget(self.btn_clear)
        lay.addWidget(self.header)
        self.log_view = QTextEdit()
        self.log_view.setReadOnly(True)
        self.log_view.setFont(QFont("Consolas", S.font_code))
        lay.addWidget(self.log_view, 1)
        sep = QFrame()
        sep.setFrameShape(QFrame.Shape.HLine)
        sep.setStyleSheet(f"background:{C['border']};border:none;")
        sep.setFixedHeight(1)
        lay.addWidget(sep)
        sw = QWidget()
        sl = QVBoxLayout(sw)
        sl.setContentsMargins(S.spacing_md, S.spacing_md, S.spacing_md, S.spacing_md)
        sl.setSpacing(S.spacing_sm)
        self.lbl_ts = QLabel("Aucune session sauvegardee")
        self.lbl_ts.setWordWrap(True)
        sl.addWidget(self.lbl_ts)
        btn_save = PrimaryButton("Sauvegarder la session", "◉")
        btn_save.setFixedHeight(S.btn_h_lg)
        btn_save.clicked.connect(self.save_requested)
        sl.addWidget(btn_save)
        self.btn_resume = QPushButton("▶  Reprendre la session")
        self.btn_resume.setMinimumHeight(S.btn_h)
        self.btn_resume.clicked.connect(self.resume_requested)
        sl.addWidget(self.btn_resume)
        lay.addWidget(sw)
        self.restyle_resume()
        ThemeManager.instance().theme_changed.connect(self.restyle_resume)

    def refresh(self) -> None:
        logs  = self.logger.get_logs()
        muted = C["text_muted"]; sec = C["text_secondary"]
        if not logs:
            self.log_view.setHtml(f"<p style='color:{muted};font-style:italic;padding:6px;font-size:{S.font_code}px;'>Aucune action.</p>"); return
        icons = {
            "import": ("↓", C["accent"]), "export_csv": ("⇓", C["blue"]),
            "export_png": ("◎", C["purple"]), "remove": ("×", C["red"]),
            "info": ("·", muted),       "save": ("◉", C["yellow"]),
            "resume": ("▶", C["blue"]),
        }
        parts = []
        for e in logs[:50]:
            ic, col = icons.get(e["type"], ("·", muted))
            msg = e["message"].replace("<","&lt;").replace(">","&gt;")
            parts.append(f"<div style='margin:1px 0;padding:2px 6px;border-left:2px solid {col};'><span style='color:{muted};font-size:{S.font_tiny}px;'>{e['ts']}</span> <span style='color:{sec};font-size:{S.font_code}px;'>{msg}</span></div>")
        self.log_view.setHtml("<body style='background:transparent;margin:0;padding:0;'>" + "".join(parts) + "</body>")

    def update_session_info(self, ts: str) -> None:
        self.lbl_ts.setText(f"Sauvegarde : {ts}" if ts else "Aucune session")

    def clear(self) -> None:
        reply = QMessageBox.question(self, "Vider le journal", "Effacer tous les messages ?", QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
        if reply == QMessageBox.StandardButton.Yes:
            self.logger.clear(); self.refresh()

    def restyle(self) -> None:
        self.setFixedWidth(S.log_w)
        self.setStyleSheet(f"background:{C['bg_deep']};border-right:1px solid {C['border']};")
        if hasattr(self, "header"):
            self.header.setStyleSheet(f"background:{C['bg_deep']};border-bottom:1px solid {C['border']};")
        if hasattr(self, "h_title"):
            self.h_title.setStyleSheet(f"font-size:{S.font_base+1}px;font-weight:700;color:{C['text_primary']};")
        if hasattr(self, "log_view"):
            self.log_view.setStyleSheet(f"background:transparent;border:none;padding:4px;color:{C['text_primary']};font-size:{S.font_code}px;line-height:1.5;")
        if hasattr(self, "btn_clear"):
            self.btn_clear.setStyleSheet(f"""
                QPushButton{{background:transparent;color:{C['red']};
                border:1px solid {C['red']};border-radius:{S.r_sm()};
                padding:2px {S.spacing_sm}px;font-size:{S.font_sm}px;
                min-height:{S.btn_h_sm}px;}}
                QPushButton:hover{{background:rgba(255,82,82,0.1);}}""")
        if hasattr(self, "lbl_ts"):
            self.lbl_ts.setStyleSheet(f"color:{C['text_muted']};font-size:{S.font_sm}px;")

    def restyle_resume(self) -> None:
        if hasattr(self, "btn_resume"):
            self.btn_resume.setStyleSheet(f"QPushButton{{background:transparent;color:{C['blue']};border:1px solid {C['blue']};border-radius:{S.r_sm()};padding:{round(S.dpi_scale*6)}px;font-size:{S.font_base}px;min-height:{S.btn_h}px;}}QPushButton:hover{{background:rgba(61,158,255,0.12);}}")
