# Lit les fichiers Excel et verifie qu'ils respectent le format attendu par l'application

import os
import pandas as pd
from shared.constants import ZONES
from shared.logging.file_logger import log_error, log_msg

CTX = "ExcelExtractor"


def extract_all_sheets(filepaths, existing_sources=None):
    if existing_sources is None:
        existing_sources = set()
    records, summaries, new_sources = [], {}, set()

    for filepath in filepaths:
        try:
            fname = os.path.splitext(os.path.basename(filepath))[0]
            raw_sheets = pd.read_excel(filepath, sheet_name=None, header=None)
            if not raw_sheets:
                raise ValueError("Le fichier ne contient aucun onglet lisible.")

            valid_sheets = 0
            for sheet_name, raw in raw_sheets.items():
                source_uid = f"{os.path.abspath(filepath)}::{sheet_name}"
                try:
                    if sheet_name.lower() == "template":
                        continue
                    if source_uid in existing_sources:
                        continue

                    validate_sheet(raw, sheet_name, filepath)

                    new_sources.add(source_uid)
                    uid = f"{fname}::{sheet_name}"
                    rows = extract_rows(raw, source_uid, uid, filepath, sheet_name)
                    if not rows:
                        raise ValueError(f"Aucune ligne valide extraite de '{sheet_name}' (verifiez les colonnes pays/tco2e).")
                    records.extend(rows)
                    summaries[source_uid] = {"label": uid, **extract_summary(raw)}
                    valid_sheets += 1

                except ValueError as ve:
                    msg = f"{os.path.basename(filepath)} :: {sheet_name} — {ve}"
                    log_msg(f"{CTX}.sheets", msg)
                    summaries[f"invalid::{source_uid}"] = {"label": f"Format invalide : {sheet_name}", "error": str(ve)}
                except Exception as e:
                    log_error(f"{CTX}.sheets", e)

            if valid_sheets == 0 and not new_sources:
                log_msg(CTX, f"Aucun onglet valide dans {os.path.basename(filepath)}")

        except ValueError as ve:
            log_msg(CTX, str(ve))
            summaries[f"error::{filepath}"] = {"label": f"{os.path.basename(filepath)} : format invalide", "error": str(ve)}
        except Exception as e:
            log_error(CTX, e)
            summaries[f"error::{filepath}"] = {"label": f"Erreur : {os.path.basename(filepath)}"}

    return pd.DataFrame(records), summaries, new_sources


def validate_sheet(raw, sheet_name, filepath):
    if raw is None or raw.empty:
        raise ValueError(f"Onglet '{sheet_name}' vide.")

    n_rows, n_cols = raw.shape
    if n_rows < 3:
        raise ValueError(f"Onglet '{sheet_name}' : seulement {n_rows} ligne(s) (minimum 3 : 2 en-tetes + donnees).")

    max_col = max(max(z["cols"]) for z in ZONES.values())
    if n_cols <= max_col:
        raise ValueError(f"Onglet '{sheet_name}' : {n_cols} colonne(s) disponible(s), {max_col + 1} attendue(s) (format zones CO2 : 5 zones x 4 colonnes). Verifiez que le fichier est au format StuGo CO2 Explorer.")

    found_valid = False
    for _, row in raw.iloc[2:35].iterrows():
        for zone_info in ZONES.values():
            try:
                pays = row.iloc[zone_info["cols"][0]]
                if pd.notna(pays) and str(pays).strip():
                    val = row.iloc[zone_info["cols"][1]]
                    if pd.notna(val):
                        float(val)
                        found_valid = True
                        break
            except Exception:
                continue
        if found_valid:
            break

    if not found_valid:
        raise ValueError(f"Onglet '{sheet_name}' : aucune donnee valide trouvee. Colonnes attendues par zone : Pays | tCO2e/voyage | Nb etudiants | Total tCO2. Verifiez le format du fichier Excel.")


def extract_rows(raw, source_uid, uid, filepath, sheet_name):
    rows = []
    for _, row in raw.iloc[2:35].iterrows():
        for zone_id, zone_info in ZONES.items():
            try:
                c0, c1, c2, c3 = zone_info["cols"]
                pays = row.iloc[c0]
                if pd.isna(pays) or str(pays).strip() == "":
                    continue
                tco2e = row.iloc[c1]; nb_etu = row.iloc[c2]; total = row.iloc[c3]
                rows.append({
                    "source_uid": source_uid,
                    "fichier": os.path.basename(filepath),
                    "filepath": os.path.abspath(filepath),
                    "sheet_id": sheet_name,
                    "faculte_uid": uid,
                    "zone": zone_id,
                    "zone_label": zone_info["label"],
                    "pays": str(pays).strip(),
                    "tco2e_par_voyage": float(tco2e)  if pd.notna(tco2e)  else 0.0,
                    "nb_etudiants": int(nb_etu)   if pd.notna(nb_etu) else 0,
                    "total_tco2": float(total)  if pd.notna(total)  else 0.0,
                })
            except Exception as e:
                log_error(f"{CTX}._extract_rows[zone={zone_id}]", e)
    return rows


def extract_summary(raw):
    s = {}
    try:
        for _, row in raw.iterrows():
            try:
                v0, v2 = str(row.iloc[0]).strip(), row.iloc[2]
                if "Total" in v0 and "etudiant" in v0.lower() and "mob" not in v0.lower():
                    s["total_etudiants_faculte"] = int(v2) if pd.notna(v2) else 0
                elif "Total" in v0 and "mob" in v0.lower():
                    s["total_etudiants_mob"] = int(v2) if pd.notna(v2) else 0
                elif "Proportion" in v0:
                    s["proportion_pct"] = float(v2) if pd.notna(v2) else 0.0
                elif "Total TCO2" in v0:
                    s["total_tco2"] = float(v2) if pd.notna(v2) else 0.0
            except Exception as e:
                log_error(f"{CTX}._extract_summary", e)
    except Exception as e:
        log_error(f"{CTX}._extract_summary[outer]", e)
    return s
