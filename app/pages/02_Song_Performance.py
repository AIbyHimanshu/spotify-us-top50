"""
app/pages/02_Song_Performance.py
─────────────────────────────────────
Longevity, peak vs average rank, popularity trend scores.
"""

import sys, os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))

import streamlit as st
import plotly.express as px
import plotly.graph_objects as go

from app.utils.data_loader import get_data

st.set_page_config(page_title="Song Performance", page_icon="🎵", layout="wide")

df, song_stats, artist_stats, _ = get_data()

# ── Sidebar ───────────────────────────────────────────────────────────────────

st.sidebar.header("🔧 Filters")
min_days = st.sidebar.slider(
    "Minimum Days on Chart", 1,
    int(song_stats["days_on_chart"].max()), 1
)
filtered_songs = song_stats[song_stats["days_on_chart"] >= min_days]

st.title("🎵 Song Performance Analysis")
st.caption(f"Analysing **{len(filtered_songs)}** songs with ≥{min_days} days on chart")

# ── KPI Row ───────────────────────────────────────────────────────────────────

col1, col2, col3, col4 = st.columns(4)
col1.metric("Total Songs",         len(filtered_songs))
col2.metric("Avg Days on Chart",   round(filtered_songs["days_on_chart"].mean(), 1))
col3.metric("Avg Best Rank",       round(filtered_songs["best_rank"].mean(), 1))
col4.metric("Avg Popularity",      round(filtered_songs["avg_popularity"].mean(), 1))

st.divider()

# ── Chart 1: Top Songs by Longevity ──────────────────────────────────────────

st.subheader("🏅 Top 20 Songs by Days on Chart")

top_longevity = filtered_songs.nlargest(20, "days_on_chart")

fig1 = px.bar(
    top_longevity,
    x="days_on_chart", y="song",
    orientation="h",
    color="avg_popularity",
    color_continuous_scale="Viridis",
    title="Songs with Longest Playlist Presence",
    labels={"days_on_chart": "Days on Chart", "song": "Song",
            "avg_popularity": "Avg Popularity"},
    text="days_on_chart",
    hover_data=["artist", "best_rank", "avg_rank"],
)
fig1.update_layout(yaxis=dict(autorange="reversed"))
st.plotly_chart(fig1, use_container_width=True)

# ── Chart 2: Peak Rank vs Longevity (One-Hit Wonders vs Chart Stayers) ────────

st.subheader("🎯 Peak Rank vs Longevity — One-Hit Wonders vs Chart Survivors")
st.caption(
    "Bottom-left = peaked high AND stayed long (elite performers). "
    "Top-right = low peak, short stay (fleeting entries)."
)

fig2 = px.scatter(
    filtered_songs,
    x="best_rank", y="days_on_chart",
    color="avg_popularity",
    size="avg_popularity",
    hover_name="song",
    hover_data=["artist", "rank_volatility", "popularity_trend_score"],
    color_continuous_scale="Plasma",
    title="Peak Rank vs Days on Chart",
    labels={
        "best_rank": "Best Rank Achieved (lower = better)",
        "days_on_chart": "Days on Chart",
        "avg_popularity": "Avg Popularity",
    },
)
fig2.update_xaxes(autorange="reversed")
st.plotly_chart(fig2, use_container_width=True)

# ── Chart 3: Rank Volatility ──────────────────────────────────────────────────

st.subheader("📉 Rank Stability — Most Volatile Songs")
st.caption("High volatility = rank bounced around a lot. Low = consistent performer.")

top_volatile = filtered_songs[filtered_songs["days_on_chart"] >= 5].nlargest(15, "rank_volatility")

fig3 = px.bar(
    top_volatile,
    x="rank_volatility", y="song",
    orientation="h",
    color="rank_volatility",
    color_continuous_scale="Reds",
    title="Top 15 Most Volatile Songs (≥5 days on chart)",
    labels={"rank_volatility": "Rank Volatility (Std Dev)", "song": "Song"},
    text=top_volatile["rank_volatility"].round(1),
    hover_data=["artist", "avg_rank", "best_rank"],
)
fig3.update_layout(yaxis=dict(autorange="reversed"))
st.plotly_chart(fig3, use_container_width=True)

# ── Chart 4: Popularity Trend Score ──────────────────────────────────────────

st.subheader("📈 Popularity Trend Score — Rising vs Declining Songs")
st.caption("Positive = gaining popularity over time. Negative = fading.")

trend_df = filtered_songs[filtered_songs["days_on_chart"] >= 5].copy()
trend_df = trend_df.sort_values("popularity_trend_score")

fig4 = px.bar(
    trend_df.head(30),
    x="popularity_trend_score", y="song",
    orientation="h",
    color="popularity_trend_score",
    color_continuous_scale="RdYlGn",
    title="Popularity Trend Score (Top 30 songs with ≥5 days on chart)",
    labels={"popularity_trend_score": "Trend Score (slope)", "song": "Song"},
    hover_data=["artist", "days_on_chart", "avg_popularity"],
)
st.plotly_chart(fig4, use_container_width=True)

# ── Full Table ────────────────────────────────────────────────────────────────

st.subheader("📋 Full Song Stats Table")

display_cols = [
    "song", "artist", "days_on_chart", "best_rank", "avg_rank",
    "rank_volatility", "avg_popularity", "popularity_trend_score",
    "album_type", "is_explicit", "duration_min"
]
st.dataframe(
    filtered_songs[display_cols].reset_index(drop=True),
    use_container_width=True,
    hide_index=True,
)
