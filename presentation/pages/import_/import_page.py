# Page d'import : glisser-deposer et liste des fichiers charges avec bouton supprimer

import os
import pandas as pd

from PyQt6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QScrollArea, QFileDialog, QMessageBox
from PyQt6.QtCore import Qt, pyqtSignal as Signal

from shared.constants import C, FAC_COLORS
from shared.scaling import S
from shared.logging.file_logger import log_error, log_msg
from presentation.theme.theme_manager import ThemeManager
from presentation.widgets.primitives import PrimaryButton, DangerButton


class ImportPage(QWidget):
    files_added  = Signal(list)
    file_removed = Signal(str)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.entries: dict[str, dict] = {}
        self.build_ui()
        ThemeManager.instance().theme_changed.connect(self.restyle)

    def build_ui(self) -> None:
        lay = QVBoxLayout(self)
        lay.setContentsMargins(S.margin_page, S.margin_page, S.margin_page, S.margin_page)
        lay.setSpacing(S.spacing_lg)
        hdr = QHBoxLayout(); hdr.setSpacing(S.spacing_md)
        title_col = QVBoxLayout(); title_col.setSpacing(S.spacing_sm // 2)
        self.t1 = QLabel("Import de fichiers")
        self.t2 = QLabel("Fichiers Excel de mobilite etudiante (.xlsx / .xls)")
        title_col.addWidget(self.t1); title_col.addWidget(self.t2)
        hdr.addLayout(title_col, 1)
        self.btn_import = PrimaryButton("Ajouter des fichiers", "↑")
        self.btn_import.setFixedHeight(S.btn_h_lg)
        self.btn_import.clicked.connect(self.browse)
        hdr.addWidget(self.btn_import)
        lay.addLayout(hdr)
        self.drop_zone = QWidget()
        self.drop_zone.setFixedHeight(round(S.dpi_scale * 96))
        dz_lay = QVBoxLayout(self.drop_zone)
        dz_lay.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.drop_lbl = QLabel("Glissez-deposez vos fichiers Excel (.xlsx / .xls) ou CSV StuGo (.csv) ici  —  ou cliquez Ajouter des fichiers")
        self.drop_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
        dz_lay.addWidget(self.drop_lbl)
        lay.addWidget(self.drop_zone)
        list_hdr = QHBoxLayout(); list_hdr.setSpacing(S.spacing_sm)
        self.lbl_count = QLabel("Aucun fichier importe")
        list_hdr.addWidget(self.lbl_count, 1)
        btn_clear = DangerButton("Tout supprimer")
        btn_clear.clicked.connect(self.clear_all)
        list_hdr.addWidget(btn_clear)
        lay.addLayout(list_hdr)
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.cards_widget = QWidget()
        self.cards_lay = QVBoxLayout(self.cards_widget)
        self.cards_lay.setContentsMargins(0, 0, 0, 0)
        self.cards_lay.setSpacing(S.spacing_sm)
        self.cards_lay.addStretch()
        scroll.setWidget(self.cards_widget)
        lay.addWidget(scroll, 1)
        self.restyle()

    def add_file(self, source_uid: str, label: str, filepath: str, df_source: pd.DataFrame) -> None:
        if source_uid in self.entries:
            return
        self.entries[source_uid] = {"label": label, "filepath": filepath, "card": None, "fc": ""}
        sheet = label.split("::")[-1] if "::" in label else label
        fname = os.path.basename(filepath)
        fc    = FAC_COLORS[(len(self.entries) - 1) % len(FAC_COLORS)]
        card = QWidget()
        card.setFixedHeight(round(S.dpi_scale * 90))
        card_lay = QHBoxLayout(card)
        card_lay.setContentsMargins(S.margin_card, S.spacing_md, S.spacing_md, S.spacing_md)
        card_lay.setSpacing(S.spacing_md)
        info_col = QVBoxLayout(); info_col.setSpacing(S.spacing_sm // 2)
        lbl_sheet = QLabel(sheet)
        lbl_sheet.setStyleSheet(f"color:{fc};font-weight:700;font-size:{S.font_base + 1}px;")
        lbl_file = QLabel(fname)
        lbl_file.setStyleSheet(f"color:{C['text_muted']};font-size:{S.font_sm}px;")
        info_col.addWidget(lbl_sheet); info_col.addWidget(lbl_file)
        try:
            df_s = df_source[df_source["source_uid"] == source_uid] if not df_source.empty else pd.DataFrame()
            if not df_s.empty:
                nb  = int(pd.to_numeric(df_s["nb_etudiants"], errors="coerce").fillna(0).sum())
                tc  = pd.to_numeric(df_s["total_tco2"], errors="coerce").fillna(0.0).sum()
                npa = df_s["pays"].nunique()
                txt = f"{nb:,} et. - {tc:.1f} tCO2e - {npa} pays"
            else:
                txt = "-"
        except Exception as e:
            log_error("import_page.ImportPage.add_file", e)
            txt = "-"
        lbl_stats = QLabel(txt)
        lbl_stats.setStyleSheet(f"color:{C['text_secondary']};font-size:{S.font_sm}px;")
        info_col.addWidget(lbl_stats)
        card_lay.addLayout(info_col, 1)
        btn_del = QPushButton("×")
        btn_del.setFixedSize(round(S.dpi_scale * 30), round(S.dpi_scale * 30))
        btn_del.setStyleSheet(f"QPushButton{{background:transparent;color:{C['text_muted']};border:none;font-size:{S.font_base + 2}px;}}QPushButton:hover{{color:{C['red']};}}")
        btn_del.clicked.connect(lambda _, uid=source_uid, w=card: self.remove_card(uid, w))
        card_lay.addWidget(btn_del, 0, Qt.AlignmentFlag.AlignTop)
        card.setStyleSheet(f"background:{C['bg_elevated']};border-radius:{S.r_md()};border:1px solid {C['border']};border-left:3px solid {fc};")
        self.entries[source_uid].update({"card": card, "lbl_file": lbl_file, "lbl_stats": lbl_stats, "btn_del": btn_del, "fc": fc})
        self.cards_lay.insertWidget(self.cards_lay.count() - 1, card)
        self.refresh_count()

    def browse(self) -> None:
        paths, _ = QFileDialog.getOpenFileNames(self, "Importer des fichiers", "", "Fichiers supportés (*.xlsx *.xls *.csv);;Excel (*.xlsx *.xls);;CSV StuGo (*.csv)")
        if paths: self.files_added.emit(paths)

    def clear_all(self) -> None:
        if not self.entries: return
        reply = QMessageBox.question(self, "Tout supprimer", f"Supprimer les {len(self.entries)} feuille(s) importee(s) ?", QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
        if reply == QMessageBox.StandardButton.Yes:
            for uid in list(self.entries.keys()): self.file_removed.emit(uid)
            self.entries.clear()
            while self.cards_lay.count() > 1:
                item = self.cards_lay.takeAt(0)
                if item.widget(): item.widget().deleteLater()
            self.refresh_count()

    def remove_card(self, source_uid: str, widget: QWidget) -> None:
        label = self.entries.get(source_uid, {}).get("label", source_uid)
        reply = QMessageBox.question(self, "Supprimer", f"Retirer '{label.split(chr(58)*2)[-1]}' ?", QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
        if reply == QMessageBox.StandardButton.Yes:
            self.entries.pop(source_uid, None)
            widget.setParent(None); widget.deleteLater()
            self.file_removed.emit(source_uid)
            self.refresh_count()

    def refresh_count(self) -> None:
        n = len(self.entries)
        self.lbl_count.setText("Aucun fichier" if n == 0 else f"{n} feuille(s) importee(s)")

    def restyle(self) -> None:
        self.t1.setStyleSheet(f"font-size:{S.font_xl}px;font-weight:800;color:{C['text_primary']};")
        self.t2.setStyleSheet(f"font-size:{S.font_base}px;color:{C['text_secondary']};")
        self.drop_zone.setStyleSheet(f"background:{C['bg_elevated']};border:2px dashed {C['border_light']};border-radius:{S.r_lg()};")
        self.drop_lbl.setStyleSheet(f"color:{C['text_muted']};font-size:{S.font_base}px;")
        self.lbl_count.setStyleSheet(f"color:{C['text_muted']};font-size:{S.font_sm}px;")
        for entry in self.entries.values():
            fc   = entry.get("fc", C["accent"])
            card = entry.get("card")
            lf   = entry.get("lbl_file")
            ls   = entry.get("lbl_stats")
            bd   = entry.get("btn_del")
            try:
                if card:
                    card.setStyleSheet(f"background:{C['bg_elevated']};border-radius:{S.r_md()};border:1px solid {C['border']};border-left:3px solid {fc};")
                if lf:
                    lf.setStyleSheet(f"color:{C['text_muted']};font-size:{S.font_sm}px;")
                if ls:
                    ls.setStyleSheet(f"color:{C['text_secondary']};font-size:{S.font_sm}px;")
                if bd:
                    bd.setStyleSheet(f"QPushButton{{background:transparent;color:{C['text_muted']};border:none;font-size:{S.font_base + 2}px;}}QPushButton:hover{{color:{C['red']};}}")
            except Exception as e:
                log_error("import_page.ImportPage.restyle", e)
