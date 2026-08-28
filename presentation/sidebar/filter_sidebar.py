# Panneau de filtres (faculte, zone, pays, etudiants, tCO2) applique aux donnees affichees

import pandas as pd
from PyQt6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QCheckBox, QLineEdit, QScrollArea, QFrame, QSizePolicy
from PyQt6.QtCore import Qt, pyqtSignal as Signal

from shared.constants import C, ZONES
from shared.scaling import S
from presentation.theme.theme_manager import ThemeManager
from shared.logging.file_logger import log_error, log_msg
from presentation.widgets.primitives import StepWidget


class FilterSidebar(QWidget):
    filter_changed = Signal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self.chk_faculties: dict[str, QCheckBox] = {}
        self.chk_zones: dict[int, QCheckBox] = {}
        self.sec_labels: list[QLabel] = []
        self.minmax_labels: list[QLabel] = []
        self.build_ui()
        self.restyle()
        ThemeManager.instance().theme_changed.connect(self.restyle)

    def build_ui(self) -> None:
        outer = QVBoxLayout(self)
        outer.setContentsMargins(0, 0, 0, 0)
        outer.setSpacing(0)

        self.header = QWidget()
        self.header.setMinimumHeight(S.header_h - S.spacing_md)
        hl = QHBoxLayout(self.header)
        hl.setContentsMargins(S.margin_card, S.spacing_sm, S.spacing_sm, S.spacing_sm)
        hl.setSpacing(S.spacing_sm)
        self.h_title = QLabel("Filtres")
        hl.addWidget(self.h_title, 1)
        self.btn_reset = QPushButton("↺ Réinit.")
        self.btn_reset.setMinimumHeight(S.btn_h_sm)
        self.btn_reset.setMinimumWidth(round(S.dpi_scale * 72))
        self.btn_reset.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_reset.clicked.connect(self.reset_filters)
        hl.addWidget(self.btn_reset)
        outer.addWidget(self.header)

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        content = QWidget()
        content.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Preferred)
        content.setMaximumWidth(round(S.dpi_scale * 240))
        cl = QVBoxLayout(content)
        pad_h = S.spacing_md
        cl.setContentsMargins(pad_h, S.spacing_sm, pad_h, pad_h)
        cl.setSpacing(S.spacing_sm)

        cl.addWidget(self.sec("FACULTÉ"))
        self.fac_lay = QVBoxLayout()
        self.fac_lay.setSpacing(S.spacing_sm // 2)
        self.fac_lay.setContentsMargins(0, 0, 0, 0)
        fac_wrap = QWidget()
        fac_wrap.setLayout(self.fac_lay)
        cl.addWidget(fac_wrap)

        cl.addWidget(self.sec("ZONE CO2"))
        for z, info in ZONES.items():
            row_w = QWidget()
            row_l = QHBoxLayout(row_w)
            row_l.setSpacing(S.spacing_sm)
            row_l.setContentsMargins(0, 1, 0, 1)
            dot = QLabel("●")
            dot.setFixedWidth(round(S.dpi_scale * 14))
            dot.setStyleSheet(f"color:{info['color']};font-size:{S.font_sm}px;background:transparent;border:none;")
            cb = QCheckBox(f"Zone {z}")
            cb.setChecked(True)
            cb.setMinimumHeight(S.btn_h_sm)
            cb.setMinimumWidth(0)
            cb.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Preferred)
            cb.stateChanged.connect(self.filter_changed)
            cb.setToolTip(info["label"])
            self.chk_zones[z] = cb
            row_l.addWidget(dot)
            row_l.addWidget(cb, 1)
            cl.addWidget(row_w)

        cl.addWidget(self.sec("PAYS (recherche)"))
        self.txt_pays = QLineEdit()
        self.txt_pays.setPlaceholderText("Chercher un pays…")
        self.txt_pays.setMinimumHeight(S.input_h)
        self.txt_pays.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        self.txt_pays.textChanged.connect(self.filter_changed)
        cl.addWidget(self.txt_pays)

        cl.addWidget(self.sec("NB ÉTUDIANTS"))
        cl.addLayout(self.minmax_row("spin_etu_min", "spin_etu_max", dict(range=(0, 99999), value_min=0, value_max=99999)))
        self.chk_hide_zero = QCheckBox("Masquer les 0 étudiant")
        self.chk_hide_zero.setMinimumHeight(S.btn_h_sm)
        self.chk_hide_zero.stateChanged.connect(self.filter_changed)
        cl.addWidget(self.chk_hide_zero)

        cl.addWidget(self.sec("TOTAL tCO2e"))
        cl.addLayout(self.minmax_row("spin_tco2_min", "spin_tco2_max", dict(range=(0, 999999), value_min=0.0, value_max=999999.0, decimals=2)))

        cl.addStretch()
        scroll.setWidget(content)
        outer.addWidget(scroll)

    def minmax_row(self, attr_min, attr_max, opts) -> QVBoxLayout:
        # Min and Max used to sit side by side, but the sidebar is too narrow
        # for two steppers at once -- each one only had ~50px, so big values
        # got clipped. Stacking them gives each stepper the full width.
        vl = QVBoxLayout()
        vl.setSpacing(S.spacing_sm)
        vl.setContentsMargins(0, 0, 0, S.spacing_sm)

        r0, r1   = opts["range"]
        decimals = opts.get("decimals", 0)

        for label_text, attr_name, value in (
            ("Min", attr_min, opts["value_min"]),
            ("Max", attr_max, opts["value_max"]),
        ):
            row = QHBoxLayout()
            row.setSpacing(S.spacing_sm)
            lbl = QLabel(label_text)
            lbl.setFixedWidth(round(S.dpi_scale * 30))
            self.minmax_labels.append(lbl)
            lbl.setStyleSheet(f"color:{C['accent']};font-size:{S.font_sm}px;font-weight:600;background:transparent;")
            sp = StepWidget(lo=r0, hi=r1, val=value, decimals=decimals)
            sp.setMinimumHeight(S.input_h + S.spacing_sm)
            sp.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
            sp.valueChanged.connect(self.filter_changed)
            setattr(self, attr_name, sp)
            row.addWidget(lbl)
            row.addWidget(sp, 1)
            vl.addLayout(row)
        return vl

    def sec(self, text: str) -> QLabel:
        l = QLabel(text)
        l.setWordWrap(True)
        l.setMinimumWidth(0)
        l.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Preferred)
        self.sec_labels.append(l)
        self.apply_sec_style(l)
        return l

    def apply_sec_style(self, l: QLabel) -> None:
        l.setStyleSheet(f"color:{C['text_muted']};font-size:{S.font_tiny + 1}px;font-weight:700;letter-spacing:0.8px;padding:{S.spacing_lg}px 0 {S.spacing_sm}px 0;background:transparent;")

    def refresh_faculties(self, df: pd.DataFrame) -> None:
        try:
            current = set(self.chk_faculties.keys())
            new = set(df["sheet_id"].unique()) if not df.empty else set()
            for fac in current - new:
                cb = self.chk_faculties.pop(fac)
                cb.setParent(None)
                cb.deleteLater()
            for fac in sorted(new - current):
                max_ch = 26
                display = (fac[:max_ch] + "…") if len(fac) > max_ch else fac
                cb = QCheckBox(display)
                cb.setToolTip(fac)
                cb.setChecked(True)
                cb.setMinimumWidth(0)
                cb.setMinimumHeight(S.btn_h_sm)
                cb.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Preferred)
                cb.stateChanged.connect(self.filter_changed)
                self.chk_faculties[fac] = cb
                self.fac_lay.addWidget(cb)
            self.restyle_checkboxes()
        except Exception as e:
            log_error("filter_sidebar.FilterSidebar.refresh_faculties", e)

    def apply(self, df: pd.DataFrame) -> pd.DataFrame:
        if df.empty:
            return df
        try:
            sel_fac = [f for f, cb in self.chk_faculties.items() if cb.isChecked()]
            if self.chk_faculties:
                if not sel_fac:
                    return df.iloc[0:0]
                df = df[df["sheet_id"].isin(sel_fac)].copy()

            sel_zones = [z for z, cb in self.chk_zones.items() if cb.isChecked()]
            if not sel_zones:
                return df.iloc[0:0]
            df = df[df["zone"].isin(sel_zones)].copy()

            txt = self.txt_pays.text().strip()
            if txt:
                df = df[df["pays"].astype(str).str.contains(txt, case=False, na=False, regex=False)].copy()

            etu_min = self.spin_etu_min.value()
            etu_max = self.spin_etu_max.value()
            nb_etu_col = pd.to_numeric(df["nb_etudiants"], errors="coerce").fillna(0)
            df = df[(nb_etu_col >= etu_min) & (nb_etu_col <= etu_max)].copy()

            tco2_min = self.spin_tco2_min.value()
            tco2_max = self.spin_tco2_max.value()
            tco2_col = pd.to_numeric(df["total_tco2"], errors="coerce").fillna(0.0)
            df = df[(tco2_col >= tco2_min) & (tco2_col <= tco2_max)].copy()

            if self.chk_hide_zero.isChecked():
                nb_etu_col2 = pd.to_numeric(df["nb_etudiants"], errors="coerce").fillna(0)
                df = df[nb_etu_col2 > 0].copy()

        except Exception as e:
            log_error("filter_sidebar.FilterSidebar.apply", e)

        return df.reset_index(drop=True)

    def reset_filters(self) -> None:
        try:
            for cb in self.chk_faculties.values():
                cb.setChecked(True)
            for cb in self.chk_zones.values():
                cb.setChecked(True)
            self.txt_pays.clear()
            self.spin_etu_min.setValue(0)
            self.spin_etu_max.setValue(99999)
            self.spin_tco2_min.setValue(0.0)
            self.spin_tco2_max.setValue(999999.0)
            self.chk_hide_zero.setChecked(False)
            self.filter_changed.emit()
        except Exception as e:
            log_error("filter_sidebar.FilterSidebar.reset_filters", e)

    def get_state(self) -> dict:
        try:
            return {
                "fac": {f: cb.isChecked() for f, cb in self.chk_faculties.items()},
                "zones": {str(z): cb.isChecked() for z, cb in self.chk_zones.items()},
                "pays_txt": self.txt_pays.text(),
                "etu_min": self.spin_etu_min.value(),
                "etu_max": self.spin_etu_max.value(),
                "tco2_min": self.spin_tco2_min.value(),
                "tco2_max": self.spin_tco2_max.value(),
                "hide_zero": self.chk_hide_zero.isChecked(),
            }
        except Exception as e:
            log_error("filter_sidebar.FilterSidebar.get_state", e)
            return {}

    def restore_state(self, state: dict) -> None:
        try:
            for f, v in state.get("fac", {}).items():
                if f in self.chk_faculties:
                    self.chk_faculties[f].setChecked(v)
            for z_str, v in state.get("zones", {}).items():
                z = int(z_str)
                if z in self.chk_zones:
                    self.chk_zones[z].setChecked(v)
            self.txt_pays.setText(state.get("pays_txt", ""))
            self.spin_etu_min.setValue(state.get("etu_min", 0))
            self.spin_etu_max.setValue(state.get("etu_max", 99999))
            self.spin_tco2_min.setValue(float(state.get("tco2_min", 0.0)))
            self.spin_tco2_max.setValue(float(state.get("tco2_max", 999999.0)))
            self.chk_hide_zero.setChecked(state.get("hide_zero", False))
        except Exception as e:
            log_error("filter_sidebar.FilterSidebar.restore_state", e)

    def restyle(self) -> None:
        try:
            fw = max(round(S.dpi_scale * 230), 200)
            self.setMinimumWidth(fw)
            self.setMaximumWidth(max(fw, round(S.dpi_scale * 270)))
            self.setStyleSheet(f"background:{C['bg_deep']};border-right:1px solid {C['border']};")
            if hasattr(self, "header"):
                self.header.setStyleSheet(f"background:{C['bg_deep']};border-bottom:1px solid {C['border']};")
            if hasattr(self, "h_title"):
                self.h_title.setStyleSheet(f"font-size:{S.font_base + 1}px;font-weight:700;color:{C['text_primary']};background:transparent;")
            if hasattr(self, "btn_reset"):
                self.btn_reset.setStyleSheet(f"""
                    QPushButton {{
                        background:transparent;
                        color:{C['text_muted']};
                        border:1px solid {C['border']};
                        border-radius:{S.r_sm()};
                        padding:{S.spacing_sm // 2}px {S.spacing_sm}px;
                        font-size:{S.font_sm}px;
                        min-height:{S.btn_h_sm}px;
                    }}
                    QPushButton:hover {{
                        color:{C['accent']};
                        border-color:{C['accent']};
                        background:{C['accent_dim']};
                    }}
                """)
            self.restyle_checkboxes()
            for l in getattr(self, 'sec_labels', []):
                try:
                    self.apply_sec_style(l)
                except Exception as e:
                    log_error("filter_sidebar.FilterSidebar.restyle", e)
            for l in getattr(self, 'minmax_labels', []):
                try:
                    l.setStyleSheet(f"color:{C['accent']};font-size:{S.font_sm}px;font-weight:600;background:transparent;")
                except Exception as e:
                    log_error("filter_sidebar.FilterSidebar.restyle", e)
        except Exception as e:
            log_error("filter_sidebar.FilterSidebar.restyle", e)

    def restyle_checkboxes(self) -> None:
        try:
            for z, cb in self.chk_zones.items():
                zc = ZONES[z]["color"]
                cb.setStyleSheet(f"QCheckBox{{color:{C['text_secondary']};font-size:{S.font_sm}px;min-height:{S.btn_h_sm}px;background:transparent;}}QCheckBox::indicator{{border:1px solid {zc};width:{round(S.dpi_scale*14)}px;height:{round(S.dpi_scale*14)}px;border-radius:{round(S.dpi_scale*3)}px;background:{C['bg_input']};}}QCheckBox::indicator:checked{{background:{zc};border-color:{zc};}}QCheckBox::indicator:hover{{border-color:{C['accent']};}}QCheckBox:hover{{color:{C['text_primary']};}}")
            for cb in self.chk_faculties.values():
                cb.setStyleSheet(f"QCheckBox{{color:{C['text_secondary']};font-size:{S.font_sm}px;min-height:{S.btn_h_sm}px;background:transparent;}}QCheckBox::indicator{{border:1px solid {C['border_light']};width:{round(S.dpi_scale*14)}px;height:{round(S.dpi_scale*14)}px;border-radius:{round(S.dpi_scale*3)}px;background:{C['bg_input']};}}QCheckBox::indicator:checked{{background:{C['accent']};border-color:{C['accent']};}}QCheckBox:hover{{color:{C['text_primary']};}}")
        except Exception as e:
            log_error("filter_sidebar.FilterSidebar.restyle_checkboxes", e)
