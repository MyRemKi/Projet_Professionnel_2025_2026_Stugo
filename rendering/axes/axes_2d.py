# Applique les couleurs du theme sombre sur les axes des graphiques 2D

from matplotlib.figure import Figure
from shared.constants import C
from shared.scaling import S


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
