"""
src/feature_engineering.py
───────────────────────────
All derived metrics: song-level, artist-level, and playlist-level KPIs.
Uses vectorized Pandas operations throughout — no Python loops.
"""

import pandas as pd
import numpy as np


# ── Song-Level Features ───────────────────────────────────────────────────────

def add_song_features(df: pd.DataFrame) -> pd.DataFrame:
    """
    Add song-level aggregated features back onto every row.
    Uses transform() so the DataFrame keeps its original shape.
    """
    df = df.copy()

    g = df.groupby("song_key")

    # Days on chart (unique dates this song appeared)
    df["days_on_chart"] = g["date"].transform("nunique")

    # Average rank (lower = better)
    df["avg_rank"] = g["position"].transform("mean").round(2)

    # Best rank achieved
    df["best_rank"] = g["position"].transform("min")

    # Rank Volatility Index — std dev of rank; NaN for single-day songs → 0
    df["rank_volatility"] = g["position"].transform("std").fillna(0).round(2)

    # Average popularity
    df["avg_popularity"] = g["popularity"].transform("mean").round(2)

    # Duration in minutes (rounded to 2dp)
    df["duration_min"] = (df["duration_ms"] / 60_000).round(2)

    return df


def popularity_trend_score(df: pd.DataFrame) -> pd.Series:
    """
    Per-song linear slope of popularity over time.
    Positive = rising, Negative = declining.
    Returns a Series indexed by song_key.
    """
    def _slope(group):
        group = group.sort_values("date")
        if len(group) < 2:
            return 0.0
        x = np.arange(len(group), dtype=float)
        y = group["popularity"].values.astype(float)
        # mask NaNs
        mask = ~np.isnan(y)
        if mask.sum() < 2:
            return 0.0
        slope = np.polyfit(x[mask], y[mask], 1)[0]
        return round(float(slope), 4)

    return df.groupby("song_key").apply(_slope).rename("popularity_trend_score")


def add_trend_score(df: pd.DataFrame) -> pd.DataFrame:
    """Merge popularity_trend_score onto the main DataFrame."""
    trend = popularity_trend_score(df).reset_index()
    return df.merge(trend, on="song_key", how="left")


# ── Artist-Level Features ─────────────────────────────────────────────────────

def build_artist_stats(df: pd.DataFrame) -> pd.DataFrame:
    """
    Build an artist-level summary DataFrame.
    Columns: artist, artist_key, unique_songs, total_appearances,
             avg_rank, best_rank, avg_popularity, dominance_index
    """
    total_slots = len(df)  # total playlist slots across all dates

    stats = (
        df.groupby(["artist_key", "artist"])
        .agg(
            unique_songs      = ("song_key", "nunique"),
            total_appearances = ("date", "count"),
            avg_rank          = ("position", "mean"),
            best_rank         = ("position", "min"),
            avg_popularity    = ("popularity", "mean"),
        )
        .reset_index()
    )

    # Dominance Index: artist's total appearances / total available slots (%)
    stats["dominance_index"] = (
        (stats["total_appearances"] / total_slots * 100).round(2)
    )

    stats["avg_rank"]       = stats["avg_rank"].round(2)
    stats["avg_popularity"] = stats["avg_popularity"].round(2)

    return stats.sort_values("total_appearances", ascending=False)


# ── Song-Level Summary Table ──────────────────────────────────────────────────

def build_song_stats(df: pd.DataFrame) -> pd.DataFrame:
    """
    One row per unique song with all KPIs.
    """
    # merge trend score in
    trend = popularity_trend_score(df)

    stats = (
        df.groupby(["song_key", "song", "artist", "artist_key",
                    "album_type", "is_explicit", "duration_min"])
        .agg(
            days_on_chart  = ("date", "nunique"),
            avg_rank       = ("position", "mean"),
            best_rank      = ("position", "min"),
            rank_volatility= ("position", "std"),
            avg_popularity = ("popularity", "mean"),
            total_tracks   = ("total_tracks", "first"),
        )
        .reset_index()
    )

    stats["rank_volatility"] = stats["rank_volatility"].fillna(0).round(2)
    stats["avg_rank"]        = stats["avg_rank"].round(2)
    stats["avg_popularity"]  = stats["avg_popularity"].round(2)

    stats = stats.merge(trend.reset_index(), on="song_key", how="left")

    return stats.sort_values("days_on_chart", ascending=False)


# ── Rank Movement ─────────────────────────────────────────────────────────────

def add_rank_movement(df: pd.DataFrame) -> pd.DataFrame:
    """
    Add rank_change column: positive = dropped, negative = rose in rank.
    Computed per song across sorted dates.
    """
    df = df.copy().sort_values(["song_key", "date"])
    df["rank_change"] = df.groupby("song_key")["position"].diff()
    return df


# ── Master Enrich ─────────────────────────────────────────────────────────────

def enrich(df: pd.DataFrame) -> pd.DataFrame:
    """
    Apply all feature engineering in the correct order.
    Call this once after preprocessing.clean().
    """
    df = add_song_features(df)
    df = add_trend_score(df)
    df = add_rank_movement(df)
    return df
