"""
app/pages/03_Artist_Dominance.py
─────────────────────────────────────
Artist leaderboard, dominance index, unique songs.
"""

import sys, os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))

import streamlit as st
import plotly.express as px
import plotly.graph_objects as go

from app.utils.data_loader import get_data

st.set_page_config(page_title="Artist Dominance", page_icon="🎤", layout="wide")

df, song_stats, artist_stats, _ = get_data()

st.title("🎤 Artist Dominance Leaderboard")
st.caption("Who owns the US Top 50? Measured by appearances, unique songs, and dominance index.")

# ── KPIs ──────────────────────────────────────────────────────────────────────

top_artist = artist_stats.iloc[0]
col1, col2, col3, col4 = st.columns(4)
col1.metric("Total Artists",           len(artist_stats))
col2.metric("Most Dominant Artist",    top_artist["artist"])
col3.metric("Dominant Artist Appearances", int(top_artist["total_appearances"]))
col4.metric("Dominance Index",         f"{top_artist['dominance_index']}%")

st.divider()

# ── Chart 1: Top Artists by Appearances ──────────────────────────────────────

st.subheader("👑 Top 20 Artists by Total Playlist Appearances")

top20 = artist_stats.head(20)

fig1 = px.bar(
    top20,
    x="total_appearances", y="artist",
    orientation="h",
    color="dominance_index",
    color_continuous_scale="Sunset",
    title="Total Playlist Appearances (all dates × positions)",
    labels={
        "total_appearances": "Total Appearances",
        "artist": "Artist",
        "dominance_index": "Dominance Index (%)",
    },
    text=top20["total_appearances"],
    hover_data=["unique_songs", "avg_rank", "avg_popularity"],
)
fig1.update_layout(yaxis=dict(autorange="reversed"))
st.plotly_chart(fig1, use_container_width=True)

# ── Chart 2: Unique Songs vs Appearances ─────────────────────────────────────

st.subheader("🎶 Song Diversity vs Presence — Catalog Breadth")
st.caption(
    "Artists in the top-right have BOTH many songs AND many appearances — "
    "true chart dominators. Artists high on Y but left on X are one-artist-many-appearances."
)

fig2 = px.scatter(
    artist_stats.head(40),
    x="unique_songs", y="total_appearances",
    size="dominance_index",
    color="avg_popularity",
    hover_name="artist",
    color_continuous_scale="Turbo",
    title="Unique Songs vs Total Appearances (Top 40 Artists)",
    labels={
        "unique_songs": "Unique Songs on Chart",
        "total_appearances": "Total Appearances",
        "dominance_index": "Dominance Index (%)",
    },
    text="artist",
)
fig2.update_traces(textposition="top center", textfont_size=9)
st.plotly_chart(fig2, use_container_width=True)

# ── Chart 3: Artist Average Rank ─────────────────────────────────────────────

st.subheader("📊 Average Chart Position — Top 20 Artists")
st.caption("Lower = better. Shows which artists consistently rank high, not just appear often.")

fig3 = px.bar(
    top20.sort_values("avg_rank"),
    x="avg_rank", y="artist",
    orientation="h",
    color="avg_rank",
    color_continuous_scale="RdYlGn_r",
    title="Average Chart Rank (lower = stronger performer)",
    labels={"avg_rank": "Average Rank (1=best)", "artist": "Artist"},
    text=top20.sort_values("avg_rank")["avg_rank"].round(1),
)
fig3.update_layout(yaxis=dict(autorange="reversed"))
st.plotly_chart(fig3, use_container_width=True)

# ── Chart 4: Artist Timeline – Appearances Over Time ─────────────────────────

st.subheader("📅 Artist Presence Over Time")

selected_artists = st.multiselect(
    "Select Artists to Compare",
    options=artist_stats["artist"].tolist(),
    default=artist_stats["artist"].head(5).tolist(),
)

if selected_artists:
    timeline_df = (
        df[df["artist"].isin(selected_artists)]
        .groupby(["date", "artist"])
        .size()
        .reset_index(name="daily_appearances")
    )
    fig4 = px.line(
        timeline_df,
        x="date", y="daily_appearances", color="artist",
        title="Daily Playlist Appearances Over Time",
        labels={"daily_appearances": "Songs on Playlist", "date": "Date"},
    )
    st.plotly_chart(fig4, use_container_width=True)

# ── Full Table ────────────────────────────────────────────────────────────────

st.subheader("📋 Full Artist Stats Table")
st.dataframe(
    artist_stats.drop(columns=["artist_key"]).reset_index(drop=True),
    use_container_width=True,
    hide_index=True,
)
