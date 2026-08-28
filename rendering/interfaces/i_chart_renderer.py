# Definit ce que doit savoir faire un renderer de graphique (2D ou 3D)

from typing import Protocol
import pandas as pd
from matplotlib.figure import Figure

class IChartRenderer(Protocol):

    def render(self, fig: Figure, df: pd.DataFrame, chart_type: str, x_col: str, y_col: str, group_col: str, top_n: int) -> None: ...
