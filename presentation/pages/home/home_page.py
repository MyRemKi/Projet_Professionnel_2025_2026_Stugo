# Page d'accueil : horloge, statistiques de session, rappel des zones et guide rapide

from datetime import datetime
import pandas as pd

from PyQt6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QGridLayout, QLabel, QPushButton, QGroupBox
from PyQt6.QtCore import Qt, QTimer, pyqtSignal as Signal

from shared.constants import C, ZONES
from shared.scaling import S
from shared.logging.file_logger import log_error, log_msg
from presentation.theme.theme_manager import ThemeManager
from presentation.widgets.primitives import StatCard, PrimaryButton


class HomePage(QWidget):
    navigate_to = Signal(str)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.sec_lbl: QLabel | None = None
        self.zone_lbls: list[QLabel] = []
        self.guide_badges: list[QLabel] = []
        self.guide_titles: list[QLabel] = []
        self.guide_descs: list[QLabel] = []
        self.zgrp: QGroupBox | None = None
        self.hgrp: QGroupBox | None = None
        self.build_ui()
        self.timer = QTimer()
        self.timer.timeout.connect(self.tick)
        self.timer.start(1000)
        self.tick()
        ThemeManager.instance().theme_changed.connect(self.restyle)

    def build_ui(self) -> None:
        lay = QVBoxLayout(self)
        lay.setContentsMargins(S.margin_page, S.margin_page, S.margin_page, S.margin_page)
        lay.setSpacing(S.spacing_lg)

        self.hero = QWidget()
        self.hero.setFixedHeight(S.hero_h)
        hl = QHBoxLayout(self.hero)
        hl.setContentsMargins(S.margin_page, S.spacing_lg, S.margin_page, S.spacing_lg)
        hl.setSpacing(S.spacing_lg)

        left = QVBoxLayout(); left.setSpacing(S.spacing_sm)
        self.h_title = QLabel("StuGo CO2 Explorer")
        self.h_sub   = QLabel("Analyse des émissions carbone des mobilités étudiantes internationales")
        left.addWidget(self.h_title); left.addWidget(self.h_sub)
        left.addSpacing(S.spacing_md)

        btns = QHBoxLayout(); btns.setSpacing(S.spacing_sm)
        b1 = PrimaryButton("Importer des fichiers", "↑")
        b1.clicked.connect(lambda: self.navigate_to.emit("import"))
        b2 = QPushButton("≡  Tableau");    b2.setMinimumHeight(S.btn_h); b2.clicked.connect(lambda: self.navigate_to.emit("table"))
        b3 = QPushButton("◈  Graphique"); b3.setMinimumHeight(S.btn_h); b3.clicked.connect(lambda: self.navigate_to.emit("chart"))
        b4 = QPushButton("⊞  Comparer");  b4.setMinimumHeight(S.btn_h); b4.clicked.connect(lambda: self.navigate_to.emit("comparison"))
        btns.addWidget(b1); btns.addWidget(b2); btns.addWidget(b3); btns.addWidget(b4)
        btns.addStretch()
        left.addLayout(btns)
        hl.addLayout(left, 1)

        cw = QWidget()
        cw.setFixedSize(round(S.dpi_scale * 155), round(S.dpi_scale * 88))
        cl = QVBoxLayout(cw)
        cl.setContentsMargins(S.spacing_md, S.spacing_sm, S.spacing_md, S.spacing_sm)
        cl.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.lbl_time = QLabel("00:00:00"); self.lbl_date = QLabel("—")
        self.lbl_time.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.lbl_date.setAlignment(Qt.AlignmentFlag.AlignCenter)
        cl.addWidget(self.lbl_time); cl.addWidget(self.lbl_date)
        self.clock_widget = cw
        hl.addWidget(cw)
        lay.addWidget(self.hero)

        self.sec_lbl = QLabel("SESSION COURANTE")
        lay.addWidget(self.sec_lbl)

        grid = QGridLayout(); grid.setSpacing(S.spacing_md)
        self.cards: dict[str, StatCard] = {}
        defs = [
            ("etu",      "Étudiants",           "0",    C["accent"]),
            ("tco2",     "Total tCO2e",          "0.00", C["orange"]),
            ("pays",     "Destinations (pays)",  "0",    C["blue"]),
            ("fichiers", "Feuilles importées",   "0",    C["purple"]),
            ("lignes",   "Lignes de données",    "0",    C["text_secondary"]),
            ("exports",  "Exports effectués",    "0",    C["yellow"]),
        ]
        for i, (k, l, d, col) in enumerate(defs):
            card = StatCard(l, d, col)
            r, cc = divmod(i, 3)
            grid.addWidget(card, r, cc)
            self.cards[k] = card
        lay.addLayout(grid)

        row = QHBoxLayout(); row.setSpacing(S.spacing_lg)

        self.zgrp = QGroupBox("ZONES CO2 — RÉFÉRENCE")
        zlay = QVBoxLayout(self.zgrp)
        zlay.setSpacing(S.spacing_sm)
        zlay.setContentsMargins(S.spacing_md, S.spacing_lg, S.spacing_md, S.spacing_md)
        for z_id, z_info in ZONES.items():
            rw = QHBoxLayout(); rw.setSpacing(S.spacing_sm)
            dot = QLabel("●")
            dot.setFixedWidth(round(S.dpi_scale * 16))
            dot.setStyleSheet(f"color:{z_info['color']};font-size:{S.font_base}px;background:transparent;border:none;")
            lbl = QLabel(z_info["label"])
            self.zone_lbls.append(lbl)
            rw.addWidget(dot); rw.addWidget(lbl); rw.addStretch()
            zlay.addLayout(rw)
        row.addWidget(self.zgrp, 2)

        self.hgrp = QGroupBox("GUIDE D'UTILISATION")
        hlay = QVBoxLayout(self.hgrp)
        hlay.setSpacing(S.spacing_md)
        hlay.setContentsMargins(S.spacing_md, S.spacing_lg, S.spacing_md, S.spacing_md)
        steps = [
            ("1", "↑  Importer",   "Ouvrez vos fichiers Excel (.xlsx, .xls)"),
            ("2", "≡  Tableau",    "Filtrez par faculté, zone, pays et seuils numériques"),
            ("3", "◈  Graphique",  "Visualisez en 2D ou en 3D interactif"),
            ("4", "⊞  Comparaison","Juxtaposez les graphiques fichier par fichier"),
            ("5", "⚙  Paramètres","Personnalisez le thème et les préférences"),
        ]
        for n, t, d in steps:
            rw = QHBoxLayout(); rw.setSpacing(S.spacing_sm)
            badge = QLabel(n)
            badge.setFixedSize(round(S.dpi_scale * 22), round(S.dpi_scale * 22))
            badge.setAlignment(Qt.AlignmentFlag.AlignCenter)
            col_v = QVBoxLayout(); col_v.setSpacing(2)
            lt = QLabel(t)
            ld = QLabel(d)
            self.guide_badges.append(badge)
            self.guide_titles.append(lt)
            self.guide_descs.append(ld)
            col_v.addWidget(lt); col_v.addWidget(ld)
            rw.addWidget(badge); rw.addLayout(col_v, 1)
            hlay.addLayout(rw)
        row.addWidget(self.hgrp, 3)
        lay.addLayout(row)
        lay.addStretch()

        self.restyle()

    def update_stats(self, df: pd.DataFrame, n_files: int, n_exports: int) -> None:
        self.cards["fichiers"].set_value(str(n_files))
        self.cards["lignes"].set_value(f"{len(df):,}" if not df.empty else "0")
        if not df.empty:
            try:
                nb = pd.to_numeric(df["nb_etudiants"], errors="coerce").fillna(0)
                tc = pd.to_numeric(df["total_tco2"],   errors="coerce").fillna(0.0)
                self.cards["etu"].set_value(f"{int(nb.sum()):,}")
                self.cards["tco2"].set_value(f"{tc.sum():.2f}")
                self.cards["pays"].set_value(str(df["pays"].nunique()))
            except Exception as e:
                log_error("home_page.HomePage.update_stats", e)
        else:
            self.cards["etu"].set_value("0")
            self.cards["tco2"].set_value("0.00")
            self.cards["pays"].set_value("0")
        self.cards["exports"].set_value(str(n_exports))

    def tick(self) -> None:
        now = datetime.now()
        JOURS = ["Lun","Mar","Mer","Jeu","Ven","Sam","Dim"]
        MOIS  = ["","Jan","Fév","Mar","Avr","Mai","Juin","Juil","Août","Sep","Oct","Nov","Déc"]
        self.lbl_time.setText(now.strftime("%H:%M:%S"))
        self.lbl_date.setText(f"{JOURS[now.weekday()]} {now.day:02d} {MOIS[now.month]}")

    def restyle(self) -> None:
        self.hero.setStyleSheet(f"background:{C['bg_elevated']};border-radius:{S.r_lg()};border:1px solid {C['border']};")
        self.h_title.setStyleSheet(f"color:{C['text_primary']};font-size:{S.font_hero}px;font-weight:800;")
        self.h_sub.setStyleSheet(f"color:{C['text_secondary']};font-size:{S.font_base + 1}px;")
        self.clock_widget.setStyleSheet(f"background:{C['bg_card']};border-radius:{S.r_md()};border:1px solid {C['border']};")
        self.lbl_time.setStyleSheet(f"color:{C['accent']};font-size:{S.font_hero - 2}px;font-weight:700;font-family:'Consolas','Courier New',monospace;background:transparent;")
        self.lbl_date.setStyleSheet(f"color:{C['text_muted']};font-size:{S.font_sm}px;background:transparent;")

        if self.sec_lbl:
            self.sec_lbl.setStyleSheet(f"color:{C['text_muted']};font-size:{S.font_tiny + 1}px;font-weight:700;letter-spacing:1px;")

        for lbl in self.zone_lbls:
            try:
                lbl.setStyleSheet(f"color:{C['text_secondary']};font-size:{S.font_base}px;")
            except Exception as e:
                log_error("home_page.HomePage.restyle", e)

        for badge in self.guide_badges:
            try:
                badge.setStyleSheet(f"background:{C['accent_dim']};color:{C['accent']};border-radius:{round(S.dpi_scale * 11)}px;font-size:{S.font_sm}px;font-weight:700;")
            except Exception as e:
                log_error("home_page.HomePage.restyle", e)

        for lt in self.guide_titles:
            try:
                lt.setStyleSheet(f"color:{C['text_primary']};font-size:{S.font_base}px;font-weight:600;")
            except Exception as e:
                log_error("home_page.HomePage.restyle", e)

        for ld in self.guide_descs:
            try:
                ld.setStyleSheet(f"color:{C['text_muted']};font-size:{S.font_sm}px;")
            except Exception as e:
                log_error("home_page.HomePage.restyle", e)
