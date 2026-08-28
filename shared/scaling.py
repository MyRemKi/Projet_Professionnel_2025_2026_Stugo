# Calcule toutes les tailles de l'interface selon le DPI de l'ecran (zoom adaptatif)

from __future__ import annotations


class S:

    font_tiny: int = 9
    font_sm: int = 11
    font_base: int = 13
    font_md: int = 15
    font_lg: int = 18
    font_xl: int = 22
    font_hero: int = 26
    font_icon: int = 16
    font_mono: int = 11
    font_code: int = 10

    btn_h: int = 32
    btn_h_sm: int = 26
    btn_h_lg: int = 40
    input_h: int = 32
    nav_btn_h: int = 46
    toolbar_h: int = 52
    header_h: int = 58
    stat_h: int = 76
    hero_h: int = 148
    splash_w: int = 580
    splash_h: int = 340

    sidebar_w: int = 196
    filter_w: int = 230
    log_w: int = 230
    icon_col_w: int = 20

    margin_page: int = 24
    margin_card: int = 14
    spacing_md: int = 10
    spacing_sm: int = 6
    spacing_lg: int = 16

    radius_sm: int = 5
    radius_md: int = 8
    radius_lg: int = 12

    row_h: int = 30
    dpi_scale: float = 1.0

    @classmethod
    def init(cls, app=None) -> None:
        try:
            from PyQt6.QtWidgets import QApplication
            screen = (app or QApplication.instance()).primaryScreen()
            if screen is None:
                return
            ldpi  = screen.logicalDotsPerInch()
            scale = max(0.85, min(ldpi / 96.0, 2.2))
            cls.dpi_scale = scale

            def sc(v: int) -> int: return max(1, round(v * scale))

            cls.font_tiny  = sc(9);  cls.font_sm    = sc(11); cls.font_base  = sc(13)
            cls.font_md    = sc(15); cls.font_lg    = sc(18); cls.font_xl    = sc(22)
            cls.font_hero  = sc(26); cls.font_icon  = sc(16); cls.font_mono  = sc(11)
            cls.font_code  = sc(10)

            cls.btn_h      = sc(32); cls.btn_h_sm   = sc(26); cls.btn_h_lg   = sc(40)
            cls.input_h    = sc(32); cls.nav_btn_h  = sc(46); cls.toolbar_h  = sc(52)
            cls.header_h   = sc(58); cls.stat_h     = sc(76); cls.hero_h     = sc(148)
            cls.splash_w   = sc(580);cls.splash_h   = sc(340)

            cls.sidebar_w  = sc(196);cls.filter_w   = sc(230);cls.log_w      = sc(230)
            cls.icon_col_w = sc(20)

            cls.margin_page = sc(24); cls.margin_card = sc(14)
            cls.spacing_md  = sc(10); cls.spacing_sm  = sc(6); cls.spacing_lg  = sc(16)
            cls.radius_sm   = sc(5);  cls.radius_md   = sc(8); cls.radius_lg   = sc(12)
            cls.row_h       = sc(30)
        except Exception:
            pass

    @classmethod
    def r_sm(cls)  -> str: return f"{cls.radius_sm}px"
    @classmethod
    def r_md(cls)  -> str: return f"{cls.radius_md}px"
    @classmethod
    def r_lg(cls)  -> str: return f"{cls.radius_lg}px"
