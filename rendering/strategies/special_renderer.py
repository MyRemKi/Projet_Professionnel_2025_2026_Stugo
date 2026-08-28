# Graphiques speciaux pour les pages de comparaison (mobilite vs carbone, evolution...)

from shared.scaling import S
import numpy as np
import matplotlib.patches as mpatches
from matplotlib.figure import Figure

from shared.constants import C, ZONES, PRES_ZONE_COLORS
from rendering.strategies.renderer_2d import setup_dark_axes, adaptive_font, adaptive_rotation
from shared.logging.file_logger import log_error


def render_grouped_mob_carb(fig, df, mode_3d=False, elev=28, azim=-48):
    fig.clear()
    if df.empty: empty(fig); return
    zone_ids = list(range(1, 6))
    agg = df.groupby("zone").agg(nb_etu=("nb_etudiants","sum"), tco2=("total_tco2","sum")).reindex(zone_ids, fill_value=0)
    te, tt = agg["nb_etu"].sum(), agg["tco2"].sum()
    pct_mob  = (agg["nb_etu"] / te * 100).fillna(0).values if te > 0 else np.zeros(5)
    pct_carb = (agg["tco2"]  / tt * 100).fillna(0).values if tt > 0 else np.zeros(5)
    colors_m = [PRES_ZONE_COLORS[z] for z in zone_ids]; color_c = C["orange"]
    if mode_3d:
        from rendering.strategies.renderer_3d import setup_3d_axes
        from rendering.geometry.cube_3d import draw_cube
        ax = fig.add_subplot(111, projection="3d")
        setup_3d_axes(ax, fig); ax.view_init(elev=elev, azim=azim)
        for i, z in enumerate(zone_ids):
            draw_cube(ax, i*1.1, 0, 0, 0.35, 0.40, pct_mob[i], colors_m[i])
            draw_cube(ax, i*1.1+0.35+0.12, 0, 0, 0.35, 0.40, pct_carb[i], color_c)
        ax.set_xticks([i*1.1+0.35+0.06 for i in range(5)])
        ax.set_xticklabels([f"Z{z}" for z in zone_ids], rotation=0, ha="center", fontsize=S.font_tiny)
        ax.set_zlabel("(%)", labelpad=8, fontsize=S.font_tiny)
        handles = [mpatches.Patch(color=PRES_ZONE_COLORS[z], label=f"Z{z} Mob:{pct_mob[z-1]:.1f}%") for z in zone_ids]
        handles.append(mpatches.Patch(color=color_c, label="CO2"))
        ax.legend(handles=handles, fontsize=S.font_tiny, loc="upper left", facecolor=C["bg_elevated"], edgecolor=C["border"], labelcolor=C["text_primary"])
        ax.set_title("Mobilites vs Poids Carbone [3D]", fontsize=S.font_sm, pad=16, fontweight="bold", color=C["text_primary"])
    else:
        ax = fig.add_subplot(111); setup_dark_axes(ax, fig)
        x, w = np.arange(5), 0.38
        bars_m = ax.bar(x - w/2, pct_mob, w, color=colors_m, edgecolor=C["bg_base"], linewidth=0.8)
        bars_c = ax.bar(x + w/2, pct_carb, w, color=color_c, edgecolor=C["bg_base"], linewidth=0.8)
        for bar, val in zip(bars_m, pct_mob):
            if val > 0: ax.text(bar.get_x()+bar.get_width()/2, bar.get_height()+0.4, f"{val:.1f}", ha="center", va="bottom", fontsize=S.font_tiny, color=C["text_secondary"])
        for bar, val in zip(bars_c, pct_carb):
            if val > 0: ax.text(bar.get_x()+bar.get_width()/2, bar.get_height()+0.4, f"{val:.1f}", ha="center", va="bottom", fontsize=S.font_tiny, color=C["text_secondary"])
        ax.set_xticks(x); ax.set_xticklabels([f"Zone {z}" for z in zone_ids])
        ax.set_ylabel("(%)")
        ax.legend(handles=[mpatches.Patch(color=PRES_ZONE_COLORS[1], label="Mobilites"), mpatches.Patch(color=color_c, label="Carbone")], fontsize=S.font_tiny, facecolor=C["bg_elevated"], edgecolor=C["border"], labelcolor=C["text_primary"])
        ax.set_title("Proportion mobilites vs poids carbone", fontsize=S.font_sm, pad=12)
    fig.tight_layout(pad=2.0)


def render_pie3d_departs(fig, df, mode_3d=True, elev=32, azim=-60):
    fig.clear()
    if df.empty: empty(fig); return
    zone_ids = list(range(1, 6))
    agg = df.groupby("zone")["nb_etudiants"].sum().reindex(zone_ids, fill_value=0)
    total = agg.sum()
    pcts = (agg / total * 100).fillna(0).values if total > 0 else np.zeros(5)
    colors = [PRES_ZONE_COLORS[z] for z in zone_ids]; explodes = [0.0, 0.0, 0.0, 0.07, 0.0]
    if mode_3d:
        from rendering.geometry.pie_3d import draw_pie3d_wedge
        ax = fig.add_subplot(111, projection="3d")
        fig.patch.set_facecolor(C["bg_base"]); ax.set_facecolor(C["bg_elevated"])
        ax.view_init(elev=elev, azim=azim); ax.set_axis_off()
        cumulative = 90.0
        for i, (pct, color, expl) in enumerate(zip(pcts, colors, explodes)):
            if pct <= 0: continue
            theta1, theta2 = cumulative, cumulative + pct / 100 * 360
            draw_pie3d_wedge(ax, theta1, theta2, color, explode=expl)
            cumulative += pct / 100 * 360
        ax.set_xlim(-1.5, 1.5); ax.set_ylim(-1.5, 1.5); ax.set_zlim(-0.1, 0.65)
        ax.legend(handles=[mpatches.Patch(color=PRES_ZONE_COLORS[z], label=f"Zone {z}  {pcts[z-1]:.1f}%  ({int(agg.iloc[z-1]):,} et.)") for z in zone_ids if pcts[z-1] > 0], fontsize=S.font_tiny, loc="upper right", bbox_to_anchor=(1.35, 0.98), framealpha=0.92, facecolor=C["bg_elevated"], edgecolor=C["border"], labelcolor=C["text_primary"])
        ax.set_title("Departs par zone [3D]", fontsize=S.font_sm, pad=16, fontweight="bold", color=C["text_primary"])
    else:
        ax = fig.add_subplot(111); setup_dark_axes(ax, fig)
        wedges, texts, autotexts = ax.pie(pcts, labels=[f"Zone {z}" for z in zone_ids], autopct="%1.0f%%", colors=colors, startangle=90, explode=explodes, pctdistance=0.70, wedgeprops=dict(edgecolor=C["bg_base"], linewidth=2))
        for t in autotexts: t.set_fontsize(9); t.set_fontweight("bold"); t.set_color("white")
        for t in texts: t.set_fontsize(9); t.set_color(C["text_secondary"])
        ax.set_title("Proportion des departs par zone", fontsize=S.font_base-1, pad=14)
    fig.tight_layout(pad=2.0)


def render_stacked_evol(fig, df, mode_3d=False, elev=30, azim=-55):
    fig.clear()
    if df.empty: empty(fig); return
    zone_ids = list(range(1, 6))
    if "annee" in df.columns:
        annees = sorted(df["annee"].dropna().unique())[:2]
        if len(annees) < 2: annees = [annees[0], annees[0]] if annees else ["22-23", "23-24"]
        pivot = {a: (df[df["annee"]==a].groupby("zone")["nb_etudiants"].sum().reindex(zone_ids, fill_value=0)) for a in annees}
    else:
        facs = sorted(df["sheet_id"].unique()); mid = max(1, len(facs)//2)
        facs1, facs2 = facs[:mid], facs[mid:] or facs; annees = ["22-23", "23-24"]
        pivot = {
            "22-23": df[df["sheet_id"].isin(facs1)].groupby("zone")["nb_etudiants"].sum().reindex(zone_ids, fill_value=0),
            "23-24": df[df["sheet_id"].isin(facs2)].groupby("zone")["nb_etudiants"].sum().reindex(zone_ids, fill_value=0),
        }
    pct = {}
    for a in annees:
        tot = pivot[a].sum(); pct[a] = (pivot[a]/tot*100).values if tot > 0 else np.zeros(5)
    lbl_annees = [f"Mob. {annees[0].upper()}", f"Mob. {annees[1].upper()}"]
    if mode_3d:
        from rendering.strategies.renderer_3d import setup_3d_axes
        from rendering.geometry.cube_3d import draw_cube
        ax = fig.add_subplot(111, projection="3d")
        setup_3d_axes(ax, fig); ax.view_init(elev=elev, azim=azim)
        for col_idx, a in enumerate(annees):
            xpos, z_base = col_idx*1.9, 0.0
            for zone_i, z in enumerate(zone_ids):
                dz = pct[a][zone_i]
                if dz <= 0: z_base += dz; continue
                draw_cube(ax, xpos, 0, z_base, 0.62, 0.50, dz, PRES_ZONE_COLORS[z])
                if dz >= 6.0: ax.text(xpos+0.31, 0.25, z_base+dz/2, f"{dz:.0f}%", ha="center", va="center", fontsize=S.font_tiny, fontweight="bold", color="white", zdir="z")
                z_base += dz
        ax.set_xticks([0+0.31, 1.9+0.31]); ax.set_xticklabels(lbl_annees, rotation=0, ha="center", fontsize=S.font_tiny)
        ax.set_zlim(0, 108); ax.set_zlabel("(%)", labelpad=8, fontsize=S.font_tiny)
        ax.legend(handles=[mpatches.Patch(color=PRES_ZONE_COLORS[z], label=f"Zone {z}") for z in zone_ids], fontsize=S.font_tiny, loc="upper left", facecolor=C["bg_elevated"], edgecolor=C["border"], labelcolor=C["text_primary"])
        ax.set_title("Evolution des zones [3D]", fontsize=S.font_sm, pad=16, fontweight="bold", color=C["text_primary"])
    else:
        ax = fig.add_subplot(111); setup_dark_axes(ax, fig)
        x, w = np.arange(len(annees)), 0.42; base_arr = np.zeros(len(annees))
        for zone_i, z in enumerate(zone_ids):
            vals = np.array([pct[a][zone_i] for a in annees])
            bars = ax.bar(x, vals, w, bottom=base_arr, label=f"Zone {z}", color=PRES_ZONE_COLORS[z], edgecolor=C["bg_base"], linewidth=0.6)
            for bar, val, bot in zip(bars, vals, base_arr):
                if val >= 3.5: ax.text(bar.get_x()+bar.get_width()/2, bot+val/2, f"{val:.1f}", ha="center", va="center", fontsize=S.font_tiny, fontweight="bold", color="white")
            base_arr += vals
        ax.set_xticks(x); ax.set_xticklabels(lbl_annees, fontsize=S.font_tiny, fontweight="bold")
        ax.set_ylim(0, 108); ax.set_ylabel("(%)")
        ax.legend(title="Zone", fontsize=S.font_tiny, loc="upper right", facecolor=C["bg_elevated"], edgecolor=C["border"], labelcolor=C["text_primary"])
        ax.set_title("Evolution des zones de destination", fontsize=S.font_sm, pad=12)
    fig.tight_layout(pad=2.0)


def render_multi_evol(fig, df, mode_3d=False, elev=28, azim=-48):
    fig.clear()
    if df.empty: empty(fig); return
    agg = (df.groupby(["fichier", "zone"])["nb_etudiants"].sum().unstack(fill_value=0).reindex(columns=list(range(1, 6)), fill_value=0))
    fichiers = list(agg.index); totals = agg.sum(axis=1)
    pct = agg.div(totals.replace(0, 1), axis=0) * 100
    zone_ids = list(range(1, 6)); width = 0.65; x = np.arange(len(fichiers))
    if mode_3d:
        from rendering.strategies.renderer_3d import setup_3d_axes
        from rendering.geometry.cube_3d import draw_cube
        ax = fig.add_subplot(111, projection="3d")
        setup_3d_axes(ax, fig); ax.view_init(elev=elev, azim=azim)
        for fi in range(len(fichiers)):
            z_base = 0.0
            for z in zone_ids:
                dz = float(pct.iloc[fi][z])
                if dz <= 0: z_base += dz; continue
                draw_cube(ax, fi*1.1, 0, z_base, 0.55, 0.45, dz, PRES_ZONE_COLORS[z])
                if dz >= 5.0: ax.text(fi*1.1+0.275, 0.225, z_base+dz/2, f"{dz:.0f}%", ha="center", va="center", fontsize=S.font_tiny, fontweight="bold", color="white", zdir="z")
                z_base += dz
        ax.set_xticks([i*1.1+0.275 for i in range(len(fichiers))])
        ax.set_xticklabels([f[:14] for f in fichiers], rotation=0, ha="center", fontsize=adaptive_font(len(fichiers)))
        ax.set_zlim(0, 108); ax.set_zlabel("(%)", labelpad=8, fontsize=S.font_tiny)
        ax.legend(handles=[mpatches.Patch(color=PRES_ZONE_COLORS[z], label=f"Zone {z}") for z in zone_ids], fontsize=S.font_tiny, loc="upper left", facecolor=C["bg_elevated"], edgecolor=C["border"], labelcolor=C["text_primary"])
        ax.set_title("Repartition zones par fichier [3D]", fontsize=S.font_sm, pad=16, fontweight="bold", color=C["text_primary"])
    else:
        ax = fig.add_subplot(111); setup_dark_axes(ax, fig)
        base_arr = np.zeros(len(fichiers))
        for z in zone_ids:
            vals = pct[z].values
            bars = ax.bar(x, vals, width, bottom=base_arr, label=f"Zone {z}", color=PRES_ZONE_COLORS[z], edgecolor=C["bg_base"], linewidth=0.6)
            for bar, val, bot in zip(bars, vals, base_arr):
                if val >= 3.5: ax.text(bar.get_x()+bar.get_width()/2, bot+val/2, f"{val:.0f}%", ha="center", va="center", fontsize=S.font_tiny, fontweight="bold", color="white")
            base_arr += vals
        fs = adaptive_font(len(fichiers)); rot, ha_a = adaptive_rotation(len(fichiers), max((len(f) for f in fichiers), default=8))
        ax.set_xticks(x); ax.set_xticklabels(fichiers, rotation=rot, ha=ha_a, fontsize=fs)
        ax.set_ylim(0, 108); ax.set_ylabel("(%)")
        ax.legend(title="Zone", fontsize=S.font_tiny, loc="upper right", facecolor=C["bg_elevated"], edgecolor=C["border"], labelcolor=C["text_primary"])
        ax.set_title("Repartition des mobilites par zone et par fichier", fontsize=S.font_sm, pad=12)
        if rot > 0: fig.subplots_adjust(bottom=0.22)
    fig.tight_layout(pad=2.0)


def empty(fig):
    ax = fig.add_subplot(111); setup_dark_axes(ax, fig)
    ax.text(0.5, 0.5, "Aucune donnee", ha="center", va="center", color=C["text_muted"], fontsize=S.font_base)
    fig.tight_layout(pad=2.0)
