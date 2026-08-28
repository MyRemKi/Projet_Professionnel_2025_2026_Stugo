# Dossier ou sont stockees les donnees utilisateur (session, preferences, logs)

import os

LOCAL = os.environ.get("LOCALAPPDATA") or os.environ.get("APPDATA") or os.path.expanduser("~")

APP_DATA_DIR = os.path.join(LOCAL, "StuGoCO2")
