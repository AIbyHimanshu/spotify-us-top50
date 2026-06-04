"""
src/analytics.py
─────────────────
Pure analytics functions. No Streamlit, no plotting.
Each function returns a DataFrame ready for visualization.
"""

import pandas as pd
import numpy as np


# ── Playlist-Level ────────────────────────────────────────────────────────────

def daily_rank_distribution(df: pd.DataFrame) -> pd.DataFrame:
    """Count how many unique songs appeared at each position across all dates."""
    return (
        df.groupby("position")["song_key"]
        .nunique()
        .reset_index(name="unique_songs")
    )


def entry_exit_analysis(df: pd.DataFrame) -> pd.DataFrame:
    """
    For each song: first_seen, last_seen, entry_rank, exit_rank.
    """
    g = df.sort_values("date").groupby("song_key")
    result = pd.DataFrame({
        "song"       : df.groupby("song_key")["song"].first(),
        "artist"     : df.groupby("song_key")["artist"].first(),
        "first_seen" : g["date"].min(),
        "last_seen"  : g["date"].max(),
        "entry_rank" : g["position"].first(),
        "exit_rank"  : g["position"].last(),
        "days_on_chart": g["date"].nunique(),
    }).reset_index()
    return result


def fast_risers(df: pd.DataFrame, top_n: int = 10) -> pd.DataFrame:
    """Songs with the largest single-day rank improvement (rank drop)."""
    has_change = df.dropna(subset=["rank_change"])
    # Negative rank_change means rank number went down = rose in chart
    risers = (
        has_change.nsmallest(top_n, "rank_change")
        [["date", "song", "artist", "position", "rank_change"]]
        .copy()
    )
    risers["rank_change"] = risers["rank_change"].abs().astype(int)
    risers = risers.rename(columns={"rank_change": "positions_gained"})
    return risers


def slow_decliners(df: pd.DataFrame, top_n: int = 10) -> pd.DataFrame:
    """Songs that stayed on chart longest while gradually losing rank."""
    from src.feature_engineering import build_song_stats
    stats = build_song_stats(df)
    # High rank_volatility + positive trend_score = declining
    decliners = stats[stats["days_on_chart"] >= 7].copy()
    decliners = decliners.sort_values(
        ["days_on_chart", "popularity_trend_score"]
    ).head(top_n)
    return decliners[["song", "artist", "days_on_chart",
                       "avg_rank", "rank_volatility", "popularity_trend_score"]]


# ── Popularity Analytics ──────────────────────────────────────────────────────

def popularity_rank_correlation(df: pd.DataFrame) -> float:
    """Pearson correlation between popularity and position."""
    return df[["popularity", "position"]].corr().iloc[0, 1].round(4)


def popularity_by_tier(df: pd.DataFrame) -> pd.DataFrame:
    """Average popularity for Top 10, Top 20, Top 50."""
    bins   = [0, 10, 20, 50]
    labels = ["Top 10", "Top 11–20", "Top 21–50"]
    df = df.copy()
    df["tier"] = pd.cut(df["position"], bins=bins, labels=labels)
    return (
        df.groupby("tier", observed=True)["popularity"]
        .agg(["mean", "median", "std"])
        .reset_index()
        .rename(columns={"mean": "avg_popularity",
                         "median": "median_popularity",
                         "std": "std_popularity"})
    )


# ── Content Attribute Analytics ───────────────────────────────────────────────

def explicit_vs_clean(df: pd.DataFrame) -> pd.DataFrame:
    """Compare explicit vs non-explicit across key metrics."""
    return (
        df.groupby("is_explicit")
        .agg(
            song_count     = ("song_key", "nunique"),
            avg_rank       = ("position", "mean"),
            avg_popularity = ("popularity", "mean"),
            avg_days       = ("days_on_chart", "mean"),
        )
        .reset_index()
        .assign(
            label=lambda x: x["is_explicit"].map(
                {True: "Explicit", False: "Clean"}
            )
        )
    )


def album_type_comparison(df: pd.DataFrame) -> pd.DataFrame:
    """Compare Singles vs Album tracks across key metrics."""
    return (
        df.groupby("album_type")
        .agg(
            song_count     = ("song_key", "nunique"),
            avg_rank       = ("position", "mean"),
            avg_popularity = ("popularity", "mean"),
            avg_days       = ("days_on_chart", "mean"),
        )
        .reset_index()
    )


def duration_buckets(df: pd.DataFrame) -> pd.DataFrame:
    """
    Bucket songs by duration and compare popularity & rank.
    Buckets: <2min, 2-3min, 3-4min, 4-5min, >5min
    """
    df = df.copy()
    bins   = [0, 2, 3, 4, 5, 100]
    labels = ["<2 min", "2–3 min", "3–4 min", "4–5 min", ">5 min"]
    df["duration_bucket"] = pd.cut(
        df["duration_min"], bins=bins, labels=labels
    )
    return (
        df.groupby("duration_bucket", observed=True)
        .agg(
            song_count     = ("song_key", "nunique"),
            avg_popularity = ("popularity", "mean"),
            avg_rank       = ("position", "mean"),
        )
        .reset_index()
    )


# ── Global KPIs ───────────────────────────────────────────────────────────────

def global_kpis(df: pd.DataFrame) -> dict:
    """
    Top-level KPI values for the dashboard header.
    """
    from src.feature_engineering import build_artist_stats, build_song_stats

    song_stats   = build_song_stats(df)
    artist_stats = build_artist_stats(df)

    most_dominant = artist_stats.iloc[0]
    longest_song  = song_stats.iloc[0]
    explicit_pct  = df["is_explicit"].mean() * 100

    return {
        "total_songs"           : int(df["song_key"].nunique()),
        "total_artists"         : int(df["artist_key"].nunique()),
        "date_range_days"       : int((df["date"].max() - df["date"].min()).days),
        "avg_popularity"        : round(df["popularity"].mean(), 1),
        "avg_days_on_chart"     : round(song_stats["days_on_chart"].mean(), 1),
        "most_dominant_artist"  : most_dominant["artist"],
        "dominant_artist_pct"   : most_dominant["dominance_index"],
        "longest_charting_song" : longest_song["song"],
        "longest_chart_days"    : int(longest_song["days_on_chart"]),
        "explicit_pct"          : round(explicit_pct, 1),
    }
