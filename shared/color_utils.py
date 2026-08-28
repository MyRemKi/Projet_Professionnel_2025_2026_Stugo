# Fonctions pour manipuler des couleurs hexadecimales (assombrir, eclaircir, convertir)

import colorsys


def luminance(hex_color: str) -> float:
    try:
        h = hex_color.lstrip("#")
        r, g, b = (int(h[i:i+2], 16) / 255 for i in (0, 2, 4))
        def lin(c): return c / 12.92 if c <= 0.04045 else ((c + 0.055) / 1.055) ** 2.4
        return 0.2126 * lin(r) + 0.7152 * lin(g) + 0.0722 * lin(b)
    except Exception:
        return 0.5


def contrast_text(bg_hex: str) -> str:
    try:
        return "#1a1e23" if luminance(bg_hex) > 0.35 else "#e8eef4"
    except Exception:
        return "#e8eef4"


def hex_to_rgb(h: str) -> tuple[float, float, float]:
    try:
        h = h.lstrip("#")
        return tuple(int(h[i:i+2], 16) / 255 for i in (0, 2, 4))
    except Exception:
        return (0.5, 0.5, 0.5)


def rgb_to_hex(r: float, g: float, b: float) -> str:
    try:
        return "#{:02x}{:02x}{:02x}".format(int(r * 255), int(g * 255), int(b * 255))
    except Exception:
        return "#888888"


def darken(hex_color: str, factor: float = 0.65) -> str:
    try:
        r, g, b = hex_to_rgb(hex_color)
        h, s, v = colorsys.rgb_to_hsv(r, g, b)
        return rgb_to_hex(*colorsys.hsv_to_rgb(h, min(s * 1.08, 1.0), v * factor))
    except Exception:
        return hex_color


def lighten(hex_color: str, factor: float = 1.22) -> str:
    try:
        r, g, b = hex_to_rgb(hex_color)
        h, s, v = colorsys.rgb_to_hsv(r, g, b)
        return rgb_to_hex(*colorsys.hsv_to_rgb(h, s * 0.65, min(v * factor, 1.0)))
    except Exception:
        return hex_color


def hue_shift(hex_c: str, shift_deg: float, sat_mult: float = 1.0, val_mult: float = 1.0) -> str:
    try:
        rr, gg, bb = hex_to_rgb(hex_c)
        hh, ss, vv = colorsys.rgb_to_hsv(rr, gg, bb)
        hh = (hh + shift_deg / 360.0) % 1.0
        return rgb_to_hex(*colorsys.hsv_to_rgb(hh, max(0, min(1, ss * sat_mult)), max(0, min(1, vv * val_mult))))
    except Exception:
        return hex_c


def derive_palette_from_2(colors: dict) -> dict:
    try:
        bg = colors.get("bg_base", "#161b22")
        ac = colors.get("accent", "#39d353")
        r, g, b = hex_to_rgb(bg)
        h, s, v = colorsys.rgb_to_hsv(r, g, b)
        is_dark = luminance(bg) < 0.35

        def step(fv, fs=1.0): return rgb_to_hex(*colorsys.hsv_to_rgb(h, max(0, min(1, s * fs)), max(0, min(1, v * fv))))

        if is_dark:
            bg_deep, bg_elev, bg_card = step(0.65), step(1.18), step(1.35)
            bg_inp, bg_hov, brd, brd_l = step(1.55), step(1.70), step(1.80), step(2.10)
            tp, ts, tm = "#e6edf3", "#8b949e", "#6e7681"
        else:
            bg_deep, bg_elev, bg_card = step(0.82), step(1.08), step(0.93)
            bg_inp, bg_hov, brd, brd_l = step(1.12), step(0.88), step(0.78), step(0.65)
            tp, ts, tm = "#1a1e23", "#444d56", "#6a737d"

        ar, ag, ab = hex_to_rgb(ac)
        ah, as_, av = colorsys.rgb_to_hsv(ar, ag, ab)
        ac_dim = rgb_to_hex(*colorsys.hsv_to_rgb(ah, min(as_ * 1.1, 1.0), av * 0.55))

        return {
            "bg_deep": bg_deep, "bg_base": bg, "bg_elevated": bg_elev, "bg_card": bg_card,
            "bg_input": bg_inp, "bg_hover": bg_hov, "border": brd, "border_light": brd_l,
            "text_primary": tp, "text_secondary": ts, "text_muted": tm,
            "accent": ac, "accent_dim": ac_dim,
            "blue": hue_shift(ac, -100), "orange": hue_shift(ac, 80, 1.1),
            "red": hue_shift(ac, 110, 1.1, 0.95), "purple": hue_shift(ac, -60, 0.9, 0.9),
            "yellow": hue_shift(ac, 60, 0.85),
        }
    except Exception:
        from shared.constants import C, CUSTOM_PRESET_KEYS
        return {k: C[k] for k, _ in CUSTOM_PRESET_KEYS}


def derive_palette_from_6(colors: dict) -> dict:
    try:
        bg_deep = colors.get("bg_deep", "#0d1117")
        bg_base = colors.get("bg_base", "#161b22")
        bg_elev = colors.get("bg_elevated", "#1c2128")
        tp = colors.get("text_primary", "#e6edf3")
        ac = colors.get("accent", "#39d353")
        ac_dim = colors.get("accent_dim", "#238636")

        def interp(h1, h2, t): r1, g1, b1 = hex_to_rgb(h1); r2, g2, b2 = hex_to_rgb(h2); return rgb_to_hex(r1 + (r2-r1)*t, g1 + (g2-g1)*t, b1 + (b2-b1)*t)

        bg_card = interp(bg_base, bg_elev, 0.5)
        r, g, b = hex_to_rgb(bg_elev)
        h, s, v = colorsys.rgb_to_hsv(r, g, b)
        is_dark = luminance(bg_base) < 0.35

        if is_dark:
            bg_inp = rgb_to_hex(*colorsys.hsv_to_rgb(h, s, min(v*1.35, 1.0)))
            bg_hov = rgb_to_hex(*colorsys.hsv_to_rgb(h, s, min(v*1.55, 1.0)))
            brd    = rgb_to_hex(*colorsys.hsv_to_rgb(h, s, min(v*1.65, 1.0)))
            brd_l  = rgb_to_hex(*colorsys.hsv_to_rgb(h, s, min(v*2.0, 1.0)))
        else:
            bg_inp = rgb_to_hex(*colorsys.hsv_to_rgb(h, max(s*0.7, 0), min(v*1.05, 1.0)))
            bg_hov = rgb_to_hex(*colorsys.hsv_to_rgb(h, max(s*0.9, 0), v*0.88))
            brd    = rgb_to_hex(*colorsys.hsv_to_rgb(h, s, v*0.78))
            brd_l  = rgb_to_hex(*colorsys.hsv_to_rgb(h, s, v*0.60))

        tr, tg, tb = hex_to_rgb(tp)
        th, ts_, tv = colorsys.rgb_to_hsv(tr, tg, tb)
        ts = rgb_to_hex(*colorsys.hsv_to_rgb(th, ts_, tv*0.62))
        tm = rgb_to_hex(*colorsys.hsv_to_rgb(th, ts_, tv*0.46))

        return {
            "bg_deep": bg_deep, "bg_base": bg_base, "bg_elevated": bg_elev, "bg_card": bg_card,
            "bg_input": bg_inp, "bg_hover": bg_hov, "border": brd, "border_light": brd_l,
            "text_primary": tp, "text_secondary": ts, "text_muted": tm,
            "accent": ac, "accent_dim": ac_dim,
            "blue": hue_shift(ac, -100), "orange": hue_shift(ac, 80, 1.1),
            "red": hue_shift(ac, 110, 1.1, 0.95), "purple": hue_shift(ac, -60, 0.9, 0.9),
            "yellow": hue_shift(ac, 60, 0.85),
        }
    except Exception:
        from shared.constants import C, CUSTOM_PRESET_KEYS
        return {k: C[k] for k, _ in CUSTOM_PRESET_KEYS}
