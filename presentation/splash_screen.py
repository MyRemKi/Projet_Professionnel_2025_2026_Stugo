# Ecran affiche au demarrage de l'application (logo, texte, barre de progression)

import os
import sys

from PyQt6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel, QProgressBar, QApplication
from PyQt6.QtCore    import Qt, QTimer, QSize
from PyQt6.QtGui     import QPixmap, QMovie, QPainter, QColor, QPainterPath, QBrush

from shared.constants import C
from shared.scaling   import S
from shared.logging.file_logger import log_error, log_msg


def asset(name: str) -> str:
    base = getattr(sys, '_MEIPASS', os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    return os.path.join(base, 'assets', name)


class SplashScreen(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint | Qt.WindowType.WindowStaysOnTopHint | Qt.WindowType.Tool)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.setFixedSize(S.splash_w, S.splash_h)

        try:
            screen = QApplication.primaryScreen().availableGeometry()
            self.move((screen.width() - S.splash_w) // 2, (screen.height() - S.splash_h) // 2)
        except Exception as e:
            log_error("splash_screen.SplashScreen.__init__", e)

        bg_path = ''
        for name in ('background.png', 'image.png'):
            candidate = asset(name)
            if os.path.exists(candidate):
                bg_path = candidate
                break
        self.bg_pixmap = QPixmap(bg_path) if bg_path else QPixmap()

        self.build_ui()

    def paintEvent(self, event):
        p = QPainter(self)
        p.setRenderHint(QPainter.RenderHint.Antialiasing)

        radius = S.radius_lg
        path   = QPainterPath()
        path.addRoundedRect(0, 0, S.splash_w, S.splash_h, radius, radius)
        p.setClipPath(path)

        if not self.bg_pixmap.isNull():
            scaled = self.bg_pixmap.scaled(S.splash_w, S.splash_h, Qt.AspectRatioMode.KeepAspectRatioByExpanding, Qt.TransformationMode.SmoothTransformation)
            ox = (scaled.width() - S.splash_w) // 2
            oy = (scaled.height() - S.splash_h) // 2
            p.drawPixmap(-ox, -oy, scaled)
        else:
            p.fillRect(self.rect(), QColor(C['bg_base']))

        p.fillRect(self.rect(), QColor(8, 11, 15, 190))

    def build_ui(self) -> None:
        root = QVBoxLayout(self)
        root.setContentsMargins(0, 0, 0, 0)
        root.setSpacing(0)

        content = QWidget()
        content.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents)
        content.setStyleSheet('background: transparent;')
        cl = QVBoxLayout(content)
        cl.setContentsMargins(S.margin_page * 2, S.margin_page * 2, S.margin_page * 2, S.margin_page)
        cl.setAlignment(Qt.AlignmentFlag.AlignCenter)
        cl.setSpacing(S.spacing_md)

        ico = QLabel('◉')
        ico.setAlignment(Qt.AlignmentFlag.AlignCenter)
        ico.setStyleSheet(f'color:{C["accent"]};font-size:{S.font_hero + 20}px;background:transparent;')

        title = QLabel('StuGo CO2 Explorer')
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title.setStyleSheet(f'color:{C["text_primary"]};font-size:{S.font_hero}px;font-weight:800;background:transparent;')

        sub = QLabel('Analyse des mobilites etudiantes')
        sub.setAlignment(Qt.AlignmentFlag.AlignCenter)
        sub.setStyleSheet(f'color:{C["text_secondary"]};font-size:{S.font_base}px;background:transparent;')

        cl.addWidget(ico)
        cl.addWidget(title)
        cl.addWidget(sub)
        root.addWidget(content, 1)

        bottom = QWidget()
        bottom.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents)
        bottom.setStyleSheet('background: transparent;')
        bl = QVBoxLayout(bottom)
        bl.setContentsMargins(S.margin_page, 0, S.margin_page, S.margin_page)
        bl.setSpacing(6)

        gif_row = QHBoxLayout()
        gif_row.setSpacing(8)
        gif_row.setAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter)

        self.gif_label = QLabel()
        self.gif_label.setFixedSize(28, 28)
        self.gif_label.setStyleSheet('background:transparent;')
        self.gif_label.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        gif_path = asset('loading.gif')
        if os.path.exists(gif_path):
            self.movie = QMovie(gif_path)
            self.movie.setScaledSize(QSize(28, 28))
            self.gif_label.setMovie(self.movie)
            self.movie.start()

        lbl_loading = QLabel('Chargement...')
        lbl_loading.setStyleSheet(f'color:{C["text_muted"]};font-size:{S.font_sm}px;background:transparent;')

        gif_row.addWidget(self.gif_label)
        gif_row.addWidget(lbl_loading)
        gif_row.addStretch()

        self.pb = QProgressBar()
        self.pb.setFixedHeight(4)
        self.pb.setTextVisible(False)
        self.pb.setRange(0, 100)
        self.pb.setValue(0)
        self.pb.setStyleSheet(f'QProgressBar{{background:{C["bg_elevated"]};border:none;border-radius:2px;}}QProgressBar::chunk{{background:{C["accent"]};border-radius:2px;}}')

        bl.addLayout(gif_row)
        bl.addWidget(self.pb)
        root.addWidget(bottom)

        self.val   = 0
        self.timer = QTimer()
        self.timer.timeout.connect(self.tick)
        self.timer.start(25)

    def tick(self) -> None:
        self.val += 1
        if 80 <= self.val < 95:
            self.timer.setInterval(90)
        self.pb.setValue(min(self.val, 99))
        if self.val >= 99:
            self.timer.stop()

    def finish(self, win) -> None:
        self.pb.setValue(100)
        QTimer.singleShot(180, lambda: self.done(win))

    def done(self, win) -> None:
        try:
            if hasattr(self, 'movie'):
                self.movie.stop()
            self.close()
            win.show()
        except Exception as e:
            log_error("splash_screen.SplashScreen.done", e)
