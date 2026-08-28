# Page comparaison : affiche plusieurs fichiers cote a cote ou fusionnes en un graphique

import os
import numpy as np
import pandas as pd

from PyQt6.QtWidgets import QWidget, QHBoxLayout, QVBoxLayout, QLabel, QPushButton, QCheckBox, QScrollArea, QGridLayout, QSizePolicy, QFileDialog, QMessageBox, QComboBox, QLineEdit, QFrame
from PyQt6.QtCore import Qt
from matplotlib.figure import Figure
from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg as FigureCanvas

from shared.constants import C, FAC_COLORS, CHART_3D_COMPATIBLE, COLUMN_LABELS, ZONES
from shared.scaling import S
from shared.logging.action_logger import ActionLogger
from presentation.theme.theme_manager import ThemeManager
from presentation.widgets.chart_controls import ChartControls
from presentation.widgets.primitives import PrimaryButton, StepWidget
from rendering.strategies.renderer_2d import render_chart, setup_dark_axes
from rendering.strategies.renderer_3d import render_chart_3d
from shared.logging.file_logger import log_error, log_msg


class ComparisonPage(QWidget):
    def __init__(self, df: pd.DataFrame, parent=None):
        super().__init__(parent)
        self.df = df if df is not None else pd.DataFrame()
        self.figs_canvases: list[tuple[Figure, FigureCanvas]] = []
        self.file_checks: dict[str, QCheckBox] = {}
        self.build_ui()
        ThemeManager.instance().theme_changed.connect(self.restyle)

    def build_ui(self) -> None:
        root = QHBoxLayout(self)
        root.setContentsMargins(0, 0, 0, 0)
        root.setSpacing(0)

        self.left = QWidget()
        left_w = max(round(S.dpi_scale * 210), 180)
        self.left.setFixedWidth(left_w)
        ll = QVBoxLayout(self.left)
        ll.setContentsMargins(0, 0, 0, 0)
        ll.setSpacing(0)

        hdr = QWidget()
        hdr.setMinimumHeight(S.header_h - S.spacing_md)
        hl = QHBoxLayout(hdr)
        hl.setContentsMargins(S.spacing_md, S.spacing_sm, S.spacing_sm, S.spacing_sm)
        hl.setSpacing(S.spacing_sm)
        self.hdr_lbl = QLabel("Fichiers")
        hl.addWidget(self.hdr_lbl, 1)
        self.btn_all  = QPushButton("✓")
        self.btn_none = QPushButton("✕")
        for b in (self.btn_all, self.btn_none):
            b.setMinimumHeight(S.btn_h_sm)
            b.setFixedWidth(round(S.dpi_scale * 36))
        self.btn_all.clicked.connect(self.sel_all)
        self.btn_none.clicked.connect(self.sel_none)
        hl.addWidget(self.btn_all)
        hl.addWidget(self.btn_none)
        ll.addWidget(hdr)
        ll.addWidget(self.sep())

        flt_bar = QWidget()
        flt_bar.setMinimumHeight(S.btn_h + S.spacing_md)
        fl = QVBoxLayout(flt_bar)
        fl.setContentsMargins(S.spacing_sm, S.spacing_sm, S.spacing_sm, S.spacing_sm // 2)
        fl.setSpacing(S.spacing_sm // 2)

        self.search_files = QLineEdit()
        self.search_files.setPlaceholderText("🔍 Filtrer fichiers…")
        self.search_files.setMinimumHeight(S.input_h)
        self.search_files.textChanged.connect(self.apply_file_filter)
        fl.addWidget(self.search_files)

        sort_row = QHBoxLayout()
        sort_row.setSpacing(S.spacing_sm // 2)
        sort_lbl = QLabel("Tri :")
        sort_lbl.setStyleSheet(f"color:{C['text_muted']};font-size:{S.font_sm}px;")
        sort_row.addWidget(sort_lbl)
        self.combo_sort = QComboBox()
        self.combo_sort.setMinimumHeight(S.input_h)
        for val, lbl in [("name", "Nom"), ("tco2_desc","CO2 ↓"), ("tco2_asc", "CO2 ↑"), ("etu_desc", "Étud. ↓"), ("etu_asc", "Étud. ↑")]:
            self.combo_sort.addItem(lbl, val)
        self.combo_sort.currentIndexChanged.connect(self.refresh_file_order)
        sort_row.addWidget(self.combo_sort, 1)
        fl.addLayout(sort_row)
        ll.addWidget(flt_bar)
        ll.addWidget(self.sep())

        scroll_l = QScrollArea()
        scroll_l.setWidgetResizable(True)
        scroll_l.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.fl_widget = QWidget()
        self.fl_lay = QVBoxLayout(self.fl_widget)
        self.fl_lay.setContentsMargins(S.spacing_sm, S.spacing_sm, S.spacing_sm, S.spacing_sm)
        self.fl_lay.setSpacing(S.spacing_sm // 2)
        self.fl_lay.addStretch()
        scroll_l.setWidget(self.fl_widget)
        ll.addWidget(scroll_l, 1)

        self.lbl_sel = QLabel("0 / 0")
        self.lbl_sel.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.lbl_sel.setMinimumHeight(S.spacing_lg + S.spacing_sm)
        ll.addWidget(self.lbl_sel)
        root.addWidget(self.left)

        right = QWidget()
        rl = QVBoxLayout(right)
        rl.setContentsMargins(0, 0, 0, 0)
        rl.setSpacing(0)

        self.controls = ChartControls(show_export=False)
        self.controls.changed.connect(self.refresh_all)

        try:
            row1_widget = self.controls.layout().itemAt(0).widget()
            row1_lay = row1_widget.layout()

            lbl_mode = QLabel("Mode :")
            lbl_mode.setStyleSheet(f"color:{C['text_muted']};font-size:{S.font_sm}px;")
            self.combo_mode = QComboBox()
            self.combo_mode.setMinimumHeight(S.input_h)
            self.combo_mode.setMinimumWidth(round(S.dpi_scale * 120))
            for val, lbl in [("grid", "Grille par fichier"), ("unified", "Graphe unifié"), ("side_by_side", "▤ Côte à côte"), ("stacked_by_file", "▦ Empilé par fichier")]:
                self.combo_mode.addItem(lbl, val)
            self.combo_mode.currentIndexChanged.connect(self.on_mode_changed)
            row1_lay.addWidget(lbl_mode)
            row1_lay.addWidget(self.combo_mode)

            lbl_c = QLabel("▲▼ Cols :")
            lbl_c.setStyleSheet(f"color:{C['accent']};font-size:{S.font_sm}px;font-weight:600;")
            self.spin_cols = StepWidget(lo=1, hi=5, val=2)
            self.spin_cols.setMinimumWidth(round(S.dpi_scale * 100))
            self.spin_cols.setMinimumHeight(S.input_h)
            self.spin_cols.valueChanged.connect(self.refresh_all)
            row1_lay.addWidget(lbl_c)
            row1_lay.addWidget(self.spin_cols)

            btn_exp = PrimaryButton("PNG", "⇓")
            btn_exp.setFixedHeight(S.btn_h_lg)
            btn_exp.clicked.connect(self.export_all)
            row1_lay.addWidget(btn_exp)
        except Exception as e:
            log_error("comparison_page.ComparisonPage.build_ui", e)
            self.combo_mode = QComboBox()
            self.combo_mode.addItem("Grille par fichier", "grid")
            self.combo_mode.addItem("Graphe unifié", "unified")
            self.combo_mode.addItem("▤ Côte à côte", "side_by_side")
            self.combo_mode.addItem("▦ Empilé par fichier", "stacked_by_file")
            self.combo_mode.currentIndexChanged.connect(self.on_mode_changed)
            self.spin_cols = StepWidget(lo=1, hi=5, val=2)
            self.spin_cols.valueChanged.connect(self.refresh_all)

        rl.addWidget(self.controls)

        self.grid_scroll = QScrollArea()
        self.grid_scroll.setWidgetResizable(True)
        self.grid_container = QWidget()
        self.grid_layout = QGridLayout(self.grid_container)
        self.grid_layout.setSpacing(S.spacing_md)
        self.grid_layout.setContentsMargins(S.spacing_md, S.spacing_md, S.spacing_md, S.spacing_md)
        self.grid_scroll.setWidget(self.grid_container)
        rl.addWidget(self.grid_scroll, 1)
        root.addWidget(right, 1)

        self.restyle()

    def update_data(self, df: pd.DataFrame) -> None:
        self.df = df
        self.refresh_file_list()
        self.refresh_all()

    def refresh_file_list(self) -> None:
        new_files = set(self.df["fichier"].unique()) if not self.df.empty else set()
        current   = set(self.file_checks.keys())
        for fname in current - new_files:
            cb = self.file_checks.pop(fname)
            cb.setParent(None); cb.deleteLater()
        for fname in sorted(new_files - current):
            ci = len(self.file_checks) % len(FAC_COLORS)
            fc = FAC_COLORS[ci]
            cb = QCheckBox(fname)
            cb.setChecked(True)
            cb.setToolTip(fname)
            cb.setMinimumHeight(S.btn_h_sm)
            cb.setStyleSheet(f"QCheckBox{{color:{fc};font-size:{S.font_sm}px;padding:{S.spacing_sm // 2}px;}}QCheckBox::indicator{{border:1px solid {fc};width:{round(S.dpi_scale*14)}px;height:{round(S.dpi_scale*14)}px;border-radius:{round(S.dpi_scale*3)}px;}}QCheckBox::indicator:checked{{background:{fc};border-color:{fc};}}QCheckBox:hover{{color:#ffffff;}}")
            cb.stateChanged.connect(self.on_toggle)
            self.file_checks[fname] = cb
            cnt = self.fl_lay.count()
            self.fl_lay.insertWidget(cnt - 1, cb)
        self.refresh_file_order()
        self.apply_file_filter()
        self.update_sel_lbl()

    def get_sorted_files(self) -> list[str]:
        sort_key = self.combo_sort.currentData() if hasattr(self, "combo_sort") else "name"
        files = list(self.file_checks.keys())
        if sort_key == "name":
            return sorted(files)
        if self.df.empty:
            return sorted(files)
        try:
            summary = self.df.groupby("fichier").agg(tco2=("total_tco2", lambda x: pd.to_numeric(x, errors="coerce").fillna(0).sum()), etu=("nb_etudiants", lambda x: pd.to_numeric(x, errors="coerce").fillna(0).sum()))
            if sort_key == "tco2_desc":
                order = summary["tco2"].sort_values(ascending=False).index
            elif sort_key == "tco2_asc":
                order = summary["tco2"].sort_values(ascending=True).index
            elif sort_key == "etu_desc":
                order = summary["etu"].sort_values(ascending=False).index
            elif sort_key == "etu_asc":
                order = summary["etu"].sort_values(ascending=True).index
            else:
                return sorted(files)
            sorted_known = [f for f in order if f in files]
            rest = [f for f in sorted(files) if f not in sorted_known]
            return sorted_known + rest
        except Exception as e:
            log_error("comparison_page.ComparisonPage.get_sorted_files", e)
            return sorted(files)

    def refresh_file_order(self) -> None:
        ordered = self.get_sorted_files()
        while self.fl_lay.count():
            item = self.fl_lay.takeAt(0)
            if item and item.widget():
                item.widget().hide()
        for fname in ordered:
            if fname in self.file_checks:
                cb = self.file_checks[fname]
                cb.show()
                self.fl_lay.addWidget(cb)
        self.fl_lay.addStretch()
        self.apply_file_filter()

    def apply_file_filter(self) -> None:
        txt = self.search_files.text().strip().lower() if hasattr(self, "search_files") else ""
        for fname, cb in self.file_checks.items():
            cb.setVisible(not txt or txt in fname.lower())
        self.update_sel_lbl()

    def on_toggle(self) -> None:
        self.update_sel_lbl()
        self.refresh_all()

    def update_sel_lbl(self) -> None:
        visible = [fname for fname, cb in self.file_checks.items() if cb.isVisible()]
        checked = sum(1 for fname in visible if self.file_checks[fname].isChecked())
        total   = len(self.file_checks)
        self.lbl_sel.setText(f"{checked} / {total}")

    def get_active(self) -> list[str]:
        ordered = self.get_sorted_files()
        return [f for f in ordered if f in self.file_checks and self.file_checks[f].isChecked()]

    def sel_all(self) -> None:
        for cb in self.file_checks.values():
            cb.blockSignals(True); cb.setChecked(True); cb.blockSignals(False)
        self.update_sel_lbl(); self.refresh_all()

    def sel_none(self) -> None:
        for cb in self.file_checks.values():
            cb.blockSignals(True); cb.setChecked(False); cb.blockSignals(False)
        self.update_sel_lbl(); self.refresh_all()

    def on_mode_changed(self) -> None:
        mode = self.combo_mode.currentData() if hasattr(self, "combo_mode") else "grid"
        if hasattr(self, "spin_cols"):
            self.spin_cols.setEnabled(mode == "grid")
        self.refresh_all()

    def clear_grid(self) -> None:
        for fig, canvas in self.figs_canvases:
            try: canvas.setParent(None); canvas.deleteLater()
            except Exception as e: log_error("comparison_page.ComparisonPage.clear_grid", e)
            try:
                import matplotlib.pyplot as plt; plt.close(fig)
            except Exception as e: log_error("comparison_page.ComparisonPage.clear_grid", e)
        self.figs_canvases.clear()
        while self.grid_layout.count():
            item = self.grid_layout.takeAt(0)
            if item.widget():
                try: item.widget().setParent(None)
                except Exception as e: log_error("comparison_page.ComparisonPage.clear_grid", e)

    def refresh_all(self) -> None:
        self.clear_grid()
        active = self.get_active()
        mode = self.combo_mode.currentData() if hasattr(self, "combo_mode") else "grid"

        if not active or self.df is None or self.df.empty:
            lbl = QLabel("Sélectionnez au moins un fichier pour afficher les graphiques.")
            lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
            lbl.setStyleSheet(f"color:{C['text_muted']};font-size:{S.font_base}px;background:transparent;")
            lbl.setWordWrap(True)
            self.grid_layout.addWidget(lbl, 0, 0)
            return

        ct     = self.controls.chart_type
        compat_warn = self.controls.mode_3d and ct not in CHART_3D_COMPATIBLE
        self.controls.set_compat_msg(f"ℹ  «{ct}» affiché en 2D" if compat_warn else "")

        if mode == "stacked_by_file":
            self.render_stacked_by_file(active, ct)
        elif mode == "side_by_side":
            self.render_side_by_side(active, ct)
        elif mode == "unified":
            self.render_unified(active, ct)
        else:
            self.render_grid(active, ct)

    def render_stacked_by_file(self, active: list[str], ct: str) -> None:
        if ct not in ("bar", "barh"):
            self.render_unified(active, ct)
            return
        if self.df is None or self.df.empty:
            return

        x_col = self.controls.x_col
        y_col = self.controls.y_col
        top_n = self.controls.top_n
        mode_3d = self.controls.mode_3d

        if x_col in ("zone", "zone_label"):
            seg_vals   = [ZONES[z]["label"] for z in sorted(ZONES.keys())]
            seg_colors = [ZONES[z]["color"]  for z in sorted(ZONES.keys())]
        elif x_col in ("sheet_id", "faculte_uid"):
            seg_vals   = sorted(self.df["sheet_id"].unique())
            seg_colors = [FAC_COLORS[i % len(FAC_COLORS)] for i in range(len(seg_vals))]
        else:
            seg_vals   = list(self.df.groupby("pays")[y_col].sum().nlargest(top_n).index)
            seg_colors = [FAC_COLORS[i % len(FAC_COLORS)] for i in range(len(seg_vals))]

        if not seg_vals:
            return

        file_data: dict[str, np.ndarray] = {}
        for fname in active:
            sub = self.df[self.df["fichier"] == fname]
            if x_col in ("zone", "zone_label"):
                agg = sub.groupby("zone_label")[y_col].sum()
            elif x_col in ("sheet_id", "faculte_uid"):
                agg = sub.groupby("sheet_id")[y_col].sum()
            else:
                agg = sub.groupby("pays")[y_col].sum()
            vals = np.array([float(pd.to_numeric(agg.get(sv, 0), errors="coerce") or 0) for sv in seg_vals])
            file_data[fname] = vals

        dpi = max(80, round(96 * S.dpi_scale * 0.85))
        wrapper = QWidget()
        wl = QVBoxLayout(wrapper)
        wl.setContentsMargins(S.spacing_sm, S.spacing_sm, S.spacing_sm, S.spacing_sm)
        wl.setSpacing(S.spacing_sm // 2)

        names_str = ", ".join(f[:18] for f in active[:4])
        if len(active) > 4:
            names_str += f"… (+{len(active)-4})"
        title_lbl = QLabel(f"  ▦ Empilé par fichier — {names_str}")
        title_lbl.setWordWrap(True)
        title_lbl.setStyleSheet(f"background:{C['bg_card']};color:{C['accent']};font-weight:700;font-size:{S.font_base}px;border-radius:{S.r_sm()};padding:{S.spacing_sm // 2}px {S.spacing_sm}px;border-left:3px solid {C['accent']};")
        wl.addWidget(title_lbl)

        fig = Figure(figsize=(10, 6), dpi=dpi)
        fig.patch.set_facecolor(C["bg_base"])
        canvas = FigureCanvas(fig)
        canvas.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        canvas.setMinimumHeight(round(S.dpi_scale * 350))

        try:
            if mode_3d and ct in CHART_3D_COMPATIBLE:
                self.render_stacked_3d(fig, active, file_data, seg_vals, seg_colors, x_col, y_col, ct)
            else:
                ax = fig.add_subplot(111)
                setup_dark_axes(ax, fig)

                x_pos   = np.arange(len(active))
                bar_w   = min(0.65, 0.9 / max(len(active), 1))
                all_files = list(self.file_checks.keys())
                short_names = [os.path.splitext(f)[0][:18] for f in active]

                bottom_arr = np.zeros(len(active))
                for vi, (sv, sc) in enumerate(zip(seg_vals, seg_colors)):
                    vals = np.array([file_data[f][vi] for f in active])

                    if ct == "barh":
                        bars = ax.barh(x_pos, vals, bar_w, left=bottom_arr, label=str(sv)[:22], color=sc, edgecolor=C["bg_base"], linewidth=0.5)
                    else:
                        bars = ax.bar(x_pos, vals, bar_w, bottom=bottom_arr, label=str(sv)[:22], color=sc, edgecolor=C["bg_base"], linewidth=0.5)

                    total_max = max((file_data[f].sum() for f in active), default=1) or 1
                    for bar, val, bot in zip(bars, vals, bottom_arr):
                        if val >= total_max * 0.06:
                            try:
                                if ct == "barh":
                                    ax.text(bot + val / 2, bar.get_y() + bar.get_height() / 2, f"{val:.1f}", ha="center", va="center", fontsize=max(6, S.font_tiny - 1), fontweight="bold", color="white")
                                else:
                                    ax.text(bar.get_x() + bar.get_width() / 2, bot + val / 2, f"{val:.1f}", ha="center", va="center", fontsize=max(6, S.font_tiny - 1), fontweight="bold", color="white")
                            except Exception as e:
                                log_error("comparison_page.ComparisonPage.render_stacked_by_file", e)
                    bottom_arr += vals

                if ct == "barh":
                    ax.set_yticks(x_pos)
                    ax.set_yticklabels(short_names, fontsize=S.font_tiny)
                    ax.set_xlabel(COLUMN_LABELS.get(y_col, y_col), fontsize=S.font_tiny)
                    fig.subplots_adjust(left=0.28)
                else:
                    ax.set_xticks(x_pos)
                    rot = 25 if len(active) > 3 else 0
                    ha  = "right" if rot > 0 else "center"
                    ax.set_xticklabels(short_names, rotation=rot, ha=ha, fontsize=S.font_tiny)
                    ax.set_ylabel(COLUMN_LABELS.get(y_col, y_col), fontsize=S.font_tiny)
                    if rot > 0:
                        fig.subplots_adjust(bottom=0.22)

                ax.legend(fontsize=S.font_tiny, facecolor=C["bg_elevated"], edgecolor=C["border"], labelcolor=C["text_primary"], title=COLUMN_LABELS.get(x_col, x_col), loc="best")
                ax.set_title(f"Répartition {COLUMN_LABELS.get(y_col, y_col)} par fichier — par {COLUMN_LABELS.get(x_col, x_col)}", fontsize=S.font_sm, pad=12)
                fig.tight_layout(pad=2.0)

        except Exception as e:
            try:
                fig.clear()
                ax = fig.add_subplot(111)
                setup_dark_axes(ax, fig)
                ax.text(0.5, 0.5, f"Erreur empilé par fichier :\n{e}", ha="center", va="center", color=C["red"], fontsize=9)
            except Exception as e2:
                log_error("comparison_page.ComparisonPage.render_stacked_by_file", e2)
        canvas.draw()
        wl.addWidget(canvas, 1)
        wrapper.setStyleSheet(f"background:{C['bg_elevated']};border-radius:{S.r_md()};border:1px solid {C['border']};")
        self.grid_layout.addWidget(wrapper, 0, 0)
        self.figs_canvases.append((fig, canvas))

    def render_stacked_3d(self, fig, active, file_data, seg_vals, seg_colors, x_col, y_col, ct) -> None:
        try:
            from rendering.geometry.cube_3d import build_cube_faces, draw_cubes_batch, cube_center
            from rendering.strategies.renderer_3d import setup_3d_axes, finalize_3d_layout

            ax = fig.add_subplot(111, projection="3d")
            setup_3d_axes(ax, fig)
            ax.view_init(elev=self.controls.elev, azim=self.controls.azim)

            cubes: list = []
            dx, dy = 0.60, 0.45

            for fi, fname in enumerate(active):
                z_base = 0.0
                for vi, (sv, sc) in enumerate(zip(seg_vals, seg_colors)):
                    dz = float(file_data[fname][vi])
                    if dz <= 0:
                        z_base += dz
                        continue
                    v, c = build_cube_faces(fi, 0, z_base, dx, dy, dz, sc)
                    cubes.append((v, c, cube_center(fi, 0, z_base, dx, dy, dz)))
                    z_base += dz

            draw_cubes_batch(ax, cubes)

            short_names = [os.path.splitext(f)[0][:14] for f in active]
            ax.set_xticks(np.arange(len(active)) + dx / 2)
            ax.set_xticklabels(short_names, rotation=10, ha="right", fontsize=max(6, S.font_tiny - 1))
            # stacked totals can dwarf the bar footprint -- flatten z so the
            # tallest stack doesn't render as a flat wall hiding the others
            ax.set_box_aspect((1.6, 1.2, 0.65), zoom=1.15)
            ax.set_zlabel(COLUMN_LABELS.get(y_col, y_col), labelpad=12, fontsize=S.font_tiny)
            ax.set_zlim(bottom=0)

            import matplotlib.patches as mpatches
            handles = [mpatches.Patch(color=sc, label=str(sv)[:22]) for sv, sc in zip(seg_vals, seg_colors)]
            ax.legend(handles=handles, fontsize=max(S.font_tiny - 1, 7), facecolor=C["bg_elevated"], edgecolor=C["border"], labelcolor=C["text_primary"], loc="upper left", bbox_to_anchor=(-0.05, 1.0), title=COLUMN_LABELS.get(x_col, x_col))

            ax.set_title(f"[3D] Empilé par fichier — {COLUMN_LABELS.get(y_col, y_col)}", fontsize=S.font_sm, pad=28, fontweight="bold", color=C["text_primary"])
            finalize_3d_layout(fig)
        except Exception as e:
            try:
                fig.clear()
                ax = fig.add_subplot(111)
                setup_dark_axes(ax, fig)
                ax.text(0.5, 0.5, f"Erreur 3D empilé :\n{e}", ha="center", va="center", color=C["red"], fontsize=9)
            except Exception as e2:
                log_error("comparison_page.ComparisonPage.render_stacked_3d", e2)

    def render_side_by_side(self, active: list[str], ct: str) -> None:
        if ct not in ("bar", "barh"):
            self.render_unified(active, ct)
            return
        if self.df is None or self.df.empty:
            return

        x_col  = self.controls.x_col
        y_col  = self.controls.y_col
        top_n  = self.controls.top_n

        if x_col in ("zone", "zone_label"):
            x_vals = [ZONES[z]["label"] for z in sorted(ZONES.keys())]
        elif x_col in ("sheet_id", "faculte_uid"):
            x_vals = sorted(self.df["sheet_id"].unique())
        else:
            x_vals = list(self.df.groupby("pays")[y_col].sum().nlargest(top_n).index)
        if not x_vals:
            return

        file_agg: dict[str, list[float]] = {}
        for fname in active:
            sub = self.df[self.df["fichier"] == fname]
            if x_col in ("zone", "zone_label"):
                agg = sub.groupby("zone_label")[y_col].sum()
            elif x_col in ("sheet_id", "faculte_uid"):
                agg = sub.groupby("sheet_id")[y_col].sum()
            else:
                agg = sub.groupby("pays")[y_col].sum()
            file_agg[fname] = [float(pd.to_numeric(agg.get(xv, 0), errors="coerce") or 0) for xv in x_vals]

        dpi = max(80, round(96 * S.dpi_scale * 0.85))
        wrapper = QWidget()
        wl = QVBoxLayout(wrapper)
        wl.setContentsMargins(S.spacing_sm, S.spacing_sm, S.spacing_sm, S.spacing_sm)
        wl.setSpacing(S.spacing_sm // 2)

        names_str = ", ".join(f[:18] for f in active[:5])
        if len(active) > 5:
            names_str += f"… (+{len(active)-5})"
        title_lbl = QLabel(f"  ▤ Côte à côte — {names_str}")
        title_lbl.setWordWrap(True)
        title_lbl.setStyleSheet(f"background:{C['bg_card']};color:{C['accent']};font-weight:700;font-size:{S.font_base}px;border-radius:{S.r_sm()};padding:{S.spacing_sm // 2}px {S.spacing_sm}px;border-left:3px solid {C['accent']};")
        wl.addWidget(title_lbl)

        fig = Figure(figsize=(10, 6), dpi=dpi)
        fig.patch.set_facecolor(C["bg_base"])
        canvas = FigureCanvas(fig)
        canvas.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        canvas.setMinimumHeight(round(S.dpi_scale * 350))

        try:
            ax = fig.add_subplot(111)
            setup_dark_axes(ax, fig)

            n     = len(active)
            x_pos = np.arange(len(x_vals))
            bar_w = min(0.8 / max(n, 1), 0.28)
            all_files = list(self.file_checks.keys())

            for i, fname in enumerate(active):
                ci     = (all_files.index(fname) if fname in all_files else i) % len(FAC_COLORS)
                color  = FAC_COLORS[ci]
                vals   = file_agg[fname]
                offset = (i - n / 2 + 0.5) * bar_w
                short  = os.path.splitext(fname)[0][:22]

                if ct == "barh":
                    bars = ax.barh(x_pos + offset, vals, bar_w, label=short, color=color, edgecolor=C["bg_base"], linewidth=0.7)
                    ax.bar_label(bars, fmt="%.1f", padding=3, fontsize=max(6, S.font_tiny - 1), color=C["text_secondary"])
                else:
                    bars = ax.bar(x_pos + offset, vals, bar_w, label=short, color=color, edgecolor=C["bg_base"], linewidth=0.7)
                    ax.bar_label(bars, fmt="%.1f", padding=3, fontsize=max(6, S.font_tiny - 1), color=C["text_secondary"])

            short_xvals = [str(xv)[:14] for xv in x_vals]
            if ct == "barh":
                ax.set_yticks(x_pos)
                ax.set_yticklabels(short_xvals, fontsize=S.font_tiny)
                ax.set_xlabel(COLUMN_LABELS.get(y_col, y_col), fontsize=S.font_tiny)
                fig.subplots_adjust(left=0.28)
            else:
                ax.set_xticks(x_pos)
                ax.set_xticklabels(short_xvals, rotation=28, ha="right", fontsize=S.font_tiny)
                ax.set_ylabel(COLUMN_LABELS.get(y_col, y_col), fontsize=S.font_tiny)
                fig.subplots_adjust(bottom=0.22)

            ax.legend(fontsize=S.font_tiny, facecolor=C["bg_elevated"], edgecolor=C["border"], labelcolor=C["text_primary"], loc="best")
            ax.set_title(f"{COLUMN_LABELS.get(y_col, y_col)} par fichier — {COLUMN_LABELS.get(x_col, x_col)}", fontsize=S.font_sm, pad=12)
            fig.tight_layout(pad=2.0)
        except Exception as e:
            try:
                fig.clear()
                ax = fig.add_subplot(111)
                setup_dark_axes(ax, fig)
                ax.text(0.5, 0.5, f"Erreur côte à côte :\n{e}", ha="center", va="center", color=C["red"], fontsize=9)
            except Exception as e2:
                log_error("comparison_page.ComparisonPage.render_side_by_side", e2)
        canvas.draw()
        wl.addWidget(canvas, 1)
        wrapper.setStyleSheet(f"background:{C['bg_elevated']};border-radius:{S.r_md()};border:1px solid {C['border']};")
        self.grid_layout.addWidget(wrapper, 0, 0)
        self.figs_canvases.append((fig, canvas))

    def render_unified(self, active: list[str], ct: str) -> None:
        merged = self.df[self.df["fichier"].isin(active)].copy()
        if merged.empty:
            return

        all_files = list(self.file_checks.keys())
        dpi = max(80, round(96 * S.dpi_scale * 0.85))

        wrapper = QWidget()
        wl = QVBoxLayout(wrapper)
        wl.setContentsMargins(S.spacing_sm, S.spacing_sm, S.spacing_sm, S.spacing_sm)
        wl.setSpacing(S.spacing_sm // 2)

        names_str = ", ".join(f[:20] for f in active[:4])
        if len(active) > 4:
            names_str += f"… (+{len(active)-4})"
        title_lbl = QLabel(f"  Graphe unifié — {names_str}")
        title_lbl.setStyleSheet(f"background:{C['bg_card']};color:{C['accent']};font-weight:700;font-size:{S.font_base}px;border-radius:{S.r_sm()};padding:{S.spacing_sm // 2}px {S.spacing_sm}px;border-left:3px solid {C['accent']};")
        title_lbl.setWordWrap(True)
        wl.addWidget(title_lbl)

        try:
            n_etu  = int(pd.to_numeric(merged["nb_etudiants"], errors="coerce").fillna(0).sum())
            tco2   = pd.to_numeric(merged["total_tco2"], errors="coerce").fillna(0.0).sum()
            n_pays = merged["pays"].nunique()
            stat_lbl = QLabel(f"  {n_etu:,} ét.  ·  {tco2:.1f} tCO2e  ·  {n_pays} pays  ·  {len(active)} fichiers")
            stat_lbl.setStyleSheet(f"color:{C['text_muted']};font-size:{S.font_sm}px;background:transparent;padding:0 {S.spacing_sm}px;")
            wl.addWidget(stat_lbl)
        except Exception as e:
            log_error("comparison_page.ComparisonPage.render_unified", e)
        fig = Figure(figsize=(10, 6), dpi=dpi)
        fig.patch.set_facecolor(C["bg_base"])
        canvas = FigureCanvas(fig)
        canvas.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        canvas.setMinimumHeight(round(S.dpi_scale * 350))

        try:
            if self.controls.mode_3d:
                render_chart_3d(fig, merged, ct, self.controls.x_col, self.controls.y_col, self.controls.group_col, self.controls.top_n, elev=self.controls.elev, azim=self.controls.azim)
            else:
                render_chart(fig, merged, ct, self.controls.x_col, self.controls.y_col, self.controls.group_col, self.controls.top_n)
        except Exception as e:
            try:
                ax = fig.add_subplot(111)
                setup_dark_axes(ax, fig)
                ax.text(0.5, 0.5, f"Erreur :\n{e}", ha="center", va="center", color=C["red"], fontsize=9)
            except Exception as e2:
                log_error("comparison_page.ComparisonPage.render_unified", e2)
        canvas.draw()
        wl.addWidget(canvas, 1)
        wrapper.setStyleSheet(f"background:{C['bg_elevated']};border-radius:{S.r_md()};border:1px solid {C['border']};")
        self.grid_layout.addWidget(wrapper, 0, 0)
        self.figs_canvases.append((fig, canvas))

    def render_grid(self, active: list[str], ct: str) -> None:
        n_cols = max(1, self.spin_cols.value())
        all_files = list(self.file_checks.keys())
        dpi = max(72, round(90 * S.dpi_scale * 0.80))

        for idx, fname in enumerate(active):
            try:
                sub_df = self.df[self.df["fichier"] == fname].copy()
                row, col = divmod(idx, n_cols)
                ci = (all_files.index(fname) if fname in all_files else idx) % len(FAC_COLORS)
                fc = FAC_COLORS[ci]

                wrapper = QWidget()
                wl = QVBoxLayout(wrapper)
                wl.setContentsMargins(S.spacing_sm, S.spacing_sm, S.spacing_sm, S.spacing_sm)
                wl.setSpacing(S.spacing_sm // 2)

                title_lbl = QLabel(f"  {fname}")
                title_lbl.setStyleSheet(f"background:{C['bg_card']};color:{fc};font-weight:700;font-size:{S.font_base}px;border-radius:{S.r_sm()};padding:{S.spacing_sm // 2}px {S.spacing_sm}px;border-left:3px solid {fc};")
                wl.addWidget(title_lbl)

                if not sub_df.empty:
                    try:
                        n_etu  = int(pd.to_numeric(sub_df["nb_etudiants"], errors="coerce").fillna(0).sum())
                        tco2   = pd.to_numeric(sub_df["total_tco2"], errors="coerce").fillna(0.0).sum()
                        n_pays = sub_df["pays"].nunique()
                        sub_stat = QLabel(f"  {n_etu:,} ét.  ·  {tco2:.1f} tCO2e  ·  {n_pays} pays")
                        sub_stat.setStyleSheet(f"color:{C['text_muted']};font-size:{S.font_sm}px;background:transparent;padding:0 {S.spacing_sm}px;")
                        wl.addWidget(sub_stat)
                    except Exception as e:
                        log_error("comparison_page.ComparisonPage.render_grid", e)
                fig = Figure(figsize=(5.5, 3.8), dpi=dpi)
                fig.patch.set_facecolor(C["bg_base"])
                canvas = FigureCanvas(fig)
                canvas.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
                canvas.setMinimumHeight(round(S.dpi_scale * 250))

                try:
                    if self.controls.mode_3d:
                        render_chart_3d(fig, sub_df, ct, self.controls.x_col, self.controls.y_col, self.controls.group_col, self.controls.top_n, elev=self.controls.elev, azim=self.controls.azim)
                    else:
                        render_chart(fig, sub_df, ct, self.controls.x_col, self.controls.y_col, self.controls.group_col, self.controls.top_n)
                except Exception as e:
                    try:
                        ax = fig.add_subplot(111)
                        setup_dark_axes(ax, fig)
                        ax.text(0.5, 0.5, f"Erreur :\n{e}", ha="center", va="center", color=C["red"], fontsize=9)
                    except Exception as e2:
                        log_error("comparison_page.ComparisonPage.render_grid", e2)
                canvas.draw()
                wl.addWidget(canvas, 1)
                wrapper.setStyleSheet(f"background:{C['bg_elevated']};border-radius:{S.r_md()};border:1px solid {C['border']};")
                self.grid_layout.addWidget(wrapper, row, col)
                self.figs_canvases.append((fig, canvas))
            except Exception as e:
                log_error("comparison_page.ComparisonPage.render_grid", e)
                continue

    def export_all(self) -> None:
        if not self.figs_canvases:
            QMessageBox.information(self, "Export", "Aucun graphique à exporter.")
            return
        folder = QFileDialog.getExistingDirectory(self, "Dossier d'export")
        if not folder:
            return
        active = self.get_active(); exported = 0
        for i, (fig, _) in enumerate(self.figs_canvases):
            try:
                label = active[i] if i < len(active) else f"graph_{i+1}"
                safe  = "".join(c if c.isalnum() or c in "-_." else "_" for c in label)
                path  = os.path.join(folder, f"compar_{safe}.png")
                fig.savefig(path, dpi=150, bbox_inches="tight", facecolor=C["bg_base"])
                exported += 1
            except Exception as e:
                log_error("comparison_page.ComparisonPage.export_all", e)
        ActionLogger.instance().log("export_png", f"{exported} graphiques → {folder}")
        QMessageBox.information(self, "Export", f"{exported} graphique(s) exporté(s).")

    def sep(self) -> QFrame:
        sep = QFrame()
        sep.setFrameShape(QFrame.Shape.HLine)
        sep.setStyleSheet(f"background:{C['border']};border:none;")
        sep.setFixedHeight(1)
        return sep

    def restyle(self) -> None:
        self.left.setStyleSheet(f"background:{C['bg_deep']};border-right:1px solid {C['border']};")
        if hasattr(self, "hdr_lbl"):
            self.hdr_lbl.setStyleSheet(f"font-size:{S.font_base + 1}px;font-weight:700;color:{C['text_primary']};background:transparent;")
        if hasattr(self, "btn_all"):
            self.btn_all.setStyleSheet(f"QPushButton{{background:{C['accent_dim']};color:{C['accent']};border:1px solid {C['accent']};border-radius:{S.r_sm()};font-size:{S.font_sm}px;font-weight:700;min-height:{S.btn_h_sm}px;}}QPushButton:hover{{background:{C['accent']};color:{C['bg_deep']};}}")
        if hasattr(self, "btn_none"):
            self.btn_none.setStyleSheet(f"QPushButton{{background:transparent;color:{C['text_muted']};border:1px solid {C['border']};border-radius:{S.r_sm()};font-size:{S.font_sm}px;min-height:{S.btn_h_sm}px;}}QPushButton:hover{{background:{C['bg_hover']};color:{C['red']};border-color:{C['red']};}}")
        if hasattr(self, "lbl_sel"):
            self.lbl_sel.setStyleSheet(f"color:{C['text_muted']};font-size:{S.font_sm}px;background:{C['bg_deep']};border-top:1px solid {C['border']};")
        if hasattr(self, "grid_container"):
            self.grid_container.setStyleSheet(f"background:{C['bg_base']};")
        if hasattr(self, "search_files"):
            self.search_files.setStyleSheet(f"QLineEdit{{background:{C['bg_input']};color:{C['text_secondary']};border:1px solid {C['border']};border-radius:{S.r_sm()};padding:{S.spacing_sm // 2}px {S.spacing_sm}px;font-size:{S.font_sm}px;min-height:{S.input_h}px;}}QLineEdit:focus{{border-color:{C['accent']};}}")
        try:
            self.refresh_all()
        except Exception as e:
            log_error("comparison_page.ComparisonPage.restyle", e)
