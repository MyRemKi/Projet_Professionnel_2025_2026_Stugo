# Lit les fichiers CSV exportes par StuGo CO2 Explorer et les transforme en tableau de donnees

import os
import pandas as pd
from shared.logging.file_logger import log_error, log_msg

CTX = "CsvExtractor"

REQUIRED = {"sheet_id", "zone", "zone_label", "pays", "tco2e_par_voyage", "nb_etudiants", "total_tco2", "fichier"}


def extract_from_csv(filepaths, existing_sources=None):
    if existing_sources is None:
        existing_sources = set()

    records, summaries, new_sources = [], {}, set()

    for filepath in filepaths:
        fname    = os.path.splitext(os.path.basename(filepath))[0]
        abs_path = os.path.abspath(filepath)
        try:
            raw = read_csv(filepath)
            validate(raw, filepath)

            groups = raw.groupby(["fichier", "sheet_id"], sort=False)
            valid_groups = 0

            for (fichier_val, sheet_id), group in groups:
                source_uid = f"{abs_path}::{fichier_val}::{sheet_id}"
                if source_uid in existing_sources:
                    continue

                label_uid = f"{fname}::{sheet_id}"
                new_sources.add(source_uid)
                valid_groups += 1

                for _, row in group.iterrows():
                    try:
                        records.append({
                            "source_uid": source_uid,
                            "fichier": str(fichier_val),
                            "filepath": abs_path,
                            "sheet_id": str(sheet_id),
                            "faculte_uid": label_uid,
                            "zone": int(row.get("zone", 0)),
                            "zone_label": str(row.get("zone_label", "")),
                            "pays": str(row.get("pays", "")).strip(),
                            "tco2e_par_voyage": float(row.get("tco2e_par_voyage", 0.0)),
                            "nb_etudiants": int(row.get("nb_etudiants", 0)),
                            "total_tco2": float(row.get("total_tco2", 0.0)),
                        })
                    except Exception as e:
                        log_error(f"{CTX}.row", e)

                summaries[source_uid] = {"label": label_uid}

            if valid_groups == 0 and not new_sources:
                log_msg(CTX, f"Aucun groupe nouveau dans {os.path.basename(filepath)}")

        except ValueError as ve:
            msg = str(ve)
            log_msg(CTX, msg)
            summaries[f"invalid::{abs_path}"] = {"label": f"Format invalide : {os.path.basename(filepath)}", "error": msg}
        except Exception as e:
            log_error(CTX, e)
            summaries[f"error::{abs_path}"] = {"label": f"Erreur : {os.path.basename(filepath)}", "error": str(e)}

    return pd.DataFrame(records), summaries, new_sources


def read_csv(filepath: str) -> pd.DataFrame:
    for enc in ("utf-8-sig", "utf-8", "latin-1", "cp1252"):
        try:
            df = pd.read_csv(filepath, sep=";", encoding=enc, dtype=str)
            if not df.empty:
                return df
        except Exception:
            continue
    raise ValueError("Impossible de lire le fichier. Vérifiez qu'il s'agit bien d'un export CSV StuGo (séparateur ';', encodage UTF-8).")


def validate(df: pd.DataFrame, filepath: str) -> None:
    missing = REQUIRED - set(df.columns)
    if missing:
        raise ValueError(f"Ce fichier n'est pas un export StuGo CO2 Explorer.\nColonnes manquantes : {', '.join(sorted(missing))}.\nSeuls les CSV exportés via le bouton 'Exporter CSV' du logiciel sont acceptés.")
    if df.empty:
        raise ValueError("Le fichier CSV est vide.")


def float(val) -> float:
    try:
        return float(str(val).replace(",", "."))
    except Exception:
        return 0.0


def int(val) -> int:
    try:
        return int(float(str(val).replace(",", ".")))
    except Exception:
        return 0
