# Complete un theme partiel (2 ou 6 couleurs) pour obtenir toutes les couleurs necessaires

from shared.constants import C, ZONES, PRES_ZONE_COLORS
from shared.logging.file_logger import log_error, log_msg

ZONE_DEFAULTS = {"zone1": "#00d4aa", "zone2": "#3d9eff", "zone3": "#fbbf24", "zone4": "#ff8c42", "zone5": "#ff5252"}

def complete_preset(preset: dict) -> dict:
    try:
        from shared.color_utils import darken
        result = dict(C)
        result.update(preset)
        ac = result.get("accent", "#00d4aa")
        if "accent_dim" not in preset:
            result["accent_dim"] = darken(ac, 0.45)
        result["accent_soft"] = darken(ac, 0.32)
        result["text_link"]   = ac
        for key, default in ZONE_DEFAULTS.items():
            if key not in preset:
                result[key] = default
        return result
    except Exception as e:
        log_error("preset_completer.complete_preset", e)
        safe = dict(C)
        try: safe.update(preset)
        except Exception as e2: log_error("preset_completer.complete_preset", e2)
        return safe
