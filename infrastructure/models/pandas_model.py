# Fait le lien entre le tableau pandas (donnees) et le tableau affiche a l'ecran (Qt)

import pandas as pd
from PyQt6.QtCore import Qt, QAbstractTableModel, QModelIndex
from PyQt6.QtGui import QColor, QFont
from shared.constants import C, COLUMN_LABELS, DF_COLUMNS, ZONES
from shared.scaling import S

ZONE_ROW_COLORS = {
    1: QColor(0,212,170,18), 2: QColor(61,158,255,18),
    3: QColor(251,191,36,18), 4: QColor(255,140,66,18),
    5: QColor(255,82,82,18),
}
NUMERIC_COLS = {"tco2e_par_voyage","total_tco2","nb_etudiants","zone"}

class PandasModel(QAbstractTableModel):
    COLS: list[str] = DF_COLUMNS

    def __init__(self, df: pd.DataFrame) -> None:
        super().__init__()
        self.df = df.reset_index(drop=True)
        self.font = QFont("Consolas", S.font_mono)

    def rowCount(self, parent=QModelIndex()): return len(self.df)
    def columnCount(self, parent=QModelIndex()): return len(self.COLS)

    def data(self, index, role=Qt.ItemDataRole.DisplayRole):
        if not index.isValid(): return None
        try:
            col = self.COLS[index.column()]; ri = index.row()
            if role == Qt.ItemDataRole.DisplayRole:
                if col not in self.df.columns: return ""
                val = self.df[col].iloc[ri]
                if col == "tco2e_par_voyage":
                    try: return f"{float(val):.4f}"
                    except: return str(val)
                if col == "total_tco2":
                    try: return f"{float(val):.2f}"
                    except: return str(val)
                if col == "nb_etudiants":
                    try: return f"{int(val):,}"
                    except: return str(val)
                return str(val) if val is not None else ""
            if role == Qt.ItemDataRole.BackgroundRole:
                if "zone" in self.df.columns:
                    try: return ZONE_ROW_COLORS.get(int(self.df["zone"].iloc[ri]), QColor(C["bg_elevated"]))
                    except: return QColor(C["bg_elevated"])
                return QColor(C["bg_elevated"])
            if role == Qt.ItemDataRole.ForegroundRole: return QColor(C["text_primary"])
            if role == Qt.ItemDataRole.FontRole: return self.font
            if role == Qt.ItemDataRole.TextAlignmentRole:
                if col in NUMERIC_COLS:
                    return Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter
                return Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter
        except Exception: pass
        return None

    def headerData(self, section, orientation, role=Qt.ItemDataRole.DisplayRole):
        if role != Qt.ItemDataRole.DisplayRole: return None
        try:
            if orientation == Qt.Orientation.Horizontal:
                return COLUMN_LABELS.get(self.COLS[section], self.COLS[section])
            return str(section + 1)
        except Exception: return None

    def sort(self, column, order=Qt.SortOrder.AscendingOrder):
        try:
            col = self.COLS[column]; self.beginResetModel()
            self.df = self.df.sort_values(col, ascending=(order==Qt.SortOrder.AscendingOrder)).reset_index(drop=True)
            self.endResetModel()
        except Exception:
            try: self.endResetModel()
            except: pass

    def update_df(self, df: pd.DataFrame):
        try:
            self.beginResetModel()
            self.df = df.reset_index(drop=True)
            self.font = QFont("Consolas", S.font_mono)
            self.endResetModel()
        except Exception:
            try: self.endResetModel()
            except: pass
