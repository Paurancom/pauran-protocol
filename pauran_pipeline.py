"""
PAURAN PROTOCOL v1.0
====================
Deterministic pipeline: Excel input → CSV + JSON output

Rules (from protocol):
- Data source: World Bank Pink Sheet, Monthly Indices (2010=100)
- No interpolation
- No backfilling
- Missing data = no calculation for that period
- v2 weights: Energy 20%, Food 40%, Metals 30%, Precious 10%
- Smoothing: 3-month moving average (min 3 periods, no partial windows)
"""

import pandas as pd
import numpy as np
import json
import sys
import os
from datetime import datetime, timezone

# ── PROTOCOL CONSTANTS (do not modify) ────────────────────────────────────────

PROTOCOL_VERSION = "v2"
BASE_YEAR        = 2010
SHEET_NAME       = "Monthly Indices"
HEADER_ROW       = 9  # 0-indexed

WEIGHTS = {
    "Energy":          0.20,
    "Food":            0.40,
    "Metals":          0.30,
    "Precious_Metals": 0.10,
}

COLUMN_MAP = {
    "iENERGY":     "Energy",
    "iFOOD":       "Food",
    "iMETMIN":     "Metals",
    "iPRECIOUSMET":"Precious_Metals",
}

# Positional fallback (new Pink Sheet format, post-2021)
# Col 0=Date, 2=Energy, 6=Food, 14=Metals, 16=Precious
COLUMN_POS = {
    "Energy":          2,
    "Food":            6,
    "Metals":          14,
    "Precious_Metals": 16,
}

DATE_PATTERN = r"^\d{4}M\d{2}$"  # e.g. 1960M01


# ── STEP 1: LOAD ──────────────────────────────────────────────────────────────

def load(filepath: str) -> pd.DataFrame:
    """
    Load World Bank Pink Sheet, Monthly Indices sheet.
    Returns raw dataframe with original column names.
    """
    if not os.path.exists(filepath):
        raise FileNotFoundError(f"File not found: {filepath}")

    df = pd.read_excel(filepath, sheet_name=SHEET_NAME, header=HEADER_ROW)
    return df


# ── STEP 2: EXTRACT ───────────────────────────────────────────────────────────

def extract(df: pd.DataFrame) -> pd.DataFrame:
    """
    Extract date + 4 component columns.
    Tries named column mapping first, falls back to positional mapping.
    Protocol rule: no interpolation, no backfill.
    Missing data rows are dropped entirely.
    """
    # Try named column mapping first
    df_named = df.rename(columns=COLUMN_MAP)
    date_col = df_named.columns[0]
    df_named = df_named.rename(columns={date_col: "Date"})

    needed = ["Date"] + list(WEIGHTS.keys())
    has_named = all(c in df_named.columns for c in needed)

    if has_named:
        df_work = df_named[needed].copy()
    else:
        # Positional fallback for newer Pink Sheet format
        print("  [Info] Named columns not found, using positional mapping.")
        df_work = pd.DataFrame()
        df_work["Date"] = df.iloc[:, 0].astype(str)
        for col_name, pos in COLUMN_POS.items():
            df_work[col_name] = pd.to_numeric(df.iloc[:, pos], errors="coerce")

    # Filter date rows only (1960M01 format)
    df_work = df_work[df_work["Date"].astype(str).str.match(DATE_PATTERN)].copy()

    # Parse date
    df_work["Date"] = pd.to_datetime(
        df_work["Date"].astype(str).str.replace("M", "-"),
        format="%Y-%m"
    )

    # Numeric conversion
    for col in WEIGHTS.keys():
        df_work[col] = pd.to_numeric(df_work[col], errors="coerce")

    # Protocol rule: missing data = no calculation
    before = len(df_work)
    df_work = df_work.dropna(subset=list(WEIGHTS.keys()))
    dropped = before - len(df_work)
    if dropped > 0:
        print(f"  [Protocol] {dropped} row(s) dropped — missing data (no interpolation applied)")

    df_work = df_work.sort_values("Date").reset_index(drop=True)
    return df_work


# ── STEP 3: CALCULATE ─────────────────────────────────────────────────────────

def calculate(df: pd.DataFrame) -> pd.DataFrame:
    """
    Apply v2 formula and 3-month smoothing.

    Formula (Section 5.1):
        Pauran_raw = 0.20×E + 0.40×F + 0.30×M + 0.10×P

    Smoothing (Section 5.2):
        Pauran_t = (raw_t + raw_{t-1} + raw_{t-2}) / 3
        min_periods=3 → no partial windows (protocol: no partial data)
    """
    df = df.copy()

    df["Pauran_raw"] = (
        WEIGHTS["Energy"]          * df["Energy"] +
        WEIGHTS["Food"]            * df["Food"] +
        WEIGHTS["Metals"]          * df["Metals"] +
        WEIGHTS["Precious_Metals"] * df["Precious_Metals"]
    )

    # 3-month moving average, min_periods=3 (no partial windows)
    df["Pauran"] = df["Pauran_raw"].rolling(window=3, min_periods=3).mean()

    return df


# ── STEP 4: EXPORT ────────────────────────────────────────────────────────────

def export(df: pd.DataFrame, out_dir: str = "."):
    """
    Export to CSV and JSON.
    Output columns: Date, Energy, Food, Metals, Precious_Metals, Pauran_raw, Pauran
    Rows where Pauran is NaN (first 2 rows, smoothing warmup) are excluded from output.
    """
    os.makedirs(out_dir, exist_ok=True)

    # Only rows with valid Pauran value
    out = df[df["Pauran"].notna()].copy()
    out["Date"] = out["Date"].dt.strftime("%Y-%m")

    output_cols = ["Date", "Energy", "Food", "Metals", "Precious_Metals", "Pauran_raw", "Pauran"]

    # ── CSV ──
    csv_path = os.path.join(out_dir, "pauran_output.csv")
    out[output_cols].to_csv(csv_path, index=False, float_format="%.6f")

    # ── JSON ──
    records = out[output_cols].to_dict(orient="records")

    json_payload = {
        "protocol":    "Pauran",
        "version":     PROTOCOL_VERSION,
        "base_year":   BASE_YEAR,
        "data_source": "World Bank – Commodity Markets Outlook (Pink Sheet), Monthly Indices",
        "weights": {
            "Energy":          WEIGHTS["Energy"],
            "Food":            WEIGHTS["Food"],
            "Metals":          WEIGHTS["Metals"],
            "Precious_Metals": WEIGHTS["Precious_Metals"],
        },
        "smoothing":      "3-month moving average",
        "generated_at":   datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "period_start":   out["Date"].iloc[0],
        "period_end":     out["Date"].iloc[-1],
        "total_months":   len(out),
        "data":           records,
    }

    json_path = os.path.join(out_dir, "pauran_output.json")
    with open(json_path, "w", encoding="utf-8") as f:
        json.dump(json_payload, f, indent=2, ensure_ascii=False)

    return csv_path, json_path


# ── MAIN ──────────────────────────────────────────────────────────────────────

def run(excel_path: str, out_dir: str = "."):
    print(f"\nPAURAN PROTOCOL {PROTOCOL_VERSION}")
    print("=" * 50)

    print(f"[1/4] Loading: {excel_path}")
    raw = load(excel_path)

    print(f"[2/4] Extracting components...")
    df = extract(raw)
    print(f"      Series: {df['Date'].iloc[0].strftime('%Y-%m')} → {df['Date'].iloc[-1].strftime('%Y-%m')} ({len(df)} months)")

    print(f"[3/4] Calculating Pauran {PROTOCOL_VERSION}...")
    df = calculate(df)
    valid = df["Pauran"].notna().sum()
    print(f"      Valid Pauran values: {valid}")
    print(f"      Latest Pauran (raw):      {df['Pauran_raw'].iloc[-1]:.4f}")
    print(f"      Latest Pauran (3M smooth):{df['Pauran'].iloc[-1]:.4f}")

    print(f"[4/4] Exporting...")
    csv_path, json_path = export(df, out_dir)
    print(f"      CSV:  {csv_path}")
    print(f"      JSON: {json_path}")

    print("\n✓ Done.")
    return df


if __name__ == "__main__":
    # Usage: python pauran_pipeline.py <excel_file> [output_dir]
    if len(sys.argv) < 2:
        print("Usage: python pauran_pipeline.py CMOHistoricalDataMonthly.xlsx [output_dir]")
        sys.exit(1)

    excel_file = sys.argv[1]
    output_dir = sys.argv[2] if len(sys.argv) > 2 else "pauran_output"

    run(excel_file, output_dir)
