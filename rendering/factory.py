# Choisit la fonction de rendu adaptee (2D ou 3D) selon le mode demande

from rendering.strategies.renderer_2d import render_chart
from rendering.strategies.renderer_3d import render_chart_3d

class RendererFactory:

    @staticmethod
    def get(mode_3d: bool):
        return render_chart_3d if mode_3d else render_chart

    @staticmethod
    def render(fig, df, chart_type, x_col, y_col, group_col, top_n, mode_3d=False, elev=28, azim=-48):
        if mode_3d:
            render_chart_3d(fig, df, chart_type, x_col, y_col, group_col, top_n, elev, azim)
        else:
            render_chart(fig, df, chart_type, x_col, y_col, group_col, top_n)
