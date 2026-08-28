# Visionneuse autonome des logs : ouvrir un dossier de logs et parcourir les entrees

import sys
import os
import re
from datetime import datetime
from collections import Counter

from PyQt6.QtWidgets import QApplication, QMainWindow, QWidget, QHBoxLayout, QVBoxLayout, QLabel, QPushButton, QListWidget, QListWidgetItem, QScrollArea, QFileDialog, QFrame, QSizePolicy, QLineEdit, QTableWidget, QTableWidgetItem, QHeaderView, QAbstractItemView, QSplitter, QStatusBar
from PyQt6.QtCore import Qt, QSize, QTimer
from PyQt6.QtGui import QPalette, QColor, QFont, QIcon


BG      = "#0d1117"
BG_EL   = "#161b22"
BG_CARD = "#21262d"
BG_INP  = "#2d333b"
BORDER  = "#30363d"
BORDER_L= "#444c56"
TEXT    = "#e6edf3"
TEXT_S  = "#8b949e"
TEXT_M  = "#6e7681"
ACCENT  = "#58a6ff"
GREEN   = "#3fb950"
YELLOW  = "#e3b341"
RED     = "#f85149"
PURPLE  = "#bc8cff"

LOG_RE = re.compile(r"^(\d{2}:\d{2})\s*=\s*\[([^\]]+)\]\s*(.+)$")
FILE_RE = re.compile(r"^log-(\d{4}-\d{2}-\d{2})\.txt$")


def parse_log_file(filepath: str) -> list[dict]:
    entries = []
    try:
        with open(filepath, "r", encoding="utf-8") as f:
            for lineno, raw_line in enumerate(f, 1):
                line = raw_line.rstrip("\n")
                if not line.strip():
                    continue
                m = LOG_RE.match(line)
                if m:
                    entries.append({"time": m.group(1), "context": m.group(2), "message": m.group(3), "raw": line, "valid": True, "lineno": lineno})
                else:
                    entries.append({"time": "??:??", "context": "Format inconnu", "message": line, "raw": line, "valid": False, "lineno": lineno})
    except PermissionError:
        entries.append({"time": "--:--", "context": "Erreur lecture", "message": f"Accès refusé : {filepath}", "raw": "", "valid": False, "lineno": 0})
    except Exception as e:
        entries.append({"time": "--:--", "context": "Erreur lecture", "message": str(e), "raw": "", "valid": False, "lineno": 0})
    return entries


def scan_log_folder(folder: str) -> list[dict]:
    results = []
    try:
        names = sorted((f for f in os.listdir(folder) if FILE_RE.match(f)), reverse=True)
        for name in names:
            m = FILE_RE.match(name)
            date_str = m.group(1) if m else "???"
            fpath = os.path.join(folder, name)
            entries = parse_log_file(fpath)
            results.append({"name": name, "path": fpath, "date": date_str, "entries": entries, "count": len(entries), "errors": sum(1 for e in entries if not e["valid"])})
    except Exception:
        pass
    return results


QSS = f"""
QMainWindow, QWidget {{
    background: {BG};
    color: {TEXT};
    font-family: 'Segoe UI', system-ui, sans-serif;
    font-size: 13px;
}}
QScrollArea {{ background: transparent; border: none; }}
QScrollArea > QWidget > QWidget {{ background: transparent; }}
QSplitter::handle {{ background: {BORDER}; width: 1px; }}

QScrollBar:vertical {{
    background: transparent; width: 6px; margin: 0;
}}
QScrollBar::handle:vertical {{
    background: {BORDER_L}; border-radius: 3px; min-height: 24px;
}}
QScrollBar::handle:vertical:hover {{ background: {ACCENT}; }}
QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {{ height: 0; }}

QPushButton {{
    background: {BG_INP}; color: {TEXT_S};
    border: 1px solid {BORDER}; border-radius: 6px;
    padding: 5px 14px; font-size: 13px; min-height: 30px;
}}
QPushButton:hover {{
    background: {BG_CARD}; border-color: {ACCENT}; color: {TEXT};
}}
QPushButton:pressed {{ background: {BG}; }}

QLineEdit {{
    background: {BG_INP}; color: {TEXT};
    border: 1px solid {BORDER}; border-radius: 6px;
    padding: 5px 10px; font-size: 13px; min-height: 30px;
}}
QLineEdit:focus {{ border-color: {ACCENT}; }}

QListWidget {{
    background: {BG_EL}; color: {TEXT_S};
    border: none; outline: none;
    font-size: 12px;
}}
QListWidget::item {{
    padding: 8px 12px;
    border-bottom: 1px solid {BORDER};
}}
QListWidget::item:selected {{
    background: {BG_CARD}; color: {TEXT};
    border-left: 3px solid {ACCENT};
}}
QListWidget::item:hover:!selected {{
    background: {BG_CARD};
}}

QTableWidget {{
    background: {BG_EL}; color: {TEXT};
    border: none; outline: none; gridline-color: {BORDER};
    font-size: 12px; alternate-background-color: {BG_CARD};
}}
QTableWidget::item {{ padding: 4px 8px; }}
QTableWidget::item:selected {{
    background: {BG_CARD}; color: {TEXT};
}}
QHeaderView::section {{
    background: {BG_CARD}; color: {TEXT_M};
    border: none; border-bottom: 1px solid {BORDER};
    border-right: 1px solid {BORDER};
    padding: 6px 8px; font-weight: 700; font-size: 11px;
    letter-spacing: 0.4px; min-height: 28px;
}}
QHeaderView::section:hover {{ color: {TEXT}; background: {BG_INP}; }}

QStatusBar {{
    background: {BG}; color: {TEXT_M};
    border-top: 1px solid {BORDER}; font-size: 11px;
    padding: 0 12px; min-height: 22px;
}}
"""


class Badge(QLabel):
    def __init__(self, text: str, bg: str, fg: str = TEXT, parent=None):
        super().__init__(text, parent)
        self.setStyleSheet(f"background:{bg};color:{fg};border-radius:4px;padding:1px 6px;font-size:11px;font-weight:700;")
        self.setFixedHeight(20)


class HeaderBar(QWidget):
    def __init__(self, on_browse, parent=None):
        super().__init__(parent)
        self.setFixedHeight(56)
        self.setStyleSheet(f"background:{BG_EL};border-bottom:1px solid {BORDER};")
        lay = QHBoxLayout(self)
        lay.setContentsMargins(16, 0, 16, 0)
        lay.setSpacing(12)

        logo = QLabel("◎")
        logo.setStyleSheet(f"color:{ACCENT};font-size:22px;background:transparent;")
        title = QLabel("StuGo Log Viewer")
        title.setStyleSheet(f"color:{TEXT};font-size:16px;font-weight:700;background:transparent;")
        lay.addWidget(logo)
        lay.addWidget(title)
        lay.addStretch()

        self.lbl_folder = QLabel("Aucun dossier sélectionné")
        self.lbl_folder.setStyleSheet(f"color:{TEXT_M};font-size:11px;background:transparent;")
        self.lbl_folder.setMaximumWidth(380)
        lay.addWidget(self.lbl_folder)

        btn = QPushButton("📂  Ouvrir un dossier")
        btn.setFixedHeight(32)
        btn.setStyleSheet(f"QPushButton{{background:{ACCENT};color:#0d1117;border:none;border-radius:6px;padding:4px 14px;font-size:13px;font-weight:700;}}QPushButton:hover{{background:#79bcff;color:#0d1117;}}")
        btn.clicked.connect(on_browse)
        lay.addWidget(btn)

    def set_folder(self, path: str) -> None:
        self.lbl_folder.setText(path or "Aucun dossier sélectionné")


class FileListPanel(QWidget):
    def __init__(self, on_select, parent=None):
        super().__init__(parent)
        self.setFixedWidth(260)
        self.setStyleSheet(f"background:{BG_EL};border-right:1px solid {BORDER};")
        lay = QVBoxLayout(self)
        lay.setContentsMargins(0, 0, 0, 0)
        lay.setSpacing(0)

        hdr = QWidget()
        hdr.setFixedHeight(44)
        hdr.setStyleSheet(f"background:{BG_EL};border-bottom:1px solid {BORDER};")
        hl = QHBoxLayout(hdr)
        hl.setContentsMargins(12, 0, 12, 0)
        lbl = QLabel("Fichiers de log")
        lbl.setStyleSheet(f"color:{TEXT};font-size:13px;font-weight:700;background:transparent;")
        hl.addWidget(lbl)
        lay.addWidget(hdr)

        self.list_widget = QListWidget()
        self.list_widget.currentRowChanged.connect(on_select)
        lay.addWidget(self.list_widget, 1)

        self.count_lbl = QLabel("Aucun fichier")
        self.count_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.count_lbl.setFixedHeight(28)
        self.count_lbl.setStyleSheet(f"color:{TEXT_M};font-size:11px;background:{BG};border-top:1px solid {BORDER};")
        lay.addWidget(self.count_lbl)

    def populate(self, files: list[dict]) -> None:
        self.list_widget.clear()
        for f in files:
            item = QListWidgetItem()
            item.setData(Qt.ItemDataRole.UserRole, f)
            item.setSizeHint(QSize(240, 60))
            self.list_widget.addItem(item)
            w = self.make_file_widget(f)
            self.list_widget.setItemWidget(item, w)
        n = len(files)
        self.count_lbl.setText(f"{n} fichier{'s' if n != 1 else ''}" if n > 0 else "Aucun fichier")

    def make_file_widget(self, f: dict) -> QWidget:
        w = QWidget()
        w.setStyleSheet("background:transparent;")
        lay = QVBoxLayout(w)
        lay.setContentsMargins(12, 8, 12, 8)
        lay.setSpacing(3)

        top = QHBoxLayout()
        top.setSpacing(6)
        name_lbl = QLabel(f["date"])
        name_lbl.setStyleSheet(f"color:{TEXT};font-size:12px;font-weight:600;background:transparent;")
        top.addWidget(name_lbl)
        top.addStretch()
        cnt_badge = Badge(str(f["count"]), BG_INP, TEXT_S)
        top.addWidget(cnt_badge)
        lay.addLayout(top)

        sub = QLabel(f["name"])
        sub.setStyleSheet(f"color:{TEXT_M};font-size:10px;background:transparent;")
        lay.addWidget(sub)

        if f["errors"] > 0:
            err_lbl = QLabel(f"⚠ {f['errors']} ligne(s) format inconnu")
            err_lbl.setStyleSheet(f"color:{YELLOW};font-size:10px;background:transparent;")
            lay.addWidget(err_lbl)
        return w


class EntryTable(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        lay = QVBoxLayout(self)
        lay.setContentsMargins(0, 0, 0, 0)
        lay.setSpacing(0)

        toolbar = QWidget()
        toolbar.setFixedHeight(46)
        toolbar.setStyleSheet(f"background:{BG_EL};border-bottom:1px solid {BORDER};")
        tl = QHBoxLayout(toolbar)
        tl.setContentsMargins(12, 6, 12, 6)
        tl.setSpacing(10)

        self.file_lbl = QLabel("Aucun fichier sélectionné")
        self.file_lbl.setStyleSheet(f"color:{TEXT};font-size:13px;font-weight:600;background:transparent;")
        tl.addWidget(self.file_lbl, 1)

        self.search = QLineEdit()
        self.search.setPlaceholderText("🔍 Filtrer les entrées…")
        self.search.setFixedWidth(220)
        self.search.textChanged.connect(self.apply_filter)
        tl.addWidget(self.search)

        btn_clear = QPushButton("✕")
        btn_clear.setFixedSize(28, 28)
        btn_clear.setToolTip("Effacer le filtre")
        btn_clear.clicked.connect(lambda: self.search.clear())
        tl.addWidget(btn_clear)
        lay.addWidget(toolbar)

        self.stats_bar = QWidget()
        self.stats_bar.setFixedHeight(34)
        self.stats_bar.setStyleSheet(f"background:{BG_CARD};border-bottom:1px solid {BORDER};")
        sl = QHBoxLayout(self.stats_bar)
        sl.setContentsMargins(12, 0, 12, 0)
        sl.setSpacing(12)
        self.stats_lbl = QLabel("")
        self.stats_lbl.setStyleSheet(f"color:{TEXT_M};font-size:11px;background:transparent;")
        sl.addWidget(self.stats_lbl)
        sl.addStretch()
        lay.addWidget(self.stats_bar)

        self.table = QTableWidget()
        self.table.setColumnCount(3)
        self.table.setHorizontalHeaderLabels(["Heure", "Contexte", "Message"])
        self.table.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self.table.setAlternatingRowColors(True)
        self.table.setShowGrid(True)
        self.table.setSortingEnabled(False)
        self.table.verticalHeader().setVisible(False)
        self.table.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeMode.ResizeToContents)
        self.table.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeMode.ResizeToContents)
        self.table.horizontalHeader().setSectionResizeMode(2, QHeaderView.ResizeMode.Stretch)
        self.table.verticalHeader().setDefaultSectionSize(28)
        self.table.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        lay.addWidget(self.table, 1)

        self.placeholder = QLabel("Sélectionnez un fichier de log dans le panneau de gauche")
        self.placeholder.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.placeholder.setStyleSheet(f"color:{TEXT_M};font-size:14px;background:transparent;")
        lay.addWidget(self.placeholder)
        self.table.hide()
        self.stats_bar.hide()

        self.all_entries: list[dict] = []

    def show_file(self, file_info: dict) -> None:
        self.all_entries = file_info["entries"]
        self.file_lbl.setText(file_info["name"])
        self.search.clear()
        self.render(self.all_entries)
        self.placeholder.hide()
        self.table.show()
        self.stats_bar.show()

    def clear(self) -> None:
        self.table.setRowCount(0)
        self.file_lbl.setText("Aucun fichier sélectionné")
        self.stats_lbl.setText("")
        self.table.hide()
        self.stats_bar.hide()
        self.placeholder.show()
        self.all_entries = []

    def apply_filter(self, text: str) -> None:
        if not text.strip():
            self.render(self.all_entries)
            return
        txt = text.lower()
        filtered = [e for e in self.all_entries if txt in e["context"].lower() or txt in e["message"].lower()]
        self.render(filtered)

    def render(self, entries: list[dict]) -> None:
        self.table.setRowCount(0)
        self.table.setSortingEnabled(False)
        mono = QFont("Consolas", 10)

        for row_idx, e in enumerate(entries):
            self.table.insertRow(row_idx)

            t_item = QTableWidgetItem(e["time"])
            t_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter | Qt.AlignmentFlag.AlignVCenter)
            t_item.setFont(mono)
            t_item.setForeground(QColor(ACCENT if e["valid"] else YELLOW))

            ctx_item = QTableWidgetItem(e["context"])
            ctx_item.setTextAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter)
            ctx_item.setFont(mono)
            ctx_color = context_color(e["context"], e["valid"])
            ctx_item.setForeground(QColor(ctx_color))

            msg_item = QTableWidgetItem(e["message"])
            msg_item.setTextAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter)
            msg_item.setToolTip(e["raw"])

            if not e["valid"]:
                for item in (t_item, ctx_item, msg_item):
                    item.setForeground(QColor(YELLOW))
                    item.setBackground(QColor(30, 20, 5, 60))

            self.table.setItem(row_idx, 0, t_item)
            self.table.setItem(row_idx, 1, ctx_item)
            self.table.setItem(row_idx, 2, msg_item)

        total  = len(entries)
        valid  = sum(1 for e in entries if e["valid"])
        bad    = total - valid
        ctx_counter = Counter(e["context"] for e in entries if e["valid"])
        top_ctx = f"  •  Contexte principal : {ctx_counter.most_common(1)[0][0]}" if ctx_counter else ""
        parts = [f"{total} entrée(s)"]
        if bad:
            parts.append(f"⚠ {bad} format inconnu")
        self.stats_lbl.setText("  ".join(parts) + top_ctx)


def context_color(ctx: str, valid: bool) -> str:
    if not valid:
        return YELLOW
    low = ctx.lower()
    if any(k in low for k in ("error", "erreur", "fail")):
        return RED
    if any(k in low for k in ("renderer", "render", "chart")):
        return PURPLE
    if any(k in low for k in ("theme", "preset", "style")):
        return "#ffa657"
    if any(k in low for k in ("session", "prefs", "repo")):
        return GREEN
    if any(k in low for k in ("extractor", "excel", "import")):
        return "#79c0ff"
    return TEXT_S


class LogViewerWindow(QMainWindow):

    def __init__(self):
        super().__init__()
        self.setWindowTitle("StuGo Log Viewer")
        self.resize(1100, 680)
        self.setMinimumSize(800, 500)
        self.folder: str = ""
        self.files: list[dict] = []
        self.build_ui()
        self.try_default_folder()

    def build_ui(self) -> None:
        self.setStatusBar(QStatusBar())

        central = QWidget()
        self.setCentralWidget(central)
        root = QVBoxLayout(central)
        root.setContentsMargins(0, 0, 0, 0)
        root.setSpacing(0)

        self.header = HeaderBar(on_browse=self.browse)
        root.addWidget(self.header)

        splitter = QSplitter(Qt.Orientation.Horizontal)
        splitter.setHandleWidth(1)
        splitter.setChildrenCollapsible(False)

        self.file_panel  = FileListPanel(on_select=self.on_file_selected)
        self.entry_panel = EntryTable()

        splitter.addWidget(self.file_panel)
        splitter.addWidget(self.entry_panel)
        splitter.setSizes([260, 840])
        splitter.setStretchFactor(0, 0)
        splitter.setStretchFactor(1, 1)
        root.addWidget(splitter, 1)

        self.statusBar().showMessage("  Ouvrez un dossier de logs pour commencer.")

    def try_default_folder(self) -> None:
        here = os.path.dirname(os.path.abspath(__file__))
        default = os.path.join(here, "logs")
        if os.path.isdir(default):
            self.load_folder(default)

    def browse(self) -> None:
        start = self.folder or os.path.dirname(os.path.abspath(__file__))
        folder = QFileDialog.getExistingDirectory(self, "Sélectionner le dossier de logs", start)
        if folder:
            self.load_folder(folder)

    def load_folder(self, folder: str) -> None:
        self.folder = folder
        self.header.set_folder(folder)
        self.files = scan_log_folder(folder)
        self.file_panel.populate(self.files)
        self.entry_panel.clear()

        n = len(self.files)
        if n == 0:
            self.statusBar().showMessage(f"  Aucun fichier log-YYYY-MM-DD.txt trouvé dans {folder}")
        else:
            total_entries = sum(f["count"] for f in self.files)
            self.statusBar().showMessage(f"  {n} fichier(s) chargé(s)  —  {total_entries} entrée(s) au total  —  {folder}")
            if self.file_panel.list_widget.count() > 0:
                self.file_panel.list_widget.setCurrentRow(0)

    def on_file_selected(self, row: int) -> None:
        if row < 0 or row >= len(self.files):
            self.entry_panel.clear()
            return
        f = self.files[row]
        self.entry_panel.show_file(f)
        self.statusBar().showMessage(f"  {f['name']}  —  {f['count']} entrée(s)" + (f"  —  ⚠ {f['errors']} format inconnu" if f["errors"] else ""))


def apply_palette(app: QApplication) -> None:
    p = QPalette()
    m = [
        (QPalette.ColorRole.Window,          BG),
        (QPalette.ColorRole.WindowText,      TEXT),
        (QPalette.ColorRole.Base,            BG_EL),
        (QPalette.ColorRole.AlternateBase,   BG_CARD),
        (QPalette.ColorRole.Highlight,       ACCENT),
        (QPalette.ColorRole.HighlightedText, BG),
        (QPalette.ColorRole.Text,            TEXT),
        (QPalette.ColorRole.ButtonText,      TEXT),
        (QPalette.ColorRole.Button,          BG_INP),
        (QPalette.ColorRole.ToolTipBase,     BG_EL),
        (QPalette.ColorRole.ToolTipText,     TEXT),
    ]
    for role, color in m:
        p.setColor(role, QColor(color))
    app.setPalette(p)


if __name__ == "__main__":
    import warnings
    warnings.filterwarnings("ignore")

    app = QApplication(sys.argv)
    app.setStyle("Fusion")
    app.setApplicationName("StuGo Log Viewer")
    apply_palette(app)
    app.setStyleSheet(QSS)

    win = LogViewerWindow()
    win.show()
    sys.exit(app.exec())
