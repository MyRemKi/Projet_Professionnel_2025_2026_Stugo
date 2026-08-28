# Petit outil separe pour parcourir et filtrer les fichiers de logs de l'application

import sys
import re
from pathlib import Path

from PyQt6.QtCore import Qt, QAbstractTableModel, QSortFilterProxyModel
from PyQt6.QtWidgets import QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QFileDialog, QLabel, QLineEdit, QComboBox, QTableView, QTextEdit, QTabWidget, QSplitter, QHeaderView, QDialog, QButtonGroup, QRadioButton, QDialogButtonBox, QMessageBox, QGroupBox, QFrame
from PyQt6.QtGui import QColor, QFont

FILE_PATTERN = re.compile(r"^log-(\d{4})-(\d{2})-(\d{2})\.txt$")
LOG_PATTERN  = re.compile(r"^(?P<heure>([01]\d|2[0-3]):[0-5]\d)\s=\s\[(?P<module>[^\]]+)\]\s(?P<message>.+)$")

EXPECTED_FILE_FORMAT = "log-AAAA-MM-JJ.txt  (ex: log-2024-03-15.txt)"
EXPECTED_LINE_FORMAT = "HH:MM = [MODULE] message  (ex: 14:32 = [AUTH] Connexion réussie)"

THEMES = {
    "Bleu nuit": {
        "bg": "#141926", "bg2": "#1e2433", "bg3": "#111828",
        "accent": "#3b6fd4", "sel": "#2e4a8a",
        "text": "#d0d8f0", "text2": "#e8eeff", "muted": "#8899cc",
        "border": "#2a3455", "tab_bg": "#1a2238", "tab_sel": "#232f4a",
        "row_a": "#1e2433", "row_b": "#232b3e",
    },
    "Vert forêt": {
        "bg": "#111a12", "bg2": "#172619", "bg3": "#0d160e",
        "accent": "#2e8b3a", "sel": "#1a5c24",
        "text": "#cff0d2", "text2": "#e6ffe8", "muted": "#7aaa80",
        "border": "#235528", "tab_bg": "#162219", "tab_sel": "#1e3020",
        "row_a": "#172619", "row_b": "#1c2e1e",
    },
    "Violet nuit": {
        "bg": "#16101f", "bg2": "#221630", "bg3": "#100b18",
        "accent": "#7c3fd4", "sel": "#4e218a",
        "text": "#e0d0f5", "text2": "#ede8ff", "muted": "#9980cc",
        "border": "#3a2558", "tab_bg": "#1c1230", "tab_sel": "#281a42",
        "row_a": "#1a1128", "row_b": "#201430",
    },
    "Rouge sombre": {
        "bg": "#1a1010", "bg2": "#271818", "bg3": "#120b0b",
        "accent": "#c0392b", "sel": "#7b1c12",
        "text": "#f0d0cc", "text2": "#ffe8e4", "muted": "#cc8880",
        "border": "#4a2220", "tab_bg": "#201212", "tab_sel": "#2c1818",
        "row_a": "#1e1212", "row_b": "#241616",
    },
    "Clair": {
        "bg": "#f0f2f7", "bg2": "#ffffff", "bg3": "#e4e8f0",
        "accent": "#1a5fd4", "sel": "#aac4f0",
        "text": "#1a2040", "text2": "#0a1020", "muted": "#556688",
        "border": "#c0cce0", "tab_bg": "#dde4f0", "tab_sel": "#ffffff",
        "row_a": "#f7f9fd", "row_b": "#edf0fa",
    },
}

MODULE_COLORS_DARK  = {"ERROR": "#ef9a9a", "WARNING": "#ffe082", "INFO": "#a5d6a7", "DEBUG": "#ce93d8", "AUTH": "#4fc3f7"}
MODULE_COLORS_LIGHT = {"ERROR": "#b71c1c", "WARNING": "#e65100", "INFO": "#1b5e20", "DEBUG": "#6a1b9a", "AUTH": "#0d47a1"}

active_theme_name = "Bleu nuit"

def current_theme():
    return THEMES[active_theme_name]


# Modele Qt pour la table de logs (colonnes Date, Heure, Module, Message)
class LogTableModel(QAbstractTableModel):
    headers = ["Date", "Heure", "Module", "Message"]

    def __init__(self):
        super().__init__()
        self.logs = []
        self.light_mode = False

    def rowCount(self, parent=None):
        return len(self.logs)

    def columnCount(self, parent=None):
        return 4

    def data(self, index, role):
        if not index.isValid():
            return None
        log = self.logs[index.row()]

        if role == Qt.ItemDataRole.DisplayRole:
            return [log["date"], log["heure"], log["module"], log["message"]][index.column()]

        palette = MODULE_COLORS_LIGHT if self.light_mode else MODULE_COLORS_DARK
        if role == Qt.ItemDataRole.ForegroundRole:
            module = log["module"].upper()
            for key, color in palette.items():
                if key in module:
                    return QColor(color)
            return QColor("#333333") if self.light_mode else QColor("#e0e0e0")

        if role == Qt.ItemDataRole.BackgroundRole:
            t = current_theme()
            return QColor(t["row_a"]) if index.row() % 2 == 0 else QColor(t["row_b"])

        return None

    def headerData(self, section, orientation, role):
        if role == Qt.ItemDataRole.DisplayRole and orientation == Qt.Orientation.Horizontal:
            return self.headers[section]

    def set_logs(self, logs):
        self.beginResetModel()
        self.logs = logs
        self.endResetModel()


# Filtre la table de logs par module, date et mot-cle
class LogFilterProxy(QSortFilterProxyModel):
    def __init__(self):
        super().__init__()
        self.search = ""
        self.module = "Tous"
        self.date   = "Toutes"

    def filterAcceptsRow(self, row, parent):
        model = self.sourceModel()
        log = model.logs[row]
        if self.module != "Tous" and log["module"] != self.module:
            return False
        if self.date != "Toutes" and log["date"] != self.date:
            return False
        text = f'{log["date"]} {log["heure"]} {log["module"]} {log["message"]}'.lower()
        return self.search in text


# Fenetre de choix du theme de couleur, avec un apercu pour chaque theme
class ThemeDialog(QDialog):
    def __init__(self, current_theme_name, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Paramètres — Thème de couleur")
        self.setFixedSize(420, 340)
        self.selected = current_theme_name

        layout = QVBoxLayout(self)
        layout.setSpacing(12)

        title = QLabel("Choisir un thème d'interface :")
        title.setStyleSheet("font-weight: bold; font-size: 11pt;")
        layout.addWidget(title)

        group = QGroupBox()
        group.setFlat(True)
        group_layout = QVBoxLayout(group)
        group_layout.setSpacing(6)

        self.buttons = QButtonGroup(self)

        for name, t in THEMES.items():
            row = QHBoxLayout()
            radio = QRadioButton(name)
            radio.setChecked(name == current_theme_name)
            self.buttons.addButton(radio)
            radio.toggled.connect(lambda checked, n=name: self.on_select(checked, n))

            swatch = QWidget()
            swatch.setFixedSize(110, 20)
            sw_layout = QHBoxLayout(swatch)
            sw_layout.setContentsMargins(0, 0, 0, 0)
            sw_layout.setSpacing(3)
            for color in [t["bg"], t["bg2"], t["accent"], t["text"]]:
                dot = QFrame()
                dot.setFixedSize(18, 18)
                dot.setStyleSheet(f"background:{color}; border-radius:9px; border:1px solid #00000033;")
                sw_layout.addWidget(dot)

            row.addWidget(radio)
            row.addStretch()
            row.addWidget(swatch)
            group_layout.addLayout(row)

        layout.addWidget(group)
        layout.addStretch()

        btns = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel)
        btns.accepted.connect(self.accept)
        btns.rejected.connect(self.reject)
        layout.addWidget(btns)

    def on_select(self, checked, name):
        if checked:
            self.selected = name

    def chosen_theme(self):
        return self.selected


# Fenetre principale : barre de filtres, tableau des logs, panneau de details
class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.logs    = []
        self.invalid = []

        self.setWindowTitle("Analyseur de Logs Admin")
        self.resize(1400, 900)
        self.setMinimumSize(900, 600)

        self.model = LogTableModel()
        self.proxy = LogFilterProxy()
        self.proxy.setSourceModel(self.model)

        self.build_ui()
        self.apply_theme()

    def build_ui(self):
        central = QWidget()
        self.setCentralWidget(central)

        layout = QVBoxLayout(central)
        layout.setContentsMargins(12, 12, 12, 12)
        layout.setSpacing(8)

        top = QHBoxLayout()
        top.setSpacing(10)

        self.btn_load = QPushButton("  Choisir dossier")
        self.btn_load.setFixedHeight(36)
        self.btn_load.clicked.connect(self.load_folder)

        self.btn_settings = QPushButton("  Paramètres")
        self.btn_settings.setObjectName("btn_settings")
        self.btn_settings.setFixedHeight(36)
        self.btn_settings.clicked.connect(self.open_theme_dialog)

        self.stats = QLabel("Aucun log chargé")
        self.stats.setObjectName("stats")

        top.addWidget(self.btn_load)
        top.addWidget(self.btn_settings)
        top.addSpacing(10)
        top.addWidget(self.stats)
        top.addStretch()
        layout.addLayout(top)

        filters = QHBoxLayout()
        filters.setSpacing(8)

        lbl_search = QLabel("Recherche :")
        lbl_search.setObjectName("filter_label")
        self.search = QLineEdit()
        self.search.setPlaceholderText("Mot-clé, module, message...")
        self.search.setFixedHeight(32)
        self.search.textChanged.connect(self.apply_filters)

        lbl_module = QLabel("Module :")
        lbl_module.setObjectName("filter_label")
        self.module = QComboBox()
        self.module.setFixedHeight(32)
        self.module.setMinimumWidth(140)
        self.module.currentTextChanged.connect(self.apply_filters)

        lbl_date = QLabel("Date :")
        lbl_date.setObjectName("filter_label")
        self.date = QComboBox()
        self.date.setFixedHeight(32)
        self.date.setMinimumWidth(130)
        self.date.currentTextChanged.connect(self.apply_filters)

        filters.addWidget(lbl_search)
        filters.addWidget(self.search, 2)
        filters.addWidget(lbl_module)
        filters.addWidget(self.module)
        filters.addWidget(lbl_date)
        filters.addWidget(self.date)
        layout.addLayout(filters)

        self.tabs = QTabWidget()

        logs_widget = QWidget()
        logs_layout = QVBoxLayout(logs_widget)
        logs_layout.setContentsMargins(0, 6, 0, 0)
        logs_layout.setSpacing(0)

        self.table = QTableView()
        self.table.setModel(self.proxy)
        self.table.setSortingEnabled(True)
        self.table.clicked.connect(self.show_details)
        self.table.setSelectionBehavior(QTableView.SelectionBehavior.SelectRows)
        self.table.setAlternatingRowColors(False)
        self.table.verticalHeader().setVisible(False)
        self.table.horizontalHeader().setStretchLastSection(True)
        self.table.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeMode.ResizeToContents)
        self.table.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeMode.ResizeToContents)
        self.table.horizontalHeader().setSectionResizeMode(2, QHeaderView.ResizeMode.ResizeToContents)
        self.table.setShowGrid(False)

        self.details = QTextEdit()
        self.details.setReadOnly(True)
        self.details.setPlaceholderText("Cliquer sur une ligne pour afficher les détails...")
        self.details.setFixedHeight(130)

        splitter = QSplitter(Qt.Orientation.Vertical)
        splitter.addWidget(self.table)
        splitter.addWidget(self.details)
        splitter.setStretchFactor(0, 4)
        splitter.setStretchFactor(1, 1)
        logs_layout.addWidget(splitter)

        invalid_widget = QWidget()
        invalid_layout = QVBoxLayout(invalid_widget)
        invalid_layout.setContentsMargins(6, 6, 6, 6)
        invalid_layout.setSpacing(8)

        self.fmt_box = QFrame()
        self.fmt_box.setObjectName("fmt_box")
        fmt_inner = QVBoxLayout(self.fmt_box)
        fmt_inner.setContentsMargins(12, 8, 12, 8)
        fmt_inner.setSpacing(4)

        fmt_title = QLabel("Format attendu par le programme")
        fmt_title.setObjectName("fmt_title")
        fmt_file  = QLabel(f"  Nom de fichier :  {EXPECTED_FILE_FORMAT}")
        fmt_file.setObjectName("fmt_detail")
        fmt_line  = QLabel(f"  Ligne de log     :  {EXPECTED_LINE_FORMAT}")
        fmt_line.setObjectName("fmt_detail")
        fmt_note  = QLabel("  Les lignes ne respectant pas ce format sont listées ci-dessous.")
        fmt_note.setObjectName("fmt_note")
        fmt_note.setWordWrap(True)

        fmt_inner.addWidget(fmt_title)
        fmt_inner.addWidget(fmt_file)
        fmt_inner.addWidget(fmt_line)
        fmt_inner.addWidget(fmt_note)

        self.invalid_view = QTextEdit()
        self.invalid_view.setReadOnly(True)
        self.invalid_view.setPlaceholderText("Aucune ligne invalide détectée.")

        invalid_layout.addWidget(self.fmt_box)
        invalid_layout.addWidget(self.invalid_view)

        self.tabs.addTab(logs_widget,     "  Logs  ")
        self.tabs.addTab(invalid_widget,  "  Lignes invalides  ")
        layout.addWidget(self.tabs)

    def load_folder(self):
        folder = QFileDialog.getExistingDirectory(self, "Dossier de logs")
        if not folder:
            return

        self.logs.clear()
        self.invalid.clear()
        file_count   = 0
        skipped_files = []

        for file in Path(folder).iterdir():
            try:
                if not file.is_file():
                    continue
                if not FILE_PATTERN.match(file.name):
                    skipped_files.append(file.name)
                    continue

                file_count += 1
                date = file.stem.replace("log-", "")

                try:
                    with open(file, "r", encoding="utf-8") as f:
                        for line_no, line in enumerate(f, start=1):
                            line = line.strip()
                            if not line:
                                continue
                            match = LOG_PATTERN.match(line)
                            if not match:
                                self.invalid.append(f"[{file.name}  ligne {line_no}]  {line}\n    → Format attendu : {EXPECTED_LINE_FORMAT}")
                            else:
                                self.logs.append({"date": date, "heure": match.group("heure"), "module": match.group("module"), "message": match.group("message")})

                except UnicodeDecodeError as e:
                    self.invalid.append(f"[{file.name}]  ERREUR encodage : {e}\n    → Le fichier doit être encodé en UTF-8.")
                except PermissionError:
                    self.invalid.append(f"[{file.name}]  ERREUR permission : accès refusé.")
                except FileNotFoundError:
                    self.invalid.append(f"[{file.name}]  ERREUR : fichier introuvable.")

            except Exception as e:
                self.invalid.append(f"[{file.name}]  EXCEPTION inattendue : {e}")

        if file_count == 0:
            msg = QMessageBox(self)
            msg.setWindowTitle("Aucun fichier reconnu")
            msg.setIcon(QMessageBox.Icon.Warning)
            msg.setText("<b>Aucun fichier de log valide trouvé dans ce dossier.</b>")
            msg.setInformativeText(f"Le programme attend des fichiers nommés :\n\n    {EXPECTED_FILE_FORMAT}\n\nEt dont chaque ligne respecte :\n\n    {EXPECTED_LINE_FORMAT}\n\nFichiers ignorés : " + (", ".join(skipped_files[:8]) + ("…" if len(skipped_files) > 8 else "") if skipped_files else "(dossier vide)"))
            msg.exec()
            self.stats.setText("Aucun log chargé — dossier invalide")
            return

        self.model.set_logs(self.logs)

        self.module.blockSignals(True)
        self.date.blockSignals(True)
        self.module.clear()
        self.date.clear()
        self.module.addItem("Tous")
        self.date.addItem("Toutes")
        self.module.addItems(sorted(set(x["module"] for x in self.logs)))
        self.date.addItems(sorted(set(x["date"] for x in self.logs)))
        self.module.blockSignals(False)
        self.date.blockSignals(False)

        self.invalid_view.setPlainText("\n\n".join(self.invalid) if self.invalid else "")
        self.stats.setText(f"Fichiers : {file_count}  |  Logs : {len(self.logs)}" + (f"  |  Invalides : {len(self.invalid)}" if self.invalid else "  |  Aucune erreur"))
        self.apply_filters()

    def apply_filters(self):
        self.proxy.search = self.search.text().lower()
        self.proxy.module = self.module.currentText() or "Tous"
        self.proxy.date   = self.date.currentText() or "Toutes"
        self.proxy.invalidateFilter()

    def show_details(self, index):
        try:
            source = self.proxy.mapToSource(index)
            log = self.model.logs[source.row()]
            t   = current_theme()
            self.details.setHtml(f'<span style="color:{t["muted"]}">Date&nbsp;&nbsp;&nbsp;:</span> <span style="color:{t["accent"]}">{log["date"]}</span>&nbsp;&nbsp;&nbsp;&nbsp;<span style="color:{t["muted"]}">Heure&nbsp;&nbsp;:</span> <span style="color:{t["accent"]}">{log["heure"]}</span>&nbsp;&nbsp;&nbsp;&nbsp;<span style="color:{t["muted"]}">Module&nbsp;:</span> <span style="color:#ffe082;font-weight:bold">{log["module"]}</span><br><br><span style="color:{t["text"]}">{log["message"]}</span>')
        except Exception:
            pass

    def open_theme_dialog(self):
        global active_theme_name
        dlg = ThemeDialog(active_theme_name, self)
        t   = current_theme()
        dlg.setStyleSheet(f"QDialog {{ background:{t['bg']}; color:{t['text']}; }}QLabel {{ color:{t['text']}; }}QGroupBox {{ border:none; }}QRadioButton {{ color:{t['text']}; font-size:10pt; }}QDialogButtonBox QPushButton {{  background:{t['accent']}; color:#fff; border:none;  border-radius:5px; padding:6px 18px; font-weight:bold; }}QDialogButtonBox QPushButton:hover {{ background:{t['sel']}; }}")
        if dlg.exec() == QDialog.DialogCode.Accepted:
            chosen = dlg.chosen_theme()
            if chosen != active_theme_name:
                active_theme_name         = chosen
                self.model.light_mode      = (chosen == "Clair")
                self.model.layoutChanged.emit()
                self.apply_theme()

    def apply_theme(self):
        t        = current_theme()
        is_light = (active_theme_name == "Clair")
        btn_text = t["text"] if is_light else "#c0d0ff"

        self.setStyleSheet(f"""
        QWidget {{
            background: {t['bg']};
            color: {t['text']};
            font-size: 10pt;
            font-family: "Segoe UI", "Arial", sans-serif;
        }}
        QMainWindow {{ background: {t['bg']}; }}

        QPushButton {{
            background: {t['accent']}; color: #ffffff;
            border: none; border-radius: 6px;
            padding: 6px 18px; font-weight: bold; font-size: 10pt;
        }}
        QPushButton:hover   {{ background: {t['sel']}; }}
        QPushButton:pressed {{ background: {t['bg3']}; }}

        QPushButton#btn_settings {{
            background: {t['bg2']}; color: {btn_text};
            border: 1px solid {t['border']};
        }}
        QPushButton#btn_settings:hover {{
            background: {t['tab_bg']}; border-color: {t['accent']};
        }}

        QLabel#filter_label {{ color: {t['muted']}; font-size: 9pt; }}
        QLabel#stats        {{ color: {t['accent']}; font-size: 9pt; font-style: italic; }}

        QFrame#fmt_box {{
            background: {t['bg3']};
            border: 1px solid {t['border']};
            border-left: 4px solid {t['accent']};
            border-radius: 6px;
        }}
        QLabel#fmt_title  {{ color: {t['accent']}; font-weight: bold; font-size: 9.5pt; }}
        QLabel#fmt_detail {{
            color: {t['text2']};
            font-family: "Consolas","Courier New",monospace; font-size: 9pt;
        }}
        QLabel#fmt_note {{ color: {t['muted']}; font-size: 8.5pt; font-style: italic; }}

        QLineEdit {{
            background: {t['bg2']}; color: {t['text2']};
            border: 1px solid {t['border']}; border-radius: 5px; padding: 4px 8px;
            selection-background-color: {t['accent']}; selection-color: #ffffff;
        }}
        QLineEdit:focus {{ border: 1px solid {t['accent']}; }}

        QComboBox {{
            background: {t['bg2']}; color: {t['text2']};
            border: 1px solid {t['border']}; border-radius: 5px; padding: 4px 8px;
        }}
        QComboBox:focus {{ border: 1px solid {t['accent']}; }}
        QComboBox::drop-down {{ border: none; width: 22px; }}
        QComboBox QAbstractItemView {{
            background: {t['bg2']}; color: {t['text2']};
            border: 1px solid {t['border']};
            selection-background-color: {t['accent']}; selection-color: #ffffff;
            outline: none;
        }}

        QTableView {{
            background: {t['bg2']}; color: {t['text']};
            border: 1px solid {t['border']}; border-radius: 6px;
            gridline-color: transparent;
            selection-background-color: {t['sel']}; selection-color: {t['text2']};
        }}
        QTableView:focus {{ outline: none; }}

        QHeaderView::section {{
            background: {t['bg3']}; color: {t['accent']};
            font-weight: bold; font-size: 9.5pt;
            padding: 7px 10px; border: none;
            border-bottom: 2px solid {t['border']};
        }}

        QTabWidget::pane {{
            border: 1px solid {t['border']}; border-radius: 6px;
            background: {t['bg']};
        }}
        QTabBar::tab {{
            background: {t['tab_bg']}; color: {t['muted']};
            border: 1px solid {t['border']}; border-bottom: none;
            border-radius: 5px 5px 0 0; padding: 7px 16px;
            margin-right: 2px; font-size: 9.5pt;
        }}
        QTabBar::tab:selected {{
            background: {t['tab_sel']}; color: {t['text2']};
            border-color: {t['accent']}; font-weight: bold;
        }}
        QTabBar::tab:hover:!selected {{ background: {t['bg2']}; color: {t['text']}; }}

        QTextEdit {{
            background: {t['bg3']}; color: {t['text']};
            border: 1px solid {t['border']}; border-radius: 5px; padding: 6px;
            font-family: "Consolas","Courier New",monospace; font-size: 9.5pt;
            selection-background-color: {t['accent']}; selection-color: #ffffff;
        }}

        QScrollBar:vertical {{ background: {t['bg']}; width: 10px; border-radius: 5px; }}
        QScrollBar::handle:vertical {{
            background: {t['border']}; border-radius: 5px; min-height: 24px;
        }}
        QScrollBar::handle:vertical:hover {{ background: {t['accent']}; }}
        QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {{ height: 0; }}

        QScrollBar:horizontal {{ background: {t['bg']}; height: 10px; border-radius: 5px; }}
        QScrollBar::handle:horizontal {{
            background: {t['border']}; border-radius: 5px; min-width: 24px;
        }}
        QScrollBar::handle:horizontal:hover {{ background: {t['accent']}; }}
        QScrollBar::add-line:horizontal, QScrollBar::sub-line:horizontal {{ width: 0; }}

        QSplitter::handle {{ background: {t['border']}; height: 4px; }}
        QSplitter::handle:hover {{ background: {t['accent']}; }}

        QMessageBox {{ background: {t['bg']}; color: {t['text']}; }}
        QMessageBox QLabel {{ color: {t['text']}; }}
        QMessageBox QPushButton {{
            background: {t['accent']}; color: #fff; border: none;
            border-radius: 5px; padding: 6px 20px; min-width: 80px;
        }}
        QMessageBox QPushButton:hover {{ background: {t['sel']}; }}
        """)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    w = MainWindow()
    w.show()
    sys.exit(app.exec())
