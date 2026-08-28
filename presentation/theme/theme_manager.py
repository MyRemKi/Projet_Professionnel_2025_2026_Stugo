# Gere le theme actuel de l'application et previent tous les widgets quand il change

from PyQt6.QtWidgets import QWidget
from PyQt6.QtCore import pyqtSignal as Signal

from shared.constants import C, ZONES, PRES_ZONE_COLORS, THEMES_PRESETS
from presentation.theme.preset_completer import complete_preset
from shared.logging.file_logger import log_error, log_msg


class ThemeManager(QWidget):

    theme_changed = Signal()
    _instance: "ThemeManager | None" = None

    @classmethod
    def instance(cls) -> "ThemeManager":
        if cls._instance is None:
            cls._instance = ThemeManager()
        return cls._instance

    def apply(self, name: str, app=None) -> None:
        try:
            preset = THEMES_PRESETS.get(name)
            if not preset:
                return
            completed = complete_preset(preset)
            C.update(completed)
            for i, key in enumerate(["zone1", "zone2", "zone3", "zone4", "zone5"]):
                ZONES[i + 1]["color"] = C.get(key, ZONES[i + 1]["color"])
            for z in ZONES:
                PRES_ZONE_COLORS[z] = ZONES[z]["color"]
            if app:
                try:
                    from presentation.theme.stylesheet_builder import StylesheetBuilder
                    app.setStyleSheet(StylesheetBuilder.build())
                except Exception as e:
                    log_error("theme_manager.ThemeManager.apply", e)
            self.theme_changed.emit()
        except Exception as e:
            log_error("theme_manager.ThemeManager.apply", e)
            try:
                self.theme_changed.emit()
            except Exception as e2:
                log_error("theme_manager.ThemeManager.apply", e2)

    def register_preset(self, name: str, colors: dict) -> None:
        THEMES_PRESETS[name] = colors


def complete_preset_internal(preset: dict) -> dict:
    return complete_preset(preset)
