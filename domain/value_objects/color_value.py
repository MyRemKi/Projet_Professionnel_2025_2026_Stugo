# Represente une couleur hexadecimale et ses transformations (assombrir, eclaircir...)

from __future__ import annotations
from dataclasses import dataclass


@dataclass(frozen=True)
class ColorValue:

    hex: str

    def __post_init__(self) -> None:
        h = self.hex.lstrip("#")
        if len(h) not in (3, 6):
            raise ValueError(f"Couleur hex invalide : {self.hex!r}")

    def darkened(self, factor: float = 0.65) -> "ColorValue":
        from shared.color_utils import darken
        return ColorValue(darken(self.hex, factor))

    def lightened(self, factor: float = 1.22) -> "ColorValue":
        from shared.color_utils import lighten
        return ColorValue(lighten(self.hex, factor))

    def hue_shifted(self, deg: float) -> "ColorValue":
        from shared.color_utils import hue_shift
        return ColorValue(hue_shift(self.hex, deg))

    def to_rgb(self) -> tuple[float, float, float]:
        from shared.color_utils import hex_to_rgb
        return hex_to_rgb(self.hex)

    def contrast_text(self) -> "ColorValue":
        from shared.color_utils import contrast_text
        return ColorValue(contrast_text(self.hex))

    def __str__(self) -> str:
        return self.hex

    @classmethod
    def from_rgb(cls, r: float, g: float, b: float) -> "ColorValue":
        from shared.color_utils import rgb_to_hex
        return cls(rgb_to_hex(r, g, b))
