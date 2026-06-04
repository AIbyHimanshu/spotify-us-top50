"""
src/preprocessing.py
────────────────────
Handles all data loading, validation, and cleaning.
"""

import pandas as pd
import numpy as np


# ── Constants ────────────────────────────────────────────────────────────────

DATA_PATH = "data/top50_us.csv"

REQUIRED_COLUMNS = [
    "date", "position", "song", "artist",
    "popularity", "duration_ms", "album_type",
    "total_tracks", "is_explicit",
]


# ── Main Loader ───────────────────────────────────────────────────────────────

def load_raw(path: str = DATA_PATH) -> pd.DataFrame:
    """Load CSV and return raw DataFrame."""
    df = pd.read_csv(path)
    return df


def validate(df: pd.DataFrame) -> dict:
    """
    Run validation checks and return a report dict.
    Does NOT raise — just reports so the dashboard can surface warnings.
    """
    report = {}

    # Missing columns
    missing_cols = [c for c in REQUIRED_COLUMNS if c not in df.columns]
    report["missing_columns"] = missing_cols

    # Rank range
    if "position" in df.columns:
        invalid_ranks = df[~df["position"].between(1, 50)]
        report["invalid_rank_count"] = len(invalid_ranks)

    # Duplicates (same song+date+artist)
    if all(c in df.columns for c in ["date", "song", "artist"]):
        dupes = df.duplicated(subset=["date", "song", "artist"]).sum()
        report["duplicate_rows"] = int(dupes)

    # Missing values
    report["null_counts"] = df.isnull().sum().to_dict()

    return report


def clean(df: pd.DataFrame) -> pd.DataFrame:
    """
    Apply all cleaning steps and return a clean DataFrame.
    """
    df = df.copy()

    # ── 1. Normalize text columns ─────────────────────────────────────────────
    # Strip + normalize but keep display casing — store lowercase key separately
    df["song"]   = df["song"].astype(str).str.strip()
    df["artist"] = df["artist"].astype(str).str.strip()

    # Lowercase keys for safe groupby (avoids duplicate groups from casing)
    df["song_key"]   = df["song"].str.lower()
    df["artist_key"] = df["artist"].str.lower()

    # ── 2. Parse dates ────────────────────────────────────────────────────────
    df["date"] = pd.to_datetime(df["date"], errors="coerce")
    df = df.dropna(subset=["date"])  # drop rows with unparseable dates

    # ── 3. Enforce types ─────────────────────────────────────────────────────
    df["position"]     = pd.to_numeric(df["position"], errors="coerce").astype("Int64")
    df["popularity"]   = pd.to_numeric(df["popularity"], errors="coerce")
    df["duration_ms"]  = pd.to_numeric(df["duration_ms"], errors="coerce")
    df["total_tracks"] = pd.to_numeric(df["total_tracks"], errors="coerce").astype("Int64")

    # is_explicit: handle bool / 0-1 / "True"/"False" strings
    if df["is_explicit"].dtype == object:
        df["is_explicit"] = df["is_explicit"].str.lower().map(
            {"true": True, "false": False, "1": True, "0": False}
        )
    df["is_explicit"] = df["is_explicit"].astype(bool)

    # album_type: normalize casing
    df["album_type"] = df["album_type"].astype(str).str.strip().str.title()

    # ── 4. Drop invalid ranks ─────────────────────────────────────────────────
    df = df[df["position"].between(1, 50)]

    # ── 5. Drop exact duplicates ──────────────────────────────────────────────
    df = df.drop_duplicates(subset=["date", "song_key", "artist_key"])

    # ── 6. Sort ───────────────────────────────────────────────────────────────
    df = df.sort_values(["date", "position"]).reset_index(drop=True)

    return df


def load_clean(path: str = DATA_PATH) -> pd.DataFrame:
    """Convenience: load + clean in one call."""
    raw = load_raw(path)
    return clean(raw)