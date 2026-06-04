"""
app/utils/data_loader.py
─────────────────────────
Cached data loader for the Streamlit app.
Auto-downloads dataset if not found (for Streamlit Cloud).
"""

import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))

import streamlit as st
import pandas as pd

from src.preprocessing import load_clean, validate
from src.feature_engineering import enrich, build_song_stats, build_artist_stats

DATA_PATH = "data/top50_us.csv"
FILE_ID   = "1ss4ehLrhb5_X_RlEK7npanh5wfwEIm1V"


def _ensure_data():
    """Download dataset if not present (runs on Streamlit Cloud)."""
    if not os.path.exists(DATA_PATH):
        os.makedirs("data", exist_ok=True)
        try:
            import gdown
            url = f"https://drive.google.com/uc?id={FILE_ID}"
            gdown.download(url, DATA_PATH, quiet=False)
        except Exception as e:
            st.error(
                f"Dataset not found and auto-download failed: {e}\n\n"
                "Please add `data/top50_us.csv` to your GitHub repo."
            )
            st.stop()


@st.cache_data(show_spinner="Loading playlist data...")
def get_data():
    """
    Returns:
        df           — enriched full DataFrame
        song_stats   — one row per unique song
        artist_stats — one row per artist
        val_report   — validation report dict
    """
    _ensure_data()
    raw        = load_clean(DATA_PATH)
    val_report = validate(raw)
    df         = enrich(raw)
    song_stats = build_song_stats(df)
    art_stats  = build_artist_stats(df)
    return df, song_stats, art_stats, val_report


def apply_filters(
    df: pd.DataFrame,
    date_range: tuple,
    artists: list,
    rank_range: tuple,
    album_types: list,
    explicit_filter: str = "All",
) -> pd.DataFrame:
    """Apply sidebar filters to the main DataFrame."""
    mask = pd.Series(True, index=df.index)

    if date_range:
        start = pd.to_datetime(date_range[0])
        end   = pd.to_datetime(date_range[1])
        mask &= df["date"].between(start, end)

    if artists:
        mask &= df["artist"].isin(artists)

    if rank_range:
        mask &= df["position"].between(rank_range[0], rank_range[1])

    if album_types:
        mask &= df["album_type"].isin(album_types)

    if explicit_filter == "Explicit Only":
        mask &= df["is_explicit"] == True
    elif explicit_filter == "Clean Only":
        mask &= df["is_explicit"] == False

    return df[mask].copy()