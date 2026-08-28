# Gere l'export du graphique en image et des donnees en CSV

import os
from matplotlib.figure import Figure
from PyQt6.QtWidgets import QFileDialog, QMessageBox
from shared.constants import C
from shared.logging.action_logger import ActionLogger

class ExportService:

    @staticmethod
    def export_png(fig: Figure, parent=None) -> bool:
        path, _ = QFileDialog.getSaveFileName(parent, "Exporter le graphique", "graphique.png", "PNG (*.png);;PDF (*.pdf);;SVG (*.svg)")
        if not path:
            return False
        try:
            fig.savefig(path, dpi=150, bbox_inches="tight", facecolor=C["bg_base"])
            ActionLogger.instance().log("export_png", f"Export -> {os.path.basename(path)}")
            QMessageBox.information(parent, "Export reussi", f"Fichier: {path}")
            return True
        except Exception as e:
            QMessageBox.warning(parent, "Erreur export", str(e))
            return False

    @staticmethod
    def export_csv(df, parent=None) -> bool:
        path, _ = QFileDialog.getSaveFileName(parent, "Exporter CSV", "co2_export.csv", "CSV (*.csv)")
        if not path:
            return False
        try:
            df.to_csv(path, index=False, sep=";", encoding="utf-8-sig")
            ActionLogger.instance().log("export_csv", f"CSV -> {os.path.basename(path)}")
            QMessageBox.information(parent, "Export CSV", f"Fichier: {path}")
            return True
        except Exception as e:
            QMessageBox.warning(parent, "Erreur CSV", str(e))
            return False
