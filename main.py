# Point d'entree du programme : demarre l'application et affiche la fenetre principale

import sys
import os
import warnings
warnings.filterwarnings("ignore")

if getattr(sys, "frozen", False):
    plugin_dir = os.path.join(os.path.dirname(sys.executable), "_internal", "PyQt6", "Qt6", "plugins")
    if os.path.isdir(plugin_dir):
        os.environ.setdefault("QT_PLUGIN_PATH", plugin_dir)

import matplotlib
matplotlib.use("QtAgg")

from PyQt6.QtWidgets import QApplication, QMessageBox
from PyQt6.QtCore import QTimer
from PyQt6.QtGui import QIcon

from shared.constants import C
from shared.scaling import S


def main() -> None:
    app = QApplication(sys.argv)
    app.setStyle("Fusion")

    import os
    icon_path = os.path.join(getattr(sys, '_MEIPASS', os.path.dirname(os.path.abspath(__file__))), 'assets', 'logo.ico')
    if os.path.exists(icon_path):
        app.setWindowIcon(QIcon(icon_path))

    from app.bootstrap import bootstrap
    bootstrap(app)

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
        QMessageBox.critical(None, "Erreur critique", f"Impossible de démarrer StuGo CO2 Explorer :\n\n{e}")
        sys.exit(1)

    if splash:
        QTimer.singleShot(450, lambda: splash.finish(win))
    else:
        win.show()

    sys.exit(app.exec())


if __name__ == "__main__":
    main()
