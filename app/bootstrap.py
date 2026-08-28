# Demarre l'application : cree la fenetre Qt, applique le theme et lance la boucle principale

import sys
import warnings
warnings.filterwarnings("ignore")
import matplotlib
matplotlib.use("QtAgg")
from PyQt6.QtWidgets import QApplication, QMessageBox
from PyQt6.QtGui import QPalette, QColor
from PyQt6.QtCore import QTimer
from shared.constants import C
from shared.scaling import S


def apply_palette(app) -> None:
    p = QPalette()
    map = [
        (QPalette.ColorRole.Window,          "bg_base"),
        (QPalette.ColorRole.WindowText,      "text_primary"),
        (QPalette.ColorRole.Base,            "bg_elevated"),
        (QPalette.ColorRole.AlternateBase,   "bg_card"),
        (QPalette.ColorRole.Highlight,       "accent_dim"),
        (QPalette.ColorRole.HighlightedText, "text_primary"),
        (QPalette.ColorRole.Text,            "text_primary"),
        (QPalette.ColorRole.ButtonText,      "text_primary"),
        (QPalette.ColorRole.Button,          "bg_input"),
        (QPalette.ColorRole.ToolTipBase,     "bg_elevated"),
        (QPalette.ColorRole.ToolTipText,     "text_primary"),
    ]
    for role, key in map:
        p.setColor(role, QColor(C[key]))
    app.setPalette(p)


def bootstrap(app) -> None:
    S.init(app)
    from presentation.theme.theme_manager import ThemeManager
    ThemeManager.instance()
    from presentation.theme.stylesheet_builder import StylesheetBuilder
    apply_palette(app)
    app.setStyleSheet(StylesheetBuilder.build())
    ThemeManager.instance().theme_changed.connect(lambda: apply_palette(app))
    ThemeManager.instance().theme_changed.connect(lambda: app.setStyleSheet(StylesheetBuilder.build()))


def run() -> None:
    app = QApplication(sys.argv)
    app.setStyle("Fusion")
    S.init(app)
    from presentation.theme.theme_manager import ThemeManager
    ThemeManager.instance()
    from presentation.theme.stylesheet_builder import StylesheetBuilder
    apply_palette(app)
    app.setStyleSheet(StylesheetBuilder.build())
    ThemeManager.instance().theme_changed.connect(lambda: apply_palette(app))
    ThemeManager.instance().theme_changed.connect(lambda: app.setStyleSheet(StylesheetBuilder.build()))
    try:
        from presentation.splash_screen import SplashScreen
        splash = SplashScreen()
        splash.show()
        app.processEvents()
    except Exception:
        splash = None
    try:
        from presentation.main_window import MainWindow
        win = MainWindow(app)
    except Exception as e:
        QMessageBox.critical(None, "Erreur critique", f"Impossible de demarrer:\n{e}")
        sys.exit(1)
    if splash:
        QTimer.singleShot(450, lambda: splash.finish(win))
    else:
        win.show()
    sys.exit(app.exec())
