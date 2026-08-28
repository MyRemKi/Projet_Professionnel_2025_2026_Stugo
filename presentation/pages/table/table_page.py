# Page tableau : affiche toutes les lignes de donnees avec tri et statistiques rapides

import pandas as pd
from PyQt6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QComboBox, QTableView, QAbstractItemView, QToolButton
from PyQt6.QtGui import QFont
from PyQt6.QtCore import Qt

from shared.constants import C, COLUMN_LABELS
from shared.scaling import S
from shared.logging.file_logger import log_error, log_msg
from presentation.theme.theme_manager import ThemeManager
from infrastructure.models.pandas_model import PandasModel


class TablePage(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.build_ui()
        self.restyle()
        ThemeManager.instance().theme_changed.connect(self.restyle)

    def build_ui(self) -> None:
        lay = QVBoxLayout(self)
        lay.setContentsMargins(S.margin_page, S.margin_page, S.margin_page, S.margin_page)
        lay.setSpacing(S.spacing_md)
        hdr = QHBoxLayout(); hdr.setSpacing(S.spacing_sm)
        self.stats_bar = QWidget()
        self.stats_bar.setFixedHeight(S.toolbar_h - S.spacing_sm)
        sb_lay = QHBoxLayout(self.stats_bar)
        sb_lay.setContentsMargins(S.margin_card, 0, S.margin_card, 0)
        sb_lay.setSpacing(0)
        self.stat_lbls: dict[str, QLabel] = {}
        stat_defs = [("rows","Lignes"),("etu","Etudiants"),("tco2","TCO2e total"),("pays","Pays"),("moy","Moy. tCO2e/voy.")]
        for idx, (key, label) in enumerate(stat_defs):
            if idx > 0:
                sep = QWidget(); sep.setFixedSize(1, round(S.dpi_scale * 20))
                sep.setStyleSheet(f"background:{C['border']};")
                sep_wrap = QWidget()
                swl = QHBoxLayout(sep_wrap)
                swl.setContentsMargins(round(S.dpi_scale * 14), 0, round(S.dpi_scale * 14), 0)
                swl.addWidget(sep)
                sb_lay.addWidget(sep_wrap)
            cw = QWidget(); cl = QVBoxLayout(cw)
            cl.setContentsMargins(0, 0, 0, 0); cl.setSpacing(2)
            cl.setAlignment(Qt.AlignmentFlag.AlignCenter)
            lv = QLabel("-"); lk = QLabel(label)
            lv.setAlignment(Qt.AlignmentFlag.AlignCenter)
            lk.setAlignment(Qt.AlignmentFlag.AlignCenter)
            cl.addWidget(lv); cl.addWidget(lk)
            self.stat_lbls[key] = lv; self.stat_lbls[f"_{key}"] = lk
            sb_lay.addWidget(cw)
        sb_lay.addStretch()
        hdr.addWidget(self.stats_bar, 1)
        lbl_sort = QLabel("Tri :")
        lbl_sort.setStyleSheet(f"color:{C['text_muted']};font-size:{S.font_sm}px;")
        hdr.addWidget(lbl_sort)
        self.combo_sort = QComboBox()
        self.combo_sort.setMinimumWidth(round(S.dpi_scale * 140))
        self.combo_sort.setMinimumHeight(S.input_h)
        for col, label in COLUMN_LABELS.items(): self.combo_sort.addItem(label, col)
        hdr.addWidget(self.combo_sort)
        self.btn_sort_dir = QToolButton()
        self.btn_sort_dir.setText("↑ Asc")
        self.btn_sort_dir.setCheckable(True)
        self.btn_sort_dir.setMinimumHeight(S.input_h)
        self.btn_sort_dir.toggled.connect(lambda c: self.btn_sort_dir.setText("↓ Desc" if c else "↑ Asc"))
        hdr.addWidget(self.btn_sort_dir)
        self.btn_csv = QPushButton("⇓  Exporter CSV")
        self.btn_csv.setMinimumHeight(S.input_h)
        hdr.addWidget(self.btn_csv)
        lay.addLayout(hdr)
        self.table = QTableView()
        self.table.setSortingEnabled(True)
        self.table.setAlternatingRowColors(True)
        self.table.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self.table.horizontalHeader().setStretchLastSection(True)
        self.table.verticalHeader().setDefaultSectionSize(S.row_h)
        self.table.verticalHeader().setVisible(False)
        self.table.setFont(QFont("Consolas", S.font_mono))
        self.table.setShowGrid(True)
        self.model = PandasModel(pd.DataFrame(columns=PandasModel.COLS))
        self.table.setModel(self.model)
        lay.addWidget(self.table, 1)

    def update_df(self, df: pd.DataFrame) -> None:
        self.model.update_df(df)
        widths = {
            "sheet_id": round(S.dpi_scale*120), "zone": round(S.dpi_scale*55),
            "zone_label": round(S.dpi_scale*145), "pays": round(S.dpi_scale*125),
            "tco2e_par_voyage": round(S.dpi_scale*130), "nb_etudiants": round(S.dpi_scale*100),
            "total_tco2": round(S.dpi_scale*105), "fichier": round(S.dpi_scale*155),
        }
        for i, col in enumerate(PandasModel.COLS):
            self.table.setColumnWidth(i, widths.get(col, round(S.dpi_scale*90)))
        if not df.empty:
            try:
                nb = pd.to_numeric(df["nb_etudiants"], errors="coerce").fillna(0)
                tc = pd.to_numeric(df["total_tco2"], errors="coerce").fillna(0.0)
                tv = pd.to_numeric(df["tco2e_par_voyage"], errors="coerce")
                self.stat_lbls["rows"].setText(f"{len(df):,}")
                self.stat_lbls["etu"].setText(f"{int(nb.sum()):,}")
                self.stat_lbls["tco2"].setText(f"{tc.sum():.2f}")
                self.stat_lbls["pays"].setText(str(df["pays"].nunique()))
                mv = tv.mean()
                self.stat_lbls["moy"].setText(f"{mv:.4f}" if not pd.isna(mv) else "-")
            except Exception as e: log_error("table_page.TablePage.update_df", e)
        else:
            for k, l in self.stat_lbls.items():
                if not k.startswith("_"): l.setText("-")

    def restyle(self) -> None:
        self.stats_bar.setStyleSheet(f"background:{C['bg_elevated']};border-radius:{S.r_sm()};border:1px solid {C['border']};")
        for key, lbl in self.stat_lbls.items():
            if key.startswith("_"):
                lbl.setStyleSheet(f"color:{C['text_muted']};font-size:{S.font_tiny + 1}px;")
            else:
                lbl.setStyleSheet(f"color:{C['accent']};font-size:{S.font_md}px;font-weight:700;font-family:'Consolas','Courier New',monospace;")
        self.btn_csv.setStyleSheet(f"QPushButton{{color:{C['blue']};border:1px solid {C['blue']};background:transparent;border-radius:{S.r_sm()};padding:{round(S.dpi_scale*5)}px {round(S.dpi_scale*12)}px;font-size:{S.font_base}px;font-weight:600;min-height:{S.input_h}px;}}QPushButton:hover{{background:rgba(61,158,255,0.1);}}")
