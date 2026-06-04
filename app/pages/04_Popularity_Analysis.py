"""
app/pages/04_Popularity_Analysis.py
───────────────────────────────────────
Rank vs popularity correlation, tier distributions, stability analysis.
"""

import sys, os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))

import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
import numpy as np

from app.utils.data_loader import get_data
from src.analytics import popularity_rank_correlation, popularity_by_tier

st.set_page_config(page_title="Popularity Analysis", page_icon="📊", layout="wide")

df, song_stats, artist_stats, _ = get_data()

st.title("📊 Popularity Score Analytics")
st.caption("How does listener popularity relate to chart rank? Where does it diverge?")

# ── KPIs ──────────────────────────────────────────────────────────────────────

corr = popularity_rank_correlation(df)

col1, col2, col3, col4 = st.columns(4)
col1.metric("Popularity ↔ Rank Correlation", corr,
            help="Negative = higher popularity → better rank. Closer to -1 = stronger link.")
col2.metric("Avg Popularity (Top 10)",
            round(df[df["position"] <= 10]["popularity"].mean(), 1))
col3.metric("Avg Popularity (Top 20)",
            round(df[df["position"] <= 20]["popularity"].mean(), 1))
col4.metric("Avg Popularity (Full 50)",
            round(df["popularity"].mean(), 1))

st.divider()

# ── Chart 1: Popularity vs Rank Scatter ──────────────────────────────────────

st.subheader("🔵 Popularity vs Chart Rank — Correlation Scatter")
st.caption(
    "Each dot = one song-day. Trendline shows the general relationship. "
    "Outliers above the line are underperforming; below = overperforming vs popularity."
)

fig1 = px.scatter(
    df.sample(min(5000, len(df)), random_state=42),  # sample for perf
    x="position", y="popularity",
    color="album_type",
    opacity=0.5,
    trendline="ols",
    title=f"Popularity vs Chart Rank (Pearson r = {corr})",
    labels={"position": "Chart Position", "popularity": "Popularity Score"},
    hover_data=["song", "artist", "date"],
)
fig1.update_xaxes(autorange="reversed")
st.plotly_chart(fig1, use_container_width=True)

# ── Chart 2: Popularity by Tier Box Plot ─────────────────────────────────────

st.subheader("📦 Popularity Distribution by Chart Tier")

bins   = [0, 10, 20, 50]
labels = ["Top 10", "Top 11–20", "Top 21–50"]
df_tier = df.copy()
df_tier["tier"] = (
    df_tier["position"]
    .pipe(lambda s: s.apply(
        lambda x: "Top 10" if x <= 10 else ("Top 11–20" if x <= 20 else "Top 21–50")
    ))
)

fig2 = px.box(
    df_tier,
    x="tier", y="popularity",
    color="tier",
    title="Popularity Distribution Across Chart Tiers",
    labels={"tier": "Chart Tier", "popularity": "Popularity Score"},
    category_orders={"tier": ["Top 10", "Top 11–20", "Top 21–50"]},
)
st.plotly_chart(fig2, use_container_width=True)

# ── Chart 3: Popularity Stability ────────────────────────────────────────────

st.subheader("📉 Popularity Stability — Consistent vs Volatile")
st.caption(
    "Compares rank volatility against average popularity. "
    "Ideal songs = high popularity + low volatility (top-left)."
)

fig3 = px.scatter(
    song_stats[song_stats["days_on_chart"] >= 3],
    x="rank_volatility", y="avg_popularity",
    color="days_on_chart",
    size="days_on_chart",
    hover_name="song",
    hover_data=["artist", "best_rank", "popularity_trend_score"],
    color_continuous_scale="Blues",
    title="Rank Volatility vs Average Popularity (songs with ≥3 days on chart)",
    labels={
        "rank_volatility": "Rank Volatility (Std Dev)",
        "avg_popularity": "Average Popularity",
        "days_on_chart": "Days on Chart",
    },
)
st.plotly_chart(fig3, use_container_width=True)

# ── Chart 4: Popularity Over Time ────────────────────────────────────────────

st.subheader("📅 Average Daily Popularity Over Time")
st.caption("Tracks whether overall chart popularity is trending up or down.")

daily_pop = (
    df.groupby("date")["popularity"]
    .mean()
    .reset_index(name="avg_popularity")
)

fig4 = px.line(
    daily_pop, x="date", y="avg_popularity",
    title="Daily Average Popularity Score of All Songs on Chart",
    labels={"date": "Date", "avg_popularity": "Avg Popularity"},
)
# Add rolling average
daily_pop["rolling_7d"] = daily_pop["avg_popularity"].rolling(7, min_periods=1).mean()
fig4.add_scatter(
    x=daily_pop["date"], y=daily_pop["rolling_7d"],
    mode="lines", name="7-Day Rolling Avg",
    line=dict(color="red", dash="dash"),
)
st.plotly_chart(fig4, use_container_width=True)

# ── Table: Tier Summary ───────────────────────────────────────────────────────

st.subheader("📋 Popularity by Tier — Summary Stats")
tier_summary = popularity_by_tier(df)
st.dataframe(tier_summary, use_container_width=True, hide_index=True)
