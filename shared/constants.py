# Toutes les constantes de l'application : couleurs, zones CO2, colonnes, pages, themes

RADIUS    = "8px"
RADIUS_SM = "5px"
RADIUS_LG = "12px"

C: dict[str, str] = {
    "bg_deep": "#080b0f",
    "bg_base": "#0d1117",
    "bg_elevated": "#131920",
    "bg_card": "#192028",
    "bg_input": "#1e2832",
    "bg_hover": "#243040",
    "border": "#1f2d3d",
    "border_light": "#2a3f55",
    "text_primary": "#e8eef4",
    "text_secondary": "#7a99b8",
    "text_muted": "#405570",
    "text_link": "#00d4aa",
    "accent": "#00d4aa",
    "accent_dim": "#004d3d",
    "accent_soft": "#003d30",
    "blue": "#3d9eff",
    "orange": "#ff8c42",
    "red": "#ff5252",
    "purple": "#a78bfa",
    "yellow": "#fbbf24",
    "zone1": "#00d4aa",
    "zone2": "#3d9eff",
    "zone3": "#fbbf24",
    "zone4": "#ff8c42",
    "zone5": "#ff5252",
}

ZONES: dict[int, dict] = {
    1: {"label": "Zone 1  <0.5 tCO2e",   "cols": (0, 1, 2, 3),     "color": C["zone1"]},
    2: {"label": "Zone 2  0.5–1 tCO2e",  "cols": (4, 5, 6, 7),     "color": C["zone2"]},
    3: {"label": "Zone 3  1–2 tCO2e",    "cols": (8, 9, 10, 11),   "color": C["zone3"]},
    4: {"label": "Zone 4  2–3 tCO2e",    "cols": (12, 13, 14, 15), "color": C["zone4"]},
    5: {"label": "Zone 5  >3 tCO2e",     "cols": (16, 17, 18, 19), "color": C["zone5"]},
}

PRES_ZONE_COLORS: dict[int, str] = {z: ZONES[z]["color"] for z in ZONES}
PRES_ZONE_LABELS_SHORT: dict[int, str] = {z: f"Zone {z}" for z in ZONES}

COLUMN_LABELS: dict[str, str] = {
    "sheet_id": "Faculté",
    "zone": "Zone N°",
    "zone_label": "Zone",
    "pays": "Pays",
    "tco2e_par_voyage": "tCO2e / voyage",
    "nb_etudiants": "Étudiants",
    "total_tco2": "Total TCO2",
    "fichier": "Fichier",
}

DF_COLUMNS: list[str] = list(COLUMN_LABELS.keys())

CHART_TYPES: list[tuple[str, str, str]] = [
    ("bar",     "Barres verticales",   "📊"),
    ("barh",    "Barres horizontales", "📊"),
    ("pie",     "Camembert",           "🥧"),
    ("donut",   "Donut",               "🍩"),
    ("area",    "Aires empilées",      "🗻"),
    ("treemap", "Treemap",             "🌳"),
]

CHART_3D_COMPATIBLE: set[str] = {
    "bar", "barh", "area", "pie", "donut",
}

PAGES: dict[str, dict] = {
    "home": {"icon": "⌂",  "label": "Accueil",     "idx": 0},
    "import": {"icon": "↑",  "label": "Import",      "idx": 1},
    "table": {"icon": "≡",  "label": "Tableau",     "idx": 2},
    "chart": {"icon": "◈",  "label": "Graphique",   "idx": 3},
    "comparison": {"icon": "⊞",  "label": "Comparaison", "idx": 4},
    "settings": {"icon": "⚙",  "label": "Paramètres",  "idx": 5},
    "help": {"icon": "?",  "label": "Aide",         "idx": 6},
}

PAGES_WITH_FILTER = {"table", "chart", "comparison"}

FAC_COLORS: list[str] = [
    "#3d9eff", "#00d4aa", "#ff8c42", "#ff5252",
    "#a78bfa", "#fbbf24", "#38bdf8", "#34d399",
    "#fb7185", "#f59e0b",
]

THEMES_PRESETS: dict[str, dict] = {
    "Arctic Ink (défaut)": {
        "bg_deep":"#080b0f","bg_base":"#0d1117","bg_elevated":"#131920","bg_card":"#192028",
        "bg_input":"#1e2832","bg_hover":"#243040","border":"#1f2d3d","border_light":"#2a3f55",
        "text_primary":"#e8eef4","text_secondary":"#7a99b8","text_muted":"#405570",
        "accent":"#00d4aa","accent_dim":"#004d3d",
        "blue":"#3d9eff","orange":"#ff8c42","red":"#ff5252","purple":"#a78bfa","yellow":"#fbbf24",
    },
    "Sombre": {
        "bg_deep":"#0d1117","bg_base":"#161b22","bg_elevated":"#1c2128","bg_card":"#21262d",
        "bg_input":"#2d333b","bg_hover":"#30363d","border":"#30363d","border_light":"#444c56",
        "text_primary":"#e6edf3","text_secondary":"#8b949e","text_muted":"#6e7681",
        "accent":"#39d353","accent_dim":"#238636",
        "blue":"#388bfd","orange":"#fb8500","red":"#f85149","purple":"#8957e5","yellow":"#e3b341",
    },
    "Clair Pro": {
        "bg_deep":"#e8eaed","bg_base":"#f6f8fa","bg_elevated":"#ffffff","bg_card":"#f0f2f5",
        "bg_input":"#ffffff","bg_hover":"#e1e4e8","border":"#d0d7de","border_light":"#9aa4b0",
        "text_primary":"#1a1e23","text_secondary":"#444d56","text_muted":"#6a737d",
        "accent":"#1a7f37","accent_dim":"#d4f7dc",
        "blue":"#0550ae","orange":"#bc4c00","red":"#cf222e","purple":"#6639ba","yellow":"#7d4e00",
    },
    "Violet Nuit": {
        "bg_deep":"#08000f","bg_base":"#100018","bg_elevated":"#18002a","bg_card":"#200038",
        "bg_input":"#2a004c","bg_hover":"#330060","border":"#3d0075","border_light":"#5500a8",
        "text_primary":"#ead5ff","text_secondary":"#a880d0","text_muted":"#7050a0",
        "accent":"#c084fc","accent_dim":"#6b21a8",
        "blue":"#388bfd","orange":"#fb8500","red":"#f85149","purple":"#c084fc","yellow":"#e3b341",
    },
    "Bleu Marine": {
        "bg_deep":"#020b18","bg_base":"#041228","bg_elevated":"#061a3a","bg_card":"#08234d",
        "bg_input":"#0a2b60","bg_hover":"#0d3373","border":"#163d80","border_light":"#1f52a8",
        "text_primary":"#dce8ff","text_secondary":"#8aafdf","text_muted":"#5a7aaa",
        "accent":"#58a6ff","accent_dim":"#1a4080",
        "blue":"#388bfd","orange":"#fb8500","red":"#f85149","purple":"#8957e5","yellow":"#e3b341",
    },
    "Solarized": {
        "bg_deep":"#002b36","bg_base":"#073642","bg_elevated":"#0d4555","bg_card":"#115065",
        "bg_input":"#155a72","bg_hover":"#186580","border":"#1a6e88","border_light":"#2a8aa0",
        "text_primary":"#fdf6e3","text_secondary":"#93a1a1","text_muted":"#657b83",
        "accent":"#2aa198","accent_dim":"#155a55",
        "blue":"#268bd2","orange":"#cb4b16","red":"#dc322f","purple":"#6c71c4","yellow":"#b58900",
    },
    "Sable Clair": {
        "bg_deep":"#f5f0e8","bg_base":"#faf7f2","bg_elevated":"#ffffff","bg_card":"#f0ebe0",
        "bg_input":"#ffffff","bg_hover":"#e8e0d0","border":"#d4c9b0","border_light":"#b8a98a",
        "text_primary":"#3d2e0e","text_secondary":"#6b5430","text_muted":"#9c7e50",
        "accent":"#b8860b","accent_dim":"#f0e0a0",
        "blue":"#2e6da4","orange":"#c85a00","red":"#c0392b","purple":"#7d3c98","yellow":"#9a7d0a",
    },
}

from PyQt6.QtCore import Qt

CURSOR_PRESETS: dict[str, object] = {
    "Défaut système": None,
    "Flèche standard": Qt.CursorShape.ArrowCursor,
    "Main pointeur": Qt.CursorShape.PointingHandCursor,
    "Curseur texte": Qt.CursorShape.IBeamCursor,
    "Croix de visée": Qt.CursorShape.CrossCursor,
    "Déplacement total": Qt.CursorShape.SizeAllCursor,
    "Interdit": Qt.CursorShape.ForbiddenCursor,
    "Sablier": Qt.CursorShape.WaitCursor,
    "Image personnalisée": "custom",
}

CUSTOM_PRESET_KEYS: list[tuple[str, str]] = [
    ("bg_deep",       "Fond profond"),
    ("bg_base",       "Fond base"),
    ("bg_elevated",   "Fond élevé"),
    ("bg_card",       "Fond carte"),
    ("bg_input",      "Fond saisie"),
    ("bg_hover",      "Fond survol"),
    ("border",        "Bordure"),
    ("border_light",  "Bordure claire"),
    ("text_primary",  "Texte principal"),
    ("text_secondary","Texte secondaire"),
    ("text_muted",    "Texte atténué"),
    ("accent",        "Couleur accent"),
    ("accent_dim",    "Accent atténué"),
    ("blue",          "Bleu"),
    ("orange",        "Orange"),
    ("red",           "Rouge"),
    ("purple",        "Violet"),
    ("yellow",        "Jaune"),
]

PRESET_GROUPS: dict[str, list[str]] = {
    "Minimal (2 clés)": ["bg_base", "accent"],
    "Essentiel (6 clés)": ["bg_deep","bg_base","bg_elevated","text_primary","accent","accent_dim"],
    "Complet (18 clés)": [k for k, _ in CUSTOM_PRESET_KEYS],
}
