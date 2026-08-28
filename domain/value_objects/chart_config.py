# Regroupe tous les reglages d'un graphique (type, colonnes, mode 3D...)

from __future__ import annotations
from dataclasses import dataclass, field


@dataclass(frozen=True)
class ChartConfig:

    chart_type: str = "bar"
    x_col: str = "zone_label"
    y_col: str = "total_tco2"
    group_col: str = "aucun"
    top_n: int = 15
    mode_3d: bool = False
    elev: int = 28
    azim: int = -48

    def with_type(self, chart_type: str) -> "ChartConfig":
        return ChartConfig(chart_type=chart_type, x_col=self.x_col, y_col=self.y_col, group_col=self.group_col, top_n=self.top_n, mode_3d=self.mode_3d, elev=self.elev, azim=self.azim)

    def with_3d(self, elev: int, azim: int) -> "ChartConfig":
        return ChartConfig(chart_type=self.chart_type, x_col=self.x_col, y_col=self.y_col, group_col=self.group_col, top_n=self.top_n, mode_3d=True, elev=elev, azim=azim)

    def as_2d(self) -> "ChartConfig":
        return ChartConfig(chart_type=self.chart_type, x_col=self.x_col, y_col=self.y_col, group_col=self.group_col, top_n=self.top_n, mode_3d=False, elev=self.elev, azim=self.azim)

    @classmethod
    def default(cls) -> "ChartConfig":
        return cls()
