from __future__ import annotations

from pathlib import Path

import pandas as pd

CORE_TABLES: dict[str, Path] = {
    "patients": Path("mimic-iv-3.1/mimic-iv-3.1/hosp/patients.csv.gz"),
    "admissions": Path("mimic-iv-3.1/mimic-iv-3.1/hosp/admissions.csv.gz"),
    "diagnoses_icd": Path("mimic-iv-3.1/mimic-iv-3.1/hosp/diagnoses_icd.csv.gz"),
    "labevents": Path("mimic-iv-3.1/mimic-iv-3.1/hosp/labevents.csv.gz"),
    "d_labitems": Path("mimic-iv-3.1/mimic-iv-3.1/hosp/d_labitems.csv.gz"),
    "icustays": Path("mimic-iv-3.1/mimic-iv-3.1/icu/icustays.csv.gz"),
    "chartevents": Path("mimic-iv-3.1/mimic-iv-3.1/icu/chartevents.csv.gz"),
    "inputevents": Path("mimic-iv-3.1/mimic-iv-3.1/icu/inputevents.csv.gz"),
    "d_items": Path("mimic-iv-3.1/mimic-iv-3.1/icu/d_items.csv.gz"),
    "edstays": Path("mimic-iv-ed-2.2/mimic-iv-ed-2.2/ed/edstays.csv.gz"),
    "triage": Path("mimic-iv-ed-2.2/mimic-iv-ed-2.2/ed/triage.csv.gz"),
    "vitalsign": Path("mimic-iv-ed-2.2/mimic-iv-ed-2.2/ed/vitalsign.csv.gz"),
    "diagnosis": Path("mimic-iv-ed-2.2/mimic-iv-ed-2.2/ed/diagnosis.csv.gz"),
}

NOTE_ARCHIVE = Path(
    "mimic-iv-note_2.2/mimic-iv-note-deidentified-free-text-clinical-notes-2.2.zip"
)


def get_table_path(data_root: Path, table_name: str) -> Path:
    if table_name not in CORE_TABLES:
        available = ", ".join(sorted(CORE_TABLES))
        raise KeyError(f"Unknown table: {table_name}. Available tables: {available}")

    path = data_root / CORE_TABLES[table_name]
    if not path.exists():
        raise FileNotFoundError(f"Table file does not exist: {path}")
    return path


def read_preview(data_root: Path, table_name: str, nrows: int = 5) -> pd.DataFrame:
    path = get_table_path(data_root, table_name)
    return pd.read_csv(path, nrows=nrows)
