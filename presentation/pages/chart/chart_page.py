# Page graphique : affiche le canvas matplotlib pilote par la barre de controles

import os
import pandas as pd

from PyQt6.QtWidgets import QWidget, QVBoxLayout, QFileDialog, QMessageBox, QSizePolicy
from matplotlib.figure import Figure
from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.backends.backend_qtagg import NavigationToolbar2QT as NavToolbar

from shared.constants import C, CHART_3D_COMPATIBLE
from shared.scaling import S
from shared.logging.action_logger import ActionLogger
from presentation.theme.theme_manager import ThemeManager
from presentation.widgets.chart_controls import ChartControls
from rendering.strategies.renderer_2d import render_chart
from rendering.strategies.renderer_3d import render_chart_3d
from shared.logging.file_logger import log_error, log_msg


class ChartPage(QWidget):
    def __init__(self, df: pd.DataFrame, parent=None):
        super().__init__(parent)
        self.df = df
        self.build_ui()
        ThemeManager.instance().theme_changed.connect(self.on_theme)

    def build_ui(self) -> None:
        lay = QVBoxLayout(self)
        lay.setContentsMargins(S.spacing_md, S.spacing_md, S.spacing_md, S.spacing_md)
        lay.setSpacing(S.spacing_sm)

        self.controls = ChartControls(show_export=True)
        self.controls.changed.connect(self.refresh)
        self.controls.btn_export.clicked.connect(self.save)
        lay.addWidget(self.controls)

        dpi = max(80, round(96 * S.dpi_scale * 0.85))
        self.fig = Figure(figsize=(10, 8), dpi=dpi)
        self.fig.patch.set_facecolor(C["bg_base"])
        self.canvas = FigureCanvas(self.fig)
        self.canvas.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)

        self.nav_toolbar = NavToolbar(self.canvas, self)
        self.nav_toolbar.setMinimumHeight(S.btn_h)
        lay.addWidget(self.nav_toolbar)
        lay.addWidget(self.canvas, 1)

        self.on_theme()

    def update_data(self, df: pd.DataFrame) -> None:
        self.df = df
        self.refresh()

    def refresh(self) -> None:
        ct = self.controls.chart_type
        if not ct:
            return
        self.fig.patch.set_facecolor(C["bg_base"])
        try:
            if self.controls.mode_3d:
                render_chart_3d(self.fig, self.df, ct, self.controls.x_col, self.controls.y_col, self.controls.group_col, self.controls.top_n, elev=self.controls.elev, azim=self.controls.azim)
            else:
                render_chart(self.fig, self.df, ct, self.controls.x_col, self.controls.y_col, self.controls.group_col, self.controls.top_n)
        except Exception as e:
            log_error("chart_page.ChartPage.refresh", e)
        self.canvas.draw()
        msg = f"ℹ  «{ct}» affiché en 2D (pas de version 3D disponible)" if self.controls.mode_3d and ct not in CHART_3D_COMPATIBLE else ""
        self.controls.set_compat_msg(msg)

    def save(self) -> None:
        path, _ = QFileDialog.getSaveFileName(self, "Exporter le graphique", "graphique.png", "PNG (*.png);;PDF (*.pdf);;SVG (*.svg)")
        if path:
            try:
                self.fig.savefig(path, dpi=150, bbox_inches="tight", facecolor=C["bg_base"])
                ActionLogger.instance().log("export_png", f"Export → {os.path.basename(path)}")
                QMessageBox.information(self, "Export réussi", f"Fichier sauvegardé :\n{path}")
            except Exception as e:
                log_error("chart_page.ChartPage.save", e)
                QMessageBox.warning(self, "Erreur export", f"Impossible d'exporter :\n{e}")

    def on_theme(self) -> None:
        if hasattr(self, "nav_toolbar"):
            self.nav_toolbar.setStyleSheet(f"background:{C['bg_elevated']};border:none;color:{C['text_secondary']};font-size:{S.font_sm}px;")
        self.refresh()
