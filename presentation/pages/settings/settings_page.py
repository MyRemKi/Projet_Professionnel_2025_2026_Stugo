# Page parametres : choix du theme, preset de couleurs personnalise, curseur, session

import json
import os
import sys
from shared.paths import APP_DATA_DIR as APP_DIR

from PyQt6.QtWidgets import QWidget, QVBoxLayout, QGridLayout, QLabel, QPushButton, QScrollArea, QMessageBox, QFileDialog, QFormLayout, QLineEdit, QComboBox, QHBoxLayout
from PyQt6.QtGui import QColor
from PyQt6.QtWidgets import QColorDialog

from shared.scaling import S
from shared.constants import C, THEMES_PRESETS, CUSTOM_PRESET_KEYS, PRESET_GROUPS, RADIUS_SM, CURSOR_PRESETS
from shared.color_utils import contrast_text, derive_palette_from_2, derive_palette_from_6
from presentation.theme.theme_manager import ThemeManager
from shared.logging.action_logger import ActionLogger
from shared.logging.file_logger import log_error, log_msg
from infrastructure.persistence import session_manager_compat as session_manager
from presentation.widgets.primitives import PrimaryButton, DangerButton


# Choix du curseur de souris (systeme ou image personnalisee)
class CursorSettingsWidget(QWidget):
    def __init__(self, app_ref, parent=None):
        super().__init__(parent)
        self.app_ref     = app_ref
        prefs = session_manager.load_prefs()
        self.custom_path = prefs.get("cursor_custom_path", "")
        self.build_ui()
        ThemeManager.instance().theme_changed.connect(self.restyle)

    def set_app(self, app) -> None: self.app_ref = app

    def build_ui(self) -> None:
        lay = QFormLayout(self); lay.setContentsMargins(0, 0, 0, 0); lay.setSpacing(10)
        self.combo = QComboBox()
        for n in CURSOR_PRESETS: self.combo.addItem(n)
        self.combo.currentTextChanged.connect(self.on_sel)
        lay.addRow("Curseur :", self.combo)
        row2 = QHBoxLayout()
        self.btn_browse = QPushButton("Parcourir..."); self.btn_browse.clicked.connect(self.browse)
        self.lbl_path = QLabel("Aucune image")
        row2.addWidget(self.btn_browse); row2.addWidget(self.lbl_path, 1)
        lay.addRow("Image :", row2)
        btn_reset = QPushButton("Restaurer le curseur par defaut"); btn_reset.clicked.connect(self.reset)
        lay.addRow("", btn_reset)
        self.restyle()

    def on_sel(self, name: str) -> None:
        is_c = name == "Image personnalisée"
        if is_c:
            self.lbl_path.setText(os.path.basename(self.custom_path) if self.custom_path else "Aucune image")
        self.apply_cursor(name, self.custom_path if is_c else "")
        self.save(name, self.custom_path)

    def browse(self) -> None:
        if self.combo.currentText() != "Image personnalisée":
            self.combo.setCurrentText("Image personnalisée")
        log_msg("CursorSettings.browse", "Ouverture du dialogue de sélection d'image")
        dlg = QFileDialog(self, "Sélectionner une image curseur", "")
        dlg.setNameFilter("Images (*.png *.jpg *.jpeg *.ico)")
        dlg.setFileMode(QFileDialog.FileMode.ExistingFile)
        if getattr(sys, "frozen", False):
            dlg.setOption(QFileDialog.Option.DontUseNativeDialog, True)
        if not dlg.exec():
            log_msg("CursorSettings.browse", "Dialogue annulé")
            return
        files = dlg.selectedFiles()
        if not files:
            return
        path = files[0]
        log_msg("CursorSettings.browse", f"Fichier sélectionné : {path}")
        try:
            import shutil
            save_dir = os.path.join(APP_DIR, "images")
            os.makedirs(save_dir, exist_ok=True)
            ext  = os.path.splitext(path)[1].lower() or ".png"
            dest = os.path.join(save_dir, f"custom_cursor{ext}")
            shutil.copy2(path, dest)
            log_msg("CursorSettings.browse", f"Copié vers : {dest}")
            from PyQt6.QtGui import QPixmap
            px = QPixmap(dest)
            if px.isNull():
                raise ValueError("Le fichier sélectionné n'est pas une image valide (QPixmap null).")
            self.custom_path = dest
            self.lbl_path.setText(os.path.basename(dest))
            self.apply_cursor("Image personnalisée", dest)
            self.save("Image personnalisée", dest)
            log_msg("CursorSettings.browse", "Image curseur importée avec succès")
        except Exception as e:
            log_error("CursorSettings.browse", e)
            QMessageBox.warning(self, "Impossible d'importer l'image", f"Le fichier n'a pas pu être chargé comme curseur :\n{e}\n\nUtilisez une image .png, .jpg ou .ico valide.")

    def reset(self) -> None:
        self.combo.setCurrentText("Défaut système"); self.custom_path = ""
        self.lbl_path.setText("Aucune image"); self.apply_cursor("Défaut système", "")
        self.save("Défaut système", "")

    def apply_cursor(self, name: str, path: str) -> None:
        try:
            from PyQt6.QtGui import QCursor, QPixmap
            from PyQt6.QtCore import Qt
            while self.app_ref.overrideCursor() is not None:
                self.app_ref.restoreOverrideCursor()
            if name == "Image personnalisée" and path and os.path.exists(path):
                px = QPixmap(path)
                if not px.isNull():
                    px = px.scaled(32, 32, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation)
                    self.app_ref.setOverrideCursor(QCursor(px, 0, 0))
                    return
            shape = CURSOR_PRESETS.get(name)
            if shape and shape != "custom":
                self.app_ref.setOverrideCursor(QCursor(shape))
        except Exception as e:
            log_error("settings_page.CursorSettingsWidget.apply_cursor", e)

    def save(self, name: str, path: str) -> None:
        prefs = session_manager.load_prefs()
        prefs["cursor_preset"] = name; prefs["cursor_custom_path"] = path
        session_manager.save_prefs(prefs)

    def restore_cursor_prefs(self) -> None:
        prefs = session_manager.load_prefs()
        name  = prefs.get("cursor_preset", "Défaut système")
        path  = prefs.get("cursor_custom_path", "")
        self.custom_path = path
        idx = self.combo.findText(name)
        if idx >= 0: self.combo.setCurrentIndex(idx)
        self.lbl_path.setText(os.path.basename(path) if path else "Aucune image")
        self.apply_cursor(name, path)

    def restyle(self) -> None:
        self.lbl_path.setStyleSheet(f"color:{C['text_muted']};font-size:11px;")


# Editeur de palette de couleurs personnalisee, sauvegardable en fichier .json
class CustomPresetEditor(QWidget):
    def __init__(self, app_ref, parent=None):
        super().__init__(parent)
        self.app_ref     = app_ref
        self.color_btns: dict[str, tuple] = {}
        self.current_keys: list[str] = []
        self.working = {k: C[k] for k, _ in CUSTOM_PRESET_KEYS}
        self.build_ui()
        ThemeManager.instance().theme_changed.connect(self.sync)

    def set_app(self, app) -> None: self.app_ref = app

    def sync(self) -> None:
        for k, _ in CUSTOM_PRESET_KEYS: self.working[k] = C[k]
        self.refresh_btns()

    def build_ui(self) -> None:
        lay = QVBoxLayout(self); lay.setContentsMargins(0, 0, 0, 0); lay.setSpacing(10)
        row1 = QHBoxLayout(); row1.setSpacing(8)
        row1.addWidget(QLabel("Nom :"))
        self.txt_name = QLineEdit(); self.txt_name.setPlaceholderText("Mon preset..."); self.txt_name.setMinimumWidth(140)
        row1.addWidget(self.txt_name)
        row1.addWidget(QLabel("Mode :"))
        self.combo_group = QComboBox(); self.combo_group.setMinimumWidth(155)
        for g in PRESET_GROUPS: self.combo_group.addItem(g)
        self.combo_group.currentTextChanged.connect(self.on_group)
        row1.addWidget(self.combo_group); row1.addStretch()
        lay.addLayout(row1)
        self.auto_info = QLabel(""); self.auto_info.setWordWrap(True); lay.addWidget(self.auto_info)
        self.grid_widget = QWidget(); self.grid_lay = QGridLayout(self.grid_widget)
        self.grid_lay.setSpacing(6); self.grid_lay.setContentsMargins(0, 0, 0, 0)
        lay.addWidget(self.grid_widget)
        btns = QHBoxLayout(); btns.setSpacing(8)
        btn_prev = QPushButton("Apercu"); btn_prev.clicked.connect(self.preview); btns.addWidget(btn_prev)
        btn_save = PrimaryButton("Sauvegarder (.json)"); btn_save.clicked.connect(self.save); btns.addWidget(btn_save)
        btn_load = QPushButton("Charger"); btn_load.clicked.connect(self.load); btns.addWidget(btn_load)
        btns.addStretch(); lay.addLayout(btns)
        self.on_group(self.combo_group.currentText())

    def on_group(self, g: str) -> None:
        self.current_keys  = PRESET_GROUPS.get(g, PRESET_GROUPS["Complet (18 clés)"])
        self.current_group = g
        self.rebuild_grid(self.current_keys)
        if g == "Minimal (2 clés)":
            self.auto_info.setText("info  Toutes les couleurs derivees depuis fond + accent.")
            self.auto_info.setStyleSheet(f"color:{C['blue']};font-size:11px;font-style:italic;")
        elif g == "Essentiel (6 clés)":
            self.auto_info.setText("info  Les 12 couleurs restantes sont calculees automatiquement.")
            self.auto_info.setStyleSheet(f"color:{C['blue']};font-size:11px;font-style:italic;")
        else:
            self.auto_info.setText("")

    FRIENDLY = {
        "bg_deep": "Fond barre laterale",
        "bg_base": "Fond principal",
        "bg_elevated": "Fond des panneaux",
        "bg_card": "Fond des cartes",
        "bg_input": "Fond champs de saisie",
        "bg_hover": "Survol des elements",
        "border": "Separateur / bordure",
        "border_light": "Bordure accentuee",
        "text_primary": "Texte principal",
        "text_secondary": "Texte secondaire",
        "text_muted": "Texte discret",
        "accent": "Couleur principale",
        "accent_dim": "Accent sombre",
        "blue": "Info / indicateur",
        "orange": "Avertissement",
        "red": "Erreur / danger",
        "purple": "Element special",
        "yellow": "Attention",
    }

    def rebuild_grid(self, keys: list[str]) -> None:
        while self.grid_lay.count():
            item = self.grid_lay.takeAt(0)
            w = item.widget()
            if w is not None:
                w.setParent(None)
        self.color_btns.clear()
        from PyQt6.QtCore import Qt
        cols = 3 if len(keys) > 6 else (2 if len(keys) > 2 else 1)
        for idx, key in enumerate(keys):
            r, c = divmod(idx, cols)
            cell = QWidget()
            cl = QHBoxLayout(cell)
            cl.setContentsMargins(0, 0, 0, 0)
            cl.setSpacing(6)
            lbl = QLabel(self.FRIENDLY.get(key, key))
            lbl.setFixedWidth(130)
            lbl.setStyleSheet(f"color:{C['text_secondary']};font-size:11px;")
            btn = QPushButton()
            btn.setFixedSize(50, 24)
            btn.setCursor(Qt.CursorShape.PointingHandCursor)
            self.style_btn(btn, self.working.get(key, "#888888"))
            btn.clicked.connect(lambda _, k=key: self.pick(k))
            cl.addWidget(lbl)
            cl.addWidget(btn)
            self.color_btns[key] = (btn, None)
            self.grid_lay.addWidget(cell, r, c)

    def style_btn(self, btn, hex_color: str) -> None:
        txt = contrast_text(hex_color)
        btn.setStyleSheet(f"QPushButton{{background:{hex_color};color:{txt};border:1px solid {C['border_light']};border-radius:3px;font-size:9px;font-weight:600;}}QPushButton:hover{{border:2px solid {C['accent']};}}")
        btn.setText(hex_color[-6:].upper())

    def refresh_btns(self) -> None:
        for key, (btn, _) in self.color_btns.items():
            self.style_btn(btn, self.working.get(key, "#888"))

    def pick(self, key: str) -> None:
        c = QColorDialog.getColor(QColor(self.working.get(key, "#ffffff")), self, f"Choisir : {key}")
        if c.isValid():
            self.working[key] = c.name()
            btn, _ = self.color_btns[key]; self.style_btn(btn, c.name())

    def build_full(self) -> dict:
        g = getattr(self, "current_group", "Complet (18 clés)")
        if g == "Minimal (2 clés)":
            return derive_palette_from_2({k: self.working.get(k, C[k]) for k in ["bg_base","accent"]})
        elif g == "Essentiel (6 clés)":
            return derive_palette_from_6({k: self.working.get(k, C[k]) for k in PRESET_GROUPS["Essentiel (6 clés)"]})
        else:
            p = {k: C[k] for k, _ in CUSTOM_PRESET_KEYS}
            for k in self.current_keys: p[k] = self.working.get(k, C.get(k, "#000"))
            return p

    def preview(self) -> None:
        name = self.txt_name.text().strip() or "Apercu"
        preset = self.build_full(); THEMES_PRESETS[f"__prev__{name}"] = preset
        ThemeManager.instance().apply(f"__prev__{name}", self.app_ref)
        del THEMES_PRESETS[f"__prev__{name}"]

    def save(self) -> None:
        name = self.txt_name.text().strip()
        if not name: QMessageBox.warning(self, "Nom manquant", "Donnez un nom."); return
        preset = self.build_full()
        save_dir = os.path.join(APP_DIR, "PresetColors")
        os.makedirs(save_dir, exist_ok=True)
        path, _ = QFileDialog.getSaveFileName(self, "Sauvegarder", os.path.join(save_dir, f"{name}.json"), "JSON (*.json)")
        if not path: return
        with open(path, "w", encoding="utf-8") as f: json.dump({"name": name, "colors": preset}, f, indent=2, ensure_ascii=False)
        ThemeManager.instance().register_preset(name, preset)
        ActionLogger.instance().log("save", f"Preset : {name}")
        QMessageBox.information(self, "Sauvegarde", f"Preset '{name}' sauvegarde.")

    def load(self) -> None:
        save_dir = os.path.join(APP_DIR, "PresetColors")
        os.makedirs(save_dir, exist_ok=True)
        paths, _ = QFileDialog.getOpenFileNames(self, "Charger", save_dir, "JSON (*.json)")
        if not paths: return
        loaded, errors = [], []
        for p in paths:
            try:
                with open(p, "r", encoding="utf-8") as f: data = json.load(f)
                name   = data.get("name", os.path.splitext(os.path.basename(p))[0])
                colors = data.get("colors", data)
                if not isinstance(colors, dict) or "bg_base" not in colors: raise ValueError("Format invalide")
                ThemeManager.instance().register_preset(name, colors)
                if not loaded:
                    self.txt_name.setText(name)
                    for k in self.current_keys:
                        if k in colors: self.working[k] = colors[k]
                    self.refresh_btns()
                loaded.append(name); ActionLogger.instance().log("import", f"Preset : {name}")
            except Exception as e: errors.append(f"{os.path.basename(p)}: {e}")
        msg = f"{len(loaded)} preset(s) charge(s)"
        if errors: msg += "\n\nErreurs :\n" + "\n".join(errors)
        QMessageBox.information(self, "Chargement", msg)


# Page principale des parametres, regroupe theme / preset / curseur / session
class SettingsPage(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.app_ref = None
        self.current_theme = "Arctic Ink (défaut)"
        self.build_ui()
        ThemeManager.instance().theme_changed.connect(self.restyle)

    def set_app(self, app) -> None:
        self.app_ref = app
        if hasattr(self, "custom_editor"): self.custom_editor.set_app(app)
        if hasattr(self, "cursor"): self.cursor.set_app(app)

    def restore_cursor(self) -> None:
        if hasattr(self, "cursor"): self.cursor.restore_cursor_prefs()

    def build_ui(self) -> None:
        lay = QVBoxLayout(self); lay.setContentsMargins(28, 28, 28, 28); lay.setSpacing(16)
        self.t1 = QLabel("Parametres"); self.t2 = QLabel("Apparence et comportement de l'application.")
        lay.addWidget(self.t1); lay.addWidget(self.t2)
        scroll = QScrollArea(); scroll.setWidgetResizable(True)
        inner = QWidget(); il = QVBoxLayout(inner); il.setContentsMargins(0, 0, 0, 0); il.setSpacing(20)
        scroll.setWidget(inner)
        il.addWidget(self.section_lbl("THEME"))
        il.addWidget(QLabel("Cliquez pour appliquer instantanement."))
        self.theme_grid = QGridLayout(); self.theme_grid.setSpacing(8)
        self.theme_buttons: dict[str, QPushButton] = {}
        for i, (name, colors) in enumerate(THEMES_PRESETS.items()):
            btn = QPushButton(); btn.setMinimumHeight(S.stat_h - S.spacing_md); btn.setMinimumWidth(round(S.dpi_scale * 195))
            self.theme_buttons[name] = btn
            self.style_theme_btn(btn, name, colors, i == 0)
            btn.clicked.connect(lambda _, n=name: self.apply(n))
            r, c = divmod(i, 2); self.theme_grid.addWidget(btn, r, c)
        il.addLayout(self.theme_grid)
        il.addWidget(self.section_lbl("PRESET PERSONNALISE"))
        self.custom_editor = CustomPresetEditor(None)
        il.addWidget(self.custom_editor)
        il.addWidget(self.section_lbl("CURSEUR"))
        self.cursor = CursorSettingsWidget(None)
        il.addWidget(self.cursor)
        il.addWidget(self.section_lbl("SESSION"))
        btn_clear = DangerButton("Effacer les donnees de session")
        btn_clear.clicked.connect(self.clear_sess)
        il.addWidget(btn_clear)
        il.addWidget(self.section_lbl("A PROPOS"))
        about = QLabel(f"<b style='font-size:14px;'>StuGo CO2 Explorer</b><br><span style='color:{C['text_muted']};'>Version 7.0</span><br><br><span style='color:{C['text_secondary']};'>Analyse des emissions CO2 liees aux mobilites etudiantes.</span>")
        about.setWordWrap(True); il.addWidget(about)
        il.addStretch()
        lay.addWidget(scroll, 1)
        self.restyle()

    def section_lbl(self, text: str) -> QLabel:
        l = QLabel(text)
        l.setStyleSheet(f"color:{C['text_muted']};font-size:10px;font-weight:700;letter-spacing:1px;")
        return l

    def style_theme_btn(self, btn, name, colors, selected) -> None:
        bg1 = colors.get("bg_elevated", "#1c2128"); bg2 = colors.get("bg_base", "#161b22")
        ac  = colors.get("accent", "#39d353"); txt = contrast_text(bg1)
        bw  = "2px" if selected else "1px"; chk = "  ✓" if selected else ""
        btn.setText(f"{name}{chk}")
        btn.setStyleSheet(f"QPushButton{{background:qlineargradient(x1:0,y1:0,x2:1,y2:1,stop:0 {bg1},stop:1 {bg2});color:{txt};border:{bw} solid {ac};border-radius:{RADIUS_SM};font-size:12px;font-weight:{'700' if selected else '500'};padding:10px 14px;text-align:left;}}QPushButton:hover{{border-width:2px;}}")

    def apply(self, name: str) -> None:
        self.current_theme = name
        ThemeManager.instance().apply(name, self.app_ref)
        prefs = session_manager.load_prefs()
        prefs["theme_preset"] = name; session_manager.save_prefs(prefs)
        ActionLogger.instance().log("info", f"Theme : {name}")
        for n, btn in self.theme_buttons.items():
            if n in THEMES_PRESETS:
                self.style_theme_btn(btn, n, THEMES_PRESETS[n], n == name)

    def clear_sess(self) -> None:
        reply = QMessageBox.question(self, "Effacer", "Supprimer les donnees de session ?", QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
        if reply == QMessageBox.StandardButton.Yes:
            if session_manager.clear_session():
                QMessageBox.information(self, "OK", "Session effacee.")
            else:
                QMessageBox.warning(self, "Erreur", "Impossible d'effacer la session.")

    def restyle(self) -> None:
        if hasattr(self, "t1"): self.t1.setStyleSheet(f"font-size:20px;font-weight:800;color:{C['text_primary']};")
        if hasattr(self, "t2"): self.t2.setStyleSheet(f"font-size:13px;color:{C['text_secondary']};")
        for name, btn in self.theme_buttons.items():
            if name in THEMES_PRESETS:
                self.style_theme_btn(btn, name, THEMES_PRESETS[name], name == self.current_theme)
