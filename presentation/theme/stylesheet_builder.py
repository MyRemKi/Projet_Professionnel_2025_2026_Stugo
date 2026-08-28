# Construit le style visuel (couleurs, tailles) applique a toute l'application

from shared.constants import C
from shared.scaling import S


class StylesheetBuilder:

    @staticmethod
    def build() -> str:
        s = S
        return f"""
/* ── Reset & base ─────────────────────────────────────────────────────── */
* {{
    font-family: 'Segoe UI', 'SF Pro Display', 'Helvetica Neue', system-ui, sans-serif;
    font-size: {s.font_base}px;
    color: {C['text_primary']};
    outline: none;
}}
QMainWindow, QWidget {{
    background: {C['bg_base']};
}}
QScrollArea {{
    background: transparent;
    border: none;
}}
QScrollArea > QWidget > QWidget {{
    background: transparent;
}}

/* ── Scrollbars ────────────────────────────────────────────────────────── */
QScrollBar:vertical {{
    background: transparent;
    width: {max(6, round(s.dpi_scale * 6))}px;
    margin: 0;
}}
QScrollBar::handle:vertical {{
    background: {C['border_light']};
    border-radius: {max(3, round(s.dpi_scale * 3))}px;
    min-height: {round(s.dpi_scale * 24)}px;
}}
QScrollBar::handle:vertical:hover {{ background: {C['accent']}; }}
QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {{ height: 0; }}
QScrollBar:horizontal {{
    background: transparent;
    height: {max(6, round(s.dpi_scale * 6))}px;
}}
QScrollBar::handle:horizontal {{
    background: {C['border_light']};
    border-radius: {max(3, round(s.dpi_scale * 3))}px;
    min-width: {round(s.dpi_scale * 24)}px;
}}
QScrollBar::handle:horizontal:hover {{ background: {C['accent']}; }}
QScrollBar::add-line:horizontal, QScrollBar::sub-line:horizontal {{ width: 0; }}

/* ── Boutons ───────────────────────────────────────────────────────────── */
QPushButton {{
    background: {C['bg_input']};
    color: {C['text_secondary']};
    border: 1px solid {C['border']};
    border-radius: {s.r_sm()};
    padding: {round(s.dpi_scale * 5)}px {round(s.dpi_scale * 14)}px;
    font-size: {s.font_base}px;
    font-weight: 500;
    min-height: {s.btn_h}px;
}}
QPushButton:hover {{
    background: {C['bg_hover']};
    border-color: {C['accent']};
    color: {C['text_primary']};
}}
QPushButton:pressed {{ background: {C['bg_card']}; }}
QPushButton:disabled {{
    color: {C['text_muted']};
    border-color: {C['border']};
}}

/* ── ComboBox ──────────────────────────────────────────────────────────── */
QComboBox {{
    background: {C['bg_input']};
    color: {C['text_primary']};
    border: 1px solid {C['border']};
    border-radius: {s.r_sm()};
    padding: {round(s.dpi_scale * 5)}px {round(s.dpi_scale * 28)}px {round(s.dpi_scale * 5)}px {round(s.dpi_scale * 10)}px;
    font-size: {s.font_base}px;
    min-height: {s.input_h}px;
}}
QComboBox:hover {{ border-color: {C['border_light']}; }}
QComboBox:focus {{ border-color: {C['accent']}; }}
QComboBox::drop-down {{
    border: none;
    width: {round(s.dpi_scale * 22)}px;
    subcontrol-origin: padding;
    subcontrol-position: right center;
}}
QComboBox::down-arrow {{
    image: none;
    width: 0; height: 0;
    border-left: {round(s.dpi_scale * 4)}px solid transparent;
    border-right: {round(s.dpi_scale * 4)}px solid transparent;
    border-top: {round(s.dpi_scale * 5)}px solid {C['text_muted']};
}}
QComboBox QAbstractItemView {{
    background: {C['bg_elevated']};
    color: {C['text_primary']};
    border: 1px solid {C['border_light']};
    border-radius: {s.r_sm()};
    selection-background-color: {C['accent_dim']};
    selection-color: {C['text_primary']};
    padding: {round(s.dpi_scale * 2)}px;
    font-size: {s.font_base}px;
}}

/* ── Champs de saisie ──────────────────────────────────────────────────── */
QLineEdit, QSpinBox, QDoubleSpinBox {{
    background: {C['bg_input']};
    color: {C['text_primary']};
    border: 1px solid {C['border']};
    border-radius: {s.r_sm()};
    padding: {round(s.dpi_scale * 5)}px {round(s.dpi_scale * 10)}px;
    font-size: {s.font_base}px;
    min-height: {s.input_h}px;
}}
QLineEdit:focus, QSpinBox:focus, QDoubleSpinBox:focus {{
    border-color: {C['accent']};
}}
QLineEdit:hover, QSpinBox:hover, QDoubleSpinBox:hover {{
    border-color: {C['border_light']};
}}
QSpinBox::up-button, QSpinBox::down-button,
QDoubleSpinBox::up-button, QDoubleSpinBox::down-button {{
    background: {C['bg_hover']};
    border: none;
    width: {round(s.dpi_scale * 20)}px;
    border-radius: {s.radius_sm // 2}px;
    subcontrol-origin: padding;
}}
QSpinBox::up-button {{ subcontrol-position: top right; }}
QSpinBox::down-button {{ subcontrol-position: bottom right; }}
QDoubleSpinBox::up-button {{ subcontrol-position: top right; }}
QDoubleSpinBox::down-button {{ subcontrol-position: bottom right; }}
QSpinBox::up-button:hover, QDoubleSpinBox::up-button:hover,
QSpinBox::down-button:hover, QDoubleSpinBox::down-button:hover {{
    background: {C['accent_dim']};
}}
QSpinBox::up-arrow, QDoubleSpinBox::up-arrow {{
    image: none;
    width: 0; height: 0;
    border-left: {round(s.dpi_scale * 4)}px solid transparent;
    border-right: {round(s.dpi_scale * 4)}px solid transparent;
    border-bottom: {round(s.dpi_scale * 5)}px solid {C['text_secondary']};
}}
QSpinBox::up-arrow:hover, QDoubleSpinBox::up-arrow:hover {{
    border-bottom-color: {C['accent']};
}}
QSpinBox::down-arrow, QDoubleSpinBox::down-arrow {{
    image: none;
    width: 0; height: 0;
    border-left: {round(s.dpi_scale * 4)}px solid transparent;
    border-right: {round(s.dpi_scale * 4)}px solid transparent;
    border-top: {round(s.dpi_scale * 5)}px solid {C['text_secondary']};
}}
QSpinBox::down-arrow:hover, QDoubleSpinBox::down-arrow:hover {{
    border-top-color: {C['accent']};
}}

/* ── TextEdit ──────────────────────────────────────────────────────────── */
QTextEdit {{
    background: {C['bg_input']};
    color: {C['text_primary']};
    border: 1px solid {C['border']};
    border-radius: {s.r_sm()};
    padding: {round(s.dpi_scale * 6)}px;
    font-size: {s.font_base}px;
}}

/* ── GroupBox ──────────────────────────────────────────────────────────── */
QGroupBox {{
    background: transparent;
    border: none;
    margin-top: {round(s.dpi_scale * 20)}px;
    padding: {round(s.dpi_scale * 6)}px 0 0 0;
    font-weight: 600;
}}
QGroupBox::title {{
    subcontrol-origin: margin;
    left: 0; top: 0;
    padding: 0;
    color: {C['text_muted']};
    font-size: {s.font_sm}px;
    font-weight: 700;
    letter-spacing: 0.8px;
    text-transform: uppercase;
}}

/* ── Tableau ───────────────────────────────────────────────────────────── */
QTableView {{
    background: {C['bg_elevated']};
    alternate-background-color: {C['bg_card']};
    color: {C['text_primary']};
    gridline-color: {C['border']};
    border: 1px solid {C['border']};
    border-radius: {s.r_sm()};
    selection-background-color: {C['accent_dim']};
    selection-color: {C['text_primary']};
    font-size: {s.font_base}px;
}}
QTableView::item {{
    padding: {round(s.dpi_scale * 3)}px {round(s.dpi_scale * 6)}px;
}}
QTableView::item:hover {{ background: {C['bg_hover']}; }}
QHeaderView::section {{
    background: {C['bg_card']};
    color: {C['text_muted']};
    border: none;
    border-bottom: 1px solid {C['border']};
    border-right: 1px solid {C['border']};
    padding: {round(s.dpi_scale * 7)}px {round(s.dpi_scale * 10)}px;
    font-weight: 700;
    font-size: {s.font_sm}px;
    letter-spacing: 0.4px;
    min-height: {round(s.dpi_scale * 30)}px;
}}
QHeaderView::section:hover {{
    color: {C['text_primary']};
    background: {C['bg_hover']};
}}

/* ── Onglets ───────────────────────────────────────────────────────────── */
QTabWidget::pane {{ border: none; background: transparent; }}
QTabBar::tab {{
    background: transparent;
    color: {C['text_muted']};
    padding: {round(s.dpi_scale * 9)}px {round(s.dpi_scale * 20)}px;
    border: none;
    border-bottom: 2px solid transparent;
    font-size: {s.font_base}px;
}}
QTabBar::tab:selected {{
    color: {C['accent']};
    border-bottom: 2px solid {C['accent']};
    font-weight: 600;
}}
QTabBar::tab:hover:!selected {{ color: {C['text_secondary']}; }}

/* ── Checkbox ──────────────────────────────────────────────────────────── */
QCheckBox {{
    color: {C['text_secondary']};
    spacing: {round(s.dpi_scale * 7)}px;
    font-size: {s.font_base}px;
}}
QCheckBox::indicator {{
    width: {round(s.dpi_scale * 16)}px;
    height: {round(s.dpi_scale * 16)}px;
    border: 1px solid {C['border_light']};
    border-radius: {round(s.dpi_scale * 3)}px;
    background: {C['bg_input']};
}}
QCheckBox::indicator:hover {{ border-color: {C['accent']}; }}
QCheckBox::indicator:checked {{
    background: {C['accent']};
    border-color: {C['accent']};
    image: none;
}}
QCheckBox:hover {{ color: {C['text_primary']}; }}

/* ── Slider ────────────────────────────────────────────────────────────── */
QSlider::groove:horizontal {{
    height: {round(s.dpi_scale * 4)}px;
    background: {C['bg_hover']};
    border-radius: {round(s.dpi_scale * 2)}px;
}}
QSlider::handle:horizontal {{
    background: {C['accent']};
    width: {round(s.dpi_scale * 16)}px;
    height: {round(s.dpi_scale * 16)}px;
    margin: {-round(s.dpi_scale * 6)}px 0;
    border-radius: {round(s.dpi_scale * 8)}px;
    border: 2px solid {C['bg_base']};
}}
QSlider::sub-page:horizontal {{
    background: {C['accent_dim']};
    border-radius: {round(s.dpi_scale * 2)}px;
}}

/* ── StatusBar ─────────────────────────────────────────────────────────── */
QStatusBar {{
    background: {C['bg_deep']};
    color: {C['text_muted']};
    border-top: 1px solid {C['border']};
    font-size: {s.font_sm}px;
    padding: 0 {round(s.dpi_scale * 12)}px;
    min-height: {round(s.dpi_scale * 24)}px;
}}

/* ── ToolButton ────────────────────────────────────────────────────────── */
QToolButton {{
    background: transparent;
    border: none;
    border-radius: {s.r_sm()};
    padding: {round(s.dpi_scale * 4)}px {round(s.dpi_scale * 8)}px;
    color: {C['text_muted']};
    font-size: {s.font_base}px;
    min-height: {s.btn_h}px;
    min-width: {s.btn_h}px;
}}
QToolButton:hover {{ background: {C['bg_hover']}; color: {C['text_primary']}; }}
QToolButton:checked {{ background: {C['accent_dim']}; color: {C['accent']}; }}

/* ── Séparateurs ───────────────────────────────────────────────────────── */
QFrame[frameShape="4"], QFrame[frameShape="5"] {{
    color: {C['border']};
}}

/* ── ProgressBar ───────────────────────────────────────────────────────── */
QProgressBar {{
    background: {C['bg_elevated']};
    border: none;
    border-radius: {s.r_sm()};
    text-align: center;
    color: {C['text_primary']};
    font-size: {s.font_sm}px;
    min-height: {round(s.dpi_scale * 8)}px;
}}
QProgressBar::chunk {{
    background: {C['accent']};
    border-radius: {s.r_sm()};
}}

/* ── MessageBox ────────────────────────────────────────────────────────── */
QMessageBox {{
    background: {C['bg_elevated']};
    font-size: {s.font_base}px;
}}
QMessageBox QLabel {{
    color: {C['text_primary']};
    font-size: {s.font_base}px;
    min-width: {round(s.dpi_scale * 280)}px;
}}
"""
