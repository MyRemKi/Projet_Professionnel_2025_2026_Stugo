# Point d'entree simple pour demander le dessin d'un graphique (2D ou 3D)

from matplotlib.figure import Figure
from rendering.strategies.renderer_2d import render_chart
from rendering.strategies.renderer_3d import render_chart_3d

class ChartService:

    @staticmethod
    def render(fig: Figure, df, chart_type: str, x_col: str, y_col: str, group_col: str, top_n: int, mode_3d: bool = False, elev: int = 28, azim: int = -48) -> None:
        if mode_3d:
            render_chart_3d(fig, df, chart_type, x_col, y_col, group_col, top_n, elev, azim)
        else:
            render_chart(fig, df, chart_type, x_col, y_col, group_col, top_n)
