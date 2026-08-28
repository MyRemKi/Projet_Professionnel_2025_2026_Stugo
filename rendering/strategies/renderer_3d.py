# Dessine les graphiques en volume (3D) : barres-cubes, camemberts en volume, aires

import numpy as np
import matplotlib.patches as mpatches
from matplotlib.figure import Figure

from shared.constants import C, ZONES, FAC_COLORS, COLUMN_LABELS, CHART_3D_COMPATIBLE, PRES_ZONE_COLORS
from shared.color_utils import hex_to_rgb
from shared.scaling import S
from rendering.geometry.cube_3d import build_cube_faces, draw_cubes_batch, cube_center
from rendering.geometry.pie_3d import build_pie3d_faces, draw_pie3d_all
from rendering.strategies.renderer_2d import render_chart, setup_dark_axes
from shared.logging.file_logger import log_error


def setup_3d_axes(ax, fig):
    try:
        fig.patch.set_facecolor(C["bg_base"])
        ax.set_facecolor(C["bg_elevated"])
        for pane, fc in [(ax.xaxis.pane, C["bg_card"]), (ax.yaxis.pane, C["bg_elevated"]), (ax.zaxis.pane, C["bg_card"])]:
            pane.fill = True; pane.set_facecolor(fc)
            pane.set_edgecolor(C["border"]); pane.set_linewidth(0.4)
        ax.grid(True, linestyle="--", linewidth=0.3, alpha=0.4, color=C["border_light"])
        # pad is deliberately generous: with rotated tick labels close in, a
        # tight pad makes the labels overlap the axis panes / bar faces
        ax.tick_params(axis="both", labelsize=max(6, S.font_tiny-1), pad=7, colors=C["text_secondary"])
        for spine in [ax.xaxis, ax.yaxis, ax.zaxis]:
            spine.label.set_color(C["text_secondary"])
            spine.labelpad = 10
        zoom_3d_axes(ax)
    except Exception: pass


def zoom_3d_axes(ax, zoom=1.2):
    # mplot3d leaves a lot of empty space around the data by default; zoom
    # in on the box so the chart fills its card instead of looking tiny and
    # lost in the middle of it.
    try:
        ax.set_box_aspect(ax.get_box_aspect(), zoom=zoom)
    except Exception:
        try: ax.dist = 7.5
        except Exception: pass


def finalize_3d_layout(fig):
    # fig.tight_layout() has no reliable effect on 3D axes (matplotlib does not
    # compute their true extent), so it was silently leaving too little room
    # for the title/legend/tick labels and letting them overlap the plot.
    # Fixed margins give consistent breathing room instead.
    try:
        fig.subplots_adjust(top=0.90, bottom=0.16, left=0.04, right=0.96)
    except Exception: pass


def render_chart_3d(fig, df, chart_type, x_col, y_col, group_col, top_n, elev=28, azim=-48):
    try:
        fig.clear()
        if df is None or df.empty:
            ax = fig.add_subplot(111); setup_dark_axes(ax, fig)
            ax.text(0.5, 0.5, "Aucune donnee", ha="center", va="center", fontsize=S.font_base, color=C["text_muted"]); return
        if chart_type not in CHART_3D_COMPATIBLE:
            render_chart(fig, df, chart_type, x_col, y_col, group_col, top_n)
            fig.text(0.5, 0.01, f"info  {chart_type!r} - affichage 2D", ha="center", fontsize=S.font_tiny, color=C["yellow"], bbox=dict(boxstyle="round,pad=0.3", fc=C["bg_elevated"], ec=C["border"], alpha=0.9))
            return
        fac_list  = sorted(df["sheet_id"].unique())
        fac_color = {f: FAC_COLORS[i % len(FAC_COLORS)] for i, f in enumerate(fac_list)}
        zone_color = {z: v["color"] for z, v in ZONES.items()}
        if chart_type in ("pie", "donut"):
            render_pie_3d(fig, df, chart_type, x_col, y_col, top_n, fac_color, zone_color, elev, azim)
            return
        ax = fig.add_subplot(111, projection="3d")
        setup_3d_axes(ax, fig); ax.view_init(elev=elev, azim=azim)
        BAR_DX, BAR_DY = 0.55, 0.45
        if chart_type in ("bar", "barh"):
            render_bar_3d(ax, df, x_col, y_col, top_n, fac_color, zone_color, BAR_DX, BAR_DY)
            try:
                # bars are narrow in x/y but can reach far in z (values can be
                # 100x the bar footprint) -- without flattening the z aspect
                # the tallest bars render as flat opaque "walls" that hide
                # everything behind them instead of looking like bars
                ax.set_box_aspect((1.6, 1.2, 0.65), zoom=1.15)
                ax.set_zlabel(COLUMN_LABELS.get(y_col, y_col), labelpad=12, fontsize=S.font_tiny)
                ax.set_title(f"[3D] {COLUMN_LABELS.get(y_col, y_col)} par {COLUMN_LABELS.get(x_col, x_col)}", fontsize=S.font_sm, pad=28, fontweight="bold", color=C["text_primary"])
            except Exception: pass
        elif chart_type == "area":
            render_area_3d(ax, df, x_col, y_col, fac_color)
        try: ax.set_zlim(bottom=0)
        except Exception: pass
        finalize_3d_layout(fig)
    except Exception as e:
        try:
            fig.clear(); ax = fig.add_subplot(111); setup_dark_axes(ax, fig)
            ax.text(0.5, 0.5, f"Erreur rendu 3D:\n{e}", ha="center", va="center", fontsize=S.font_sm, color=C["red"], wrap=True)
        except Exception: pass


def render_pie_3d(fig, df, chart_type, x_col, y_col, top_n, fac_color, zone_color, elev, azim):
    try:
        if x_col in ("zone", "zone_label"):
            agg = df.groupby("zone_label")[y_col].sum(); agg = agg[agg > 0]
            zone_ids = [z for z in ZONES if ZONES[z]["label"] in agg.index]
            colors = [ZONES[z]["color"] for z in zone_ids]
            labels = [ZONES[z]["label"] for z in zone_ids]
            values = [float(agg.get(ZONES[z]["label"], 0)) for z in zone_ids]
        elif x_col in ("sheet_id", "faculte_uid"):
            agg = df.groupby("sheet_id")[y_col].sum(); agg = agg[agg > 0]
            colors = [fac_color.get(f, "#888") for f in agg.index]
            labels = list(agg.index); values = [float(v) for v in agg.values]
        else:
            agg = df.groupby("pays")[y_col].sum().nlargest(top_n); agg = agg[agg > 0]
            colors = FAC_COLORS[:len(agg)]; labels = list(agg.index)
            values = [float(v) for v in agg.values]
        total = sum(values)
        if total == 0: return
        pcts = [v / total * 100 for v in values]
        ax = fig.add_subplot(111, projection="3d")
        try:
            fig.patch.set_facecolor(C["bg_base"]); ax.set_facecolor(C["bg_elevated"])
            ax.view_init(elev=elev, azim=azim); ax.set_axis_off()
            zoom_3d_axes(ax, zoom=1.6)
        except Exception: pass
        wedges = []
        max_pct = max(pcts) if pcts else 0
        cum = 90.0
        for i, pct in enumerate(pcts):
            theta1 = cum; theta2 = theta1 + pct / 100 * 360
            cum = theta2
            if pct <= 0: continue
            explode = 0.08 if pct == max_pct else 0.0
            v, c_, center = build_pie3d_faces(theta1, theta2, colors[i], explode=explode)
            wedges.append((v, c_, center))
        # draw_pie3d_all sorts wedges back-to-front itself, using the actual
        # camera direction, so no manual angle-based ordering is needed here
        draw_pie3d_all(ax, wedges)
        ax.set_xlim(-1.6, 1.6); ax.set_ylim(-1.6, 1.6); ax.set_zlim(-0.1, 0.65)
        handles = [mpatches.Patch(color=colors[i], label=f"{labels[i][:24]}  {pcts[i]:.1f}%  ({values[i]:.1f})") for i in range(len(colors)) if pcts[i] > 0]
        if handles:
            try:
                ax.legend(handles=handles, fontsize=max(S.font_tiny-1, 7), loc="upper left", bbox_to_anchor=(-0.05, 1.0), framealpha=1.0, facecolor=C["bg_elevated"], edgecolor=C["border"], labelcolor=C["text_primary"], ncol=1)
            except Exception: pass
        suffix = " (Donut)" if chart_type == "donut" else ""
        try:
            ax.set_title(f"Repartition {COLUMN_LABELS.get(y_col, y_col)}{suffix} [3D]", fontsize=S.font_sm, pad=32, fontweight="bold", color=C["text_primary"])
        except Exception: pass
        finalize_3d_layout(fig)
    except Exception as e:
        try:
            ax = fig.add_subplot(111); setup_dark_axes(ax, fig)
            ax.text(0.5, 0.5, f"Erreur camembert 3D:\n{e}", ha="center", va="center", color=C["red"], fontsize=9)
        except Exception: pass


def render_bar_3d(ax, df, x_col, y_col, top_n, fac_color, zone_color, dx, dy):
    try:
        cubes = []
        if x_col in ("zone", "zone_label"):
            agg = df.groupby("zone_label")[y_col].sum().sort_values(ascending=False)
            for i, (lbl, val) in enumerate(agg.items()):
                z_id = next((k for k, v in ZONES.items() if v["label"] == lbl), i+1)
                color = zone_color.get(z_id, "#888")
                v, c = build_cube_faces(i, 0, 0, dx, dy, float(val), color)
                cubes.append((v, c, cube_center(i, 0, 0, dx, dy, float(val))))
            draw_cubes_batch(ax, cubes)
            ax.set_xticks(np.arange(len(agg)) + dx/2)
            ax.set_xticklabels([f"{l.split(':')[0][:10]}" for l in agg.index], rotation=15, ha="right", fontsize=max(6, S.font_tiny-1))
        elif x_col in ("sheet_id", "faculte_uid"):
            agg = df.groupby("sheet_id")[y_col].sum()
            for i, (fac, val) in enumerate(agg.items()):
                color = fac_color.get(fac, "#888")
                v, c = build_cube_faces(i, 0, 0, dx, dy, float(val), color)
                cubes.append((v, c, cube_center(i, 0, 0, dx, dy, float(val))))
            draw_cubes_batch(ax, cubes)
            ax.set_xticks(np.arange(len(agg)) + dx/2)
            ax.set_xticklabels([f[:8] for f in agg.index], rotation=15, ha="right", fontsize=max(6, S.font_tiny-1))
        elif x_col == "pays":
            agg = df.groupby("pays")[y_col].sum().nlargest(top_n)
            for i, (pays, val) in enumerate(agg.items()):
                sub = df[df["pays"] == pays]; mode_fac = sub["sheet_id"].mode()
                color = fac_color.get(mode_fac.iloc[0] if len(mode_fac) else "", "#888")
                v, c = build_cube_faces(i, 0, 0, dx, dy, float(val), color)
                cubes.append((v, c, cube_center(i, 0, 0, dx, dy, float(val))))
            draw_cubes_batch(ax, cubes)
            ax.set_xticks(np.arange(len(agg)) + dx/2)
            ax.set_xticklabels([f"{p[:8]}" for p in agg.index], rotation=15, ha="right", fontsize=max(6, S.font_tiny-1))
    except Exception as e:
        try:
            ax.text(0.5, 0.5, 0.5, f"Erreur barres 3D:\n{e}", ha="center", va="center", fontsize=S.font_sm, color=C["red"])
        except Exception: pass


def render_area_3d(ax, df, x_col, y_col, fac_color):
    try:
        if x_col in ("zone", "zone_label"):
            for fac in sorted(df["sheet_id"].unique()):
                sub = df[df["sheet_id"] == fac].groupby("zone")[y_col].sum().sort_index()
                ax.plot(list(sub.index), [0]*len(sub), list(sub.values), color=fac_color.get(fac, "#888"), linewidth=2, marker="o", markersize=4, label=fac)
            ax.set_xticks(list(ZONES.keys()))
            ax.set_xticklabels([f"Z{z}" for z in ZONES], rotation=0, ha="center", fontsize=S.font_tiny)
        else:
            agg = df.groupby("pays")[y_col].sum().nlargest(15).sort_index()
            ax.plot(range(len(agg)), [0]*len(agg), list(agg.values), color=C["accent"], linewidth=2, marker="o", markersize=4)
        ax.set_zlabel(COLUMN_LABELS.get(y_col, y_col), labelpad=12, fontsize=S.font_tiny)
        ax.set_title(f"[3D] Aires empilees - {COLUMN_LABELS.get(y_col, y_col)}", fontsize=S.font_sm, pad=28, fontweight="bold", color=C["text_primary"])
        ax.legend(title="Faculte", fontsize=S.font_tiny, facecolor=C["bg_elevated"], edgecolor=C["border"], labelcolor=C["text_primary"])
        finalize_3d_layout(ax.get_figure())
    except Exception as e:
        try:
            ax.text(0.5, 0.5, 0.5, f"Erreur aires 3D:\n{e}", ha="center", va="center", fontsize=S.font_sm, color=C["red"])
        except Exception: pass
