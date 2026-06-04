"""
app/pages/01_Playlist_Timeline.py
─────────────────────────────────────
Rank movements, entry/exit, fast risers, slow decliners.
"""

import sys, os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))

import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd

from app.utils.data_loader import get_data, apply_filters
from src.analytics import fast_risers, slow_decliners, entry_exit_analysis

st.set_page_config(page_title="Playlist Timeline", page_icon="📅", layout="wide")

# ── Load ──────────────────────────────────────────────────────────────────────

df, song_stats, artist_stats, _ = get_data()

# ── Sidebar Filters ───────────────────────────────────────────────────────────

st.sidebar.header("🔧 Filters")

date_min, date_max = df["date"].min().date(), df["date"].max().date()
date_range = st.sidebar.date_input(
    "Date Range", value=[date_min, date_max],
    min_value=date_min, max_value=date_max
)

all_artists = sorted(df["artist"].unique().tolist())
artists = st.sidebar.multiselect("Artist", all_artists, placeholder="All artists")

rank_range = st.sidebar.slider("Rank Range", 1, 50, (1, 50))

album_types = st.sidebar.multiselect(
    "Album Type", df["album_type"].dropna().unique().tolist(),
    default=df["album_type"].dropna().unique().tolist()
)

explicit_filter = st.sidebar.radio(
    "Content", ["All", "Explicit Only", "Clean Only"]
)

# ── Apply filters ─────────────────────────────────────────────────────────────

filtered = apply_filters(
    df,
    date_range=date_range if len(date_range) == 2 else None,
    artists=artists,
    rank_range=rank_range,
    album_types=album_types,
    explicit_filter=explicit_filter,
)

st.title("📅 Playlist Timeline Explorer")
st.caption(f"Showing **{filtered['song_key'].nunique()} songs** across **{filtered['date'].nunique()} days**")

# ── Chart 1: Rank Over Time ───────────────────────────────────────────────────

st.subheader("📈 Rank Over Time")

# Limit to top 15 songs by appearances to keep chart readable
top_songs = (
    filtered.groupby("song")["date"].count()
    .nlargest(15).index.tolist()
)
chart_df = filtered[filtered["song"].isin(top_songs)].sort_values("date")

fig1 = px.line(
    chart_df,
    x="date", y="position", color="song",
    title="Chart Position Over Time (Top 15 songs by appearances)",
    labels={"position": "Chart Position", "date": "Date"},
)
fig1.update_yaxes(autorange="reversed", title="Chart Position (1 = best)")
fig1.update_layout(hovermode="x unified", legend_title="Song")
st.plotly_chart(fig1, use_container_width=True)

# ── Chart 2: Daily Heatmap ────────────────────────────────────────────────────

st.subheader("🗓️ Daily Position Heatmap")
st.caption("Visualizes which songs held which positions on each day.")

pivot = filtered.pivot_table(
    index="song", columns="date", values="position", aggfunc="min"
)
# Show top 20 songs by most appearances
top20 = filtered["song"].value_counts().head(20).index.tolist()
pivot_top = pivot.loc[pivot.index.isin(top20)]

if not pivot_top.empty:
    fig2 = px.imshow(
        pivot_top,
        color_continuous_scale="RdYlGn_r",
        aspect="auto",
        title="Heatmap: Chart Position by Song & Date",
        labels={"color": "Rank"},
    )
    fig2.update_layout(coloraxis_colorbar=dict(title="Rank"))
    st.plotly_chart(fig2, use_container_width=True)
else:
    st.info("Not enough data for heatmap with current filters.")

# ── Chart 3: Fast Risers ──────────────────────────────────────────────────────

st.subheader("🚀 Fast Risers")
st.caption("Songs with the single biggest single-day rank jump.")

risers = fast_risers(filtered, top_n=10)
if not risers.empty:
    fig3 = px.bar(
        risers,
        x="positions_gained", y="song",
        orientation="h",
        color="positions_gained",
        color_continuous_scale="Greens",
        title="Top 10 Biggest Single-Day Rank Jumps",
        labels={"positions_gained": "Positions Gained", "song": "Song"},
        text="positions_gained",
    )
    fig3.update_layout(yaxis=dict(autorange="reversed"))
    st.plotly_chart(fig3, use_container_width=True)
else:
    st.info("No rank movement data available with current filters.")

# ── Table: Entry / Exit Analysis ─────────────────────────────────────────────

st.subheader("🚪 Entry & Exit Analysis")

entry_exit = entry_exit_analysis(filtered)
st.dataframe(
    entry_exit.sort_values("days_on_chart", ascending=False)
    .reset_index(drop=True),
    use_container_width=True,
    hide_index=True,
)
