# Barre de controles au-dessus d'un graphique (type, axes, mode 3D, rotation)

from PyQt6.QtWidgets import QWidget, QHBoxLayout, QVBoxLayout, QLabel, QPushButton, QComboBox, QSlider, QSizePolicy
from PyQt6.QtCore import Qt, QTimer, pyqtSignal as Signal

from shared.constants import C, CHART_TYPES, COLUMN_LABELS, CHART_3D_COMPATIBLE
from shared.scaling import S
from shared.logging.file_logger import log_error, log_msg
from presentation.theme.theme_manager import ThemeManager
from presentation.widgets.primitives import PrimaryButton, StepWidget


class ChartControls(QWidget):
    changed = Signal()

    def __init__(self, show_export: bool = True, parent=None):
        super().__init__(parent)
        self._mode_3d = False
        self._elev    = 28
        self._azim    = -48
        self.rot_timer = QTimer(self)
        self.rot_timer.setSingleShot(True)
        self.rot_timer.setInterval(200)
        self.rot_timer.timeout.connect(self.changed)
        self.build_ui(show_export)
        self.restyle()
        self.update_dim_btns()
        ThemeManager.instance().theme_changed.connect(self.restyle)
        ThemeManager.instance().theme_changed.connect(self.update_dim_btns)

    def build_ui(self, show_export: bool) -> None:
        lay = QVBoxLayout(self)
        lay.setContentsMargins(0, 0, 0, 0)
        lay.setSpacing(0)

        row1 = QWidget()
        row1.setMinimumHeight(S.toolbar_h)
        r1l  = QHBoxLayout(row1)
        r1l.setContentsMargins(S.spacing_md, S.spacing_sm, S.spacing_md, S.spacing_sm)
        r1l.setSpacing(S.spacing_sm)

        dim_sz = max(36, S.btn_h)
        self.btn_2d = QPushButton("2D")
        self.btn_2d.setCheckable(True); self.btn_2d.setChecked(True)
        self.btn_2d.setFixedSize(dim_sz + 12, dim_sz)
        self.btn_3d = QPushButton("3D")
        self.btn_3d.setCheckable(True)
        self.btn_3d.setFixedSize(dim_sz + 12, dim_sz)
        self.btn_2d.clicked.connect(lambda: self.set_mode(False))
        self.btn_3d.clicked.connect(lambda: self.set_mode(True))
        r1l.addWidget(self.btn_2d); r1l.addWidget(self.btn_3d)
        r1l.addSpacing(S.spacing_md)

        r1l.addWidget(self.lbl("Type :"))
        self.combo_chart = QComboBox()
        self.combo_chart.setMinimumWidth(round(S.dpi_scale * 170))
        self.combo_chart.setMinimumHeight(S.input_h)
        self.combo_chart.setSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Fixed)
        for cid, label, icon in CHART_TYPES:
            self.combo_chart.addItem(f"{icon} {label}", cid)
        self.combo_chart.currentIndexChanged.connect(self.on_type_changed)
        r1l.addWidget(self.combo_chart)
        r1l.addStretch()

        if show_export:
            self.btn_export = PrimaryButton("Exporter PNG", "⇓")
            self.btn_export.setFixedHeight(S.btn_h_lg)
            r1l.addWidget(self.btn_export)

        lay.addWidget(row1)

        row2 = QWidget()
        row2.setMinimumHeight(S.toolbar_h - S.spacing_sm)
        r2l  = QHBoxLayout(row2)
        r2l.setContentsMargins(S.spacing_md, S.spacing_sm // 2, S.spacing_md, S.spacing_sm // 2)
        r2l.setSpacing(S.spacing_sm)

        r2l.addWidget(self.lbl("Axe X :"))
        self.combo_x = QComboBox()
        self.combo_x.setMinimumWidth(round(S.dpi_scale * 100))
        self.combo_x.setMinimumHeight(S.input_h)
        for val, lbl in [("sheet_id","Faculte"),("zone_label","Zone"),("pays","Pays")]:
            self.combo_x.addItem(lbl, val)
        self.combo_x.currentIndexChanged.connect(self.changed)
        r2l.addWidget(self.combo_x)

        r2l.addWidget(self.lbl("Valeur :"))
        self.combo_y = QComboBox()
        self.combo_y.setMinimumWidth(round(S.dpi_scale * 130))
        self.combo_y.setMinimumHeight(S.input_h)
        for val, lbl in [("total_tco2","Total tCO2e"),("nb_etudiants","Nb Etudiants"),("tco2e_par_voyage","tCO2e/voyage")]:
            self.combo_y.addItem(lbl, val)
        self.combo_y.currentIndexChanged.connect(self.changed)
        r2l.addWidget(self.combo_y)

        r2l.addWidget(self.lbl("Couleur :"))
        self.combo_group = QComboBox()
        self.combo_group.setMinimumWidth(round(S.dpi_scale * 90))
        self.combo_group.setMinimumHeight(S.input_h)
        for val, lbl in [("sheet_id","Faculte"),("zone_label","Zone"),("aucun","—")]:
            self.combo_group.addItem(lbl, val)
        self.combo_group.currentIndexChanged.connect(self.changed)
        r2l.addWidget(self.combo_group)

        self.lbl_topn = self.lbl("Top pays :")
        r2l.addWidget(self.lbl_topn)
        self.spin_topn = StepWidget(lo=3, hi=50, val=15, step=1)
        self.spin_topn.setMinimumWidth(round(S.dpi_scale * 100))
        self.spin_topn.setMinimumHeight(S.input_h)
        self.spin_topn.valueChanged.connect(self.changed)
        r2l.addWidget(self.spin_topn)
        r2l.addStretch()
        lay.addWidget(row2)

        self.rot_bar = QWidget()
        self.rot_bar.setMinimumHeight(S.toolbar_h - S.spacing_sm)
        rl = QHBoxLayout(self.rot_bar)
        rl.setContentsMargins(S.spacing_md, S.spacing_sm // 2, S.spacing_md, S.spacing_sm // 2)
        rl.setSpacing(S.spacing_sm)
        rl.addWidget(self.lbl("Elevation :"))
        self.lbl_elev = QLabel("28°")
        self.lbl_elev.setFixedWidth(round(S.dpi_scale * 38))
        self.sld_elev = QSlider(Qt.Orientation.Horizontal)
        self.sld_elev.setRange(-90, 90); self.sld_elev.setValue(28)
        self.sld_elev.setMinimumWidth(round(S.dpi_scale * 120))
        self.sld_elev.valueChanged.connect(self.on_elev)
        rl.addWidget(self.sld_elev); rl.addWidget(self.lbl_elev)
        rl.addSpacing(S.spacing_md)
        rl.addWidget(self.lbl("Azimut :"))
        self.lbl_azim = QLabel("-48°")
        self.lbl_azim.setFixedWidth(round(S.dpi_scale * 44))
        self.sld_azim = QSlider(Qt.Orientation.Horizontal)
        self.sld_azim.setRange(-180, 180); self.sld_azim.setValue(-48)
        self.sld_azim.setMinimumWidth(round(S.dpi_scale * 140))
        self.sld_azim.valueChanged.connect(self.on_azim)
        rl.addWidget(self.sld_azim); rl.addWidget(self.lbl_azim)
        btn_r = QPushButton("↺ Reset")
        btn_r.setMinimumHeight(S.btn_h_sm)
        btn_r.clicked.connect(lambda: (self.sld_elev.setValue(28), self.sld_azim.setValue(-48)))
        rl.addWidget(btn_r); rl.addStretch()
        lay.addWidget(self.rot_bar)
        self.rot_bar.setVisible(False)

        self.lbl_compat = QLabel("")
        self.lbl_compat.setMinimumHeight(S.spacing_lg)
        lay.addWidget(self.lbl_compat)

    @property
    def mode_3d(self)    -> bool: return self._mode_3d
    @property
    def elev(self)       -> int: return self._elev
    @property
    def azim(self)       -> int: return self._azim
    @property
    def chart_type(self) -> str: return self.combo_chart.currentData() or ""
    @property
    def x_col(self)      -> str: return self.combo_x.currentData() or ""
    @property
    def y_col(self)      -> str: return self.combo_y.currentData() or ""
    @property
    def group_col(self)  -> str: return self.combo_group.currentData() or ""
    @property
    def top_n(self)      -> int: return self.spin_topn.value()

    def set_compat_msg(self, msg: str) -> None:
        try: self.lbl_compat.setText(msg)
        except Exception as e: log_error("chart_controls.ChartControls.set_compat_msg", e)

    def lbl(self, t: str) -> QLabel:
        l = QLabel(t)
        l.setStyleSheet(f"color:{C['text_muted']};font-size:{S.font_sm}px;")
        return l

    def set_mode(self, m: bool) -> None:
        self._mode_3d = m
        self.btn_2d.setChecked(not m); self.btn_3d.setChecked(m)
        self.rot_bar.setVisible(m)
        self.update_dim_btns()
        self.changed.emit()

    def on_elev(self, v: int) -> None:
        self._elev = v
        try: self.lbl_elev.setText(f"{v}°")
        except Exception as e: log_error("chart_controls.ChartControls.on_elev", e)
        self.rot_timer.start()

    def on_azim(self, v: int) -> None:
        self._azim = v
        try: self.lbl_azim.setText(f"{v}°")
        except Exception as e: log_error("chart_controls.ChartControls.on_azim", e)
        self.rot_timer.start()

    def on_type_changed(self) -> None:
        try:
            self.combo_x.setEnabled(True)
            self.combo_y.setEnabled(True)
            self.combo_group.setEnabled(True)
        except Exception as e: log_error("chart_controls.ChartControls.on_type_changed", e)
        self.changed.emit()

    def update_dim_btns(self) -> None:
        try:
            ac = C["accent"]; ad = C["accent_dim"]; inp = C["bg_input"]; mu = C["text_muted"]
            act = f"QPushButton{{background:{ad};color:{ac};border:2px solid {ac};font-weight:700;border-radius:{S.r_sm()};font-size:{S.font_base}px;}}QPushButton:hover{{background:{ac};color:{C['bg_deep']};}}"
            ina = f"QPushButton{{background:{inp};color:{mu};border:1px solid {C['border']};border-radius:{S.r_sm()};font-size:{S.font_base}px;}}QPushButton:hover{{background:{C['bg_hover']};color:{C['text_primary']};border-color:{C['border_light']};}}"
            self.btn_2d.setStyleSheet(ina if self._mode_3d else act)
            self.btn_3d.setStyleSheet(act if self._mode_3d else ina)
        except Exception as e: log_error("chart_controls.ChartControls.update_dim_btns", e)

    def restyle(self) -> None:
        try:
            if hasattr(self, "rot_bar"):
                self.rot_bar.setStyleSheet(f"background:{C['bg_card']};border-radius:{S.r_sm()};border:1px solid {C['border']};")
            if hasattr(self, "lbl_elev"):
                self.lbl_elev.setStyleSheet(f"color:{C['accent']};font-weight:700;font-size:{S.font_base}px;")
            if hasattr(self, "lbl_azim"):
                self.lbl_azim.setStyleSheet(f"color:{C['accent']};font-weight:700;font-size:{S.font_base}px;")
            if hasattr(self, "lbl_compat"):
                self.lbl_compat.setStyleSheet(f"color:{C['yellow']};font-size:{S.font_sm}px;font-style:italic;padding:0 {S.spacing_sm}px;")
            if hasattr(self, "lbl_topn"):
                self.lbl_topn.setStyleSheet(f"color:{C['accent']};font-size:{S.font_sm}px;font-weight:600;")
        except Exception as e: log_error("chart_controls.ChartControls.restyle", e)
        self.update_dim_btns()
