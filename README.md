# US Spotify Top 50 — Music Analytics Dashboard

> Deep analytics on US playlist chart dynamics for **Atlantic Recording Corporation**

[![Streamlit App](https://static.streamlit.io/badges/streamlit_badge_black_white.svg)](https://spotify-us-top50.streamlit.app/)

---

## Overview

This project delivers historical analytics on the **US Spotify Top 50** playlist — tracking ranking stability, artist dominance, popularity trends, and content attributes to support data-driven artist promotion and release timing decisions.

**This is NOT a prediction or recommendation system.** It is a **Business Intelligence + Data Storytelling** dashboard.

---

## Live Dashboard Pages

| Page | Description |
|------|-------------|
| Playlist Timeline | Rank movements, entry/exit, fast risers, daily heatmap |
| Song Performance | Longevity, peak vs average rank, volatility, trend scores |
| Artist Dominance | Leaderboard, dominance index, song diversity, timeline |
| Popularity Analysis | Rank↔popularity correlation, tier distributions, stability |
| Content Attributes | Explicit vs clean, singles vs albums, duration impact |

---

## Tech Stack

| Layer | Technology |
|-------|-----------|
| Data Processing | Python, Pandas, NumPy |
| Visualization | Plotly, Matplotlib, Seaborn |
| Dashboard | Streamlit |
| Deployment | Streamlit Community Cloud |

---

## Run Locally

### 1. Clone the repo
```bash
git clone https://github.com/your-username/spotify-us-top50.git
cd spotify-us-top50
```

### 2. Create virtual environment
```bash
python -m venv venv
source venv/bin/activate   # Mac/Linux
venv\Scripts\activate      # Windows
```

### 3. Install dependencies
```bash
pip install -r requirements.txt
```

### 4. Download dataset
```bash
python download_data.py
```

### 5. Launch dashboard
```bash
streamlit run app/main.py
```

---

## Project Structure

```
spotify-us-top50/
├── data/                    # Dataset (not committed to git but you can access it at https://drive.google.com/file/d/1ss4ehLrhb5_X_RlEK7npanh5wfwEIm1V/view)
├── notebooks/               # EDA notebook
├── src/
│   ├── preprocessing.py     # Data loading, validation, cleaning
│   ├── feature_engineering.py  # KPI derivation (vectorized)
│   ├── analytics.py         # Business analytics functions
├── app/
│   ├── main.py              # Streamlit entry point + global KPIs
│   ├── pages/               # Multi-page Streamlit app
│   └── utils/
│       └── data_loader.py   # Cached data loader + filter helper
├── requirements.txt
└── README.md
```

---

## 📊 Key KPIs Tracked

- **Days on Chart** — chart longevity per song
- **Rank Volatility Index** — std deviation of rank (stability metric)
- **Popularity Trend Score** — linear slope of popularity over time
- **Artist Dominance Index** — artist's share of all playlist slots
- **Explicit Content Share** — content strategy insight

---

## 🏢 Business Context

Built for **Atlantic Recording Corporation** to support:
- Artist promotion strategy
- Release timing decisions
- Marketing spend optimization
- Catalog performance analysis

---

## 📄 License

MIT
