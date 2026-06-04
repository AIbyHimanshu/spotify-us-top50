"""
app/pages/05_Content_Attributes.py
───────────────────────────────────────
Explicit vs clean, singles vs albums, duration impact.
"""

import sys, os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))

import streamlit as st
import plotly.express as px
import plotly.graph_objects as go

from app.utils.data_loader import get_data
from src.analytics import explicit_vs_clean, album_type_comparison, duration_buckets

st.set_page_config(page_title="Content Attributes", page_icon="🔍", layout="wide")

df, song_stats, artist_stats, _ = get_data()

st.title("🔍 Content Attribute Analysis")
st.caption(
    "Does explicit content perform better? Do singles outlast album tracks? "
    "What's the sweet spot for song length?"
)

# ── Section 1: Explicit vs Clean ─────────────────────────────────────────────

st.subheader("Explicit vs Clean Content Performance")

explicit_df = explicit_vs_clean(df)

col1, col2 = st.columns(2)

with col1:
    fig1a = px.bar(
        explicit_df,
        x="label", y="avg_popularity",
        color="label",
        title="Average Popularity",
        labels={"avg_popularity": "Avg Popularity", "label": ""},
        text=explicit_df["avg_popularity"].round(1),
        color_discrete_map={"Explicit": "#EF553B", "Clean": "#636EFA"},
    )
    st.plotly_chart(fig1a, use_container_width=True)

with col2:
    fig1b = px.bar(
        explicit_df,
        x="label", y="avg_rank",
        color="label",
        title="Average Chart Rank (lower = better)",
        labels={"avg_rank": "Avg Rank", "label": ""},
        text=explicit_df["avg_rank"].round(1),
        color_discrete_map={"Explicit": "#EF553B", "Clean": "#636EFA"},
    )
    fig1b.update_yaxes(autorange="reversed")
    st.plotly_chart(fig1b, use_container_width=True)

col3, col4 = st.columns(2)

with col3:
    fig1c = px.bar(
        explicit_df,
        x="label", y="avg_days",
        color="label",
        title="Average Days on Chart",
        labels={"avg_days": "Avg Days", "label": ""},
        text=explicit_df["avg_days"].round(1),
        color_discrete_map={"Explicit": "#EF553B", "Clean": "#636EFA"},
    )
    st.plotly_chart(fig1c, use_container_width=True)

with col4:
    fig1d = px.pie(
        explicit_df,
        values="song_count", names="label",
        title="Share of Unique Songs on Chart",
        color="label",
        color_discrete_map={"Explicit": "#EF553B", "Clean": "#636EFA"},
    )
    st.plotly_chart(fig1d, use_container_width=True)

st.markdown("---")

# ── Section 2: Single vs Album Track ─────────────────────────────────────────

st.subheader("💿 Single vs Album Track Performance")

album_df = album_type_comparison(df)

col5, col6, col7 = st.columns(3)

with col5:
    fig2a = px.bar(
        album_df,
        x="album_type", y="avg_popularity",
        color="album_type",
        title="Average Popularity",
        text=album_df["avg_popularity"].round(1),
    )
    st.plotly_chart(fig2a, use_container_width=True)

with col6:
    fig2b = px.bar(
        album_df,
        x="album_type", y="avg_rank",
        color="album_type",
        title="Average Chart Rank (lower = better)",
        text=album_df["avg_rank"].round(1),
    )
    fig2b.update_yaxes(autorange="reversed")
    st.plotly_chart(fig2b, use_container_width=True)

with col7:
    fig2c = px.bar(
        album_df,
        x="album_type", y="avg_days",
        color="album_type",
        title="Average Days on Chart",
        text=album_df["avg_days"].round(1),
    )
    st.plotly_chart(fig2c, use_container_width=True)

st.markdown("---")

# ── Section 3: Duration Impact ────────────────────────────────────────────────

st.subheader("⏱️ Song Duration Impact on Performance")

dur_df = duration_buckets(df)

col8, col9 = st.columns(2)

with col8:
    fig3a = px.bar(
        dur_df,
        x="duration_bucket", y="avg_popularity",
        color="avg_popularity",
        color_continuous_scale="Magma",
        title="Average Popularity by Duration",
        labels={"duration_bucket": "Duration Range", "avg_popularity": "Avg Popularity"},
        text=dur_df["avg_popularity"].round(1),
    )
    st.plotly_chart(fig3a, use_container_width=True)

with col9:
    fig3b = px.bar(
        dur_df,
        x="duration_bucket", y="avg_rank",
        color="avg_rank",
        color_continuous_scale="RdYlGn_r",
        title="Average Chart Rank by Duration (lower = better)",
        labels={"duration_bucket": "Duration Range", "avg_rank": "Avg Rank"},
        text=dur_df["avg_rank"].round(1),
    )
    fig3b.update_yaxes(autorange="reversed")
    st.plotly_chart(fig3b, use_container_width=True)

# Scatter: raw duration vs popularity
st.subheader("🔵 Raw Duration vs Popularity — Scatter")
fig4 = px.scatter(
    song_stats,
    x="duration_min", y="avg_popularity",
    color="album_type",
    size="days_on_chart",
    hover_name="song",
    hover_data=["artist", "best_rank"],
    trendline="ols",
    title="Song Duration (minutes) vs Average Popularity",
    labels={"duration_min": "Duration (minutes)", "avg_popularity": "Avg Popularity"},
)
st.plotly_chart(fig4, use_container_width=True)

# ── Key Insight Callouts ──────────────────────────────────────────────────────

st.subheader("💡 Key Business Insights")

exp_row  = explicit_df.set_index("label")
alb_row  = album_df.set_index("album_type") if "album_type" in album_df.columns else None

col_i1, col_i2, col_i3 = st.columns(3)

with col_i1:
    if "Explicit" in exp_row.index and "Clean" in exp_row.index:
        diff = exp_row.loc["Explicit","avg_popularity"] - exp_row.loc["Clean","avg_popularity"]
        direction = "higher" if diff > 0 else "lower"
        st.info(
            f"**Explicit vs Clean**\n\n"
            f"Explicit tracks average **{abs(diff):.1f} points {direction}** "
            f"popularity than clean tracks."
        )

with col_i2:
    if alb_row is not None and "Single" in alb_row.index and "Album" in alb_row.index:
        diff = alb_row.loc["Single","avg_days"] - alb_row.loc["Album","avg_days"]
        direction = "longer" if diff > 0 else "shorter"
        st.info(
            f"**Singles vs Album Tracks**\n\n"
            f"Singles stay on chart **{abs(diff):.1f} days {direction}** "
            f"than album tracks on average."
        )

with col_i3:
    if not dur_df.empty:
        best_bucket = dur_df.loc[dur_df["avg_popularity"].idxmax(), "duration_bucket"]
        st.info(
            f"**Optimal Duration**\n\n"
            f"Songs in the **{best_bucket}** range achieve the highest "
            f"average popularity score."
        )
