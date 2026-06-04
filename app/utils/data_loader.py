"""
app/utils/data_loader.py
─────────────────────────
Cached data loader for the Streamlit app.
@st.cache_data ensures the CSV is only read and processed ONCE per session.
"""

import sys
import os

# Allow imports from project root
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))

import streamlit as st
import pandas as pd

from src.preprocessing import load_clean, validate
from src.feature_engineering import enrich, build_song_stats, build_artist_stats


DATA_PATH = "data/top50_us.csv"


@st.cache_data(show_spinner="Loading playlist data...")
def get_data():
    """
    Returns:
        df          — enriched full DataFrame (one row per song-date)
        song_stats  — one row per unique song with all KPIs
        artist_stats— one row per artist with dominance metrics
        val_report  — validation report dict (for data quality warnings)
    """
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
    """
    Apply sidebar filters to the main DataFrame.
    All filters are optional (pass None/empty to skip).
    """
    mask = pd.Series(True, index=df.index)

    if date_range:
        start, end = pd.to_datetime(date_range[0]), pd.to_datetime(date_range[1])
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
