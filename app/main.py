"""
app/main.py
────────────
Streamlit entry point. Run with:  streamlit run app/main.py
"""

import sys, os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

import streamlit as st
from app.utils.data_loader import get_data
from src.analytics import global_kpis

# ── Page Config ───────────────────────────────────────────────────────────────

st.set_page_config(
    page_title="US Top 50 — Music Analytics",
    page_icon="🎵",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── Load Data ─────────────────────────────────────────────────────────────────

df, song_stats, artist_stats, val_report = get_data()

# ── Data Quality Warnings ─────────────────────────────────────────────────────

if val_report.get("duplicate_rows", 0) > 0:
    st.warning(
        f"⚠️ {val_report['duplicate_rows']} duplicate rows were removed during cleaning."
    )
if val_report.get("missing_columns"):
    st.error(f"❌ Missing columns in dataset: {val_report['missing_columns']}")

# ── Header ────────────────────────────────────────────────────────────────────

st.title("🎵 US Spotify Top 50 — Playlist Analytics")
st.markdown(
    "Deep analytics on US chart dynamics for **Atlantic Recording Corporation** — "
    "ranking stability, artist dominance, popularity trends & content insights."
)

st.divider()

# ── Global KPI Cards ──────────────────────────────────────────────────────────

kpis = global_kpis(df)

col1, col2, col3, col4 = st.columns(4)
col1.metric("🎶 Unique Songs",        kpis["total_songs"])
col2.metric("🎤 Unique Artists",      kpis["total_artists"])
col3.metric("📅 Days Tracked",        kpis["date_range_days"])
col4.metric("⭐ Avg Popularity",      kpis["avg_popularity"])

col5, col6, col7, col8 = st.columns(4)
col5.metric("📈 Avg Days on Chart",   kpis["avg_days_on_chart"])
col6.metric("👑 Most Dominant Artist",kpis["most_dominant_artist"],
            f"{kpis['dominant_artist_pct']}% of slots")
col7.metric("🏆 Longest Charting",    kpis["longest_charting_song"],
            f"{kpis['longest_chart_days']} days")
col8.metric("🔞 Explicit Content",    f"{kpis['explicit_pct']}%")

st.divider()

# ── Navigation Guide ──────────────────────────────────────────────────────────

st.subheader("📂 Dashboard Pages")
st.markdown("""
Use the **sidebar** to navigate between pages:

| Page | What it shows |
|------|--------------|
| 📅 Playlist Timeline | Rank movements over time, entry/exit analysis |
| 🎵 Song Performance | Longevity, peak vs average rank, chart survivors |
| 🎤 Artist Dominance | Leaderboard, dominance index, unique songs per artist |
| 📊 Popularity Analysis | Rank vs popularity correlation, tier distributions |
| 🔍 Content Attributes | Explicit vs clean, singles vs albums, duration impact |
""")

st.caption(
    f"Data range: **{df['date'].min().strftime('%b %d, %Y')}** → "
    f"**{df['date'].max().strftime('%b %d, %Y')}**   |   "
    f"Built with Streamlit + Plotly   |   Atlantic Recording Corporation"
)
