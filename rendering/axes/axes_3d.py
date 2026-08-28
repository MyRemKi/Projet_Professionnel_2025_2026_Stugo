# Applique les couleurs du theme sombre sur les axes des graphiques 3D

from matplotlib.figure import Figure
from shared.constants import C
from shared.scaling import S


def setup_3d_axes(ax, fig: Figure) -> None:
    try:
        fig.patch.set_facecolor(C["bg_base"])
        ax.set_facecolor(C["bg_elevated"])
        for pane, fc in [
            (ax.xaxis.pane, C["bg_card"]),
            (ax.yaxis.pane, C["bg_elevated"]),
            (ax.zaxis.pane, C["bg_card"]),
        ]:
            pane.fill = True
            pane.set_facecolor(fc)
            pane.set_edgecolor(C["border"])
            pane.set_linewidth(0.4)
        ax.grid(True, linestyle="--", linewidth=0.3, alpha=0.4, color=C["border_light"])
        ax.tick_params(axis="both", labelsize=max(6, S.font_tiny - 1), pad=2, colors=C["text_secondary"])
        for spine in [ax.xaxis, ax.yaxis, ax.zaxis]:
            spine.label.set_color(C["text_secondary"])
    except Exception:
        pass
