# Fenetre principale : assemble la barre laterale, les pages et gere import/session

import json
import os
from datetime import datetime

import pandas as pd
from PyQt6.QtWidgets import QMainWindow, QWidget, QHBoxLayout, QVBoxLayout, QStackedWidget, QStatusBar, QFileDialog, QMessageBox

from shared.constants import C, PAGES
from shared.scaling import S
from shared.logging.action_logger import ActionLogger
from shared.logging.file_logger import log_error, log_msg
from presentation.theme.theme_manager import ThemeManager
from infrastructure.persistence import session_manager_compat as session_manager
from infrastructure.extractors.extractor_factory import ExtractorFactory
from infrastructure.models.pandas_model import PandasModel
from presentation.sidebar.nav_sidebar import Sidebar
from presentation.sidebar.filter_sidebar import FilterSidebar
from presentation.sidebar.log_panel import LogSessionPanel
from presentation.pages.home.home_page import HomePage
from presentation.pages.import_.import_page import ImportPage
from presentation.pages.table.table_page import TablePage
from presentation.pages.chart.chart_page import ChartPage
from presentation.pages.comparison.comparison_page import ComparisonPage
from presentation.pages.settings.settings_page import SettingsPage
from presentation.pages.help.help_page import HelpPage


class MainWindow(QMainWindow):
    def __init__(self, app):
        super().__init__()
        self.app = app
        self.setWindowTitle("StuGo CO2 Explorer  v7")
        base_w = round(S.dpi_scale * 1440)
        base_h = round(S.dpi_scale * 880)
        self.resize(max(1200, base_w), max(720, base_h))
        self.setMinimumSize(round(S.dpi_scale * 1100), round(S.dpi_scale * 680))

        self.df_all: pd.DataFrame = pd.DataFrame()
        self.summaries: dict = {}
        self.loaded_uids: set[str] = set()
        self.logger = ActionLogger.instance()
        self.n_exports = 0
        self.current_page = "home"
        self.dirty = False

        self.build_ui()
        self.restore_logs()
        self.try_auto_resume()
        self.load_saved_prefs()

    def build_ui(self) -> None:
        self.setStatusBar(QStatusBar())
        central = QWidget(); self.setCentralWidget(central)
        root = QHBoxLayout(central)
        root.setContentsMargins(0, 0, 0, 0)
        root.setSpacing(0)

        self.sidebar = Sidebar()
        self.sidebar.page_changed.connect(self.nav)
        root.addWidget(self.sidebar)

        center = QWidget()
        cl = QHBoxLayout(center)
        cl.setContentsMargins(0, 0, 0, 0)
        cl.setSpacing(0)

        self.left_stack = QStackedWidget()
        self.left_stack.setFixedWidth(S.filter_w)

        self.filter_sidebar = FilterSidebar()
        self.filter_sidebar.filter_changed.connect(self.apply_filters)
        self.left_stack.addWidget(self.filter_sidebar)

        self.log_panel = LogSessionPanel()
        self.log_panel.save_requested.connect(self.save_session)
        self.log_panel.resume_requested.connect(self.resume_session)
        self.left_stack.addWidget(self.log_panel)
        self.left_stack.addWidget(QWidget())
        self.left_stack.addWidget(QWidget())
        cl.addWidget(self.left_stack)

        right = QWidget()
        rl = QVBoxLayout(right)
        rl.setContentsMargins(0, 0, 0, 0)
        rl.setSpacing(0)

        self.page_stack = QStackedWidget()
        rl.addWidget(self.page_stack, 1)

        self.home_page = HomePage()
        self.home_page.navigate_to.connect(self.nav)
        self.page_stack.addWidget(self.home_page)

        self.import_page = ImportPage()
        self.import_page.files_added.connect(self.load_files)
        self.import_page.file_removed.connect(self.remove_file)
        self.page_stack.addWidget(self.import_page)

        self.table_page = TablePage()
        self.table_page.combo_sort.currentIndexChanged.connect(self.apply_filters)
        self.table_page.btn_sort_dir.toggled.connect(lambda _: self.apply_filters())
        self.table_page.btn_csv.clicked.connect(self.export_csv)
        self.table_page.btn_csv.setEnabled(False)
        self.page_stack.addWidget(self.table_page)

        self.chart_page = ChartPage(self.df_all)
        self.page_stack.addWidget(self.chart_page)

        self.comparison_page = ComparisonPage(self.df_all)
        self.page_stack.addWidget(self.comparison_page)

        self.settings_page = SettingsPage()
        self.settings_page.set_app(self.app)
        self.page_stack.addWidget(self.settings_page)

        self.help_page = HelpPage()
        self.page_stack.addWidget(self.help_page)

        cl.addWidget(right, 1)
        root.addWidget(center, 1)
        self.nav("home")

        ThemeManager.instance().theme_changed.connect(self.restyle_status)

    def restyle_status(self) -> None:
        if hasattr(self, "last_msg"):
            self.statusBar().showMessage(self.last_msg)

    def update_export_btn(self) -> None:
        self.table_page.btn_csv.setEnabled(not self.df_all.empty)

    def nav(self, key: str) -> None:
        self.current_page = key
        self.page_stack.setCurrentIndex(PAGES[key]["idx"])
        self.sidebar.set_page(key)

        if key in {"table", "chart", "comparison"}:
            self.left_stack.setCurrentIndex(0)
            self.left_stack.setFixedWidth(S.filter_w)
        elif key == "settings":
            self.left_stack.setCurrentIndex(2)
            self.left_stack.setFixedWidth(0)
        else:
            self.left_stack.setCurrentIndex(1)
            self.left_stack.setFixedWidth(S.log_w)

        if key == "comparison":
            df = self.filtered_df()
            self.comparison_page.update_data(df)

        msg = f"  {PAGES[key]['icon']}  {PAGES[key]['label']}"
        self.last_msg = msg
        self.statusBar().showMessage(msg)

    def load_files(self, filepaths: list[str]) -> None:
        import pandas as pd
        by_ext: dict[str, list[str]] = {}
        unsupported: list[str] = []
        for fp in filepaths:
            ext = os.path.splitext(fp)[1].lower()
            if ext in ExtractorFactory.supported():
                by_ext.setdefault(ext, []).append(fp)
            else:
                unsupported.append(os.path.basename(fp))

        if unsupported:
            QMessageBox.warning(self, "Format non supporté", f"Fichier(s) ignoré(s) — format non supporté :\n" + "\n".join(f"  • {f}" for f in unsupported) + "\n\nFormats acceptés : .xlsx, .xls, .csv (export StuGo)")

        merged_df  = pd.DataFrame()
        new_sum    = {}
        new_uids   = set()

        for ext, paths in by_ext.items():
            try:
                handler = ExtractorFactory.get(ext)
                part_df, part_sum, part_uids = handler(paths, self.loaded_uids)
                if not part_df.empty:
                    merged_df = part_df if merged_df.empty else pd.concat([merged_df, part_df], ignore_index=True)
                new_sum.update(part_sum)
                new_uids |= part_uids
            except Exception as e:
                log_error("MainWindow.load_files", e)
                QMessageBox.critical(self, "Erreur d'import", f"Impossible de lire les fichiers {ext} :\n{e}")

        new_df = merged_df

        n_skipped_by_dedup = 0
        cross_dupes = self.find_cross_duplicates(new_uids)
        if cross_dupes:
            csv_to_skip = {c["csv_uid"] for c in cross_dupes}
            lines = []
            for c in cross_dupes:
                cp      = c["csv_uid"].split("::")
                sheet   = cp[2] if len(cp) == 3 else "?"
                fichier = cp[1] if len(cp) == 3 else "?"
                if c["csv_is_new"] and c["xlsx_is_new"]:
                    ctx = "Excel + CSV importés ensemble"
                elif c["csv_is_new"]:
                    ctx = "Excel déjà chargé"
                else:
                    ctx = "CSV déjà chargé"
                lines.append(f"  • {sheet}  ({fichier})  [{ctx}]")

            xlsx_to_skip = {c["xlsx_uid"] for c in cross_dupes if c["xlsx_is_new"]}
            n_csv  = len(csv_to_skip)
            n_xlsx = len(xlsx_to_skip)
            n_other_xlsx = len([u for u in new_uids if len(u.split("::")) == 2 and u not in xlsx_to_skip])
            details = "\n".join(lines)
            msg = f"{n_csv} feuille(s) CSV sont des exports de fichiers Excel déjà présents :\n\n{details}\n\n"
            if n_other_xlsx:
                msg += f"Note : {n_other_xlsx} autre(s) feuille(s) Excel (sans doublon) seront importées.\n\n"
            msg += "Que voulez-vous faire ?\n→ Non (recommandé) : ignorer CSV et Excel en double\n→ Oui : importer les deux (données doublées)"

            reply = QMessageBox.question(self, "Doublons détectés", msg, QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No, QMessageBox.StandardButton.No)
            if reply == QMessageBox.StandardButton.No:
                uids_to_skip = csv_to_skip | xlsx_to_skip
                n_skipped_by_dedup = len(uids_to_skip)
                new_uids -= uids_to_skip
                new_sum   = {k: v for k, v in new_sum.items() if k not in uids_to_skip}
                if not new_df.empty:
                    new_df = new_df[new_df["source_uid"].isin(new_uids)] if new_uids else pd.DataFrame()

        invalid = {k: v for k, v in new_sum.items() if k.startswith("invalid::") or k.startswith("error::")}
        if invalid:
            msgs = "\n".join(f"• {v.get('label','?')} : {v.get('error','erreur inconnue')}" for v in invalid.values())
            log_msg("MainWindow.load_files", f"{len(invalid)} onglet(s) invalide(s) : {msgs}")
            QMessageBox.warning(self, "Format de fichier incorrect", f"{len(invalid)} onglet(s) ignoré(s) car le format ne correspond pas au format StuGo CO2 Explorer :\n\n{msgs}\n\nConsultez logs/log-*.txt pour plus de détails.")

        if new_df.empty and not new_uids:
            if not invalid:
                if n_skipped_by_dedup:
                    QMessageBox.information(self, "Import", f"{n_skipped_by_dedup} feuille(s) CSV ignorée(s) — les données Excel correspondantes sont déjà chargées.\nAucune nouvelle donnée ajoutée.")
                else:
                    QMessageBox.information(self, "Import", "Aucune nouvelle donnée trouvée.")
            return

        self.loaded_uids |= new_uids
        self.summaries.update(new_sum)
        self.df_all = new_df if self.df_all.empty else pd.concat([self.df_all, new_df], ignore_index=True)

        for uid in new_uids:
            try:
                label = new_sum.get(uid, {}).get("label", uid)
                sub   = new_df[new_df["source_uid"] == uid]
                fp    = sub["filepath"].iloc[0] if not sub.empty else ""
                self.import_page.add_file(uid, label, fp, self.df_all)
                sheet = label.split("::")[-1] if "::" in label else label
                self.logger.log("import", f"{sheet}  ({os.path.basename(fp)})")
            except Exception as e:
                log_error("MainWindow.load_files[uid_loop]", e)
                continue

        self.filter_sidebar.refresh_faculties(self.df_all)
        self.apply_filters()
        self.log_panel.refresh()
        dedup_note = f" — {n_skipped_by_dedup} CSV ignoré(s) (doublon Excel)" if n_skipped_by_dedup else ""
        self.statusBar().showMessage(f"  ✓  {len(new_uids)} feuille(s) chargée(s) — {len(self.df_all):,} lignes au total{dedup_note}")
        self.dirty = True
        self.update_export_btn()

    def remove_file(self, source_uid: str) -> None:
        if source_uid not in self.loaded_uids:
            return
        label = self.summaries.get(source_uid, {}).get("label", source_uid)
        self.loaded_uids.discard(source_uid)
        self.df_all = self.df_all[self.df_all["source_uid"] != source_uid].reset_index(drop=True)
        self.summaries.pop(source_uid, None)
        self.filter_sidebar.refresh_faculties(self.df_all)
        self.apply_filters()
        self.logger.log("remove", f"Supprimé : {label.split('::')[-1]}")
        self.log_panel.refresh()
        self.dirty = True
        self.update_export_btn()

    def find_cross_duplicates(self, new_uids: set) -> list[dict]:
        all_uids = self.loaded_uids | new_uids

        xlsx_idx: dict[tuple, str] = {}
        for uid in all_uids:
            parts = uid.split("::")
            if len(parts) == 2:
                xlsx_idx[(os.path.basename(parts[0]), parts[1])] = uid

        conflicts, seen = [], set()
        for uid in all_uids:
            parts = uid.split("::")
            if len(parts) == 3:
                key = (parts[1], parts[2])
                if key in xlsx_idx:
                    pair = (uid, xlsx_idx[key])
                    if pair not in seen:
                        seen.add(pair)
                        conflicts.append({"csv_uid": uid, "xlsx_uid": xlsx_idx[key], "csv_is_new": uid in new_uids, "xlsx_is_new": xlsx_idx[key] in new_uids})
        return conflicts

    def filtered_df(self) -> pd.DataFrame:
        if self.df_all.empty:
            return pd.DataFrame(columns=PandasModel.COLS)

        df = self.df_all.copy()
        df = self.filter_sidebar.apply(df)

        try:
            sort_col = self.table_page.combo_sort.currentData()
            asc = not self.table_page.btn_sort_dir.isChecked()
            if sort_col and sort_col in df.columns:
                df = df.sort_values(sort_col, ascending=asc).reset_index(drop=True)
        except Exception as e:
            log_error("main_window.MainWindow.filtered_df", e)
        return df

    def apply_filters(self) -> None:
        df = self.filtered_df()

        self.table_page.update_df(df)
        self.chart_page.update_data(df)
        self.home_page.update_stats(df, len(self.loaded_uids), self.n_exports)

        if self.current_page == "comparison":
            self.comparison_page.update_data(df)

    def export_csv(self) -> None:
        path, _ = QFileDialog.getSaveFileName(self, "Exporter CSV", "co2_export.csv", "CSV (*.csv)")
        if path:
            try:
                df = self.filtered_df()
                df.to_csv(path, index=False, sep=";", encoding="utf-8-sig")
                self.n_exports += 1
                self.logger.log("export_csv", f"CSV → {os.path.basename(path)}")
                self.log_panel.refresh()
                QMessageBox.information(self, "Export CSV", f"Fichier sauvegardé :\n{path}")
            except Exception as e:
                log_error("main_window.MainWindow.export_csv", e)
                QMessageBox.warning(self, "Erreur export CSV", f"Impossible d'exporter :\n{e}")

    def closeEvent(self, event) -> None:
        if not self.dirty:
            event.accept()
            return

        box = QMessageBox(self)
        box.setWindowTitle("Quitter StuGo CO2 Explorer")
        box.setText("Vos données d'activité (fichiers chargés, actions récentes) ne seront pas conservées si vous ne sauvegardez pas la session.\n\nSouhaitez-vous sauvegarder la session avant de quitter ?")
        box.setIcon(QMessageBox.Icon.Warning)
        btn_save   = box.addButton("Sauvegarder et quitter", QMessageBox.ButtonRole.AcceptRole)
        btn_quit   = box.addButton("Quitter sans sauvegarder", QMessageBox.ButtonRole.DestructiveRole)
        btn_cancel = box.addButton("Annuler", QMessageBox.ButtonRole.RejectRole)
        box.setDefaultButton(btn_save)
        box.exec()

        clicked = box.clickedButton()
        if clicked == btn_save:
            self.save_session()
            event.accept()
        elif clicked == btn_quit:
            event.accept()
        else:
            event.ignore()

    def save_session(self) -> None:
        existing = session_manager.load_session()
        if existing:
            existing_ts = existing.get("ts", "date inconnue")
            reply = QMessageBox.question(self, "Session existante", f"Une session est déjà sauvegardée ({existing_ts}).\n\nVoulez-vous l'écraser avec la session actuelle ?", QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No, QMessageBox.StandardButton.No)
            if reply != QMessageBox.StandardButton.Yes:
                return

        uid_list = list(self.loaded_uids)
        fps: dict[str, str] = {}
        for uid in uid_list:
            try:
                sub = self.df_all[self.df_all["source_uid"] == uid]
                fps[uid] = str(sub["filepath"].iloc[0]) if not sub.empty else ""
            except Exception as e:
                log_error("main_window.MainWindow.save_session", e)
                fps[uid] = ""

        ts = datetime.now().strftime("%d/%m/%Y à %H:%M:%S")
        data = {
            "uids": uid_list,
            "filepaths": fps,
            "filters": self.filter_sidebar.get_state(),
            "page": self.current_page,
            "logs": json.loads(self.logger.to_json()),
            "ts": ts,
        }
        if session_manager.save_session(data):
            self.dirty = False
            self.logger.log("save", f"Session sauvegardée ({ts})")
            self.log_panel.refresh()
            self.log_panel.update_session_info(ts)
            self.statusBar().showMessage(f"  ◉  Session sauvegardée — {ts}")
        else:
            QMessageBox.warning(self, "Erreur", "Impossible de sauvegarder la session.")

    def restore_logs(self) -> None:
        data = session_manager.load_session()
        if data:
            logs_data = data.get("logs", [])
            if logs_data:
                self.logger.from_json(json.dumps(logs_data))
            ts = data.get("ts", "")
            if ts:
                self.log_panel.update_session_info(ts)
        self.log_panel.refresh()

    def try_auto_resume(self) -> None:
        data = session_manager.load_session()
        if data:
            ts = data.get("ts", "")
            if ts:
                self.log_panel.update_session_info(ts)

    def resume_session(self) -> None:
        data = session_manager.load_session()
        if not data:
            QMessageBox.information(self, "Reprendre", "Aucune session sauvegardée."); return

        uid_list  = data.get("uids", [])
        fp_map    = data.get("filepaths", {})
        flt_data  = data.get("filters", {})
        page      = data.get("page", "home")

        if not uid_list:
            QMessageBox.information(self, "Reprendre", "Session vide."); return

        unique_files = list({fp for fp in fp_map.values() if fp and os.path.exists(fp)})
        missing      = [fp for fp in fp_map.values() if fp and not os.path.exists(fp)]

        if unique_files:
            self.df_all = pd.DataFrame()
            self.summaries = {}
            self.loaded_uids = set()
            self.load_files(unique_files)

        if flt_data:
            try:
                self.filter_sidebar.restore_state(flt_data)
                self.apply_filters()
            except Exception as e:
                log_error("main_window.MainWindow.resume_session", e)
        self.nav(page if page in PAGES else "home")
        self.logger.log("resume", "Session restaurée")
        self.log_panel.refresh()

        msg = "Session restaurée avec succès."
        if missing:
            msg += f"\n\n⚠  {len(missing)} fichier(s) introuvable(s) :\n" + "\n".join(f"  • {os.path.basename(p)}" for p in missing[:8])
        QMessageBox.information(self, "Session restaurée", msg)

    def load_saved_prefs(self) -> None:
        try:
            prefs = session_manager.load_prefs()
            theme_name = prefs.get("theme_preset", "Arctic Ink (défaut)")
            from shared.constants import THEMES_PRESETS
            if theme_name and theme_name in THEMES_PRESETS:
                ThemeManager.instance().apply(theme_name, self.app)
                self.settings_page.current_theme = theme_name
        except Exception as e:
            log_error("main_window.MainWindow.load_saved_prefs", e)
        try:
            self.settings_page.restore_cursor()
        except Exception as e:
            log_error("main_window.MainWindow.load_saved_prefs", e)
