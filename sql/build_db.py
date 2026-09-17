"""
Clinical Trials Intelligence Explorer — Database Builder
============================================================
Loads the cleaned trials CSV into a normalized SQLite schema.

Why normalized instead of one flat table:
A trial can have multiple conditions, interventions, phases, and German
sites. Storing those as semicolon-separated strings (as the raw pull does)
works for a spreadsheet but breaks SQL aggregation — you can't easily
count "how many trials study condition X" if X is buried inside a string
with four other conditions. Splitting these into proper bridge tables is
what makes real SQL analysis (joins, GROUP BY, window functions) possible.

USAGE:
    python build_db.py
Reads:  trials_clean_v1.csv  (in this folder)
Writes: trials.db            (in this folder)
"""

import pandas as pd
import sqlite3

SOURCE_CSV = "../data/trials_clean_v1.csv"
DB_PATH = "../data/trials.db"

SCHEMA = """
DROP TABLE IF EXISTS trials;
DROP TABLE IF EXISTS trial_conditions;
DROP TABLE IF EXISTS trial_interventions;
DROP TABLE IF EXISTS trial_phases;
DROP TABLE IF EXISTS trial_germany_cities;

CREATE TABLE trials (
    nct_id                   TEXT PRIMARY KEY,
    title                    TEXT,
    status                   TEXT,
    start_date               TEXT,
    primary_completion_date  TEXT,
    completion_date          TEXT,
    study_type               TEXT,
    enrollment_count         INTEGER,
    enrollment_type          TEXT,
    allocation               TEXT,
    intervention_model       TEXT,
    masking                  TEXT,
    lead_sponsor             TEXT,
    lead_sponsor_class       TEXT,
    n_germany_sites          INTEGER,
    n_total_sites            INTEGER,
    search_condition         TEXT
);

CREATE TABLE trial_conditions (
    nct_id    TEXT,
    condition TEXT,
    FOREIGN KEY (nct_id) REFERENCES trials(nct_id)
);

CREATE TABLE trial_interventions (
    nct_id       TEXT,
    intervention TEXT,
    FOREIGN KEY (nct_id) REFERENCES trials(nct_id)
);

CREATE TABLE trial_phases (
    nct_id TEXT,
    phase  TEXT,
    FOREIGN KEY (nct_id) REFERENCES trials(nct_id)
);

CREATE TABLE trial_germany_cities (
    nct_id TEXT,
    city   TEXT,
    FOREIGN KEY (nct_id) REFERENCES trials(nct_id)
);
"""

TRIALS_COLS = [
    "nct_id", "title", "status", "start_date", "primary_completion_date",
    "completion_date", "study_type", "enrollment_count", "enrollment_type",
    "allocation", "intervention_model", "masking", "lead_sponsor",
    "lead_sponsor_class", "n_germany_sites", "n_total_sites", "search_condition",
]


def explode(df: pd.DataFrame, value_col: str, out_col: str) -> pd.DataFrame:
    """Turn a semicolon-separated column into one row per value."""
    rows = []
    for _, row in df[["nct_id", value_col]].dropna(subset=[value_col]).iterrows():
        for v in str(row[value_col]).split(";"):
            v = v.strip()
            if v:
                rows.append((row["nct_id"], v))
    return pd.DataFrame(rows, columns=["nct_id", out_col])


def main():
    df = pd.read_csv(SOURCE_CSV)
    print(f"Loaded {len(df)} rows from {SOURCE_CSV}")

    conn = sqlite3.connect(DB_PATH)
    conn.executescript(SCHEMA)

    df[TRIALS_COLS].to_sql("trials", conn, if_exists="append", index=False)

    bridges = {
        "trial_conditions": ("conditions", "condition"),
        "trial_interventions": ("interventions", "intervention"),
        "trial_phases": ("phases", "phase"),
        "trial_germany_cities": ("germany_cities", "city"),
    }
    for table, (source_col, out_col) in bridges.items():
        exploded = explode(df, source_col, out_col)
        exploded.to_sql(table, conn, if_exists="append", index=False)
        print(f"  {table}: {len(exploded)} rows")

    conn.commit()
    conn.close()
    print(f"\nDatabase built: {DB_PATH}")


if __name__ == "__main__":
    main()
