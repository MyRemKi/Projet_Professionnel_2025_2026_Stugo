# Dessine les graphiques 2D (barres, camembert, aires, treemap) avec matplotlib

from shared.scaling import S
import numpy as np
import matplotlib.patches as mpatches
from matplotlib.figure import Figure

from shared.constants import C, ZONES, PRES_ZONE_COLORS, FAC_COLORS, COLUMN_LABELS
from shared.logging.file_logger import log_error


def setup_dark_axes(ax, fig: Figure) -> None:
    fig.patch.set_facecolor(C["bg_base"])
    ax.set_facecolor(C["bg_elevated"])
    ax.tick_params(colors=C["text_secondary"])
    ax.xaxis.label.set_color(C["text_secondary"])
    ax.yaxis.label.set_color(C["text_secondary"])
    ax.title.set_color(C["text_primary"])
    for spine in ax.spines.values():
        spine.set_color(C["border"])
    ax.grid(True, color=C["border"], linewidth=0.4, alpha=0.5)


def adaptive_font(n: int) -> int:
    base = S.font_tiny
    if n <= 6: return max(base, S.font_sm)
    if n <= 12: return base + 1
    if n <= 20: return base
    return max(6, base - 1)


def adaptive_rotation(n: int, max_len: int = 8) -> tuple[int, str]:
    if n <= 5 and max_len <= 8: return 0, "center"
    if n <= 10: return 30, "right"
    return 45, "right"


def render_chart(fig: Figure, df, chart_type: str, x_col: str, y_col: str, group_col: str, top_n: int) -> None:
    fig.clear()
    if df.empty:
        ax = fig.add_subplot(111)
        setup_dark_axes(ax, fig)
        ax.text(0.5, 0.5, "Aucune donnée", ha="center", va="center", fontsize=S.font_base, color=C["text_muted"])
        fig.tight_layout(pad=2.0)
        return

    fac_list  = sorted(df["sheet_id"].unique())
    fac_color = {f: FAC_COLORS[i % len(FAC_COLORS)] for i, f in enumerate(fac_list)}
    zone_color = {z: v["color"] for z, v in ZONES.items()}
    ax = fig.add_subplot(111)
    setup_dark_axes(ax, fig)

    try:
        dispatch_2d(ax, fig, df, chart_type, x_col, y_col, group_col, top_n, fac_color, zone_color)
    except Exception as e:
        ax.text(0.5, 0.5, f"Erreur graphique :\n{str(e)}", ha="center", va="center", fontsize=S.font_sm, color=C["red"], wrap=True)

    fig.tight_layout(pad=2.5)


def dispatch_2d(ax, fig, df, chart_type, x_col, y_col, group_col, top_n, fac_color, zone_color):
    if chart_type in ("bar", "barh"):
        render_bar(ax, fig, df, chart_type, x_col, y_col, group_col, top_n, fac_color, zone_color)
    elif chart_type in ("pie", "donut"):
        render_pie(ax, df, chart_type, x_col, y_col, fac_color, top_n)
    elif chart_type == "area":
        render_area(ax, df, y_col, fac_color)
    elif chart_type == "treemap":
        render_treemap(ax, df, x_col, y_col, top_n, fac_color)


def render_bar(ax, fig, df, chart_type, x_col, y_col, group_col, top_n, fac_color, zone_color):
    if x_col in ("zone", "zone_label"):
        agg = df.groupby("zone_label")[y_col].sum().sort_values(ascending=False)
        colors = [zone_color.get(i + 1, "#888") for i in range(len(agg))]
        fs = adaptive_font(len(agg))
        rot, ha = adaptive_rotation(len(agg), max(len(str(l)) for l in agg.index))
        if chart_type == "bar":
            bars = ax.bar(range(len(agg)), agg.values, color=colors, edgecolor=C["bg_base"], linewidth=0.8)
            ax.set_xticks(range(len(agg)))
            ax.set_xticklabels(agg.index, rotation=rot, ha=ha, fontsize=fs)
            ax.bar_label(bars, fmt="%.1f", padding=3, fontsize=fs, color=C["text_secondary"])
        else:
            bars = ax.barh(range(len(agg)), agg.values, color=colors, edgecolor=C["bg_base"], linewidth=0.8)
            ax.set_yticks(range(len(agg)))
            ax.set_yticklabels(agg.index, fontsize=fs)
            ax.bar_label(bars, fmt="%.1f", padding=3, fontsize=fs, color=C["text_secondary"])

    elif x_col in ("sheet_id", "faculte_uid"):
        if group_col == "zone_label":
            pivot = df.pivot_table(index="sheet_id", columns="zone_label", values=y_col, aggfunc="sum").fillna(0)
            zone_cols = [ZONES[z]["label"] for z in ZONES if ZONES[z]["label"] in pivot.columns]
            pivot = pivot[zone_cols]
            zcolors = [ZONES[z]["color"] for z in ZONES if ZONES[z]["label"] in pivot.columns]
            pivot.plot(kind="bar" if chart_type == "bar" else "barh", ax=ax, color=zcolors, edgecolor=C["bg_base"], width=0.7)
            ax.legend(title="Zone", fontsize=S.font_tiny, facecolor=C["bg_elevated"], edgecolor=C["border"], labelcolor=C["text_primary"])
        else:
            agg = df.groupby("sheet_id")[y_col].sum()
            colors = [fac_color[f] for f in agg.index]
            fs = adaptive_font(len(agg))
            rot, ha = adaptive_rotation(len(agg))
            if chart_type == "bar":
                bars = ax.bar(range(len(agg)), agg.values, color=colors, edgecolor=C["bg_base"], linewidth=0.8)
                ax.set_xticks(range(len(agg)))
                ax.set_xticklabels(agg.index, rotation=rot, ha=ha, fontsize=fs)
                ax.bar_label(bars, fmt="%.1f", padding=3, fontsize=fs, color=C["text_secondary"])
            else:
                bars = ax.barh(range(len(agg)), agg.values, color=colors, edgecolor=C["bg_base"], linewidth=0.8)
                ax.set_yticks(range(len(agg)))
                ax.set_yticklabels(agg.index, fontsize=fs)
                ax.bar_label(bars, fmt="%.1f", padding=3, fontsize=fs, color=C["text_secondary"])

    elif x_col == "pays":
        agg = df.groupby("pays")[y_col].sum().nlargest(top_n)
        colors = [fac_color.get(df[df["pays"] == p]["sheet_id"].mode().iloc[0] if not df[df["pays"] == p]["sheet_id"].empty else "", "#888") for p in agg.index]
        fs = adaptive_font(len(agg))
        rot, ha = adaptive_rotation(len(agg), max(len(p) for p in agg.index))
        if chart_type == "bar":
            bars = ax.bar(range(len(agg)), agg.values, color=colors, edgecolor=C["bg_base"], linewidth=0.8)
            ax.set_xticks(range(len(agg)))
            ax.set_xticklabels(agg.index, rotation=rot, ha=ha, fontsize=fs)
            ax.bar_label(bars, fmt="%.1f", padding=3, fontsize=fs, color=C["text_secondary"])
        else:
            bars = ax.barh(range(len(agg)), agg.values, color=colors, edgecolor=C["bg_base"], linewidth=0.8)
            ax.set_yticks(range(len(agg)))
            ax.set_yticklabels(agg.index, fontsize=fs)
            ax.bar_label(bars, fmt="%.1f", padding=3, fontsize=fs, color=C["text_secondary"])

    ax.set_title(f"{COLUMN_LABELS.get(y_col, y_col)} par {COLUMN_LABELS.get(x_col, x_col)}", fontsize=S.font_sm, pad=12)
    ax.set_ylabel(COLUMN_LABELS.get(y_col, y_col))
    if chart_type == "bar": fig.subplots_adjust(bottom=0.22)
    else: fig.subplots_adjust(left=0.28)


def render_pie(ax, df, chart_type, x_col, y_col, fac_color, top_n):
    if x_col in ("zone", "zone_label"):
        agg = df.groupby("zone_label")[y_col].sum()
        agg = agg[agg > 0]
        colors = [ZONES[z]["color"] for z in ZONES if ZONES[z]["label"] in agg.index]
    elif x_col in ("sheet_id", "faculte_uid"):
        agg = df.groupby("sheet_id")[y_col].sum()
        agg = agg[agg > 0]
        colors = [fac_color[f] for f in agg.index]
    else:
        agg = df.groupby("pays")[y_col].sum().nlargest(top_n)
        agg = agg[agg > 0]
        colors = FAC_COLORS[:len(agg)]

    kw = dict(wedgeprops=dict(edgecolor=C["bg_base"], linewidth=2))
    if chart_type == "donut":
        kw["wedgeprops"]["width"] = 0.55
    fs = adaptive_font(len(agg))
    wedges, texts, autotexts = ax.pie(agg.values, labels=None, autopct="%1.1f%%", colors=colors, startangle=90, pctdistance=0.78, **kw)
    for t in autotexts:
        t.set_fontsize(fs); t.set_color("white"); t.set_fontweight("bold")
    ax.legend(wedges, agg.index, title=COLUMN_LABELS.get(x_col, ""), loc="best", fontsize=max(fs - 1, 6), facecolor=C["bg_elevated"], edgecolor=C["border"], labelcolor=C["text_primary"])
    if chart_type == "donut":
        ax.text(0, 0, f"{agg.sum():.1f}\n{COLUMN_LABELS.get(y_col, '')}", ha="center", va="center", fontsize=S.font_tiny, fontweight="bold", color=C["text_primary"])
    ax.set_title(f"Répartition {COLUMN_LABELS.get(y_col, y_col)}", fontsize=S.font_sm, pad=12)


def render_area(ax, df, y_col, fac_color):
    pivot = df.pivot_table(index="zone", columns="sheet_id", values=y_col, aggfunc="sum").fillna(0)
    colors_area = [fac_color.get(c, "#888") for c in pivot.columns]
    pivot.plot(kind="area", ax=ax, color=colors_area, alpha=0.75, linewidth=1.5)
    ax.set_xticks(list(ZONES.keys()))
    ax.set_xticklabels([ZONES[z]["label"] for z in ZONES], rotation=25, ha="right", fontsize=S.font_tiny)
    ax.legend(title="Faculté", fontsize=S.font_tiny, facecolor=C["bg_elevated"], edgecolor=C["border"], labelcolor=C["text_primary"])
    ax.set_title(f"Aires empilées — {COLUMN_LABELS.get(y_col, y_col)}", fontsize=S.font_sm)


def render_treemap(ax, df, x_col, y_col, top_n, fac_color):
    try:
        import squarify
        if x_col in ("sheet_id", "faculte_uid"):
            agg = df.groupby("sheet_id")[y_col].sum().sort_values(ascending=False)
            colors_tm = [fac_color.get(f, "#888") for f in agg.index]
        elif x_col in ("zone", "zone_label"):
            agg = df.groupby("zone_label")[y_col].sum().sort_values(ascending=False)
            colors_tm = [ZONES[z]["color"] for z in ZONES if ZONES[z]["label"] in agg.index]
        else:
            agg = df.groupby("pays")[y_col].sum().nlargest(top_n).sort_values(ascending=False)
            colors_tm = FAC_COLORS[:len(agg)]
        fs = adaptive_font(len(agg))
        squarify.plot(sizes=agg.values, label=[f"{f}\n{v:.1f}" for f, v in zip(agg.index, agg.values)], color=colors_tm, alpha=0.85, ax=ax, pad=2, text_kwargs={"fontsize": fs, "color": "white", "fontweight": "bold"})
        ax.axis("off")
        ax.set_title(f"Treemap {COLUMN_LABELS.get(y_col, y_col)}", fontsize=S.font_sm)
    except ImportError:
        ax.text(0.5, 0.5, "pip install squarify\npour les treemaps", ha="center", va="center", fontsize=S.font_base - 1, color=C["red"])
